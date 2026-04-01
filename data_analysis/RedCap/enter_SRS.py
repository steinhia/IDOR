from collections import Counter

import pandas as pd
import pdb
import os
import numpy as np
csv_folder="csv/"
import subprocess
from extract_csv import extract_neuro_classification, extract_demographics

### TODO inclure code pour vérifier les résultats



file_path = "csv/SRS2_manual.csv"

def extract_questions():
    def extract_list(df):
        return list(df.iloc[:, 7:-2].columns)
    questions = {"preescolar": [], "escolar": [], "ah": []}
    questions["preescolar"] = extract_list(pd.read_csv("csv/SRS2_preescolar_labels.csv"))
    questions["escolar"] = extract_list(pd.read_csv("csv/SRS2_escolar_labels.csv"))
    questions["ah"] = extract_list(pd.read_csv("csv/SRS2_AH_labels.csv"))

    labels = {
        "1": "preescolar",
        "2": "escolar",
        "3": "ah"
    }
    return questions,labels
questions,labels=extract_questions()


def extract_lists():


    # --- Fonction pour demander une réponse valide ---
    def ask_score(question):
        while True:
            try:
                val = int(input(f"{question} (1-4) : "))
                if val in [1, 2, 3, 4, -1]:
                    return val
            except:
                pass
            print("Réponse invalide, entrer un nombre entre 1 et 4.")

    # --- Boucle principale ---
    while True:
        # ID participant
        subj = input("participant ID: ")
        subj_id = f"SUB{subj}"

        # Type de test
        while True:
            test_type = input("Type de test (1=preescolar, 2=escolar, 3=ah) : ")
            if test_type in ["1", "2", "3"]:
                break
            print("Choix invalide.")

        selected_questions = questions[labels[test_type]]

        # Réponses
        responses = []
        for q in selected_questions:
            score = ask_score(q)
            responses.append(score)

        # --- Créer une ligne ---
        row = {
            "participant_id": subj_id,
            "test_type": labels[test_type]
        }

        for i, val in enumerate(responses, start=1):
            row[f"Q{i}"] = val

        df_new = pd.DataFrame([row])

        # --- Charger ou créer le CSV ---
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df = pd.concat([df, df_new], ignore_index=True)
        else:
            df = df_new

        # --- Sauvegarde ---
        df.to_csv(file_path, index=False)

        print("Participant enregistré !")

        # Continuer ?
        cont = input("Ajouter un autre participant ? (y/n) : ")
        if cont.lower() != "y":
            break

# --- Fonction vérification ---
def check_existing_score(current_val, q_text, col):
    check = input(f"{q_text} ({col}): | Enter = keep, or type new value: \n" + str(current_val) +"\n")

    if check == "":
        return current_val

    try:
        new_val = int(check)
        if new_val in [1, 2, 3, 4]:
            return new_val
    except:
        pass

    print("Invalid input, keeping original value.")
    return current_val


# --- Fonction principale ---
def edit_participant():
    if not os.path.exists(file_path):
        print("CSV file not found.")
        return

    df = pd.read_csv(file_path)

    # 👉 TU ENTRES JUSTE UN CHIFFRE
    subj_num = input("Participant number: ").strip()
    subj_id = "SUB" + subj_num   # ← UNE SEULE SOURCE DE VÉRITÉ

    if subj_id not in df["participant_id"].values:
        print("Participant not found.")
        return

    # choix type
    while True:
        test_type = input("Test type (1=preescolar, 2=escolar, 3=ah): ")
        if test_type in ["1", "2", "3"]:
            break
        print("Invalid choice.")

    selected_questions = questions[labels[test_type]]

    # --- ligne du participant (UNE SEULE FOIS) ---
    row_mask = df["participant_id"] == subj_id

    # --- boucle questions ---
    for i, q_text in enumerate(selected_questions):
        col = f"Q{i+1}"

        if col not in df.columns:
            df[col] = None

        current_val = df.loc[row_mask, col].iloc[0]

        new_val = check_existing_score(current_val, q_text, col)

        df.loc[row_mask, col] = new_val

    # sauvegarde
    df.to_csv(file_path, index=False)
    print("Changes saved.")


#edit_participant()
extract_lists()

