# -*- coding: utf-8 -*-
"""bt_gru_attention.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1R0ffsvkgQM7TmRDY86cuI3fBnl_FVRyu
"""

from google.colab import drive
drive.mount('/content/drive')

pip install googletrans==4.0.0-rc1

import json
from operator import itemgetter
from itertools import groupby
import numpy as np

import sys
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# device = 'cpu'
print(device)

import torch
import torch.nn.functional as F
import torch.nn as nn
import torch.optim as optim
import numpy as np
# import spacy
import random
import pandas as pd
from sklearn.model_selection import train_test_split
import re
import time
import json

f = open('/content/drive/MyDrive/Project_files/training.te-en.en.txt', 'r')
g = open('/content/drive/MyDrive/Project_files/training.te-en.te.txt', 'r')
x_en = f.read()
y_te = g.read()
telugu = x_en.split('\n')
captions = y_te.split('\n')
print(telugu[1002])

inputs=[]
outputs=[]
para_en = []
para_te = []
for x in range(len(captions[0:5000])):
  sentence = []
  sent_te = []
  for y in captions[x].split(' '):
    sentence.append(y)
  for y in telugu[x].split(' '):
    sent_te.append(y)
  para_en.append(sentence)
  para_te.append(sent_te)

for x in range(len(para_te)):
  inputs.append(para_te[x])
  outputs.append(para_en[x])

print(inputs)
print(outputs)

input_tokens=[]
output_tokens=[]
input_vocab=[]
output_vocab=[]
for i in range(len(inputs)):
  # words=Tokenization(inputs[i])
  words = inputs[i]
  tokens=[]
  tokens.append("<s>")
  tokens=tokens+words
  tokens.append("<e>")
  input_tokens.append(tokens)
  input_vocab+=words
  # words=Tokenization(outputs[i])
  words = outputs[i]
  tokens=[]
  tokens.append("<s>")
  tokens=tokens+words
  tokens.append("<e>")
  output_tokens.append(tokens)
  output_vocab+=words

input_vocab.append("<s>")
input_vocab.append("<e>")
output_vocab.append("<s>")
output_vocab.append("<e>")
input_vocab.append("<unk>")
output_vocab.append("<unk>")
input_vocab.append("<pad>")
output_vocab.append("<pad>")
# inputs=[]
# outputs=[]
print(len(input_tokens))

inputV_to_txt={}
outputV_to_txt={}
key=0
for i in range(len(input_vocab)):
  if input_vocab[i] in inputV_to_txt:
    continue
  else :
    inputV_to_txt[input_vocab[i]]=key
    key+=1
key=0
for i in range(len(output_vocab)):
  if output_vocab[i] in outputV_to_txt:
    continue
  else :
    outputV_to_txt[output_vocab[i]]=key
    key+=1
print(inputV_to_txt)
print(outputV_to_txt)

number_to_txt={}
for x in inputV_to_txt:
  number_to_txt[inputV_to_txt[x]]=x

number_to_en={}
for x in outputV_to_txt:
  # number_to_txt[outputV_to_txt[x]]=x
  number_to_en[outputV_to_txt[x]]=x

print(number_to_txt)
print(number_to_en)

input_maxlength=0
output_maxlength=0
max_length=0
print(len(input_tokens))
for i in range(len(input_tokens)):
  if len(input_tokens[i])>input_maxlength:
    input_maxlength=len(input_tokens[i])
  if len(output_tokens[i])>output_maxlength:
    output_maxlength=len(output_tokens[i])

if input_maxlength>output_maxlength:
  max_length=input_maxlength
else:
  max_length=output_maxlength

print(len(input_tokens))
for i in range(len(input_tokens)):
  input_tokens[i]=input_tokens[i]+["<pad>"]*(max_length-len(input_tokens[i]))
  output_tokens[i]=output_tokens[i]+["<pad>"]*(max_length-len(output_tokens[i]))
for i in range(len(input_tokens)):
    print(input_tokens[i])

import torch
import torch.nn.functional as F
import torch.nn as nn
import torch.optim as optim
import numpy as np
# import spacy
import random
import pandas as pd
from sklearn.model_selection import train_test_split
import re
import time
import json

