"""Interactive 3D graph canvas component built with Tkinter Canvas."""
import math
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple, Callable, Any, Set
import networkx as nx

from src.models import Node, Relation, Graph
from src.gui.theme import (
    CANVAS_BG, GRID_COLOR,
    NODE_FILL, NODE_OUTLINE, NODE_TEXT, NODE_RADIUS,
    NODE_SELECTED_FILL, NODE_SELECTED_OUTLINE,
    NODE_SHADOW, NODE_SPECULAR, NODE_SELECTED_SPECULAR,
    EDGE_COLOR, EDGE_HOVER_COLOR, EDGE_SELECTED_COLOR, EDGE_TEXT, EDGE_TEXT_BG,
    ACCENT_CYAN, WARNING_AMBER
)


def calculate_edge_geometry(
    sx: float,
    sy: float,
    tx: float,
    ty: float,
    rs: float,
    rt: float,
    h: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate start/end endpoints, Bezier control point, and midpoint badge position.
    
    If h == 0: straight line entering/leaving nodes at their borders.
    If h != 0: quadratic Bezier curve bowing out by h pixels along the perpendicular normal,
               with endpoints adjusted tangent to the curve entering/leaving node perimeters.
    """
    dx = tx - sx
    dy = ty - sy
    dist = math.hypot(dx, dy)

    if dist < 1e-4:
        return {
            "points": [sx, sy, tx, ty],
            "label": (sx, sy),
            "is_curved": False
        }

    if abs(h) < 1.0:
        # Straight line
        if dist > (rs + rt):
            start_x = sx + (dx / dist) * rs
            start_y = sy + (dy / dist) * rs
            end_x = tx - (dx / dist) * rt
            end_y = ty - (dy / dist) * rt
        else:
            start_x, start_y = sx, sy
            end_x, end_y = tx, ty

        label_x = (start_x + end_x) / 2
        label_y = (start_y + end_y) / 2
        return {
            "points": [start_x, start_y, end_x, end_y],
            "label": (label_x, label_y),
            "is_curved": False
        }

    # Quadratic Bezier Curve with offset h along perpendicular unit normal
    mx = (sx + tx) / 2.0
    my = (sy + ty) / 2.0
    nx_unit = -dy / dist
    ny_unit = dx / dist
    cx = mx + nx_unit * h
    cy = my + ny_unit * h

    # Tangent at target node: vector from C to T
    vxt = tx - cx
    vyt = ty - cy
    dist_t = math.hypot(vxt, vyt)
    if dist_t > rt:
        end_x = tx - (vxt / dist_t) * rt
        end_y = ty - (vyt / dist_t) * rt
    else:
        end_x, end_y = tx, ty

    # Tangent at source node: vector from S to C
    vxs = cx - sx
    vys = cy - sy
    dist_s = math.hypot(vxs, vys)
    if dist_s > rs:
        start_x = sx + (vxs / dist_s) * rs
        start_y = sy + (vys / dist_s) * rs
    else:
        start_x, start_y = sx, sy

    # Label position at quadratic Bezier apex P(t=0.5):
    # P(0.5) = 0.25 * S + 0.5 * C + 0.25 * T
    label_x = 0.25 * start_x + 0.5 * cx + 0.25 * end_x
    label_y = 0.25 * start_y + 0.5 * cy + 0.25 * end_y

    return {
        "points": [start_x, start_y, cx, cy, end_x, end_y],
        "label": (label_x, label_y),
        "is_curved": True
    }


class GraphCanvas(tk.Frame):
    """
    High-performance interactive 3D graph visualization canvas.
    Supports 3D perspective projection, camera orbit (pitch & yaw),
    real-time 3D node dragging with elevation lift, depth sorting,
    and curved directed lines for bidirectional and multi-edge relations.
    """

    def __init__(
        self,
        parent,
        on_node_selected: Optional[Callable[[Node], None]] = None,
        on_relation_selected: Optional[Callable[[Relation], None]] = None,
        on_selection_cleared: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(parent, bg=CANVAS_BG, **kwargs)
        self.on_node_selected = on_node_selected
        self.on_relation_selected = on_relation_selected
        self.on_selection_cleared = on_selection_cleared

        # Data & 3D coordinates: uuid -> (world_x, world_y, world_z)
        self.graph: Optional[Graph] = None
        self.node_positions: Dict[str, Tuple[float, float, float]] = {}

        # Viewport transformation & 3D camera
        self.scale: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.camera_pitch: float = 0.38   # Tilt angle in radians (downwards view)
        self.camera_yaw: float = 0.52     # Orbit angle in radians (azimuth)
        self.camera_dist: float = 1100.0  # Camera distance along view axis
        self.focal_length: float = 850.0  # Perspective focal length

        # Auto-rotation turntable state
        self.auto_rotate: bool = False
        self.auto_rotate_job: Optional[str] = None

        # State tracking
        self.selected_node_uuid: Optional[str] = None
        self.selected_rel_uuid: Optional[str] = None
        self.dragged_node_uuid: Optional[str] = None
        self.drag_start_screen: Tuple[float, float] = (0.0, 0.0)

        self.is_panning: bool = False
        self.pan_start_x: float = 0.0
        self.pan_start_y: float = 0.0

        self.is_orbiting: bool = False
        self.orbit_start_x: float = 0.0
        self.orbit_start_y: float = 0.0

        # Canvas item mappings
        self.node_items: Dict[str, List[int]] = {}     # uuid -> [shadow_id, circle_id, hl_id, text_id]
        self.edge_items: Dict[str, List[int]] = {}     # rel_uuid -> [line_id, bg_id, text_id]
        self.item_to_entity: Dict[int, Tuple[str, Any]] = {}  # canvas_id -> ('node'/'rel', object)

        self._build_canvas()
        self._bind_events()

    def _build_canvas(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            bg=CANVAS_BG,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

    def _bind_events(self):
        # Left-click & drag: Select, Node drag, or Pan
        self.canvas.bind("<ButtonPress-1>", self._on_left_click_press)
        self.canvas.bind("<B1-Motion>", self._on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)

        # Right-click or middle-click: 3D camera orbit rotation
        self.canvas.bind("<ButtonPress-2>", self._on_orbit_start)
        self.canvas.bind("<B2-Motion>", self._on_orbit_motion)
        self.canvas.bind("<ButtonRelease-2>", self._on_orbit_end)

        self.canvas.bind("<ButtonPress-3>", self._on_orbit_start)
        self.canvas.bind("<B3-Motion>", self._on_orbit_motion)
        self.canvas.bind("<ButtonRelease-3>", self._on_orbit_end)

        # Zoom with scroll wheel
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.zoom(1.15, e.x, e.y))
        self.canvas.bind("<Button-5>", lambda e: self.zoom(0.85, e.x, e.y))

        # Canvas resize
        self.canvas.bind("<Configure>", self._on_resize)

    # -------------------------------------------------------------------------
    # 3D Math & Coordinate Projections
    # -------------------------------------------------------------------------

    def project_3d(self, wx: float, wy: float, wz: float = 0.0) -> Tuple[float, float, float, float]:
        """
        Project 3D world coordinates (wx, wy, wz) onto 2D canvas screen coordinates.
        Returns: (screen_x, screen_y, view_depth_z2, perspective_scale)
        """
        cos_yaw = math.cos(self.camera_yaw)
        sin_yaw = math.sin(self.camera_yaw)
        x1 = wx * cos_yaw - wz * sin_yaw
        z1 = wx * sin_yaw + wz * cos_yaw

        cos_pitch = math.cos(self.camera_pitch)
        sin_pitch = math.sin(self.camera_pitch)
        y2 = wy * cos_pitch - z1 * sin_pitch
        z2 = wy * sin_pitch + z1 * cos_pitch

        depth = max(60.0, self.camera_dist + z2)
        persp = (self.focal_length / depth) * self.scale
        sx = x1 * persp + self.offset_x
        sy = y2 * persp + self.offset_y
        return sx, sy, z2, persp

    def world_to_screen(self, wx: float, wy: float, wz: float = 0.0) -> Tuple[float, float]:
        """Convert world coordinates to screen (sx, sy). Backward-compatible helper."""
        sx, sy, _, _ = self.project_3d(wx, wy, wz)
        return sx, sy

    def screen_to_world(self, sx: float, sy: float, target_z2: float = 0.0) -> Tuple[float, float, float]:
        """
        Unproject screen coordinates (sx, sy) back into 3D world coordinates (wx, wy, wz)
        at a given camera viewing depth target_z2.
        """
        depth = max(60.0, self.camera_dist + target_z2)
        persp = (self.focal_length / depth) * self.scale
        if abs(persp) < 1e-5:
            persp = 1.0

        x1 = (sx - self.offset_x) / persp
        y2 = (sy - self.offset_y) / persp

        cos_pitch = math.cos(self.camera_pitch)
        sin_pitch = math.sin(self.camera_pitch)
        wy = y2 * cos_pitch + target_z2 * sin_pitch
        z1 = -y2 * sin_pitch + target_z2 * cos_pitch

        cos_yaw = math.cos(self.camera_yaw)
        sin_yaw = math.sin(self.camera_yaw)
        wx = x1 * cos_yaw + z1 * sin_yaw
        wz = -x1 * sin_yaw + z1 * cos_yaw
        return wx, wy, wz

    # -------------------------------------------------------------------------
    # Graph Loading & Layout
    # -------------------------------------------------------------------------

    def set_graph(self, graph: Graph):
        """Set the active graph and compute 3D force-directed node layout."""
        self.graph = graph
        self.selected_node_uuid = None
        self.selected_rel_uuid = None
        self._compute_layout()
        self.fit_to_screen()

    def _compute_layout(self):
        """Calculate node positions in 3D using NetworkX 3D spring layout."""
        if not self.graph or not self.graph.nodes:
            self.node_positions = {}
            return

        G = nx.MultiDiGraph()
        for node in self.graph.nodes:
            G.add_node(node.uuid, name=node.name)
        for rel in self.graph.relations:
            G.add_edge(rel.source_uuid, rel.target_uuid, uuid=rel.relationship_uuid, name=rel.relationship_name)

        # 3D Spring layout calculates coordinates normalized in roughly [-1.0, 1.0]
        pos = nx.spring_layout(
            G,
            dim=3,
            k=2.2 / math.sqrt(max(1, len(self.graph.nodes))),
            iterations=70,
            seed=42
        )

        spread = max(380, len(self.graph.nodes) * 55)
        self.node_positions = {}
        for uuid, coord in pos.items():
            self.node_positions[uuid] = (coord[0] * spread, coord[1] * spread, coord[2] * spread)

    def refresh_graph(self, graph: Graph):
        """Update active graph, preserving existing 3D node positions where possible."""
        self.graph = graph
        if not self.graph or not self.graph.nodes:
            self.node_positions.clear()
            self.redraw()
            return

        current_uuids = {n.uuid for n in self.graph.nodes}
        self.node_positions = {u: pos for u, pos in self.node_positions.items() if u in current_uuids}

        import random
        for node in self.graph.nodes:
            if node.uuid not in self.node_positions:
                jitter_x = random.uniform(-80, 80)
                jitter_y = random.uniform(-80, 80)
                jitter_z = random.uniform(-80, 80)
                self.node_positions[node.uuid] = (jitter_x, jitter_y, jitter_z)

        if self.selected_node_uuid and self.selected_node_uuid not in current_uuids:
            self.selected_node_uuid = None
        if self.selected_rel_uuid and not any(r.relationship_uuid == self.selected_rel_uuid for r in self.graph.relations):
            self.selected_rel_uuid = None

        self.redraw()

    # -------------------------------------------------------------------------
    # Bidirectional & Multi-Edge Pair Grouping
    # -------------------------------------------------------------------------

    def _group_relations_by_pair(self) -> Dict[Tuple[str, str], List[Relation]]:
        """Group relationships by canonical node pair (sorted UUID tuple)."""
        pairs: Dict[Tuple[str, str], List[Relation]] = {}
        if not self.graph:
            return pairs

        for rel in self.graph.relations:
            if rel.source_uuid == rel.target_uuid:
                pair_key = (rel.source_uuid, rel.target_uuid)
            else:
                pair_key = tuple(sorted([rel.source_uuid, rel.target_uuid]))

            if pair_key not in pairs:
                pairs[pair_key] = []
            pairs[pair_key].append(rel)

        return pairs

    # -------------------------------------------------------------------------
    # Rendering (Painter's Algorithm Depth-Sorted)
    # -------------------------------------------------------------------------

    def redraw(self):
        """Render all 3D shadows, curved edges, and glossy spheres onto canvas."""
        self.canvas.delete("all")
        self.node_items.clear()
        self.edge_items.clear()
        self.item_to_entity.clear()

        if not self.graph:
            self._draw_empty_message()
            return

        # 1. Project all nodes into 3D view space: uuid -> (sx, sy, z2, persp, radius)
        projected_nodes: Dict[str, Tuple[float, float, float, float, float]] = {}
        for node in self.graph.nodes:
            if node.uuid not in self.node_positions:
                continue
            pos = self.node_positions[node.uuid]
            wx, wy, wz = pos[0], pos[1], pos[2]

            # Tactile elevation lift if node is actively dragged:
            if node.uuid == self.dragged_node_uuid:
                wz += 60.0

            sx, sy, z2, persp = self.project_3d(wx, wy, wz)
            r = max(12.0, NODE_RADIUS * persp)
            projected_nodes[node.uuid] = (sx, sy, z2, persp, r)

        # 2. Draw Node Shadows (Painter's bottom layer)
        self._draw_node_shadows(projected_nodes)

        # 3. Draw Edges with Curvature for Two-Way Closed Relations
        self._draw_edges(projected_nodes)

        # 4. Draw 3D Glossy Sphere Nodes (Sorted back-to-front by depth z2)
        self._draw_nodes(projected_nodes)

    def _draw_empty_message(self):
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 600
        self.canvas.create_text(
            w / 2, h / 2,
            text="No graph loaded.\nSelect node and relation CSV files to visualize in 3D.",
            fill=GRID_COLOR,
            font=("Helvetica", 14),
            justify="center",
        )

    def _draw_node_shadows(self, projected: Dict[str, Tuple[float, float, float, float, float]]):
        """Draw 3D floor drop-shadows beneath each node."""
        for uuid, (sx, sy, z2, persp, r) in projected.items():
            is_lifted = (uuid == self.dragged_node_uuid)
            sh_x = sx + 8.0 * persp
            sh_y = sy + (12.0 if not is_lifted else 26.0) * persp
            sh_rx = r * 1.05
            sh_ry = r * 0.55

            self.canvas.create_oval(
                sh_x - sh_rx, sh_y - sh_ry,
                sh_x + sh_rx, sh_y + sh_ry,
                fill=NODE_SHADOW,
                outline="",
            )

    def _draw_edges(self, projected: Dict[str, Tuple[float, float, float, float, float]]):
        """Calculate Bezier curves for two-way relations and render depth-sorted."""
        if not self.graph:
            return

        grouped = self._group_relations_by_pair()
        edge_render_list: List[Dict[str, Any]] = []

        for pair_key, rels in grouped.items():
            u, v = pair_key

            # Self-loop handling
            if u == v:
                if u not in projected:
                    continue
                sx, sy, z2, persp, r = projected[u]
                for rel in rels:
                    edge_render_list.append({
                        "avg_depth": z2,
                        "rel": rel,
                        "type": "self_loop",
                        "node_proj": (sx, sy, z2, persp, r),
                        "is_selected": (rel.relationship_uuid == self.selected_rel_uuid),
                        "persp": persp,
                    })
                continue

            if u not in projected or v not in projected:
                continue

            u_proj = projected[u]
            v_proj = projected[v]

            forward_rels = [r for r in rels if r.source_uuid == u]
            reverse_rels = [r for r in rels if r.source_uuid == v]
            avg_depth = (u_proj[2] + v_proj[2]) / 2.0

            # Determine curve offsets h:
            # If two-way relation (both directions exist), bow them gracefully apart!
            is_bidirectional = (len(forward_rels) > 0 and len(reverse_rels) > 0)
            base_curve = 38.0 * min(self.scale, 1.4)

            # Forward edges
            for i, rel in enumerate(forward_rels):
                if is_bidirectional:
                    h = base_curve + i * 26.0
                elif len(forward_rels) > 1:
                    # Multi-edge same direction: symmetric spread
                    h = (i - (len(forward_rels) - 1) / 2.0) * 32.0
                else:
                    h = 0.0

                geom = calculate_edge_geometry(
                    u_proj[0], u_proj[1],
                    v_proj[0], v_proj[1],
                    u_proj[4], v_proj[4],
                    h=h
                )
                edge_render_list.append({
                    "avg_depth": avg_depth,
                    "rel": rel,
                    "type": "normal",
                    "geom": geom,
                    "is_selected": (rel.relationship_uuid == self.selected_rel_uuid),
                    "persp": (u_proj[3] + v_proj[3]) / 2.0,
                })

            # Reverse edges
            for j, rel in enumerate(reverse_rels):
                if is_bidirectional:
                    h = base_curve + j * 26.0
                elif len(reverse_rels) > 1:
                    h = (j - (len(reverse_rels) - 1) / 2.0) * 32.0
                else:
                    h = 0.0

                geom = calculate_edge_geometry(
                    v_proj[0], v_proj[1],
                    u_proj[0], u_proj[1],
                    v_proj[4], u_proj[4],
                    h=h
                )
                edge_render_list.append({
                    "avg_depth": avg_depth,
                    "rel": rel,
                    "type": "normal",
                    "geom": geom,
                    "is_selected": (rel.relationship_uuid == self.selected_rel_uuid),
                    "persp": (u_proj[3] + v_proj[3]) / 2.0,
                })

        # Painter's Algorithm: Sort edges back-to-front by depth
        edge_render_list.sort(key=lambda item: item["avg_depth"])

        for item in edge_render_list:
            rel = item["rel"]
            is_selected = item["is_selected"]
            persp = item["persp"]
            color = EDGE_SELECTED_COLOR if is_selected else EDGE_COLOR
            width = max(2, int((3 if is_selected else 2) * min(persp, 1.4)))

            if item["type"] == "self_loop":
                sx, sy, _, _, r = item["node_proj"]
                loop_r = r * 1.5
                line_id = self.canvas.create_oval(
                    sx - loop_r, sy - 2 * loop_r,
                    sx + loop_r, sy,
                    outline=color,
                    width=width,
                )
                label_x = sx
                label_y = sy - 2 * loop_r - 8
            else:
                geom = item["geom"]
                arrow_w = max(6, int(10 * persp))
                arrow_l = max(8, int(12 * persp))
                arrow_a = max(3, int(5 * persp))

                line_id = self.canvas.create_line(
                    *geom["points"],
                    fill=color,
                    width=width,
                    arrow=tk.LAST,
                    arrowshape=(arrow_w, arrow_l, arrow_a),
                    smooth=geom["is_curved"],
                )
                label_x, label_y = geom["label"]

            # Edge relationship name badge
            font_size = max(8, int(9 * min(persp, 1.3)))
            text_id = self.canvas.create_text(
                label_x, label_y,
                text=rel.relationship_name,
                fill=EDGE_TEXT if not is_selected else WARNING_AMBER,
                font=("Helvetica", font_size, "bold" if is_selected else "normal"),
            )

            bbox = self.canvas.bbox(text_id)
            if bbox:
                bg_id = self.canvas.create_rectangle(
                    bbox[0] - 3, bbox[1] - 1, bbox[2] + 3, bbox[3] + 1,
                    fill=EDGE_TEXT_BG,
                    outline=EDGE_HOVER_COLOR if not is_selected else WARNING_AMBER,
                    width=1,
                )
                self.canvas.tag_lower(bg_id, text_id)
            else:
                bg_id = 0

            self.edge_items[rel.relationship_uuid] = [line_id, bg_id, text_id]
            self.item_to_entity[line_id] = ("rel", rel)
            if bg_id:
                self.item_to_entity[bg_id] = ("rel", rel)
            self.item_to_entity[text_id] = ("rel", rel)

    def _draw_nodes(self, projected: Dict[str, Tuple[float, float, float, float, float]]):
        """Draw 3D glossy spheres with specular reflection, sorted back-to-front."""
        if not self.graph:
            return

        # Sort nodes by depth z2 ascending (furthest first, nearest last)
        sorted_nodes = []
        for node in self.graph.nodes:
            if node.uuid in projected:
                sorted_nodes.append((projected[node.uuid][2], node))
        sorted_nodes.sort(key=lambda x: x[0])

        for _, node in sorted_nodes:
            sx, sy, z2, persp, r = projected[node.uuid]
            is_selected = (node.uuid == self.selected_node_uuid)
            is_lifted = (node.uuid == self.dragged_node_uuid)

            fill_color = NODE_SELECTED_FILL if is_selected else NODE_FILL
            outline_color = NODE_SELECTED_OUTLINE if is_selected else NODE_OUTLINE
            outline_width = max(2, int((3 if (is_selected or is_lifted) else 2) * min(persp, 1.4)))

            # 1. Base 3D Sphere Body
            circle_id = self.canvas.create_oval(
                sx - r, sy - r, sx + r, sy + r,
                fill=fill_color,
                outline=outline_color,
                width=outline_width,
            )

            # 2. 3D Specular Highlight (creates curvature shine on top-left)
            hl_x = sx - r * 0.32
            hl_y = sy - r * 0.32
            hl_r = max(2.0, r * 0.36)
            hl_color = NODE_SELECTED_SPECULAR if is_selected else NODE_SPECULAR
            hl_id = self.canvas.create_oval(
                hl_x - hl_r, hl_y - hl_r,
                hl_x + hl_r, hl_y + hl_r,
                fill=hl_color,
                outline="",
            )

            # 3. Label Text
            display_name = node.name
            if len(display_name) > 12:
                display_name = display_name[:11] + "…"

            font_size = max(8, int(10 * min(persp, 1.4)))
            text_id = self.canvas.create_text(
                sx, sy,
                text=display_name,
                fill=NODE_TEXT,
                font=("Helvetica", font_size, "bold"),
            )

            self.node_items[node.uuid] = [circle_id, hl_id, text_id]
            self.item_to_entity[circle_id] = ("node", node)
            self.item_to_entity[hl_id] = ("node", node)
            self.item_to_entity[text_id] = ("node", node)

    # -------------------------------------------------------------------------
    # Viewport Zoom, Pan & 3D Fit
    # -------------------------------------------------------------------------

    def zoom(self, factor: float, center_x: Optional[float] = None, center_y: Optional[float] = None):
        """Zoom in or out centered at given screen coordinate."""
        new_scale = max(0.15, min(4.5, self.scale * factor))
        if abs(new_scale - self.scale) < 1e-4:
            return

        if center_x is None:
            center_x = (self.canvas.winfo_width() or 800) / 2
        if center_y is None:
            center_y = (self.canvas.winfo_height() or 600) / 2

        # Scale relative to center
        self.offset_x = center_x - (center_x - self.offset_x) * (new_scale / self.scale)
        self.offset_y = center_y - (center_y - self.offset_y) * (new_scale / self.scale)
        self.scale = new_scale
        self.redraw()

    def zoom_in(self):
        self.zoom(1.2)

    def zoom_out(self):
        self.zoom(0.8)

    def fit_to_screen(self):
        """Scale and center all 3D nodes to fit within current canvas dimensions."""
        if not self.node_positions:
            self.scale = 1.0
            self.offset_x = (self.canvas.winfo_width() or 800) / 2
            self.offset_y = (self.canvas.winfo_height() or 600) / 2
            self.redraw()
            return

        # Project all nodes with scale=1.0 and offset=(0, 0)
        old_scale = self.scale
        old_ox, old_oy = self.offset_x, self.offset_y
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        projected = [self.project_3d(pos[0], pos[1], pos[2]) for pos in self.node_positions.values()]
        xs = [p[0] for p in projected]
        ys = [p[1] for p in projected]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        canvas_w = max(200, self.canvas.winfo_width() or 800)
        canvas_h = max(200, self.canvas.winfo_height() or 600)

        span_x = max(120.0, max_x - min_x + 140.0)
        span_y = max(120.0, max_y - min_y + 140.0)

        scale_x = (canvas_w - 90) / span_x
        scale_y = (canvas_h - 90) / span_y
        self.scale = max(0.25, min(1.8, min(scale_x, scale_y)))

        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        self.offset_x = canvas_w / 2 - mid_x * self.scale
        self.offset_y = canvas_h / 2 - mid_y * self.scale

        self.redraw()

    def reset_layout(self):
        """Recalculate 3D force-directed layout and center view."""
        self._compute_layout()
        self.fit_to_screen()

    def reset_3d_angle(self):
        """Reset camera pitch and yaw to default 3D isometric perspective."""
        self.camera_pitch = 0.38
        self.camera_yaw = 0.52
        self.fit_to_screen()

    def toggle_auto_rotate(self) -> bool:
        """Toggle automatic 3D turntable rotation. Returns current state."""
        self.auto_rotate = not self.auto_rotate
        if self.auto_rotate:
            self._auto_rotate_step()
        else:
            if self.auto_rotate_job:
                self.after_cancel(self.auto_rotate_job)
                self.auto_rotate_job = None
        return self.auto_rotate

    def _auto_rotate_step(self):
        """Single step of 3D turntable rotation."""
        if not self.auto_rotate:
            return
        self.camera_yaw = (self.camera_yaw + 0.012) % (2 * math.pi)
        self.redraw()
        self.auto_rotate_job = self.after(35, self._auto_rotate_step)

    # -------------------------------------------------------------------------
    # Event Handlers: 3D Orbit, Dragging & Panning
    # -------------------------------------------------------------------------

    def _on_left_click_press(self, event):
        # Shift + Left click -> 3D Orbit
        if event.state & 0x0001:
            self._on_orbit_start(event)
            return

        item = self.canvas.find_withtag("current")
        if item:
            canvas_id = item[0]
            if canvas_id in self.item_to_entity:
                kind, entity = self.item_to_entity[canvas_id]
                if kind == "node":
                    self.select_node(entity)
                    self.dragged_node_uuid = entity.uuid
                    self.drag_start_screen = (event.x, event.y)
                    self.redraw()  # Redraw with 3D elevation lift
                    return
                elif kind == "rel":
                    self.select_relation(entity)
                    return

        # Clicked on empty canvas space -> start pan
        self.clear_selection()
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def _on_left_drag(self, event):
        if self.is_orbiting:
            self._on_orbit_motion(event)
            return

        if self.dragged_node_uuid and self.dragged_node_uuid in self.node_positions:
            # Dragging node in 3D viewing plane
            dx = event.x - self.drag_start_screen[0]
            dy = event.y - self.drag_start_screen[1]
            self.drag_start_screen = (event.x, event.y)

            cur_wx, cur_wy, cur_wz = self.node_positions[self.dragged_node_uuid]
            _, _, _, persp = self.project_3d(cur_wx, cur_wy, cur_wz)
            if abs(persp) < 1e-4:
                persp = 1.0

            dx_view = dx / persp
            dy_view = dy / persp

            cos_p, sin_p = math.cos(self.camera_pitch), math.sin(self.camera_pitch)
            cos_y, sin_y = math.cos(self.camera_yaw), math.sin(self.camera_yaw)

            # Inverse camera rotation
            y1 = dy_view * cos_p
            z1 = -dy_view * sin_p

            dwx = dx_view * cos_y + z1 * sin_y
            dwy = y1
            dwz = -dx_view * sin_y + z1 * cos_y

            self.node_positions[self.dragged_node_uuid] = (
                cur_wx + dwx,
                cur_wy + dwy,
                cur_wz + dwz
            )
            self.redraw()
        elif self.is_panning:
            # 2D Viewport Pan
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.offset_x += dx
            self.offset_y += dy
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.redraw()

    def _on_left_release(self, event):
        if self.is_orbiting:
            self._on_orbit_end(event)
        if self.dragged_node_uuid:
            self.dragged_node_uuid = None
            self.redraw()  # Settle elevation back down
        self.is_panning = False

    def _on_orbit_start(self, event):
        self.is_orbiting = True
        self.orbit_start_x = event.x
        self.orbit_start_y = event.y

    def _on_orbit_motion(self, event):
        if not self.is_orbiting:
            return
        dx = event.x - self.orbit_start_x
        dy = event.y - self.orbit_start_y

        self.camera_yaw = (self.camera_yaw + dx * 0.007) % (2 * math.pi)
        self.camera_pitch = max(-1.42, min(1.42, self.camera_pitch + dy * 0.007))

        self.orbit_start_x = event.x
        self.orbit_start_y = event.y
        self.redraw()

    def _on_orbit_end(self, event):
        self.is_orbiting = False

    def _on_mouse_wheel(self, event):
        delta = event.delta
        factor = 1.1 if delta > 0 else 0.9
        self.zoom(factor, event.x, event.y)

    def _on_resize(self, event):
        if not self.node_positions and self.graph:
            self.fit_to_screen()

    # -------------------------------------------------------------------------
    # Selection Management
    # -------------------------------------------------------------------------

    def select_node(self, node: Node):
        """Highlight node and notify selection listener."""
        self.selected_node_uuid = node.uuid
        self.selected_rel_uuid = None
        self.redraw()
        if self.on_node_selected:
            self.on_node_selected(node)

    def select_relation(self, relation: Relation):
        """Highlight relationship and notify selection listener."""
        self.selected_rel_uuid = relation.relationship_uuid
        self.selected_node_uuid = None
        self.redraw()
        if self.on_relation_selected:
            self.on_relation_selected(relation)

    def clear_selection(self):
        """Clear highlight and notify listener."""
        if self.selected_node_uuid or self.selected_rel_uuid:
            self.selected_node_uuid = None
            self.selected_rel_uuid = None
            self.redraw()
            if self.on_selection_cleared:
                self.on_selection_cleared()

