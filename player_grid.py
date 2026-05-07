from rich import print
from rich.live import Live
from console import console
from rich.table import Table
import readchar

from player import PlayerPreview


class Player_grid:
    def __init__(self, players=[]):
        self.players = players
        self.selected = 0

    def selector(self, title):
        table = self.mount_table(title)
        console.print("Controls: ↑/k up  ↓/j down  Enter select", style="dim")

        with Live(table) as live:
            while True:
                live.update
                key = readchar.readkey()

                if key == readchar.key.UP or key == "k":
                    self.selected = (self.selected - 1) % len(self.players)
                    table = self.mount_table(title)
                    live.update(table)
                if key == readchar.key.DOWN or key == "j":
                    self.selected = (self.selected + 1) % len(self.players)
                    table = self.mount_table(title)
                    live.update(table)
                elif key == readchar.key.ENTER:
                    return self.selected

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
        return table

    def render(self, title="players"):
        table = self.mount_table(title)
        console.print(table)
