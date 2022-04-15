import tensorflow as tf
import os
import re
import numpy as np
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
MAX_LENGTH = 13
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
VOCAB_SIZE = len(tokenizer.word_index) + 1


enc_model = load_model('enc_model.h5')
dec_model = load_model('dec_model.h5')

def sentence2tokens(sentence: str):
    words = sentence.lower().split()
    tokens_list = list()
    for current_word in words:
        result = tokenizer.word_index.get(current_word, '')
        if result != '':
            tokens_list.append(result)
    return pad_sequences([tokens_list], maxlen=MAX_LENGTH, padding='post')


def chat(text):
    # encode the input sequence into state vectors
    states_values = enc_model.predict(sentence2tokens(text))
    # start with a target sequence of size 1 - word 'start'   
    empty_target_seq = np.zeros((1, 1))
    empty_target_seq[0, 0] = tokenizer.word_index['start']
    stop_condition = False
    decoded_translation = ''
    while not stop_condition:
        # feed the state vectors and 1-word target sequence 
        # to the decoder to produce predictions for the next word
        dec_outputs, h, c = dec_model.predict([empty_target_seq] 
                                              + states_values)         
        # sample the next word using these predictions
        sampled_word_index = np.argmax(dec_outputs[0, -1, :])
        sampled_word = None
        # append the sampled word to the target sequence
        for word, index in tokenizer.word_index.items():
            if sampled_word_index == index:
                if word != 'end':
                    decoded_translation += ' {}'.format(word)
                sampled_word = word
        if sampled_word == 'end' or len(decoded_translation.split()) > MAX_LENGTH:
            stop_condition = True
        # prepare next iteration
        empty_target_seq = np.zeros((1, 1))
        empty_target_seq[0, 0] = sampled_word_index
        states_values = [h, c]

    return decoded_translation