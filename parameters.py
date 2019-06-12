MODEL = 'pre'
# MODEL = 'post'
LOAD_MODEL = False
LOAD_MODEL_PATH = "./model_saves/pre_model_0_e4"

WINDOW_SIZE = 5000
OVERLAP = 30
NUM_EPOCHS = 5
LEARNING_RATE = 1e-5
USE_CUDA = False

MODEL_NAME = "pre_model_0"
SAVE_PATH = "./model_saves/" + MODEL_NAME
EXPORT_PATH = "./output/" + MODEL_NAME + ".wav"