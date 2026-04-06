# 0- Overview of all scripts 

* I - Behavioral data processing : data processing for demographics, classification of the patient malformation, cognitive scores (processing speed, working memory) and SRS2
* II - Choosing the control participants : matching with the DCC patients to choose the control participants
* III - SRS-2 Manual Entry & Editing Tool : create a csv that contains answers to SRS2 questions when missing from the RedCap csv

# I- Behavioral data processing 

## Overview

This project implements a pipeline to extract, clean, and analyze behavioral data from REDCap and other sources. It includes multiple behavioral domains:

* Demographics
* Neuroclassification
* Cognitive scores (Processing Speed, Working Memory)
* SRS-2 (Social Responsiveness Scale, Second Edition)

All data are harmonized into a common format to enable downstream statistical analyses and integration with neuroimaging data. All datasets share a common subject identifier (`subj_id`) and can be merged for multimodal analyses.

## Project Structure

* RedCap/             # contains all necessary scripts
* RedCap/data/        # Raw REDCap and external datasets
* RedCap/csv/         # Processed outputs

## Dependencies

* All scripts run after installing the conda environment from file from the env/ directory : conda env create -f environment.yml
* If you don't want to use conda, make sure to have all these libraries available:
  * Python 3.x
  * pandas
  * numpy
  * openpyxl
  * LibreOffice (headless mode)
  
## How to Run

Main entry point:

```bash
python extract_behavioral_data.py
```

This script:

1. Extracts all behavioral domains
2. Structures them into clean dataframes
3. Prepares them for merging and analysis

---

## Behavioral Data Extraction (extract_csv.py)

All behavioral data (except SRS-2 scoring) are extracted using functions defined in:

```bash
extract_csv.py
```

---

### 1. Demographics

* `extract_demographics()`

**Output:**

* `subj_id`
* `sex`
* `age`

---

### 2. fMRI Metadata

* `extract_fmri_data()`

* Reads: `data/fmri.csv`
* Keeps only valid acquisitions
* Selects latest scan per subject
* Extracts:
  * acquisition age
  * gender

**Output:**

* `subj_id`
* `acquisition_age`
* `gender`

---

### 3. Neuroclassification

* `extract_neuro_classification()`

* Reads: `data/Neuro.csv`
* Parses `CCD` column into two levels:

**Main classification:**

* Total
* Hipoplásico
* Hiperplásico
* Parcial
* Controle

**Secondary classification:**

* Isolado
* Plus (associated malformations)

**Output:**

* `subj_id`
* `neuro_classification`
* `isolado_classification`

---

### 4. Cognitive Scores

Cognitive data are extracted from REDCap exports with heterogeneous formats.
The pipeline dynamically identifies which test was used and retrieves the correct scores.

---

#### a - Generic Extraction Logic

##### `extract_redcap_general(...)`

This function:

* Parses `"Instruments used"`
* Identifies which test was performed
* Maps each test to the correct column index
* Extracts:
  * Raw scores
  * Scaled scores
* Cleans redundant columns

This function is reused for multiple cognitive domains.

---

#### b - Processing Speed

##### `extract_processing_speed()`

* Reads: `data/ProcessingSpeed.csv`
* Handles multiple instruments:
  * Coding (WISC-IV / WAIS-III)
  * Symbol Search

**Outputs include:**

* `Coding_Raw`
* `Coding_Scaled`
* `Search_Raw`
* `Search_Scaled`

---

#### c - Working Memory

##### `extract_working_memory()`

* Reads: `data/WorkingMemory.csv`
* Extracts:
  * Digit Span
  * Corsi Blocks
* Handles subcomponents:
  * Forward
  * Backward

**Outputs include:**

* Raw scores
* Span scores
* Total scores
* Scaled scores

---

### 5 - SRS-2 

This project implements a full pipeline to **process, clean, and analyze SRS-2 (Social Responsiveness Scale, Second Edition) data** from two sources:

* **IDOR dataset (patients)**
* **HCP dataset (controls)**

The pipeline extracts raw questionnaire data, harmonizes formats, computes SRS-2 scores using an official scoring sheet, and performs basic statistical analyses (to be continued).

* Supports multiple test versions:
  * Preschool (`pre`)
  * School-age (`escolar`)
  * Adult (`adulto a`, `adulto h`)
* Harmonizes REDCap structure into unified question columns
* Handles missing responses
* Uses official scoring via Excel

#### Main Features

* Extraction of SRS-2 data from **REDCap exports**
  * Handling of the truplication issue by generating a more easy-to-read format
* Integration of:
  * Demographic data
  * Neuroclassification labels
* Handling of missing or invalid responses
* Automatic computation of:
  * Total score
  * Subscale scores
* Comparison between **patients and controls**

---

#### Input Data : required files (in `data/`)

