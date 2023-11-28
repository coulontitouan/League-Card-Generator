import math
from .app import app
from flask import flash, render_template, redirect, url_for, send_file
from flask_login import login_user , current_user, logout_user
from flask import request,redirect, url_for
from flask_login import login_required
from wtforms import StringField , HiddenField, DateField , RadioField, PasswordField,SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from hashlib import sha256
from wtforms import DateField
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from flask import request, jsonify
import os, signal

@app.route("/")
def home():
    competitions = None
    return render_template(
        "home.html",
        competitions = competitions
    )

@app.route('/image/<name>/<tag>.png')
def serve_user_image(name,tag):
    # Obtenez les données depuis l'API
    print(name,tag)
    profil,challenges = get_data(name,tag)
    
    # Générez l'image à partir des données
    user_image = generate_image(profil,challenges)
    
    # Sauvegardez l'image temporairement pour la servir
    temp_image_path = f"static/league/{name}#{tag}.png"
    user_image.save(temp_image_path)
    
    # Renvoyez l'image au navigateur
    return send_file(temp_image_path, mimetype='image/png')

@app.route("/shutdown", methods=['GET'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({ "success": True, "message": "Server is shutting down..." })

def get_data(name,tag):
    player_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key=RGAPI-604ac389-4dd6-4826-874e-624da22391fc"
    response = requests.get(player_url)
    player_data = response.json()


    profil_url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{player_data['puuid']}?api_key=RGAPI-604ac389-4dd6-4826-874e-624da22391fc"
    response = requests.get(profil_url)
    profil_data = response.json()

    challenges_url = f"https://euw1.api.riotgames.com/lol/challenges/v1/player-data/{player_data['puuid']}?api_key=RGAPI-604ac389-4dd6-4826-874e-624da22391fc"
    response = requests.get(challenges_url)
    challenges_data = response.json()

    return profil_data,challenges_data

def get_titre(id):
    titres = requests.get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/fr_fr/v1/challenges.json").json()["titles"]
    for t in titres:
        if int(titres[t]['itemId']) == int(id):
            return titres[t]['name']
        
def get_rang(id):
    pass

def generate_image(profil_data,challenges_data):
    
    image = Image.new("RGBA", (1536, 512), color="white")
    draw = ImageDraw.Draw(image)

    draw.text((500, 100), f"Pseudo: {profil_data['name']}", fill="black")
    draw.text((500, 130), f"Niveau: {profil_data['summonerLevel']}", fill="black")
    draw.text((500, 160), f"Titre: {get_titre(challenges_data['preferences']['title'])}", fill="black")
    draw.text((500, 190), f"Rang: {get_rang(None)}", fill="black")
    
    url_icone = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{profil_data['profileIconId']}.jpg"
    icone = Image.open(requests.get(url_icone, stream=True).raw)
    icone = icone.resize((190,190))

    url_bordure = f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/uikit/themed-borders/theme-{math.floor(challenges_data['preferences']['prestigeCrestBorderLevel']//25)+1}-border.png"
    bordure = Image.open(requests.get(url_bordure, stream=True).raw)
    mask = Image.new("L", icone.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, icone.width, icone.height), fill=255)
    result = Image.new("RGB", icone.size, (255,255,255))
    result.paste(icone,mask=mask)
    icone = result
    
    image.paste(icone,(159,144))

    image.paste(bordure,(0,0),bordure)

    return image

