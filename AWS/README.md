# PRJ1509 – Neuroimaging Processing Pipeline (Patients vs Controls)

## Project Structure

Main scripts:

* `clean_raw_data.sh` / `clean_raw_data_HCP.sh`
* `extract_DICOM.sh` / `extract_HCP.sh`
* `verify_bids.sh`
* `launch_fmriprep.sh`
* `verify_fmriprep.sh`
* `launch_melodic.sh`
* `verify_melodic.sh`
* `correlations_ICA_network.sh`
* `launch_atlas.sh`
* `launch_xcpd.sh` / `launch_xcpd_PCA.sh`
* `verify_xcpd.sh`

## Data Organization & Paths

All paths are relative to the project root:

```

03_PROCS/
|-- RAW_DATA/
|   |-- DICOM/            # Patients raw DICOM data
|   `-- HCP/              # Controls (HCP raw structure)
|
|-- PROC_DATA/
|   |-- dataset/              # BIDS dataset (patients)
|   |-- dataset-HCP/          # BIDS-like dataset (controls)
|   |
|   |-- derivatives/          # Patients outputs
|   |   |-- fmriprep/         # fMRIPrep outputs (sub-XXX, HTML reports)
|   |   `-- melodic/          # ICA (MELODIC results)
|   |
|   |-- derivatives-HCP/      # Controls outputs
|   |   |-- fmriprep/
|   |   `-- melodic/
|   |
|   `-- freesurfer/           # FreeSurfer outputs
|
|-- Scripts/                  # All processing scripts (this README)
|-- atlases/                 # Atlases used for analysis
|-- csv/                     # Final outputs (correlations, metrics)
`-- install/                 # Software installations (FSL, etc.)

```


## Overview

This pipeline processes two types of datasets:

* **Patients** → local DICOM data
* **Controls** → HCP dataset

Each dataset follows a similar structure:

1. Raw data cleaning
2. Extraction to NIfTI
3. BIDS formatting
4. Preprocessing (fMRIPrep)
5. ICA decomposition (MELODIC)
6. Post-processing / analysis

---

##  PATIENTS PIPELINE

### 1. Clean raw DICOM data

Remove non-neuroimaging sequences (scout, angiography, etc.) to aliviate the disk:

```bash
bash clean_raw_data.sh
```

---

### 2. Convert DICOM → BIDS (NIfTI)

Extract relevant sequences (T1, T2, resting-state, fieldmaps, diffusion):

```bash
bash extract_DICOM.sh
```

---

### 3. Verify BIDS dataset

Check that all required files are present:

```bash
bash verify_bids.sh
```

---

### 4. Run fMRIPrep

Preprocessing (motion correction, normalization, etc.):

```bash
bash launch_fmriprep.sh
```

---

### 5. Verify fMRIPrep outputs

Check for missing subjects or failed runs:

```bash
bash verify_fmriprep.sh
```

---

### 6. Run ICA decomposition (MELODIC)

Independent Component Analysis on resting-state:

```bash
bash launch_melodic.sh
```

---

### 7. Verify MELODIC outputs

Check for missing subjects or failed runs:

```bash
bash verify_melodic.sh
```

---

### 8. Compute ICA and network correlations

Perform Independant Component Analysis on the Melodic results

```bash
bash correlations_ICA_network.sh
```

---

### 9. Atlas-based analysis (TODO)

```bash
bash launch_atlas.sh
```

---

### 10. Post-processing (XCP-D) optional, unfinished work

```bash
bash launch_xcpd.sh
bash launch_xcpd_PCA.sh
```

Verify:

```bash
bash verify_xcpd.sh
```

---

## CONTROLS PIPELINE (HCP)

Warning: Same logic, but different input format

---

### 1. Clean raw HCP data
Remove non-useful sequences to aliviate the disk:

```bash
bash clean_raw_data_HCP.sh
```

---

### 2. Extract HCP data

Convert HCP structure into BIDS-like dataset:

```bash
bash extract_HCP.sh
```

---

### 3. Verify BIDS dataset

 Use controls mode:

```bash
bash verify_bids.sh --controls
```

---

### 4. Run fMRIPrep

```bash
bash launch_fmriprep.sh --controls
```

---

### 5. Verify fMRIPrep

```bash
bash verify_fmriprep.sh --controls
```

---

### 6. Run MELODIC

```bash
bash launch_melodic.sh --controls
```

---

### 7. Verify MELODIC

```bash
bash verify_melodic.sh --controls
```

---

### 8. ICA and network correlations

```bash
bash correlations_ICA_network.sh --controls
```

---

### 9. Atlas analysis

```bash
bash launch_atlas.sh --controls
```

---

### 10. Post-processing (XCP-D)

```bash
bash launch_xcpd.sh --controls
bash launch_xcpd_PCA.sh --controls
```

Verify:

```bash
bash verify_xcpd.sh --controls
```

---

### Notes

* Re-running scripts is safe: existing outputs are skipped
* Always verify each step before moving to the next

---

##  Typical Order Summary

### Patients

```
* clean_raw_data.sh
* extract_DICOM.sh
* verify_bids.sh
* launch_fmriprep.sh
* verify_fmriprep.sh
* launch_melodic.sh
* verify_melodic.sh
* correlations_ICA_network.sh
* launch_atlas.sh
* launch_xcpd.sh
* verify_xcpd.sh
```

### Controls

```
* clean_raw_data_HCP.sh
* extract_HCP.sh
* verify_bids.sh --controls
* launch_fmriprep.sh --controls
* verify_fmriprep.sh --controls
* launch_melodic.sh --controls
* verify_melodic.sh --controls
* correlations_ICA_network.sh --controls
* launch_atlas.sh --controls
* launch_xcpd.sh --controls
* verify_xcpd.sh --controls
```

---

## Output

Final outputs include:

* Preprocessed BOLD data
* ICA components
* Network correlation matrices (`csv/`)
* Atlas-based metrics

