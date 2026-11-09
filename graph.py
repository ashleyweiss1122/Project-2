class SubwayGraph:
    # represents NYC subway system as a weighted, directed graph

    def __init__(self):
        self.vertices = {}
        self.adjacency = {}

    def add_vertex(self, stop_id, stop_info):
        # add subway stop to graph
        self.vertices[stop_id] = stop_info

        if stop_id not in self.adjacency:
            self.adjacency[stop_id] = {}

    def add_edge(self, start, destination, travel_time, edge_type="train"):
        # add directed connection between stops
        if start not in self.adjacency:
            return

        if destination not in self.adjacency:
            return

        if travel_time < 0:
            return

        current_edge = self.adjacency[start].get(destination)

        if current_edge is None or travel_time < current_edge["travel_time"]:
            self.adjacency[start][destination] = {
                "travel_time": travel_time,
                "type": edge_type
            }

    def get_neighbors(self, stop_id):
        # returns all neighboring stops and travel times
        return self.adjacency.get(stop_id, {})

    def get_vertex_count(self):
        # returns number of subway stops
        return len(self.vertices)

    def get_edge_count(self):
        # returns number of unique directed connections
        return sum(len(neighbors) for neighbors in self.adjacency.values())


def build_graph(stops, connections, transfers):
    graph = SubwayGraph()

    # Add all subway platforms as vertices
    for stop_id, stop_info in stops.items():
        graph.add_vertex(stop_id, stop_info)

    # Add train connections
    for start, edges in connections.items():
        for edge in edges:
            graph.add_edge(
                start,
                edge["destination"],
                edge["travel_time"],
                "train"
            )

    # Add station transfer connections
    for transfer in transfers:
        graph.add_edge(
            transfer["source"],
            transfer["destination"],
            transfer["travel_time"],
            "transfer"
        )

    return graph

'''
if __name__ == "__main__":
    from parser import load_stops, load_connections, load_transfers

    stops = load_stops()
    connections = load_connections()
    transfers = load_transfers(stops)

    connection_counts = [
        len(edges) for edges in connections.values()
    ]

    print("\n===== CONNECTION =====")
    print("Stops with connection records:", len(connections))
    print("Total connection records:", sum(connection_counts))
    print("Maximum connections from one stop:",
          max(connection_counts, default=0))

    # Count unique directed stop pairs before building the graph
    unique_pairs = set()

    for start, edges in connections.items():
        for edge in edges:
            unique_pairs.add((start, edge["destination"]))

    print("\n===== RAW EDGEs =====")
    print("Total scheduled connections:",
          sum(len(edges) for edges in connections.values()))

    print("Unique directed stop pairs:", len(unique_pairs))

    print("Duplicate scheduled connections:",
          sum(len(edges) for edges in connections.values()) - len(unique_pairs))

    subway_graph = build_graph(stops, connections, transfers)

    # Count stops that appear in actual train trips.
    active_stops = set(connections.keys())

    for edges in connections.values():
        for edge in edges:
            active_stops.add(edge["destination"])

    # Check for stop IDs referenced by trips but missing
    # from stops.txt.
    missing_stops = active_stops - set(stops.keys())

    # Count original scheduled connections.
    original_connections = sum(
        len(edges) for edges in connections.values()
    )

    print("\n===== SUBWAY GRAPH VALIDATION =====")

    print("Total stop records:", len(stops))
    print("Stops used in train trips:", len(active_stops))
    print("Stops with outgoing connections:", len(connections))
    print("Original scheduled connections:", original_connections)
    print("Unique directed edges:", subway_graph.get_edge_count())
    print("Stop IDs missing from stops.txt:", len(missing_stops))

    if missing_stops:
        print("Examples of missing stops:", list(missing_stops)[:10])

    print("\n===== SAMPLE CONNECTIONS =====")

    for stop_id in list(subway_graph.adjacency.keys())[:10]:
        neighbors = subway_graph.get_neighbors(stop_id)

        if neighbors:
            print(stop_id, "->", neighbors)

        # Count stops with actual outgoing and incoming edges
    stops_with_outgoing = set()
    stops_with_incoming = set()

    for start, neighbors in subway_graph.adjacency.items():
        if neighbors:
            stops_with_outgoing.add(start)

        for destination in neighbors:
            stops_with_incoming.add(destination)

    connected_stops = stops_with_outgoing | stops_with_incoming

    isolated_stops = set(stops.keys()) - connected_stops

    print("\n===== NETWORK CONNECTIVITY =====")
    print("Stops with outgoing edges:", len(stops_with_outgoing))
    print("Stops with incoming edges:", len(stops_with_incoming))
    print("Total connected stops:", len(connected_stops))
    print("Isolated stops:", len(isolated_stops))

    print("\n===== UNIQUE DESTINATION COUNTS =====")

    destination_counts = []

    for stop_id, neighbors in subway_graph.adjacency.items():
        if neighbors:
            destination_counts.append(len(neighbors))

    print("Stops with actual outgoing edges:", len(destination_counts))
    print("Average unique destinations per stop:",
          sum(destination_counts) / len(destination_counts))
    print("Maximum unique destinations:", max(destination_counts))

    print("\nStops with the most unique destinations:")

    sorted_stops = sorted(
        subway_graph.adjacency.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    for stop_id, neighbors in sorted_stops[:10]:
        if neighbors:
            print(stop_id, "->", len(neighbors), "destinations")
'''