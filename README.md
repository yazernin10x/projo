## ProJo - Application Web de Gestion de Projets Collaboratifs

### Description du Projet

Conception et développement d'une application web complète de gestion de projets collaboratifs, utilisant Django pour le backend et Tailwind CSS/DaisyUI pour une interface moderne et responsive.

### Fonctionnalités Principales

**Gestion des Projets :**

- Création et modification de projets avec titre, description et échéances.
- Attribution de rôles aux membres (Propriétaire, Modérateur, Membre, Invité).
- Système de permissions basé sur les rôles.
- Interface intuitive pour la gestion des membres d'équipe.

**Gestion des Tâches :**

- Création et assignation de tâches aux membres du projet.
- Suivi de l'état d'avancement (À faire, En cours, Terminée).
- Système de commentaires pour la collaboration.
- Gestion des échéances et des priorités.

**Interface Utilisateur :**

- Design moderne et responsive avec Tailwind CSS et DaisyUI.
- Animations et transitions fluides.
- Composants réutilisables et modulaires.

### Aspects Techniques

**Backend :**

- Framework Django 5.1.
- Système d'authentification personnalisé.
- Création de l'api  de l'application avec DRF pour exposer les données. (en cours)
- Tests unitaires
- Commandes personnalisées.
- Filtre personnalisé

**Frontend :**

- HTML5 sémantique.
- Tailwind CSS pour le styling.
- DaisyUI pour les composants.
- JavaScript vanilla pour les interactions.

**Base de Données :**

- Modèles relationnels optimisés.
- PostgreSQL




## Etape d'installation

1. Installer poetry
2. poetry init
3. poetry add django
4. poetry env activate
5. poetry run django-admin startproject core .
6. 

## Envoyer le projet sur github

1. git init
2. git add .
3. git commit -m "Initial commit"
4. git branch -M main
5. git remote add origin git@github.com:yazernin10x/projo.git
6. git push -u origin main

## Commandes utiles

Apres création des models 

1. python manage.py makemigrations
2. python manage.py migrate

Apres création des superusers

python manage.py createsuperuser

Pour lancer le serveur

python manage.py runserver

Pour lancer les tests
exemple:
poetry run python manage.py test apps.users.tests

Pour lancer les tests avec coverage
poetry run python manage.py test apps.users.tests --coverage

Pour lancer les tests avec coverage et générer le rapport
poetry run python manage.py test apps.users.tests --coverage --cov-report html


