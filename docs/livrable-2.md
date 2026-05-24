# Livrable 2 - Version disponible des plugins

## Objectif

Ajouter la version disponible a installer pour chaque plugin detecte.

## Premiere passe

La premiere implementation utilise le slug du dossier plugin pour interroger l'API publique WordPress.org :

```text
https://api.wordpress.org/plugins/info/1.2/
```

Si le plugin existe sur WordPress.org, l'outil recupere sa derniere version publique.

## Donnees ajoutees

Pour chaque plugin :

- version actuellement installee
- version disponible, quand elle est connue
- statut de mise a jour
- source de la version disponible

## Interface

L'interface ajoute :

- une colonne `Version disponible`
- une colonne `Mise a jour`
- un filtre dedie aux statuts de mise a jour
- un resume du nombre de mises a jour detectees

## Statuts de mise a jour

- `A jour` : la version installee correspond a la version disponible
- `A installer` : une version plus recente est disponible
- `Inconnue` : le plugin n'est pas trouve publiquement ou la verification a echoue
- `Version actuelle inconnue` : la version installee n'a pas pu etre lue
- `Non verifie` : statut technique par defaut avant verification

## Limites acceptees pour cette passe

- les plugins premium peuvent rester en version disponible inconnue
- les plugins custom peuvent rester en version disponible inconnue
- un slug local different du slug WordPress.org peut empecher la correspondance
- la comparaison de versions reste volontairement simple

## Suite possible

- ajouter un mapping manuel entre slug local et slug WordPress.org
- conserver les resultats en cache
- gerer les sources premium quand elles exposent une API
- afficher un resume dedie aux plugins a mettre a jour
