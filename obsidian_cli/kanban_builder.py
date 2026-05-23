import re


class KanbanBuilder:
    def __init__(self):
        self._lane_order: list[str] = []
        self._lanes: dict[str, list[dict]] = {}

    def add_lane(self, name: str) -> None:
        if name not in self._lanes:
            self._lane_order.append(name)
            self._lanes[name] = []

    def add_card(self, lane: str, text: str, done: bool = False) -> None:
        if lane not in self._lanes:
            raise ValueError(f"Lane '{lane}' not found. Call add_lane first.")
        self._lanes[lane].append({"text": text, "done": done})

    def to_markdown(self) -> str:
        lines = ["---", "kanban-plugin: basic", "---", ""]
        for lane in self._lane_order:
            lines.append(f"## {lane}")
            lines.append("")
            done_cards = [c for c in self._lanes[lane] if c["done"]]
            todo_cards = [c for c in self._lanes[lane] if not c["done"]]
            for card in todo_cards:
                lines.append(f"- [ ] {card['text']}")
            if done_cards:
                lines.append("")
                lines.append("**Complete**")
                for card in done_cards:
                    lines.append(f"- [x] {card['text']}")
            lines.append("")
        lines += [
            '%% kanban:settings',
            '{"kanban-plugin":"basic"}',
            '%%',
        ]
        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, markdown: str) -> "KanbanBuilder":
        kb = cls()
        current_lane: str | None = None
        for line in markdown.splitlines():
            heading = re.match(r"^## (.+)$", line)
            if heading:
                current_lane = heading.group(1).strip()
                kb.add_lane(current_lane)
                continue
            if current_lane is None:
                continue
            todo = re.match(r"^- \[ \] (.+)$", line)
            if todo:
                kb.add_card(current_lane, todo.group(1).strip(), done=False)
                continue
            done = re.match(r"^- \[x\] (.+)$", line, re.IGNORECASE)
            if done:
                kb.add_card(current_lane, done.group(1).strip(), done=True)
        return kb
