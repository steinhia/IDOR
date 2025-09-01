import torchaudio
import torchaudio.functional as F
import torch
import numpy as np
import soundfile as sf
from textgrid import TextGrid, IntervalTier
import textgrid
import pdb
from scipy.signal import butter, filtfilt, hilbert
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
        textgrid = TextGrid(speech_timestamps)
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

def compute_envelope(wav, sr, speech_intervals):
    if not speech_intervals:
        raise ValueError(f"No speech interval found in {textgrid_path}")

    # --- concatenate signal segments ---
    wav_segments = []
    for start, end in speech_intervals:
        start_idx = int(start * sr)
        end_idx = int(end * sr)
        wav_segments.append(wav[start_idx:end_idx])
    wav_concat = np.concatenate(wav_segments)


    analytic_signal = hilbert(wav.numpy())
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

    # Calculer écart-type
    std_dev = np.std(envelope_segment)

    # Coefficient de variation (optionnel)
    mean_val = np.mean(envelope_segment)
    coef_var = std_dev / mean_val if mean_val > 0 else 0

    # Tu peux choisir l’indicateur qui te parle le plus
    return amplitude, std_dev, coef_var

def mean_pause_duration(silence_intervals):
    return np.mean([s[1]-s[0] for s in silence_intervals])

def speechrate(wav_path,speech_intervals):

    # Analyser le fichier audio
    resultats = mysp.analyze(wav_path)

    pdb.set_trace()
    # Accéder au nombre de syllabes détectées
    syllable_count = analysis['syllable_count']

    # Calculer le speech rate (syllabes par seconde)
    duration = analysis['duration']  # Durée totale de l'audio en secondes
    speech_rate = syllable_count / duration

    print(f"Speech Rate: {speech_rate:.2f} syllables per second")



def estimate_speech_rate(audio_file, threshold=0.02, frame_length=1024, hop_length=512):
    # TODO investigate how calculate speech rate
    # Charger l'audio
    waveform, sr = torchaudio.load(audio_file)
    waveform = waveform.mean(dim=0)  # convertir en mono si nécessaire

    # Calculer l'énergie du signal par frame
    energy = waveform.unfold(0, frame_length, hop_length).pow(2).mean(dim=1)

    # Détecter les frames au-dessus du seuil → approximation des syllabes
    onsets = (energy > threshold).nonzero(as_tuple=True)[0]

    # Speech rate approximatif
    duration = waveform.shape[0] / sr
    pdb.set_trace()
    return len(onsets) / duration if duration > 0 else 0

# Load audio
for i in range(1,2):
    wav_path = 'data/1.wav'
    wav,sr=load_audio(wav_path)
    speech_timestamps = apply_vad(wav, sr)
    textgrid_path=create_TextGrid(wav_path,speech_timestamps, wav, sr)
    speech_intervals,silent_intervals = get_vad_intervals(textgrid_path)
    smoothed_envelope=compute_envelope(wav, sr,speech_intervals)
    amplitude, std_dev, coef_var= compute_monotony(smoothed_envelope)
    print("amplitude: ",amplitude)
    print("std_dev: ",std_dev)
    print("coef_var: ",coef_var)
    mpd=mean_pause_duration(silent_intervals)
    print("mean pause duration: ",mpd)
    estimate_speech_rate(wav_path)



