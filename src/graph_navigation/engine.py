from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import heapq
from math import inf

from .models import Edge, KnowledgeEdge, POI, Recommendation, RoutePlan, Scenario, TripPreference


@dataclass(frozen=True)
class _RouteState:
    minutes: float
    node: str
    path: tuple[str, ...]
    reliability: float


class NavigationEngine:
    def __init__(self, road_edges: list[Edge], pois: list[POI], knowledge_edges: list[KnowledgeEdge]) -> None:
        self._road_edges = road_edges
        self._pois = {poi.poi_id: poi for poi in pois}
        self._road_graph: dict[str, list[Edge]] = defaultdict(list)
        for edge in road_edges:
            self._road_graph[edge.source].append(edge)

        self._knowledge_graph: dict[str, list[KnowledgeEdge]] = defaultdict(list)
        for edge in knowledge_edges:
            self._knowledge_graph[edge.source].append(edge)

    def recommend(self, scenario: Scenario, limit: int = 3) -> list[Recommendation]:
        baseline = self._shortest_route(scenario.origin, scenario.destination)
        candidates: list[Recommendation] = [
            Recommendation(
                scenario_name=scenario.name,
                baseline_route=baseline,
                final_route=baseline,
                poi=None,
                detour_minutes=0.0,
                poi_score=0.0,
                total_score=self._baseline_score(baseline.travel_minutes, baseline.reliability, scenario.preference),
                explanations=("Fastest baseline route without a POI stop.",),
            )
        ]

        for poi in self._pois.values():
            if scenario.preference.vehicle_type not in poi.vehicle_types:
                continue

            outbound = self._shortest_route(scenario.origin, poi.anchor_node)
            inbound = self._shortest_route(poi.anchor_node, scenario.destination)
            final_route = self._merge_routes(outbound, inbound)
            detour = final_route.travel_minutes - baseline.travel_minutes
            if detour > scenario.preference.max_detour_minutes:
                continue

            poi_score, explanations = self._score_poi(poi, scenario.preference)
            total_score = self._total_score(
                travel_minutes=final_route.travel_minutes,
                reliability=final_route.reliability,
                poi_score=poi_score,
                preference=scenario.preference,
            )
            candidates.append(
                Recommendation(
                    scenario_name=scenario.name,
                    baseline_route=baseline,
                    final_route=final_route,
                    poi=poi,
                    detour_minutes=detour,
                    poi_score=poi_score,
                    total_score=total_score,
                    explanations=tuple(explanations),
                )
            )

        return sorted(candidates, key=lambda item: item.total_score, reverse=True)[:limit]

    def _shortest_route(self, origin: str, destination: str) -> RoutePlan:
        heap: list[tuple[float, int, _RouteState]] = []
        counter = 0
        heapq.heappush(heap, (0.0, counter, _RouteState(0.0, origin, (origin,), 1.0)))
        best_minutes: dict[str, float] = {origin: 0.0}

        while heap:
            _, _, state = heapq.heappop(heap)
            if state.node == destination:
                return RoutePlan(
                    path=state.path,
                    travel_minutes=round(state.minutes, 2),
                    reliability=round(state.reliability, 3),
                )

            if state.minutes > best_minutes.get(state.node, inf):
                continue

            for edge in self._road_graph.get(state.node, []):
                next_minutes = state.minutes + edge.travel_minutes
                if next_minutes >= best_minutes.get(edge.target, inf):
                    continue

                best_minutes[edge.target] = next_minutes
                counter += 1
                next_state = _RouteState(
                    minutes=next_minutes,
                    node=edge.target,
                    path=state.path + (edge.target,),
                    reliability=state.reliability * edge.reliability,
                )
                heapq.heappush(heap, (next_minutes, counter, next_state))

        raise ValueError(f"No route from {origin} to {destination}")

    def _merge_routes(self, first: RoutePlan, second: RoutePlan) -> RoutePlan:
        return RoutePlan(
            path=first.path + second.path[1:],
            travel_minutes=round(first.travel_minutes + second.travel_minutes, 2),
            reliability=round(first.reliability * second.reliability, 3),
        )

    def _score_poi(self, poi: POI, preference: TripPreference) -> tuple[float, list[str]]:
        score = 0.0
        explanations: list[str] = []

        if poi.category == self._category_for_intent(preference.intent):
            score += 0.35
            explanations.append(f"Matches trip intent '{preference.intent}'.")

        relations = self._knowledge_graph.get(poi.poi_id, [])
        relation_targets = {(edge.relation, edge.target): edge.weight for edge in relations}

        for amenity in preference.required_amenities:
            if amenity in poi.amenities or ("offers_amenity", amenity) in relation_targets:
                score += 0.12
                explanations.append(f"Provides required amenity '{amenity}'.")
            else:
                score -= 0.20
                explanations.append(f"Missing required amenity '{amenity}'.")

        for amenity in preference.avoid_amenities:
            if amenity in poi.amenities:
                score -= 0.15
                explanations.append(f"Contains avoided amenity '{amenity}'.")

        if preference.vehicle_type in poi.vehicle_types:
            score += 0.08

        if poi.open_now:
            score += 0.05
            explanations.append("Currently open.")
        else:
            score -= 0.50
            explanations.append("Currently closed.")

        if poi.predicted_wait_minutes <= 5:
            score += 0.08
            explanations.append("Low predicted wait time.")
        elif poi.predicted_wait_minutes >= 10:
            score -= 0.10
            explanations.append("High predicted wait time.")

        score += max(0.0, min(poi.rating / 5.0, 1.0)) * 0.20
        explanations.append(f"Strong user rating of {poi.rating:.1f}/5.0.")

        if poi.name in preference.prefer_brands:
            score += 0.10
            explanations.append("Matches a preferred brand.")

        for relation in relations:
            if relation.relation in {"preferred_for_intent", "compatible_with_vehicle_type", "safe_for_segment", "reliable_in_context"}:
                if relation.target in {preference.intent, preference.vehicle_type, "family", "peak_traffic"}:
                    score += 0.05 * relation.weight

        return round(score, 3), explanations

    def _baseline_score(self, travel_minutes: float, reliability: float, preference: TripPreference) -> float:
        return self._total_score(travel_minutes, reliability, poi_score=0.0, preference=preference)

    def _total_score(
        self,
        travel_minutes: float,
        reliability: float,
        poi_score: float,
        preference: TripPreference,
    ) -> float:
        eta_score = max(0.0, 1.0 - (travel_minutes / 40.0))
        reliability_score = min(max(reliability, 0.0), 1.0)
        context_score = max(0.0, poi_score)
        total = (
            eta_score * preference.weight_eta
            + poi_score * preference.weight_poi_quality
            + reliability_score * preference.weight_reliability
            + context_score * preference.weight_context
        )
        return round(total, 3)

    @staticmethod
    def _category_for_intent(intent: str) -> str:
        mapping = {
            "fuel_stop": "fuel",
            "ev_charge": "ev_charging",
            "family_rest": "rest_stop",
        }
        return mapping.get(intent, intent)
