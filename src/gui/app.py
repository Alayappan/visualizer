"""Main application window for the Neo4j Graph Visualizer Desktop App."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Tuple
from pathlib import Path

from src.models import Node, Relation, Graph
from src.validators.graph_parser import GraphParser
from src.gui.theme import (
    apply_theme, BG_DARK, BG_PANEL, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, SUCCESS_GREEN, WARNING_AMBER
)
from src.gui.file_selector import FileSelector
from src.gui.graph_canvas import GraphCanvas
from src.gui.detail_panel import DetailPanel
from src.gui.dialogs import NodeDialog, RelationDialog


class GraphVisualizerApp:
    """
    Master desktop application coordinating:
    - File upload and schema validation
    - Interactive 3D graph visualization with curved bidirectional links
    - Full graph CRUD operations (Add Node, Edit Node, Delete Node, Add Relation, Edit Relation, Delete Relation)
    - Direct CSV persistence on Save / Save As
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Neo4j Graph Visualizer")
        self.root.geometry("1340x860")
        self.root.minsize(960, 640)

        # Apply dark modern theme
        self.style = apply_theme(self.root)

        # State tracking
        self.current_graph: Optional[Graph] = None
        self.nodes_csv_path: Optional[Path] = None
        self.relations_csv_path: Optional[Path] = None
        self.is_dirty: bool = False

        self._build_menu()
        self._build_toolbar()
        self._build_main_container()
        self._build_status_bar()
        self._bind_shortcuts()

        # Start in file selection view
        self.show_upload_view()

    # -------------------------------------------------------------------------
    # Menu & Toolbar
    # -------------------------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Upload / Select CSVs", command=self.show_upload_view, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Family Dataset", command=self._load_family_graph)
        file_menu.add_command(label="Load Sample Dataset", command=self._load_sample)
        file_menu.add_separator()
        file_menu.add_command(label="Save Changes to CSV", command=self._save_changes, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Add Node", command=self._on_add_node, accelerator="Ctrl+N")
        edit_menu.add_command(label="Add Relationship", command=self._on_add_relation, accelerator="Ctrl+Shift+N")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self._zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self._zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Screen", command=self._fit_graph, accelerator="Ctrl+0")
        view_menu.add_command(label="Recalculate 3D Layout", command=self._reset_layout)
        view_menu.add_separator()
        view_menu.add_command(label="Reset 3D Angle", command=self._reset_3d_angle, accelerator="Ctrl+R")
        view_menu.add_command(label="Toggle 3D Auto-Rotate", command=self._toggle_auto_rotate, accelerator="Space")
        menubar.add_cascade(label="View", menu=view_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Controls & Shortcuts Guide", command=self._show_controls_guide)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _build_toolbar(self):
        self.toolbar = ttk.Frame(self.root, style="Panel.TFrame")
        self.toolbar.pack(side="top", fill="x", padx=0, pady=0)

        # 1. Navigation / Upload
        self.btn_new_upload = ttk.Button(
            self.toolbar,
            text="📁 New Upload",
            command=self.show_upload_view,
        )
        self.btn_new_upload.pack(side="left", padx=(10, 4), pady=6)

        ttk.Separator(self.toolbar, orient="vertical").pack(side="left", fill="y", padx=4, pady=4)

        # 2. Graph Editing Controls
        self.btn_add_node = ttk.Button(
            self.toolbar,
            text="➕ Node",
            command=self._on_add_node,
        )
        self.btn_add_node.pack(side="left", padx=3, pady=6)

        self.btn_add_relation = ttk.Button(
            self.toolbar,
            text="🔗 Relation",
            command=self._on_add_relation,
        )
        self.btn_add_relation.pack(side="left", padx=3, pady=6)

        self.btn_save = ttk.Button(
            self.toolbar,
            text="💾 Save",
            command=self._save_changes,
        )
        self.btn_save.pack(side="left", padx=3, pady=6)

        self.btn_save_as = ttk.Button(
            self.toolbar,
            text="💾 Save As",
            command=self._save_as,
        )
        self.btn_save_as.pack(side="left", padx=3, pady=6)

        ttk.Separator(self.toolbar, orient="vertical").pack(side="left", fill="y", padx=4, pady=4)

        # 3. Canvas Zoom & Fit Controls
        self.btn_zoom_in = ttk.Button(
            self.toolbar,
            text="🔍 In (+)",
            command=self._zoom_in,
        )
        self.btn_zoom_in.pack(side="left", padx=3, pady=6)

        self.btn_zoom_out = ttk.Button(
            self.toolbar,
            text="🔍 Out (-)",
            command=self._zoom_out,
        )
        self.btn_zoom_out.pack(side="left", padx=3, pady=6)

        self.btn_fit = ttk.Button(
            self.toolbar,
            text="⤢ Fit",
            command=self._fit_graph,
        )
        self.btn_fit.pack(side="left", padx=3, pady=6)

        self.btn_relayout = ttk.Button(
            self.toolbar,
            text="🔄 Re-layout",
            command=self._reset_layout,
        )
        self.btn_relayout.pack(side="left", padx=3, pady=6)

        ttk.Separator(self.toolbar, orient="vertical").pack(side="left", fill="y", padx=4, pady=4)

        # 4. 3D Interactivity Controls
        self.btn_reset_3d = ttk.Button(
            self.toolbar,
            text="📐 Reset 3D",
            command=self._reset_3d_angle,
        )
        self.btn_reset_3d.pack(side="left", padx=3, pady=6)

        self.btn_auto_rotate = ttk.Button(
            self.toolbar,
            text="▶ Auto-Rotate 3D",
            command=self._toggle_auto_rotate,
        )
        self.btn_auto_rotate.pack(side="left", padx=3, pady=6)

        # Right Summary Label
        self.toolbar_summary = ttk.Label(
            self.toolbar,
            text="No graph loaded",
            font=("Helvetica", 10, "bold"),
            foreground=TEXT_SECONDARY,
            background=BG_PANEL,
        )
        self.toolbar_summary.pack(side="right", padx=16, pady=6)

    def _build_main_container(self):
        """Build the master workspace container."""
        self.workspace = ttk.Frame(self.root, style="TFrame")
        self.workspace.pack(fill="both", expand=True)
        self.workspace.columnconfigure(0, weight=1)
        self.workspace.rowconfigure(0, weight=1)

        # 1. File Selector Frame
        self.file_selector = FileSelector(
            self.workspace,
            on_graph_loaded=self.on_graph_loaded,
        )

        # 2. Graph View Frame (Paned: Canvas on left, Details on right)
        self.graph_view_frame = ttk.Frame(self.workspace, style="TFrame")
        self.graph_view_frame.columnconfigure(0, weight=1)
        self.graph_view_frame.rowconfigure(0, weight=1)

        self.paned = tk.PanedWindow(
            self.graph_view_frame,
            orient=tk.HORIZONTAL,
            bg=BG_DARK,
            bd=0,
            sashwidth=4,
            sashrelief=tk.FLAT,
        )
        self.paned.grid(row=0, column=0, sticky="nsew")

        # Graph Canvas
        self.canvas_widget = GraphCanvas(
            self.paned,
            on_node_selected=self._on_node_selected,
            on_relation_selected=self._on_relation_selected,
            on_selection_cleared=self._on_selection_cleared,
        )
        self.paned.add(self.canvas_widget, minsize=500)

        # Detail Panel (collapsible sidebar with Edit / Delete actions)
        self.detail_panel = DetailPanel(
            self.paned,
            on_close=self._on_detail_panel_closed,
            on_edit_node=self._on_edit_node,
            on_delete_node=self._on_delete_node,
            on_edit_relation=self._on_edit_relation,
            on_delete_relation=self._on_delete_relation,
            width=350,
        )
        self.paned.add(self.detail_panel, minsize=280, width=350)

    def _build_status_bar(self):
        self.status_bar = ttk.Frame(self.root, style="Panel.TFrame")
        self.status_bar.pack(side="bottom", fill="x")

        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready. Select CSV files or click 'Open Family Dataset' to begin.",
            font=("Helvetica", 10),
            foreground=TEXT_SECONDARY,
            background=BG_PANEL,
        )
        self.status_label.pack(side="left", padx=12, pady=4)

        self.status_coords = ttk.Label(
            self.status_bar,
            text="Zoom: 100%",
            font=("Helvetica", 10),
            foreground=TEXT_SECONDARY,
            background=BG_PANEL,
        )
        self.status_coords.pack(side="right", padx=12, pady=4)

        self.status_guide = ttk.Label(
            self.status_bar,
            text="🖱️ Left-drag: Move Node | Right-drag / Shift+drag: 3D Orbit | Wheel: Zoom",
            font=("Helvetica", 9),
            foreground=TEXT_MUTED,
            background=BG_PANEL,
        )
        self.status_guide.pack(side="right", padx=16, pady=4)

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self.show_upload_view())
        self.root.bind("<Command-o>", lambda e: self.show_upload_view())
        self.root.bind("<Control-s>", lambda e: self._save_changes())
        self.root.bind("<Command-s>", lambda e: self._save_changes())
        self.root.bind("<Control-n>", lambda e: self._on_add_node())
        self.root.bind("<Command-n>", lambda e: self._on_add_node())
        self.root.bind("<Control-plus>", lambda e: self._zoom_in())
        self.root.bind("<Command-plus>", lambda e: self._zoom_in())
        self.root.bind("<Control-minus>", lambda e: self._zoom_out())
        self.root.bind("<Command-minus>", lambda e: self._zoom_out())
        self.root.bind("<Control-0>", lambda e: self._fit_graph())
        self.root.bind("<Command-0>", lambda e: self._fit_graph())
        self.root.bind("<Control-r>", lambda e: self._reset_3d_angle())
        self.root.bind("<Command-r>", lambda e: self._reset_3d_angle())
        self.root.bind("<space>", lambda e: self._toggle_auto_rotate())
        self.root.bind("<Escape>", lambda e: self.canvas_widget.clear_selection())

    # -------------------------------------------------------------------------
    # View State Transitions
    # -------------------------------------------------------------------------

    def show_upload_view(self):
        """Switch workspace to file upload and validation view."""
        if hasattr(self, "canvas_widget") and self.canvas_widget.auto_rotate:
            self._toggle_auto_rotate()

        self.graph_view_frame.grid_forget()
        self.file_selector.grid(row=0, column=0, sticky="nsew")

        # Disable graph tools in upload view
        self.btn_add_node.configure(state="disabled")
        self.btn_add_relation.configure(state="disabled")
        self.btn_save.configure(state="disabled")
        self.btn_save_as.configure(state="disabled")
        self.btn_zoom_in.configure(state="disabled")
        self.btn_zoom_out.configure(state="disabled")
        self.btn_fit.configure(state="disabled")
        self.btn_relayout.configure(state="disabled")
        self.btn_reset_3d.configure(state="disabled")
        self.btn_auto_rotate.configure(state="disabled")
        self.btn_new_upload.configure(state="disabled")

        self.status_label.config(text="Select and validate CSV files or click 'Open Family Dataset'.")

    def on_graph_loaded(self, graph: Graph, nodes_path: Optional[Path] = None, relations_path: Optional[Path] = None):
        """Callback when CSV files are successfully parsed into a Graph object."""
        self.current_graph = graph
        if nodes_path:
            self.nodes_csv_path = Path(nodes_path)
        if relations_path:
            self.relations_csv_path = Path(relations_path)

        self.is_dirty = False
        self._update_title()

        self.detail_panel.set_graph(graph)
        self.canvas_widget.set_graph(graph)

        # Switch view to interactive canvas
        self.file_selector.grid_forget()
        self.graph_view_frame.grid(row=0, column=0, sticky="nsew")

        # Enable graph tools
        self.btn_add_node.configure(state="normal")
        self.btn_add_relation.configure(state="normal")
        self.btn_save.configure(state="normal")
        self.btn_save_as.configure(state="normal")
        self.btn_zoom_in.configure(state="normal")
        self.btn_zoom_out.configure(state="normal")
        self.btn_fit.configure(state="normal")
        self.btn_relayout.configure(state="normal")
        self.btn_reset_3d.configure(state="normal")
        self.btn_auto_rotate.configure(state="normal")
        self.btn_new_upload.configure(state="normal")

        # Update summary text
        self._update_summary()
        self.status_label.config(
            text=f"Graph loaded in 3D ({graph.node_count} nodes, {graph.relation_count} relations). Click node/relation to inspect & edit."
        )
        self.status_coords.config(text=f"Zoom: {int(self.canvas_widget.scale * 100)}%")

    def _update_summary(self):
        if not self.current_graph:
            self.toolbar_summary.config(text="No graph loaded")
            return
        dirty_flag = " [Unsaved changes*]" if self.is_dirty else ""
        file_hint = f" ({self.nodes_csv_path.name})" if self.nodes_csv_path else ""
        self.toolbar_summary.config(
            text=f"Nodes: {self.current_graph.node_count}  |  Relations: {self.current_graph.relation_count}{file_hint}{dirty_flag}"
        )

    def _update_title(self):
        prefix = "* " if self.is_dirty else ""
        file_part = f" - {self.nodes_csv_path.name}" if self.nodes_csv_path else ""
        self.root.title(f"{prefix}Neo4j Graph Visualizer{file_part}")

    def _mark_dirty(self):
        self.is_dirty = True
        self._update_title()
        self._update_summary()

    def _clear_dirty(self):
        self.is_dirty = False
        self._update_title()
        self._update_summary()

    # -------------------------------------------------------------------------
    # Node & Relationship CRUD Handlers
    # -------------------------------------------------------------------------

    def _on_add_node(self):
        """Open dialog to create and add a new Node to the graph."""
        if not self.current_graph:
            return
        dialog = NodeDialog(self.root, title="Add New Node")
        if dialog.result:
            try:
                self.current_graph.add_node(dialog.result)
                self.canvas_widget.refresh_graph(self.current_graph)
                self._mark_dirty()
                self.status_label.config(text=f"Added node '{dialog.result.name}' to graph.")
            except Exception as e:
                messagebox.showerror("Error Adding Node", str(e))

    def _on_edit_node(self, node: Node):
        """Open dialog to edit existing Node name and properties."""
        if not self.current_graph:
            return
        dialog = NodeDialog(self.root, node=node, title=f"Edit Node: {node.name}")
        if dialog.result:
            self.current_graph.update_node(node.uuid, dialog.result.name, dialog.result.properties)
            self.canvas_widget.refresh_graph(self.current_graph)
            updated_node = self.current_graph.get_node(node.uuid)
            if updated_node:
                self.detail_panel.display_node(updated_node)
            self._mark_dirty()
            self.status_label.config(text=f"Updated node '{dialog.result.name}'.")

    def _on_delete_node(self, node: Node):
        """Prompt and cascade-delete Node and all connected relationships."""
        if not self.current_graph:
            return
        rels = self.current_graph.get_relations_for_node(node.uuid)
        rel_msg = f"\nThis will cascade-delete {len(rels)} connected relationship(s)." if rels else ""
        confirm = messagebox.askyesno(
            "Delete Node",
            f"Are you sure you want to delete node '{node.name}'?{rel_msg}\nThis cannot be undone.",
            icon="warning"
        )
        if confirm:
            success, deleted_rels = self.current_graph.delete_node(node.uuid)
            if success:
                self.canvas_widget.refresh_graph(self.current_graph)
                self.detail_panel.clear()
                self._mark_dirty()
                self.status_label.config(text=f"Deleted node '{node.name}' and {len(deleted_rels)} relationship(s).")

    def _on_add_relation(self):
        """Open dialog to create and add a new Relationship between two nodes."""
        if not self.current_graph:
            return
        if self.current_graph.node_count < 1:
            messagebox.showwarning("Cannot Add Relation", "The graph must contain at least one node to create a relationship.")
            return

        dialog = RelationDialog(self.root, graph=self.current_graph, title="Add New Relationship")
        if dialog.result:
            try:
                self.current_graph.add_relation(dialog.result)
                self.canvas_widget.refresh_graph(self.current_graph)
                self._mark_dirty()
                self.status_label.config(text=f"Added relationship '{dialog.result.relationship_name}' to graph.")
            except Exception as e:
                messagebox.showerror("Error Adding Relationship", str(e))

    def _on_edit_relation(self, relation: Relation):
        """Open dialog to edit existing Relationship type and properties."""
        if not self.current_graph:
            return
        dialog = RelationDialog(self.root, graph=self.current_graph, relation=relation, title=f"Edit Relation: {relation.relationship_name}")
        if dialog.result:
            self.current_graph.update_relation(relation.relationship_uuid, dialog.result.relationship_name, dialog.result.properties)
            self.canvas_widget.refresh_graph(self.current_graph)
            updated_rel = self.current_graph.get_relation(relation.relationship_uuid)
            if updated_rel:
                self.detail_panel.display_relation(updated_rel)
            self._mark_dirty()
            self.status_label.config(text=f"Updated relationship '{dialog.result.relationship_name}'.")

    def _on_delete_relation(self, relation: Relation):
        """Prompt and delete Relationship."""
        if not self.current_graph:
            return
        confirm = messagebox.askyesno(
            "Delete Relationship",
            f"Are you sure you want to delete relationship '{relation.relationship_name}'?",
            icon="warning"
        )
        if confirm:
            success = self.current_graph.delete_relation(relation.relationship_uuid)
            if success:
                self.canvas_widget.refresh_graph(self.current_graph)
                self.detail_panel.clear()
                self._mark_dirty()
                self.status_label.config(text=f"Deleted relationship '{relation.relationship_name}'.")

    # -------------------------------------------------------------------------
    # Direct CSV Persistence on Save / Save As
    # -------------------------------------------------------------------------

    def _save_changes(self):
        """Save graph modifications directly back to the active CSV files."""
        if not self.current_graph:
            return
        if not self.nodes_csv_path or not self.relations_csv_path:
            self._save_as()
            return

        try:
            self.current_graph.save_to_csv(self.nodes_csv_path, self.relations_csv_path)
            self._clear_dirty()
            self.status_label.config(text=f"✓ Changes saved directly to {self.nodes_csv_path.name} & {self.relations_csv_path.name}.")
            messagebox.showinfo(
                "Saved",
                f"Graph successfully saved to disk:\n\n• Nodes: {self.nodes_csv_path}\n• Relations: {self.relations_csv_path}"
            )
        except Exception as e:
            messagebox.showerror("Error Saving CSV", f"Failed to save changes: {e}")

    def _save_as(self):
        """Save graph modifications to new CSV files selected by user."""
        if not self.current_graph:
            return

        nodes_file = filedialog.asksaveasfilename(
            title="Save Nodes CSV As",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="nodes_modified.csv"
        )
        if not nodes_file:
            return

        relations_file = filedialog.asksaveasfilename(
            title="Save Relations CSV As",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="relations_modified.csv"
        )
        if not relations_file:
            return

        try:
            self.current_graph.save_to_csv(nodes_file, relations_file)
            self.nodes_csv_path = Path(nodes_file)
            self.relations_csv_path = Path(relations_file)
            self._clear_dirty()
            self.status_label.config(text=f"✓ Graph saved as {self.nodes_csv_path.name} & {self.relations_csv_path.name}.")
            messagebox.showinfo("Saved As", f"Graph exported successfully to new files.")
        except Exception as e:
            messagebox.showerror("Error Saving CSV", f"Failed to save files: {e}")

    # -------------------------------------------------------------------------
    # Selection Callbacks
    # -------------------------------------------------------------------------

    def _on_node_selected(self, node: Node):
        self.detail_panel.display_node(node)
        self.status_label.config(text=f"Selected Node: {node.name} ({node.uuid})")

    def _on_relation_selected(self, relation: Relation):
        self.detail_panel.display_relation(relation)
        self.status_label.config(text=f"Selected Relation: {relation.relationship_name} ({relation.relationship_uuid})")

    def _on_selection_cleared(self):
        self.detail_panel.clear()
        if self.current_graph:
            self.status_label.config(
                text=f"Graph active ({self.current_graph.node_count} nodes, {self.current_graph.relation_count} relations)."
            )

    def _on_detail_panel_closed(self):
        self.canvas_widget.clear_selection()

    # -------------------------------------------------------------------------
    # Viewport & 3D Actions
    # -------------------------------------------------------------------------

    def _zoom_in(self):
        if self.current_graph:
            self.canvas_widget.zoom_in()
            self.status_coords.config(text=f"Zoom: {int(self.canvas_widget.scale * 100)}%")

    def _zoom_out(self):
        if self.current_graph:
            self.canvas_widget.zoom_out()
            self.status_coords.config(text=f"Zoom: {int(self.canvas_widget.scale * 100)}%")

    def _fit_graph(self):
        if self.current_graph:
            self.canvas_widget.fit_to_screen()
            self.status_coords.config(text=f"Zoom: {int(self.canvas_widget.scale * 100)}%")

    def _reset_layout(self):
        if self.current_graph:
            self.canvas_widget.reset_layout()
            self.status_coords.config(text=f"Zoom: {int(self.canvas_widget.scale * 100)}%")

    def _reset_3d_angle(self):
        if self.current_graph:
            self.canvas_widget.reset_3d_angle()
            self.status_coords.config(text=f"Zoom: {int(self.canvas_widget.scale * 100)}%")
            self.status_label.config(text="3D perspective reset to default angle.")

    def _toggle_auto_rotate(self):
        if self.current_graph:
            is_rotating = self.canvas_widget.toggle_auto_rotate()
            if is_rotating:
                self.btn_auto_rotate.configure(text="⏸ Pause Rotate")
                self.status_label.config(text="3D Turntable active. Orbiting...")
            else:
                self.btn_auto_rotate.configure(text="▶ Auto-Rotate 3D")
                self.status_label.config(text="3D Turntable paused.")

    def _load_sample(self):
        self.show_upload_view()
        self.file_selector.load_sample_data()

    def _load_family_graph(self):
        """Direct one-click loader for the family dataset."""
        nodes_path = Path("data/family_nodes.csv")
        relations_path = Path("data/family_relations.csv")
        if not nodes_path.exists() or not relations_path.exists():
            root_data = Path(__file__).resolve().parent.parent.parent / "data"
            nodes_path = root_data / "family_nodes.csv"
            relations_path = root_data / "family_relations.csv"
        if not nodes_path.exists() or not relations_path.exists():
            messagebox.showerror("File Not Found", "Family dataset files not found in 'data/' directory.")
            return

        is_valid, errors, graph = GraphParser.load_graph_from_sources(nodes_path, relations_path)
        if is_valid and graph:
            self.on_graph_loaded(graph, nodes_path, relations_path)
        else:
            messagebox.showerror("Validation Error", "\n".join(errors))

    def _show_controls_guide(self):
        messagebox.showinfo(
            "Controls & Shortcuts Guide",
            "🎮 Mouse Controls:\n"
            "• Left Click: Select Node or Relation\n"
            "• Left Click + Drag Node: Move node in 3D viewing plane with elevation lift\n"
            "• Left Click + Drag Canvas: Pan viewport\n"
            "• Right Click + Drag (or Shift + Left Drag): 3D Camera Orbit (rotate pitch/yaw)\n"
            "• Mouse Wheel: Smooth 3D Zoom\n\n"
            "⌨️ Keyboard Shortcuts:\n"
            "• Ctrl+N: Add Node\n"
            "• Ctrl+Shift+N: Add Relationship\n"
            "• Ctrl+S: Save to CSV files\n"
            "• Ctrl+R: Reset 3D Angle\n"
            "• Space: Toggle 3D Auto-Rotate Turntable\n"
            "• Ctrl+0: Fit Graph to Screen\n"
            "• Ctrl++ / Ctrl+-: Zoom In / Out\n"
            "• Escape: Clear Selection"
        )

    def _show_about(self):
        messagebox.showinfo(
            "About Neo4j Graph Visualizer",
            "Neo4j Graph Visualizer Desktop App v1.2.0\n\n"
            "• 3D Interactive Graph Engine\n"
            "• Curved Directed Lines for Bidirectional Relations\n"
            "• Full Graph CRUD with CSV Persistence\n"
            "• Built with Python & Tkinter."
        )


def main():
    root = tk.Tk()
    app = GraphVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

