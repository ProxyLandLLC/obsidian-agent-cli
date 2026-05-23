import json
import uuid


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


def _grid_position(index: int, columns: int = 3,
                   cell_w: int = 300, cell_h: int = 200,
                   gap: int = 50) -> tuple[int, int]:
    col = index % columns
    row = index // columns
    return col * (cell_w + gap), row * (cell_h + gap)


class CanvasBuilder:
    def __init__(self):
        self._nodes: list[dict] = []
        self._edges: list[dict] = []

    def add_text_node(self, text: str, color: str = "",
                      width: int = 250, height: int = 100) -> str:
        node_id = _new_id()
        x, y = _grid_position(len(self._nodes))
        node = {"id": node_id, "type": "text", "text": text,
                 "x": x, "y": y, "width": width, "height": height}
        if color:
            node["color"] = color
        self._nodes.append(node)
        return node_id

    def add_file_node(self, file_path: str, subpath: str = "",
                      color: str = "", width: int = 400, height: int = 300) -> str:
        node_id = _new_id()
        x, y = _grid_position(len(self._nodes))
        node = {"id": node_id, "type": "file", "file": file_path,
                 "x": x, "y": y, "width": width, "height": height}
        if subpath:
            node["subpath"] = subpath
        if color:
            node["color"] = color
        self._nodes.append(node)
        return node_id

    def add_link_node(self, url: str, color: str = "",
                      width: int = 400, height: int = 300) -> str:
        node_id = _new_id()
        x, y = _grid_position(len(self._nodes))
        node = {"id": node_id, "type": "link", "url": url,
                 "x": x, "y": y, "width": width, "height": height}
        if color:
            node["color"] = color
        self._nodes.append(node)
        return node_id

    def add_group_node(self, label: str = "", background: str = "",
                       background_style: str = "cover",
                       color: str = "", width: int = 600, height: int = 400) -> str:
        node_id = _new_id()
        x, y = _grid_position(len(self._nodes))
        node = {"id": node_id, "type": "group",
                 "x": x, "y": y, "width": width, "height": height}
        if label:
            node["label"] = label
        if background:
            node["background"] = background
            node["backgroundStyle"] = background_style
        if color:
            node["color"] = color
        self._nodes.append(node)
        return node_id

    def add_edge(self, from_id: str, to_id: str,
                 label: str = "", color: str = "",
                 from_side: str = "right", to_side: str = "left",
                 from_end: str = "none", to_end: str = "arrow") -> str:
        edge_id = _new_id()
        edge = {"id": edge_id, "fromNode": from_id, "toNode": to_id,
                 "fromSide": from_side, "toSide": to_side,
                 "fromEnd": from_end, "toEnd": to_end}
        if label:
            edge["label"] = label
        if color:
            edge["color"] = color
        self._edges.append(edge)
        return edge_id

    def build(self) -> dict:
        return {"nodes": list(self._nodes), "edges": list(self._edges)}

    def to_json(self) -> str:
        return json.dumps(self.build(), indent=2)

    @classmethod
    def from_spec(cls, spec: dict) -> "CanvasBuilder":
        cb = cls()
        index_to_id: dict[int, str] = {}
        for i, node_spec in enumerate(spec.get("nodes", [])):
            t = node_spec.get("type", "text")
            color = node_spec.get("color", "")
            if t == "text":
                nid = cb.add_text_node(node_spec.get("text", ""), color=color)
            elif t == "file":
                nid = cb.add_file_node(node_spec.get("file", ""),
                                       subpath=node_spec.get("subpath", ""),
                                       color=color)
            elif t == "link":
                nid = cb.add_link_node(node_spec.get("url", ""), color=color)
            elif t == "group":
                nid = cb.add_group_node(
                    label=node_spec.get("label", ""),
                    background=node_spec.get("background", ""),
                    background_style=node_spec.get("backgroundStyle", "cover"),
                    color=color,
                )
            else:
                nid = cb.add_text_node(str(node_spec), color=color)
            index_to_id[i] = nid
        for edge_spec in spec.get("edges", []):
            from_id = index_to_id.get(edge_spec.get("from"))
            to_id = index_to_id.get(edge_spec.get("to"))
            if from_id and to_id:
                cb.add_edge(from_id, to_id,
                            label=edge_spec.get("label", ""),
                            color=edge_spec.get("color", ""))
        return cb
