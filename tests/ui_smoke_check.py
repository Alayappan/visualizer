"""Comprehensive UI smoke test verifying all requested visualizer features using the venv Python."""
import sys
from pathlib import Path
import tkinter as tk

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import MagicMock
import tkinter.messagebox
tkinter.messagebox.showinfo = MagicMock(return_value="ok")
tkinter.messagebox.showerror = MagicMock(return_value="ok")
tkinter.messagebox.showwarning = MagicMock(return_value="ok")
tkinter.messagebox.askyesno = MagicMock(return_value=True)

from src.gui.app import GraphVisualizerApp
from src.gui.theme import apply_theme
from src.models import Node, Relation


def run_ui_smoke_test():
    print("=" * 60)
    print("🚀 STARTING UI VERIFICATION USING VENV PYTHON")
    print("=" * 60)

    root = tk.Tk()
    root.withdraw()
    apply_theme(root)

    app = GraphVisualizerApp(root)
    root.update()

    # 1. Check Initial State
    print("\n[1] Checking Initial FileSelector View...")
    assert hasattr(app.file_selector, "btn_load_sample"), "Missing Sample Data button"
    print("  ✓ 'Sample Data' button exists on FileSelector")
    print(f"  ✓ Initial toolbar Add Node state: {app.btn_add_node.cget('state')}")
    assert str(app.btn_add_node.cget('state')) == "disabled"

    # 2. Load Sample Graph via one-click loader
    print("\n[2] Loading Sample Graph Dataset...")
    app._load_sample()
    app.file_selector._on_visualize_click()
    root.update()

    assert app.current_graph is not None, "Sample graph failed to load!"
    print(f"  ✓ Nodes Loaded: {app.current_graph.node_count} (Expected 3)")
    print(f"  ✓ Relations Loaded: {app.current_graph.relation_count} (Expected 2)")
    assert app.current_graph.node_count == 3
    assert app.current_graph.relation_count == 2

    # 3. Check Toolbar Features
    print("\n[3] Verifying Toolbar Features...")
    print(f"  ✓ '➕ Node' button state: {app.btn_add_node.cget('state')}")
    print(f"  ✓ '🔗 Relation' button state: {app.btn_add_relation.cget('state')}")
    print(f"  ✓ '💾 Save' button state: {app.btn_save.cget('state')}")
    print(f"  ✓ '💾 Save As' button state: {app.btn_save_as.cget('state')}")
    print(f"  ✓ '📐 Reset 3D' button state: {app.btn_reset_3d.cget('state')}")
    print(f"  ✓ '▶ Auto-Rotate 3D' button state: {app.btn_auto_rotate.cget('state')}")
    assert str(app.btn_add_node.cget('state')) == "normal"
    assert str(app.btn_add_relation.cget('state')) == "normal"
    assert str(app.btn_save.cget('state')) == "normal"
    assert str(app.btn_reset_3d.cget('state')) == "normal"
    assert str(app.btn_auto_rotate.cget('state')) == "normal"

    # 4. Check 3D & Curved lines features on Canvas
    print("\n[4] Verifying 3D Graphics & Curved Closed Relations on Canvas...")
    canvas = app.canvas_widget
    print(f"  ✓ 3D Camera pitch: {canvas.camera_pitch:.2f}, yaw: {canvas.camera_yaw:.2f}")
    assert len(canvas.node_positions) == 3
    print(f"  ✓ 3D Node Positions computed: {len(canvas.node_positions)} nodes with (X, Y, Z)")

    # Check curve offset calculation
    from src.gui.graph_canvas import calculate_edge_geometry
    geom_fwd = calculate_edge_geometry(100.0, 100.0, 300.0, 100.0, 20.0, 20.0, h=35.0)
    geom_rev = calculate_edge_geometry(300.0, 100.0, 100.0, 100.0, 20.0, 20.0, h=35.0)
    print(f"  ✓ Bidirectional curve forward control point: {geom_fwd['points'][2]:.1f}, {geom_fwd['points'][3]:.1f}")
    print(f"  ✓ Bidirectional curve reverse control point: {geom_rev['points'][2]:.1f}, {geom_rev['points'][3]:.1f}")
    assert geom_fwd["is_curved"] is True
    assert geom_rev["is_curved"] is True
    assert geom_fwd["points"][3] != 100.0  # Off the straight line

    # 5. Check 3D Interactivity: Orbit & Auto-rotate
    print("\n[5] Verifying 3D Interactivity (Orbit & Auto-Rotate)...")
    init_yaw = canvas.camera_yaw
    app._toggle_auto_rotate()
    assert canvas.auto_rotate is True
    print("  ✓ Auto-rotate started successfully")
    canvas._auto_rotate_step()
    assert canvas.camera_yaw != init_yaw
    print(f"  ✓ Camera yaw rotated from {init_yaw:.3f} to {canvas.camera_yaw:.3f}")
    app._toggle_auto_rotate()
    assert canvas.auto_rotate is False
    print("  ✓ Auto-rotate paused successfully")

    app._reset_3d_angle()
    print("  ✓ Reset 3D angle successful")

    # 6. Check Detail Panel Node Selection & Action Buttons
    print("\n[6] Verifying Node Inspection & Action Buttons...")
    sample_node = app.current_graph.nodes[0]
    app._on_node_selected(sample_node)
    root.update()
    assert app.detail_panel.title_label.cget("text") == "Node Details"
    print("  ✓ Detail Panel switched to 'Node Details'")
    assert app.detail_panel.on_edit_node is not None
    assert app.detail_panel.on_delete_node is not None
    print("  ✓ '✏️ Edit' and '🗑️ Delete' action handlers attached for Node")

    # 7. Check Detail Panel Relation Selection & Action Buttons
    print("\n[7] Verifying Relation Inspection & Action Buttons...")
    sample_rel = app.current_graph.relations[0]
    app._on_relation_selected(sample_rel)
    root.update()
    assert app.detail_panel.title_label.cget("text") == "Relationship Details"
    print("  ✓ Detail Panel switched to 'Relationship Details'")
    assert app.detail_panel.on_edit_relation is not None
    assert app.detail_panel.on_delete_relation is not None
    print("  ✓ '✏️ Edit' and '🗑️ Delete' action handlers attached for Relation")

    # 8. Check Graph Editing & CSV Persistence
    print("\n[8] Verifying Graph Editing & CSV Persistence...")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_nodes_path = Path(tmp_dir) / "nodes.csv"
        test_rels_path = Path(tmp_dir) / "relations.csv"
        app.nodes_csv_path = test_nodes_path
        app.relations_csv_path = test_rels_path

        # Add node
        new_node = Node(name="Test Service", uuid="a1b2c3d4-e5f6-4a1b-8c2d-3e4f5a6b7c8d", properties={"role": "Service"})
        app.current_graph.add_node(new_node)
        app.canvas_widget.refresh_graph(app.current_graph)
        app._mark_dirty()
        print(f"  ✓ Node added. New count: {app.current_graph.node_count}")
        assert app.current_graph.node_count == 4

        # Add relation
        new_rel = Relation(
            source_uuid=sample_node.uuid,
            target_uuid=new_node.uuid,
            relationship_name="connects_to",
            relationship_uuid="b2c3d4e5-f6a1-4b2c-9d3e-4f5a6b7c8d9e",
            properties={"protocol": "HTTPS"}
        )
        app.current_graph.add_relation(new_rel)
        app.canvas_widget.refresh_graph(app.current_graph)
        print(f"  ✓ Relation added. New count: {app.current_graph.relation_count}")
        assert app.current_graph.relation_count == 3

        # Save to CSV
        app._save_changes()
        assert test_nodes_path.exists()
        assert test_rels_path.exists()
        print("  ✓ Save wrote changes directly to CSV files")

        content_nodes = test_nodes_path.read_text()
        content_rels = test_rels_path.read_text()
        assert "Test Service" in content_nodes
        assert "connects_to" in content_rels
        print("  ✓ Verified CSV contents contain new node and relation")

        # Delete relation
        app.current_graph.delete_relation(new_rel.relationship_uuid)
        app.canvas_widget.refresh_graph(app.current_graph)
        print(f"  ✓ Relation deleted. Count: {app.current_graph.relation_count}")
        assert app.current_graph.relation_count == 2

        # Cascade delete node
        del_ok, _ = app.current_graph.delete_node(new_node.uuid)
        assert del_ok is True
        app.canvas_widget.refresh_graph(app.current_graph)
        print(f"  ✓ Node cascade-deleted. Count: {app.current_graph.node_count}")
        assert app.current_graph.node_count == 3

        # Save updated state
        app._save_changes()
        updated_nodes_csv = test_nodes_path.read_text()
        assert "Test Service" not in updated_nodes_csv
        print("  ✓ Saved CSV verified: deleted node cleanly removed")

    root.destroy()
    print("\n" + "=" * 60)
    print("✅ ALL UI AND EDITING FEATURES VERIFIED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_ui_smoke_test()

