# Livrable 1 - Interface simple plugins WordPress

## Objectif

Afficher dans une interface simple la liste des plugins d'un site WordPress et leur version actuellement installee.

## Perimetre

Ce livrable s'appuie sur la lecture deja disponible :

- depuis un acces FTP
- depuis un chemin local temporaire pour les tests

## Parcours utilisateur

1. ouvrir l'interface locale
2. choisir la source : Local ou FTP
3. renseigner les champs de connexion ou le chemin local
4. lancer l'analyse
5. consulter la liste des plugins detectes

## Donnees affichees

Pour chaque plugin :

- nom affiche
- identifiant technique
- version actuelle
- fichier principal detecte
- statut de lecture

L'interface affiche aussi :

- le nombre total de plugins detectes
- la derniere source analysee
- un resume des statuts de lecture

## Fonctions de confort

- recherche par nom, identifiant, version ou fichier principal
- filtre par statut : OK, version manquante, illisible
- tri alphabetique automatique des plugins
- validation des champs avant lancement de l'analyse

## Etats geres

- champs obligatoires manquants
- port FTP invalide
- erreur de connexion ou de lecture FTP
- chemin local invalide
- plugin sans version detectable
- plugin illisible

## Criteres d'acceptation

- l'utilisateur peut lancer une analyse depuis l'interface
- les plugins detectes apparaissent sous forme de tableau
- chaque ligne affiche au minimum le nom du plugin et sa version actuelle
- l'utilisateur voit clairement combien de plugins ont ete detectes
- l'utilisateur voit la derniere source analysee
- l'utilisateur peut rechercher ou filtrer dans les plugins detectes
- les erreurs sont affichees sans bloquer l'interface

## Hors perimetre

- recuperation de la derniere version disponible
- comparaison avec une maintenance precedente
- rapport Figma
- gestion multi-sites clients
