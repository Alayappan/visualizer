---
name: graph-visualization
description: Use when developing, optimizing, or debugging interactive graph visualizations, Tkinter Canvas rendering, spring layout physics, zoom/pan/drag controls, and node/link click events in the desktop app.
---

# Graph Visualization Skill (Tkinter Canvas)

## 1. Overview & Purpose
This skill covers the interactive graph rendering engine implemented in [`src/gui/graph_canvas.py`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/src/gui/graph_canvas.py) using a native Tkinter Canvas and NetworkX.

It provides detailed instructions for calculating force-directed layouts, rendering nodes and directed relations, handling viewport transformations (pan and zoom), and real-time node dragging.

---

## 2. Visual Elements & Specifications

### 2.1 Nodes
- **Representation:** Circles drawn via `canvas.create_oval()` with high-contrast fill and outline.
- **Labels:** Node `name` displayed centered within the circle.
- **Identifier:** Retains original UUID from `nodes.csv`.
- **Interactions:**
  - Left-Click: Selects node, highlights with golden outline (`#f59e0b`), and fires `on_node_selected`.
  - Left-Drag: Repositions node in real-time, dynamically updating all connected edges and labels.

### 2.2 Relationships (Edges)
- **Representation:** Directional lines drawn via `canvas.create_line()` with arrowheads (`arrow=tk.LAST`).
- **Endpoint Offsetting:** Endpoints are offset from node centers by the circle radius so arrows point directly to the node border.
- **Labels:** Text element with background pill rectangle showing `relationship_name`.
- **Self-loops:** Rendered as smooth ovals looping above the node.
- **Interactions:**
  - Left-Click: Selects relationship, highlights in amber, and fires `on_relation_selected`.

---

## 3. Coordinate Transformation (World <-> Screen)

```python
def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
    sx = wx * self.scale + self.offset_x
    sy = wy * self.scale + self.offset_y
    return sx, sy

def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
    wx = (sx - self.offset_x) / self.scale
    wy = (sy - self.offset_y) / self.scale
    return wx, wy
```

---

## 4. Pan & Zoom Behaviors

1. **Zoom Around Cursor:**
   When the user scrolls the mouse wheel at screen point `(cx, cy)`:
   - Convert `(cx, cy)` to world coordinates `(wx, wy)`.
   - Update `scale = scale * factor`.
   - Adjust offsets: `offset_x = cx - wx * scale` and `offset_y = cy - wy * scale`.
   - Redraw canvas.
2. **Smooth Pan:**
   On mouse drag (middle button, right button, or left button on empty canvas):
   - `dx = event.x - pan_start_x`
   - `dy = event.y - pan_start_y`
   - `offset_x += dx`, `offset_y += dy`
   - Redraw canvas.
3. **Fit to Screen:**
   Calculate bounding box of all node positions and compute scale to fit canvas width/height minus padding.

---

## 5. Verification & Testing
Run GUI unit tests:
```bash
pytest tests/test_gui.py -k TestGraphCanvas -v
```
Verify:
- Node positions calculated correctly.
- Zoom and pan modify scale and offsets predictably.
- Node selection updates canvas item highlights.
