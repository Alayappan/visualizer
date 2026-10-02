"""Unit tests for Tkinter GUI components in desktop visualizer."""
import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.models import Node, Relation, Graph
from src.gui.theme import apply_theme
from src.gui.detail_panel import DetailPanel
from src.gui.graph_canvas import GraphCanvas, calculate_edge_geometry
from src.gui.file_selector import FileSelector
from src.gui.app import GraphVisualizerApp


@pytest.fixture(scope="module")
def tk_root():
    """Create a headless Tkinter root window for GUI tests."""
    try:
        root = tk.Tk()
        root.withdraw()  # Keep hidden
        apply_theme(root)
        yield root
        root.destroy()
    except tk.TclError as e:
        pytest.skip(f"Tkinter display not available: {e}")


@pytest.fixture
def sample_graph():
    """Create a sample graph for GUI testing."""
    node1 = Node(name="Server-1", uuid="550e8400-e29b-41d4-a716-446655440000", properties={"cpu": "80%"})
    node2 = Node(name="Database", uuid="550e8400-e29b-41d4-a716-446655440001", properties={"engine": "PostgreSQL"})
    rel = Relation(
        source_uuid="550e8400-e29b-41d4-a716-446655440000",
        target_uuid="550e8400-e29b-41d4-a716-446655440001",
        relationship_name="queries",
        relationship_uuid="550e8400-e29b-41d4-a716-446655440002",
        properties={"port": 5432},
    )
    return Graph(nodes=[node1, node2], relations=[rel], node_count=2, relation_count=1)


class TestDetailPanel:
    """Test DetailPanel display, editing actions, and clearing."""

    def test_display_node(self, tk_root, sample_graph):
        panel = DetailPanel(tk_root)
        panel.set_graph(sample_graph)

        node = sample_graph.nodes[0]
        panel.display_node(node)

        assert panel.title_label.cget("text") == "Node Details"
        panel.clear()
        assert panel.title_label.cget("text") == "Properties Inspector"
        panel.destroy()

    def test_display_relation(self, tk_root, sample_graph):
        panel = DetailPanel(tk_root)
        panel.set_graph(sample_graph)

        rel = sample_graph.relations[0]
        panel.display_relation(rel)

        assert panel.title_label.cget("text") == "Relationship Details"
        panel.destroy()

    def test_display_node_without_properties(self, tk_root):
        node = Node(name="Plain", uuid="550e8400-e29b-41d4-a716-446655440099")
        panel = DetailPanel(tk_root)
        panel.display_node(node)
        assert panel.title_label.cget("text") == "Node Details"
        panel.destroy()

    def test_node_action_callbacks(self, tk_root, sample_graph):
        """Test edit and delete button callbacks when inspecting a node."""
        edited_nodes = []
        deleted_nodes = []

        panel = DetailPanel(
            tk_root,
            on_edit_node=lambda n: edited_nodes.append(n),
            on_delete_node=lambda n: deleted_nodes.append(n),
        )
        panel.set_graph(sample_graph)
        node = sample_graph.nodes[0]
        panel.display_node(node)

        assert panel.btn_edit is not None
        assert panel.btn_delete is not None

        panel.btn_edit.invoke()
        assert len(edited_nodes) == 1
        assert edited_nodes[0].uuid == node.uuid

        panel.btn_delete.invoke()
        assert len(deleted_nodes) == 1
        assert deleted_nodes[0].uuid == node.uuid

        panel.clear()
        assert panel.btn_edit is None
        assert panel.btn_delete is None
        panel.destroy()

    def test_relation_action_callbacks(self, tk_root, sample_graph):
        """Test edit and delete button callbacks when inspecting a relationship."""
        edited_rels = []
        deleted_rels = []

        panel = DetailPanel(
            tk_root,
            on_edit_relation=lambda r: edited_rels.append(r),
            on_delete_relation=lambda r: deleted_rels.append(r),
        )
        panel.set_graph(sample_graph)
        rel = sample_graph.relations[0]
        panel.display_relation(rel)

        assert panel.btn_edit_rel is not None
        assert panel.btn_delete_rel is not None

        panel.btn_edit_rel.invoke()
        assert len(edited_rels) == 1
        assert edited_rels[0].relationship_uuid == rel.relationship_uuid

        panel.btn_delete_rel.invoke()
        assert len(deleted_rels) == 1
        assert deleted_rels[0].relationship_uuid == rel.relationship_uuid

        panel.clear()
        assert panel.btn_edit_rel is None
        assert panel.btn_delete_rel is None
        panel.destroy()


