import pdb
import pandas as pd
from extract_csv import extract_fmri_data,extract_neuro_classification

def extract_patient_list():
    """
    extract list of patients from RedCap
    :return: dataframe with all patient info necessary to make the matching
    """
    ## patients with imaging
    fmri=extract_fmri_data()
    neuro_class=extract_neuro_classification()
    neuro_types=['Total','Parcial','Hipoplásico']
    neuro_class=neuro_class[neuro_class.neuro_classification.isin(neuro_types)]
    fmri=fmri[fmri.subj_id.isin(neuro_class.subj_id)]
    ## patients with SRS2
    SRS2=pd.read_csv("csv/SRS2_Demographic.csv")
    SRS2_liste = list(SRS2.subj_id.values) + ['SUBJ' + i for i in ['005', '824', '838', '792', '823', '840', '843', '835', '762', '757', '739']]
    fmri=fmri[fmri.subj_id.isin(SRS2_liste)]
    return fmri

def extract_control_list():
    ## HCP
    ## participants from dHCP
    # only one where we actually use the data
    pd.read_csv('data/HCP/ndar_subject01_1244611.txt', sep="\t").to_csv("data/HCP/demographic_hcp_2.csv", index=False)
    #from 36 years -> not useful
    pd.read_csv('data/HCP/ndar_subject01_1244710.txt', sep="\t").to_csv("data/HCP/demographic_hcp_1.csv", index=False)
    # foetus -> not useful
    pd.read_csv('data/HCP/ndar_subject01_1244353.txt', sep="\t").to_csv("data/HCP/demographic_hcp_3.csv", index=False)
    # participants that have SRS2
    pd.read_csv('data/HCP/ndar_subject01_SRS2.txt', sep="\t").to_csv("demographic_SRS2.csv", index=False)
    hcp1 = pd.read_csv('data/HCP/demographic_hcp_1.csv')[['subjectkey','src_subject_id','interview_date','interview_age','sex']].iloc[1:]
    hcp2 = pd.read_csv('data/HCP/demographic_hcp_2.csv')[['subjectkey','src_subject_id','interview_date','interview_age','sex']].iloc[1:]
    hcp3 = pd.read_csv('data/HCP/demographic_hcp_3.csv')[['subjectkey','src_subject_id','interview_date','interview_age','sex']].iloc[1:]
    ## participants from HCP with SRS2
    srs2 = pd.read_csv('demographic_SRS2.csv')[['subjectkey','src_subject_id','interview_date','interview_age','sex']].iloc[1:]
    hcp = pd.concat([hcp1, hcp2, hcp3])
    hcp=hcp[hcp.src_subject_id.isin(srs2.src_subject_id.values)]
    return hcp

def compute_matching(fmri,hcp):
    """
    choose the control participants from all data available (neuroimaging, SRS2 etc)
    :param fmri: patient list
    :param hcp: available control list
    :return: dataframe with patient and matched controls
    """
    fmri['age_years'] = (fmri['acquisition_age'].astype(float) / 12).astype(int)
    hcp['age_years'] = (hcp['interview_age'].astype(float) / 12).astype(int)
    fmri['acquisition_age'] = pd.to_numeric(fmri['acquisition_age'], errors='coerce')
    hcp['interview_age'] = pd.to_numeric(hcp['interview_age'], errors='coerce')

    # merge + diff + better matching
    fmri = (
        fmri.merge(hcp, left_on='gender', right_on='sex', how='left')
        .assign(diff_months=lambda x: (x.interview_age - x.acquisition_age).abs())
        .sort_values('diff_months')  # on trie bien sur les mois
        .drop_duplicates('subj_id')  # garde le meilleur match
        .assign(
            age_years_patient=lambda x: x.acquisition_age / 12,
            age_years_paired_control=lambda x: x.interview_age / 12,
            diff_years=lambda x: abs(x.age_years_x - x.age_years_y)
        )
        .rename(columns={
            'src_subject_id': 'id_paired_control',
            'interview_age': 'age_months_paired_control',
            'sex': 'sex_paired_control'
        })
    )
    fmri.to_csv("csv/matching.csv")

if __name__ == "__main__":
    fmri=extract_patient_list()
    hcp=extract_control_list()
    compute_matching(fmri,hcp)





