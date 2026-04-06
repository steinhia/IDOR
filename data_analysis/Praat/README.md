# Speech Analysis Pipeline

This Python script analyzes speech recordings to extract prosodic features such as speech rate, monotony, pause duration, and amplitude envelope. The analysis is performed in two stages:

1. Automatic speech detection (VAD) and export
2. Manual annotation in Praat   
3. Prosody analysis

---

## Requirements

Install Python ≥ 3.8 and required libraries: pip install torch torchaudio numpy scipy soundfile tgt textgrid
  

---

## Step 1: Automatic Speech Detection

The script automatically:

- Loads a .wav audio file, converts stereo to mono, and resamples to 16 kHz if needed.
- Detects speech intervals using the Silero VAD model.
- Generates a .TextGrid file (e.g., example.TextGrid) containing two types of intervals: `speech` and `silence`.

**Note:** The automatically generated TextGrid provides a starting point. The intervals may not be perfectly accurate and require manual verification.

---

## Step 2: Manual Annotation in Praat

1. Open the generated TextGrid in Praat alongside the audio file.
2. Verify and adjust the `speech` and `silence` intervals:
   - Make sure all spoken segments are labeled as `speech`.
   - Make sure pauses, breaths, or background noise are labeled as `silence`.
   - Only the patient speech intervals should be anotated, the other ones should remain as 'silence' to be excluded from the calculation
3. Save the corrected TextGrid.

**Important:** The tier name must remain exactly `vad` with labels `speech` and `silence`.

---

## Step 3: Prosody Analysis

After manual annotation, the script performs the following analyses:

- **Speech segment extraction:** concatenates all verified speech segments into a single waveform.
- **Amplitude envelope computation:** calculates a smoothed envelope using a low-pass filter and saves it to `data/1_envelope.wav`.
- **Monotony metrics:** computes amplitude (max-min of envelope), standard deviation, and coefficient of variation.
- **Mean pause duration:** computes the average length of silent intervals.
- **Speech rate estimation:** estimates the number of syllables per second based on peaks in the smoothed envelope.

**Outputs:**

- `data/1_envelope.wav` → smoothed amplitude envelope for visualization
- Console outputs including monotony metrics, mean pause duration, and estimated speech rate (syllables/s)

---

## Usage Instructions

1. Place your audio file in the `data/` folder (e.g., `data/1.wav`).
2. Run the script: python speech_analysis.py
3. Open the automatically generated TextGrid in Praat.
4. Manually correct `speech` and `silence` intervals (only keep 'speech' intervals for the patient, not the interviewer), then save the TextGrid.
5. Re-run the script to perform prosody analysis on the manually corrected annotations.



