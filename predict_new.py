import pandas as pd
import numpy as np
import joblib

# Paramètres du script

THRESHOLD = 0.3      # Seuil pour considérer qu'il y a une attaque
CHUNK_SIZE = 10000   # Nombre de lignes à traiter à la fois (évite de surcharger la RAM)


# Chargement du modèle entraîné

# On charge le modèle RandomForest entraîné précédemment
model = joblib.load("random_forest_model.pkl")

# On charge également le scaler utilisé pendant l'entraînement
scaler = joblib.load("scaler.pkl")

# Récupération des noms de features attendus par le modèle
feature_names = model.feature_names_in_


# Variables pour les statistiques

total = 0           # nombre total de logs analysés
num_attacks = 0     # nombre d'attaques détectées
predictions = []    # liste des prédictions finales


# Lecture du dataset par morceaux

# On lit le fichier CSV par blocs pour éviter de charger tout en mémoire
chunks = pd.read_csv("nouveau_dataset.csv", chunksize=CHUNK_SIZE)

for chunk in chunks:


    # Nettoyage des données

    # Si une colonne "Label" existe (cas d'un dataset d'entraînement)
    # on la supprime car on ne doit pas l'utiliser pour la prédiction
    if 'Label' in chunk.columns:
        chunk = chunk.drop(columns=['Label'])

    # Remplacer les valeurs infinies par NaN
    chunk.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Remplacer les valeurs manquantes par 0
    chunk.fillna(0, inplace=True)

    # Alignement des colonnes

    # On s'assure que les colonnes correspondent à celles utilisées
    # lors de l'entraînement du modèle
    chunk = chunk.reindex(columns=feature_names, fill_value=0)

    # Conversion des données en float pour éviter les erreurs
    chunk = chunk.astype(float)



    # Normalisation des données

    # On applique le même scaler que lors de l'entraînement
    chunk_scaled = scaler.transform(chunk)

    # Prédiction avec probabilités

    # Le modèle renvoie une probabilité d'attaque
    probas = model.predict_proba(chunk_scaled)[:, 1]

    # Si la probabilité dépasse le seuil défini, on considère que c'est une attaque
    y_pred = (probas >= THRESHOLD).astype(int)

    # On ajoute les résultats dans la liste globale
    predictions.extend(y_pred)

    # Mise à jour des statistiques
    num_attacks += sum(y_pred)
    total += len(y_pred)


# Résumé des résultats

percent_attacks = (num_attacks / total) * 100

print(f"\nNombre d’attaques détectées : {num_attacks}/{total}")
print(f"Pourcentage d’attaques détectées : {percent_attacks:.2f}%")


# Sauvegarde des prédictions

pd.DataFrame(predictions, columns=["Prediction"]).to_csv("predictions.csv", index=False)

print("\nLes prédictions ont été sauvegardées dans 'predictions.csv'")

# Distribution des prédictions

print("\nDistribution des prédictions :")
print(pd.Series(predictions).value_counts())
