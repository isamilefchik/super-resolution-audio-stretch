import math
import numpy as np
import torch
import scipy.signal
import matplotlib.pyplot as plt
from parameters import WINDOW_SIZE, OVERLAP, NPERSEG, BATCHES_PER_EPOCH, FRAMES_PER_BATCH

# Takes input mono audio track, stretches it to twice its length (interpolating
# samples through average of adjacent samples), and splits into arrays of
# window_size.
def preprocess_input_data(src, window_size=WINDOW_SIZE, overlap=OVERLAP):
    if not isinstance(src.shape[0], int):
        raise ValueError("Non-mono track input.")
    
    print("Preprocessing input...")
    double_length = np.zeros(2 * len(src))
    for i in range(double_length.shape[0]):   
        # Interpolate audio 
        if i % 2:
            if math.ceil(i / 2.0) < src.shape[0]:
                double_length[i] = (src[int(math.floor(i / 2.0))] \
                                    + src[int(math.ceil(i / 2.0))]) / 2.0
        else:
            double_length[i] = src[int(i / 2)]
        
        # Print progress
        if i % 100000 == 0 or i == double_length.shape[0] - 1:
            progress = 100 * ((i + 1) / double_length.shape[0])
            if progress != 100:
                progress = str(progress)[:4]
                print('   Stretching audio: {}% complete   '.format(progress), end='\r')
            else:
                print('   Stretching audio: 100% complete   ')

    window_split = window_splitter(double_length, window_size, overlap)
    return window_split

# Splits target audio into arrays of window_size
def preprocess_target_data(src, window_size=WINDOW_SIZE, overlap=OVERLAP):
    return window_splitter(src, window_size, overlap)

def preprocess_input_data_s(src):
    if not isinstance(src.shape[0], int):
        raise ValueError("Non-mono track input.")

    print("Preprocessing input...")
    double_length = np.zeros(2 * len(src))
    for i in range(double_length.shape[0]):   
        # Interpolate audio 
        if i % 2:
            if math.ceil(i / 2.0) < src.shape[0]:
                double_length[i] = (src[int(math.floor(i / 2.0))] \
                                    + src[int(math.ceil(i / 2.0))]) / 2.0
        else:
            double_length[i] = src[int(i / 2)]

        # Print progress
        if i % 100000 == 0 or i == double_length.shape[0] - 1:
            progress = 100 * ((i + 1) / double_length.shape[0])
            if progress != 100:
                progress = str(progress)[:4]
                print('   Stretching audio: {}% complete   '.format(progress), end='\r')
            else:
                print('   Stretching audio: 100% complete   ')

    return double_length

# Splits audio into windows of WINDOW_SIZE, with OVERLAP samples
# overlapping between each window
def window_splitter(src, window_size=WINDOW_SIZE, overlap=OVERLAP):
    window_split = []
    i = 0
    while i < (src.shape[0] - window_size):
        window_split.append(src[i:(i+window_size)])
        i += window_size - overlap - 1
    return np.array(window_split)

def generate_spectrogram(src, sr):
    return scipy.signal.stft(src, fs=sr, nperseg=NPERSEG, window='hann')[2].T

def pre_model_prepare(input_audio, target_audio):
    input_audio = preprocess_input_data(input_audio, WINDOW_SIZE)
    target_audio = preprocess_target_data(target_audio, WINDOW_SIZE)
    assert input_audio.shape[0] == target_audio.shape[0]
    return input_audio, target_audio

def post_model_prepare(input_audio, target_audio):
    input_audio = window_splitter(input_audio, int(WINDOW_SIZE / 2), int(OVERLAP / 2))
    target_audio = window_splitter(target_audio, WINDOW_SIZE)
    return input_audio, target_audio

def pre_model_s_prepare(input_audio, target_audio, sr):
    input_audio = preprocess_input_data_s(input_audio)
    assert input_audio.shape[0] == target_audio.shape[0]

    input_s = generate_spectrogram(input_audio, sr)
    target_s = generate_spectrogram(target_audio, sr)
    assert input_s.shape[0] == target_s.shape[0], "Dimension 0 of generated spectrograms do not match"
    assert input_s.shape[1] == target_s.shape[1], "Dimension 1 of generated spectrograms do not match"


    for i, frame in enumerate(input_s):
        for j, freq_bin in enumerate(frame):
            if not isinstance(freq_bin.real, np.float64):
                print(freq_bin)
            if not isinstance(freq_bin.imag, np.float64):
                print(freq_bin)


    input_formatted = []
    target_formatted = []
    i = 0
    while i < (input_s.shape[0] - FRAMES_PER_BATCH):
        input_formatted.append([input_s[i:i+FRAMES_PER_BATCH].real, input_s[i:i+FRAMES_PER_BATCH].imag])
        target_formatted.append([target_s[i:i+FRAMES_PER_BATCH].real, target_s[i:i+FRAMES_PER_BATCH].imag])
        i += FRAMES_PER_BATCH

    end_pad = np.zeros((FRAMES_PER_BATCH - (input_s.shape[0] - i), input_s.shape[1]))
    temp_input_r = np.append(input_s[i:].real, end_pad, axis=0)
    temp_input_i = np.append(input_s[i:].imag, end_pad, axis=0)
    temp_target_r = np.append(target_s[i:].real, end_pad, axis=0)
    temp_target_i = np.append(target_s[i:].imag, end_pad, axis=0)
    input_formatted.append([temp_input_r, temp_input_i])
    target_formatted.append([temp_target_r, temp_target_i])

    input_formatted = np.array(input_formatted, dtype=np.float)
    target_formatted = np.array(target_formatted, dtype=np.float)

    input_formatted = input_formatted * 1e4
    target_formatted = target_formatted * 1e4

    input_batches = np.array_split(input_formatted, BATCHES_PER_EPOCH)
    target_batches = np.array_split(target_formatted, BATCHES_PER_EPOCH)

    for i, batch in enumerate(input_batches):
        if (batch.shape != target_batches[i].shape):
            print("Input batch: " + str(i) + " \tShape: " + str(batch.shape))
            print("Target batch: " + str(i) + " \tShape: " + str(target_batches[i].shape))

    for i in range(len(input_batches)):
        input_batches[i] = torch.tensor(input_batches[i], dtype=torch.double)
        target_batches[i] = torch.tensor(target_batches[i], dtype=torch.double)
    
    return input_batches, target_batches
