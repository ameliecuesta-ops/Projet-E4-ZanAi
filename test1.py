import pandas as pd
import zipfile

# Nom du fichier zip
zip_filename = "archive.zip"

# Liste des fichiers CSV dans le zip
with zipfile.ZipFile(zip_filename, 'r') as z:
    csv_files = z.namelist()
    print("Fichiers disponibles dans le zip :")
    for i, f in enumerate(csv_files):
        print(f"{i}: {f}")

# Choix du CSV
index = int(input("\nEntrez le numéro du CSV à charger : "))
csv_to_load = csv_files[index]

# Charger le CSV choisi
with zipfile.ZipFile(zip_filename) as z:
    with z.open(csv_to_load) as f:
        df = pd.read_csv(f)

# Nettoyer les noms de colonnes
df.columns = df.columns.str.strip()

#on cherche les noms des colonnes qu'on veut
print("\nLabels uniques dans le dataset :")
print(df['Label'].unique())


# Filtrer uniquement BENIGN et Brute Force
df_filtered = df[
    (df['Label'] == 'BENIGN') |
    (df['Label'].str.contains("Brute", case=False, na=False))]

# Aperçu lisible : 20 lignes aléatoires, seulement 10 colonnes
print("\nAperçu de 20 lignes aléatoires :")
print(df_filtered.sample(20)[df_filtered.columns[:10]])

# Répartition des labels
print("\nRépartition des labels :")
print(df_filtered['Label'].value_counts())

# Statistiques rapides pour les colonnes numériques
print("\nRésumé statistique des colonnes numériques :")
print(df_filtered.describe())

# Valeurs manquantes par colonne
print("\nValeurs manquantes par colonne :")
print(df_filtered.isnull().sum())

# Dimensions du dataset filtré
print("\nDimensions du dataset filtré (lignes, colonnes) :", df_filtered.shape)

# Sauvegarde
df_filtered.to_csv("dataset_bruteforce.csv", index=False)
