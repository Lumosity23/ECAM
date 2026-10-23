# Dictionnaires et classes avec le thème « Crossy Road »

Dans Crossy Road, un personnage saute de rangée en rangée. Chaque rangée (« voie »)
est de l'herbe, une route avec des véhicules, une rivière... On ramasse des pièces, et
avec ces pièces on débloque de nouveaux personnages.

C'est un jeu **voisin** de celui du projet : tu y travailles les mêmes outils (dictionnaires,
classes, listes d'objets), sans refaire le projet lui-même. À la fin de chaque partie, un
**« pont vers le projet »** te demande d'appliquer ce que tu viens d'apprendre à TON jeu.
Ces questions-là sont ouvertes : il n'y a pas de corrigé, c'est à toi (et à ton binôme)
de décider.

## Comment travailler

1. **Prédis avant d'exécuter** : écris d'abord ce que tu crois que ça va afficher.
2. **Un exercice, un fichier.**
3. **Après chaque exercice, explique à voix haute** (« Explique-moi »). Si tu n'y arrives pas,
   c'est que ce n'est pas encore compris.
4. Les résultats attendus servent à te vérifier. S'ils diffèrent, cherche pourquoi avant de corriger.
5. Les commentaires décrivent l'**intention** d'un bloc, pas chaque ligne.

Difficulté : ★ facile, ★★ moyen, ★★★ demande de la réflexion.

---

# PARTIE 1 : LES DICTIONNAIRES

## K1 : Une voie, c'est un dictionnaire ★

    voie = {"type": "route", "vitesse": 3, "sens": "droite", "nb_vehicules": 4}

1. Affiche le type de la voie, puis sa vitesse.
2. La route est en travaux : sa vitesse passe à 1.
3. Ajoute une information `"largeur"` valant 2.
4. Affiche `"couleur"` **sans que le programme plante** (valeur par défaut `"gris"`).

*Explique-moi* : quelle différence entre `voie["couleur"]` et `voie.get("couleur", "gris")` ?

## K2 : Une liste de voies ★★

    terrain = [
        {"type": "herbe",   "vitesse": 0},
        {"type": "route",   "vitesse": 3},
        {"type": "route",   "vitesse": 5},
        {"type": "riviere", "vitesse": 2},
        {"type": "route",   "vitesse": 1},
        {"type": "herbe",   "vitesse": 0},
    ]

1. Compte combien il y a de voies de **chaque type** (avec un dictionnaire).
2. Trouve la **position** (l'index) de la voie la plus rapide.
3. Calcule la **vitesse moyenne des routes** uniquement.

Résultats attendus : herbe 2, route 3, rivière 1 ; la plus rapide est à l'index 2 ;
la moyenne des routes vaut 3.0.

*Explique-moi* : pourquoi faut-il traiter différemment « la première fois qu'on voit un
type » et « les fois suivantes » quand on compte ?

## K3 : Un catalogue de véhicules (dictionnaire de dictionnaires) ★★

    catalogue = {
        "voiture": {"vitesse": 4, "longueur": 2},
        "camion":  {"vitesse": 2, "longueur": 4},
        "moto":    {"vitesse": 6, "longueur": 1},
    }

1. Affiche la longueur du camion.
2. Affiche les véhicules **plus rapides que 3**.
3. Affiche les noms **du plus long au plus court**.
4. Une voie contient `["voiture", "camion", "moto", "voiture"]` : calcule la **longueur
   totale** des véhicules sur cette voie.

Résultats attendus : (2) voiture et moto ; (3) camion, voiture, moto ; (4) 9.

*Explique-moi* : dans `catalogue["camion"]["longueur"]`, que représente chaque paire de crochets ?

## K4 : La boutique de personnages ★★

    prix = {"poulet": 0, "lapin": 50, "grenouille": 100, "robot": 250}

Le joueur a des pièces et un **set** de personnages qu'il possède déjà (au départ
`{"poulet"}`). Écris une fonction `debloquer(pieces, possedes, nom)` qui :

- refuse si le personnage n'existe pas,
- refuse s'il est déjà possédé,
- refuse si le joueur n'a pas assez de pièces,
- sinon retire le prix, ajoute le personnage au set, et renvoie les pièces restantes.

Test avec 120 pièces : `lapin` donne 70 pièces ; redemander `lapin` est refusé (déjà
possédé) ; `dragon` est refusé (inconnu) ; `grenouille` avec les 70 pièces restantes est
refusée (trop cher).

