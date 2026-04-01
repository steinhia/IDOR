
import pandas as pd
import pdb
import re
import numpy as np
csv_folder="csv/"
data_folder="data/"

def extract_demographics():
    """
    extract demographics from RedCap
    :return: dataframe with subject id and demographic info
    """
    df= pd.read_csv(data_folder + "Demographic.csv").rename(columns={"Record ID":"subj_id"})
    df = df.rename(columns={'Sexo': 'sex'})
    df['sex'] = df['sex'].replace({
        'Masculino': 'M',
        'Feminino': 'F'
    })
    return df

def extract_fmri_data():
    df=pd.read_csv(data_folder+'fmri.csv').dropna(how='all')
    # include gender information in the fmri lines
    df['criterios_gen'] = df.groupby('subj_id')['criterios_gen'].transform('first')
    df = df[df['criterios_gen'].notna()]
    df = df[df['redcap_repeat_instance'].replace('', pd.NA).notna()]
    df = df[df['lpi_mri_age_2'].replace('', pd.NA).notna()]
    df = df.loc[df.groupby('subj_id')['redcap_repeat_instance'].idxmax()]
    df['criterios_gen'] = df['criterios_gen'].astype(str).replace({
        '2.0': 'M',
        '1.0': 'F'
    })
    df.rename(columns={'lpi_mri_age_2':'acquisition_age','criterios_gen':'gender'}, inplace=True)
    df_select=df[['subj_id','acquisition_age','gender']]
    return df_select

def extract_neuro_classification():
    df=pd.read_csv(data_folder+"Neuro.csv")[['Record ID','CCD']].dropna()
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
    df["neuro_classification"] = df["CCD"].map(main_cat)
    df["isolado_classification"] = df["CCD"].map(isolado_cat)
    df.rename({"Record ID":"subj_id"},axis=1, inplace=True)
    return df[['subj_id','neuro_classification','isolado_classification']]
#extract_neuro_classification()

def extract_processing_speed( instr_col='Instruments used', max_tests=2):
    df=pd.read_csv(data_folder+"ProcessingSpeed.csv")
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

def extract_redcap_general(df,first_column,test_names,length_tests,instr_to_index, instr_col='Instruments used'):
    df = df.dropna(subset=[instr_col])
    # creates .0 columns and raw columns to store the results
    test_results = df.columns[first_column:first_column + length_tests]
    df = df.rename(columns={c: f"{c}.0" for c in test_results})
    split_tests = df["Instruments used"].fillna("").str.split(",").apply(lambda x: [t.strip() for t in x if t.strip()])
    for name in test_names:
        df[name] = split_tests.apply(lambda lst: next((t for t in lst if name.lower() in t.lower()), None))

    # for each test_type ("Visual Search", "Coding" etc)
    for tname in test_names:
        # for each result type ("Raw Score", "Scaled Score")
        for tres in test_results:
            df[f"{tname}_{tres}"] = df.apply(
                lambda row: (
                    row[f"{tres}.{instr_to_index[row[tname]]}"]
                    if pd.notna(row[tname]) else np.nan
                ),
                axis=1
            )
    # clean dataframe
    cols_to_drop = [
        c for c in df.columns
        if any(r in c for r in test_results) and not any(c.startswith(t + "_") for t in test_names)
    ]
    cols_to_drop+=["Repeat Instrument","Repeat Instance","Instruments used","Complete?"]
    df = df.drop(columns=cols_to_drop)
    df.rename({"Record ID":"subj_id"},axis=1,inplace=True)
    return df

def extract_processing_speed():
    df=pd.read_csv(data_folder+"ProcessingSpeed.csv")
    first_column=4
    length_tests=2
    test_names=["Coding","Symbol Search"]
    test_results=["Raw Score","Scaled Score"]
    instr_to_index = {
        "Coding A (WISC-IV)": 0,
        "Coding B (WISC-IV)": 2,
        "Coding (WAIS-III)": 4,
        "Symbol Search A (WISC-IV)": 1,
        "Symbol Search B (WISC-IV)": 3,
        "Symbol Search (WAIS-III)": 5
    }
    df= extract_redcap_general(df,first_column,test_names,length_tests,instr_to_index)
    return df
#df=extract_processing_speed()

def extract_working_memory():
    df=pd.read_csv(data_folder+"WorkingMemory.csv")
    df.insert(20, "Total Score.2", "")
    df.insert(21, "Scaled Score.2", "")
    first_column=4
    length_tests=6
    test_names=["Digit Span","Corsi Blocks"]
    instr_to_index = {
        "Digit Span (WAIS III)": 0,
        "Digit Span (WISC-IV)": 1,
        "Corsi Blocks": 2
    }
    df= extract_redcap_general(df,first_column,test_names,length_tests,instr_to_index)
    return df[['subj_id','Digit Span', 'Corsi Blocks', 'Digit Span_Forward - Span', 'Digit Span_Forward - Raw Score', 'Digit Span_Backward - Span',
       'Digit Span_Backward - Raw Score', 'Digit Span_Total Score', 'Digit Span_Scaled Score', 'Corsi Blocks_Forward - Span',
       'Corsi Blocks_Forward - Raw Score', 'Corsi Blocks_Backward - Span', 'Corsi Blocks_Backward - Raw Score', 'Corsi Blocks_Total Score',
       'Corsi Blocks_Scaled Score']]
#df=extract_working_memory()

