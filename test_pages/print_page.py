import requests
import sys

args = sys.argv


if len(args) < 2:
    exit()
headers = {
    "User-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0"
}
page = requests.get(args[1], headers=headers)
print(page.text)
