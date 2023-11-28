# Projet 2 : Gestion – Compétition Escrime
---
Titouan COULON, Noam DOUCET, Anthony GARDELLE, Arthur GOUDAL, Killian OUZET
---
---
# Reformulation de la commande
Avec l'objectif final de gérer plusieurs compétitions d'escrime nous devions créer une application où l'on peut :
+ Répondre à la définition de la compétition.
+ Inscrire à la compétition un nombre de « tireurs » ou « tireuses » non limité.
+ Inscrire des arbitres au compétition.
+ Répartire automatique les compétiteurs en poule de 5 à 9 participants, selon
  les règles de la fédération.
+ Répartire des poules ou les matches d’élimination sur les pistes disponibles.
+ Gérer des phases d’élimination directe après les phases de poule.
+ Éditer sur application des feuilles de match (feuille de score données aux arbitres).
+ Établir un classement provisoire (après les poules) et d’un classement final après les matchs d’élimination.
+ Afficher sur grand écran des classements et de l’arbre du tableau d’élimination et des résultats.

Spécifications techniques :
+ On considère qu’il existe une base de données régionale des escrimeurs qui
  pratiquent la compétition. Si un joueur s’inscrit pour la première fois à une
  compétition, l’application l’ajoutera à cette base.
+ L’application archivera les compétitions gérées par le club et mettra à jour les
  classements des compétiteurs. Attention, le classement à l’issue de la compétition
  n’est qu’un élément du classement à proprement parler d’un joueur. (Fusion avec
  des BD externe)
+ On considère qu'il existe 6 armes (fleuret homme, fleuret femme, épée homme, épée femme, sabre homme
et sabre femme) et 9 catégories (U13, U15, U17, U20, senior, V1, V2, V3, V4).
---
# Mise en place de l'application
Pour lancer l'application il vous suffit d'éxécuter les commande bash suivante :
```
git clone https://github.com/coulontitouan/escrime.git
cd escrime
source start.sh (Linux)
.\start.ps1 (Windows)
```
Ensuite il vous suffit de cliquer sur "http://192.168.28.66:8080"
```
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://192.168.28.66:8080
Press CTRL+C to quit
```
Pour fermer l'application il suffit de faire la combinaison de touche CTRL+C dans le terminal