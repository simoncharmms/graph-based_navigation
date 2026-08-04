from __future__ import annotations

import argparse
from textwrap import indent

from .demo_data import build_demo_knowledge_edges, build_demo_pois, build_demo_road_edges, build_demo_scenarios
from .engine import NavigationEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Graph-based navigation demo CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("demo", help="Run all demonstration scenarios")

    scenario = subparsers.add_parser("scenario", help="Run a single scenario")
    scenario.add_argument("name", choices=[item.name for item in build_demo_scenarios()])
    scenario.add_argument("--limit", type=int, default=3)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    engine = NavigationEngine(
        road_edges=build_demo_road_edges(),
        pois=build_demo_pois(),
        knowledge_edges=build_demo_knowledge_edges(),
    )
    scenarios = {scenario.name: scenario for scenario in build_demo_scenarios()}

    if args.command == "demo":
        for name in scenarios:
            print(render_scenario(engine, scenarios[name], limit=3))
        return

    print(render_scenario(engine, scenarios[args.name], limit=args.limit))


def render_scenario(engine: NavigationEngine, scenario, limit: int) -> str:
    recommendations = engine.recommend(scenario, limit=limit)
    lines = [
        f"Scenario: {scenario.name}",
        f"Origin -> Destination: {scenario.origin} -> {scenario.destination}",
        f"Intent: {scenario.preference.intent} | Vehicle: {scenario.preference.vehicle_type}",
        "Recommendations:",
    ]
    for index, recommendation in enumerate(recommendations, start=1):
        stop_name = recommendation.poi.name if recommendation.poi else "No stop"
        lines.extend(
            [
                f"{index}. {stop_name}",
                f"   overall score: {recommendation.total_score:.3f}",
                f"   travel minutes: {recommendation.final_route.travel_minutes:.1f}",
                f"   detour minutes: {recommendation.detour_minutes:.1f}",
                f"   route: {' -> '.join(recommendation.final_route.path)}",
                f"   explanation:\n{indent(chr(10).join(f'- {item}' for item in recommendation.explanations), '      ')}",
            ]
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
