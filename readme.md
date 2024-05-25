# Projet Pong avec Flask-SocketIO

Ce projet est une implémentation du jeu Pong utilisant Flask et Flask-SocketIO pour gérer la communication en temps réel entre le serveur et les clients.

## Installation

### Prérequis

- Python 3.x
- pip

### Étapes d'installation

1. Clonez le dépôt :

    ```bash
    git clone <URL_DU_DEPOT>
    cd <NOM_DU_DEPOT>
    ```

2. Créez un environnement virtuel et activez-le :

    ```bash
    python -m venv env
    source env/bin/activate   # Sur Windows: env\Scripts\activate
    ```

3. Installez les dépendances nécessaires :

    ```bash
    pip install -r requirements.txt
    ```

### Exécution du projet

1. Lancez l'application Flask :

    ```bash
    python app.py
    ```

2. Ouvrez un navigateur et allez à l'adresse suivante :

    ```
    http://127.0.0.1:5000
    ```

## Fonctionnalités

- **Jeu Pong en temps réel** : Jouez à Pong contre d'autres joueurs en temps réel.
- **Ajout de bots** : Utilisez la commande `!addBot` pour ajouter des bots au jeu.
- **Suppression de bots** : Utilisez la commande `!removeBot` pour supprimer un bot ou `!removeBot all` pour supprimer tous les bots.
- **Réinitialisation du jeu** : Utilisez la commande `!reset` pour réinitialiser le jeu et le remettre à l'état 'idle'.
- **Chat en temps réel** : Communiquez avec d'autres joueurs en temps réel.

## Commandes

- `!start` : Commence le jeu (seulement par l'utilisateur nommé "Xander").
- `!addBot` : Ajoute un bot au jeu (seulement par l'utilisateur nommé "Xander").
- `!removeBot` : Supprime le dernier bot ajouté (seulement par l'utilisateur nommé "Xander").
- `!removeBot all` : Supprime tous les bots (seulement par l'utilisateur nommé "Xander").
- `!reset` : Réinitialise le jeu à l'état 'idle' et réinitialise toutes les variables du jeu.

## Développement

### Structure du projet

- `app.py` : Code principal du serveur Flask et gestion de SocketIO.
- `templates/index.html` : Frontend de l'application.

### Fonctionnement des Threads

Les threads permettent l'exécution simultanée de plusieurs opérations au sein d'un même processus. En Python, les threads sont gérés par le module `threading`. Voici comment ils sont utilisés dans cette application :

1. **Thread Principal** : Gère l'exécution principale de l'application Flask et écoute les connexions SocketIO.
2. **Threads des Bots** : Chaque bot est exécuté dans un thread séparé. Cela permet à chaque bot de prendre des décisions et de bouger de manière indépendante, sans bloquer l'exécution du thread principal ou des autres bots.
3. **Thread du Jeu** : Un thread spécifique gère la boucle de jeu, mettant à jour la position de la balle et vérifiant les collisions.

### Fonctionnement de l'Application

1. **Initialisation de l'Application** :
    - L'application utilise Flask pour le serveur web et Flask-SocketIO pour la communication en temps réel.
    - `app.py` est le fichier principal où le serveur Flask est configuré et où les événements SocketIO sont gérés.

2. **Gestion des Connexions et Déconnexions** :
    - Lorsqu'un joueur se connecte, un objet `Player` est créé et ajouté à l'équipe ayant le moins de joueurs.
    - Lorsqu'un joueur se déconnecte, il est retiré de son équipe et des listes de joueurs.

3. **Commandes Disponibles** :
    - **`!start`** : Lance le jeu, utilisable uniquement par "Xander".
    - **`!addBot`** : Ajoute un bot au jeu, utilisable uniquement par "Xander". Le bot est créé avec un nom unique et exécuté dans un thread séparé.
    - **`!removeBot`** : Supprime le dernier bot ajouté, utilisable uniquement par "Xander".
    - **`!removeBot all`** : Supprime tous les bots, utilisable uniquement par "Xander".
    - **`!reset`** : Réinitialise le jeu et remet l'état à 'idle', utilisable uniquement par "Xander".

4. **Fonctionnement du Jeu** :
    - **Boucle de Jeu** : Le jeu est géré dans un thread séparé qui met à jour la position de la balle, vérifie les collisions et diffuse les états du jeu aux clients toutes les 1/60e de seconde.
    - **Bots** : Les bots suivent la balle de manière simple. Chaque bot vérifie la position de la balle et ajuste sa position en conséquence toutes les 1/30e de seconde.
    - **Communication en Temps Réel** : Flask-SocketIO est utilisé pour émettre les mises à jour du jeu aux clients en temps réel.

### Contributions

Les contributions sont les bienvenues ! Veuillez ouvrir une issue pour discuter de ce que vous aimeriez changer.

## Auteurs

- Breuil Alexandre - Développeur principal
- Flavio Bertollini - Développeur principal
- Reza - Développeur principal
- David Aeschlimann - Développeur principal



## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
