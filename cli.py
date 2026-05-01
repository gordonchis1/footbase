from utils import parse_html
from search import searchPlayer, players
from player_grid import Player_grid


def player(query):

    if not query:
        raise ValueError("No player name")
    else:
        text_result = searchPlayer(query)
        html = parse_html(text_result)
        players_list = players(html)
        grid = Player_grid(players_list)
        selected = grid.selector(query)
        print(players_list[selected])
        return
