# Dictionnaires et classes : une série d'exercices sur le thème d'un jeu de donjon

Thème : un jeu d'aventure générique (héros, monstres, objets, salles). Volontairement
**sans lien avec un jeu précis**, pour s'entraîner à une compétence, puis l'appliquer
ensuite à son propre projet.

## Comment travailler (à lire avant de commencer)

1. **Prédis avant d'exécuter.** Pour chaque exercice qui affiche quelque chose, écris
   d'abord sur papier ce que tu crois qu'il va afficher. Compare ensuite.
2. **Une seule fenêtre à la fois** : un exercice, un fichier. Ne mélange pas.
3. **Après chaque exercice, réponds à voix haute** à la question « Explique-moi ».
   Si tu ne peux pas l'expliquer, tu ne l'as pas encore compris : refais-le autrement.
4. **Les résultats attendus** servent à te vérifier. Si ton résultat diffère, ne corrige
   pas au hasard : cherche *pourquoi* il diffère.
5. Les commentaires décrivent l'**intention** d'un bloc (« je cherche le monstre le plus
   fort »), jamais la traduction ligne à ligne.

Difficulté : ★ facile, ★★ moyen, ★★★ demande de la réflexion.

---

# PARTIE 1 : LES DICTIONNAIRES

On représente le héros ainsi :

    heros = {"nom": "Aria", "pv": 30, "force": 8, "agilite": 5}

## D1 : Lire un dictionnaire ★

Avec le dictionnaire `heros` ci-dessus :

1. Affiche la force du héros.
2. Affiche sa magie. **Que se passe-t-il ?** Note le nom exact de l'erreur.
3. Affiche sa magie sans que le programme plante, en affichant `0` si la stat n'existe pas.
4. Teste si la clé `"agilite"` existe, puis si la clé `"chance"` existe.

*Explique-moi* : quelle est la différence entre `heros["magie"]` et `heros.get("magie", 0)` ?

## D2 : Modifier un dictionnaire ★

Le héros monte de niveau.

1. Sa force passe de 8 à 10.
2. Il gagne une nouvelle stat `"magie"` valant 3.
3. Il perd sa stat `"agilite"` (retire-la complètement du dictionnaire).
4. Affiche le dictionnaire final.

Résultat attendu (l'ordre peut varier) : `nom: Aria, pv: 30, force: 10, magie: 3`.

*Explique-moi* : modifier une valeur existante et en ajouter une nouvelle, c'est la même
syntaxe. Pourquoi ?

## D3 : Parcourir un dictionnaire ★★

1. Affiche une fiche de personnage, une ligne par stat, au format `force : 10`.
2. Calcule la somme de **toutes les stats numériques** (ignore le nom).
3. Trouve **le nom de la stat la plus élevée**.

Avec `{"nom": "Aria", "pv": 30, "force": 10, "magie": 3}` : la somme vaut 43 et la
stat la plus élevée est `pv`.

*Explique-moi* : à quoi servent `.keys()`, `.values()` et `.items()` ? Dans quel cas
choisis-tu chacun ?

## D4 : Compter avec un dictionnaire ★★

Après un combat, le héros a ramassé ce butin :

    butin = ["potion", "épée", "potion", "clé", "potion", "épée"]

Construis un dictionnaire qui donne **combien d'exemplaires de chaque objet** il possède.
Fais-le d'abord à la main avec une boucle (sans bibliothèque).

Résultat attendu : `potion: 3, épée: 2, clé: 1`.

*Bonus* : cherche ce que fait `collections.Counter`. Pourquoi est-il pratique ?

*Explique-moi* : que se passe-t-il la **première fois** que tu rencontres un objet ? Et
les fois suivantes ? Pourquoi faut-il traiter ces deux cas ?

## D5 : Dictionnaire de dictionnaires ★★

Le bestiaire du jeu :

    bestiaire = {
        "gobelin": {"pv": 12, "attaque": 3},
        "orc":     {"pv": 30, "attaque": 7},
        "dragon":  {"pv": 120, "attaque": 25},
    }

1. Affiche les PV de l'orc.
2. Affiche le nom de tous les monstres qui ont **plus de 20 PV**.
3. Affiche les noms des monstres **du plus fort au plus faible** (selon l'attaque).
4. Ajoute un monstre `"squelette"` avec 15 PV et 5 d'attaque.

Résultats attendus : (2) orc et dragon, (3) dragon, orc, gobelin.

*Explique-moi* : dans `bestiaire["orc"]["pv"]`, que représente chaque paire de crochets ?

## D6 : Un dictionnaire comme table de prix ★★

La boutique du village :

    boutique = {"potion": 5, "épée": 40, "bouclier": 25}

Écris une **fonction** `acheter(or_du_heros, inventaire, objet)` qui :

- refuse si l'objet n'existe pas dans la boutique (message clair),
- refuse si le héros n'a pas assez d'or (message clair),
- sinon retire le prix de l'or, ajoute l'objet à l'inventaire, et renvoie le nouvel or.

Test : avec 30 pièces d'or, acheter une potion donne 25 pièces et ajoute la potion ;
acheter une épée est refusé ; acheter un `"arc"` est refusé.

*Explique-moi* : ta fonction modifie l'inventaire qu'on lui donne. Est-ce que l'appelant
voit le changement ? Pourquoi ?

## D7 : Quelle structure choisir ? ★★ (à discuter)

Pour chacune de ces données, choisis une **liste**, un **dictionnaire** ou un **set**, et
justifie en une phrase :

a) les objets possédés par le héros, avec leur quantité,
b) les noms des salles déjà visitées (sans doublon, savoir vite si une salle est visitée),
c) la file des monstres qui vont arriver, dans l'ordre,
d) les caractéristiques d'un monstre,
e) les touches du clavier actuellement enfoncées.

