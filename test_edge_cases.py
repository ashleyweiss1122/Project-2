
from parser import load_stops, load_connections, load_transfers
from graph import build_graph
from algorithms import dijkstra, a_star


def test_edge_cases():
    stops = load_stops()
    connections = load_connections()
    transfers = load_transfers(stops)
    graph = build_graph(stops, connections, transfers)

    print("\nBACKEND EDGE CASE TESTS")

    # Test 1: Invalid starting station.
    print("\nTEST 1: Invalid starting station")

    try:
        dijkstra(graph, "INVALID", "A27N")
        print("FAILED: Invalid station was accepted.")
    except (KeyError, ValueError):
        print("PASSED: Invalid station was rejected.")

    # Test 2: Invalid destination station.
    print("\nTEST 2: Invalid destination station")

    try:
        a_star(graph, "101S", "INVALID")
        print("FAILED: Invalid destination was accepted.")
    except (KeyError, ValueError):
        print("PASSED: Invalid destination was rejected.")

    # Test 3: Same starting and destination station.
    print("\nTEST 3: Same starting and destination")

    for algorithm in [dijkstra, a_star]:
        result = algorithm(graph, "101S", "101S")

        passed = (
            result["found"]
            and result["path"] == ["101S"]
            and result["travel_time"] == 0
        )

        print(algorithm.__name__, "PASSED" if passed else "FAILED")

    # Test 4: Unreachable destination.
    print("\nTEST 4: Unreachable destination")

    dijkstra_result = dijkstra(graph, "A27N", "101S")
    astar_result = a_star(graph, "A27N", "101S")

    for result in [dijkstra_result, astar_result]:
        passed = (
            not result["found"]
            and result["path"] == []
            and result["travel_time"] == float("inf")
        )

        print("PASSED" if passed else "FAILED")

    # Test 5: Empty graph.
    print("\nTEST 5: Empty graph")

    from graph import SubwayGraph

    empty_graph = SubwayGraph()

    try:
        dijkstra(empty_graph, "101S", "A27N")
        print("FAILED: Empty graph was accepted.")
    except (KeyError, ValueError):
        print("PASSED: Empty graph was rejected.")


if __name__ == "__main__":
    test_edge_cases()
