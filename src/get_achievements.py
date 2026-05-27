import os
from time import sleep
from test_pages.tests_index import ACHIEVEMENTS_PAGE
from constants import BASE_TRANSFERMARKT_URL
import requests
from console import console
from utils import parse_html, parse_text


def get_achievements_page(path: str) -> str:
    mode = os.getenv("MODE")

    with console.status("Loading achievements", spinner="bouncingBall"):
        if mode == "dev":
            with open(ACHIEVEMENTS_PAGE, "r") as file:
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


def parse_achievements(page: str):
    html = parse_html(page)
    achievements_container = html.find("div", "large-8 columns")
    achievements_boxs = achievements_container.find_all("div", "large-6 columns")
    achievements_titles = []

    for box in achievements_boxs:
        achievements_titles.append(
            parse_text(box.find("h2", "content-box-headline").get_text())
        )

    print(achievements_titles)
    return ""


def get_achievements(path: str):
    page = get_achievements_page(path)
    achievements = parse_achievements(page)
    return achievements


if __name__ == "__main__":
    get_achievements("/")
