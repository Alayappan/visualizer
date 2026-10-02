"""Detail panel component for inspecting node and relationship properties."""
import tkinter as tk
from tkinter import ttk, messagebox
import json
from typing import Optional, Callable
from src.models import Node, Relation, Graph
from src.gui.theme import (
    BG_PANEL, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, WARNING_AMBER
)


class DetailPanel(ttk.Frame):
    """Side panel displaying formatted attributes and JSON properties for selected graph elements."""

    def __init__(
        self,
        parent,
        on_close: Optional[Callable[[], None]] = None,
        on_edit_node: Optional[Callable[[Node], None]] = None,
        on_delete_node: Optional[Callable[[Node], None]] = None,
        on_edit_relation: Optional[Callable[[Relation], None]] = None,
        on_delete_relation: Optional[Callable[[Relation], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, style="Panel.TFrame", **kwargs)
        self.on_close = on_close
        self.on_edit_node = on_edit_node
        self.on_delete_node = on_delete_node
        self.on_edit_relation = on_edit_relation
        self.on_delete_relation = on_delete_relation
        self.current_graph: Optional[Graph] = None
        self.btn_edit: Optional[tk.Button] = None
        self.btn_delete: Optional[tk.Button] = None
        self.btn_edit_rel: Optional[tk.Button] = None
        self.btn_delete_rel: Optional[tk.Button] = None
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header Frame
        header_frame = ttk.Frame(self, style="Panel.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        header_frame.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(
            header_frame,
            text="Properties Inspector",
            font=("Helvetica", 14, "bold"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.close_btn = tk.Button(
            header_frame,
            text="✕",
            font=("Helvetica", 11, "bold"),
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            bd=0,
            cursor="hand2",
            command=self.clear,
        )
        self.close_btn.grid(row=0, column=1, sticky="e")

        # Separator
        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=1, column=0, sticky="ew", padx=10, pady=4)

        # Content container
        self.content_frame = ttk.Frame(self, style="Panel.TFrame")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=8)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(5, weight=1)

        # Placeholder message
        self.placeholder_label = ttk.Label(
            self.content_frame,
            text="Click on any node or relationship\nin the graph to view its details.",
            font=("Helvetica", 11),
            foreground=TEXT_MUTED,
            background=BG_PANEL,
            justify="center",
        )
        self.placeholder_label.pack(expand=True, fill="both", pady=40)

        # Detail widgets (hidden until item selected)
        self.info_container = ttk.Frame(self.content_frame, style="Panel.TFrame")
        self.info_container.columnconfigure(1, weight=1)

    def set_graph(self, graph: Optional[Graph]):
        """Reference the active graph for entity lookups."""
        self.current_graph = graph

    def display_node(self, node: Node):
        """Populate panel with selected Node details."""
        self._clear_content()

        self.title_label.config(text="Node Details")

        row = 0
        # Type Badge
        badge = tk.Label(
            self.info_container,
            text="  NODE  ",
            font=("Helvetica", 9, "bold"),
            bg=ACCENT_BLUE,
            fg="#ffffff",
            padx=4,
            pady=2,
        )
        badge.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1

        # Name
        self._add_field(row, "Name:", node.name, is_bold=True)
        row += 1

        # UUID
        self._add_field(row, "UUID:", node.uuid, copyable=True)
        row += 1

        # Connected Relations Summary
        if self.current_graph:
            incident = self.current_graph.get_relations_for_node(node.uuid)
            self._add_field(row, "Connections:", f"{len(incident)} relationship(s)")
            row += 1

        # Properties Table
        self._add_properties_section(row, node.properties)
        row += 1

        # Action Buttons (Edit / Delete)
        if self.on_edit_node or self.on_delete_node:
            btn_box = ttk.Frame(self.info_container, style="Panel.TFrame")
            btn_box.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(14, 0))
            if self.on_edit_node:
                self.btn_edit = tk.Button(
                    btn_box,
                    text="✏ Edit Node",
                    font=("Helvetica", 9, "bold"),
                    bg=BG_CARD,
                    fg=TEXT_PRIMARY,
                    activebackground=BG_PANEL,
                    activeforeground=TEXT_PRIMARY,
                    bd=0,
                    padx=8,
                    pady=4,
                    cursor="hand2",
                    command=lambda: self.on_edit_node(node) if self.on_edit_node else None,
                )
                self.btn_edit.pack(side="left", padx=(0, 8))
            if self.on_delete_node:
                self.btn_delete = tk.Button(
                    btn_box,
                    text="🗑 Delete Node",
                    font=("Helvetica", 9, "bold"),
                    bg=BG_CARD,
                    fg="#f87171",
                    activebackground=BG_PANEL,
                    activeforeground="#f87171",
                    bd=0,
                    padx=8,
                    pady=4,
                    cursor="hand2",
                    command=lambda: self.on_delete_node(node) if self.on_delete_node else None,
                )
                self.btn_delete.pack(side="left")

        self.info_container.pack(fill="both", expand=True)

    def display_relation(self, relation: Relation):
        """Populate panel with selected Relation details."""
        self._clear_content()

        self.title_label.config(text="Relationship Details")

        row = 0
        # Type Badge
        badge = tk.Label(
            self.info_container,
            text="  RELATIONSHIP  ",
            font=("Helvetica", 9, "bold"),
            bg=WARNING_AMBER,
            fg="#000000",
            padx=4,
            pady=2,
        )
        badge.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1

        # Relationship Name
        self._add_field(row, "Type:", relation.relationship_name, is_bold=True)
        row += 1

        # UUID
        self._add_field(row, "UUID:", relation.relationship_uuid, copyable=True)
        row += 1

        # Source Node
        source_name = relation.source_uuid
        if self.current_graph:
            s_node = self.current_graph.get_node(relation.source_uuid)
            if s_node:
                source_name = f"{s_node.name} ({s_node.uuid[:8]}...)"
        self._add_field(row, "From (Source):", source_name)
        row += 1

        # Target Node
        target_name = relation.target_uuid
        if self.current_graph:
            t_node = self.current_graph.get_node(relation.target_uuid)
            if t_node:
                target_name = f"{t_node.name} ({t_node.uuid[:8]}...)"
        self._add_field(row, "To (Target):", target_name)
        row += 1

        # Properties Table
        self._add_properties_section(row, relation.properties)
        row += 1

        # Action Buttons (Edit / Delete)
        if self.on_edit_relation or self.on_delete_relation:
            btn_box = ttk.Frame(self.info_container, style="Panel.TFrame")
            btn_box.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(14, 0))
            if self.on_edit_relation:
                self.btn_edit_rel = tk.Button(
                    btn_box,
                    text="✏ Edit Relation",
                    font=("Helvetica", 9, "bold"),
                    bg=BG_CARD,
                    fg=TEXT_PRIMARY,
                    activebackground=BG_PANEL,
                    activeforeground=TEXT_PRIMARY,
                    bd=0,
                    padx=8,
                    pady=4,
                    cursor="hand2",
                    command=lambda: self.on_edit_relation(relation) if self.on_edit_relation else None,
                )
                self.btn_edit_rel.pack(side="left", padx=(0, 8))
            if self.on_delete_relation:
                self.btn_delete_rel = tk.Button(
                    btn_box,
                    text="🗑 Delete Relation",
                    font=("Helvetica", 9, "bold"),
                    bg=BG_CARD,
                    fg="#f87171",
                    activebackground=BG_PANEL,
                    activeforeground="#f87171",
                    bd=0,
                    padx=8,
                    pady=4,
                    cursor="hand2",
                    command=lambda: self.on_delete_relation(relation) if self.on_delete_relation else None,
                )
                self.btn_delete_rel.pack(side="left")

        self.info_container.pack(fill="both", expand=True)

    def _add_field(self, row: int, label_text: str, value_text: str, is_bold: bool = False, copyable: bool = False):
        lbl = ttk.Label(
            self.info_container,
            text=label_text,
            font=("Helvetica", 10, "bold"),
            foreground=TEXT_SECONDARY,
            background=BG_PANEL,
        )
        lbl.grid(row=row, column=0, sticky="nw", pady=3)

        val_frame = ttk.Frame(self.info_container, style="Panel.TFrame")
        val_frame.grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=3)
        val_frame.columnconfigure(0, weight=1)

        val = ttk.Label(
            val_frame,
            text=value_text,
            font=("Helvetica", 10, "bold" if is_bold else "normal"),
            foreground=TEXT_PRIMARY,
            background=BG_PANEL,
            wraplength=180,
        )
        val.grid(row=0, column=0, sticky="w")

        if copyable:
            copy_btn = tk.Button(
                val_frame,
                text="Copy",
                font=("Helvetica", 8),
                bg=BG_CARD,
                fg=TEXT_PRIMARY,
                bd=0,
                padx=4,
                pady=1,
                cursor="hand2",
                command=lambda: self._copy_to_clipboard(value_text),
            )
            copy_btn.grid(row=0, column=1, sticky="e", padx=(4, 0))

    def _add_properties_section(self, row: int, properties: Optional[dict]):
        prop_lbl = ttk.Label(
            self.info_container,
            text="Properties:",
            font=("Helvetica", 10, "bold"),
            foreground=TEXT_SECONDARY,
            background=BG_PANEL,
        )
        prop_lbl.grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 4))
        row += 1

        if not properties or not isinstance(properties, dict) or len(properties) == 0:
            none_lbl = ttk.Label(
                self.info_container,
                text="(No additional properties)",
                font=("Helvetica", 9, "italic"),
                foreground=TEXT_MUTED,
                background=BG_PANEL,
            )
            none_lbl.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)
            return

        # Treeview table for properties
        tree_frame = ttk.Frame(self.info_container, style="Panel.TFrame")
        tree_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=4)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        tree = ttk.Treeview(tree_frame, columns=("Key", "Value"), show="headings", height=min(8, len(properties)))
        tree.heading("Key", text="Key")
        tree.heading("Value", text="Value")
        tree.column("Key", width=90, anchor="w")
        tree.column("Value", width=160, anchor="w")

        for k, v in properties.items():
            val_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            tree.insert("", "end", values=(k, val_str))

        tree.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def _clear_content(self):
        self.placeholder_label.pack_forget()
        for child in self.info_container.winfo_children():
            child.destroy()
        self.info_container.pack_forget()
        self.btn_edit = None
        self.btn_delete = None
        self.btn_edit_rel = None
        self.btn_delete_rel = None

    def clear(self):
        """Reset panel to empty placeholder state."""
        self._clear_content()
        self.title_label.config(text="Properties Inspector")
        self.placeholder_label.pack(expand=True, fill="both", pady=40)
        if self.on_close:
            self.on_close()