*Explique-moi* : pourquoi un **set** pour les personnages possédés et un **dictionnaire**
pour les prix ? Ta fonction modifie le set qu'on lui donne : l'appelant le voit-il ?

## K5 : Des voies qui se ressemblent un peu trop ★★★ (chasse au bug)

    voies = [{"vitesse": 1}] * 3
    voies[0]["vitesse"] = 9
    print(voies)

1. **Prédis** ce qui s'affiche.
2. Exécute. Explique l'écart : combien de dictionnaires y a-t-il vraiment ?
3. Comment fabriquer **trois** vraies voies indépendantes ? (cherche les
   *compréhensions de liste*.)

*Explique-moi* : multiplier une liste par 3 copie-t-il les éléments, ou répète-t-il la
**même référence** ?

## K6 : Les états d'un jeu avec un dictionnaire ★★★

    transitions = {
        "menu":      {"jouer": "jeu"},
        "jeu":       {"pause": "pause", "fin": "ecran_fin"},
        "pause":     {"reprendre": "jeu", "quitter": "menu"},
        "ecran_fin": {"rejouer": "jeu", "menu": "menu"},
    }

Écris `changer_etat(etat, evenement)` qui renvoie le **nouvel état**, ou l'état actuel
(avec un message) si l'événement n'est pas permis dans cet état.

Tests : `("menu", "jouer")` donne `"jeu"` ; `("jeu", "pause")` donne `"pause"` ;
`("menu", "pause")` reste `"menu"` avec un message.

*Explique-moi* : comment cette table remplace-t-elle une grande suite de `if` ?

## 🌉 Pont vers le projet n°1 (à faire seule, avec ton binôme)

Sur papier, **sans écrire de code** :

1. Pour chaque « chose » de votre jeu (la grenouille, une voie, un véhicule, un radeau, la
   partie en cours), liste **les informations à retenir**.
2. Pour chacune : **dictionnaire ou classe ?** Écris une phrase pour justifier.
3. Quels **états** a votre jeu, et quels événements les font passer de l'un à l'autre ?

Comparez vos réponses : si vous n'êtes pas d'accord, c'est une bonne discussion à avoir
*avant* de coder.

---

# PARTIE 2 : LES CLASSES

## K7 : Un véhicule qui roule ★★

Crée une classe `Voiture` avec une position `x`, une `vitesse` (en cases par seconde,
négative si elle va vers la gauche) et une `longueur`. Ajoute une méthode `avancer(dt)`
qui déplace la voiture de `vitesse × dt`.

Tests : `x = 0`, vitesse 3, `avancer(2.0)` donne `x = 6.0` ; `x = 10`, vitesse -4,
`avancer(1.5)` donne `x = 4.0`.

*Explique-moi* : pourquoi multiplier la vitesse par `dt` ? Que représente `dt` ?

## K8 : Une voie qui contient des véhicules (composition) ★★★

Crée une classe `Voie` qui contient une **liste de `Voiture`**, avec :

- une méthode pour ajouter une voiture,
- `avancer_tout(dt)` qui fait avancer **toutes** les voitures de la voie,
- `longueur_totale()` qui additionne les longueurs de ses voitures.

Test : une voie avec des voitures de longueur 2, 4 et 1 donne une longueur totale de 7.

*Explique-moi* : dans `avancer_tout`, qui appelle `avancer` ? Sur quel objet ?

## K9 : Attribut de classe contre attribut d'instance ★★★ (chasse au bug)

    class Voie:
        vehicules = []

    a = Voie()
    b = Voie()
    a.vehicules.append("camion")
    print(b.vehicules)

1. **Prédis** ce que contient `b.vehicules`.
2. Exécute, explique. Où se trouve vraiment la liste ?
3. Corrige la classe pour que chaque voie ait **sa propre** liste.
4. Donne un cas où un attribut de classe est **voulu** (par exemple compter le nombre de
   voies créées).

## K10 : Héritage ou dictionnaire ? ★★★ (si l'héritage a été vu)

Crée des classes `Voiture`, `Camion`, `Moto` qui héritent d'une classe `Vehicule`, avec
des valeurs par défaut différentes (longueur, vitesse).

Ensuite, **par écrit** : aurais-tu pu faire la même chose avec **une seule** classe et le
`catalogue` de l'exercice K3 ? Compare les deux solutions (quantité de code, facilité à
ajouter un nouveau véhicule, lisibilité).

