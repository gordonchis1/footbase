import os

from console import Console
from get_achievements import get_achievements
from log import write_log
import readchar
from rich.align import Align
from club import Club
from get_player import get_injury, get_player, parse_player_page
from rich_pixels import Pixels
from rich.layout import Layout
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from rich.table import Table
from rich.live import Live

from console import console
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
        self.__id = self.generate_id()
        self.__path_name = self.generate_path_name()

    def generate_path_name(self):
        path = self.path
        splited_path = path.split("/")
        result = splited_path[1]
        return result

    def generate_id(self):
        path = self.path
        splited_path = path.split("/")
        result = splited_path[-1]

        return result

    def load_full(self):
        if not self.path:
            raise ValueError("No player_url")
        player_page = get_player(self.path)
        club, player_info, player_image_url = parse_player_page(player_page)
        injury = get_injury(player_page)
        # player_info["achievements_path"],
        active_player = ActivePlayer(
            player_info["name"],
            club,
            player_info,
            player_image_url,
            self.worth,
            self.__id,
            self.__path_name,
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
    @property
    def controls(self):
        return {
            "info": {
                "title": "Info",
                "label": "info",
                "key": "i",
                "render": self.render_info,
            },
            "stats": {
                "title": "Stats",
                "label": "stats",
                "key": "s",
                "render": self.render_stats,
            },
            "achievements": {
                "title": "Achievements",
                "label": "achievements",
                "key": "a",
                "render": self.render_achievements,
            },
        }

    def __init__(
        self,
        name: str,
        club: Club,
        data: dict,
        player_image_url: str,
        worth: str,
        id: str,
        path_name: str,
        injury: dict = {"injury": False, "type": "", "expected_return": ""},
    ):
        self.__dict__.update(data)
        self.name = name
        self.club = club
        self.worth = worth
        self.injury = injury
        self.__tab = "info"
        self.__player_image_url = player_image_url
        self.__path_name = path_name
        self.__id = id

    def __get_achievements_path(self) -> str:
        # /<path_name>/logros/jugadores/spieler/<id>
        return f"/{self.__path_name}/erfolge/spieler/{self.__id}"

    def render_achievements(self, main_layout: Layout):
        main_layout["right"].add_split(
            Layout(
                Panel(f"Loading {self.name} achievements...", title=self.name),
                name="achievements",
            ),
        )
        achievements = get_achievements(self.__get_achievements_path())
        console_test = Console()
        panel = Panel("", title=self.name, expand=True)
        achievements_layout = main_layout["right"]["achievements"]
        render_map = achievements_layout.render(console, console.options)
        height = render_map[achievements_layout].region.height
        lines = console.render_lines(achievements_layout, options=console.options)
        last_full_heading = ""

        markdown_achievements = ""
        raw_markdown_achievements = ""
        raw_markdown_achievements_tmp = ""

        for idx in range(len(achievements)):
            raw_markdown_achievements_tmp = raw_markdown_achievements
            achievement = achievements[idx]
            raw_markdown_achievements += f"## {achievement['name']} \n"
            for time in achievement["times"]:
                raw_markdown_achievements += f"- {time} \n"
            markdown_achievements = Markdown(raw_markdown_achievements)
            lines = console_test.render_lines(markdown_achievements)
            if len(lines) > height - 3:
                raw_markdown_achievements_tmp += "\n **page 1**"
                break
            raw_markdown_achievements_tmp = raw_markdown_achievements
            last_full_heading = achievement["name"]

        write_log(f"last heading {last_full_heading}")
        write_log(raw_markdown_achievements_tmp)
        markdown_achievements = Markdown(raw_markdown_achievements_tmp)
        panel.renderable = markdown_achievements
        main_layout["right"]["achievements"].update(panel)

    def render_stats(self, main_layout):
        return [Layout()]

    def render_info(self, main_layout: Layout) -> None:
        injury_markdown = self.render_injury()
        main_layout["right"].add_split(
            Layout(
                Panel(
                    self.__get_markdown_rendered(),
                    title=self.name,
                    expand=True,
                ),
                name="info",
            ),
            Layout(
                Panel(injury_markdown, box=box.ROUNDED, style="red"),
                size=5,
                name="injury",
                visible=self.injury["injury"],
            ),
        )

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

        for control in self.controls:
            style = "black on white" if control == self.__tab else ""

            controls_table.add_column(
                justify="center",
                style=style,
                ratio=1,
            )

        for control in self.controls:
            if control == self.__tab:
                controls_strings.append(
                    f"{self.controls[control]['title']} ([green]{self.controls[control]['key']}[/green])"
                )
                continue
            controls_strings.append(
                f"{self.controls[control]['title']} ([green]{self.controls[control]['key']}[/green])"
            )

        controls_table.add_row(*controls_strings)

        return controls_table

    def render_layout(self):
        player_img_tmp_path = None
        club_img_tmp_path = None
        try:
            controls_table = self.render_controls()
            player_image, player_img_tmp_path = self.render_player_image()
            club_image, club_img_tmp_path = self.club.render_club_img()

            main_layout = Layout()
            main_layout.split_row(
                Layout(name="left", size=40),
                Layout(name="right"),
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
            controls_layout = Layout(controls_table, size=3, name="controls")

            main_layout["right"].split_column(controls_layout)
            self.controls[self.__tab]["render"](main_layout)

            with Live(
                Align.center(main_layout, vertical="middle"),
                screen=True,
                console=console,
            ) as live:
                while True:
                    asigned_keys = list(
                        map(
                            lambda control: self.controls[control]["key"], self.controls
                        )
                    )
                    key = readchar.readkey().lower()
                    if key in asigned_keys:
                        for control in self.controls:
                            if self.controls[control]["key"] == key:
                                self.__tab = self.controls[control]["label"]
                        controls_table = self.render_controls()
                        controls_layout = Layout(
                            controls_table, size=3, name="controls"
                        )
                        main_layout["right"].unsplit()
                        main_layout["right"].split_column(controls_layout)
                        self.controls[self.__tab]["render"](main_layout)
                        live.update(Align.center(main_layout, vertical="middle"))

        except KeyboardInterrupt:
            if player_img_tmp_path:
                os.remove(player_img_tmp_path)
            if club_img_tmp_path:
                os.remove(club_img_tmp_path)
