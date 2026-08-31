import os

from .get_achievements import get_achievements
from .get_competitions import Competition, get_competitions
from .get_stats import Stats, get_stats
from .log import write_log
import readchar
from rich.align import Align
from .club import Club
from .get_player import get_injury, get_player, parse_player_page
from rich_pixels import Pixels
from rich.layout import Layout
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from rich.table import Table
from rich.live import Live

from .console import console
from .utils import save_tmp_image


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

    def render_stats(self, main_layout: Layout):
        main_layout["right"].add_split(
            Layout(
                Panel(f"Loading {self.name} stats...", title=self.name),
                name="stats",
            ),
        )

        stats = Stats(self.__id)
        competitions = get_competitions(stats.competitions_ids)
        table = Table(
            collapse_padding=True,
            pad_edge=False,
            expand=True,
            show_edge=True,
            show_lines=True,
        )
        table.add_column("League", justify="left")
        table.add_column("Goals", justify="center")
        table.add_column("Assists", justify="center")
        table.add_column("Minutes", justify="center")
        table.add_column("Appearences", justify="center")

        for competition in competitions:
            if competition is None:
                continue
            competition_stats = stats.competitions_stats[competition.id]
            table.add_row(
                competition.name,
                f"{competition_stats['total_goals']}",
                f"{competition_stats['total_assists']}",
                f"{competition_stats['minutes_played']}",
                f"{competition_stats['appearences']}",
            )

        main_layout["right"]["stats"].update(Panel(table, padding=(0, 0)))

        write_log(
            f"Total goals: {stats.get_total_goals()}, Total assists: {stats.get_total_assists()}"
        )
        get_competitions(stats.competitions_ids)

    def render_achievements(self, main_layout: Layout):
        main_layout["right"].add_split(
            Layout(
                Panel(f"Loading {self.name} achievements...", title=self.name),
                name="achievements",
            ),
        )
        achievements = get_achievements(self.__get_achievements_path())
        panel = Panel("", title=self.name, expand=True)
        layout_render_lines = console.render_lines(
            main_layout["right"]["achievements"], options=console.options
        )
        height = len(layout_render_lines) - 8
        markdown_achievements = []

        for achievement in achievements:
            current_markdown_achievement = f"## {achievement['name']}"
            for time in achievement["times"]:
                current_markdown_achievement += f"\n- {time}"
            markdown_achievements.append(current_markdown_achievement)

        def generate_page(achievements_markdown_list):
            to_render_lines = 0
            idx = 0
            markdown_achievements_raw_tmp = ""

            while height > to_render_lines and len(markdown_achievements) > idx:
                markdown_achievements_raw_tmp += (
                    "\n" + markdown_achievements[idx] + "\n"
                )
                markdown_achievement = Markdown(markdown_achievements_raw_tmp)
                to_render_lines = len(
                    console.render_lines(markdown_achievement, options=console.options)
                )
                if to_render_lines > height:
                    break
                idx += 1
            write_log(
                f"Rendered_achievements: {idx}, total_achievements: {len(achievements_markdown_list)}"
            )
            return achievements_markdown_list[:idx], achievements_markdown_list[idx:]

        def generate_pages(achievements_markdown_list):
            pages = []
            if len(achievements_markdown_list) == 0:
                return pages

            page, rest = generate_page(achievements_markdown_list)
            pages = generate_pages(rest)
            pages.insert(0, page)
            return pages

        pages = generate_pages(markdown_achievements)
        currrent_page_idx = 0
        final_markdown_raw = "\n".join(
            [
                *pages[currrent_page_idx],
                f"\n **{currrent_page_idx + 1}/{len(pages)}** | Use: j/↓ go down or k/↑",
            ]
        )
        final_markdown = Markdown(final_markdown_raw)
        panel.renderable = final_markdown
        main_layout["right"]["achievements"].update(panel)

        while True:
            key = readchar.readkey()
            if key == "j" or key == readchar.key.UP:
                if currrent_page_idx == len(pages) - 1:
                    currrent_page_idx = 0
                else:
                    currrent_page_idx += 1
            if key == "k" or key == readchar.key.DOWN:
                if currrent_page_idx != 0:
                    currrent_page_idx -= 1
                else:
                    currrent_page_idx = len(pages) - 1

            final_markdown_raw = "\n".join(
                [
                    *pages[currrent_page_idx],
                    f"\n **{currrent_page_idx + 1}/{len(pages)}** | Use: j/↓ go down or k/↑",
                ]
            )

            asigned_keys = list(
                map(lambda control: self.controls[control]["key"], self.controls)
            )
            final_markdown = Markdown(final_markdown_raw)
            panel.renderable = final_markdown
            main_layout["right"]["achievements"].update(panel)

            if key in asigned_keys:
                for control in self.controls:
                    if self.controls[control]["key"] == key:
                        self.__change_tab(self.controls[control]["label"])
                        self.__update_rendered(main_layout)
                break

    def __change_tab(self, tab):
        self.__tab = tab

    def __update_rendered(self, main_layout):
        controls_layout = self.render_controls()
        main_layout["right"].unsplit()
        main_layout["right"].split_column(controls_layout)
        self.controls[self.__tab]["render"](main_layout)

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

        return Layout(controls_table, size=3, name="controls")

    def render_layout(self):
        player_img_tmp_path = None
        club_img_tmp_path = None
        try:
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
            controls_layout = self.render_controls()

            main_layout["right"].split_column(controls_layout)
            self.controls[self.__tab]["render"](main_layout)

            with Live(
                Align.center(main_layout, vertical="middle"),
                screen=True,
                console=console,
            ):
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
                                self.__change_tab(self.controls[control]["label"])
                        controls_layout = self.render_controls()
                        self.__update_rendered(main_layout)
        except KeyboardInterrupt:
            if player_img_tmp_path:
                os.remove(player_img_tmp_path)
            if club_img_tmp_path:
                os.remove(club_img_tmp_path)
