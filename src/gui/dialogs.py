"""Modal dialogs for creating and editing nodes and relationships."""
import uuid
import json
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List
from src.models import Node, Relation, Graph
from src.validators import CSVValidator
from src.gui.theme import (
    BG_DARK, BG_PANEL, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, ERROR_RED, SUCCESS_GREEN
)


class NodeDialog(tk.Toplevel):
    """Dialog for creating or editing a Node."""

    def __init__(self, parent, node: Optional[Node] = None, title: Optional[str] = None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.node = node
        self.result: Optional[Node] = None

        self.title(title or ("Edit Node" if node else "Create Node"))
        self.geometry("520x460")
        self.minsize(450, 400)
        self.configure(bg=BG_DARK)

        self._build_ui()
        self.wait_window()

    def _build_ui(self):
        container = ttk.Frame(self, style="Panel.TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.columnconfigure(1, weight=1)

        # Title
        hdr = ttk.Label(
            container,
            text="Edit Node Details" if self.node else "Add New Node",
            font=("Helvetica", 14, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        hdr.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # Name
        lbl_name = ttk.Label(
            container,
            text="Node Name *:",
            font=("Helvetica", 11, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        lbl_name.grid(row=1, column=0, sticky="w", pady=8)

        self.name_var = tk.StringVar(value=self.node.name if self.node else "")
        self.name_entry = ttk.Entry(container, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=8)
        self.name_entry.focus_set()

        # UUID
        lbl_uuid = ttk.Label(
            container,
            text="UUID v4 *:",
            font=("Helvetica", 11, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        lbl_uuid.grid(row=2, column=0, sticky="w", pady=8)

        default_uuid = self.node.uuid if self.node else str(uuid.uuid4())
        self.uuid_var = tk.StringVar(value=default_uuid)
        self.uuid_entry = ttk.Entry(container, textvariable=self.uuid_var)
        self.uuid_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=8)

        # Properties JSON
        lbl_props = ttk.Label(
            container,
            text="Properties (JSON):",
            font=("Helvetica", 11, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        lbl_props.grid(row=3, column=0, sticky="nw", pady=(12, 4))

        props_text = ""
        if self.node and self.node.properties:
            props_text = json.dumps(self.node.properties, indent=2)

        self.props_box = tk.Text(
            container,
            height=8,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            font=("Courier", 10),
            padx=8,
            pady=8,
            bd=0,
        )
        self.props_box.insert("1.0", props_text)
        self.props_box.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(4, 16))
        container.rowconfigure(4, weight=1)

        # Action Buttons
        btn_frame = ttk.Frame(container, style="Panel.TFrame")
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="e")

        btn_cancel = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_save = ttk.Button(btn_frame, text="Save Node", style="Primary.TButton", command=self._on_save)
        btn_save.pack(side="right")

    def _on_save(self):
        name = self.name_var.get().strip()
        uuid_val = self.uuid_var.get().strip()
        props_str = self.props_box.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Validation Error", "Node Name cannot be empty.", parent=self)
            return

        if not CSVValidator.validate_uuid_format(uuid_val):
            messagebox.showerror("Validation Error", f"Invalid UUID v4 format: '{uuid_val}'", parent=self)
            return

        properties = None
        if props_str:
            try:
                parsed = json.loads(props_str)
                if not isinstance(parsed, dict):
                    messagebox.showerror("Validation Error", "Properties JSON must be an object (key-value dictionary).", parent=self)
                    return
                properties = parsed
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Parsing Error", f"Invalid JSON in properties:\n{e}", parent=self)
                return

        try:
            self.result = Node(name=name, uuid=uuid_val, properties=properties)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Model Error", str(e), parent=self)


class RelationDialog(tk.Toplevel):
    """Dialog for creating or editing a Relationship."""

    def __init__(self, parent, graph: Graph, relation: Optional[Relation] = None, title: Optional[str] = None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.graph = graph
        self.relation = relation
        self.result: Optional[Relation] = None

        self.title(title or ("Edit Relationship" if relation else "Create Relationship"))
        self.geometry("560x520")
        self.minsize(500, 460)
        self.configure(bg=BG_DARK)

        self._build_ui()
        self.wait_window()

    def _build_ui(self):
        container = ttk.Frame(self, style="Panel.TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.columnconfigure(1, weight=1)

        # Title
        hdr = ttk.Label(
            container,
            text="Edit Relationship" if self.relation else "Add New Relationship",
            font=("Helvetica", 14, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        hdr.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # Node options for dropdowns: "Name (UUID)"
        node_options = [f"{n.name} ({n.uuid})" for n in self.graph.nodes]
        uuid_to_opt = {n.uuid: f"{n.name} ({n.uuid})" for n in self.graph.nodes}
        opt_to_uuid = {f"{n.name} ({n.uuid})": n.uuid for n in self.graph.nodes}
        self.opt_to_uuid = opt_to_uuid

        # Source Node Dropdown
        lbl_source = ttk.Label(
            container,
            text="Source Node *:",
            font=("Helvetica", 11, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        lbl_source.grid(row=1, column=0, sticky="w", pady=6)

        default_source = uuid_to_opt.get(self.relation.source_uuid, "") if self.relation else (node_options[0] if node_options else "")
        self.source_var = tk.StringVar(value=default_source)
        self.source_combo = ttk.Combobox(container, textvariable=self.source_var, values=node_options, state="readonly")
        self.source_combo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=6)

        # Target Node Dropdown
        lbl_target = ttk.Label(
            container,
            text="Target Node *:",
            font=("Helvetica", 11, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        lbl_target.grid(row=2, column=0, sticky="w", pady=6)

        default_target = uuid_to_opt.get(self.relation.target_uuid, "") if self.relation else (node_options[1] if len(node_options) > 1 else (node_options[0] if node_options else ""))
        self.target_var = tk.StringVar(value=default_target)
        self.target_combo = ttk.Combobox(container, textvariable=self.target_var, values=node_options, state="readonly")
        self.target_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=6)

        # Relationship Name / Type
        lbl_name = ttk.Label(
            container,
            text="Type / Name *:",
            font=("Helvetica", 11, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        lbl_name.grid(row=3, column=0, sticky="w", pady=6)

        self.name_var = tk.StringVar(value=self.relation.relationship_name if self.relation else "")
        self.name_entry = ttk.Entry(container, textvariable=self.name_var)
        self.name_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=6)

        # Relationship UUID
        lbl_uuid = ttk.Label(
            container,
            text="Relation UUID *:",
            font=("Helvetica", 11, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        lbl_uuid.grid(row=4, column=0, sticky="w", pady=6)

        default_uuid = self.relation.relationship_uuid if self.relation else str(uuid.uuid4())
        self.uuid_var = tk.StringVar(value=default_uuid)
        self.uuid_entry = ttk.Entry(container, textvariable=self.uuid_var)
        self.uuid_entry.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=6)

        # Properties JSON
        lbl_props = ttk.Label(
            container,
            text="Properties (JSON):",
            font=("Helvetica", 11, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        lbl_props.grid(row=5, column=0, sticky="nw", pady=(10, 4))

        props_text = ""
        if self.relation and self.relation.properties:
            props_text = json.dumps(self.relation.properties, indent=2)

        self.props_box = tk.Text(
            container,
            height=6,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            font=("Courier", 10),
            padx=8,
            pady=8,
            bd=0,
        )
        self.props_box.insert("1.0", props_text)
        self.props_box.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(4, 16))
        container.rowconfigure(6, weight=1)

        # Buttons
        btn_frame = ttk.Frame(container, style="Panel.TFrame")
        btn_frame.grid(row=7, column=0, columnspan=2, sticky="e")

        btn_cancel = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_save = ttk.Button(btn_frame, text="Save Relationship", style="Primary.TButton", command=self._on_save)
        btn_save.pack(side="right")

    def _on_save(self):
        source_opt = self.source_var.get().strip()
        target_opt = self.target_var.get().strip()
        rel_name = self.name_var.get().strip()
        rel_uuid = self.uuid_var.get().strip()
        props_str = self.props_box.get("1.0", tk.END).strip()

        if not source_opt or source_opt not in self.opt_to_uuid:
            messagebox.showerror("Validation Error", "Please select a valid Source Node.", parent=self)
            return

        if not target_opt or target_opt not in self.opt_to_uuid:
            messagebox.showerror("Validation Error", "Please select a valid Target Node.", parent=self)
            return

        source_uuid = self.opt_to_uuid[source_opt]
        target_uuid = self.opt_to_uuid[target_opt]

        if not rel_name:
            messagebox.showerror("Validation Error", "Relationship Name cannot be empty.", parent=self)
            return

        if not CSVValidator.validate_uuid_format(rel_uuid):
            messagebox.showerror("Validation Error", f"Invalid UUID v4 format: '{rel_uuid}'", parent=self)
            return

        properties = None
        if props_str:
            try:
                parsed = json.loads(props_str)
                if not isinstance(parsed, dict):
                    messagebox.showerror("Validation Error", "Properties JSON must be an object (key-value dictionary).", parent=self)
                    return
                properties = parsed
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Parsing Error", f"Invalid JSON in properties:\n{e}", parent=self)
                return

        try:
            self.result = Relation(
                source_uuid=source_uuid,
                target_uuid=target_uuid,
                relationship_name=rel_name,
                relationship_uuid=rel_uuid,
                properties=properties,
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Model Error", str(e), parent=self)
