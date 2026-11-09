#Barebones entry point using fixtures until the search algorithms are ready

import argparse
import json
from pathlib import Path

from visualization import ComparisonWindow
# Path locates files
# ComparisonWindow has the Matplotlib figure and controls

DATA_DIR = Path(__file__).resolve().parent / "data"


#takes a file and returns the python json object (json to python)
def load_json(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)

#loads both graph and results from json and prints contents
#graph has nodes and coordinates with edges and weights
#results has starting node, desitnation, and alg outputs
def main():
    parser = argparse.ArgumentParser(description="Play back mock search results in two panels.")
    parser.add_argument("--small", action="store_true", help="Use the original five-node example.")
    args = parser.parse_args()
    graph = load_json("sample_graph.json" if args.small else "large_graph.json")
    results = load_json("mock_results.json" if args.small else "large_mock_results.json")

    print("Metro optimization (MOCK DATA)")
    print(f"Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} directed edges")
    print(f"Query: {results['start']} -> {results['goal']}")

# loop through results and prints
    for result in results["results"]:
        path = " -> ".join(map(str, result["path"]))
        print(f"{result['algorithm']}: {path} | distance: {result['distance']}")
# reminder to complete!!!
    print("\nThese are saved examples; no search or benchmark has run.")
    # Keep the window object alive while Matplotlib handles clicks and timer events.
    window = ComparisonWindow(graph, results)
    window.show()


if __name__ == "__main__":
    main()
