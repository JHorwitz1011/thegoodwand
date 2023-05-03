import os

GAMES_DIR = "~/thegoodwand/spells/"
MAIN_FUNCTION = 'main.py'

def game_exists(game_name:str) -> bool:
    """
    checks if a game exists given file structure of device
    """
    return os.path.isfile(os.path.join(os.path.expanduser(GAMES_DIR), game_name, MAIN_FUNCTION))
   
def fetch_game(game_name:str) -> str:
    """
    return filepath of game. if it doesn't exist, fetches git url from wix server. clones repo to ~/spells/
    """
    if game_exists(game_name):
        return os.path.join(os.path.expanduser(GAMES_DIR), game_name, MAIN_FUNCTION)
    else:   
        pass # download game from server

    