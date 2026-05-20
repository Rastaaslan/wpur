# Notes template Figma

## Idee generale

Le rapport pourra fonctionner comme une automatisation de document type Word : un template maitre reste intact, l'outil le duplique, puis remplit la copie avec les donnees de maintenance.

## Strategie recommandee

Utiliser une base de design stable, puis exposer seulement les zones qui doivent changer.

### Base stable

- logo
- fond
- titres fixes
- separateurs
- pictos
- styles graphiques
- structure des colonnes
- pied de page

### Champs dynamiques

- nom du client
- URL du site
- periode du rapport
- date de maintenance
- liste des plugins
- version actuellement installee
- version a installer
- alertes
- commentaires de maintenance

### Blocs dynamiques

- ligne plugin modele
- colonne semaine modele
- bloc alerte
- bloc resume

## Nommage possible dans Figma

Exemples de noms d'elements a prevoir dans le template :

```text
REPORT_TEMPLATE
client_name
site_url
report_period
maintenance_date
week_column_template
plugin_row_template
alerts_block
summary_block
```

## Duplication automatisee

Le workflow cible :

1. conserver un template maitre Figma intact
2. dupliquer automatiquement la page ou le frame template
3. renommer la copie, par exemple `Rapport - Client X - Mai 2026`
4. remplir les champs dynamiques
5. dupliquer les lignes plugins selon le nombre de plugins detectes
6. ajuster les colonnes et blocs necessaires
7. produire un rapport final pret dans Figma

## Gestion dynamique des plugins

Le nombre de lignes plugins ne doit pas etre fixe dans le template.

L'outil devra pouvoir :

- dupliquer une ligne modele autant de fois que necessaire
- remplir chaque ligne avec les donnees du plugin
- ajuster l'espacement vertical
- masquer ou supprimer les lignes inutiles
- repartir les lignes dans plusieurs colonnes si necessaire

## Regles de mise en page a definir

Pour garantir que le rapport tienne sur une seule page, il faudra definir des regles :

- nombre maximum de plugins par colonne
- comportement si une liste est trop longue
- taille minimale de texte acceptable
- affichage resume si le volume depasse la place disponible
- gestion des rapports sur 1, 2, 3 ou 4 semaines

## Point important

Plus le template est proprement structure et nomme, plus l'automatisation sera robuste. L'outil devra modifier uniquement les champs et blocs prevus, sans toucher au socle graphique.
