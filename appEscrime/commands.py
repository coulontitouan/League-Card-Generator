"""Module contenant les commandes de l'application."""
from datetime import datetime
import csv
from hashlib import sha256
import os
import click
from sqlalchemy import desc
from .app import app , db
from .models import Type_phase, Arme, Categorie, Club, Escrimeur, Classement, Lieu, Competition, Phase, Match, Participation, Resultat

@app.cli.command()
def loadbd():
    """Crée les tables et gère le peuplement de la base de données"""

    # création de toutes les tables
    db.create_all()

    # création des 3 armes possibles
    armes = {'Fleuret': Arme(libelle = 'Fleuret'),
             'Epée': Arme(libelle = 'Epée'),
             'Sabre': Arme(libelle = 'Sabre')}
    for arme in armes.values():
        db.session.add(arme)

    # création des 9 catégories possibles
    categories = {'M13': Categorie(libelle = 'M13', age_maxi = 13),
                  'M15': Categorie(libelle = 'M15', age_maxi = 15),
                  'M17': Categorie(libelle = 'M17', age_maxi = 17),
                  'M20': Categorie(libelle = 'M20', age_maxi = 20),
                  'Seniors': Categorie(libelle = 'Seniors', age_maxi = 39),
                  'Vétérans1': Categorie(libelle = 'Vétérans1', age_maxi = 49),
                  'Vétérans2': Categorie(libelle = 'Vétérans2', age_maxi = 59),
                  'Vétérans3': Categorie(libelle = 'Vétérans3', age_maxi = 69),
                  'Vétérans4': Categorie(libelle = 'Vétérans4', age_maxi = -1)}
    for categorie in categories.values():
        db.session.add(categorie)

    # création de l'instance de club permettant d'identifier les administrateurs
    clubs = {'CEB Admin': Club(nom = 'CEB Admin'),
             'Aucun club': Club(nom = 'Aucun club')}
    for club in clubs.values():
        db.session.add(club)

    # création du type de phase de poule
    types_phase = {'Poule': Type_phase(libelle = 'Poule', touches_victoire = 5)}
    for type_phase in types_phase.values():
        db.session.add(type_phase)

    db.session.commit()

    escrimeurs = {}
    competitions = {}
    lieux = {}
    phases = {}

    # chargement de toutes les données
    for nom_fichier in os.listdir('../data'): # Éxecution dans appEscrime
        with open('../data/' + nom_fichier, newline = '', encoding = 'Latin-1') as fichier:
            nom_fichier = nom_fichier[:-4]
            print(nom_fichier)
            lecteur = csv.DictReader(fichier, delimiter = ';')
            contenu = nom_fichier.split('_')

            if contenu[0] == 'classement':
                load_escrimeurs(contenu, lecteur, escrimeurs, clubs, armes, categories)
                
            elif contenu[0] == 'connexion':
                load_connexion(lecteur, escrimeurs)

            elif contenu[0] == 'competitions':
                load_competitions(lecteur, armes, categories, competitions, lieux)

            elif contenu[0] == 'matchs':
                load_matchs(contenu, lecteur, escrimeurs, competitions, types_phase, phases)

            elif contenu[0] == 'resultats':
                load_resultats(contenu, lecteur)

            db.session.commit()


def load_escrimeurs(contenu, lecteur, escrimeurs, clubs, armes, categories):
    """Charge les escrimeurs, classements, armes, catégories et clubs dans la base de données

    Args:
        contenu (list[String]): le contenu du fichier csv courant
        lecteur (DictReader): le lecteur du fichier csv courant
        escrimeurs (dict): le dictionnaire des escrimeurs déjà présents dans la base
        clubs (_type_): le dictionnaire des clubs déjà présents dans la base
        armes (_type_): le dictionnaire des armes déjà présentes dans la base
        categories (_type_): le dictionnaire des catégories déjà présentes dans la base
    """

    if '-' in contenu[3]:
        split_cat = contenu[3].split('-')
        contenu[3] = split_cat[0][:-1] + split_cat[-1]

    for ligne in lecteur:
        print(ligne)
        nom_club = ligne['club']
        if nom_club not in clubs:
            club = Club(nom = nom_club)
            clubs[nom_club] = club
            db.session.add(club)

        licence = ligne['adherent']
        if licence not in escrimeurs:
            naissance = ligne['date naissance'].split('/')
            club = clubs[nom_club]
            escrimeur = Escrimeur(num_licence = licence,
                                  prenom = ligne['prenom'],
                                  nom = ligne['nom'],
                                  sexe = contenu[2],
                                  date_naissance = datetime(int(naissance[2]),
                                                            int(naissance[1]),
                                                            int(naissance[0])),
                                  club = club)
            escrimeurs[licence] = escrimeur
            db.session.add(escrimeur)

        arme = armes[contenu[1]]
        categorie = categories[contenu[3]]
        escrimeur = escrimeurs[ligne['adherent']]
        db.session.add(Classement(rang = ligne['rang'],
                                  points = ligne['points'],
                                  num_licence = escrimeur.num_licence,
                                  id_arme = arme.id,
                                  id_categorie = categorie.id))


def load_connexion(lecteur, escrimeurs):
    """Charge les informations de connexion dans la base de données

    Args:
        lecteur (DictReader): le lecteur du fichier csv courant
        escrimeurs (dict): le dictionnaire des escrimeurs déjà présents dans la base
    """
    for ligne in lecteur:
        mdp = ligne['mdp']
        escrimeur = escrimeurs[ligne['adherent']]
        escrimeur.set_mdp(mdp)


