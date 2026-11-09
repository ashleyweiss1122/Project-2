
from parser import load_stops, load_connections, load_transfers
from graph import build_graph
from algorithms import dijkstra, a_star
from visualization import ComparisonWindow
from visualization_adapter import (convert_graph_for_visualization, convert_results_for_visualization)


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

    # convert data for visualization
    visual_graph = convert_graph_for_visualization(subway_graph)

    visual_results = convert_results_for_visualization(
        start,
        destination,
        dijkstra_result,
        astar_result
    )

    # launch visualization
    window = ComparisonWindow(visual_graph, visual_results)
    window.show()


if __name__ == "__main__":
    main()
