from log import write_log
import requests
from constants import STATS_TRANSFERMARKT_URL
from test_pages.tests_index import STATS_JSON
import os
import json
import copy


def get_stats(id: str):
    mode = os.getenv("MODE")

    if mode == "dev":
        with open(STATS_JSON, "r") as file:
            text = file.read()
            stats_json = json.loads(text)
            return stats_json["data"]

    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0",
    }

    url = STATS_TRANSFERMARKT_URL.replace("{id}", id)
    response = requests.get(url, headers=headers)
    stats_json = response.json()
    if stats_json["success"]:
        return stats_json["data"]
    else:
        raise Exception("Fail getting stats")


default_goal_stats = {
    "total_goals": 0,
    "total_assists": 0,
    "appearences": 0,
    "minutes_played": 0,
    "yellow_cards": 0,
    "red_cards": 0,
    "second_yellow_card": 0,
    "competitionTypeId": 0,
}


class Stats:
    def __init__(self, id) -> None:
        stats = get_stats(id)
        if stats is not None:
            competitions_ids = stats["competitionIds"]
            performance_data = stats["performance"]
            self.competitions_ids = competitions_ids
            self.competitions_stats = {}
            for competition in competitions_ids:
                self.competitions_stats[competition] = copy.deepcopy(default_goal_stats)
            clubs_ids = []
            clubs_stats = {}
            total_goals = 0
            for game in performance_data:
                game_information = game["gameInformation"]
                game_stats = game["statistics"]
                clubs_information = game["clubsInformation"]
                club = clubs_information["club"]
                assists = game_stats["goalStatistics"]["assists"]
                goals = game_stats["goalStatistics"]["goalsScoredTotal"]
                general_statistics = game_stats["generalStatistics"]
                played_time_statistics = game_stats["playingTimeStatistics"]
                cards_statistics = game_stats["cardStatistics"]

                club_id = club["clubId"]
                competition_id = game_information["competitionId"]
                if game_information["competitionTypeId"] is not None:
                    self.competitions_stats[competition_id]["competitionTypeId"] = (
                        game_information["competitionTypeId"]
                    )

                if club_id not in clubs_ids:
                    clubs_ids.append(club_id)
                if club_id not in clubs_stats:
                    clubs_stats[club_id] = copy.deepcopy(default_goal_stats)

                if goals is not None:
                    total_goals += goals
                    self.competitions_stats[competition_id]["total_goals"] += goals
                    clubs_stats[club_id]["total_goals"] += goals
                if assists is not None:
                    self.competitions_stats[competition_id]["total_assists"] += assists
                    clubs_stats[club_id]["total_assists"] += assists
                if general_statistics["participationState"] == "played":
                    clubs_stats[club_id]["appearences"] += 1
                    self.competitions_stats[competition_id]["appearences"] += 1
                if played_time_statistics["playedMinutes"] is not None:
                    clubs_stats[club_id]["minutes_played"] += played_time_statistics[
                        "playedMinutes"
                    ]

                    self.competitions_stats[competition_id]["minutes_played"] += (
                        played_time_statistics["playedMinutes"]
                    )
                if cards_statistics["yellowCardNet"] is not None:
                    self.competitions_stats[competition_id]["yellow_cards"] += (
                        cards_statistics["yellowCardNet"]
                    )
                    clubs_stats[club_id]["yellow_cards"] += cards_statistics[
                        "yellowCardNet"
                    ]
                if "redCard" in cards_statistics:
                    self.competitions_stats[competition_id]["red_cards"] += 1
                    clubs_stats[club_id]["red_cards"] += 1
                if "yellowRedCard" in cards_statistics:
                    self.competitions_stats[competition_id]["second_yellow_card"] += 1
                    clubs_stats[club_id]["second_yellow_card"] += 1

            self.clubs_ids = clubs_ids
            self.clubs_stats = clubs_stats
            write_log(f"Total goals from init: {total_goals}")

    def get_total_goals(self):
        sum = 0
        for stats in self.competitions_stats:
            if (
                self.competitions_stats[stats]["competitionTypeId"] != 17
                and self.competitions_stats[stats]["competitionTypeId"] != 16
                and self.competitions_stats[stats]["competitionTypeId"] != 12
                and self.competitions_stats[stats]["competitionTypeId"] != 20
            ):
                sum += self.competitions_stats[stats]["total_goals"]
        return sum

    def get_total_assists(self):
        sum = 0
        for stats in self.competitions_stats:
            if (
                self.competitions_stats[stats]["competitionTypeId"] != 17
                and self.competitions_stats[stats]["competitionTypeId"] != 16
                and self.competitions_stats[stats]["competitionTypeId"] != 12
                and self.competitions_stats[stats]["competitionTypeId"] != 20
            ):
                sum += self.competitions_stats[stats]["total_assists"]
        return sum