final_input=[]
final_output=[]
for i in range(len(input_tokens)):
  word_T=[]
  for word in input_tokens[i]:
    if inputV_to_txt.get(word)!=None:
      word_T.append(int(inputV_to_txt[word]))
    else :
      word_T.append(int(inputV_to_txt.get("<unk>")))
  final_input.append(word_T)
  word_S=[]
  for word in output_tokens[i]:
    if word in outputV_to_txt:
      word_S.append(int(outputV_to_txt[word]))
      # print(outputV_to_txt[word],word)
    else :
      word_S.append(int(outputV_to_txt.get("<unk>")))
    # print(word_S)
  
  final_output.append(word_S)


# input_tokens=[]
# outtput_tokens=[]

print(final_input)

final_input=np.array(final_input)
final_output=np.array(final_output)
# device = 'cpu'
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
f_input = torch.LongTensor(final_input).to(device)
f_output = torch.LongTensor(final_output).to(device)

batch_wiseinput=torch.split(f_input,128)
batch_wiseoutput=torch.split(f_output,128)

batchs_f=[]
for i in range(0,len(batch_wiseinput)):
  batchs_f.append((batch_wiseinput[i],batch_wiseoutput[i]))
print(len(batchs_f))
print(len(batchs_f[0]))
f_output=[]
f_input=[]

class Encoder(nn.Module):
    
    def __init__(self, input_size, embedding_size, hidden_size, decoder_hidden_size, num_layers, dropout):
        super(Encoder, self).__init__()
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size * 2, decoder_hidden_size)
        self.embedding = nn.Embedding(input_size, embedding_size)
        self.rnn = nn.GRU(embedding_size, hidden_size, bidirectional=True)

    def forward(self, x):
        embedding = self.dropout(self.embedding(x))
        # print(np.shape(embedding),"embedding")
        outputs, hidden = self.rnn(embedding)
        # print(np.shape(hidden))
        # print(np.shape(outputs))
        temp = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim = 1)
        # print(np.shape(temp))
        hidden = torch.tanh(self.fc(temp))
        return hidden, outputs

class Decoder(nn.Module):
    
    def __init__(
        self, embedding_size, encoding_hidden_size, hidden_size, output_size, num_layers, dropout):
        super(Decoder, self).__init__()
        self.output_size = output_size
        self.dropout = nn.Dropout(dropout)
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.attn = nn.Linear((encoding_hidden_size * 2) + hidden_size, hidden_size)
        self.embedding = nn.Embedding(output_size, embedding_size)
        self.v = nn.Linear(hidden_size, 1, bias = False)
        self.rnn = nn.GRU((encoding_hidden_size * 2) + embedding_size, hidden_size)
        self.fc = nn.Linear((encoding_hidden_size * 2) + hidden_size + embedding_size , output_size)

    def forward(self, x, hidden, cell):
        x = x.unsqueeze(0)
        # print(np.shape(x),"x")
        embedding = self.dropout(self.embedding(x))
        # print(np.shape(embedding))
#         print('hi',hidden.shape, cell.shape[0])
        hidden1 = hidden.unsqueeze(1).repeat(1, cell.shape[0], 1)
        # print(np.shape(hidden1),"hidden1")
        cell1 = cell.permute(1, 0, 2)
        # print(np.shape(cell1),"cell1")
        temp = torch.cat((hidden1, cell1), dim = 2)
        # print(np.shape(temp),"temp")
        energy = torch.tanh(self.attn(temp))
        # print(np.shape(energy),"energy")
        attention = self.v(energy).squeeze(2)
        # print(np.shape(attention),"attention")
        a = F.softmax(attention, dim=1)
        # print(np.shape(a),"a")
        a = a.unsqueeze(1)
        # print(np.shape(a),"SS")
        cell1 = cell.permute(1, 0, 2)
        # print(np.shape(cell1),"cell1")
        weighted = torch.bmm(a, cell1)
        # print(np.shape(weighted),"weighted")
        weighted = weighted.permute(1, 0, 2)
        # print(np.shape(weighted),"weighted")
        # print(np.shape(embedding),np.shape(weighted))
        rnn_input = torch.cat((embedding, weighted), dim = 2)
        # print(np.shape(rnn_input),"rr")
