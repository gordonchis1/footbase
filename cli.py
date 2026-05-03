from get_player import get_player
from utils import parse_html
from search import search_and_select_player, searchPlayer, players
from player_grid import Player_grid


def player(query):
    if not query:
        raise ValueError("No player name")
    else:
        player = search_and_select_player(query)
        path = player.player_url
        return
