import math
import random
from .app import app
from flask import flash, render_template, redirect, url_for, send_file
from flask import request,redirect, url_for
from wtforms import StringField , HiddenField, DateField , RadioField, PasswordField,SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from PIL import Image, ImageDraw, ImageFont
import requests
from flask import request, jsonify
import os, signal
riot_key = "RGAPI-604ac389-4dd6-4826-874e-624da22391fc"
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

class RiotForm(FlaskForm):
    pseudo=StringField('pseudo',validators=[DataRequired()])
    tag=StringField('tag',validators=[DataRequired()])
    next = HiddenField()

    def est_valide(self):
        player = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self.pseudo.data}/{self.tag.data}?api_key={riot_key}").json()
        print(player)
        return player.get("puuid","") != ""

@app.route("/", methods=("GET", "POST"))
def home():
    f = RiotForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    if f.validate_on_submit():
        valide = f.est_valide()
        if valide:
            print(f)
            return redirect(url_for("cree_image",name=f.pseudo.data,tag=f.tag.data))
    if(not riot_key.startswith("RGAPI")):
        return render_template(
            "404.html",
            image=image404("static/404/")
        )
    return render_template(
        "home.html",
        form=f
    )

@app.route('/image/<name>/<tag>.png')
def cree_image(name,tag):
    print(name,tag)
    player,profil,challenges = get_data(name,tag)
    
    user_image = generate_image(player,profil,challenges)
    
    temp_image_path = f"static/league/{name}#{tag}.png"
    user_image.save(temp_image_path)
    
    return send_file(temp_image_path, mimetype='image/png')

@app.route("/shutdown", methods=['GET'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({ "success": True, "message": "Server is shutting down..." })

def get_data(name,tag):
    player_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={riot_key}"
    response = requests.get(player_url)
    player_data = response.json()

    profil_url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{player_data['puuid']}?api_key={riot_key}"
    response = requests.get(profil_url)
    profil_data = response.json()

    challenges_url = f"https://euw1.api.riotgames.com/lol/challenges/v1/player-data/{player_data['puuid']}?api_key={riot_key}"
    response = requests.get(challenges_url)
    challenges_data = response.json()

    return player_data,profil_data,challenges_data

def get_titre(id):
    if id == "":
        return ""
    titres = requests.get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/fr_fr/v1/challenges.json").json()["titles"]
    for t in titres:
        if int(titres[t]['itemId']) == int(id):
            return titres[t]['name']
    return ""
        
def get_rang(id_joueur):
    if id_joueur == "":
        return "Non classé"
    classes = requests.get(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{id_joueur}?api_key={riot_key}").json()
    for c in classes:
        if c['queueType'] == "RANKED_SOLO_5x5":
            return f"{rang_trad[c['tier']]} {c['rank']} {c['leaguePoints']} PL"
    return "Non classé"

def round_image(image:Image, transparent:bool=False):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.width, image.height), fill=255)
    if transparent:
        result = Image.new("RGBA", image.size, (255,255,255,0))
    else:
        result = Image.new("RGB", image.size, (255,255,255))
    result.paste(image,mask=mask)
    return result

def get_champions(id_joueur, limit=3):
    champions = requests.get(f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id_joueur}?api_key={riot_key}").json()[:limit]
    result = []

    for c in champions:
        lien = f"https://cdn.communitydragon.org/latest/champion/{c['championId']}/tile"
        image_champ = round_image(Image.open(requests.get(lien, stream=True).raw).resize((105,105)),True)

        lien = f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-champion-details/global/default/cdp-prog-mastery-{c['championLevel']}.png"
        image_maitrise = Image.open(requests.get(lien, stream=True).raw)
    
        image_maitrise.paste(image_champ,(7,13),image_champ)

        image_maitrise = image_maitrise.resize((96,160))

        result.append(image_maitrise)
    return result

def generate_gradient(colour1: str, colour2: str, width: int, height: int) -> Image:
    """Generate a vertical gradient."""
    left = Image.new('RGB', (width, height), colour1)
    right = Image.new('RGB', (width, height), colour2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for x in range(width):
        mask_data.append(int(255 * (x / width)))
    mask_data.extend(mask_data*(height-1))
    print(len(mask_data))
    mask.putdata(mask_data)
    left.paste(right, (0, 0), mask)
    return left

def generate_image(player_data,profil_data,challenges_data):
    
    width, height = (1536, 512)
    image = generate_gradient("#091428","#0A1428",width,height)
    draw = ImageDraw.Draw(image)
    
    arialrounded = ImageFont.truetype("static/fonts/BeaufortForLoL-TTF/BeaufortforLOL-Bold.ttf", 40)
    impact = ImageFont.truetype("static/fonts/Spiegel-TTF/Spiegel_TT_Bold.ttf", 100)
    
    url_icone = f"https://cdn.communitydragon.org/latest/profile-icon/{profil_data['profileIconId']}"
    icone = Image.open(requests.get(url_icone, stream=True).raw)
    icone = round_image(icone.resize((190,190)),True)
    image.paste(icone,(159,144),icone)

    url_bordure = f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/uikit/themed-borders/theme-{math.floor(challenges_data['preferences']['prestigeCrestBorderLevel']//25)+1}-border.png"
    bordure = Image.open(requests.get(url_bordure, stream=True).raw)
    image.paste(bordure,(0,0),bordure)

    titre = f"{get_titre(challenges_data['preferences']['title'])}"
    draw.text((256-draw.textlength(titre, arialrounded)/2, 430), titre, fill="#F0E6D2", align="center", font=arialrounded)

    niveau = f"{profil_data['summonerLevel']}"
    draw.text((256-draw.textlength(niveau, arialrounded)/2, 50), niveau, fill="#F0E6D2", font=arialrounded)

    pseudo = f"{player_data['gameName']}#{player_data['tagLine']}"
    draw.text((500, 50), pseudo, fill="#F0E6D2", font=impact)

    draw.text((500, 256), f"Rang : {get_rang(profil_data['id'])}", fill="#F0E6D2", font=arialrounded)
    counter = 10
    for i in get_champions(profil_data['id']):
        image.paste(i, (width-130,counter),i)
        counter+=170
    draw.line(((500, 170), (500+draw.textlength(pseudo,impact), 170)), "#C89B3C", width=4)

    return image

def image404(dir):
    print(random.choice(os.listdir(dir)))
    return f"{dir}{random.choice(os.listdir(dir))}"