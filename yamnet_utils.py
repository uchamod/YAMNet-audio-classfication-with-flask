# yamnet_utils.py
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import scipy.signal
import csv
from scipy.io import wavfile

# Load YAMNet model and class labels
model = hub.load("https://tfhub.dev/google/yamnet/1")

def class_names_from_csv(csv_path):
    class_names = []
    with tf.io.gfile.GFile(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            class_names.append(row['display_name'])
    return class_names

class_map_path = model.class_map_path().numpy()
class_names = class_names_from_csv(class_map_path)

def ensure_sample_rate(original_sr, waveform, target_sr=16000):
    if original_sr != target_sr:
        desired_length = int(round(len(waveform) * float(target_sr) / original_sr))
        waveform = scipy.signal.resample(waveform, desired_length)
    return target_sr, waveform

def predict_sound(filepath):
    sample_rate, wav_data = wavfile.read(filepath)
    sample_rate, wav_data = ensure_sample_rate(sample_rate, wav_data)
    waveform = wav_data / tf.int16.max
    scores, _, _ = model(waveform)
    scores_np = scores.numpy()
    mean_scores = scores_np.mean(axis=0)
    top_class = class_names[mean_scores.argmax()]
    return top_class
