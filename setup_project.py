import os
import shutil


def create_directory_structure():
    """Crée toute la structure de dossiers nécessaire pour Django 5.2"""

    directories = [
        # Apps
        'apps',
        'apps/users',
        'apps/users/migrations',
        'apps/posts',
        'apps/posts/migrations',
        'apps/social',
        'apps/social/migrations',
        'apps/api',

        # Templates
        'templates',
        'templates/users',
        'templates/posts',
        'templates/social',

        # Static
        'static',
        'static/css',
        'static/js',
        'static/images',

        # Media
        'media',
        'media/profile_pics',
        'media/cover_photos',
        'media/posts',
        'media/posts/images',
        'media/posts/videos',
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Créé: {directory}")

    # Créer les fichiers __init__.py
    init_files = [
        'apps/__init__.py',
        'apps/users/__init__.py',
        'apps/users/migrations/__init__.py',
        'apps/posts/__init__.py',
        'apps/posts/migrations/__init__.py',
        'apps/social/__init__.py',
        'apps/social/migrations/__init__.py',
        'apps/api/__init__.py',
    ]

    for init_file in init_files:
        with open(init_file, 'a') as f:
            pass
        print(f"✓ Créé: {init_file}")


def create_empty_models():
    """Crée les fichiers models.py vides s'ils n'existent pas"""
    model_files = [
        'apps/users/models.py',
        'apps/posts/models.py',
        'apps/social/models.py',
    ]

    for model_file in model_files:
        if not os.path.exists(model_file):
            with open(model_file, 'w') as f:
                f.write("from django.db import models\n\n# Ajoutez vos modèles ici\n")
            print(f"✓ Créé: {model_file}")
        else:
            print(f"⚠ Existe déjà: {model_file}")


def create_empty_files():
    """Crée les fichiers vides pour chaque app"""
    apps = ['users', 'posts', 'social', 'api']
    files = ['views.py', 'urls.py', 'forms.py', 'serializers.py', 'admin.py']

    for app in apps:
        for file in files:
            filepath = f'apps/{app}/{file}'
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    if file == 'admin.py':
                        f.write("from django.contrib import admin\n\n# Enregistrez vos modèles ici\n")
                    elif file == 'views.py':
                        f.write("from django.shortcuts import render\n\n# Créez vos vues ici\n")
                    elif file == 'urls.py':
                        f.write(
                            "from django.urls import path\nfrom . import views\n\napp_name = '{}'\n\nurlpatterns = [\n    # Ajoutez vos URLs ici\n]\n".format(
                                app))
                print(f"✓ Créé: {filepath}")


def check_structure():
    """Vérifie que la structure Django de base existe"""
    required_files = [
        'manage.py',
        'social_media_project/settings.py',
        'social_media_project/urls.py',
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} trouvé")
        else:
            print(f"❌ {file} manquant!")
            all_exist = False

    return all_exist


def create_default_profile_pic():
    """Crée un placeholder pour l'image de profil par défaut"""
    default_pic_dir = 'media/profile_pics'
    os.makedirs(default_pic_dir, exist_ok=True)

    print(f"⚠ N'oubliez pas d'ajouter une image par défaut dans {default_pic_dir}/default.jpg")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Configuration de la structure du projet Django 5.2")
    print("=" * 60)
    print()

    print("🔍 Vérification de la structure Django...")
    if not check_structure():
        print("\n❌ Structure Django de base incomplète!")
        print("   Assurez-vous d'être dans le bon répertoire")
        exit(1)
    print()

    print("📁 Création de la structure de dossiers...")
    create_directory_structure()
    print()

    print("📝 Création des fichiers vides...")
    create_empty_models()
    create_empty_files()
    print()

    print("🖼️  Configuration des médias...")
    create_default_profile_pic()
    print()

    print("=" * 60)
    print("✅ Structure créée avec succès!")
    print("=" * 60)
    print()
    print("📋 Prochaines étapes:")
    print("   1. Copiez le contenu des modèles dans apps/users/models.py")
    print("   2. Copiez le contenu des modèles dans apps/posts/models.py")
    print("   3. Copiez le contenu des modèles dans apps/social/models.py")
    print("   4. Mettez à jour social_media_project/settings.py")
    print("   5. Exécutez: python manage.py makemigrations")
    print("   6. Exécutez: python manage.py migrate")
    print("   7. Exécutez: python manage.py createsuperuser")
    print()