from bs4 import BeautifulSoup
import os
import subprocess


def clear_console():
    # Use 'cls' for Windows (nt) and 'clear' for Linux/macOS (posix)
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True)


def parse_html(text):
    html = BeautifulSoup(text, "html.parser")

    return html


def parse_text(text):
    return " ".join(text.strip().split())