def load_competitions(lecteur, armes, categories, competitions, lieux):
    """Charge les compétitions dans la base de données

    Args:
        lecteur (DictReader): le lecteur du fichier csv courant
        categories (dict): le dictionnaire des catégories déjà présentes dans la base
        competitions (dict): le dictionnaire des compétitions déjà présentes dans la base
        lieux (dict): le dictionnaire des lieux déjà présents dans la base
    """
    for ligne in lecteur:
        nom_lieu = ligne['lieu']
        if nom_lieu not in lieux:
            lieu = Lieu(nom = nom_lieu,
                        adresse = ligne['adresse'],
                        ville = ligne['ville'])
            lieux[nom_lieu] = lieu
            db.session.add(lieu)

        date_compet = ligne['date'].split('/')
        arme = armes[ligne['arme']]
        categorie = categories[ligne['categorie']]
        lieu = lieux[ligne['lieu']]
        competition = Competition(nom = ligne['nom'],
                                  date = datetime(int(date_compet[2]),
                                                  int(date_compet[1]),
                                                  int(date_compet[0])),
                                  coefficient = ligne['coefficient'],
                                  sexe = ligne['sexe'],
                                  id_arme = arme.id,
                                  id_categorie = categorie.id,
                                  id_lieu = lieu.id
                                  )
        competitions[ligne['nom']] = competition
        db.session.add(competition)


def load_matchs(contenu, lecteur, escrimeurs, competitions, phases, types_phase):
    """Charge les matchs dans la base de données

    Args:
        contenu (list[String]): le contenu du fichier csv courant
        lecteur (DictReader): le lecteur du fichier csv courant
        escrimeurs (dict): le dictionnaire des escrimeurs déjà présents dans la base
        competitions (dict): le dictionnaire des compétitions déjà présentes dans la base
        phases (dict): le dictionnaire des phases de compétition déjà présentes dans la base
        types_phase (dict): le dictionnaire des types de phase déjà présents dans la base
    """
    for ligne in lecteur:
        nom_phase = ligne['libelle phase']
        if nom_phase not in types_phase:
            type_phase = Type_phase(libelle = nom_phase, nb_touches = 15)
            types_phase[nom_phase] = type_phase
            db.session.add(type_phase)

        concatenation_compet_phase = competitions[contenu[3]] + ligne['phase']
        if concatenation_compet_phase not in phases:
            phase = Phase(id = ligne['phase'],
                          id_competition = competitions[contenu[4]],
                          libelle = nom_phase)
            phases[concatenation_compet_phase] = phase
            db.session.add(phase)

            mmatch = Match(id = ligne['numero'],
                           id_competition = competitions[contenu[3]],
                           id_phase = ligne['phase'],
                           piste = ligne['piste'],
                           etat = ligne['etat'],
                           num_arbitre = escrimeurs[ligne['arbitre']].num_licence)
            db.session.add(mmatch)

            for i in range(1,3):
                escrimeur = escrimeurs[ligne['tireur' + i]]
                nb_touches = int(ligne['touches' + i])
                if ligne['etat'] == 'Termine':
                    if nb_touches == types_phase[ligne['libelle phase']].touches_victoire:
                        db.session.add(Participation(match = mmatch,
                                                     tireur = escrimeur,
                                                     touches = nb_touches,
                                                     statut = "Vainqueur"))
                    else:
                        db.session.add(Participation(match = mmatch,
                                                     tireur = escrimeur,
                                                     touches = nb_touches,
                                                     statut = "Perdant"))
                else:
                    db.session.add(Participation(match = mmatch,
                                                 tireur = escrimeur,
                                                 touches = nb_touches))


def load_resultats(contenu, lecteur):
    """Charge les résultats dans la base de données

    Args:
        contenu (list[String]): le contenu du fichier csv courant
        lecteur (DictReader): le lecteur du fichier csv courant
    """
    for ligne in lecteur:
        competition = contenu[3]
        db.session.add(Resultat(id_competition = competition,
                                id_escrimeur = ligne['adherent'],
                                rang = ligne['rang'],
                                points = ligne['points']))


@app.cli.command()
def syncbd():
    """Crée les tables de la base de données"""
    db.create_all()

@app.cli.command()
def deletebd():
    """Supprime la base de données"""
    if os.path.exists('../CEB.db'):
        os.remove('../CEB.db')

def newuser(num_licence, password, prenom, nom, sexe,ddn,club):
    m=sha256()
    m.update(password.encode())
    tireur = Escrimeur(num_licence = num_licence, mot_de_passe = m.hexdigest(), prenom = prenom, nom = nom, sexe = sexe, date_naissance = ddn, id_club = club )
    db.session.add(tireur)
    db.session.commit()

@app.cli.command()
@click.argument('prenom')
@click.argument('nom')
@click.argument('sexe')
@click.argument('mot_de_passe')
def newadmin(prenom, nom, sexe, mot_de_passe ):
    """Ajoute un admin"""
    m = sha256()
    m.update(mot_de_passe.encode())
    num = Escrimeur.query.order_by(desc(Escrimeur.num_licence)).filter_by(id_club=1).first()
    if num is None:
        num = '0'
    else:
        num = num.num_licence
    date_convert = datetime.strptime('01-01-0001', '%d-%m-%Y').date()
    u = Escrimeur(num_licence=str(int(num)+1) , prenom=prenom, nom=nom, sexe=sexe, date_naissance=date_convert, id_club=1, mot_de_passe=m.hexdigest())
    db.session.add(u)
    db.session.commit()