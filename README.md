# WPUR

Outil de preparation de rapports de maintenance WordPress.

Le projet commence par le **livrable zero** : lister les plugins installes sur un site WordPress via un acces FTP.

## Livrable zero

## Interface locale temporaire

Pour tester avec un chemin sur ta machine :

```powershell
python -m wpur.ui
```

Puis ouvrir :

```text
http://127.0.0.1:8000
```

Le champ accepte soit le chemin racine d'un site WordPress, soit directement le dossier `wp-content/plugins`.

L'interface permet aussi de tester un acces FTP avec :

- hote
- utilisateur
- mot de passe
- port
- chemin WordPress sur le FTP

### Utilisation

```powershell
python -m wpur.plugins_ftp --host ftp.exemple.com --user mon_user --password mon_mot_de_passe
```

Si WordPress n'est pas a la racine FTP :

```powershell
python -m wpur.plugins_ftp --host ftp.exemple.com --user mon_user --password mon_mot_de_passe --base-path /www
```

Sortie JSON :

```powershell
python -m wpur.plugins_ftp --host ftp.exemple.com --user mon_user --password mon_mot_de_passe --format json
```

Sortie CSV :

```powershell
python -m wpur.plugins_ftp --host ftp.exemple.com --user mon_user --password mon_mot_de_passe --format csv
```

### Variables d'environnement

Les identifiants peuvent aussi etre fournis par variables d'environnement :

- `WPUR_FTP_HOST`
- `WPUR_FTP_USER`
- `WPUR_FTP_PASSWORD`
- `WPUR_FTP_BASE_PATH`

Exemple :

```powershell
$env:WPUR_FTP_HOST="ftp.exemple.com"
$env:WPUR_FTP_USER="mon_user"
$env:WPUR_FTP_PASSWORD="mon_mot_de_passe"
python -m wpur.plugins_ftp
```

## Documentation projet

Le backlog Scrum est disponible dans [docs/backlog.md](docs/backlog.md).

La preparation du livrable 1 est detaillee dans [docs/livrable-1.md](docs/livrable-1.md).

La premiere passe du livrable 2 est detaillee dans [docs/livrable-2.md](docs/livrable-2.md).
