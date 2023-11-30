class TitrePasDansBD(Exception):
    def __init__(self):
        self.message = "L'ID du titre n'est pas dans la BD à l'URL : 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/fr_fr/v1/challenges.json'"