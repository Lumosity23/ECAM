# Cours : programmation orientée données (POD) avec ECAM

**Idée** : séparer les données du comportement. Des structures qui ne contiennent
que des champs, et des fonctions libres qui les transforment. Pas d'héritage.

**Règle du cours** : on écrit `class` uniquement pour *déclarer des données*
(jamais de méthode, jamais d'héritage).

**Façon de travailler** : contexte et squelette fournis, tu écris les fonctions
marquées « À TOI DE JOUER », un test te dit si c'est bon, un commit par leçon.

## Programme

| # | Leçon | Tu écris | Dépend du jeu choisi ? |
|---|---|---|---|
| 0 | Prérequis : les 7 exercices du Registry (étages, commandes, ressources) | `add_stage`, `get_resource`, `remove_resource`, `Commands.remove_component` | non |
| 1 | Struct et tableaux : AoS, SoA, tableau structuré, **mesurés** | 4 fonctions | non |
| 2 | Fonctions et état explicite : convertir du code objet en données | un exercice de conversion | non |
| 3 | ECAM comme base de données : requêtes par masque | un système de mouvement en fonction | non |
| 4 | `add_system` et `App` acceptent de simples fonctions | un changement dans ECAM | non |
| 5 | Composant `Color` : rendu piloté par les données | un changement de shader | non |
| 6 | Le jeu : entités et niveau lu depuis des chaînes | le spawn | **oui** |
| 7 | Entrée, intention (donnée), système | le contrôle du joueur | oui |
| 8 | Collisions et `despawn` différé | la logique de rebond / d'interaction | oui |
| 9 | Ressources et machine à états | score, vies, états | oui |
| 10 | Score et vies sans texte, niveaux en JSON, meilleur score sauvegardé | sauvegarde | oui |
| 11 | Bilan : mesurer, et savoir quand l'objet vaut mieux | réflexion écrite | non |

**Jeu fil rouge : casse-briques (Breakout), rectangles unis.**

Choix volontaire : le Frogger du projet noté est développé séparément, en pygame et pygame_gui, sans lien avec ce cours. Un Frogger en ECAM pourra venir après la défense.

## Leçons faites

- [x] Leçon 1 : `course/lecon_01_structs_et_tableaux.py`
- [ ] Leçon 2 : `course/lecon_02_classe_vers_donnees.py`
