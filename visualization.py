"""Two Matplotlib panels with playback of saved search expansions."""

from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.widgets import Button, Slider


UNEXPLORED = "#9ca3af"
EXPANDED = "#2563eb"
ORIGIN = "#15803d"
DESTINATION = "#b91c1c"
ROUTE = "#d49b00"


class ComparisonWindow:
    """Own the figure, playback state, and controls in one place."""

    def __init__(self, graph, results):
        if len(results["results"]) != 2:
            raise ValueError("Expected exactly two algorithm results.")

        self.results = results
        self.tick = 0
        self.playing = False
        self.last_tick = max(len(result["expanded_order"]) for result in results["results"])
        self.positions = {node["id"]: (node["x"], node["y"]) for node in graph["nodes"]}
        self.node_ids = list(self.positions)

        self.figure, axes = plt.subplots(1, 2, figsize=(12, 7), sharex=True, sharey=True)
        self.figure.subplots_adjust(left=0.06, right=0.96, bottom=0.32, top=0.80, wspace=0.20)
        self.figure.suptitle("Metro optimization — MOCK DATA", fontsize=18)
        self.figure.text(0.5, 0.89, "One expansion per tick in each unfinished panel. Playback is not execution time.",
                         ha="center", fontsize=10)
        self.figure.text(0.5, 0.85,
                         "Blue: expanded nodes/arrival paths   Gold: final route   Green/red outlines: origin/destination",
                         ha="center", fontsize=9)

        self.panels = [self.draw_panel(axis, graph, result)
                       for axis, result in zip(axes, results["results"])]

        # Keep widgets on self so they remain alive while the window is open.
        self.play_button = Button(self.figure.add_axes([0.13, 0.14, 0.18, 0.06]), "Play")
        self.step_button = Button(self.figure.add_axes([0.41, 0.14, 0.18, 0.06]), "Step")
        self.reset_button = Button(self.figure.add_axes([0.69, 0.14, 0.18, 0.06]), "Reset")
        self.speed_slider = Slider(self.figure.add_axes([0.30, 0.06, 0.45, 0.03]),
                                   "Expansions/sec", 1, 10, valinit=2, valstep=1)
        self.play_button.on_clicked(self.toggle_play)
        self.step_button.on_clicked(self.step)
        self.reset_button.on_clicked(self.reset)
        self.speed_slider.on_changed(self.change_speed)

        # A Matplotlib timer calls advance() periodically without blocking clicks.
        self.timer = self.figure.canvas.new_timer(interval=500)
        self.timer.add_callback(self.advance)
        self.figure.canvas.mpl_connect("close_event", self.pause)
        self.render()

    def draw_panel(self, axis, graph, result):
        """Create shapes once; render() will only update their colors and text."""
        axis.set_title("A*" if result["algorithm"] == "astar" else result["algorithm"].title())
        axis.set_aspect("equal", adjustable="box")
        axis.set_axis_off()
        edges = []
        small_graph = len(self.node_ids) <= 10
        node_size = 650 if small_graph else 280
        shrink = 16 if small_graph else 11
        for edge in graph["edges"]:
            start = self.positions[edge["source"]]
            end = self.positions[edge["target"]]
            arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14,
                                    shrinkA=shrink, shrinkB=shrink, color=UNEXPLORED,
                                    linewidth=1.5, zorder=1)
            axis.add_patch(arrow)
            edges.append((edge["source"], edge["target"], arrow))
            # Offset the weight from the midpoint so it doesn't sit on the line.
            axis.annotate(str(edge["weight"]),
                          xy=((start[0] + end[0]) / 2, (start[1] + end[1]) / 2),
                          xytext=(0, 9), textcoords="offset points", ha="center",
                          fontsize=9 if small_graph else 8, bbox={"facecolor": "white", "edgecolor": "none", "pad": 1}, zorder=3)

        points = [self.positions[node_id] for node_id in self.node_ids]
        scatter = axis.scatter([p[0] for p in points], [p[1] for p in points], s=node_size, zorder=4)
        labels = {}
        for node_id, (x, y) in self.positions.items():
            labels[node_id] = axis.text(x, y, str(node_id), ha="center", va="center", color="white", fontsize=10 if small_graph else 8, zorder=5)

        # Explicit shared limits keep both maps identical and leave room for nodes.
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        pad_x, pad_y = max(max(xs) - min(xs), 1) * 0.15, max(max(ys) - min(ys), 1) * 0.20
        axis.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
        axis.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
        # Figure coordinates reserve status space even as the graph grows.
        box = axis.get_position()
        status = self.figure.text((box.x0 + box.x1) / 2, 0.29, "", ha="center", va="top", fontsize=9)
        return {"result": result, "scatter": scatter, "edges": edges, "status": status, "labels": labels}

    def render(self):
        """Turn the current tick into colors and labels in both panels."""
        for panel in self.panels:
            result = panel["result"]
            trace = result["expanded_order"]
            count = min(self.tick, len(trace))
            expanded = set(trace[:count])
            finished = self.tick >= len(trace)
            path = result["path"] if finished and result["found"] else []
            route_nodes = set(path)
            route_edges = set(zip(path, path[1:]))

            # Reveal the recorded predecessor edge only when its node is expanded.
            # Merely checking an outgoing edge must not turn it blue.
            arrivals = result.get("arrival_edges", [])
            traversed_edges = {tuple(edge) for edge in arrivals[:count]
                               if edge is not None and edge[0] in expanded and edge[1] in expanded}

            colors = []
            outlines = []
            for node_id in self.node_ids:
                color = EXPANDED if node_id in expanded else UNEXPLORED
                if node_id == self.results["start"]:
                    color = ORIGIN
                if node_id == self.results["goal"]:
                    color = DESTINATION
                # Completed route takes color priority, including both endpoints.
                colors.append(ROUTE if node_id in route_nodes else color)
                outlines.append(ORIGIN if node_id == self.results["start"] else
                                DESTINATION if node_id == self.results["goal"] else "white")
            panel["scatter"].set_facecolors(colors)
            panel["scatter"].set_edgecolors(outlines)
            panel["scatter"].set_linewidths(2)
            for node_id, label in panel["labels"].items():
                label.set_color("#111827" if node_id in route_nodes else "white")
            for source, target, arrow in panel["edges"]:
                on_route = (source, target) in route_edges
                explored = (source, target) in traversed_edges
                arrow.set_color(ROUTE if on_route else EXPANDED if explored else UNEXPLORED)
                arrow.set_linewidth(3 if on_route else 2 if explored else 1.5)

            state = "Finished" if finished else "Ready" if self.tick == 0 else "In progress"
            status = f"Expanded: {count}/{len(trace)} — {state}"
            if finished:
                route_text = "Route: " + " → ".join(map(str, path))
                status += ("\n" + fill(route_text, width=52) + f" | Distance: {result['distance']}"
                           if result["found"] else "\nNo route")
            panel["status"].set_text(status)
        self.figure.canvas.draw_idle()

    def advance(self):
        """One timer tick advances both traces; shorter traces stay finished."""
        self.tick = min(self.tick + 1, self.last_tick)
        self.render()
        if self.tick >= self.last_tick:
            self.pause()

    def toggle_play(self, event=None):
        if self.playing:
            self.pause()
        elif self.tick < self.last_tick:
            self.playing = True
            self.play_button.label.set_text("Pause")
            self.timer.start()
            self.figure.canvas.draw_idle()

    def pause(self, event=None):
        self.timer.stop()
        self.playing = False
        self.play_button.label.set_text("Play")
        self.figure.canvas.draw_idle()

    def step(self, event=None):
        self.pause()
        self.advance()

    def reset(self, event=None):
        self.pause()
        self.tick = 0
        self.render()

    def change_speed(self, value):
        self.timer.interval = int(1000 / value)
        if self.playing:
            self.timer.stop()
            self.timer.start()

    def show(self):
        plt.show()
