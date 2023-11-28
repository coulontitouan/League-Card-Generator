import math
from .app import app ,db
from flask import flash, render_template, redirect, url_for, send_file
from flask_login import login_user , current_user, logout_user
from flask import request,redirect, url_for
from flask_login import login_required
from wtforms import StringField , HiddenField, DateField , RadioField, PasswordField,SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from hashlib import sha256
from .models import *
from .commands import newuser
from wtforms import DateField
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

with app.app_context():
    class CreeCompetitionForm(FlaskForm):
        """Classe qui permet de créer une compétition"""
        nom_lieu = StringField('Nom lieu',validators=[DataRequired()])
        adresse_lieu = StringField('Adresse lieu',validators=[DataRequired()])
        ville_lieu = StringField('Ville lieu',validators=[DataRequired()])
        nom_competition = StringField('Nom compétition',validators=[DataRequired()])
        date_competition = DateField('Date compétition', format='%Y-%m-%d', validators=[DataRequired()])
        sexe_competition = RadioField('Sexe',choices = ['Hommes','Femmes'])
        coefficient_competition = StringField('Coefficient',validators=[DataRequired()])
        nom_arme = SelectField("Arme",coerce=str,default=1)
        nom_categorie = SelectField("Catégorie",coerce=str,default=1)
        next = HiddenField()
    
@app.route("/")
def home():
    competitions = get_all_competitions()
    return render_template(
        "home.html",
        competitions = competitions
    )

@app.route("/informations")
def informations():
    return render_template(
        "informations.html"
    )

class LoginForm(FlaskForm):
    num_licence=StringField('num_licence',validators=[DataRequired()])
    mot_de_passe=PasswordField("Password",validators=[DataRequired()])
    next = HiddenField()

    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        m=sha256()
        m.update(self.mot_de_passe.data.encode())
        passwd= m.hexdigest()
        return user if passwd == user.mot_de_passe else None
    
        
class SignUpForm(FlaskForm):
    num_licence=StringField('num_licence',validators=[DataRequired()])
    mot_de_passe=PasswordField("Password",validators=[DataRequired()])
    prenom = StringField('prenom',validators=[DataRequired()])
    nom = StringField('nom',validators=[DataRequired()])
    sexe = RadioField('sexe',choices = ['Homme','Femme'],validators=[DataRequired()])
    date_naissance = DateField('date',validators=[DataRequired()])
    club = SelectField("club",coerce=str,default=2,validators=[DataRequired()], choices = [(1,""),(2,""),(3,""),(4,""),(5,"")])
    next=HiddenField()

    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        m=sha256()
        m.update(self.mot_de_passe.data.encode())
        passwd= m.hexdigest()
        return user if passwd == user.mot_de_passe else None
    
    
    def est_deja_inscrit_sans_mdp(self):
        user = Escrimeur.query.get(self.num_licence.data)
        a= "Homme"
        if user is not None:
            if self.sexe.data == "Femme":
                a = "Dames" 
            if user.sexe == a and user.prenom.upper() == self.prenom.data.upper() and user.nom.upper() == self.nom.data.upper():
                m=sha256()
                m.update(self.mot_de_passe.data.encode())
                passwd= m.hexdigest()
                user.set_mdp(passwd)
                db.session.commit()
                return True
        else:
            return None

@app.route("/connexion/", methods=("GET", "POST"))
def connexion():
    f =LoginForm()
    f2 = SignUpForm()
    selection_club = []
    for club in db.session.query(Club).all():
        if club.id != 1:
            selection_club.append((club.id, club.nom))
    f2.club.choices = selection_club
    if not f.is_submitted():
        f.next.data = request.args.get("next")

    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            prochaine_page = f.next.data or url_for("home")
            return redirect(prochaine_page)
    return render_template(
        "connexion.html",formlogin=f, formsignup = f2)

@app.route("/connexion/inscription", methods=("GET", "POST"))
def inscription():
    f =LoginForm()
    f2 = SignUpForm()
    selection_club = []
    for club in db.session.query(Club).all():
        if club.id !=1:
            selection_club.append((club.id,club.nom))
    f2.club.choices = selection_club
    if not f2.is_submitted():
        f2.next.data = request.args.get("next")
    elif f2.validate_on_submit():
        if f2.est_deja_inscrit_sans_mdp() is not None:
            user = f2.get_authenticated_user()
            if user:
                    login_user(user)
                    prochaine_page = f2.next.data or url_for("home")
                    return redirect(prochaine_page)
        else:
            if f2.sexe.data == "Femme":
                newuser(f2.num_licence.data,f2.mot_de_passe.data,f2.prenom.data,f2.nom.data,"Dames",f2.date_naissance.data,f2.club.data)
            else:       
                newuser(f2.num_licence.data,f2.mot_de_passe.data,f2.prenom.data,f2.nom.data,"Homme",f2.date_naissance.data,f2.club.data)

                user = f2.get_authenticated_user()
                if user:
                        login_user(user)
                        prochaine_page = f2.next.data or url_for("home")
                        return redirect(prochaine_page)

    return render_template(
        "connexion.html",formlogin=f, formsignup = f2)

@app.route("/competition/<int:id>")
def competition(id):
    """Fonction qui permet d'afficher une compétition"""
    competition = get_competition(id)
    return render_template(
        "competition.html",
        competition = competition
    )

@app.route("/competition/<int:idC>/poule/<int:idP>")
def poule(idC, idP):
    """Fonction qui permet d'afficher une poule"""
    return render_template(
        "poule.html"
    )

@app.route("/deconnexion/")
def deconnexion():
    logout_user()
    return redirect(url_for("home"))

@app.route('/cree/competition/', methods=("GET", "POST"))
def creationCompet():
    """Fonction qui permet de créer une compétition"""
    f = CreeCompetitionForm()
    f.nom_arme.choices = cree_liste(get_all_armes())
    f.nom_categorie.choices = cree_liste(get_all_categories())
    if not  f.is_submitted():
        f.next.data = request.args.get("next")
    else:
        lieu = get_lieu(f.nom_lieu.data, f.adresse_lieu.data, f.ville_lieu.data)
        arme = get_arme(f.nom_arme.data)
        categorie = get_categorie(f.nom_categorie.data)
        if lieu is None:
            lieu = Lieu(nom =  f.nom_lieu.data, adresse =  f.adresse_lieu.data, ville =  f.ville_lieu.data)
            db.session.add(lieu)
            db.session.commit()
        competition = Competition(id = (get_max_competition_id() + 1), nom = f.nom_competition.data, date = f.date_competition.data, coefficient = f.coefficient_competition.data, sexe = f.sexe_competition.data, id_lieu = lieu.id, id_arme = arme.id, id_categorie = categorie.id)
        db.session.add(competition)
        db.session.commit()
        flash('Compétition créée avec succès', 'success')  # Utilise Flash de Flask pour les messages
        return redirect(url_for('home'))
    return render_template('cree-competition.html', form=f)

@app.route("/profil")
def profil():
    return render_template(
        "profil.html"
    )

# class Changer_mdpForm(FlaskForm):
#     new_mdp=PasswordField("Password",validators=[DataRequired()])
#     next = HiddenField()

# @app.route("/profil/changer-mdp", methods=("POST",))
# def changer_mdp():
#     f =Changer_mdpForm()
#     return render_template(
#         "changer-mdp.html", f
#     )

from flask import request, jsonify
import os, signal
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