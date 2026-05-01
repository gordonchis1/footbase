from rich import print
from console import console
from rich.table import Table
import readchar


class Player_grid:
    def __init__(self, players=[]):
        self.players = players

    def render(self, title="Players"):
        table = Table(title=title, show_lines=True)
        table.add_column("Name", justify="center", style="cyan", no_wrap=True)
        table.add_column("Team", justify="center", style="cyan", no_wrap=True)
        table.add_column("Age", justify="center", style="cyan", no_wrap=True)
        table.add_column("Nationality", justify="center", style="cyan", no_wrap=True)
        table.add_column("Position", justify="right", style="cyan", no_wrap=True)
        table.add_column("Worth", justify="right", style="cyan", no_wrap=True)

        for player in self.players:
            table.add_row(
                player.name,
                player.team,
                player.age,
                player.nationality,
                player.position,
                player.worth,
            )

        console.print(table)
        while True:
            key = readchar.readkey()

            if key == readchar.key.UP:
                print("up")

            elif key == readchar.key.ENTER:
                break
