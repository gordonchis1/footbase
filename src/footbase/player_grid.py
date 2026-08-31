from rich import print
from rich import align
from rich.align import Align
from rich.console import Group
from rich.live import Live
from .console import console
from rich.table import Table
import readchar

from .player import PlayerPreview
from rich.text import Text


class Player_grid:
    def __init__(self, players=[]):
        self.players = players
        self.selected = 0

    def selector(self, title):
        table = self.mount_table(title)
        controls = Text.from_markup(
            "[dim]Controls:[/dim] [green]↑/k[/green] [dim]up[/dim] [green]↓/j[/green] [dim]down[/dim] [green]Enter[/green] [dim]select[/dim]",
            justify="center",
        )
        layout = Group(table, controls)

        with Live(layout, screen=True, console=console) as live:
            while True:
                key = readchar.readkey()
                if key == readchar.key.UP or key == "k":
                    self.selected = (self.selected - 1) % len(self.players)
                if key == readchar.key.DOWN or key == "j":
                    self.selected = (self.selected + 1) % len(self.players)
                elif key == readchar.key.ENTER:
                    console.clear()
                    return self.selected

                table = self.mount_table(title)
                layout = Group(table, controls)
                live.update(layout)

    def mount_table(self, title="Players"):
        table = Table(title=title, show_lines=True)
        table.add_column("Name", justify="center", style="green bold", no_wrap=True)
        table.add_column("Team", justify="center", style="cyan", no_wrap=True)
        table.add_column("Age", justify="center", style="cyan", no_wrap=True)
        table.add_column("Nationality", justify="center", style="cyan", no_wrap=True)
        table.add_column("Position", justify="right", style="cyan", no_wrap=True)
        table.add_column("Worth", justify="right", style="cyan", no_wrap=True)

        for idx in range(len(self.players)):
            player: PlayerPreview = self.players[idx]
            style = ""
            if self.selected == idx:
                style = "on green bold white"
            table.add_row(
                player.name,
                player.team,
                player.age,
                player.nationality,
                player.position,
                player.worth,
                style=style,
            )
        return Align.center(table)

    def render(self, title="players"):
        table = self.mount_table(title)
        console.print(table)
