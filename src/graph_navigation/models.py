from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    travel_minutes: float
    reliability: float = 1.0
    road_type: str = "local"


@dataclass(frozen=True)
class POI:
    poi_id: str
    name: str
    category: str
    anchor_node: str
    rating: float
    amenities: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    open_now: bool = True
    predicted_wait_minutes: float = 0.0
    vehicle_types: tuple[str, ...] = ("ice", "ev")


@dataclass(frozen=True)
class KnowledgeEdge:
    source: str
    relation: str
    target: str
    weight: float = 1.0


@dataclass(frozen=True)
class TripPreference:
    intent: str
    vehicle_type: str
    max_detour_minutes: float
    prefer_brands: tuple[str, ...] = ()
    required_amenities: tuple[str, ...] = ()
    avoid_amenities: tuple[str, ...] = ()
    weight_eta: float = 0.40
    weight_poi_quality: float = 0.35
    weight_reliability: float = 0.15
    weight_context: float = 0.10


@dataclass(frozen=True)
class Scenario:
    name: str
    origin: str
    destination: str
    preference: TripPreference


@dataclass(frozen=True)
class RoutePlan:
    path: tuple[str, ...]
    travel_minutes: float
    reliability: float


@dataclass(frozen=True)
class Recommendation:
    scenario_name: str
    baseline_route: RoutePlan
    final_route: RoutePlan
    poi: POI | None
    detour_minutes: float
    poi_score: float
    total_score: float
    explanations: tuple[str, ...] = field(default_factory=tuple)
