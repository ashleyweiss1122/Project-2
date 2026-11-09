'''
from parser import load_stops, load_connections, load_transfers
from graph import build_graph
from algorithms import dijkstra, a_star
#Barebones entry point using fixtures until the search algorithms are ready

import argparse
import json
from pathlib import Path

from visualization import ComparisonWindow
# Path locates files
# ComparisonWindow has the Matplotlib figure and controls

DATA_DIR = Path(__file__).resolve().parent / "data"
from visualization_adapter import (convert_graph_for_visualization, convert_results_for_visualization)


#takes a file and returns the python json object (json to python)
def load_json(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)

#loads both graph and results from json and prints contents
#graph has nodes and coordinates with edges and weights
#results has starting node, desitnation, and alg outputs
def main():
    # load subway data
    stops = load_stops()
    connections = load_connections()
    transfers = load_transfers(stops)

    # build backend graph
    subway_graph = build_graph(stops, connections, transfers)

    # select route to visualize
    start = "101S"
    destination = "A27N"

    # run algorithms
    dijkstra_result = dijkstra(subway_graph, start, destination)
    astar_result = a_star(subway_graph, start, destination)
    parser = argparse.ArgumentParser(description="Play back mock search results in two panels.")
    parser.add_argument("--small", action="store_true", help="Use the original five-node example.")
    args = parser.parse_args()
    graph = load_json("sample_graph.json" if args.small else "large_graph.json")
    results = load_json("mock_results.json" if args.small else "large_mock_results.json")

    # convert data for visualization
    visual_graph = convert_graph_for_visualization(subway_graph)
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
    visual_results = convert_results_for_visualization(
        start,
        destination,
        dijkstra_result,
        astar_result
    )

    # launch visualization
    window = ComparisonWindow(visual_graph, visual_results)
    window.show()
'''

import tkinter as tk
from tkinter import simpledialog, messagebox

from parser import load_stops, load_connections, load_transfers
from graph import build_graph
from algorithms import dijkstra, a_star
from visualization import ComparisonWindow
from visualization_adapter import (
    convert_graph_for_visualization,
    convert_results_for_visualization
)

def station_input_window(root, title, prompt):
    result = {"value": None}

    window = tk.Toplevel(root)
    window.title(title)

    # Set window size and center it on the screen
    window_width = 550
    window_height = 300

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    window.resizable(True, True)

    tk.Label(
        window,
        text=prompt,
        font=("Arial", 18, "bold")
    ).pack(pady=(35, 15))

    entry = tk.Entry(
        window,
        font=("Arial", 16),
        width=30
    )
    entry.pack(pady=10)
    entry.focus_set()

    def submit():
        result["value"] = entry.get()
        window.destroy()

    def cancel():
        window.destroy()

    tk.Button(
        window,
        text="Continue",
        font=("Arial", 14),
        width=15,
        command=submit
    ).pack(pady=15)

    window.protocol("WM_DELETE_WINDOW", cancel)
    window.bind("<Return>", lambda event: submit())

    window.grab_set()
    root.wait_window(window)

    return result["value"]

def select_station(stops, prompt, root):
    stations = {}

    # Group platforms by physical station name.
    for stop_id, info in stops.items():
        parent_id = info["parent_station"]

        if parent_id:
            station_name = stops[parent_id]["name"].strip()
            platform_id = stop_id
        else:
            station_name = info["name"].strip()
            platform_id = stop_id

            # Skip parent stations that have child platforms.
            if any(
                other["parent_station"] == stop_id
                for other in stops.values()
            ):
                continue

        if not station_name:
            continue

        key = station_name.lower()

        if key not in stations:
            stations[key] = {
                "name": station_name,
                "stop_ids": []
            }

        if platform_id not in stations[key]["stop_ids"]:
            stations[key]["stop_ids"].append(platform_id)

    while True:
        search = station_input_window(
            root,
            "Metro Boom - Station Selection",
            prompt
        )

        if search is None:
            return None, None

        search = search.strip()

        if not search:
            messagebox.showwarning(
                "Missing station",
                "Please enter a station name or stop ID."
            )
            continue

        # Allow exact stop ID entry.
        if search in stops:
            info = stops[search]
            parent_id = info["parent_station"]

            if parent_id:
                return stops[parent_id]["name"], [search]

            station_name = info["name"]

            if any(
                other["parent_station"] == search
                for other in stops.values()
            ):
                return station_name, stations[station_name.lower()]["stop_ids"]

            return station_name, [search]

        # Search station names.
        matches = [
            station for key, station in stations.items()
            if search.lower() in key
        ]

        if len(matches) == 1:
            return matches[0]["name"], matches[0]["stop_ids"]

        if len(matches) > 1:
            choices = "\n".join(
                f"{index}. {station['name']}"
                for index, station in enumerate(matches, start=1)
            )

            choice = simpledialog.askinteger(
                "Select station",
                "Multiple stations found:\n\n"
                + choices
                + "\n\nEnter the number of your station:",
                parent=root,
                minvalue=1,
                maxvalue=len(matches)
            )

            if choice is not None:
                selected = matches[choice - 1]
                return selected["name"], selected["stop_ids"]

        else:
            messagebox.showwarning(
                "Station not found",
                "No matching station found. Please try again."
            )

def find_best_route(graph, start_ids, destination_ids, algorithm):
    best_result = None
    best_start = None
    best_destination = None

    for start_id in start_ids:
        for destination_id in destination_ids:
            result = algorithm(graph, start_id, destination_id)

            if result["found"]:
                if (
                    best_result is None
                    or result["travel_time"] < best_result["travel_time"]
                ):
                    best_result = result
                    best_start = start_id
                    best_destination = destination_id

            elif best_result is None:
                best_result = result
                best_start = start_id
                best_destination = destination_id

    return best_start, best_destination, best_result


def main():
    print("Metro Boom - Metro Optimization")

    # Load the real subway data.
    stops = load_stops()
    connections = load_connections()
    transfers = load_transfers(stops)

    # Build the subway graph.
    subway_graph = build_graph(stops, connections, transfers)

    print(
        f"\nLoaded {subway_graph.get_vertex_count()} stops "
        f"and {subway_graph.get_edge_count()} connections."
    )

    root = tk.Tk()
    root.withdraw()

    # Let the user choose stations by name.
    start_name, start_ids = select_station(
        stops, "Enter your starting station:", root
    )

    if start_ids is None:
        root.destroy()
        return

    destination_name, destination_ids = select_station(
        stops, "Enter your destination station:", root
    )

    if destination_ids is None:
        root.destroy()
        return

    root.destroy()

    print(f"\nFinding route from {start_name} to {destination_name}...")

    # Run both algorithms across the selected station platforms.
    dijkstra_start, dijkstra_destination, dijkstra_result = find_best_route(
        subway_graph, start_ids, destination_ids, dijkstra
    )

    astar_start, astar_destination, astar_result = find_best_route(
        subway_graph, start_ids, destination_ids, a_star
    )

    # Use the selected platform IDs for the visualization adapter.
    visual_graph = convert_graph_for_visualization(subway_graph)

    visual_results = convert_results_for_visualization(
        dijkstra_start,
        dijkstra_destination,
        dijkstra_result,
        astar_result
    )

    print("\nRoute search complete.")
    print(f"Dijkstra travel time: {dijkstra_result['travel_time']}")
    print(f"A* travel time: {astar_result['travel_time']}")

    # Launch the visualization.
    window = ComparisonWindow(visual_graph, visual_results)
    window.show()


if __name__ == "__main__":
    main()