class TestGraphCanvas:
    """Test GraphCanvas rendering, 3D projection, camera orbit, zoom, and curved lines."""

    def test_canvas_layout_and_render(self, tk_root, sample_graph):
        canvas = GraphCanvas(tk_root)
        canvas.set_graph(sample_graph)

        assert len(canvas.node_positions) == 2
        assert sample_graph.nodes[0].uuid in canvas.node_positions
        assert sample_graph.nodes[1].uuid in canvas.node_positions

        # Verify redraw executes
        canvas.redraw()

        # Verify zoom
        initial_scale = canvas.scale
        canvas.zoom_in()
        assert canvas.scale > initial_scale
        canvas.zoom_out()

        # Verify fit to screen and reset layout
        canvas.fit_to_screen()
        canvas.reset_layout()

        # Verify selection
        canvas.select_node(sample_graph.nodes[0])
        assert canvas.selected_node_uuid == sample_graph.nodes[0].uuid
        canvas.clear_selection()
        assert canvas.selected_node_uuid is None

        canvas.select_relation(sample_graph.relations[0])
        assert canvas.selected_rel_uuid == sample_graph.relations[0].relationship_uuid
        canvas.clear_selection()
        assert canvas.selected_rel_uuid is None

        canvas.destroy()

    def test_canvas_self_loop(self, tk_root):
        """Test rendering a self-referencing relationship."""
        node = Node(name="SelfLoop", uuid="550e8400-e29b-41d4-a716-446655440000")
        rel = Relation(
            source_uuid=node.uuid,
            target_uuid=node.uuid,
            relationship_name="loops",
            relationship_uuid="550e8400-e29b-41d4-a716-446655440001",
        )
        graph = Graph(nodes=[node], relations=[rel], node_count=1, relation_count=1)
        canvas = GraphCanvas(tk_root)
        canvas.set_graph(graph)
        canvas.redraw()
        assert len(canvas.edge_items) == 1
        canvas.destroy()

    def test_edge_geometry_calculation(self):
        """Test straight line vs quadratic Bezier curve calculation."""
        # Straight line
        straight = calculate_edge_geometry(0, 0, 100, 0, 20, 20, h=0.0)
        assert straight["is_curved"] is False
        assert len(straight["points"]) == 4
        assert straight["points"][0] == 20
        assert straight["points"][2] == 80
        assert straight["label"] == (50.0, 0.0)

        # Curved line with positive offset
        curved_fwd = calculate_edge_geometry(0, 0, 100, 0, 20, 20, h=30.0)
        assert curved_fwd["is_curved"] is True
        assert len(curved_fwd["points"]) == 6
        assert curved_fwd["label"][1] > 0

        # Curved line in reverse with positive offset
        curved_rev = calculate_edge_geometry(100, 0, 0, 0, 20, 20, h=30.0)
        assert curved_rev["is_curved"] is True
        assert curved_rev["label"][1] < 0

        # Coincident nodes
        coincident = calculate_edge_geometry(50, 50, 50, 50, 20, 20, h=0.0)
        assert coincident["points"] == [50, 50, 50, 50]

    def test_bidirectional_curved_lines(self, tk_root):
        """Test two-way closed relationships render as dual curved arcs."""
        node_a = Node(name="Person A", uuid="550e8400-e29b-41d4-a716-446655440001")
        node_b = Node(name="Person B", uuid="550e8400-e29b-41d4-a716-446655440002")
        rel_ab = Relation(
            source_uuid=node_a.uuid,
            target_uuid=node_b.uuid,
            relationship_name="knows",
            relationship_uuid="550e8400-e29b-41d4-a716-446655440003",
        )
        rel_ba = Relation(
            source_uuid=node_b.uuid,
            target_uuid=node_a.uuid,
            relationship_name="known_by",
            relationship_uuid="550e8400-e29b-41d4-a716-446655440004",
        )
        graph = Graph(nodes=[node_a, node_b], relations=[rel_ab, rel_ba], node_count=2, relation_count=2)

        canvas = GraphCanvas(tk_root)
        canvas.set_graph(graph)
        canvas.redraw()

        assert len(canvas.edge_items) == 2
        assert rel_ab.relationship_uuid in canvas.edge_items
        assert rel_ba.relationship_uuid in canvas.edge_items

        grouped = canvas._group_relations_by_pair()
        pair_key = tuple(sorted([node_a.uuid, node_b.uuid]))
        assert len(grouped[pair_key]) == 2
        canvas.destroy()

    def test_3d_projection_and_depth(self, tk_root):
        """Test 3D projection, depth sorting, and perspective scaling."""
        canvas = GraphCanvas(tk_root)
        canvas.offset_x = 400.0
        canvas.offset_y = 300.0
        canvas.scale = 1.0

        # Point in front vs point in back
        sx1, sy1, z2_front, persp_front = canvas.project_3d(0, 0, 200.0)
        sx2, sy2, z2_back, persp_back = canvas.project_3d(0, 0, -200.0)

        assert persp_front != persp_back
        assert z2_front != z2_back

        # Round-trip screen_to_world
        wx, wy, wz = 80.0, -40.0, 15.0
        sx, sy, z2, _ = canvas.project_3d(wx, wy, wz)
        rec_wx, rec_wy, rec_wz = canvas.screen_to_world(sx, sy, z2)
        assert abs(rec_wx - wx) < 0.1
        assert abs(rec_wy - wy) < 0.1
        assert abs(rec_wz - wz) < 0.1

        canvas.destroy()

    def test_3d_camera_orbit_and_reset(self, tk_root, sample_graph):
        """Test 3D camera orbit rotation and reset angle."""
        canvas = GraphCanvas(tk_root)
        canvas.set_graph(sample_graph)

        initial_pitch = canvas.camera_pitch
        initial_yaw = canvas.camera_yaw

        class DummyEvent:
            x = 100
            y = 100

        canvas._on_orbit_start(DummyEvent())
        assert canvas.is_orbiting is True

        move_event = DummyEvent()
        move_event.x = 150
        move_event.y = 120
        canvas._on_orbit_motion(move_event)
        assert canvas.camera_yaw != initial_yaw
        assert canvas.camera_pitch != initial_pitch

        canvas._on_orbit_end(move_event)
        assert canvas.is_orbiting is False

        # Reset 3D angle
        canvas.reset_3d_angle()
        assert canvas.camera_pitch == 0.38
        assert canvas.camera_yaw == 0.52

        canvas.destroy()

    def test_3d_turntable_auto_rotate(self, tk_root, sample_graph):
        """Test 3D turntable continuous auto-rotation toggle and step."""
        canvas = GraphCanvas(tk_root)
        canvas.set_graph(sample_graph)

        assert canvas.auto_rotate is False
        state = canvas.toggle_auto_rotate()
        assert state is True
        assert canvas.auto_rotate is True

        old_yaw = canvas.camera_yaw
        canvas._auto_rotate_step()
        assert canvas.camera_yaw != old_yaw

        state_off = canvas.toggle_auto_rotate()
        assert state_off is False
        assert canvas.auto_rotate is False

        canvas.destroy()

    def test_3d_node_drag(self, tk_root, sample_graph):
        """Test dragging node in 3D viewing plane with elevation lift."""
        canvas = GraphCanvas(tk_root)
        canvas.set_graph(sample_graph)

        node = sample_graph.nodes[0]
        initial_pos = canvas.node_positions[node.uuid]

        canvas.select_node(node)
        canvas.dragged_node_uuid = node.uuid
        canvas.drag_start_screen = (200.0, 200.0)

        class DummyEvent:
            state = 0
            x = 240
            y = 220

        canvas._on_left_drag(DummyEvent())
        new_pos = canvas.node_positions[node.uuid]
        assert new_pos != initial_pos

        canvas._on_left_release(DummyEvent())
        assert canvas.dragged_node_uuid is None

        canvas.destroy()


