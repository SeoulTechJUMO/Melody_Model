import keras
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.utils import np_utils
from keras.layers.core import Dropout
from keras.models import load_model
import midiparser
import note_tools
import time
import glob
import os
import pickle
import matplotlib.pyplot as plt
import shutil

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

def make_model(kinds,weight_num,drop_rate,one_hot_vec_size):
    #이전 가중치 정보가 있다면 로드
    if glob.glob("model_save/"+kinds+".h5"):
        for file in glob.glob("model_save/"+kinds+"_model.h5"):
            model.load_model(file)
    else:
        model = Sequential()
        model.add(LSTM(weight_num, return_sequences=True, batch_input_shape = (1, 4, 2), stateful=True, kernel_initializer='he_normal'))
        model.add(LSTM(weight_num, return_sequences=False, kernel_initializer='he_normal'))
        model.add(Dropout(drop_rate))

        model.add(Dense(one_hot_vec_size, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

#학습하기
def exec_learn(track_list,mode):
    num_epochs = 300
    weight_num = 256
    dropout_rate = 0.2
    window_size = 4
    seq_length = 200

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

    #데이터셋 생성
    x_train, y_train = seq2dataset(seq, window_size, note_dict[tonic])

    #입력을 (샘플 수, 타임스텝, 특성 수)로 형태 변환
    x_train = np.reshape(x_train, (len(seq)-window_size, 4, 2))

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
        model.append(make_model('major',weight_num,dropout_rate,one_hot_vec_size_note))
    elif kinds == 'minor':
        model.append(make_model('minor',weight_num,dropout_rate,one_hot_vec_size_note))

    #beat모델
    model.append(make_model('beat',weight_num,dropout_rate,one_hot_vec_size_beat))

    for i in range(len(model)):
        history.append(LossHistory())
        history[i].init()

    #모델 학습
    for epoch_idx in range(num_epochs):
        print ('epochs : ' + str(epoch_idx))
        for i,each_model in enumerate(model):
            each_model.fit(x_train, y_label[i], epochs=1, batch_size=1, verbose=2, shuffle=False, callbacks=[history[i]])
            each_model.reset_states()

    #한곡의 학습이 끝나면 저장
    model[0].save("model_save/"+kinds+"_model.h5")
    model[1].save("model_save/beat_model.h5")
    
    for i, his in history:
        plt.plot(his.losses)
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.legend(['train'], loc='upper left')
        plt.show()

    #모델 평가하기
    scores_note = model[0].evaluate(x_train, y_label[0], batch_size=1)
    scores_beat = model[1].evaluate(x_train, y_label[1], batch_size=1)
    print("%s: %.2f%%" %(model[0].metrics_names[1], scores[1]*100))
    print("%s: %.2f%%" %(model[1].metrics_names[1], scores[1]*100))

    model[0].reset_states()
    model[1].reset_states()


#모델 사용하기
def using_model():
    pred_count = len(seq)-1 # 최대 예측 개수 정의

    seq_out = seq[:4]
    pred_out = model.predict(x_train, batch_size=1)

    for i in range(pred_count):
        idx = np.argmax(pred_out[i]) # one-hot 인코딩을 인덱스 값으로 변환
        #print(pred_out[i])
        print(idx)
        #seq_out.append(idx2code[idx]) # seq_out는 최종 악보이므로 인덱스 값을 코드로 변환하여 저장
    
    print("one step prediction : ", seq_out)


beat2idx = {'128':0, '96':1, '64':2, '48':3, '32':4, '24':5, '16':6, 
            '12':7, '8':8, '6':9, '4':10, '3':11, '2':12, '1.5':13, 
            '1':14, '0.75':15, '0.5':16}
note_dict = { 'c':0, 'c#':1, 'd':2, 'd#':3, 'e':4, 'f':5, 'f#':6,
            'g':7, 'g#':8, 'a':9, 'a#':10, 'b':11}

max_pitch_val = 128.0
max_beat_val = 16.0

ticks = 96
bpm = 120

for file in glob.glob("data/*.bin"):
    with open(file,'rb') as song:
        song_list = pickle.load(song)
    
    for song in song_list:
        exec_learn(song[0],song[1])
    
    #학습완료한 데이터는 이동
    shutil.move(file,"data/complete")
