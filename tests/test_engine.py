from graph_navigation.demo_data import build_demo_knowledge_edges, build_demo_pois, build_demo_road_edges, build_demo_scenarios
from graph_navigation.engine import NavigationEngine


def _engine() -> NavigationEngine:
    return NavigationEngine(
        road_edges=build_demo_road_edges(),
        pois=build_demo_pois(),
        knowledge_edges=build_demo_knowledge_edges(),
    )


def test_baseline_route_is_shortest_path() -> None:
    engine = _engine()
    scenario = build_demo_scenarios()[0]
    recommendation = engine.recommend(scenario, limit=1)[0]
    assert recommendation.baseline_route.path == ("home", "arterial_w", "junction", "highway_e", "office")
    assert recommendation.baseline_route.travel_minutes == 22


def test_fuel_scenario_prefers_fuel_poi() -> None:
    engine = _engine()
    scenario = next(item for item in build_demo_scenarios() if item.name == "fuel_stop")
    recommendations = engine.recommend(scenario, limit=3)
    assert recommendations[0].poi is not None
    assert recommendations[0].poi.category == "fuel"


def test_ev_scenario_only_returns_ev_compatible_stop() -> None:
    engine = _engine()
    scenario = next(item for item in build_demo_scenarios() if item.name == "ev_charge")
    recommendations = engine.recommend(scenario, limit=3)
    poi_names = [item.poi.name for item in recommendations if item.poi is not None]
    assert "ChargePlus Hub" in poi_names
    assert all(item.poi is None or "ev" in item.poi.vehicle_types for item in recommendations)


def test_family_scenario_rewards_required_amenities() -> None:
    engine = _engine()
    scenario = next(item for item in build_demo_scenarios() if item.name == "family_rest")
    recommendations = engine.recommend(scenario, limit=3)
    assert recommendations[0].poi is not None
    assert recommendations[0].poi.name == "Family Plaza"