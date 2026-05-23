import json
import uuid


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


def _grid_position(index: int, columns: int = 3,
                   cell_w: int = 250, cell_h: int = 150,
                   gap: int = 60) -> tuple[int, int]:
    col = index % columns
    row = index // columns
    return col * (cell_w + gap), row * (cell_h + gap)


_DEFAULT_APP_STATE = {
    "gridSize": None,
    "viewBackgroundColor": "#ffffff",
}


class ExcalidrawBuilder:
    def __init__(self):
        self._elements: list[dict] = []

    def _shape_count(self) -> int:
        return sum(1 for e in self._elements if e["type"] not in ("arrow", "line"))

    def _base_element(self, el_type: str, width: int = 200, height: int = 100,
                      stroke_color: str = "#1e1e2e",
                      background_color: str = "transparent",
                      fill_style: str = "hachure",
                      stroke_width: int = 2,
                      roughness: int = 1) -> dict:
        x, y = _grid_position(self._shape_count())
        return {
            "id": _new_id(),
            "type": el_type,
            "x": x, "y": y,
            "width": width, "height": height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": background_color,
            "fillStyle": fill_style,
            "strokeWidth": stroke_width,
            "roughness": roughness,
            "opacity": 100,
            "groupIds": [],
            "roundness": None,
            "isDeleted": False,
            "boundElements": [],
            "updated": 0,
            "link": None,
            "locked": False,
        }

    def add_rectangle(self, label: str = "",
                      stroke_color: str = "#1e1e2e",
                      background_color: str = "transparent",
                      width: int = 200, height: int = 100) -> str:
        el = self._base_element("rectangle", width, height, stroke_color, background_color)
        if label:
            el["label"] = {"text": label}
        self._elements.append(el)
        return el["id"]

    def add_ellipse(self, label: str = "",
                    stroke_color: str = "#1e1e2e",
                    background_color: str = "transparent",
                    width: int = 200, height: int = 100) -> str:
        el = self._base_element("ellipse", width, height, stroke_color, background_color)
        if label:
            el["label"] = {"text": label}
        self._elements.append(el)
        return el["id"]

    def add_diamond(self, label: str = "",
                    stroke_color: str = "#1e1e2e",
                    background_color: str = "transparent",
                    width: int = 200, height: int = 100) -> str:
        el = self._base_element("diamond", width, height, stroke_color, background_color)
        if label:
            el["label"] = {"text": label}
        self._elements.append(el)
        return el["id"]

    def add_text(self, text: str,
                 font_size: int = 20,
                 font_family: int = 1,
                 text_align: str = "left") -> str:
        el = self._base_element("text", width=200, height=25,
                                stroke_color="#1e1e2e", background_color="transparent")
        el.update({
            "text": text,
            "fontSize": font_size,
            "fontFamily": font_family,
            "textAlign": text_align,
            "verticalAlign": "top",
            "containerId": None,
            "originalText": text,
        })
        self._elements.append(el)
        return el["id"]

    def add_arrow(self, from_id: str, to_id: str,
                  label: str = "",
                  stroke_color: str = "#1e1e2e") -> str:
        el = {
            "id": _new_id(),
            "type": "arrow",
            "x": 0, "y": 0,
            "width": 100, "height": 0,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "hachure",
            "strokeWidth": 2,
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "roundness": {"type": 2},
            "isDeleted": False,
            "boundElements": [],
            "updated": 0,
            "link": None,
            "locked": False,
            "points": [[0, 0], [100, 0]],
            "lastCommittedPoint": None,
            "startBinding": {"elementId": from_id, "focus": 0, "gap": 1},
            "endBinding": {"elementId": to_id, "focus": 0, "gap": 1},
            "startArrowhead": None,
            "endArrowhead": "arrow",
        }
        if label:
            el["label"] = {"text": label}
        self._elements.append(el)
        return el["id"]

    def add_line(self, from_id: str, to_id: str,
                 stroke_color: str = "#1e1e2e") -> str:
        el = {
            "id": _new_id(),
            "type": "line",
            "x": 0, "y": 0,
            "width": 100, "height": 0,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "hachure",
            "strokeWidth": 2,
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "roundness": None,
            "isDeleted": False,
            "boundElements": [],
            "updated": 0,
            "link": None,
            "locked": False,
            "points": [[0, 0], [100, 0]],
            "lastCommittedPoint": None,
            "startBinding": {"elementId": from_id, "focus": 0, "gap": 1},
            "endBinding": {"elementId": to_id, "focus": 0, "gap": 1},
            "startArrowhead": None,
            "endArrowhead": None,
        }
        self._elements.append(el)
        return el["id"]

    def build(self) -> dict:
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "obsidian-cli",
            "elements": list(self._elements),
            "appState": dict(_DEFAULT_APP_STATE),
            "files": {},
        }

    def to_json(self) -> str:
        return json.dumps(self.build(), indent=2)

    @classmethod
    def from_spec(cls, spec: dict) -> "ExcalidrawBuilder":
        eb = cls()
        index_to_id: dict[int, str] = {}
        for i, el_spec in enumerate(spec.get("elements", [])):
            t = el_spec.get("type", "rectangle")
            label = el_spec.get("label", el_spec.get("text", ""))
            stroke = el_spec.get("stroke_color", "#1e1e2e")
            bg = el_spec.get("background_color", "transparent")
            if t == "rectangle":
                eid = eb.add_rectangle(label, stroke_color=stroke, background_color=bg)
            elif t == "ellipse":
                eid = eb.add_ellipse(label, stroke_color=stroke, background_color=bg)
            elif t == "diamond":
                eid = eb.add_diamond(label, stroke_color=stroke, background_color=bg)
            elif t == "text":
                eid = eb.add_text(label or el_spec.get("text", ""),
                                  font_size=el_spec.get("font_size", 20))
            else:
                eid = eb.add_rectangle(label)
            index_to_id[i] = eid
        for arrow_spec in spec.get("arrows", []):
            from_id = index_to_id.get(arrow_spec.get("from"))
            to_id = index_to_id.get(arrow_spec.get("to"))
            if from_id and to_id:
                eb.add_arrow(from_id, to_id, label=arrow_spec.get("label", ""))
        return eb
