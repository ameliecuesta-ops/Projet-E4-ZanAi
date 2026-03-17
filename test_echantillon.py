import pandas as pd
import joblib

# --- Charger modèle et scaler ---
model = joblib.load("random_forest_model.pkl")
scaler = joblib.load("scaler.pkl")

# --- Charger le dataset d'entraînement pour récupérer des attaques ---
df = pd.read_csv("dataset_bruteforce.csv")

# Sélectionner un petit échantillon d'attaques
attacks_sample = df[df['Label'] != 'BENIGN'].head(10).drop(columns=['Label'])

# --- Mise à l'échelle ---
X_scaled = scaler.transform(attacks_sample)

# --- Prédiction avec seuil ajustable ---
threshold = 0.1
probas = model.predict_proba(X_scaled)[:, 1]
y_pred = (probas >= threshold).astype(int)

# --- Afficher résultats ---
print("Probabilités des attaques : ", probas)
print("Prédictions après seuil : ", y_pred)

# --- Vérifier si toutes les attaques ont été détectées ---
if all(y_pred == 1):
    print("\n✅ Le modèle détecte correctement toutes les attaques de l'échantillon !")
else:
    print("\n❌ Certaines attaques n'ont pas été détectées. Tu peux ajuster le seuil ou vérifier les features.")