* `SRS2.csv` : REDCap export (IDOR dataset)
* `SRS2_correction.xlsx` : official scoring sheet
* `srs02_HCP.txt` : HCP dataset (tab-separated)

#### Data Processing Pipeline

##### Usage

Run the full pipeline:

```bash
python extract_SRS2.py
```

This will:

1. Extract and format IDOR and HCP datasets
2. Compute SRS-2 scores
3. Merge results from the 2 populations
4. Run basic analyses


##### 1. Extraction and Formatting

###### IDOR dataset (`extract_SRS2`)

* Merges SRS-2 responses with demographic data
* Fixes column inconsistencies (e.g., shifted indices in escolar version)
* Maps REDCap format to unified structure:
  * One column per question (`1` to `65/66`)
* Keeps only the **latest test per subject**

###### HCP dataset (`extract_srs2_HCP`)

* Filters subjects based on matching list
* Renames columns to match IDOR format

---

##### 2. Data Cleaning

###### Missing values (`replace_nans`)

* Detects and replaces invalid (empty) responses
* Warning : Current behavior:
  * Missing/invalid values are replaced with `1` (default)
  * Median-based imputation is **not yet implemented** (missing information from the clinical psychology team)


##### 3. Score Computation

* Core function: `calculate_SRS2_scores`

* For each subject:

1. Loads `SRS2_correction.xlsx`
2. Uses the following fields to fill the formula :
  * test type
  * sex
  * responses
3. Extracts computed scores

##### Output scores:

* TOTAL
* PERCEPÇÃO SOCIAL
* COGNIÇÃO SOCIAL
* COMUNICAÇÃO SOCIAL
* MOTIVAÇÃO SOCIAL
* PADRÕES RESTRITOS E REPETITIVOS
* COMUNICAÇÃO E INTERAÇÃO SOCIAL

---

##### 4. Output Files

Generated in `csv/`:

```
SRS2_results.csv           # Wide format (one row per subject)
SRS2_results_long.csv      # Long format (one row per score, useful for plotting)
SRS2_results_HCP.csv       # Controls
```

---

##### 5. Analysis

* file `first_analysis_SRS2`

Performs basic descriptive analyses (to be continued):

* Number of subjects per group
* Mean scores:
  * global
  * per subscale
* Comparison by neuroclassification
* Proportion of subjects above threshold (score > 50)


# II - Choosing the control participants

## Overview

This script builds a **matched dataset between patients and control subjects** for analyses (behavioral and neuroimaging).

The goal is to:

* Select **patients with valid data** (fMRI + SRS-2 + neuroclassification)
* Select **eligible controls** from HCP datasets
* Match each patient with a control subject based on:

  * **Sex**
  * **Age (as close as possible)**

## Usage

Run the script:

```bash id="t8o4d1"
python matching.py
```

## Output

Saved in:

```bash id="y9b7j3"
csv/matching.csv
```

### Patients (IDOR dataset)

* fMRI data (age at acquisition, gender)
* Neuroclassification
* SRS-2 availability 

### Controls (HCP dataset)

* Demographic files from HCP
* SRS-2 availability

## Pipeline Steps

### 1. Extract Patient List

#### `extract_patient_list()`

Selects patients that meet all required criteria:

* Have **fMRI data**
* Have a valid **neuroclassification**:
  * Total
  * Parcial
  * Hipoplásico
* Have **SRS-2 data available**

* Output: list of eligible patients with:
  * `subj_id`
  * age at acquisition
  * gender


### 2. Extract Control List

#### `extract_control_list()`

Processes HCP datasets to identify valid control subjects:

* Loads multiple demographic files from HCP
* Keeps only participants with:
  * valid demographic data
  * available **SRS-2**

* Output: list of potential controls with:
  * subject ID
  * age
  * sex

### 3. Matching Procedure

#### `compute_matching(fmri, hcp)`

Matches each patient to a control subject based on:

* **Sex matching** (strict)
* **Age proximity** (best match selected)

For each patient:

* All possible controls with same sex are considered
* The control with the **closest age** is selected

* Output includes:

* Patient ID
* Matched control ID
* Patient age
* Control age
* Age difference


# III - SRS-2 Manual Entry & Editing Tool

This script (`enter_SRS.py`) provides a simple **interactive tool to manually enter or correct SRS-2 questionnaire responses**.

### What it does

* Lets you **input SRS-2 answers** for a participant (question by question)
* Supports different test versions (preescolar, escolar, adulto)
* Saves responses into a CSV file:
* can edit/verify the responses of one participant

```bash
csv/SRS2_manual.csv
```

### Main Functions

* `extract_lists` — extracts and records the list of responses for a participant
* `edit_participant` — allows reviewing and modifying existing responses

### Purpose

This tool is useful when:

* Data is missing from REDCap
* Manual correction is required
