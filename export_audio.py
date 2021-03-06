from librosa.output import write_wav
from librosa.util import normalize
import numpy as np
from parameters import WINDOW_SIZE, OVERLAP, NPERSEG
import scipy.signal

def render_audio(model_output, path, sr, window_size=WINDOW_SIZE, overlap=OVERLAP):
    rendered = np.zeros(window_size * model_output.shape[0])
    r_index = 0
    for i in range(model_output.shape[0]):
        for j in range(model_output[i].shape[0] - overlap):
            if j < overlap:
                if i > 0:
                    amp_factor = j / float(overlap)
                    rendered[r_index + j] = (model_output[i][j] * amp_factor) + (model_output[i-1][model_output[i-1].shape[0] - 1 - overlap + j] * (1-amp_factor))
            else:
                rendered[r_index + j] = float(model_output[i][j])
        r_index += (window_size - overlap - 1)
    rendered = np.array(rendered)
    rendered = normalize(rendered)
    write_wav(path, rendered, sr)

def render_audio_s(model_output, path, sr):
    print("Rendering audio from STFT...")

    model_output = model_output / 1e8
    complexed = []
    for i in range(model_output.shape[0]):
        for j in range(model_output.shape[2]):
            complexed_frame = []
            for k in range(model_output.shape[3]):
                complexed_frame.append(np.complex(model_output[i, 0, j, k], model_output[i, 1, j, k]))
            complexed.append(complexed_frame)
    complexed = np.array(complexed)

    # Thank you Eric O Lebigot on https://stackoverflow.com/questions/2598734/numpy-creating-a-complex-array-from-2-real-ones for this one:
    # complexed = np.apply_along_axis(lambda args: complex(*args), 2, model_output)
    _, inverse = scipy.signal.istft(complexed.T, fs=sr, nperseg=NPERSEG, window='hann')
    rendered = normalize(inverse)
    write_wav(path, rendered, sr)