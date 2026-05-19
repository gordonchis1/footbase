import os
from threading import Event

import readchar
from rich.align import Align
from club import Club
from get_player import get_injury, get_player, parse_player_page
from console import console
from rich_pixels import Pixels
from rich.layout import Layout
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box, padding
from rich.table import Table
from rich.live import Live

from utils import save_tmp_image


class Player:
    def __init__(self, name, age, team, nationality, path, position, worth):
        self.name = name
        self.age = age
        self.team = team
        self.nationality = nationality
        self.path = path
        self.position = position
        self.worth = worth


class PlayerPreview(Player):
    def __init__(self, name, age, team, nationality, path, position, worth):
        super().__init__(name, age, team, nationality, path, position, worth)

    def load_full(self):
        if not self.path:
            raise ValueError("No player_url")
        player_page = get_player(self.path)
        club, player_info, player_image_url = parse_player_page(player_page)
        injury = get_injury(player_page)
        active_player = ActivePlayer(
            player_info["name"],
            club,
            player_info,
            player_image_url,
            self.worth,
            injury,
        )
        return active_player

    def __repr__(self):
        return f"""
        - Name: {self.name}
        - Age: {self.age}
        - Team: {self.team}
        - Nationality: {self.nationality}
        - Path: {self.path}
        - Position: {self.position}
        - Wroth: {self.worth}
        """


activePlayerControls = [
    {"title": "Info", "label": "info", "key": "i"},
    {"title": "Achievements", "label": "achievements", "key": "a"},
    {"title": "Stats", "label": "stats", "key": "s"},
]


class ActivePlayer:
    def __init__(
        self,
        name,
        club: Club,
        data: dict,
        player_image_url: str,
        worth,
        injury={"injury": False, "type": "", "expected_return": ""},
    ):
        self.__dict__.update(data)
        self.name = name
        self.__player_image_url = player_image_url
        self.club = club
        self.worth = worth
        self.injury = injury
        self.__tab = "info"

    def __repr__(self):
        result = ""
        for key in self.__dict__:
            if key.startswith("_"):
                continue
            if isinstance(self.__dict__[key], str):
                result += f"- **{key}**: {self.__dict__[key]} \n"
        return result

    def __get_markdown_rendered(self):
        return Markdown(self.__repr__())

    def render_player_image(self):
        local_img_path = save_tmp_image(self.__player_image_url)
        player_image_asii = ""
        if local_img_path:
            player_image_asii = Pixels.from_image_path(local_img_path, (40, 40))
        return player_image_asii, local_img_path

    def render_injury(self):
        injury_markdown = Markdown(
            f"""
# 🏥 Injury 
**{self.injury["type"]}**: {self.injury["expected_return"]}
"""
        )
        return injury_markdown

    def render_controls(self):
        controls_table = Table(
            box=box.SQUARE,
            show_header=False,
            padding=(0, 1),
            expand=True,
        )

        controls_strings = []

        for control in activePlayerControls:
            style = "black on white" if control["label"] == self.__tab else ""

            controls_table.add_column(
                justify="center",
                style=style,
                ratio=1,
            )

        for control in activePlayerControls:
            if control["label"] == self.__tab:
                controls_strings.append(
                    f"{control['title']} ([green]{control['key']}[/green])"
                )
                continue
            controls_strings.append(
                f"{control['title']} ([green]{control['key']}[/green])"
            )

        controls_table.add_row(*controls_strings)

        return controls_table

    def render_layout(self):
        player_img_tmp_path = None
        club_img_tmp_path = None
        try:
            injury_markdown = self.render_injury()
            controls_table = self.render_controls()
            player_image, player_img_tmp_path = self.render_player_image()
            club_image, club_img_tmp_path = self.club.render_club_img()

            main_layout = Layout()
            main_layout.split_row(
                Layout(name="left", size=40),
                Layout(name="right"),
            )
            main_layout["right"].split_column(
                Layout(controls_table, size=3, name="controls"),
                Layout(
                    Panel(
                        self.__get_markdown_rendered(),
                        title=self.name,
                        expand=True,
                    )
                ),
                Layout(
                    Panel(injury_markdown, box=box.ROUNDED, style="red"),
                    size=5,
                    name="injury",
                    visible=self.injury["injury"],
                ),
            )

            main_layout["left"].split_column(
                Layout(
                    player_image,
                    name="left_top",
                ),
                Layout(
                    club_image,
                    name="left_bottom",
                ),
            )

            with Live(
                Align.center(main_layout, vertical="middle"), screen=True
            ) as live:
                while True:
                    sections = list(map(lambda x: x["key"], activePlayerControls))
                    key = readchar.readkey()
                    if key in sections:
                        for idx in range(len(sections)):
                            key_section = sections[idx]
                            if key_section == key:
                                self.__tab = activePlayerControls[idx]["label"]
                        main_layout["right"]["controls"].update(self.render_controls())
                        live.update(Align.center(main_layout, vertical="middle"))

        except KeyboardInterrupt:
            if player_img_tmp_path:
                os.remove(player_img_tmp_path)
            if club_img_tmp_path:
                os.remove(club_img_tmp_path)
