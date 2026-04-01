import torchaudio
import torchaudio.functional as F
import torch
import numpy as np
import soundfile as sf
from textgrid import TextGrid, IntervalTier
import textgrid
import pdb
from scipy.signal import butter, filtfilt, hilbert
import scipy.signal as sps
import tgt
import os

def load_audio(wav_path):
    wav, sr = torchaudio.load(wav_path)
    # if stereo -> convert to mono
    wav = wav.mean(dim=0, keepdim=True)
    # verify frequency
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
        wav = resampler(wav)
        sr = 16000
    return wav,sr

def apply_vad(wav,sr):
    # Load model VAD Silero
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
    (get_speech_timestamps, _, _, _, _) = utils
    speech_timestamps = get_speech_timestamps(wav[0], model, sampling_rate=sr)
    return speech_timestamps

def create_TextGrid(wav_path,speech_timestamps,wav,sr):
    textgrid_path = wav_path.replace('.wav','.TextGrid')
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
        tg.write('example.TextGrid')
        print("TextGrid saved: example.TextGrid")
    return textgrid_path

def get_vad_intervals(textgrid_file):
    tg = tgt.read_textgrid(textgrid_file)
    vad_tier = tg.get_tier_by_name("vad")
    speech_intervals = [(interval.start_time, interval.end_time)
                        for interval in vad_tier.intervals
                        if interval.text == "speech"]
    silence_intervals = [(interval.start_time, interval.end_time)
                        for interval in vad_tier.intervals
                        if interval.text == "silence"]
    return speech_intervals,silence_intervals

def get_wav_concat(wav,speech_intervals):
    if not speech_intervals:
        raise ValueError(f"No speech interval found in {textgrid_path}")

    # --- concatenate signal segments ---
    wav_segments = []
    for start, end in speech_intervals:
        start_idx = int(start * sr)
        end_idx = int(end * sr)
        wav_segments.append(wav[0][start_idx:end_idx])
    wav_concat = np.concatenate(wav_segments)
    return torch.from_numpy(wav_concat)

def compute_envelope(wav_concat, sr, speech_intervals):

    analytic_signal = hilbert(wav_concat)
    amplitude_envelope = np.abs(analytic_signal)

    def lowpass(data, sr, cutoff=10.0):
        nyquist = 0.5 * sr
        normal_cutoff = cutoff / nyquist
        b, a = butter(N=4, Wn=normal_cutoff, btype='low')
        return filtfilt(b, a, data)
    smoothed_envelope = lowpass(amplitude_envelope, sr)
    # normalization
    #smoothed_envelope /= np.max(np.abs(smoothed_envelope))
    # dimension difficulties for exporting
    if smoothed_envelope.ndim == 2:
        smoothed_envelope = smoothed_envelope.flatten()
    # save file for vizualization
    sf.write("data/1_envelope.wav", smoothed_envelope, sr)
    return smoothed_envelope

def compute_monotony(envelope_segment):
    amplitude = np.max(envelope_segment) - np.min(envelope_segment)
    std_dev = np.std(envelope_segment)
    mean_val = np.mean(envelope_segment)
    coef_var = std_dev / mean_val if mean_val > 0 else 0

    print("amplitude: ",amplitude)
    print("std_dev: ",std_dev)
    print("coef_var: ",coef_var)
    return amplitude, std_dev, coef_var

def mean_pause_duration(silence_intervals):
    mpd= np.mean([s[1]-s[0] for s in silence_intervals])
    print("mean pause duration: ",mpd)
    return mpd


def estimate_speech_rate(waveform, sr):
    # Etract envelop in the vowel band (300–4000 Hz)
    bandpass = torchaudio.functional.bandpass_biquad(waveform, sr, 1000, Q=0.707)
    env = torch.abs(torch.from_numpy(sps.hilbert(bandpass.squeeze().numpy())))

    # Smooth enveloppe
    env_smooth = torch.from_numpy(sps.medfilt(env, kernel_size=201))
    env_smooth = env_smooth.numpy() if hasattr(env_smooth, "numpy") else env_smooth

    # peak detection
    peaks, _ = sps.find_peaks(env_smooth, distance=sr * 0.1, height=env_smooth.mean())
    n_syllables = len(peaks)

    duration = waveform.shape[0] / sr
    speech_rate = n_syllables / duration

    print(f"Syllabes estimées (acoustique): {n_syllables}")
    print(f"Durée: {duration:.2f}s")
    print(f"Speech rate ≈ {speech_rate:.2f} syll/s")

for i in range(1,2):
    wav_path = 'data/1.wav'
    wav,sr=load_audio(wav_path)
    speech_timestamps = apply_vad(wav, sr)
    textgrid_path=create_TextGrid(wav_path,speech_timestamps, wav, sr)
    speech_intervals,silent_intervals = get_vad_intervals(textgrid_path)
    wav_concat=get_wav_concat(wav,speech_intervals)
    smoothed_envelope=compute_envelope(wav_concat, sr,speech_intervals)
    amplitude, std_dev, coef_var= compute_monotony(smoothed_envelope)
    mpd=mean_pause_duration(silent_intervals)
    estimate_speech_rate(wav_concat,sr)



