import pandas as pd
import pdb

csv_path="MAC_adultos_hierarchical.csv"
raw_header = pd.read_csv(csv_path, nrows=3, header=None, dtype=str)

# Remplir verticalement les NaN (ou cellules vides) par la dernière valeur connue
filled_header = raw_header.fillna(method='ffill', axis=1)

# abbreviate level 0
abbrev_level0 = filled_header.iloc[0].apply(
    lambda x: ''.join(word[0].upper() for word in str(x).split() if word)
)

# Concaténer les 3 lignes en une seule ligne de noms de colonnes
new_columns = [
    f"{a}_{b}_{c}".strip("_").replace("_nan_","_").replace(" ","_")  # strip au cas où une cellule est vide malgré tout
    for a, b, c in zip(abbrev_level0, filled_header.iloc[1], filled_header.iloc[2])
]

# Lire le reste du fichier à partir de la ligne 4
df = pd.read_csv(csv_path, skiprows=3, header=None)
df.columns = new_columns
df = df.set_index('Subject')
df.to_csv("MAC_flat.csv")
pdb.set_trace()


