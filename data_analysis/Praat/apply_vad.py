"""
speech_analysis.py

Pipeline for analyzing speech recordings:
1. Automatic detection of speech vs silence (VAD)
2. Export to TextGrid for manual annotation in Praat
3. Prosody analysis on annotated speech segments

Requirements:
- Python ≥ 3.8
- Libraries: torch, torchaudio, numpy, scipy, soundfile, tgt, textgrid
"""

import torchaudio
import torch
import numpy as np
import soundfile as sf
from textgrid import TextGrid, IntervalTier
import tgt
import os
from scipy.signal import butter, filtfilt, hilbert, medfilt, find_peaks


def load_audio(wav_path: str):
    """
    Load a WAV file, convert to mono and resample to 16kHz if necessary.

    Args:
        wav_path (str): Path to audio file.

    Returns:
        wav (torch.Tensor): Mono waveform (1 x N)
        sr (int): Sampling rate (Hz)
    """
    wav, sr = torchaudio.load(wav_path)
    wav = wav.mean(dim=0, keepdim=True)  # convert to mono
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
        wav = resampler(wav)
        sr = 16000
    return wav, sr


def apply_vad(wav: torch.Tensor, sr: int):
    """
    Apply Voice Activity Detection (VAD) using Silero model.

    Args:
        wav (torch.Tensor): Mono waveform.
        sr (int): Sampling rate.

    Returns:
        List[dict]: Timestamps of detected speech segments.
    """
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
    (get_speech_timestamps, _, _, _, _) = utils
    speech_timestamps = get_speech_timestamps(wav[0], model, sampling_rate=sr)
    return speech_timestamps


def create_TextGrid(wav_path: str, speech_timestamps: list, wav: torch.Tensor, sr: int) -> str:
    """
    Create a TextGrid with speech/silence intervals from VAD.

    Args:
        wav_path (str): Original WAV file path.
        speech_timestamps (list): Output from apply_vad().
        wav (torch.Tensor): Audio waveform.
        sr (int): Sampling rate.

    Returns:
        str: Path to saved TextGrid file.
    """
    textgrid_path = wav_path.replace('.wav', '.TextGrid')

    if not os.path.exists(textgrid_path):
        tg = TextGrid(minTime=0, maxTime=float(wav.shape[1] / sr))
        tier = IntervalTier(name='vad', minTime=0, maxTime=float(wav.shape[1] / sr))

        last_end = 0
        for s in speech_timestamps:
            start = s['start'] / sr
            end = s['end'] / sr
            if start > last_end:
                tier.add(minTime=last_end, maxTime=start, mark='silence')
            tier.add(minTime=start, maxTime=end, mark='speech')
            last_end = end
        if last_end < wav.shape[1] / sr:
            tier.add(minTime=last_end, maxTime=wav.shape[1] / sr, mark='silence')

        tg.append(tier)
        tg.write(textgrid_path)
        print(f"TextGrid saved: {textgrid_path}")

    return textgrid_path


def get_vad_intervals(textgrid_file: str):
    """
    Extract speech and silence intervals from TextGrid.

    Args:
        textgrid_file (str): Path to annotated TextGrid.

    Returns:
        speech_intervals (list of tuple): List of (start, end) in seconds for speech.
        silence_intervals (list of tuple): List of (start, end) in seconds for silence.
    """
    tg = tgt.read_textgrid(textgrid_file)
    vad_tier = tg.get_tier_by_name("vad")
    speech_intervals = [(i.start_time, i.end_time) for i in vad_tier.intervals if i.text == "speech"]
    silence_intervals = [(i.start_time, i.end_time) for i in vad_tier.intervals if i.text == "silence"]
    return speech_intervals, silence_intervals


def get_wav_concat(wav: torch.Tensor, speech_intervals: list, sr: int):
    """
    Concatenate all speech segments into a single waveform.

    Args:
        wav (torch.Tensor): Original waveform.
        speech_intervals (list of tuple): List of (start, end) speech intervals.
        sr (int): Sampling rate.

    Returns:
        torch.Tensor: Concatenated speech waveform.
    """
    if not speech_intervals:
        raise ValueError("No speech intervals found.")

    segments = [wav[0][int(start * sr):int(end * sr)] for start, end in speech_intervals]
    wav_concat = np.concatenate(segments)
    return torch.from_numpy(wav_concat)


