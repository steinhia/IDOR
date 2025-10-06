import json

import pandas as pd
import pdb

#csv_path="MAC_raw.csv"
#raw_header = pd.read_csv(csv_path, nrows=3, header=None, dtype=str)

table_list=["Neuro","Dados_demograficos","Testes_neuropsicologicos","Dados_motores_da_fala","MAC"]

def get_header_corrected(name):
    """
    :param name: name of the file from which you want to extract the header
    :return: header of the file
    """
    return list(pd.read_csv("csv/"+name+"_corrected_example.csv").columns)

def save_header_corrected(table_list):
    """
    :param table_list: list of files from which you want to build the headers
    :return: None
    creates a json file with the headers as in the example files
    """
    header={}
    for i in table_list:
        header[i]=get_header_corrected(i)
    with open("csv/headers.json", "w", encoding="utf-8") as f:
        json.dump(header, f, indent=2, ensure_ascii=False)
save_header_corrected(table_list)

def replace_header(name=None):
    l=table_list if name is None else [name]
    with open("csv/headers.json", "r", encoding="utf-8") as f:
        dico = json.load(f)
    for i in l:
        try:
            df=pd.read_csv("csv/" + i + "_raw.csv")
            if i=="MAC": # 2 lines of columns
                df = df.iloc[1:].reset_index(drop=True)
            df.columns=list(dico[i])
            df.to_csv("csv/"+i+".csv", index=False)
            print(f"file {i} replaced")
        except: print(f"file {i} not found")
replace_header()

