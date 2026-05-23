import json
import pytest
from obsidian_cli.excalidraw_builder import ExcalidrawBuilder


def test_builder_produces_valid_structure():
    eb = ExcalidrawBuilder()
    result = eb.build()
    assert result["type"] == "excalidraw"
    assert result["version"] == 2
    assert "elements" in result
    assert "appState" in result
    assert "files" in result


def test_add_rectangle_returns_id():
    eb = ExcalidrawBuilder()
    nid = eb.add_rectangle("My Box")
    assert isinstance(nid, str)
    assert len(nid) == 16
    assert len(eb._elements) == 1
    el = eb._elements[0]
    assert el["type"] == "rectangle"
    assert el["id"] == nid


def test_add_text_element():
    eb = ExcalidrawBuilder()
    nid = eb.add_text("Hello World")
    assert eb._elements[0]["type"] == "text"
    assert eb._elements[0]["text"] == "Hello World"


def test_add_ellipse():
    eb = ExcalidrawBuilder()
    nid = eb.add_ellipse("Circle Label")
    assert eb._elements[0]["type"] == "ellipse"


def test_add_diamond():
    eb = ExcalidrawBuilder()
    nid = eb.add_diamond("Decision")
    assert eb._elements[0]["type"] == "diamond"


def test_add_arrow_connects_elements():
    eb = ExcalidrawBuilder()
    id1 = eb.add_rectangle("Start")
    id2 = eb.add_rectangle("End")
    arrow_id = eb.add_arrow(id1, id2, label="leads to")
    arrows = [e for e in eb._elements if e["type"] == "arrow"]
    assert len(arrows) == 1
    assert arrows[0]["startBinding"]["elementId"] == id1
    assert arrows[0]["endBinding"]["elementId"] == id2


def test_add_line():
    eb = ExcalidrawBuilder()
    id1 = eb.add_rectangle("A")
    id2 = eb.add_rectangle("B")
    eb.add_line(id1, id2)
    lines = [e for e in eb._elements if e["type"] == "line"]
    assert len(lines) == 1


def test_grid_layout_positions_elements():
    eb = ExcalidrawBuilder()
    for i in range(4):
        eb.add_rectangle(f"Box {i}")
    rects = [e for e in eb._elements if e["type"] == "rectangle"]
    assert rects[0]["y"] == rects[1]["y"] == rects[2]["y"]
    assert rects[3]["y"] > rects[0]["y"]


def test_custom_colors():
    eb = ExcalidrawBuilder()
    eb.add_rectangle("Colored", stroke_color="#ff0000", background_color="#00ff00")
    el = eb._elements[0]
    assert el["strokeColor"] == "#ff0000"
    assert el["backgroundColor"] == "#00ff00"


def test_to_json_valid():
    eb = ExcalidrawBuilder()
    eb.add_text("Hello")
    j = eb.to_json()
    parsed = json.loads(j)
    assert parsed["type"] == "excalidraw"


def test_from_spec_nodes_and_arrows():
    spec = {
        "elements": [
            {"type": "rectangle", "label": "Start"},
            {"type": "ellipse", "label": "Process"},
            {"type": "diamond", "label": "Decision"},
            {"type": "text", "text": "Note"},
        ],
        "arrows": [
            {"from": 0, "to": 1, "label": "next"},
        ],
    }
    eb = ExcalidrawBuilder.from_spec(spec)
    rects = [e for e in eb._elements if e["type"] == "rectangle"]
    ellipses = [e for e in eb._elements if e["type"] == "ellipse"]
    arrows = [e for e in eb._elements if e["type"] == "arrow"]
    assert len(rects) == 1
    assert len(ellipses) == 1
    assert len(arrows) == 1
