# Backlog Scrum WPUR

## Vision

Automatiser la preparation des rapports de maintenance WordPress pour un catalogue de clients, en commencant par la collecte fiable des plugins installes et de leurs versions.

## Livrable zero

**Objectif :** disposer d'un outil utilisant un acces FTP pour lister les plugins installes sur un site WordPress.

### User story

En tant qu'utilisateur, je veux fournir un acces FTP a un site WordPress afin d'obtenir la liste des plugins installes et leur version actuelle.

### Criteres d'acceptation

- L'outil se connecte a un FTP standard.
- L'outil repere le dossier `wp-content/plugins`.
- L'outil liste les dossiers de plugins presents.
- L'outil lit les en-tetes WordPress des fichiers PHP de plugin.
- L'outil retourne au minimum le nom technique, le nom affiche et la version installee.
- L'outil signale clairement les plugins dont la version ne peut pas etre lue.

## Premier livrable

**Objectif :** afficher dans une interface simple la liste des plugins d'un site WordPress et leur version actuelle.

Preparation detaillee : voir [livrable-1.md](livrable-1.md).

### User story

En tant qu'utilisateur, je souhaite avoir une interface simple sur laquelle est visible la liste des plugins d'un site internet WordPress et leur version actuelle.

### Criteres d'acceptation

- L'utilisateur peut renseigner ou selectionner un site.
- L'interface affiche une ligne par plugin.
- Chaque ligne affiche le nom du plugin et la version installee.
- Les erreurs de connexion ou de lecture sont visibles sans bloquer toute l'interface.

## Second livrable

**Objectif :** ajouter la version disponible a installer.

### User story

En tant qu'utilisateur, je souhaite pouvoir voir la version actuellement installee et la version a installer pour chaque plugin.

### Criteres d'acceptation

- L'outil recupere la derniere version connue de chaque plugin public.
- L'outil gere les plugins premium ou prives sans resultat public.
- L'interface distingue clairement les plugins a jour, a mettre a jour et inconnus.

## Troisieme livrable

**Objectif :** alimenter dynamiquement une page Figma a partir d'un template.

Notes de cadrage : voir [figma-template-notes.md](figma-template-notes.md).

### User story

En tant qu'utilisateur, je souhaite generer une page de rapport Figma a partir des donnees de maintenance collectees.

### Criteres d'acceptation

- Un template Figma est identifie comme source.
- Les donnees de plugins alimentent les zones prevues du template.
- Le rapport tient sur une page.
- Pour un rapport de quatre semaines, quatre colonnes sont remplies sur cette meme page.

## Quatrieme livrable

**Objectif :** lancer l'outil sur un ou plusieurs sites clients.

### User story

En tant qu'utilisateur, je souhaite lancer l'outil sur une selection de sites clients afin de preparer les rapports de maintenance en lot.

### Criteres d'acceptation

- L'utilisateur peut configurer plusieurs sites clients.
- L'utilisateur peut lancer l'analyse sur un ou plusieurs sites.
- Les resultats sont regroupes par client et par site.
- Les erreurs d'un site ne bloquent pas les autres sites.

## Alertes rapport

### Regle metier initiale

Lors d'une maintenance, l'outil compare les plugins installes avec le dernier etat connu. Si un plugin a ete ajoute depuis la maintenance precedente, une alerte est levee.

### Donnees minimales a conserver

- Client
- Site
- Date de maintenance
- Plugins detectes
- Version installee
- Version disponible, quand elle est connue
- Alertes detectees
