import lstm_dev
import glob
import pickle
import midigenerator
import numpy as np

ticks = 96
bpm = 120

window_size = 4

with open("data/notes_1000_files.bin",'rb') as song:
     song_list = pickle.load(song)

seq = song_list[10][0]
seq = seq[:window_size]

for note in seq:
    print(note[0].note_string)

for note in seq:
    print(note[0].length)

pattern = lstm_dev.using_model('model_save/minor_model.h5','model_save/beat_model.h5',seq,window_size)
midigenerator.create_midi(pattern,'created_midi/new_pattern7.mid',120,96)