class TestFileSelector:
    """Test FileSelector validation state and fixture loading."""

    def test_sample_data_loading(self, tk_root):
        loaded_graphs = []

        def on_loaded(g, np=None, rp=None):
            loaded_graphs.append(g)

        selector = FileSelector(tk_root, on_graph_loaded=on_loaded)
        selector.load_sample_data()

        assert selector.nodes_df is not None
        assert selector.relations_df is not None
        assert len(selector.nodes_df) == 3
        assert len(selector.relations_df) == 2

        selector._on_visualize_click()
        assert len(loaded_graphs) == 1
        assert loaded_graphs[0].node_count == 3
        selector.destroy()

    def test_family_data_loading(self, tk_root):
        loaded_graphs = []

        def on_loaded(g, np=None, rp=None):
            loaded_graphs.append(g)

        selector = FileSelector(tk_root, on_graph_loaded=on_loaded)
        selector.load_family_data()

        assert selector.nodes_df is not None
        assert len(selector.nodes_df) == 8
        assert len(selector.relations_df) == 26

        selector._on_visualize_click()
        assert len(loaded_graphs) == 1
        assert loaded_graphs[0].node_count == 8
        selector.destroy()

    def test_validation_missing_paths(self, tk_root):
        selector = FileSelector(tk_root, on_graph_loaded=lambda g, np=None, rp=None: None)
        assert selector.validate_files() is False
        selector.destroy()


