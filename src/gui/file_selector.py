"""File selection and validation frame for nodes and relations CSV files."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable, List
import pandas as pd

from src.models import Graph
from src.validators import CSVValidator
from src.validators.graph_parser import GraphParser
from src.gui.theme import (
    BG_DARK, BG_PANEL, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, SUCCESS_GREEN, SUCCESS_BG, ERROR_RED, ERROR_BG, WARNING_AMBER
)


class FileSelector(ttk.Frame):
    """Component managing CSV selection, schema validation feedback, and graph loading."""

    def __init__(self, parent, on_graph_loaded: Callable[[Graph], None], **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.on_graph_loaded = on_graph_loaded

        self.nodes_path_var = tk.StringVar()
        self.relations_path_var = tk.StringVar()
        self.nodes_df: Optional[pd.DataFrame] = None
        self.relations_df: Optional[pd.DataFrame] = None

        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # Container Card
        card = ttk.Frame(self, style="Panel.TFrame")
        card.pack(fill="both", expand=True, padx=30, pady=30)
        card.columnconfigure(0, weight=1)

        # Header Title
        title = ttk.Label(
            card,
            text="Upload & Validate Graph CSV Files",
            style="Header.TLabel",
        )
        title.pack(anchor="w", padx=24, pady=(24, 6))

        subtitle = ttk.Label(
            card,
            text="Select your nodes.csv and relations.csv datasets to validate schema and render the interactive graph.",
            style="Subheader.TLabel",
        )
        subtitle.pack(anchor="w", padx=24, pady=(0, 20))

        # Form Card
        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x", padx=24, pady=10)
        form.columnconfigure(1, weight=1)

        # --- Nodes File Row ---
        lbl_nodes = ttk.Label(
            form,
            text="Nodes CSV:",
            font=("Helvetica", 11, "bold"),
            background=BG_CARD,
            foreground=TEXT_PRIMARY,
        )
        lbl_nodes.grid(row=0, column=0, sticky="w", padx=(16, 12), pady=(16, 10))

        self.entry_nodes = ttk.Entry(form, textvariable=self.nodes_path_var, width=50)
        self.entry_nodes.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(16, 10))

        btn_browse_nodes = ttk.Button(
            form,
            text="Browse...",
            command=self._browse_nodes,
        )
        btn_browse_nodes.grid(row=0, column=2, sticky="e", padx=(0, 16), pady=(16, 10))

        # --- Relations File Row ---
        lbl_rels = ttk.Label(
            form,
            text="Relations CSV:",
            font=("Helvetica", 11, "bold"),
            background=BG_CARD,
            foreground=TEXT_PRIMARY,
        )
        lbl_rels.grid(row=1, column=0, sticky="w", padx=(16, 12), pady=(0, 16))

        self.entry_rels = ttk.Entry(form, textvariable=self.relations_path_var, width=50)
        self.entry_rels.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 16))

        btn_browse_rels = ttk.Button(
            form,
            text="Browse...",
            command=self._browse_relations,
        )
        btn_browse_rels.grid(row=1, column=2, sticky="e", padx=(0, 16), pady=(0, 16))

        # Action Buttons Row
        btn_bar = ttk.Frame(card, style="Panel.TFrame")
        btn_bar.pack(fill="x", padx=24, pady=14)

        self.btn_validate = ttk.Button(
            btn_bar,
            text="✓ Validate CSV Files",
            style="Primary.TButton",
            command=self.validate_files,
        )
        self.btn_validate.pack(side="left", padx=(0, 10))

        self.btn_load_sample = ttk.Button(
            btn_bar,
            text="Sample Data",
            command=self.load_sample_data,
        )
        self.btn_load_sample.pack(side="left", padx=5)

        # self.btn_load_family = ttk.Button(
        #     btn_bar,
        #     text="👨‍👩‍👧‍👦 Family Dataset",
        #     command=self.load_family_data,
        # )
        # self.btn_load_family.pack(side="left", padx=5)

        self.btn_visualize = ttk.Button(
            btn_bar,
            text="🚀 Visualize Graph",
            style="Success.TButton",
            state="disabled",
            command=self._on_visualize_click,
        )
        self.btn_visualize.pack(side="right")

        # Feedback Section
        self.feedback_container = ttk.Frame(card, style="Panel.TFrame")
        self.feedback_container.pack(fill="both", expand=True, padx=24, pady=(10, 24))
        self.feedback_container.columnconfigure(0, weight=1)
        self.feedback_container.rowconfigure(1, weight=1)

        self.status_banner = tk.Label(
            self.feedback_container,
            text="",
            font=("Helvetica", 11, "bold"),
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            anchor="w",
            padx=12,
            pady=8,
        )
        self.status_banner.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Error display box with scrollbar
        self.error_box_frame = ttk.Frame(self.feedback_container, style="Panel.TFrame")
        self.error_box_frame.grid(row=1, column=0, sticky="nsew")
        self.error_box_frame.columnconfigure(0, weight=1)
        self.error_box_frame.rowconfigure(0, weight=1)

        self.error_text = tk.Text(
            self.error_box_frame,
            bg=BG_DARK,
            fg=ERROR_RED,
            font=("Courier", 11),
            insertbackground=TEXT_PRIMARY,
            wrap="word",
            bd=0,
            padx=10,
            pady=10,
            height=8,
        )
        self.error_text.grid(row=0, column=0, sticky="nsew")

        error_scroll = ttk.Scrollbar(self.error_box_frame, orient="vertical", command=self.error_text.yview)
        self.error_text.configure(yscrollcommand=error_scroll.set)
        error_scroll.grid(row=0, column=1, sticky="ns")

        self.error_box_frame.grid_remove()  # Hide until errors exist

    def _browse_nodes(self):
        filepath = filedialog.askopenfilename(
            title="Select Nodes CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filepath:
            self.nodes_path_var.set(filepath)
            self._reset_validation_state()

    def _browse_relations(self):
        filepath = filedialog.askopenfilename(
            title="Select Relations CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filepath:
            self.relations_path_var.set(filepath)
            self._reset_validation_state()

    def load_sample_data(self):
        """Automatically load included valid test CSV fixtures."""
        fixtures_dir = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"
        nodes_csv = fixtures_dir / "valid_nodes.csv"
        relations_csv = fixtures_dir / "valid_relations.csv"

        if nodes_csv.exists() and relations_csv.exists():
            self.nodes_path_var.set(str(nodes_csv))
            self.relations_path_var.set(str(relations_csv))
            self.validate_files()
        else:
            messagebox.showwarning("Sample Files Not Found", f"Could not find fixture files in:\n{fixtures_dir}")

    def load_family_data(self):
        """Automatically load the family graph dataset from data/ directory."""
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        nodes_csv = data_dir / "family_nodes.csv"
        relations_csv = data_dir / "family_relations.csv"

        if nodes_csv.exists() and relations_csv.exists():
            self.nodes_path_var.set(str(nodes_csv))
            self.relations_path_var.set(str(relations_csv))
            self.validate_files()
        else:
            messagebox.showwarning("Family Dataset Not Found", f"Could not find family CSV files in:\n{data_dir}")

    def _reset_validation_state(self):
        self.btn_visualize.configure(state="disabled")
        self.status_banner.config(text="", bg=BG_PANEL, fg=TEXT_SECONDARY)
        self.error_text.delete("1.0", tk.END)
        self.error_box_frame.grid_remove()
        self.nodes_df = None
        self.relations_df = None

    def validate_files(self) -> bool:
        """Execute CSV validation rules against the selected files."""
        nodes_path = self.nodes_path_var.get().strip()
        relations_path = self.relations_path_var.get().strip()

        if not nodes_path:
            self._show_errors(["Please select a Nodes CSV file."])
            return False

        if not relations_path:
            self._show_errors(["Please select a Relations CSV file."])
            return False

        all_errors: List[str] = []

        # Validate Nodes CSV
        nodes_valid, node_errs, nodes_df = CSVValidator.validate_nodes_csv(nodes_path)
        all_errors.extend(node_errs)

        if not nodes_valid:
            self._show_errors(all_errors)
            return False

        valid_node_uuids = set(nodes_df["uuid"].astype(str).str.strip().tolist())

        # Validate Relations CSV
        rels_valid, rel_errs, rels_df = CSVValidator.validate_relations_csv(relations_path, valid_node_uuids)
        all_errors.extend(rel_errs)

        if not rels_valid:
            self._show_errors(all_errors)
            return False

        # Success!
        self.nodes_df = nodes_df
        self.relations_df = rels_df
        node_count = len(nodes_df)
        rel_count = len(rels_df)

        self._show_success(node_count, rel_count)
        return True

    def _show_errors(self, errors: List[str]):
        self.btn_visualize.configure(state="disabled")
        self.status_banner.config(
            text=f"✗ Validation Failed ({len(errors)} error{'s' if len(errors) != 1 else ''} found):",
            bg=ERROR_BG,
            fg="#ffffff",
        )
        self.error_text.delete("1.0", tk.END)
        for err in errors:
            self.error_text.insert(tk.END, f"• {err}\n")
        self.error_box_frame.grid()

    def _show_success(self, node_count: int, rel_count: int):
        self.error_box_frame.grid_remove()
        self.status_banner.config(
            text=f"✓ Validation Successful! Loaded {node_count} node(s) and {rel_count} relation(s). Ready to visualize.",
            bg=SUCCESS_BG,
            fg="#ffffff",
        )
        self.btn_visualize.configure(state="normal")

    def get_paths(self):
        """Return the currently selected CSV Path objects if set."""
        np = Path(self.nodes_path_var.get().strip()) if self.nodes_path_var.get().strip() else None
        rp = Path(self.relations_path_var.get().strip()) if self.relations_path_var.get().strip() else None
        return np, rp

    def _on_visualize_click(self):
        if self.nodes_df is not None and self.relations_df is not None:
            graph = GraphParser.build_graph(self.nodes_df, self.relations_df)
            np, rp = self.get_paths()
            self.on_graph_loaded(graph, np, rp)
        else:
            self.validate_files()

