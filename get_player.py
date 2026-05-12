import os
from time import sleep

import requests

from console import console
from constants import BASE_TRANSFERMARKT_URL
from test_pages.tests_index import PLAYER_PAGE
from utils import parse_html, parse_text
from club import Club


def get_player(path):
    mode = os.getenv("MODE")

    with console.status(f"Loading player: {path}", spinner="bouncingBall"):
        if mode == "dev":
            with open(PLAYER_PAGE, "r") as file:
                sleep(1)
                return file.read()
        try:
            headers = {
                "User-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0",
            }
            url = f"{BASE_TRANSFERMARKT_URL}{path}"
            search_result = requests.get(url, headers=headers)
            return search_result.text
        except Exception as error:
            raise Exception(error)


def parse_player_page(player_page):
    console.clear()
    html = parse_html(player_page)
    html_club_info = html.find("div", "data-header__box--big")
    club = parse_text(html.find("span", "data-header__club").get_text())
    league = html.find("span", "data-header__league")

    if club != "Retired":
        if league:
            league = parse_text(league.get_text())
        league_level, joined, expires = html_club_info.find_all(
            "span", "data-header__label"
        )
        league_level = parse_text(league_level.get_text().split(":", 1)[1])
        joined = parse_text(joined.get_text().split(":", 1)[1])
        club_img = (
            html_club_info.find("a", "data-header__box__club-link")
            .find("img")
            .get("srcset")
        )
        expires = parse_text(expires.get_text().split(":", 1)[1])

        player_info = html.find("div", "info-table--right-space")
        info_values_html = player_info.find_all("span", "info-table__content--bold")
        info_keys_html = player_info.find_all("span", "info-table__content--regular")

        info_keys = list(map(lambda el: parse_text(el.get_text())[:-1], info_keys_html))
        info_values = list(map(lambda el: parse_text(el.get_text()), info_values_html))

        player_image_url = html.find("img", "data-header__profile-image").get("src")
        info_obj = {}
        for idx in range(len(info_keys)):
            key = info_keys[idx]
            value = info_values[idx]
            if len(value) == 0:
                continue
            if "/" in key:
                key = key.split("/")[0]
            info_obj[key] = value
        info_obj["name"] = parse_text(
            html.find("h1", "data-header__headline-wrapper").get_text()
        )

        club_info = Club(club, league, joined, expires, league_level, club_img)

        return club_info, info_obj, player_image_url
    return None
