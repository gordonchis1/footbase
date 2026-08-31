from pathlib import Path
from datetime import datetime
import os


def write_log(message: any):
    cwd = Path.cwd()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = f"{cwd}/logs.txt"
    exists = os.path.exists(path)

    if not exists:
        with open(path, "x") as f:
            f.close()

    with open(path, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")
