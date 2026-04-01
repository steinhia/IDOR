import pdb

from extract_SRS2 import SRS2_processing
from extract_csv import extract_neuro_classification, extract_processing_speed, extract_working_memory, extract_redcap_general, extract_demographics

if __name__ == "__main__":
    df_demographic=extract_demographics()
    df_demographic['type']="demographic"
    df_neuro=extract_neuro_classification()
    df_neuro['type']="neuro"
    df_SRS2=SRS2_processing()
    df_SRS2['type']="SRS2"
    df_PS=extract_processing_speed()
    df_PS['type']="PS"
    df_WM=extract_working_memory()
    df_WM['type']="WM"
    pdb.set_trace()

