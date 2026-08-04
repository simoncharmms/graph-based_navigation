from __future__ import annotations

from .models import Edge, KnowledgeEdge, POI, Scenario, TripPreference


def build_demo_road_edges() -> list[Edge]:
    return [
        Edge("home", "arterial_w", 5, reliability=0.95, road_type="urban"),
        Edge("arterial_w", "junction", 6, reliability=0.95, road_type="urban"),
        Edge("junction", "downtown", 8, reliability=0.92, road_type="urban"),
        Edge("junction", "highway_e", 4, reliability=0.96, road_type="highway"),
        Edge("highway_e", "office", 7, reliability=0.97, road_type="highway"),
        Edge("downtown", "office", 6, reliability=0.88, road_type="urban"),
        Edge("junction", "fuel_exit", 3, reliability=0.93, road_type="service"),
        Edge("fuel_exit", "highway_e", 4, reliability=0.91, road_type="service"),
        Edge("junction", "charger_hub", 4, reliability=0.94, road_type="service"),
        Edge("charger_hub", "office", 8, reliability=0.95, road_type="urban"),
        Edge("arterial_w", "family_plaza", 4, reliability=0.90, road_type="service"),
        Edge("family_plaza", "junction", 5, reliability=0.90, road_type="service"),
        Edge("highway_e", "scenic_detour", 4, reliability=0.84, road_type="local"),
        Edge("scenic_detour", "office", 9, reliability=0.85, road_type="local"),
    ]


def build_demo_pois() -> list[POI]:
    return [
        POI(
            poi_id="poi_fuel_fast",
            name="QuickFuel Express",
            category="fuel",
            anchor_node="fuel_exit",
            rating=4.2,
            amenities=("restroom", "coffee"),
            tags=("low_detour", "highway_access"),
            predicted_wait_minutes=2,
        ),
        POI(
            poi_id="poi_charge_plus",
            name="ChargePlus Hub",
            category="ev_charging",
            anchor_node="charger_hub",
            rating=4.7,
            amenities=("restroom", "cafe", "covered_parking"),
            tags=("fast_charge", "reliable"),
            predicted_wait_minutes=6,
            vehicle_types=("ev",),
        ),
        POI(
            poi_id="poi_family_stop",
            name="Family Plaza",
            category="rest_stop",
            anchor_node="family_plaza",
            rating=4.6,
            amenities=("restroom", "playground", "food"),
            tags=("family_friendly", "safe_access"),
            predicted_wait_minutes=3,
        ),
        POI(
            poi_id="poi_downtown_cafe",
            name="Downtown Cafe",
            category="food",
            anchor_node="downtown",
            rating=4.8,
            amenities=("coffee", "wifi"),
            tags=("urban", "busy"),
            predicted_wait_minutes=8,
        ),
    ]


def build_demo_knowledge_edges() -> list[KnowledgeEdge]:
    return [
        KnowledgeEdge("poi_fuel_fast", "offers_amenity", "restroom", 0.8),
        KnowledgeEdge("poi_fuel_fast", "offers_amenity", "coffee", 0.7),
        KnowledgeEdge("poi_fuel_fast", "preferred_for_intent", "fuel_stop", 1.0),
        KnowledgeEdge("poi_fuel_fast", "accessible_from", "highway_corridor", 0.9),
        KnowledgeEdge("poi_charge_plus", "offers_amenity", "restroom", 0.8),
        KnowledgeEdge("poi_charge_plus", "offers_amenity", "cafe", 0.7),
        KnowledgeEdge("poi_charge_plus", "compatible_with_vehicle_type", "ev", 1.0),
        KnowledgeEdge("poi_charge_plus", "preferred_for_intent", "ev_charge", 1.0),
        KnowledgeEdge("poi_charge_plus", "reliable_in_context", "peak_traffic", 0.8),
        KnowledgeEdge("poi_family_stop", "offers_amenity", "restroom", 0.9),
        KnowledgeEdge("poi_family_stop", "offers_amenity", "playground", 1.0),
        KnowledgeEdge("poi_family_stop", "offers_amenity", "food", 0.8),
        KnowledgeEdge("poi_family_stop", "preferred_for_intent", "family_rest", 1.0),
        KnowledgeEdge("poi_family_stop", "safe_for_segment", "family", 0.9),
        KnowledgeEdge("poi_downtown_cafe", "offers_amenity", "coffee", 0.9),
        KnowledgeEdge("poi_downtown_cafe", "busy_during", "peak_traffic", 0.4),
    ]


def build_demo_scenarios() -> list[Scenario]:
    return [
        Scenario(
            name="fuel_stop",
            origin="home",
            destination="office",
            preference=TripPreference(
                intent="fuel_stop",
                vehicle_type="ice",
                max_detour_minutes=10,
                required_amenities=("restroom",),
            ),
        ),
        Scenario(
            name="ev_charge",
            origin="home",
            destination="office",
            preference=TripPreference(
                intent="ev_charge",
                vehicle_type="ev",
                max_detour_minutes=14,
                required_amenities=("restroom",),
                prefer_brands=("ChargePlus Hub",),
                weight_poi_quality=0.40,
                weight_eta=0.30,
            ),
        ),
        Scenario(
            name="family_rest",
            origin="home",
            destination="office",
            preference=TripPreference(
                intent="family_rest",
                vehicle_type="ice",
                max_detour_minutes=12,
                required_amenities=("restroom", "food", "playground"),
                weight_poi_quality=0.45,
                weight_eta=0.25,
            ),
        ),
    ]
