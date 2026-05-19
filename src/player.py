import os
from threading import Event

from rich.align import Align
from club import Club
from get_player import get_injury, get_player, parse_player_page
from console import console
from rich_pixels import Pixels
from rich.layout import Layout
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from rich.columns import Columns
from rich.table import Table

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

    def render_layout(self):
        local_img_path = save_tmp_image(self.__player_image_url)
        local_club_path = save_tmp_image(self.club.club_img)
        club_img_asii = self.club.get_asii_img(local_club_path, (40, 40))
        try:
            with console.screen() as screen:
                player_image_asii = ""
                if local_img_path:
                    player_image_asii = Pixels.from_image_path(local_img_path, (40, 40))

                main_layout = Layout()

                main_layout.split_row(
                    Layout(name="left", size=40),
                    Layout(name="right"),
                )

                injury_markdown = Markdown(
                    f"""
# 🏥 Injury 
**{self.injury["type"]}**: {self.injury["expected_return"]}
"""
                )

                controls_table = Table(
                    box=box.SQUARE,
                    show_header=False,
                    padding=(0, 1),
                    expand=True,
                )

                controls_table.add_column(justify="center")
                controls_table.add_column(justify="center")

                controls_table.add_row(
                    "Info ([green]I[/green])",
                    "Achievements ([green]A[/green])",
                )

                main_layout["right"].split_column(
                    Layout(controls_table, size=3),
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
                        player_image_asii,
                        name="left_top",
                    ),
                    Layout(
                        club_img_asii,
                        name="left_bottom",
                    ),
                )

                screen.update(Align.center(main_layout, vertical="middle"))
                Event().wait()
        except KeyboardInterrupt:
            if local_img_path:
                os.remove(local_img_path)
            if local_club_path:
                os.remove(local_club_path)