class TestGraphVisualizerApp:
    """Test Master Application state flow, editing, 3D actions, and persistence."""

    def test_app_initialization_and_view_switching(self, tk_root, sample_graph):
        app = GraphVisualizerApp(tk_root)

        # Load graph
        app.on_graph_loaded(sample_graph)
        assert app.current_graph == sample_graph
        assert str(app.btn_zoom_in.cget("state")) == "normal"
        assert str(app.btn_add_node.cget("state")) == "normal"
        assert str(app.btn_add_relation.cget("state")) == "normal"
        assert str(app.btn_save.cget("state")) == "normal"

        # Zoom and fit actions
        app._zoom_in()
        app._zoom_out()
        app._fit_graph()
        app._reset_layout()

        # Node / relation selections
        app._on_node_selected(sample_graph.nodes[0])
        assert app.detail_panel.title_label.cget("text") == "Node Details"

        app._on_relation_selected(sample_graph.relations[0])
        assert app.detail_panel.title_label.cget("text") == "Relationship Details"

        app._on_selection_cleared()
        assert app.detail_panel.title_label.cget("text") == "Properties Inspector"

        # Switch back to upload view
        app.show_upload_view()
        assert str(app.btn_zoom_in.cget("state")) == "disabled"
        assert str(app.btn_add_node.cget("state")) == "disabled"

    def test_app_3d_controls(self, tk_root, sample_graph):
        """Test 3D angle reset and auto-rotate controls in app."""
        app = GraphVisualizerApp(tk_root)
        app.on_graph_loaded(sample_graph)

        assert str(app.btn_reset_3d.cget("state")) == "normal"
        assert str(app.btn_auto_rotate.cget("state")) == "normal"

        app._reset_3d_angle()
        assert app.canvas_widget.camera_pitch == 0.38
        assert app.canvas_widget.camera_yaw == 0.52

        app._toggle_auto_rotate()
        assert app.canvas_widget.auto_rotate is True
        assert "Pause" in str(app.btn_auto_rotate.cget("text"))

        app._toggle_auto_rotate()
        assert app.canvas_widget.auto_rotate is False
        assert "Auto-Rotate" in str(app.btn_auto_rotate.cget("text"))

    def test_app_crud_operations(self, tk_root, sample_graph, tmp_path):
        """Test node and relationship modification and CSV file saving."""
        nodes_file = tmp_path / "test_nodes.csv"
        rels_file = tmp_path / "test_rels.csv"

        app = GraphVisualizerApp(tk_root)
        app.on_graph_loaded(sample_graph, nodes_file, rels_file)

        # Test node addition
        new_node = Node(name="Cache", uuid="550e8400-e29b-41d4-a716-446655440099", properties={"type": "Redis"})
        app.current_graph.add_node(new_node)
        app.canvas_widget.refresh_graph(app.current_graph)
        app._mark_dirty()
        assert app.is_dirty is True
        assert app.current_graph.node_count == 3

        # Test relation addition
        new_rel = Relation(
            source_uuid="550e8400-e29b-41d4-a716-446655440000",
            target_uuid="550e8400-e29b-41d4-a716-446655440099",
            relationship_name="caches",
            relationship_uuid="550e8400-e29b-41d4-a716-446655440088",
        )
        app.current_graph.add_relation(new_rel)
        app.canvas_widget.refresh_graph(app.current_graph)
        assert app.current_graph.relation_count == 2

        # Test save directly to CSV
        app._save_changes()
        assert app.is_dirty is False
        assert nodes_file.exists()
        assert rels_file.exists()

        # Test node deletion (cascades to 2 connected relationships)
        deleted_success, deleted_rels = app.current_graph.delete_node("550e8400-e29b-41d4-a716-446655440000")
        assert deleted_success is True
        assert len(deleted_rels) == 2
        assert app.current_graph.node_count == 2
        assert app.current_graph.relation_count == 0

    def test_app_dialog_crud_workflows(self, tk_root, sample_graph, tmp_path):
        """Test full app dialog CRUD workflows, help dialogs, and loaders."""
        nodes_file = tmp_path / "nodes.csv"
        rels_file = tmp_path / "rels.csv"
        app = GraphVisualizerApp(tk_root)
        app.on_graph_loaded(sample_graph, nodes_file, rels_file)

        # 1. Add Node via Dialog
        dummy_node = Node(name="Auth", uuid="550e8400-e29b-41d4-a716-446655440077", properties={"role": "Auth"})
        with patch("src.gui.app.NodeDialog") as mock_node_dialog:
            mock_inst = MagicMock()
            mock_inst.result = dummy_node
            mock_node_dialog.return_value = mock_inst
            app._on_add_node()
        assert app.current_graph.node_count == 3
        assert app.is_dirty is True

        # 2. Edit Node via Dialog
        updated_node = Node(name="AuthService", uuid="550e8400-e29b-41d4-a716-446655440077", properties={"role": "AuthV2"})
        with patch("src.gui.app.NodeDialog") as mock_node_dialog:
            mock_inst = MagicMock()
            mock_inst.result = updated_node
            mock_node_dialog.return_value = mock_inst
            app._on_edit_node(dummy_node)
        assert app.current_graph.get_node(dummy_node.uuid).name == "AuthService"

        # 3. Add Relation via Dialog
        dummy_rel = Relation(
            source_uuid="550e8400-e29b-41d4-a716-446655440000",
            target_uuid="550e8400-e29b-41d4-a716-446655440077",
            relationship_name="authenticates_with",
            relationship_uuid="550e8400-e29b-41d4-a716-446655440066",
        )
        with patch("src.gui.app.RelationDialog") as mock_rel_dialog:
            mock_inst = MagicMock()
            mock_inst.result = dummy_rel
            mock_rel_dialog.return_value = mock_inst
            app._on_add_relation()
        assert app.current_graph.relation_count == 2

        # 4. Edit Relation via Dialog
        updated_rel = Relation(
            source_uuid=dummy_rel.source_uuid,
            target_uuid=dummy_rel.target_uuid,
            relationship_name="verifies_with",
            relationship_uuid=dummy_rel.relationship_uuid,
            properties={"protocol": "OAuth2"},
        )
        with patch("src.gui.app.RelationDialog") as mock_rel_dialog:
            mock_inst = MagicMock()
            mock_inst.result = updated_rel
            mock_rel_dialog.return_value = mock_inst
            app._on_edit_relation(dummy_rel)
        assert app.current_graph.get_relation(dummy_rel.relationship_uuid).relationship_name == "verifies_with"

        # 5. Delete Relation
        app._on_delete_relation(dummy_rel)
        assert app.current_graph.relation_count == 1

        # 6. Delete Node
        app._on_delete_node(dummy_node)
        assert app.current_graph.node_count == 2

        # 7. Save As
        save_nodes = str(tmp_path / "save_as_nodes.csv")
        save_rels = str(tmp_path / "save_as_rels.csv")
        with patch("tkinter.filedialog.asksaveasfilename", side_effect=[save_nodes, save_rels]):
            app._save_as()
        assert Path(save_nodes).exists()
        assert Path(save_rels).exists()

        # 8. Loaders & Guides
        app._load_sample()
        app._load_family_graph()
        assert app.current_graph.node_count == 8
        app._show_controls_guide()
        app._show_about()

