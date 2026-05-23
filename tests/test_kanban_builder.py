import pytest
from obsidian_cli.kanban_builder import KanbanBuilder


def test_empty_board_has_frontmatter():
    kb = KanbanBuilder()
    md = kb.to_markdown()
    assert "kanban-plugin: basic" in md


def test_add_lane():
    kb = KanbanBuilder()
    kb.add_lane("To Do")
    md = kb.to_markdown()
    assert "## To Do" in md


def test_add_card_to_lane():
    kb = KanbanBuilder()
    kb.add_lane("To Do")
    kb.add_card("To Do", "First task")
    md = kb.to_markdown()
    assert "- [ ] First task" in md


def test_add_card_done():
    kb = KanbanBuilder()
    kb.add_lane("Done")
    kb.add_card("Done", "Finished task", done=True)
    md = kb.to_markdown()
    assert "- [x] Finished task" in md


def test_multiple_lanes():
    kb = KanbanBuilder()
    kb.add_lane("To Do")
    kb.add_lane("In Progress")
    kb.add_lane("Done")
    md = kb.to_markdown()
    assert md.index("## To Do") < md.index("## In Progress") < md.index("## Done")


def test_multiple_cards_in_lane():
    kb = KanbanBuilder()
    kb.add_lane("Backlog")
    kb.add_card("Backlog", "Task A")
    kb.add_card("Backlog", "Task B")
    md = kb.to_markdown()
    assert "Task A" in md
    assert "Task B" in md
    assert md.index("Task A") < md.index("Task B")


def test_card_to_nonexistent_lane_raises():
    kb = KanbanBuilder()
    with pytest.raises(ValueError, match="Lane 'Missing' not found"):
        kb.add_card("Missing", "orphan card")


def test_from_markdown_parse_lanes():
    md = """---
kanban-plugin: basic
---

## To Do

- [ ] Task A
- [ ] Task B

## Done

**Complete**
- [x] Task C

%% kanban:settings
{"kanban-plugin":"basic"}
%%"""
    kb = KanbanBuilder.from_markdown(md)
    assert "To Do" in kb._lanes
    assert "Done" in kb._lanes
    assert len(kb._lanes["To Do"]) == 2
    assert len(kb._lanes["Done"]) == 1


def test_from_markdown_roundtrip():
    kb = KanbanBuilder()
    kb.add_lane("To Do")
    kb.add_card("To Do", "My Task")
    md = kb.to_markdown()
    kb2 = KanbanBuilder.from_markdown(md)
    assert "To Do" in kb2._lanes
    assert any("My Task" in c["text"] for c in kb2._lanes["To Do"])
