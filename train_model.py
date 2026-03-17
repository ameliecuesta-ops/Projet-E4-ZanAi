import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
import joblib
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score
from sklearn.metrics import accuracy_score, confusion_matrix

# Charger le dataset
df = pd.read_csv("dataset_bruteforce.csv")

# Transformer labels
df['Label'] = df['Label'].apply(lambda x: 0 if x == 'BENIGN' else 1)
print(df['Label'].value_counts())

# Séparer features et labels
X = df.drop(columns=['Label'])
y = df['Label']

# Nettoyage des données
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(0, inplace=True)

# (Optionnel) Normalisation
scaler = StandardScaler()
X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)


# Sauvegarder le scaler pour utilisation future
joblib.dump(scaler, "scaler.pkl")
print("Scaler sauvegardé dans scaler.pkl")


# --- Sur-échantillonner les attaques avec SMOTE ---
smote = SMOTE(sampling_strategy=0.5, random_state=42)  # attaques = 50% du nombre de benign
X_res, y_res = smote.fit_resample(X, y)

print("\nAprès SMOTE :")
print(pd.Series(y_res).value_counts())


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("\nDistribution TRAIN:")
print(y_train.value_counts())

print("\nDistribution TEST:")
print(y_test.value_counts())

# Entraînement modèle
model = RandomForestClassifier(class_weight="balanced")
model.fit(X_train, y_train)

# Évaluation
y_pred = model.predict(X_test)
print("\nRapport de classification :")
print(classification_report(y_test, y_pred))


joblib.dump(model, "random_forest_model.pkl")
print("Random forest sauvegardée")



# Prédictions sur le test set
y_pred = model.predict(X_test)

# Accuracy en %
accuracy = accuracy_score(y_test, y_pred) * 100
print(f"Accuracy sur le jeu de test : {accuracy:.2f}%")

# Rapport détaillé
print("\nRapport de classification :")
print(classification_report(y_test, y_pred, digits=4))

# Matrice de confusion
cm = confusion_matrix(y_test, y_pred)
print("\nMatrice de confusion :")
print(cm)
