# Mathfinder

**Mathfinder** est une application à destination des chercheurs, étudiants et analystes qui souhaitent découvrir les relations mathématiques qui lient les différentes variables de leurs données.

## Comment fonctionne Mathfinder ?

Mathfinder utilise un [modèle de régression symbolique](https://pypi.org/project/symbolic-learn/) pour trouver une formule mathématique qui caractérise au mieux les données fournies.

## Installation de Mathfinder
Voici la procédure à suivre pour installer Mathfinder sur un serveur. Nous partirons ici du principe que Python et pip sont déjà installés.
- Clonez ce dépôt
- Ouvrez un terminal dans le dossier où se trouve le code, et exécutez les commandes suivantes :
```
pip install pipenv
pipenv install .
```
- Vous pouvez ensuite installer MySQL :
```
sudo apt update
sudo apt install mysql-server
```
Si votre serveur utilise Windows, [téléchargez l'installeur de MySQL](https://dev.mysql.com/doc/refman/8.3/en/windows-installation.html) à la place. Lorsque MySQL est installé, créez une base de données puis exécutez cette commande :
```
mysql votre_bdd < mysql_dump.sql
```
Ceci créera dans votre base de données une table Models dont Mathfinder aura besoin pour fonctionner.
- Lancez le serveur MLflow :
```
pipenv run mlflow server --host 127.0.0.1 --port 8080
```
- Dans un autre terminal, exécutez l'application Mathfinder :
```
export MYSQL_USER="<votre nom d'utilisateur sur MySQL>"
export MYSQL_PWD="<votre mot de passe sur MySQL>"
export MYSQL_DB_NAME="<le nom de la base de données que vous avez créée sur MySQL>"
pipenv run streamlit run Mathfinder.py
```
- Enfin, exécutez ces commandes dans un nouveau terminal lorsque vous voulez lancer le script de monitorage :
```
export MYSQL_USER="<votre nom d'utilisateur sur MySQL>"
export MYSQL_PWD="<votre mot de passe sur MySQL>"
export MYSQL_DB_NAME="<le nom de la base de données que vous avez créée sur MySQL>"
export SMTP_SERVER="<l'adresse de votre serveur SMTP>"
export SMTP_LOGIN="<votre login sur ce serveur>"
export SMTP_PWD="<votre mot de passe>"
pipenv run python monitoring.py
```
Mathfinder est maintenant opérationnel sur votre serveur ! Vous pouvez accéder à l'application Mathfinder en vous rendant à l'adresse http://localhost:8501 sur votre navigateur internet (remplacer "localhost" par l'adresse IP du serveur pour y accéder depuis un autre ordinateur du réseau). Le tableau de bord de MLflow est quant à lui disponible à l'adresse http://127.0.0.1:8080.

## Signaler un bug
Pour signaler un bug, vous pouvez suivre cette procédure :
1. Cliquez sur l’onglet "Tickets" en haut de cette page
2. Cliquez sur "Nouveau ticket"
3. Entrez un titre qui résume très brièvement le problème que vous avez rencontré. Puis entrez une description qui détaille le plus précisément possible les éléments suivants :
    - une description du problème
    - une capture d’écran qui montre le problème, si possible
    - une suite d’étapes à suivre pour reproduire le problème
4. Validez la création du ticket.