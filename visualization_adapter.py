
def convert_graph_for_visualization(graph):

    nodes = []
    edges = []

    # Convert subway stops into visualization nodes
    for stop_id, stop_info in graph.vertices.items():
        nodes.append({
            "id": stop_id,
            "x": stop_info["longitude"],
            "y": stop_info["latitude"]
        })

    # Convert subway connections into visualization edges
    for start, neighbors in graph.adjacency.items():
        for destination, edge_info in neighbors.items():
            edges.append({
                "source": start,
                "target": destination,
                "weight": edge_info["travel_time"]
            })

    return {
        "nodes": nodes,
        "edges": edges
    }


def convert_results_for_visualization(start, destination, dijkstra_result, astar_result):

    results = []

    for algorithm_name, result in [
        ("Dijkstra", dijkstra_result),
        ("astar", astar_result)
    ]:
        results.append({
            "algorithm": algorithm_name,
            "expanded_order": result["expanded_order"],
            "arrival_edges": result["arrival_edges"],
            "path": result["path"],
            "found": result["found"],
            "distance": result["travel_time"]
        })

    return {
        "start": start,
        "goal": destination,
        "results": results
    }

'''
if __name__ == "__main__":
    from parser import load_stops, load_connections, load_transfers
    from graph import build_graph
    from algorithms import dijkstra, a_star

    stops = load_stops()
    connections = load_connections()
    transfers = load_transfers(stops)

    subway_graph = build_graph(stops, connections, transfers)

    start = "101S"
    destination = "A27N"

    # Convert graph
    visual_graph = convert_graph_for_visualization(subway_graph)

    # Run both algorithms
    dijkstra_result = dijkstra(subway_graph, start, destination)
    astar_result = a_star(subway_graph, start, destination)

    # Convert algorithm results
    visual_results = convert_results_for_visualization(
        start,
        destination,
        dijkstra_result,
        astar_result
    )

    print("VISUALIZATION DATA TEST")
    print("Nodes:", len(visual_graph["nodes"]))
    print("Edges:", len(visual_graph["edges"]))
    print("Start:", visual_results["start"])
    print("Goal:", visual_results["goal"])

    for result in visual_results["results"]:
        print("\nAlgorithm:", result["algorithm"])
        print("Path found:", result["found"])
        print("Distance:", result["distance"])
        print("Expanded nodes:", len(result["expanded_order"]))
        print("Arrival edges:", len(result["arrival_edges"]))
        print("Path length:", len(result["path"]))
'''