def compute_envelope(wav_concat: torch.Tensor, sr: int):
    """
    Compute the smoothed amplitude envelope of a waveform.

    Args:
        wav_concat (torch.Tensor): Concatenated speech waveform.
        sr (int): Sampling rate.

    Returns:
        np.ndarray: Smoothed envelope
    """
    analytic_signal = hilbert(wav_concat)
    amplitude_envelope = np.abs(analytic_signal)

    # Low-pass filter to smooth the envelope
    def lowpass(data, sr, cutoff=10.0):
        nyquist = 0.5 * sr
        normal_cutoff = cutoff / nyquist
        b, a = butter(N=4, Wn=normal_cutoff, btype='low')
        return filtfilt(b, a, data)

    smoothed_envelope = lowpass(amplitude_envelope, sr)

    if smoothed_envelope.ndim == 2:
        smoothed_envelope = smoothed_envelope.flatten()

    # Save for visualization
    os.makedirs("data", exist_ok=True)
    sf.write("data/1_envelope.wav", smoothed_envelope, sr)
    return smoothed_envelope


def compute_monotony(envelope_segment: np.ndarray):
    """
    Compute monotony metrics of the speech envelope.

    Args:
        envelope_segment (np.ndarray): Smoothed amplitude envelope.

    Returns:
        amplitude, std_dev, coef_var
    """
    amplitude = np.max(envelope_segment) - np.min(envelope_segment)
    std_dev = np.std(envelope_segment)
    mean_val = np.mean(envelope_segment)
    coef_var = std_dev / mean_val if mean_val > 0 else 0

    print("Amplitude:", amplitude)
    print("Standard deviation:", std_dev)
    print("Coefficient of variation:", coef_var)
    return amplitude, std_dev, coef_var


def mean_pause_duration(silence_intervals: list):
    """
    Compute mean duration of silent intervals.

    Args:
        silence_intervals (list of tuple)

    Returns:
        float: Mean pause duration in seconds.
    """
    mpd = np.mean([end - start for start, end in silence_intervals])
    print("Mean pause duration:", mpd)
    return mpd


def estimate_speech_rate(wav_concat: torch.Tensor, sr: int):
    """
    Estimate speech rate (syllables per second) from waveform.

    Args:
        wav_concat (torch.Tensor)
        sr (int)

    Returns:
        float: Speech rate (syllables/s)
    """
    bandpass = torchaudio.functional.bandpass_biquad(wav_concat, sr, 1000, Q=0.707)
    env = np.abs(hilbert(bandpass.squeeze().numpy()))
    env_smooth = medfilt(env, kernel_size=201)

    # Detect peaks representing syllables
    peaks, _ = find_peaks(env_smooth, distance=sr * 0.1, height=np.mean(env_smooth))
    n_syllables = len(peaks)

    duration = wav_concat.shape[0] / sr
    speech_rate = n_syllables / duration

    print(f"Estimated syllables: {n_syllables}")
    print(f"Duration: {duration:.2f}s")
    print(f"Speech rate ≈ {speech_rate:.2f} syll/s")
    return speech_rate


# --- Main pipeline ---
if __name__ == "__main__":
    wav_path = 'data/1.wav'
    wav, sr = load_audio(wav_path)

    # Step 1: Automatic VAD
    speech_timestamps = apply_vad(wav, sr)
    textgrid_path = create_TextGrid(wav_path, speech_timestamps, wav, sr)

    print("\n=== Step 2: Please open the TextGrid in Praat, verify and adjust speech/silence intervals ===\n")

    # Step 3: Prosody analysis (after manual annotation)
    speech_intervals, silence_intervals = get_vad_intervals(textgrid_path)
    wav_concat = get_wav_concat(wav, speech_intervals, sr)
    envelope = compute_envelope(wav_concat, sr)
    compute_monotony(envelope)
    mean_pause_duration(silence_intervals)
    estimate_speech_rate(wav_concat, sr)