import re
import numpy as np
from time import time
import matplotlib.pyplot as plt
import pickle
import tensorflow as tf
import random

D_MODEL = 100
max_len = 16


def clean_sentence(sentence):
  sentence = sentence.lower().strip()
  # creating a space between a word and the punctuation following it
  # eg: "he is a boy." => "he is a boy ."
  sentence = re.sub(r"([?.!,])", r" \1 ", sentence)
  sentence = re.sub(r'[" "]+', " ", sentence)
  # removing contractions
  sentence = re.sub(r"i'm", "i am", sentence)
  sentence = re.sub(r"he's", "he is", sentence)
  sentence = re.sub(r"she's", "she is", sentence)
  sentence = re.sub(r"it's", "it is", sentence)
  sentence = re.sub(r"that's", "that is", sentence)
  sentence = re.sub(r"there's", "there is", sentence)
  sentence = re.sub(r"'til", "until", sentence)
  sentence = re.sub(r"what's", "that is", sentence)
  sentence = re.sub(r"where's", "where is", sentence)
  sentence = re.sub(r"how's", "how is", sentence)
  sentence = re.sub(r"\'ll", " will", sentence)
  sentence = re.sub(r"\'ve", " have", sentence)
  sentence = re.sub(r"\'re", " are", sentence)
  sentence = re.sub(r"\'d", " would", sentence)
  sentence = re.sub(r"\'re", " are", sentence)
  sentence = re.sub(r"won't", "will not", sentence)
  sentence = re.sub(r"can't", "cannot", sentence)
  sentence = re.sub(r"n't", " not", sentence)
  sentence = re.sub(r"n'", "ng", sentence)
  sentence = re.sub(r"'bout", "about", sentence)
  # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
  sentence = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", sentence)
  sentence = re.sub(r"[^a-zA-Z?.!,]+", " ", sentence)
  sentence = sentence.strip()
  return sentence

def create_padding_mask(x):
  mask = tf.cast(tf.math.equal(x, 0), tf.float32)
  # (batch_size, 1, 1, sequence length)
  return mask[:, tf.newaxis, tf.newaxis, :]

def create_look_ahead_mask(x):
  seq_len = tf.shape(x)[1]
  look_ahead_mask = 1 - tf.linalg.band_part(tf.ones((seq_len, seq_len)), -1, 0)
  padding_mask = create_padding_mask(x)
  return tf.maximum(look_ahead_mask, padding_mask)

def loss_function(y_true, y_pred):
  y_true = tf.reshape(y_true, shape=(-1, max_len - 1))
  
  loss = tf.keras.losses.SparseCategoricalCrossentropy(
      from_logits=True, reduction='none')(y_true, y_pred)

  mask = tf.cast(tf.not_equal(y_true, 0), tf.float32)
  loss = tf.multiply(loss, mask)

  return tf.reduce_mean(loss)


class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):

  def __init__(self, d_model, warmup_steps=4000):
    super(CustomSchedule, self).__init__()
    
    self.d_model = tf.constant(d_model,dtype=tf.float32)
    self.warmup_steps = warmup_steps
    
  def get_config(self):
        return {"d_model": self.d_model,"warmup_steps":self.warmup_steps}
    
  def __call__(self, step):
    arg1 = tf.math.rsqrt(step)
    arg2 = step * (self.warmup_steps**-1.5)

    return tf.math.multiply(tf.math.rsqrt(self.d_model), tf.math.minimum(arg1, arg2))


def evaluate(sentence):
  sentence = clean_sentence(sentence)

  sentence = tf.expand_dims(start_token + tokenizer.texts_to_sequences([sentence])[0] + end_token, axis=0)
  output = tf.expand_dims(start_token, 0)

  for i in range(max_len):
    predictions = model(inputs=[sentence, output], training=False)

    # select the last word from the seq_len dimension
    predictions = predictions[:, -1:, :]
    maxid = tf.argmax(predictions, axis=-1) 

    if maxid == end_token: 
      selected = maxid
    else:  #beam search with beamwidth = 3
      candidates = tf.argsort(predictions, axis=-1, direction='ASCENDING')[:,:,-3:] #select three maximum candidate words
      selected = random.choice(np.squeeze(candidates)) #randomly choice one word
      selected = np.expand_dims(np.expand_dims(selected, axis=0), axis=0) #expand dims [[value]]

    predicted_id = tf.cast(selected, tf.int32)

    # return the result if the predicted_id is equal to the end token
    if tf.equal(predicted_id, end_token[0]):
      break

    # concatenated the predicted_id to the output which is given to the decoder
    # as its input.
    output = tf.concat([output, predicted_id], axis=-1)

  return tf.squeeze(output, axis=0)


def predict(sentence):
  prediction = evaluate(sentence)
  tokens = [p for p in prediction.numpy() if p < vocab_size and p != start_token and p != end_token]
  predicted_sentence = tokenizer.sequences_to_texts([tokens])[0]
  return predicted_sentence



with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
vocab_size = len(tokenizer.word_index) + 3
start_token, end_token = [len(tokenizer.word_index)], [len(tokenizer.word_index) + 1]


learning_rate = CustomSchedule(D_MODEL)
optimizer = tf.keras.optimizers.Adam(
    learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9)

def accuracy(y_true, y_pred):
  # ensure labels have shape (batch_size, max_len_q - 1)
  y_true = tf.reshape(y_true, shape=(-1, max_len_q - 1))
  return tf.keras.metrics.sparse_categorical_accuracy(y_true, y_pred)

#try except block is used to prevent model to be loaded each time the page refreshes for faster response.
try:
  model 
except:
  model = tf.keras.models.load_model('chatbotEmpty.tf')
  model.compile(optimizer=optimizer, loss=loss_function, metrics=[accuracy])
  #trained 300epochs
  model.load_weights('chatbotWeights.h5')



def chat(text):
    output = predict(text)
    return output