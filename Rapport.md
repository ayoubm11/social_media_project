# Rapport Technique - Projet Social Media

## Table des matières

1. [Description du Projet](#description-du-projet)
2. [Technologies Utilisées](#technologies-utilisées)
3. [Architecture du Projet](#architecture-du-projet)
4. [Diagrammes UML](#diagrammes-uml)
5. [Diagrammes de Fonctionnement](#diagrammes-de-fonctionnement)
6. [Fonctionnalités Détaillées](#fonctionnalités-détaillées)
7. [Structure des Données](#structure-des-données)

---

## Description du Projet

### Vue d'ensemble

**SocialApp** est une application web de réseau social développée avec Django. Elle permet aux utilisateurs de créer un profil, publier du contenu (texte, images, vidéos), interagir avec les publications (likes, commentaires, partages), suivre d'autres utilisateurs, communiquer en temps réel via un système de chat, et recevoir des notifications en temps réel.

### Objectifs

- Permettre aux utilisateurs de créer et gérer leur profil
- Faciliter le partage de contenu multimédia
- Encourager les interactions sociales (likes, commentaires, partages)
- Permettre la communication en temps réel entre utilisateurs
- Notifier les utilisateurs des activités pertinentes

### Caractéristiques principales

- **Authentification** : Inscription, connexion et gestion de profil
- **Publications** : Création, modification et suppression de posts
- **Interactions** : Système de likes, commentaires et partages
- **Réseau social** : Suivre/désabonner, suggestions d'amis
- **Messagerie** : Chat en temps réel avec WebSockets
- **Notifications** : Système de notifications en temps réel
- **API REST** : API complète pour intégration externe

---

## Technologies Utilisées

### Backend

#### Framework principal
- **Django 5.2.8** : Framework web Python pour le développement backend
- **Django REST Framework 3.15.2** : API REST pour l'intégration frontend/backend
- **ASGI/Daphne** : Serveur ASGI pour gérer les WebSockets et requêtes asynchrones

#### Base de données
- **SQLite3** : Base de données relationnelle pour le développement
- **Django ORM** : Couche d'abstraction pour la gestion de la base de données

#### Temps réel et communication
- **Django Channels 4.3.2** : Gestion des WebSockets pour le chat en temps réel
- **Redis/Channels-Redis** : Backend de channels pour la distribution des messages

#### Autres bibliothèques
- **Pillow 11.0.0** : Traitement d'images pour les photos de profil et publications
- **django-crispy-forms 2.3** : Rendering de formulaires stylisés
- **crispy-bootstrap5 2025.6** : Intégration Bootstrap 5 avec crispy-forms
- **django-cors-headers 4.6.0** : Gestion CORS pour l'API
- **django-filter 24.3** : Filtrage avancé pour l'API REST
- **python-decouple 3.8** : Gestion des variables d'environnement

### Frontend

- **Bootstrap 5.3.0** : Framework CSS pour l'interface utilisateur
- **Bootstrap Icons 1.11.0** : Bibliothèque d'icônes
- **JavaScript (Vanilla)** : Gestion des interactions côté client
- **WebSocket API** : Communication bidirectionnelle pour le chat

### Outils de développement

- **Python 3.x** : Langage de programmation principal
- **Git** : Contrôle de version
- **SQLite** : Base de données de développement

---

## Architecture du Projet

### Structure des applications Django

```
social_media_project/
│
├── apps/
│   ├── users/          # Gestion des utilisateurs et profils
│   ├── posts/          # Publications, commentaires et likes
│   ├── social/         # Relations sociales, notifications, chat
│   └── api/            # API REST pour intégration externe
│
├── social_media_project/
│   ├── settings.py     # Configuration du projet
│   ├── urls.py         # URLs principales
│   ├── asgi.py         # Configuration ASGI pour WebSockets
│   └── wsgi.py         # Configuration WSGI traditionnelle
│
├── templates/          # Templates HTML
│   ├── base.html       # Template de base
│   ├── users/          # Templates pour utilisateurs
│   ├── posts/          # Templates pour publications
│   └── social/         # Templates pour fonctionnalités sociales
│
├── media/              # Fichiers média uploadés
├── static/             # Fichiers statiques (CSS, JS)
└── manage.py           # Script de gestion Django
```

### Modèle MVC de Django

- **Models** : Définition des structures de données (users, posts, social)
- **Views** : Logique métier et traitement des requêtes
- **Templates** : Présentation HTML avec système de templating Django
- **URLs** : Routage des requêtes HTTP vers les vues appropriées

---

## Diagrammes UML

### Diagramme de classes - Modèles de données

```mermaid
classDiagram
    class CustomUser {
        +String username
        +String email
        +String bio
        +String location
        +Date birth_date
        +URL website
    }
    
    class Profile {
        +ImageField profile_picture
        +ImageField cover_photo
        +Integer followers_count
        +Integer following_count
        +Integer posts_count
        +DateTime created_at
        +DateTime updated_at
    }
    
    class Post {
        +String content
        +CharField post_type
        +ImageField image
        +FileField video
        +Integer likes_count
        +Integer comments_count
        +Integer shares_count
        +DateTime created_at
        +Boolean is_shared
    }
    
    class Comment {
        +String content
        +Integer likes_count
        +DateTime created_at
    }
    
    class Like {
        +CharField content_type
        +DateTime created_at
    }
    
    class Follow {
        +DateTime created_at
    }
    
    class Notification {
        +CharField notification_type
        +String message
        +Boolean is_read
        +DateTime created_at
    }
    
    class Conversation {
        +DateTime created_at
    }
    
    class Message {
        +String content
        +DateTime created_at
        +DateTime delivered_at
        +DateTime read_at
    }
    
    CustomUser ||--|| Profile : "has one"
    CustomUser ||--o{ Post : "creates"
    CustomUser ||--o{ Comment : "writes"
    CustomUser ||--o{ Like : "gives"
    CustomUser ||--o{ Follow : "follower"
    CustomUser ||--o{ Follow : "following"
    CustomUser ||--o{ Notification : "receives"
    CustomUser ||--o{ Notification : "sends"
    CustomUser }o--o{ Conversation : "participates"
    CustomUser ||--o{ Message : "sends"
    
    Post ||--o{ Comment : "has"
    Post ||--o{ Like : "receives"
    Post ||--o| Post : "shared_post"
    Comment ||--o{ Like : "receives"
    Comment ||--o| Comment : "parent_reply"
    Conversation ||--o{ Message : "contains"
    Notification }o--o| Post : "references"
    Notification }o--o| Comment : "references"
```

### Relations entre modèles

#### Relation One-to-One
- `CustomUser` ↔ `Profile` : Chaque utilisateur a un et un seul profil

#### Relations One-to-Many (ForeignKey)
- `CustomUser` → `Post` : Un utilisateur peut créer plusieurs posts
- `CustomUser` → `Comment` : Un utilisateur peut écrire plusieurs commentaires
- `CustomUser` → `Like` : Un utilisateur peut liker plusieurs contenus
- `Post` → `Comment` : Un post peut avoir plusieurs commentaires
- `Post` → `Like` : Un post peut avoir plusieurs likes
- `Conversation` → `Message` : Une conversation peut contenir plusieurs messages
- `Message` → `CustomUser` (sender) : Un message a un expéditeur

#### Relations Many-to-Many
- `Conversation` ↔ `CustomUser` (participants) : Une conversation peut avoir plusieurs participants
- `Follow` : Relation symétrique entre follower et following

#### Auto-référence
- `Post` → `Post` (shared_post) : Un post peut partager un autre post
- `Comment` → `Comment` (parent) : Système de réponses imbriquées

---

## Diagrammes de Fonctionnement

### Architecture générale

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT (Navigateur)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   HTML/CSS  │  │  JavaScript  │  │  WebSocket   │      │
│  │  Templates  │  │  (Vanilla)   │  │  Client      │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                    SERVEUR DJANGO (ASGI)                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │          DJANGO FRAMEWORK                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │    │
│  │  │  Views   │  │  Models  │  │ Templates│        │    │
│  │  └──────────┘  └──────────┘  └──────────┘        │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │          DJANGO CHANNELS                           │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │    │
│  │  │Consumers │  │ Routing  │  │  ASGI    │        │    │
│  │  └──────────┘  └──────────┘  └──────────┘        │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                  LAYER DE DONNÉES                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ SQLite   │  │  Redis   │  │  Media   │                  │
│  │ Database │  │ Channels │  │  Files   │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Flux de création de post

```
┌─────────┐
│ Utilisateur │
└────┬────┘
     │ 1. Clique sur "Créer un post"
     ▼
┌─────────────────┐
│ Formulaire POST │
└────┬────────────┘
     │ 2. Soumet le formulaire
     ▼
┌─────────────────────┐
│ views.create_post() │
└────┬────────────────┘
     │ 3. Valide les données
     ▼
┌─────────────────┐
│ Post.objects.   │
│ create()        │
└────┬────────────┘
     │ 4. Sauvegarde en BDD
     ▼
┌─────────────────┐
│ Notification    │
│ aux followers   │
└────┬────────────┘
     │ 5. Redirection
     ▼
┌─────────────────┐
│ Feed (Timeline) │
└─────────────────┘
```

### Flux de chat en temps réel

```
┌──────────┐                    ┌──────────┐
│Client A  │                    │Client B  │
└────┬─────┘                    └────┬─────┘
     │                               │
     │ 1. Connexion WebSocket        │
     ├───────────────────────────────┤
     │                               │
     ▼                               ▼
┌──────────────────────────────────────────┐
│      ChatConsumer (WebSocket)            │
│  ┌────────────────────────────────────┐  │
│  │  - Recevoir message                │  │
│  │  - Sauvegarder en BDD              │  │
│  │  - Broadcast via Channel Layer     │  │
│  └────────────────────────────────────┘  │
└────────────┬───────────────────┬─────────┘
             │                   │
             │ 2. Message        │ 3. Message
             │    via Redis      │    distribué
             │                   │
             ▼                   ▼
┌──────────────────────────────────────────┐
│        Redis Channel Layer               │
└────────────┬───────────────────┬─────────┘
             │                   │
             ▼                   ▼
┌──────────┐                    ┌──────────┐
│Client A  │                    │Client B  │
│(Reçoit)  │                    │(Reçoit)  │
└──────────┘                    └──────────┘
```

### Flux d'authentification

```
┌─────────┐
│ Utilisateur │
└────┬────┘
     │ 1. Accède à /login
     ▼
┌─────────────────┐
│ LoginView       │
│ (GET)           │
└────┬────────────┘
     │ 2. Affiche formulaire
     ▼
┌─────────────────┐
│ Formulaire      │
│ Username/Pass   │
└────┬────────────┘
     │ 3. Soumet (POST)
     ▼
┌─────────────────┐
│ LoginView       │
│ (POST)          │
└────┬────────────┘
     │ 4. Authentification
     ▼
┌─────────────────┐
│ Auth Middleware │
└────┬────────────┘
     │ 5. Session créée
     ▼
┌─────────────────┐
│ Redirect vers   │
│ LOGIN_REDIRECT  │
│ (/feed)         │
└─────────────────┘
```

---

## Fonctionnalités Détaillées

### 1. Gestion des Utilisateurs

#### Inscription
- Création de compte avec username, email, password
- Validation des données (email unique, username unique)
- Création automatique du profil associé

#### Connexion/Déconnexion
- Authentification via sessions Django
- Redirection automatique après connexion
- Gestion des erreurs d'authentification

#### Profil utilisateur
- Photo de profil et photo de couverture
- Bio, localisation, date de naissance, site web
- Compteurs (followers, following, posts)
- Édition du profil

### 2. Système de Publications

#### Création de post
- **Types de posts** :
  - Texte seul
  - Image avec texte
  - Vidéo avec texte
  - Partage de post existant
  
#### Interactions
- **Likes** : Système de likes pour posts et commentaires
- **Commentaires** : Commentaires avec système de réponses (threading)
- **Partages** : Partager un post avec ou sans message personnalisé

#### Gestion
- Modification de ses propres posts
- Suppression de ses propres posts
- Affichage chronologique (timeline)

### 3. Réseau Social

#### Système de suivi
- Suivre/Désabonner un utilisateur
- Liste des followers et following
- Mise à jour automatique des compteurs

#### Suggestions
- Suggestions basées sur :
  - Les amis d'amis
  - Les utilisateurs populaires
  - Les nouveaux utilisateurs

#### Recherche
- Recherche d'utilisateurs par :
  - Username
  - Email
  - Bio

### 4. Messagerie en Temps Réel

#### Conversations
- Liste de toutes les conversations
- Création automatique de conversation
- Affichage du dernier message
- Compteur de messages non lus

#### Chat WebSocket
- Envoi/réception en temps réel
- Statuts de livraison (delivered, read)
- Historique des messages
- Interface de chat intuitive

### 5. Notifications

#### Types de notifications
- Like sur un post
- Commentaire sur un post
- Nouveau follower
- Partage d'un post
- Message reçu

#### Fonctionnalités
- Affichage en temps réel
- Badge de compteur
- Marquage comme lu
- Redirection vers le contenu concerné

### 6. API REST

#### Endpoints disponibles
- `/api/users/` : Gestion des utilisateurs
- `/api/posts/` : Gestion des posts
- `/api/comments/` : Gestion des commentaires
- `/api/follows/` : Gestion des relations de suivi
- `/api/notifications/` : Gestion des notifications

#### Caractéristiques
- Authentification par session
- Pagination automatique (10 éléments/page)
- Filtrage, recherche et tri
- Permissions : AuthenticatedOrReadOnly

---

## Structure des Données

### Tables principales

#### CustomUser
- `id` : Primary Key
- `username` : String (unique)
- `email` : Email (unique)
- `password` : Hashed password
- `bio` : Text (500 caractères max)
- `location` : String (100 caractères)
- `birth_date` : Date
- `website` : URL
- `date_joined` : DateTime
- `last_login` : DateTime

#### Profile
- `id` : Primary Key
- `user_id` : ForeignKey → CustomUser (OneToOne)
- `profile_picture` : ImageField
- `cover_photo` : ImageField
- `followers_count` : Integer
- `following_count` : Integer
- `posts_count` : Integer
- `created_at` : DateTime
- `updated_at` : DateTime

#### Post
- `id` : Primary Key
- `author_id` : ForeignKey → CustomUser
- `content` : Text (2000 caractères)
- `post_type` : CharField (text/image/video/shared)
- `image` : ImageField (nullable)
- `video` : FileField (nullable)
- `shared_post_id` : ForeignKey → Post (nullable, auto-référence)
- `is_shared` : Boolean
- `likes_count` : Integer
- `comments_count` : Integer
- `shares_count` : Integer
- `created_at` : DateTime
- `updated_at` : DateTime

#### Comment
- `id` : Primary Key
- `post_id` : ForeignKey → Post
- `author_id` : ForeignKey → CustomUser
- `content` : Text (500 caractères)
- `parent_id` : ForeignKey → Comment (nullable, auto-référence)
- `likes_count` : Integer
- `created_at` : DateTime
- `updated_at` : DateTime

#### Like
- `id` : Primary Key
- `user_id` : ForeignKey → CustomUser
- `content_type` : CharField (post/comment)
- `post_id` : ForeignKey → Post (nullable)
- `comment_id` : ForeignKey → Comment (nullable)
- `created_at` : DateTime
- **Contrainte unique** : (user, content_type, post, comment)

#### Follow
- `id` : Primary Key
- `follower_id` : ForeignKey → CustomUser
- `following_id` : ForeignKey → CustomUser
- `created_at` : DateTime
- **Contrainte unique** : (follower, following)

#### Notification
- `id` : Primary Key
- `recipient_id` : ForeignKey → CustomUser
- `sender_id` : ForeignKey → CustomUser
- `notification_type` : CharField (like/comment/follow/share)
- `post_id` : ForeignKey → Post (nullable)
- `comment_id` : ForeignKey → Comment (nullable)
- `message` : String (255 caractères)
- `is_read` : Boolean
- `created_at` : DateTime

#### Conversation
- `id` : Primary Key
- `created_at` : DateTime
- **Table de jonction** : conversation_participants (ManyToMany avec CustomUser)

#### Message
- `id` : Primary Key
- `conversation_id` : ForeignKey → Conversation
- `sender_id` : ForeignKey → CustomUser
- `content` : Text
- `created_at` : DateTime
- `delivered_at` : DateTime (nullable)
- `read_at` : DateTime (nullable)

---

## Diagramme de séquence - Création d'un post

```
Utilisateur    Frontend        View          Model         Base de données
    │             │             │              │                  │
    │──POST /post/create/──────>│              │                  │
    │             │             │              │                  │
    │             │             │──validate()─>│                  │
    │             │             │              │                  │
    │             │             │<─valid───────│                  │
    │             │             │              │                  │
    │             │             │──save()────────────────────────>│
    │             │             │              │                  │
    │             │             │<─────────────────────────────────│
    │             │             │              │                  │
    │             │             │──notify_followers()             │
    │             │             │              │                  │
    │             │<──Redirect──│              │                  │
    │<──Success───│             │              │                  │
    │             │             │              │                  │
    │──GET /feed──┐             │              │                  │
    │             │─────────────>│              │                  │
    │             │             │──get_posts()───────────────────>│
    │             │             │              │                  │
    │             │             │<─────────────────────────────────│
    │             │<──HTML──────│              │                  │
    │<──Page──────│             │              │                  │
```

---

## Diagramme de séquence - Chat en temps réel

```
Client A       WebSocket      ChatConsumer   Model         Redis         Client B
    │             │                │            │              │              │
    │──Connect────>│                │            │              │              │
    │             │──Connect───────>│            │              │              │
    │             │                │──Join group───────────────>│              │
    │<──Connected─│                │            │              │              │
    │             │                │            │              │              │
    │──Send msg───>│                │            │              │              │
    │             │──Message───────>│            │              │              │
    │             │                │──save()────>│              │              │
    │             │                │            │              │              │
    │             │                │──Broadcast───────────────>│              │
    │             │                │            │              │              │
    │             │                │            │              │──Notify──────>│
    │             │                │            │              │              │
    │<──Echo──────│                │            │              │              │
    │             │                │            │              │<──Message─────│
    │             │                │            │              │              │
```

---

## Sécurité

### Mesures implémentées

1. **Authentification**
   - Mots de passe hashés (PBKDF2)
   - Sessions sécurisées
   - Protection CSRF

2. **Autorisations**
   - Vérification des permissions sur chaque action
   - Protection contre les modifications non autorisées
   - Validation des données d'entrée

3. **Protection des fichiers**
   - Validation des types de fichiers uploadés
   - Limitation de taille (10MB)
   - Stockage sécurisé dans le dossier media

4. **CORS**
   - Configuration CORS pour l'API
   - Restriction des origines autorisées

---

## Conclusion

### Points forts

✅ Architecture modulaire avec séparation des préoccupations  
✅ Communication en temps réel avec WebSockets  
✅ API REST complète pour intégration externe  
✅ Interface utilisateur moderne et responsive  
✅ Système de notifications efficace  
✅ Gestion complète des interactions sociales  

### Perspectives d'amélioration

- Migration vers PostgreSQL pour la production
- Implémentation d'un système de hashtags et tendances
- Ajout de fonctionnalités de stories/statuts éphémères
- Optimisation des performances avec cache
- Déploiement avec Docker et CI/CD
- Tests automatisés (unitaires et d'intégration)
- Système de recommandations basé sur l'IA

---

**Date du rapport** : Novembre 2025  
**Version** : 1.0  
**Auteur** : Équipe de développement SocialApp

