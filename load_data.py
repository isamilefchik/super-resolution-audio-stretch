import math
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from parameters import WINDOW_SIZE, OVERLAP

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
    return scipy.signal.stft(src, fs=sr, nperseg=1024, window='hann')[2].T

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
    # f, t, Zxx = scipy.signal.stft(input_audio, fs=sr, window='hann')
    # plt.pcolormesh(t, f, np.abs(Zxx))
    # plt.show()
    # f, t, Zxx = scipy.signal.stft(target_audio, fs=sr, window='hann')
    # plt.pcolormesh(t, f, np.abs(Zxx))
    # plt.show()

    input_audio = preprocess_input_data_s(input_audio)
    assert input_audio.shape[0] == target_audio.shape[0]

    input_s = generate_spectrogram(input_audio, sr)
    target_s = generate_spectrogram(target_audio, sr)

    # Splits each complex number into its own array of the real
    # and imaginary components
    input_decomp = np.dstack((input_s.real, input_s.imag))
    target_decomp = np.dstack((target_s.real, target_s.imag))

    return input_decomp, target_decomp
