import pandas as pd
import numpy as np
import joblib

def detect_attacks(file_path="nouveau_dataset.csv", threshold=0.3):
    """
    Fonction qui lit un CSV, applique le modèle et retourne un résumé
    pour LangChain.
    """
    # Charger le modèle et le scaler
    model = joblib.load("random_forest_model.pkl")
    scaler = joblib.load("scaler.pkl")

    # Lire le nouveau dataset
    X_new = pd.read_csv(file_path)

    # Supprimer la colonne Label si elle existe
    if 'Label' in X_new.columns:
        X_new = X_new.drop(columns=['Label'])

    # Nettoyer les données
    X_new.replace([np.inf, -np.inf], np.nan, inplace=True)
    X_new.fillna(0, inplace=True)

    # S'assurer que les colonnes correspondent au modèle
    feature_names = model.feature_names_in_
    X_new = X_new.reindex(columns=feature_names, fill_value=0).astype(float)

    # Appliquer le scaler
    X_new_scaled = scaler.transform(X_new)

    # Probabilités et prédictions selon le seuil
    probas = model.predict_proba(X_new_scaled)[:, 1]
    y_pred = (probas >= threshold).astype(int)

    # Résumé exploitable
    attacks_detected = int(sum(y_pred))
    total_rows = len(y_pred)
    attack_percentage = attacks_detected / total_rows * 100

    return {
        "total_rows": total_rows,
        "attacks_detected": attacks_detected,
        "attack_percentage": attack_percentage
    }

# Exemple d'appel
if __name__ == "__main__":
    result = detect_attacks()
    print("Résumé : ", result)
