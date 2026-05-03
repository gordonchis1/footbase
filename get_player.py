import os
from console import console
from time import sleep
from constants import BASE_TRANSFERMARKT_SEARCH_URL
from test_pages.tests_index import PLAYER_PAGE
import requests


def get_player(path):
    mode = os.getenv("MODE")

    with console.status(f"Loading player: {path}", spinner="bouncingBall"):
        if mode == "dev":
            with open(PLAYER_PAGE, "r") as file:
                sleep(1)
                return file.read()
        try:
            headers = {
                "User-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0"
            }
            search_result = requests.get(
                f"{BASE_TRANSFERMARKT_SEARCH_URL}{path}", headers=headers
            )
            return search_result.text
        except Exception as error:
            raise Exception(error)
