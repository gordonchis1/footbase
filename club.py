from rich_pixels import FullcellRenderer, Pixels

from utils import save_tmp_image


class Club:
    def __init__(self, club, league, joined, expires, league_level, club_img):
        self.club = club
        self.league = league
        self.joined = joined
        self.expires = expires
        self.league_level = league_level
        self.club_img = club_img

    def __repr__(self):
        return f"""
    - Club: {self.club}
    - League: {self.league}
    - Joined: {self.joined}
    - Expires: {self.expires}
    - League Level: {self.league_level}
    """

    def get_asii_img(self, local_img_path, size):
        if local_img_path:
            player_image_asii = Pixels.from_image_path(local_img_path, resize=size)
            return player_image_asii