#         hidden = hidden.reshape(1, hidden.shape[0], hidden.shape[1])
#         print(rnn_input.shape, hidden.shape)
        output, hidden = self.rnn(rnn_input, hidden.unsqueeze(0))
        # print(np.shape(output),np.shape(hidden))
        x = torch.cat((output.squeeze(0), weighted.squeeze(0), embedding.squeeze(0)), dim = 1)
        predictions = self.fc(x)       
        return predictions, hidden.squeeze(0)

'''
Creating the Model
'''
class Seq2Seq(nn.Module):
    
    def __init__(self, encoder, decoder):
        super(Seq2Seq, self).__init__()
        self.encoder = encoder
        self.decoder = decoder
        
    def forward(self, source, target, teacher_force_ratio=0.5):
        batch_size = source.shape[1]
        target_len = target.shape[0]
        target_vocab_size = self.decoder.output_size
        outputs = torch.zeros(target_len, batch_size, target_vocab_size).to(device)
        hidden, cell = self.encoder(source)
        x = target[0]
        for t in range(1, target_len):
            output, hidden = self.decoder(x, hidden, cell)
            outputs[t] = output
            teacher_force = random.random() < teacher_force_ratio
            best_guess = output.argmax(1)
            x = target[t] if random.random() < teacher_force else best_guess
        return outputs

'''
Important Parmeters
'''
num_epochs = 5
learning_rate = 0.03
batch_size = 128

'''
HyperParameters
'''
load_model = False
# device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')
# device = 'cpu'
device = 'cuda' if torch.cuda.is_available() else 'cpu'
input_size_encoder = len(inputV_to_txt)
input_size_decoder = len(outputV_to_txt)
output_size = len(outputV_to_txt)
num_layers = 1
enc_dropout = 0.5
dec_dropout = 0.5
# device = 'cpu'

encoder_net = Encoder(input_size_encoder, 128,256,256,1, enc_dropout).to(device)
decoder_net = Decoder(128, 256, 256, output_size, num_layers, dec_dropout).to(device)

from sklearn import model_selection
'''
Initiating Model
'''
def init_weights(m):
    for name, param in m.named_parameters():
        nn.init.uniform_( param.data, -0.08, 0.08 )

model = Seq2Seq(encoder_net, decoder_net).to(device)
model.apply( init_weights )
'''
Using Adam Optimizer
'''
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

pad_idx = inputV_to_txt["<pad>"]
criterion = nn.CrossEntropyLoss(ignore_index = pad_idx)

def train(model, iterator, optimizer, criterion, clip):
    model.train()

    epoch_loss = 0

    for i, batch in enumerate( iterator ):
        source = batch[0]
        target = batch[1]

        optimizer.zero_grad()

        output = model( source, target )

        output_dim = output.shape[-1]

        output = output[1:].view( -1, output_dim )
        target = target[1:].view( -1 )

        loss = criterion( output, target )

        loss.backward()

        # torch.nn.utils.clip_grad_norm_( model.parameters(), clip )

        optimizer.step()

        epoch_loss += loss.item()

    return epoch_loss / len( iterator )

for x in range(5):
  print(train(model,batchs_f,optimizer,criterion,1))

torch.save(model.state_dict(),'/content/drive/MyDrive/Project_files/btgruattent5.pth')

paraphased_sentence = []
def evaluation():
    # sentence = sentence.split()
    sentence= ['<s>', 'shiya', 'fasting,Knowledge', 'workstations,', 'demand', 'teginchi', 'fasting,Knowledge', 'demand', 'demand', 'demand', 'demand']

    print(sentence)
    sent = []
    # sentence=[inputV_to_txt[token]for token in sentence]
    for token in sentence:
        if token in inputV_to_txt:
            sent.append(inputV_to_txt[token])
        else:
            sent.append(inputV_to_txt["<unk>"])
    pred = sentence
    sentence = sent
    print(sentence)
    sentence.insert(0, inputV_to_txt["<s>"])
    print(sentence)
    sentence.append(inputV_to_txt["<e>"])
    print(sentence)
    sentence_tensor = torch.LongTensor(sentence).unsqueeze(1).to(device)
    with torch.no_grad():
            hidden, cell = model.encoder(sentence_tensor)
    print(inputV_to_txt["<s>"])
    outputs = [outputV_to_txt["<s>"]]
    print(outputs)
    for _ in range(len(sentence_tensor)):
        previous_word = torch.LongTensor([outputs[-1]]).to(device)
        print(previous_word)
        with torch.no_grad():
            output, hidden = model.decoder(previous_word, hidden, cell)
            best_guess = output.argmax(1).item()
        outputs.append(best_guess)
        if output.argmax(1).item() == outputV_to_txt["<e>"]:
          print("yuhh")
          break
    print(outputs)
    paraphased_sentence = [number_to_en[idx] for idx in outputs]
    print(paraphased_sentence[1:])
    return paraphased_sentence

