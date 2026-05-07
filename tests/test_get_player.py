import unittest
from test_pages.tests_index import PLAYER_PAGE


class TestGetPlayer(unittest.TestCase):
    def test_active_player(self):
        with open(PLAYER_PAGE, "r") as file:
            html = file.read()


if __name__ == "__main__":
    unittest.main()
