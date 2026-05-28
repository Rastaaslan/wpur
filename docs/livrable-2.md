# Livrable 2 - Versions disponibles des plugins

## Objectif

Afficher, pour chaque plugin detecte, la version actuellement installee et la
derniere version publique connue quand le plugin existe sur WordPress.org.

## Perimetre implemente

- recuperation des informations via l'endpoint JSON public WordPress.org ;
- enrichissement des resultats FTP et locaux ;
- cache JSON local avec TTL pour eviter les appels repetes ;
- fallback sur cache stale en cas d'erreur reseau ;
- recherches de versions en parallele ;
- CLI dediee `python -m wpur.versions` ;
- option CLI FTP `--with-latest` ;
- affichage dans l'interface locale ;
- tests unitaires sur comparaison de versions, statuts, cache et enrichissement.

## Source distante

WPUR interroge :

```text
https://api.wordpress.org/plugins/info/1.0/{slug}.json
```

Le `slug` utilise est le nom du dossier du plugin detecte dans
`wp-content/plugins`.

## Statuts

### Statuts de mise a jour

- `up_to_date` : la version installee correspond a la version publique ;
- `update_available` : une version publique plus recente existe ;
- `premium_custom` : le plugin n'est pas trouve sur WordPress.org ;
- `unknown` : la comparaison n'est pas possible ;
- `error` : la recuperation distante a echoue ;
- `newer_than_public` : la version installee semble plus recente que la version publique.

### Statuts distants

- `public` : plugin trouve dans le repertoire public ;
- `premium_custom` : plugin absent du repertoire public ou reponse d'erreur WordPress.org ;
- `unknown` : reponse publique incomplete ;
- `error` : erreur HTTP, reseau ou JSON ;
- `cache` / `cache_stale` : indique l'origine de la donnee via `version_source`.

## Cache

Le cache par defaut est :

```text
.wpur-cache/plugin_versions.json
```

Il peut etre change par :

```powershell
$env:WPUR_VERSION_CACHE="C:\chemin\plugin_versions.json"
```

Ou par option CLI :

```powershell
python -m wpur.plugins_ftp --with-latest --version-cache C:\chemin\plugin_versions.json
```

Le cache limite les appels API pendant les tests et les scans repetes. L'option
`--refresh-latest` force une nouvelle recuperation.

## Limites connues

- la detection premium/custom repose sur l'absence du plugin dans le repertoire public ;
- les slugs premium qui reprennent un slug public peuvent produire un resultat public ;
- WPUR ne verifie pas encore les plugins via l'API interne du site WordPress ;
- WPUR ne recupere pas encore les mises a jour de themes ou du coeur WordPress ;
- la comparaison de versions couvre les formats courants, mais ne remplace pas une logique PHP WordPress complete.

## Prochaine etape

Le livrable 2.5 pourra maintenant s'appuyer sur les champs stables :

- `installed_version` ;
- `latest_version` ;
- `update_status` ;
- `remote_status` ;
- `version_checked_at` ;
- `version_source`.
