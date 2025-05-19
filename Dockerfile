# Image officielle Python légère
FROM python:3.11-slim

# Mettre le dossier de travail dans le container
WORKDIR /app

# Copier les fichiers requirements (optionnel si pas de requirements.txt)
# Ici on installe Flask (si tu n'as pas requirements.txt, on peut l'ajouter)
RUN pip install flask

# Copier tout le contenu de ton projet dans /app
COPY . .

# Exposer le port 5000 (port par défaut de Flask)
EXPOSE 5000

# Lancer l'application Flask (mode debug activé)
CMD ["python", "ton_script.py"]
