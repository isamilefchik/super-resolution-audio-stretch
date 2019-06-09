import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import math
import numpy as np
from librosa.core import load
from librosa.output import write_wav
import load_data
from pre_upscale_model import Pre_Upscale_Model
from post_upscale_model import Post_Upscale_Model
from hyperparameters import *

def train_model(model, input_data, target_data, optimizer, epoch):
    model.train()
    loss = nn.MSELoss()
    total_loss = 0
    # TODO
    # TODO
    # TODO
    # TODO: GET RID OF - 10
    # TODO
    # TODO
    # TODO
    sample_size = input_data.shape[0] - 10
    for i in range(sample_size):
        input_window = torch.tensor(np.array([[input_data[i]]]))
        target_window = torch.tensor(np.array([[target_data[i]]]))
        optimizer.zero_grad()
        output = model(input_window.double())
        train_loss = loss(output, target_window.double())
        train_loss.backward()
        total_loss += train_loss.sum()
        optimizer.step()
        progress = 100 * ((i + 1) / sample_size)
        if progress != 100:
            progress = str(progress)[:4]
            print('   Epoch {}: {}% complete   '.format(epoch, progress), end='\r')
        else:
            print('   Epoch {}: 100% complete   '.format(epoch))

    print('   Train Epoch: {} \tLoss: {:.6f}'.format(epoch, total_loss))

def test_model(model, input_data, target_data):
    model.eval()
    loss = nn.MSELoss()
    test_loss = 0
    stitched_audio = []
    with torch.no_grad():
        # TODO
        # TODO
        # TODO
        # TODO: GET RID OF - 10
        # TODO
        # TODO
        # TODO
        for i in range(input_data.shape[0] - 10):
            input_window = torch.tensor([[input_data[i]]])
            target_window = torch.tensor([[target_data[i]]])
            output = model(input_window.double())
            stitched_audio.append(output[0,0].numpy())
            test_loss += loss(output, target_window.double()).mean()
    
    test_loss /= input_data.shape[0]
    print('\nTest set: Average loss: {:.4f}'.format(test_loss))
    
    stitched_audio = np.array(stitched_audio)
    # stitched_audio = np.concatenate(stitched_audio, axis=None)
    return stitched_audio

def render_audio(model_output, path, sample_rate, window_size=WINDOW_SIZE, overlap=OVERLAP):
    rendered = np.zeros(window_size * model_output.shape[0])
    r_index = 0
    for i in range(model_output.shape[0]):
        for j in range(model_output[i].shape[0]):
            if j < overlap:
                rendered[r_index + j] = rendered[r_index + j] + \
                                        (model_output[i][j] * (j / float(overlap)))
            elif j >= (window_size - overlap - 1):
                rendered[r_index + j] = rendered[r_index + j] + \
                                        (model_output[i][j] * ((window_size - j - 1) / float(overlap)))
            else:
                rendered[r_index + j] = model_output[i][j]
        r_index += (window_size - overlap - 1)
    rendered = np.array(rendered)
    write_wav(path, rendered, sample_rate)

def main():
    print("Loading audio files...")
    input_audio, sr = load("./midi_renders/fugue_1_plucks.wav")
    target_audio, sr = load("./midi_renders/fugue_1_plucks_slow.wav")
    if (MODEL == 'pre'):
        input_audio = load_data.preprocess_input_data(input_audio, WINDOW_SIZE)
        target_audio = load_data.preprocess_target_data(target_audio, WINDOW_SIZE)
        assert input_audio.shape[0] == target_audio.shape[0]
    else:
        input_audio = load_data.window_splitter(input_audio, int(WINDOW_SIZE / 2), int(OVERLAP / 2))
        target_audio = load_data.window_splitter(target_audio, WINDOW_SIZE)

    device = torch.device("cuda" if USE_CUDA else "cpu")
    model = Pre_Upscale_Model().to(device) if MODEL == 'pre' else Post_Upscale_Model().to(device)
    model = model.double()
    optimizer = optim.Adam(model.parameters(), LEARNING_RATE)

    print("Training model...")
    for epoch in range(1, NUM_EPOCHS + 1):
        train_model(model, input_audio, target_audio, optimizer, epoch)
        cur_save_path = SAVE_PATH + "_e" + str(epoch)
        torch.save(model.state_dict(), cur_save_path)
        print("Saved model to " + cur_save_path)

    # input_audio, sr = load("./midi_renders/fugue_2_plucks.wav")
    # target_audio, sr = load("./midi_renders/fugue_2_plucks_slow.wav")
    # input_audio = load_data.preprocess_input_data(input_audio, WINDOW_SIZE)
    # target_audio = load_data.preprocess_target_data(target_audio, WINDOW_SIZE)
    test_result = test_model(model, input_audio, target_audio)
    render_audio(test_result, "./output/test_result.wav", sr, window_size=WINDOW_SIZE)

if __name__ == "__main__":
    main()
