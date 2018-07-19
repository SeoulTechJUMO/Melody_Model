import keras
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.utils import np_utils
from keras.layers.core import Dropout
import midiparser
import note_tools
import midigenerator

#note 0을 rest_note라고 간주한다. 노트 입력 가능 범위는 1~128
ListOfList = midiparser.make_score(r'D:\code\py\MMMake\midi\hak.mid')
ticks = midiparser.midi_ticks(r'D:\code\py\MMMake\midi\hak.mid')

# 랜덤시드 고정시키기
np.random.seed(5)

# 손실 이력 클래스 정의
class LossHistory(keras.callbacks.Callback):
    def init(self):
        self.losses = []
        
    def on_epoch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))

# 데이터셋 생성 함수
def seq2dataset(seq, window_size):
    
    dataset_X = []
    dataset_Y = []
    
    for i in range(len(seq)-window_size):
            
        subset = seq[i:(i+window_size+1)]
            
        for j in range(len(subset)-1):
            features = code2features(subset[j])            
            dataset_X.append(features)

        dataset_Y.append([code2idx[subset[window_size]]])
            
    return np.array(dataset_X), np.array(dataset_Y)

# 속성 변환 함수
def code2features(code):
    features = []

    features.append(code.note/float(max_scale_value))
    features.append(beat2length[note_tools.cal_tick_to_beat(code.length,ticks)])
    return features

# 1. 데이터 준비하기

# 코드 사전 정의

beat2length = {'64':0, '32':1, '16':2, '8':3, '4':4, '2':5, '1':6, '0.5':7}

code2idx = {'c4':0, 'd4':1, 'e4':2, 'f4':3, 'g4':4, 'a4':5, 'b4':6,
            'c8':7, 'd8':8, 'e8':9, 'f8':10, 'g8':11, 'a8':12, 'b8':13}


max_scale_value = 128.0
    
# 시퀀스 데이터 정의
seq = ListOfList[0]

# 2. 데이터셋 생성하기
window_size = 4

x_train, y_train = seq2dataset(seq, window_size)

# 입력을 (샘플 수, 타임스텝, 특성 수)로 형태 변환
x_train = np.reshape(x_train, (len(seq)-window_size, 4, 2))

# 라벨값에 대한 one-hot 인코딩 수행
y_train = np_utils.to_categorical(y_train)

one_hot_vec_size = y_train.shape[1]

print("one hot encoding vector size is ", one_hot_vec_size)
print(x_train)

'''

# 3. 모델 구성하기
model = Sequential()
model.add(LSTM(128, batch_input_shape = (1, 4, 2), stateful=True))

#model.add(LSTM(128, return_sequences=True, batch_input_shape = (1, 4, 2), stateful=True))
#model.add(Dropout(0.2))
#model.add(LSTM(128, return_sequences=False))
#model.add(Dropout(0.2))

model.add(Dense(one_hot_vec_size, activation='softmax'))
    
# 4. 모델 학습과정 설정하기
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 5. 모델 학습시키기
num_epochs = 500

history = LossHistory() # 손실 이력 객체 생성
history.init()

for epoch_idx in range(num_epochs):
    print ('epochs : ' + str(epoch_idx) )
    model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2, shuffle=False, callbacks=[history]) # 50 is X.shape[0]
    model.reset_states()
    
# 6. 학습과정 살펴보기
import matplotlib.pyplot as plt

plt.plot(history.losses)
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train'], loc='upper left')
plt.show()

# 7. 모델 평가하기
scores = model.evaluate(x_train, y_train, batch_size=1)
print("%s: %.2f%%" %(model.metrics_names[1], scores[1]*100))
model.reset_states()

# 8. 모델 사용하기

pred_count = 50 # 최대 예측 개수 정의

# 한 스텝 예측

seq_out = ['g8', 'e8', 'e4', 'f8']
pred_out = model.predict(x_train, batch_size=1)

for i in range(pred_count):
    idx = np.argmax(pred_out[i]) # one-hot 인코딩을 인덱스 값으로 변환
    seq_out.append(idx2code[idx]) # seq_out는 최종 악보이므로 인덱스 값을 코드로 변환하여 저장
    
print("one step prediction : ", seq_out)

model.reset_states()
'''