from .cli import player
import sys
from .utils import clear_console

commands = {"player": player}


def main():
    args = sys.argv
    if len(args) >= 2:
        command = args[1]
        if command in commands:
            if len(args) >= 3:
                commands[command](args[2])


if __name__ == "__main__":
    main()
