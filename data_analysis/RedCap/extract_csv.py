
import pandas as pd
import pdb
import re
import numpy as np
csv_folder="csv/"


def extract_neuro_classification():
    df=pd.read_csv(csv_folder+"Neuro.csv")[['Record ID','CCD']].dropna()
    def main_cat(vals):
        v = [x.strip() for x in vals.split(",")]
        for k, r in [("ACC", "Total"), ("Hipoplásico", "Hipoplásico"),("Hiperplásico","Hiperplásico"),
                     ("Parcial", "Parcial"), ("Não", "Controle")]:
            if k in v: return r
        return "Unknown"
    def isolado_cat(vals):
        v = [x.strip() for x in vals.split(",")]
        if "Isolado" in v: return "Isolado"
        if "Associado a outras malformações" in v: return "Plus"
        return "Unknown"
    df["Neuro_classification"] = df["CCD"].map(main_cat)
    df["isolado_classification"] = df["CCD"].map(isolado_cat)
    return df
#extract_neuro_classification()

def extract_processing_speed( instr_col='Instruments used', max_tests=2):
    df=pd.read_csv(csv_folder+"ProcessingSpeed.csv")
    df = df.dropna(subset=["Instruments used"]).drop(columns=["Repeat Instrument", "Repeat Instance"])
    df = df.rename(columns=lambda x: x + ".0" if x.endswith("Raw Score") or x.endswith("Scaled Score") else x)
    cols = list(df.columns)
    instr_to_index = {
        "Coding A (WISC-IV)": 0,
        "Coding B (WISC-IV)": 2,
        "Coding (WAIS-III)": 4,
        "Symbol Search A (WISC-IV)": 1,
        "Symbol Search B (WISC-IV)": 3,
        "Symbol Search (WAIS-III)": 5
    }
    instr_split = df["Instruments used"].where(df["Instruments used"].notna() & (df["Instruments used"] != '')).str.split(r'\s*,\s*')
    df["Coding"] = instr_split.apply(lambda x: next((int(instr_to_index[i]) for i in x if "Coding" in i), np.nan) if isinstance(x, list) else np.nan)
    df["Search"] = instr_split.apply(lambda x: next((int(instr_to_index[i]) for i in x if "Symbol Search" in i), np.nan) if isinstance(x, list) else np.nan)
    pdb.set_trace()
    df["Coding_Raw"] = df.apply( lambda row: row[f"Raw Score.{int(row['Coding'])}"] if not pd.isna(row["Coding"]) else np.nan, axis=1 )
    df["Coding_Scaled"] = df.apply( lambda row: row[f"Scaled Score.{int(row['Coding'])}"] if not pd.isna(row["Coding"]) else np.nan, axis=1 )
    df["Search_Raw"] = df.apply( lambda row: row[f"Raw Score.{int(row['Search'])}"] if not pd.isna(row["Search"]) else np.nan, axis=1 )
    df["Search_Scaled"] = df.apply( lambda row: row[f"Scaled Score.{int(row['Search'])}"] if not pd.isna(row["Search"]) else np.nan, axis=1 )
    print(df[["Coding", "Coding_Raw", "Coding_Scaled", "Search", "Search_Raw", "Search_Scaled"]])
    return df
#df=extract_processing_speed()

def extract_processing_speed_general( instr_col='Instruments used', max_tests=2):
    df=pd.read_csv(csv_folder+"ProcessingSpeed.csv")
    df = df.dropna(subset=["Instruments used"])
    first_column=4
    length_tests=2
    instr_to_index = {
        "Coding A (WISC-IV)": 0,
        "Coding B (WISC-IV)": 2,
        "Coding (WAIS-III)": 4,
        "Symbol Search A (WISC-IV)": 1,
        "Symbol Search B (WISC-IV)": 3,
        "Symbol Search (WAIS-III)": 5
    }
    # creates .0 columns and raw columns to store the results
    tests = df.columns[first_column:first_column + length_tests]
    df = df.rename(columns={c: f"{c}.0" for c in tests})
    for c in tests:
        df[c] = df[f"{c}.0"]

    # On split sur la virgule et on enlève les espaces autour
    split_tests = df["Instruments used"].fillna("").apply(lambda x: [t.strip() for t in x.split(",") if t.strip()])

    # Créer Test1 … TestN
    for i in range(length_tests):
        df[f"Test{i + 1}"] = split_tests.apply(lambda x: x[i] if i < len(x) else None)

    pdb.set_trace()
    df = df[[*df.columns[:first_column],
             *[f"{c}.0" for c in df.columns[first_column:first_column + length_tests]],
             *df.columns[first_column + length_tests:],
             *df.columns[first_column:first_column + length_tests]]]
    #df = df.assign(**{f"{c}.0": df[c] for c in df.columns[first_column:first_column + length_tests]})
    pdb.set_trace()

    df = df.dropna(subset=["Instruments used"]).drop(columns=["Repeat Instrument", "Repeat Instance"])
    df = df.rename(columns=lambda x: x + ".0" if x.endswith("Raw Score") or x.endswith("Scaled Score") else x)
    cols = list(df.columns)
    instr_split = df["Instruments used"].where(df["Instruments used"].notna() & (df["Instruments used"] != '')).str.split(r'\s*,\s*')
    df["Coding"] = instr_split.apply(lambda x: next((int(instr_to_index[i]) for i in x if "Coding" in i), np.nan) if isinstance(x, list) else np.nan)
    df["Search"] = instr_split.apply(lambda x: next((int(instr_to_index[i]) for i in x if "Symbol Search" in i), np.nan) if isinstance(x, list) else np.nan)
    pdb.set_trace()
    df["Coding_Raw"] = df.apply( lambda row: row[f"Raw Score.{int(row['Coding'])}"] if not pd.isna(row["Coding"]) else np.nan, axis=1 )
    df["Coding_Scaled"] = df.apply( lambda row: row[f"Scaled Score.{int(row['Coding'])}"] if not pd.isna(row["Coding"]) else np.nan, axis=1 )
    df["Search_Raw"] = df.apply( lambda row: row[f"Raw Score.{int(row['Search'])}"] if not pd.isna(row["Search"]) else np.nan, axis=1 )
    df["Search_Scaled"] = df.apply( lambda row: row[f"Scaled Score.{int(row['Search'])}"] if not pd.isna(row["Search"]) else np.nan, axis=1 )
    print(df[["Coding", "Coding_Raw", "Coding_Scaled", "Search", "Search_Raw", "Search_Scaled"]])
    return df
df=extract_processing_speed_general()
pdb.set_trace()
