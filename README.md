# WPUR

Outil de preparation de rapports de maintenance WordPress.

WPUR sait aujourd'hui lister les plugins installes, lire leur version actuelle,
puis enrichir ces resultats avec la derniere version publique connue sur
WordPress.org quand le plugin est disponible dans le repertoire public.

## Installation dev

```powershell
python -m pip install -e ".[dev]"
```

Puis lancer les tests :

```powershell
python -m pytest
```

## Interface locale

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

La case **Versions disponibles WordPress.org** active l'enrichissement du
livrable 2 : version disponible, statut de mise a jour, plugin public,
premium/prive, inconnu ou en erreur.

## CLI FTP

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

Avec les dernieres versions publiques :

```powershell
python -m wpur.plugins_ftp --host ftp.exemple.com --user mon_user --password mon_mot_de_passe --with-latest
```

Sortie JSON enrichie :

```powershell
python -m wpur.plugins_ftp --host ftp.exemple.com --user mon_user --password mon_mot_de_passe --with-latest --format json
```

Options utiles :

- `--refresh-latest` ignore le cache local ;
- `--version-cache` choisit le fichier de cache JSON ;
- `--version-timeout` regle le delai API WordPress.org ;
- `--version-workers` regle le nombre de recherches en parallele.

## CLI versions publiques

Pour tester directement la version publique d'un plugin :

```powershell
python -m wpur.versions akismet contact-form-7 --json
```

Statuts de mise a jour :

- `up_to_date` : version installee egale a la version publique ;
- `update_available` : une version publique plus recente existe ;
- `premium_custom` : plugin absent du repertoire public WordPress.org ;
- `unknown` : information insuffisante ;
- `error` : erreur de recuperation ;
- `newer_than_public` : la version installee semble plus recente que la version publique.

Les resultats WordPress.org sont mis en cache par defaut dans
`.wpur-cache/plugin_versions.json`. Le chemin peut aussi etre force avec la
variable `WPUR_VERSION_CACHE`.

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

Le livrable 2 est detaille dans [docs/livrable-2.md](docs/livrable-2.md).