## K11 : Le même véhicule, deux façons ★★★ (à comparer)

Représente un véhicule **comme un dictionnaire** avec des fonctions libres, puis **comme une
classe** avec des méthodes. Écris la même petite scène avec les deux.

Compare par écrit : lequel est le plus lisible ? lequel est le plus simple à sauvegarder dans
un fichier ? lequel résiste le mieux à une faute de frappe dans un nom de champ ?

## 🌉 Pont vers le projet n°2 (à faire seule, avec ton binôme)

**Sans écrire de code**, dessine sur papier un petit schéma de **vos classes** : pour chacune,
son nom, ses attributs, ses méthodes, et **qui contient qui** (comme `Voie` contient des
`Voiture`). Puis vérifiez ensemble : chaque information du projet a-t-elle une place ?
Quelqu'un pourrait-il expliquer ce schéma à l'enseignant ?

---

# PARTIE 3 : DICTIONNAIRES ET CLASSES ENSEMBLE

## K12 : Ramasser des pièces ★★★

    pieces = [
        {"x": 1, "prise": True},
        {"x": 2, "prise": True},
        {"x": 3, "prise": False},
        {"x": 4, "prise": True},
    ]

On veut **retirer de la liste** les pièces déjà prises.

1. Essaie d'abord de les retirer **pendant** que tu parcours la liste avec `for`.
2. **Prédis** ce qui restera, puis exécute. Surprise : une pièce prise est restée. Pourquoi ?
3. Trouve une façon propre de faire.

Résultat observé avec la version naïve : il reste les pièces `x = 2` (prise !) et `x = 3`.

*Explique-moi* : que se passe-t-il quand on supprime un élément d'une liste qu'on est en train de parcourir ?

## K13 : Sauvegarder un profil ★★★ (fonctions inconnues à étudier)

Un profil contient des pièces et les personnages débloqués :

    profil = {"pieces": 70, "personnages": ["poulet", "lapin"]}

1. Écris ce profil dans un **fichier**, puis recharge-le.
2. Que devient un `set` si tu essaies de l'écrire directement ? Pourquoi ? (Teste, lis l'erreur.)

Tu devras étudier le module `json` (`json.dump`, `json.load`). Prépare une fiche : pour
chaque fonction, ce qu'elle fait, ce qu'elle reçoit, ce qu'elle renvoie.

## K14 : Mini-projet « Le garage des personnages » en texte ★★★

Sans aucune bibliothèque graphique : un programme avec une boucle qui lit des commandes
(`pieces`, `acheter <nom>`, `equiper <nom>`, `collection`, `quitter`).

- les prix dans un **dictionnaire**,
- les personnages possédés dans un **set**,
- le joueur (pièces, personnage équipé) dans une **classe**,
- le profil sauvegardé et rechargé au démarrage.

Réussite : le programme ne plante jamais sur une commande inconnue ; chaque fonction et chaque
méthode peut être expliquée par toi.

## 🌉 Pont vers le projet n°3 (à faire seule, avec ton binôme)

Relis le **cahier des charges** ligne par ligne. Pour chaque exigence, écris :

- **quelle donnée** doit être mémorisée,
- **où** elle sera stockée (dans quel dictionnaire ou quelle classe),
- **qui la modifie** et **qui la lit**.

Si une exigence vous laisse sans réponse, notez-la : c'est une question pour la prochaine séance.

---

# POUR LE TUTEUR

- **K2 et K4** : elle doit distinguer « première fois » et « fois suivantes », et expliquer le
  choix set contre dictionnaire.
- **K5 et K9** : ce sont les deux pièges qui reviennent le plus. Elle doit dire « même
  référence, pas des copies », avec ses mots.
- **K7** : elle comprend que `dt` rend le mouvement indépendant du nombre d'images par seconde.
- **K12** : elle comprend que modifier une liste qu'on parcourt saute des éléments.
- **Les ponts** : ne les corrige pas à sa place. Écoute ses choix, pose des questions
  (« qui modifie cette donnée ? »), laisse-la défendre sa solution. C'est le meilleur
  entraînement à la défense orale.

Trois niveaux d'indice : une **question**, puis une **direction**, puis (seulement après un
vrai effort) **presque la réponse**, jamais le code complet. Termine chaque séance par une
**variante** : « change ton code pour qu'il fasse X à la place ».
