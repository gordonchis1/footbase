import os
import requests
from .constants import BASE_TRANSFERMARKT_SEARCH_URL
from .player import PlayerPreview
from .test_pages.tests_index import SEARCH_PAGE
from .utils import parse_text
from .console import console
from time import sleep
from .utils import parse_html
from .player_grid import Player_grid


def searchPlayer(query):
    mode = os.getenv("MODE")

    with console.status(f"Loading player: {query}", spinner="bouncingBall"):
        if mode == "dev":
            with open(SEARCH_PAGE, "r") as file:
                sleep(1)
                return file.read()
        try:
            params = {"query": query}
            headers = {
                "User-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0"
            }
            search_result = requests.get(
                BASE_TRANSFERMARKT_SEARCH_URL, params=params, headers=headers
            )
            return search_result.text
        except Exception as error:
            raise Exception(error)


def parse_player_info_table(table):
    [img, name, team] = table.find_all("td")

    player_info = {
        "player_img": img.find("img").get("src"),
        "name": parse_text(name.get_text()),
        "team": parse_text(team.get_text()),
        "url": name.a.get("href"),
    }
    return player_info


def players(html):
    players_list = []
    grids = html.find_all("div", id="player-grid")
    tables = []
    bodys = []
    for grid in grids:
        tables.append(grid.table)

    for table in tables:
        bodys.append(table.tbody)

    for body in bodys:
        for player_table in body.find_all("tr", recursive=False):
            player_tr = player_table.find_all("td", recursive=False)
            player_info_table = player_tr[0].find_all("table", recursive=False)[0]
            player_info = parse_player_info_table(player_info_table)

            position = player_tr[1].get_text()
            age = player_tr[3].get_text()
            nationality = player_tr[4].find("img").get("alt")
            worth = player_tr[5].get_text()
            player = PlayerPreview(
                player_info["name"],
                age,
                player_info["team"],
                nationality,
                player_info["url"],
                position,
                worth,
            )
            players_list.append(player)

    return players_list


def search_and_select_player(query):
    text_result = searchPlayer(query)
    html = parse_html(text_result)
    players_list = players(html)
    grid = Player_grid(players_list)
    selected = grid.selector(query)
    player = players_list[selected]
    return player
