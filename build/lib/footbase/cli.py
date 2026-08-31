from .player import PlayerPreview
from .search import search_and_select_player
import click


@click.group()
def cli():
    pass


@click.command()
@click.argument("name")
def search(name):
    """
    Search for a player by NAME and display information about the player.
    """
    if not name:
        raise ValueError("No player name")
    else:
        player_preview: PlayerPreview = search_and_select_player(name)
        player = player_preview.load_full()
        player.render_layout()
        return


cli.add_command(search)
