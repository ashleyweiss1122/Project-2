import time
from parser import load_stops, load_connections, load_transfers
from graph import build_graph
from algorithms import dijkstra
from algorithms import heuristic, a_star

# Load NYC subway data
stops = load_stops()
connections = load_connections()

print("\nSTATIONS WITH OUTGOING CONNECTIONS")

for stop_id, edges in connections.items():
    if len(edges) > 0:
        print(stop_id, "has", len(edges), "connections")
        break

transfers = load_transfers(stops)
'''
print("\nRAW CONNECTION CHECK")

print("101N in connections:", "101N" in connections)

print("Raw connections from 101N:")
print(connections.get("101N", []))

print("\nRaw connections to 101N:")

for start, edges in connections.items():
    for edge in edges:
        if edge["destination"] == "101N":
            print(start, "->", edge["destination"],
                  "Travel time:", edge["travel_time"])
'''
# Build subway graph
subway_graph = build_graph(stops, connections, transfers)

# Choose two subway stops
start = "101S"
destination = "A27N"

# Run Dijkstra
start_time = time.perf_counter()

result = dijkstra(subway_graph, start, destination)

dijkstra_time = time.perf_counter() - start_time

# Display results
print("\nDIJKSTRA TEST")
print("Starting station:", start)
print("Destination:", destination)
print("Shortest path:", result["path"])
print("Travel time:", result["travel_time"], "seconds")
print("Nodes explored:", result["nodes_explored"])
print("Route found:", result["found"])

print("Arrival edges recorded:", len(result["arrival_edges"]))
print("First 5 arrival edges:", result["arrival_edges"][:5])
print(
    "Expansion count matches arrival edges:",
    len(result["expanded_order"]) == len(result["arrival_edges"])
)

print("Dijkstra execution time:", dijkstra_time * 1000, "milliseconds")

print("\nHEURISTIC TEST")

estimated_time = heuristic(subway_graph, "101S", "A27N")

print("Estimated travel time:", estimated_time, "seconds")


print("\nA* TEST")

astar_start = "101S"
astar_destination = "A27N"

astar_start_time = time.perf_counter()

astar_result = a_star(subway_graph, astar_start, astar_destination)

astar_time = time.perf_counter() - astar_start_time

print("Starting station: ", astar_start)
print("Destination: ", astar_destination)
print("Shortest path:", astar_result["path"])
print("Travel time:", astar_result["travel_time"], "seconds")
print("Nodes explored:", astar_result["nodes_explored"])
print("Route found:", astar_result["found"])

print("Arrival edges recorded:", len(astar_result["arrival_edges"]))
print(
    "Expansion count matches arrival edges:",
    len(astar_result["expanded_order"]) == len(astar_result["arrival_edges"])
)

print("A* execution time:", astar_time * 1000, "milliseconds")

# Warm up both algorithms
dijkstra(subway_graph, "101S", "A27N")
a_star(subway_graph, "101S", "A27N")


print("\nPERFORMANCE BENCHMARK")

iterations = 1000

dijkstra_times = []
astar_times = []

for _ in range(iterations):
    start_time = time.perf_counter()
    dijkstra(subway_graph, "101S", "A27N")
    dijkstra_times.append(time.perf_counter() - start_time)

    start_time = time.perf_counter()
    a_star(subway_graph, "101S", "A27N")
    astar_times.append(time.perf_counter() - start_time)

average_dijkstra = sum(dijkstra_times) / iterations * 1000
average_astar = sum(astar_times) / iterations * 1000


print("Iterations:", iterations)
print("Average Dijkstra time:", average_dijkstra, "ms")
print("Average A* time:", average_astar, "ms")

print("\nMULTIPLE ROUTE TESTS")

test_routes = [
    ("103N", "101N"),
    ("101S", "A27N"),
    ("A27N", "101S"),
    ("A25N", "D20S"),
    ("R16N", "A27N"),
    ("101S", "R16N"),
]

for start, destination in test_routes:
    print(f"\nTesting {start} -> {destination}")

    dijkstra_result = dijkstra(subway_graph, start, destination)
    astar_result = a_star(subway_graph, start, destination)

    print("Dijkstra time:", dijkstra_result["travel_time"])
    print("A* time:", astar_result["travel_time"])

    print("Dijkstra nodes:", dijkstra_result["nodes_explored"])
    print("A* nodes:", astar_result["nodes_explored"])

    print("Same travel time:",
          dijkstra_result["travel_time"] == astar_result["travel_time"])

print("\nFULL HEURISTIC CONSISTENCY TEST")

inconsistent_edges = []
destinations_checked = 0

for destination in subway_graph.vertices:

    destinations_checked += 1

    for start in subway_graph.adjacency:

        for neighbor, edge in subway_graph.get_neighbors(start).items():

            h_start = heuristic(subway_graph, start, destination)
            h_neighbor = heuristic(subway_graph, neighbor, destination)

            if h_start > edge["travel_time"] + h_neighbor + 0.000001:
                inconsistent_edges.append(
                    (start, neighbor, destination, edge["travel_time"])
                )

print("Destinations checked:", destinations_checked)
print("Inconsistent edges found:", len(inconsistent_edges))

for edge in inconsistent_edges[:10]:
    print(edge)