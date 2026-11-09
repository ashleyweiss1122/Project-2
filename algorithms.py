import math

def haversine_distance(stop_a, stop_b):
    # calculate straight-line distance between two subway stops
    # returns distance in meters

    lat1 = math.radians(stop_a["latitude"])
    lon1 = math.radians(stop_a["longitude"])
    lat2 = math.radians(stop_b["latitude"])
    lon2 = math.radians(stop_b["longitude"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # in meters
    earth_radius = 6371000

    return earth_radius * c

def heuristic(graph, current, destination):
    # estimate remaining travel time in seconds.

    current_stop = graph.vertices[current]
    destination_stop = graph.vertices[destination]

    distance = haversine_distance(current_stop, destination_stop)

    # maximum possible subway speed: 100 meters/second.
    maximum_speed = 100

    return distance / maximum_speed


def a_star(graph, start, destination):
    # find shortest travel time path using A*

    distances = {stop: float("inf") for stop in graph.vertices}
    previous = {}

    distances[start] = 0

    heap = MinHeap()
    heap.push(heuristic(graph, start, destination), start)

    nodes_explored = 0
    expanded_order = []
    arrival_edges = []

    while not heap.is_empty():
        current_f, current = heap.pop()

        if current_f > distances[current] + heuristic(graph, current, destination) + 0.000001:
            continue

        nodes_explored += 1
        expanded_order.append(current)

        if current == start:
            arrival_edges.append(None)
        else:
            arrival_edges.append((previous[current], current))

        if current == destination:
            break

        for neighbor, edge in graph.get_neighbors(current).items():
            new_distance = distances[current] + edge["travel_time"]

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current

                estimated_total = (
                        new_distance + heuristic(graph, neighbor, destination)
                )

                heap.push(estimated_total, neighbor)

    #reconstruct shortest path
    path = []

    if distances[destination] != float("inf"):
        current = destination

        while current in previous:
            path.append(current)
            current = previous[current]

        path.append(start)
        path.reverse()

    return {
        "path": path,
        "travel_time": distances[destination],
        "nodes_explored": nodes_explored,
        "expanded_order": expanded_order,
        "arrival_edges": arrival_edges,
        "found": len(path) > 0
    }


class MinHeap:
    # priority queue using min heap
    def __init__(self):
        self.heap = []

    def push(self, priority, item):
        self.heap.append((priority, item))
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        minimum = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._bubble_down(0)

        return minimum

    def _bubble_up(self, index):
        while index > 0:
            parent = (index - 1) // 2

            if self.heap[index][0] >= self.heap[parent][0]:
                break

            self.heap[index], self.heap[parent] = (
                self.heap[parent], self.heap[index]
            )

            index = parent

    def _bubble_down(self, index):
        size = len(self.heap)

        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            smallest = index

            if left < size and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left

            if right < size and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = (
                self.heap[smallest], self.heap[index]
            )

            index = smallest

    def is_empty(self):
        return len(self.heap) == 0

def dijkstra(graph, start, destination):
    # find shortest travel time using Dijkstra's algorithm

    distances = {stop: float("inf") for stop in graph.vertices}
    previous = {}

    distances[start] = 0

    priority_queue = MinHeap()
    priority_queue.push(0, start)

    nodes_explored = 0
    expanded_order = []
    arrival_edges = []

    while not priority_queue.is_empty():
        current_distance, current_stop = priority_queue.pop()

        if current_distance > distances[current_stop]:
            continue

        nodes_explored += 1
        expanded_order.append(current_stop)

        if current_stop == start:
            arrival_edges.append(None)
        else:
            arrival_edges.append((previous[current_stop], current_stop))

        if current_stop == destination:
            break

        for neighbor, edge_info in graph.get_neighbors(current_stop).items():
            travel_time = edge_info["travel_time"]
            new_distance = current_distance + travel_time

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_stop

                priority_queue.push(new_distance, neighbor)

    # reconstruct shortest path
    path = []

    if distances[destination] != float("inf"):
        current = destination

        while current != start:
            path.append(current)
            current = previous[current]

        path.append(start)
        path.reverse()

    return {
        "path": path,
        "travel_time": distances[destination],
        "nodes_explored": nodes_explored,
        "expanded_order": expanded_order,
        "arrival_edges": arrival_edges,
        "found": len(path) > 0
    }
