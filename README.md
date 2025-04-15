# CPTS - IA accès aux soins

## Description

Le projet de la Communauté Professionnelle Territoriale de Santé Entre Cèze et Gardon en Cevennes (CPTS-ECEGEC) en partenariat avec ISIS ingénieurs vise à développer une solution innovante basée sur la reconnaissance vocale (Speech-to-Text) adaptée aux besoins spécifiques des professionnels de santé. En nous inspirant de modèles d’intelligence artificielle open-source comme Whisper et DeepSpeech, nous concevons un outil performant, personnalisable et conforme aux réglementations telles que le RGPD.
Cette solution sera optimisée pour des scénarios complexes et inclura des fonctionnalités avancées, comme la transcription précise de termes médicaux lors d'une consultation de médecine générale, permettant ainsi la génération automatique de comptes rendus. Nous mettons également l’accent sur une interface utilisateur intuitive et un environnement technique robuste, garantissant un déploiement facile dans les structures de santé.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

* **Python 3.x** ([https://www.python.org/downloads/](https://www.python.org/downloads/))
* **pip** (normalement installé avec Python)
* **Node.js** ([https://nodejs.org/](https://nodejs.org/))
* **npm** ou **yarn** (normalement installé avec Node.js)

## Installation

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/valentinISIS/PTUT_Fie4
    cd PTUT_Fie4
    ```

## Lancement du Backend (Flask Python)

1.  **Se rendre dans le dossier backend :**
    ```bash
    cd backend
    ```

2.  **Créer et activer un environnement virtuel (recommandé) :**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Linux/macOS
    venv\Scripts\activate  # Sur Windows
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancer l'application Flask :**
    ```bash
    python main.py  # ou le nom de votre fichier principal Flask
    ```

    Vous devriez voir un message indiquant que le serveur Flask est en cours d'exécution (par exemple, sur `http://127.0.0.1:5000/`).

## Lancement du Frontend (Vue.js)

1.  **Se rendre dans le dossier frontend :**
    ```bash
    cd frontend
    ```

2.  **Installer les dépendances :**
    * Avec npm :
        ```bash
        npm install
        ```
    * Avec yarn :
        ```bash
        yarn install
        ```

3.  **Lancer l'application Vue.js en mode développement :**
    * Avec npm :
        ```bash
        npm run serve
        ```
    * Avec yarn :
        ```bash
        yarn serve
        ```

    L'application Vue.js devrait se lancer automatiquement dans votre navigateur (généralement sur `http://localhost:8080/`).
