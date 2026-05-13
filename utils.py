from bs4 import BeautifulSoup
import os
import subprocess
import requests
import tempfile


def clear_console():
    # Use 'cls' for Windows (nt) and 'clear' for Linux/macOS (posix)
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True)


def parse_html(text):
    html = BeautifulSoup(text, "html.parser")

    return html


def parse_text(text):
    return " ".join(text.strip().split())


def save_tmp_image(url):
    if not url:
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        response = requests.get(url)
        response.raise_for_status()
        temp.write(response.content)
        local_img_path = temp.name
        return local_img_path
