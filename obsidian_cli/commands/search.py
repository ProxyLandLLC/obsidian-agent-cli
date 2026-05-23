import json
import click
from ..config import load_config
from ..transport import Transport


@click.group()
def search():
    """Search vault notes."""


@search.command()
@click.argument("query")
def simple(query):
    cfg = load_config()
    t = Transport(cfg)
    result = t.search_simple(query)
    click.echo(json.dumps(result))


@search.command()
@click.argument("dql")
def advanced(dql):
    cfg = load_config()
    t = Transport(cfg)
    result = t.search_advanced(dql, "application/vnd.olrapi.dataview.dql+txt")
    click.echo(json.dumps(result))


@search.command()
@click.argument("expr")
def jsonlogic(expr):
    cfg = load_config()
    t = Transport(cfg)
    result = t.search_advanced(expr, "application/vnd.olrapi.jsonlogic+json")
    click.echo(json.dumps(result))


@search.command()
def tags():
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_tags()
    click.echo(json.dumps(result))
