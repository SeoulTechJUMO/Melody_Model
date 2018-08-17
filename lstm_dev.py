import keras
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.utils import np_utils
from keras.layers.core import Dropout
from keras.models import load_model
from keras.optimizers import adam
import midiparser
import note_tools
import time
import glob
import os
import pickle
import matplotlib.pyplot as plt
import shutil
import sys

np.random.seed(5)
delta_range = []
i = -60
for k in range(120):
    delta_range.append(i+k)

#공용 변수들
beat2idx = {'128':0, '96':1, '64':2, '48':3, '32':4, '24':5, '16':6, 
            '12':7, '8':8, '6':9, '4':10, '3':11, '2':12, '1.5':13, 
            '1':14, '0.75':15, '0.5':16}
idx2beat = {i:v for (v, i) in beat2idx.items()}
note_dict = { 'c':0, 'c#':1, 'd':2, 'd#':3, 'e':4, 'f':5, 'f#':6,
            'g':7, 'g#':8, 'a':9, 'a#':10, 'b':11}
pit2idx = {i:v for (v,i) in enumerate(delta_range)}
idx2pit = {i:v for (v,i) in pit2idx.items()}

max_pitch_val = 128.0
max_beat_val = 16.0

class LossHistory(keras.callbacks.Callback):
    def init(self):
        self.losses = []
        
    def on_epoch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))

# 데이터셋 생성 함수
def seq2dataset(seq, window_size, tonic):
    dataset_X = []
    dataset_Y = []
    
    for i in range(len(seq)-window_size):
            
        subset = seq[i:(i+window_size+1)]
            
        for j in range(len(subset)-1):
            features = makeset(subset[j])            
            dataset_X.append(features)

        dataset_Y.append(makelabel(subset[window_size],True))
        dataset_Y.append(makelabel(subset[window_size],False))

    return np.array(dataset_X), np.array(dataset_Y)

#학습 라벨 만들기
def makelabel(code,flag):
    features = []
    #노트 라벨
    if flag == True:
        features.append(code[0].note)
        return features
    #박자 라벨
    else:
        features.append(beat2idx[code[0].length])
        return features

#학습 데이터 set, 노트 + 박자
def makeset(code):
    features = []

    features.append(code[0].note/float(max_pitch_val))
    features.append(beat2idx[code[0].length]/float(max_beat_val))
    return features

def make_model(kinds,weight_num,drop_rate,one_hot_vec_size,window_size,feature):
    #이전 가중치 정보가 있다면 로드
    if glob.glob("model_save/"+kinds+".h5"):
        for file in glob.glob("model_save/"+kinds+"_model.h5"):
            model.load_model(file)
    else:
        model = Sequential()
        #model.add(LSTM(weight_num, return_sequences=True, batch_input_shape = (1, 4, 2), stateful=True))
        model.add(LSTM(weight_num, return_sequences=True, batch_input_shape = (1, window_size, feature)))
        model.add(Dropout(drop_rate))
        model.add(LSTM(weight_num, return_sequences=False))
        model.add(Dropout(drop_rate))
        
        model.add(Dense(one_hot_vec_size, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def remake_mode(seq,tonic):
    for pat in seq:
        for k in pat:
            if k.note - tonic > 0:
                k.note -= tonic
    return seq

#학습하기
def exec_learn(track_list,mode):
    num_epochs = 200
    weight_num = 512
    dropout_rate = 0.3
    window_size = 4
    seq_length = 50
    feature = 2

    history = []
    model = []
    y_note = []
    y_beat = []
    y_label = []

    #스케일 판단
    mode = mode.split()
    tonic = mode[0]
    kinds = mode[1]

    #시퀀스 데이터를 일정 크기로 자른다
    seq = track_list[:seq_length]

    #조성 조정
    seq = remake_mode(seq,note_dict[tonic])

    #데이터셋 생성
    x_train, y_train = seq2dataset(seq, window_size, note_dict[tonic])

    #입력을 (샘플 수, 타임스텝, 특성 수)로 형태 변환
    x_train = np.reshape(x_train, (len(seq)-window_size, window_size, feature))

    #라벨 음표와 박자를 구별
    for idx,i in enumerate(y_train):
        if idx%2 == 0:
            y_note.append(i)
        else:
            y_beat.append(i)

    y_label.append(y_note)
    y_label.append(y_beat)

    #라벨값에 대한 one-hot 인코딩 수행

    y_label[0] = np_utils.to_categorical(y_label[0])
    y_label[1] = np_utils.to_categorical(y_label[1])

    one_hot_vec_size_note = y_label[0].shape[1]
    one_hot_vec_size_beat = y_label[1].shape[1]

    #major, minor 모델
    if kinds == 'major':
        model.append(make_model('major',weight_num,dropout_rate,one_hot_vec_size_note,window_size,feature))
    elif kinds == 'minor':
        model.append(make_model('minor',weight_num,dropout_rate,one_hot_vec_size_note,window_size,feature))

    #beat모델
    model.append(make_model('beat',weight_num,dropout_rate,one_hot_vec_size_beat,window_size,feature))

    #모델 학습
    for epoch_idx in range(num_epochs):
        print ('epochs : ' + str(epoch_idx))
        for i,each_model in enumerate(model):
            each_model.fit(x_train, y_label[i], epochs=1, batch_size=1, verbose=2, shuffle=False)
            #each_model.reset_states()

    #한곡의 학습이 끝나면 저장
    model[0].save("model_save/"+kinds+"_model.h5")
    model[1].save("model_save/beat_model.h5")


#모델 사용하기
def using_model(pitch_model_dir,beat_model_dir,seq,window_size):
    feature = 2

    pitch_model = load_model(pitch_model_dir)
    beat_model = load_model(beat_model_dir)

    seq_out = []
    seq_in = []
    predict = []
    seq_pred = []
    pattern = []
    for i in seq:
        for j in i:
            pattern.append(j)

    for note in seq:    
        seq_in.append(makeset(note))

    for i in range(100):
        sample_in = np.array(seq_in)
        sample_in = np.reshape(seq_in, (1, window_size, feature))

        pred_out = pitch_model.predict(sample_in)
        idx = np.argmax(pred_out)
        predict.append(idx)

        pred_out = beat_model.predict(sample_in)
        idx = np.argmax(pred_out)
        predict.append(idx2beat[idx])

        seq_out.append(predict)
        seq_pred.append(predict[0]/float(max_pitch_val))
        seq_pred.append(beat2idx[predict[1]]/float(max_beat_val))
        seq_in.append(seq_pred)
        seq_in.pop(0)

        predict = []
        seq_pred = []
 
    for pat in seq_out:
        pattern.append(note_tools.pred_note(pat[0],float(pat[1])))
    return pattern

#학습 main
if __name__ == "__main__":
    count = 0
    for file in glob.glob("data/*.bin"):
        print(file)
        with open(file,'rb') as song:
            song_list = pickle.load(song)
    
        for song in song_list:        
            count += 1
            print("number of files : {} file".format(count))
            exec_learn(song[0],song[1])
            #if count == 1:
            #    sys.exit(1)

    
        #학습완료한 데이터는 이동
        shutil.move(file,"data/complete")