Il peut y avoir plusieurs bonnes réponses : l'important est l'argument.

## D8 : Le piège de la copie ★★★ (chasse au bug)

    heros_a = {"nom": "Aria", "pv": 30}
    heros_b = heros_a
    heros_b["pv"] = 10
    print(heros_a["pv"])

1. **Prédis** ce qui s'affiche.
2. Exécute, compare. Surpris ?
3. Explique pourquoi (sans te cacher derrière « c'est comme ça »).
4. Comment obtenir un **vrai** deuxième héros indépendant ? (cherche `.copy()`.)
5. Et si le dictionnaire contient un autre dictionnaire à l'intérieur ? `.copy()`
   suffit-il ? Teste, et cherche `copy.deepcopy`.

*Explique-moi* : un dictionnaire est-il copié ou **partagé** quand on l'affecte à une
autre variable ?

## D9 : Naviguer dans un donjon ★★★

    donjon = {
        "hall":    {"nord": "cuisine", "est": "salon"},
        "cuisine": {"sud": "hall"},
        "salon":   {"ouest": "hall"},
    }

Écris une fonction `aller(salle_actuelle, direction)` qui renvoie la **nouvelle salle**,
ou la salle actuelle (avec un message) si la direction est impossible.

Tests : `aller("hall", "nord")` donne `"cuisine"` ; `aller("cuisine", "est")` reste
dans `"cuisine"` avec un message.

Ensuite, fais un petit programme qui demande une direction au clavier en boucle jusqu'à
ce que l'utilisateur écrive `quitter`.

---

# PARTIE 2 : LES CLASSES

## C1 : Une première classe ★

Crée une classe `Monstre` avec un nom, des points de vie (`pv`) et une valeur d'attaque.

1. Crée trois monstres différents.
2. Affiche le nom et les PV de chacun.
3. Change les PV d'**un seul** et vérifie que les deux autres n'ont pas bougé.

*Explique-moi* : quelle est la différence entre une **classe** et une **instance** ?
À quoi sert `self` ?

## C2 : Des méthodes ★★

Ajoute à `Monstre` :

- une méthode `subir_degats(n)` qui retire `n` PV **sans jamais descendre sous 0**,
- une méthode `est_vivant()` qui renvoie vrai ou faux.

Test : un monstre à 10 PV, `subir_degats(4)` donne 6 PV et `est_vivant()` vrai ;
ensuite `subir_degats(20)` donne **0** PV (pas -14) et `est_vivant()` faux.

*Explique-moi* : pourquoi `est_vivant` n'affiche rien mais **renvoie** une valeur ?
Quelle est la différence entre `print` et `return` ?

## C3 : Construire proprement ★★

1. Donne des **valeurs par défaut** (par exemple 10 PV, 2 d'attaque) pour qu'on puisse
   créer un monstre en n'indiquant que son nom.
2. Ajoute une méthode spéciale pour que `print(monstre)` affiche un texte lisible
   (par exemple `Gobelin (12 PV)`). Cherche `__str__`.

*Explique-moi* : que se passe-t-il quand on écrit `Monstre("Orc")` ? Quelle méthode est
appelée en premier ?

## C4 : Faire interagir deux objets ★★★

Crée une classe `Heros` (nom, PV, force) avec une méthode `attaquer(cible)` qui inflige
des dégâts égaux à sa force. Fais ensuite un **combat au tour par tour** : le héros
attaque, puis, si le monstre est encore vivant, il riposte, jusqu'à la mort de l'un des deux.

Test : héros 20 PV et 5 de force contre un gobelin de 12 PV qui attaque à 3 → le héros
gagne en **3 tours** avec **14 PV** restants.

*Explique-moi* : dans `heros.attaquer(gobelin)`, quel objet est `self` et quel objet est
`cible` ? Qui est modifié ?

## C5 : Attribut de classe contre attribut d'instance ★★★ (chasse au bug)

Un élève écrit :

    class Monstre:
        butin = []
        def __init__(self, nom):
            self.nom = nom

    a = Monstre("Gobelin")
    b = Monstre("Orc")
    a.butin.append("potion")
    print(b.butin)

1. **Prédis** ce qui s'affiche pour `b.butin`.
2. Exécute. Explique l'écart.
3. Corrige la classe pour que chaque monstre ait **son propre** butin.
4. Dans quel cas un attribut de classe est-il **voulu** ? (exemple : un compteur du
   nombre de monstres créés.)

## C6 : Composition : un objet qui en contient d'autres ★★★

- Crée une classe `Arme` (nom, dégâts).
- Le `Heros` peut **équiper** une arme (ou aucune).
- Ses dégâts deviennent : sa force **plus** les dégâts de l'arme équipée.
- Le héros possède aussi un **inventaire** (un dictionnaire objet → quantité).

Test : un héros de force 8 avec une épée de 6 dégâts inflige **14**. Sans arme, il
inflige 8. Que se passe-t-il s'il change d'arme au milieu du combat ?

*Explique-moi* : pourquoi l'arme est une **classe** et l'inventaire un **dictionnaire** ?

## C7 : L'héritage (si vu en cours) ★★★

Crée deux classes qui héritent de `Monstre` : un `Gobelin` (rapide, peu de PV) et un
`Dragon` (beaucoup de PV, souffle de feu en plus de l'attaque normale).

Discussion à mener **par écrit** : aurais-tu pu obtenir le même résultat avec **un seul**
`Monstre` et un dictionnaire de paramètres ? Quels sont les avantages et les
inconvénients de chaque approche ?

## C8 : Le même objet, deux façons ★★★ (à comparer)

Représente un monstre **d'abord comme un dictionnaire** avec des fonctions libres
(`subir_degats(monstre, n)`), **puis comme une classe** avec des méthodes. Écris la même
petite scène avec les deux.

Compare par écrit : lequel est le plus lisible ? le plus facile à sauvegarder dans un
fichier ? le plus sûr contre les fautes de frappe dans un nom de champ ?

---

# PARTIE 3 : DICTIONNAIRES ET CLASSES ENSEMBLE

## B1 : Un monde rempli d'objets ★★★

Crée une liste (ou un dictionnaire) de plusieurs monstres. Fais **perdre des PV** à tous
d'un coup, puis **retire de la liste** ceux qui sont morts.

**Piège** : essaie d'abord de retirer les monstres morts *pendant* que tu parcours la
liste avec `for`. Observe ce qui se passe (des monstres sont sautés). Explique pourquoi,
puis trouve une façon propre de le faire.

## B2 : Sauvegarder et recharger un personnage ★★★ (fonctions inconnues à étudier)

1. Écris une fonction qui transforme un `Heros` en **dictionnaire** (ses données).
2. Écris celle qui fait l'inverse : dictionnaire vers `Heros`.
3. Écris le dictionnaire dans un **fichier**, puis recharge-le.

Tu devras chercher dans la documentation le module `json` (`json.dump`, `json.load`).
Prépare une fiche : pour chaque fonction, ce qu'elle fait, ce qu'elle reçoit, ce qu'elle
renvoie.

*Explique-moi* : pourquoi ne peut-on pas écrire directement un objet `Heros` dans un
fichier JSON ?

## B3 : Mini-projet : un donjon en texte ★★★

Sans aucune bibliothèque graphique, assemble tout :

- les salles dans un **dictionnaire** (partie D9),
- un `Heros` et des `Monstre` en **classes**,
- un inventaire en **dictionnaire**,
- une boucle de jeu qui lit des commandes : `aller nord`, `attaquer`, `ramasser`,
  `inventaire`, `quitter`.

Critères de réussite : le programme ne plante jamais sur une commande inconnue ; on peut
terminer une partie ; chaque fonction et chaque méthode peut être expliquée par toi.

---

# POUR LE TUTEUR : points à vérifier à chaque exercice

- **D1** : elle sait nommer `KeyError` et expliquer pourquoi `.get` évite le plantage.
- **D4** : elle distingue clairement « première fois » et « fois suivantes ».
- **D6** : elle comprend qu'un dictionnaire passé en argument est **partagé**, pas copié.
- **D8** : elle sait dire « c'est le même objet, deux noms ». Ne te contente pas de « il
  faut faire `.copy()` ».
- **C2** : elle différencie `print` et `return` avec ses propres mots.
- **C4** : elle repère `self` et `cible` sans hésiter.
- **C5** : elle sait quand un attribut de classe est voulu et quand c'est un bug.
- **B1** : elle comprend pourquoi modifier une liste pendant qu'on la parcourt saute des
  éléments.

## Comment donner un indice (trois niveaux)

1. **Une question** : « Que contient ta variable à cette ligne ? »
2. **Une direction** : « Regarde ce que renvoie cette fonction. »
3. **Presque la réponse** : seulement après un vrai effort, et jamais le code complet.

## Format d'une séance (30 à 40 min)

5 min de rappel (elle explique l'exercice précédent) → 20 min sur un nouvel exercice
(elle tape, tu guides) → 5 min de « Explique-moi » → 5 min de variante (« change ton code
pour qu'il fasse X à la place »). La variante est le meilleur test de compréhension.
