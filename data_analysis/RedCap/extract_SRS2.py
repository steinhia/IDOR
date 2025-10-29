from collections import Counter

import pandas as pd
import pdb
import re
import numpy as np
csv_folder="csv/"

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
    question_to_subscale = {int(q): scale for scale, questions in echelles.items() for q in questions}
    # assign subscale
    df_long['subscale'] = df_long['answer_id'].map(question_to_subscale)
    df_long.to_csv(csv_folder+"SRS2_res.csv")


    # possible analysis : mean score
    sum_by_patient_subscale = df_long.groupby(['subj_id', 'subscale'])['value'].sum().reset_index(name='sum_score')
    mean_score_by_subscale = sum_by_patient_subscale.groupby('subscale')['sum_score'].mean().reset_index(name='mean_score')

    # number of patients above threshold
    total_patients = sum_by_patient_subscale['subj_id'].nunique()
    count_over_60 = sum_by_patient_subscale.groupby('subscale').apply(
        lambda x: (x['sum_score'] > 60).sum()
    ).reset_index(name='n_over_60')
    count_over_60['percent_over_60'] = 100 * count_over_60['n_over_60'] / total_patients
    result = mean_score_by_subscale.merge(count_over_60, on='subscale')

    ## TODO regarder normes

    pdb.set_trace()


extract_SRS2()

pdb.set_trace()
