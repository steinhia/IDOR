from collections import Counter

import pandas as pd
import pdb
import re
import numpy as np
csv_folder="csv/"
import subprocess
from openpyxl import load_workbook
from extract_csv import extract_neuro_classification

# pre-escolar escolar
echelles = {
    "PERCEPÇÃO SOCIAL": [2, 7, 25, 32, 45, 52, 54, 56],
    "COGNIÇÃO SOCIAL": [5, 10, 15, 17, 30, 40, 42, 44, 48, 58, 59, 62],
    "COMUNICAÇÃO SOCIAL": [12, 13, 16, 18, 19, 21, 22, 26, 33, 35, 36, 37, 38, 41, 46, 47, 51, 53, 55, 57, 60, 61],
    "MOTIVAÇÃO SOCIAL": [1, 3, 6, 9, 11, 23, 27, 34, 43, 64, 65],
    "PADRÕES RESTRITOS E REPETITIVOS": [4, 8, 14, 20, 24, 28, 29, 31, 39, 49, 50, 63],
}
inverse=np.array([0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


def verify_partition(echelles):
    # rassembler tous les numéros
    all_nums = [num for sublist in echelles.values() for num in sublist]

    # compter les occurrences
    counts = Counter(all_nums)

    # missing : pas présents
    missing = [n for n in range(1, 66) if counts[n] == 0]

    # doublons : apparus plus d'une fois
    duplicates = [n for n, c in counts.items() if c > 1]

    # hors intervalle 1-65
    out_of_range = [n for n in counts if n < 1 or n > 65]
    print("Trié (sans modifier l'original) :", sorted(all_nums))
    print("Missing:", missing)
    print("Duplicates:", duplicates)
    print("Out of range:", out_of_range)
#verify_partition(echelles)

def calculate_SRS2_id(id_subject,responses,test_type):
    # load file
    wb = load_workbook(csv_folder + "SRS2_correction.xlsx")
    corr = wb["Correção"]

    # 2. Write results
    corr['B1'] = test_type
    corr['B2'] = int(0)
    for idx,i in enumerate(range(5, 70)):
        corr['C' + str(i)] = responses[idx]

    # 3. save temp file
    temp_path = csv_folder+"temp_input.xlsx"
    wb.save(temp_path)

    # 4. Calculation with LibreOffice headless
    subprocess.run(["libreoffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", ".", temp_path], check=True)

    # 5. Read calculated values
    keys = ["TOTAL", "PERCEPÇÃO SOCIAL", "COGNIÇÃO SOCIAL", "COMUNICAÇÃO SOCIAL", "MOTIVAÇÃO SOCIAL", "PADRÕES RESTRITOS E REPETITIVOS", "COMUNICAÇÃO E INTERAÇÃO SOCIAL"]
    wb2 = load_workbook("temp_input.xlsx", data_only=True)  # <-- data_only=True lit les valeurs, pas les formules
    ws2 = wb2["Correção"]
    values = [ws2[f"I{row}"].value for row in range(5, 12)]
    res = dict(zip(keys, values))
    return pd.DataFrame({ "subj_id": [id_subject] * len(keys), "key": keys, "value": values })

def calculate_SRS2(df,repeat_calculation=True):
    tests = {1: "pre", 2: "escolar", 3: "adulto a", 4: "adulto h"}
    if repeat_calculation:
        all_results = []
        for _, row in df.iterrows():
            id_subject = row["subj_id"]
            test_type = tests[row["srs2_botao"]]
            responses = row.iloc[1:66].tolist()
            all_results.append(calculate_SRS2_id(id_subject, responses,test_type))
        final_df = pd.concat(all_results, ignore_index=True)
        final_df.to_csv(csv_folder + "SRS2_results.csv", index=False)
        df_wide = final_df.pivot(index='subj_id', columns='key', values='value').reset_index()
        df_wide.to_csv(csv_folder + "SRS2_results_readable.csv", index=False)
    else:
        final_df=pd.read_csv(csv_folder + "SRS2_results.csv")
    return final_df



#resultats = calculate_SRS2()

def extract_SRS2():
    df=pd.read_csv(csv_folder+"SRS2.csv")
    df = df[df['srs2_botao'].notna()].copy()
    # numerotation problem in the es test
    df = df.rename(columns={f"srs2_es_{i}": f"srs2_es_{i - 1}" for i in range(2, 68)})
    tests = { 1: "Pré-escolar", 2: "Escolar", 3: "Adulto Autorrelato", 4: "Adulto Heterorrelato" }
    tests = { 1: "ps", 2: "es", 3: "aa", 4: "ah" }

    # regroup different test types under same columns (response numero)
    def extract_answers(row):
        test_type = tests[int(row['srs2_botao'])]  # ps / es / aa / ah
        cols = [f"srs2_{test_type}_{i}" for i in range(1, 66)]
        return pd.Series(row[cols].values, index=[f"{i}" for i in range(1, 66)])
    df = df[['subj_id', 'srs2_botao']].join(df.apply(extract_answers, axis=1))
    cols = [f"{i}" for i in range(1, 66)]
    # keep last test
    df = df.groupby('subj_id').last().reset_index()
    # apply punctuation and keeps nan
    df[cols] = df[cols].where(df[cols].isna() | (df[cols] == 0), np.where(inverse, 4 - df[cols], df[cols] - 1))
    # change df format
    df_long = df.melt(
        id_vars=['subj_id'],  # garder subj_id
        value_vars=cols,  # colonnes answer_1 ... answer_65
        var_name='answer_id',  # nouvelle colonne avec le nom de la question
        value_name='value'  # valeur de la réponse
    )
    df_long['answer_id'] = df_long['answer_id'].astype(int)
    return df

def analyse_SRS2(df):
    #neuro classification
    df_neuro = extract_neuro_classification()[['Record ID', 'Neuro_classification']].rename(columns={'Record ID': 'subj_id'})
    df = df.merge(df_neuro, on='subj_id', how='inner')

    # Number of subjects of each group
    print("number of subjects of each group",df.groupby('subj_id').first().groupby('Neuro_classification').count()['key'])

    # mean score
    print("mean score by scale \n",df.groupby('key').agg({'value': 'mean'}))
    print("mean score by scale and Neuro classification\n ",df.groupby(['key','Neuro_classification']).agg({'value': 'mean'}).unstack())

    df['above_60'] = df['value'] > 50
    print("proportion above threshold \n", df.groupby('key')['above_60'].mean())
    print("proportion above threshold \n ", df.groupby(['key','Neuro_classification'])['above_60'].mean().unstack())




df=extract_SRS2()
final_df=calculate_SRS2(df,repeat_calculation=False)
pdb.set_trace()
analyse_SRS2(final_df)
pdb.set_trace()