model.load_state_dict(torch.load('/content/drive/MyDrive/Project_files/btgruattent5.pth'))

# validation
inputs=[]
outputs=[]
para_en = []
para_te = []
for x in range(len(captions[5000:6000])):
  sentence = []
  sent_te = []
  for y in captions[x].split(' '):
    sentence.append(y)
  for y in telugu[x].split(' '):
    sent_te.append(y)
  para_en.append(sentence)
  para_te.append(sent_te)

for x in range(len(para_te)):
  inputs.append(para_te[x])
  outputs.append(para_en[x])

print(inputs)
print(outputs)

input_tokens=[]
output_tokens=[]
input_vocab=[]
output_vocab=[]
for i in range(len(inputs)):
  # words=Tokenization(inputs[i])
  words = inputs[i]
  tokens=[]
  tokens.append("<s>")
  tokens=tokens+words
  tokens.append("<e>")
  input_tokens.append(tokens)
  input_vocab+=words
  # words=Tokenization(outputs[i])
  words = outputs[i]
  tokens=[]
  tokens.append("<s>")
  tokens=tokens+words
  tokens.append("<e>")
  output_tokens.append(tokens)
  output_vocab+=words

for i in range(len(input_tokens)):
  input_tokens[i]=input_tokens[i]+["<pad>"]*(max_length-len(input_tokens[i]))
  output_tokens[i]=output_tokens[i]+["<pad>"]*(max_length-len(output_tokens[i]))

final_input=[]
final_output=[]
for i in range(len(input_tokens)):
  word_T=[]
  for word in input_tokens[i]:
    if inputV_to_txt.get(word)!=None:
      word_T.append(int(inputV_to_txt[word]))
    else :
      word_T.append(int(inputV_to_txt.get("<unk>")))
  final_input.append(word_T)
  word_S=[]
  for word in output_tokens[i]:
    if word in outputV_to_txt:
      word_S.append(int(outputV_to_txt[word]))
      # print(outputV_to_txt[word],word)
    else :
      word_S.append(int(outputV_to_txt.get("<unk>")))
    # print(word_S)
  
  final_output.append(word_S)

final_input=np.array(final_input)
final_output=np.array(final_output)
# device = 'cpu'
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
f_input = torch.LongTensor(final_input).to(device)
f_output = torch.LongTensor(final_output).to(device)
batch_wiseinput=torch.split(f_input,128)
batch_wiseoutput=torch.split(f_output,128)

batchs_f=[]
for i in range(0,len(batch_wiseinput)):
  batchs_f.append((batch_wiseinput[i],batch_wiseoutput[i]))
print(len(batchs_f))
print(len(batchs_f[0]))
f_output=[]
f_input=[]

for i in range(5):
    epoch_loss = 0
    for i, batch in enumerate(batchs_f):
            source = batch[0]
            target = batch[1]

            optimizer.zero_grad()

            output = model( source, target )

            output_dim = output.shape[-1]

            output = output[1:].view( -1, output_dim )
            target = target[1:].view( -1 )

            loss = criterion( output, target )

            loss.backward()

            # torch.nn.utils.clip_grad_norm_( model.parameters(), clip )

            optimizer.step()

            epoch_loss += loss.item()

            print(epoch_loss / len( batchs_f ))

sentence = input()
paraphased_sentence = evaluation(sentence,model)





import nltk
from nltk.translate import meteor_score
nltk.download('wordnet')
print(paraphased_sentence)
pred = ['ఈ', 'కాలము', 'భారతదేశము', 'ఓ', 'పెద్ద', 'సాంఘిక', 'మార్పు', 'చవిచూసినది.']
score = meteor_score.meteor_score([pred],paraphased_sentence)
print("METEOR score:", score*109)

