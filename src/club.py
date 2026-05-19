from rich_pixels import Pixels

from utils import save_tmp_image


class Club:
    def __init__(self, club, league, joined, expires, league_level, club_img):
        self.club = club
        self.league = league
        self.joined = joined
        self.expires = expires
        self.league_level = league_level
        self.__club_img = club_img

    def __repr__(self):
        return f"""
    - Club: {self.club}
    - League: {self.league}
    - Joined: {self.joined}
    - Expires: {self.expires}
    - League Level: {self.league_level}
    """

    def render_club_img(self):
        local_img_path = save_tmp_image(self.__club_img)
        club_image_asii = None
        if local_img_path:
            club_image_asii = Pixels.from_image_path(local_img_path, (40, 40))
        return club_image_asii, local_img_path
