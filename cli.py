from player import PlayerPreview
from search import search_and_select_player


def player(query):
    if not query:
        raise ValueError("No player name")
    else:
        player: PlayerPreview = search_and_select_player(query)
        player.load_full()
        return
