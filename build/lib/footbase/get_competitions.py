from .constants import COMPETITIONS_TRANSFERMARKT_URL
import os
import json
from .test_pages.tests_index import COMPETITIONS_JSON
import requests


class Competition:
    def __init__(self, name, id) -> None:
        self.name = name
        self.id = id

    def __repr__(self) -> str:
        return f"Name: {self.name}, Id: {self.id}"


def create_competitions(competitions_json) -> list[Competition]:
    competitions = []
    for competition in competitions_json:
        new_competition = Competition(name=competition["name"], id=competition["id"])
        competitions.append(new_competition)

    return competitions


def get_competitions(ids: list[str]) -> list[Competition]:
    # https://tmapi-alpha.transfermarkt.technology/competitions?ids[]=CDR
    url = f"{COMPETITIONS_TRANSFERMARKT_URL}?"

    for id in ids:
        url += f"ids[]={id}&"

    mode = os.getenv("MODE")

    if mode == "dev":
        with open(COMPETITIONS_JSON, "r") as file:
            text = file.read()
            competitions_json = json.loads(text)
            competitions = create_competitions(competitions_json["data"])
            return competitions

    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0",
    }
    response = requests.get(url, headers=headers)
    competitions_json = response.json()
    if competitions_json["success"]:
        return create_competitions(competitions_json["data"])
    else:
        raise Exception("Fail getting competitions")
