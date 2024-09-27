# Utilisez l'image de base Python
FROM python:3.11

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier des dépendances dans le conteneur
COPY requirements.txt .

# Installez les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste de l'application dans le conteneur
COPY . .

# Commande pour exécuter votre application
CMD ["python", "main.py"]