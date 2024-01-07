import math
import random
from pathlib import Path
from exceptions import *
from app import app
from flask import flash, render_template, redirect, url_for, send_file, jsonify
from flask import request,redirect, url_for
from wtforms import StringField , HiddenField, DateField , RadioField, PasswordField,SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from PIL import Image, ImageDraw, ImageFont
import requests
import os, signal
import json
riot_key = "RGAPI-5d59be91-f9a6-436d-af4c-903137306949"
rang_trad = {
    "UNRANKED": "Non classé",
    "IRON": "Fer",
    "BRONZE": "Bronze",
    "SILVER": "Argent",
    "GOLD": "Or",
    "PLATINUM": "Platine",
    "EMERALD": "Émeraude",
    "DIAMOND": "Diamant",
    "MASTER": "Maître",
    "GRANDMASTER": "Grand Maître",
    "CHALLENGER": "Challenger"
}

version = None

class RiotForm(FlaskForm):
    pseudo=StringField('pseudo',validators=[DataRequired()])
    tag=StringField('tag',validators=[DataRequired()])
    next = HiddenField()

    def est_valide(self):
        player = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self.pseudo.data}/{self.tag.data}?api_key={riot_key}").json()
        return player.get("puuid","") != ""

@app.route("/", methods=("GET", "POST"))
def home():
    update_version()
    f = RiotForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    if f.validate_on_submit():
        valide = f.est_valide()
        if valide:
            return redirect(url_for("cree_image",name=f.pseudo.data,tag=f.tag.data))
    if(not riot_key.startswith("RGAPI")):
        return render_template(
            "404.html",
            image=random_image("/home/livreur/League-Card-Generator/static/images/404/")
        )
    return render_template(
        "home.html",
        form=f,
        background=random_image("/home/livreur/League-Card-Generator/static/images/background/")
    )

@app.route("/shutdown", methods=['GET'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({ "success": True, "message": "Server is shutting down..." })

@app.route('/images/<name>/<tag>.png')
def cree_image(name:str,tag:str) -> Image:
    riot,summoner,challenges = get_data(name,tag)

    user_image =  generate_image(riot,summoner,challenges)

    image_path = f"/home/livreur/League-Card-Generator/static/league/{riot['gameName']}#{riot['tagLine']}.png"
    user_image.save(f"{image_path}")

    return send_file(image_path,mimetype='image/png')

def get_data(name:str,tag:str):
    riot_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={riot_key}"
    riot_data = requests.get(riot_url).json()

    summoner_url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{riot_data['puuid']}?api_key={riot_key}"
    summoner_data = requests.get(summoner_url).json()

    challenges_url = f"https://euw1.api.riotgames.com/lol/challenges/v1/player-data/{riot_data['puuid']}?api_key={riot_key}"
    challenges_data = requests.get(challenges_url).json()

    return riot_data,summoner_data,challenges_data

def get_titre(id_titre) -> str:
    if id_titre == "":
        return ""

    titres = json.load(open("/home/livreur/League-Card-Generator/static/league/data/challenges.json"))["titles"]
    for t in titres.values():
        if t['itemId'] == int(id_titre):
            return t['name']
    raise TitrePasDansBD()

def get_rang(id_joueur:int) -> str:
    classes = requests.get(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{id_joueur}?api_key={riot_key}").json()
    for c in classes:
        if c['queueType'] == "RANKED_SOLO_5x5":
            return f"{rang_trad[c['tier']]} {c['rank']} ({c['leaguePoints']} PL)"
    return "Non classé"

def round_image(image:Image) -> Image:
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.width, image.height), fill=255)
    result = Image.new("RGBA", image.size, (255,255,255,0))
    result.paste(image,mask=mask)
    return result

def get_champions(puuid_joueur:int, limit:int=3) -> list[Image.Image]:
    champions = requests.get(f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid_joueur}?api_key={riot_key}").json()[:limit]
    result = []

    for c in champions:
        
        lien = get_name_from_id(c['championId'])
        image_champ = round_image(Image.open(requests.get(lien, stream=True).raw).resize((105,105)))

        lien = f"/home/livreur/League-Card-Generator/static/league/mastery/mastery{c['championLevel']}.png"
        image_maitrise = Image.open(lien)

        image_maitrise.paste(image_champ,(7,13),image_champ)

        image_maitrise = image_maitrise.resize((96,160))

        result.append(image_maitrise)
    return result

def generate_gradient(colour1: str, colour2: str, width: int, height: int) -> Image:
    left = Image.new('RGB', (width, height), colour1)
    right = Image.new('RGB', (width, height), colour2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for x in range(width):
        mask_data.append(int(255 * (x / width)))
    mask_data.extend(mask_data*(height-1))
    mask.putdata(mask_data)
    left.paste(right, (0, 0), mask)
    return left

def generate_image(riot_data:dict,summoner_data:dict,challenges_data:dict) -> Image:
    update_version()

    beaufort = ImageFont.truetype("/home/livreur/League-Card-Generator/static/fonts/BeaufortForLoL-TTF/BeaufortforLOL-Bold.ttf", 40)
    beaufort_titre = ImageFont.truetype("/home/livreur/League-Card-Generator/static/fonts/BeaufortForLoL-TTF/BeaufortforLOL-Heavy.ttf", 100)

    width, height = (1536, 512)
    image = generate_gradient("#091428","#0A1428",width,height)
    draw = ImageDraw.Draw(image)

    url_icone = f"http://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/{summoner_data['profileIconId']}.png"
    icone = Image.open(requests.get(url_icone, stream=True).raw)
    icone = round_image(icone.resize((190,190)))
    image.paste(icone,(159,144),icone)

    if challenges_data['preferences']:
        # A REGLER Livreur#TEST0
        url_bordure = f"static/league/border/border{math.floor(challenges_data['preferences']['prestigeCrestBorderLevel']//25)+1}.png"
        bordure = Image.open(url_bordure)
        image.paste(bordure,(0,0),bordure)
        
        titre = f"{get_titre(challenges_data['preferences']['title'])}"
        draw.text((256-draw.textlength(titre, beaufort)/2, 430), titre, fill="#F0E6D2", align="center", font=beaufort)

    niveau = f"{summoner_data['summonerLevel']}"
    draw.text((256-draw.textlength(niveau, beaufort)/2, 50), niveau, fill="#F0E6D2", font=beaufort)

    pseudo = f"{riot_data['gameName']}#{riot_data['tagLine']}"
    draw.text((500, 50), pseudo, fill="#F0E6D2", font=beaufort_titre)

    draw.text((500, 256), f"Rang : {get_rang(summoner_data['id'])}", fill="#F0E6D2", font=beaufort)
    counter = 10
    for i in get_champions(summoner_data['puuid']):
        image.paste(i, (width-130,counter),i)
        counter+=170
    draw.line(((500, 170), (500+draw.textlength(pseudo,beaufort_titre), 170)), "#C89B3C", width=4)

    return image

def random_image(dir):
    var = random.choice(os.listdir(dir))
    return var

def update_version():
    global version
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]

def get_name_from_id(id):
    global version
    data = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/fr_FR/champion.json").json()["data"]
    for name in data.keys():
        if data[name]["key"] == str(id):
            return f"https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/{name}_0.jpg"