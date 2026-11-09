
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
