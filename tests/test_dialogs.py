"""Unit tests for NodeDialog and RelationDialog."""
import pytest
import tkinter as tk
from unittest.mock import patch
from src.models import Node, Relation, Graph
from src.gui.dialogs import NodeDialog, RelationDialog


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def sample_graph():
    node1 = Node(name="A", uuid="550e8400-e29b-41d4-a716-446655440000")
    node2 = Node(name="B", uuid="550e8400-e29b-41d4-a716-446655440001")
    return Graph(nodes=[node1, node2], relations=[], node_count=2, relation_count=0)


def test_node_dialog_creation_and_save(tk_root):
    with patch.object(NodeDialog, "wait_window", lambda self: None):
        dlg = NodeDialog(tk_root)
        dlg.name_var.set("TestNode")
        dlg.uuid_var.set("550e8400-e29b-41d4-a716-446655440010")
        dlg.props_box.delete("1.0", tk.END)
        dlg.props_box.insert("1.0", '{"env": "test"}')

        dlg._on_save()
        assert dlg.result is not None
        assert dlg.result.name == "TestNode"
        assert dlg.result.properties == {"env": "test"}


def test_node_dialog_validation_errors(tk_root):
    with patch.object(NodeDialog, "wait_window", lambda self: None), \
         patch("tkinter.messagebox.showerror") as mock_err:
        dlg = NodeDialog(tk_root)

        # Empty name
        dlg.name_var.set("")
        dlg._on_save()
        assert mock_err.called

        # Bad UUID
        dlg.name_var.set("Valid")
        dlg.uuid_var.set("not-a-uuid")
        dlg._on_save()
        assert mock_err.called

        # Invalid JSON
        dlg.uuid_var.set("550e8400-e29b-41d4-a716-446655440010")
        dlg.props_box.insert("1.0", "{bad json")
        dlg._on_save()
        assert mock_err.called

        # Non-dict JSON
        dlg.props_box.delete("1.0", tk.END)
        dlg.props_box.insert("1.0", '["not", "a", "dict"]')
        dlg._on_save()
        assert mock_err.called


def test_relation_dialog_creation_and_save(tk_root, sample_graph):
    with patch.object(RelationDialog, "wait_window", lambda self: None):
        dlg = RelationDialog(tk_root, graph=sample_graph)
        dlg.name_var.set("links_to")
        dlg.uuid_var.set("550e8400-e29b-41d4-a716-446655440099")
        dlg.props_box.delete("1.0", tk.END)
        dlg.props_box.insert("1.0", '{"weight": 10}')

        dlg._on_save()
        assert dlg.result is not None
        assert dlg.result.relationship_name == "links_to"
        assert dlg.result.properties == {"weight": 10}


def test_relation_dialog_validation_errors(tk_root, sample_graph):
    with patch.object(RelationDialog, "wait_window", lambda self: None), \
         patch("tkinter.messagebox.showerror") as mock_err:
        dlg = RelationDialog(tk_root, graph=sample_graph)

        # Missing name
        dlg.name_var.set("")
        dlg._on_save()
        assert mock_err.called

        # Bad UUID
        dlg.name_var.set("connects")
        dlg.uuid_var.set("bad-uuid")
        dlg._on_save()
        assert mock_err.called

        # Invalid JSON
        dlg.uuid_var.set("550e8400-e29b-41d4-a716-446655440099")
        dlg.props_box.insert("1.0", "{bad json")
        dlg._on_save()
        assert mock_err.called
