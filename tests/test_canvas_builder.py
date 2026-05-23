import json
from obsidian_cli.canvas_builder import CanvasBuilder


def test_empty_canvas_has_valid_structure():
    cb = CanvasBuilder()
    result = cb.build()
    assert "nodes" in result
    assert "edges" in result
    assert result["nodes"] == []
    assert result["edges"] == []


def test_add_text_node():
    cb = CanvasBuilder()
    node_id = cb.add_text_node("Hello World")
    result = cb.build()
    assert len(result["nodes"]) == 1
    node = result["nodes"][0]
    assert node["type"] == "text"
    assert node["text"] == "Hello World"
    assert node["id"] == node_id
    assert "x" in node and "y" in node
    assert "width" in node and "height" in node


def test_add_file_node():
    cb = CanvasBuilder()
    cb.add_file_node("AI Workspace/project/arch.md")
    result = cb.build()
    node = result["nodes"][0]
    assert node["type"] == "file"
    assert node["file"] == "AI Workspace/project/arch.md"


def test_add_link_node():
    cb = CanvasBuilder()
    cb.add_link_node("https://example.com")
    result = cb.build()
    node = result["nodes"][0]
    assert node["type"] == "link"
    assert node["url"] == "https://example.com"


def test_add_group_node():
    cb = CanvasBuilder()
    cb.add_group_node("Backend Services")
    result = cb.build()
    node = result["nodes"][0]
    assert node["type"] == "group"
    assert node["label"] == "Backend Services"


def test_add_edge_connects_nodes():
    cb = CanvasBuilder()
    id1 = cb.add_text_node("A")
    id2 = cb.add_text_node("B")
    cb.add_edge(id1, id2, label="calls", color="4")
    result = cb.build()
    assert len(result["edges"]) == 1
    edge = result["edges"][0]
    assert edge["fromNode"] == id1
    assert edge["toNode"] == id2
    assert edge["label"] == "calls"
    assert edge["color"] == "4"


def test_nodes_auto_positioned_in_grid():
    cb = CanvasBuilder()
    for i in range(4):
        cb.add_text_node(f"Node {i}")
    result = cb.build()
    positions = [(n["x"], n["y"]) for n in result["nodes"]]
    assert len(set(positions)) == 4


def test_build_from_spec():
    spec = {
        "nodes": [
            {"type": "text", "text": "Overview"},
            {"type": "file", "file": "AI Workspace/project/arch.md"},
        ],
        "edges": [
            {"from": 0, "to": 1, "label": "documents"}
        ]
    }
    cb = CanvasBuilder.from_spec(spec)
    result = cb.build()
    assert len(result["nodes"]) == 2
    assert len(result["edges"]) == 1
    assert result["edges"][0]["label"] == "documents"


def test_to_json_string():
    cb = CanvasBuilder()
    cb.add_text_node("Test")
    json_str = cb.to_json()
    parsed = json.loads(json_str)
    assert parsed["nodes"][0]["text"] == "Test"


def test_from_spec_forwards_color():
    spec = {
        "nodes": [
            {"type": "text", "text": "Important", "color": "1"},
            {"type": "file", "file": "AI Workspace/arch.md", "color": "4"},
        ],
        "edges": []
    }
    cb = CanvasBuilder.from_spec(spec)
    result = cb.build()
    assert result["nodes"][0]["color"] == "1"
    assert result["nodes"][1]["color"] == "4"
