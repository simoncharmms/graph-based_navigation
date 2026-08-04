# Graph-Based Navigation Demo

This repository demonstrates a practical version of the idea described in [graph_based_navigation_proposal.md](graph_based_navigation_proposal.md): combine a directed road network with a directed POI knowledge graph, then rank route and stop combinations instead of only computing the fastest path.

## What the Demo Shows

- deterministic routing on a directed road graph
- semantic POI reasoning on a directed knowledge graph
- intent-aware route-stop ranking for fuel, EV charging, and family rest scenarios
- human-readable explanations for why a stop is recommended

The implementation is intentionally compact and dependency-light so it is easy to inspect, run, and extend.

## Repo Layout

```text
src/graph_navigation/
  cli.py
  demo_data.py
  engine.py
  models.py
tests/
  test_engine.py
graph_based_navigation_proposal.md
```

## Quick Start

Create a virtual environment and install the package in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

Run the CLI demo:

```bash
graph-nav demo
```

Run a specific scenario:

```bash
graph-nav scenario fuel_stop
graph-nav scenario ev_charge
graph-nav scenario family_rest
```

Run tests:

```bash
pytest
```

## Example Output

The demo prints:

- a baseline fastest route
- recommended route-stop itineraries
- travel time and detour
- POI score and overall score
- explanation strings derived from the knowledge graph and trip preferences

## Design Notes

The route planner uses a simple shortest-path search over a directed road graph. Candidate POIs are attached to routable anchors. The knowledge graph contributes amenity, compatibility, and contextual signals that influence which stop should be added to an itinerary.

This is not a production navigation engine. It is a structured demonstration intended to show how a knowledge graph can augment conventional routing in a commercially realistic way.
