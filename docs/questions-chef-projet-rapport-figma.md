# Questions a valider pour le rapport Figma

## Objectif

Clarifier le fonctionnement attendu du rapport avant d'automatiser la generation Figma.

Le point important : le rapport envoye au client est trimestriel, mais les operations de maintenance peuvent avoir une frequence differente selon le client.

## 1. Format du rapport trimestriel

Quelle structure doit avoir le rapport envoye chaque trimestre ?

- un seul document Figma par trimestre ?
+ une page par mois dans le document trimestriel ?
- une seule page pour tout le trimestre ?
- une page de synthese + des pages mensuelles ?


## 2. Role des colonnes

Que represente une colonne dans le tableau ?

- une semaine ?
+ une date d'intervention ?
- une quinzaine ?
+ une intervention de maintenance, quelle que soit sa date ?
- autre chose ?

Point a confirmer :

Les colonnes doivent-elles varier selon la frequence de maintenance du client ?

Exemples de frequences client :

- toutes les semaines
- tous les 15 jours
- tous les mois
- tous les trimestres
- tous les ans

## 3. Frequence client et nombre de colonnes

Pour un rapport trimestriel, combien de colonnes attend-on selon la frequence ?

Exemples a valider :

Client hebdomadaire   : environ 12 colonnes sur le trimestre
Client quinzaine      : environ 6 colonnes sur le trimestre
Client mensuel        : 3 colonnes sur le trimestre
Client trimestriel    : 1 colonne sur le trimestre
Client annuel         : seulement le trimestre concerne ou rapport vide ?

Question importante :

Si le format existant est mensuel, doit-on limiter chaque page mensuelle aux interventions du mois ?

## 4. Clients avec maintenance moins frequente que le trimestre

Certains clients peuvent avoir une frequence de maintenance moins frequente que le rythme d'envoi du rapport trimestriel, par exemple une maintenance annuelle.

Question a valider :

Comment gere-t-on ces clients lors des envois trimestriels ?

Options possibles :

- envoyer un rapport trimestriel vide indiquant qu'aucune operation n'etait prevue
- ne generer un rapport que sur le trimestre ou une intervention a eu lieu
- generer un rapport trimestriel avec un statut "aucune maintenance planifiee"
- exclure ces clients des envois trimestriels automatiques hors periode d'intervention

Decision attendue :

Pour les clients annuels ou avec une frequence moins frequente que trimestrielle, doit-on produire un rapport a chaque trimestre ou seulement lorsqu'une operation est realisee ?

## 5. Reprise d'un fichier existant

Workflow propose :

1. chercher le rapport Figma du client pour le mois
2. s'il existe, l'ouvrir
3. trouver la prochaine colonne libre
4. remplir cette colonne
5. sinon, creer le rapport depuis le template pour le nouveau mois

Question a valider :

Comment identifie-t-on qu'une colonne est deja remplie ?

Possibilites :

- par la date deja renseignee
- par un statut interne
- par un nom de calque Figma
- par un fichier de suivi cote outil

## 6. Plugins a afficher

Faut-il afficher :

- tous les plugins installes ?

Point a trancher :

Si un site a beaucoup de plugins, comment eviter de surcharger la page ?

Options possibles :

- ajouter une ligne "X plugins controles sans changement"
- creer une page supplementaire si necessaire

## 7. Sections du rapport

Confirmer les sections a conserver :

- contenu du site
- mise a jour du CMS
- mise a jour des plugins
- mise a jour des themes
- sauvegardes
- autre maintenance

Questions :

- faut-il garder exactement ces sections ?
- faut-il en ajouter ?
- faut-il pouvoir masquer une section vide ?
- faut-il renommer certaines sections selon le client ?

## 8. Donnees client necessaires

Pour chaque client, quelles donnees doit-on configurer ?

Proposition :

client_name
site_url
maintenance_frequency
report_period = quarterly
figma_template_id
figma_report_file_id
ftp_host
ftp_user
ftp_base_path

Question :

Les identifiants FTP doivent-ils etre stockes dans l'outil ou saisis a chaque lancement ?

## 9. Template Figma attendu

Elements utiles :

REPORT_TEMPLATE
month_label
report_number
client_name
site_url
date_column_template
section_template
row_template
plugin_row_template
checkbox_empty_template
checkbox_checked_template
footer

Questions :

- le rendu final doit-il etre exporte en PDF ?


## Decisions minimales a obtenir

Avant de commencer l'automatisation Figma, il faut au minimum valider :

1. structure du rapport trimestriel
2. signification des colonnes
3. comportement selon la frequence client
4. contenu exact des cellules
5. liste des plugins a afficher
6. regles si la page est trop pleine
7. structure et nommage du template Figma
8. reprise ou creation d'un fichier Figma

## Proposition technique actuelle

Partir sur :

```text
1 client = une configuration
1 trimestre = un rapport Figma
1 rapport trimestriel = 3 pages mensuelles
chaque page mensuelle reprend le design existant
l'outil remplit la prochaine colonne disponible selon la frequence du client
```

Cette approche semble la plus proche du modele fourni tout en restant automatisable.
