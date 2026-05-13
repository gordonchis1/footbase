from player import PlayerPreview
from search import search_and_select_player


def player(query):
    if not query:
        raise ValueError("No player name")
    else:
        player_preview: PlayerPreview = search_and_select_player(query)
        player = player_preview.load_full()
        player.render()
        return
