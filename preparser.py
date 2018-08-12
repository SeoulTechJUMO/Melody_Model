import midiparser
import glob
import pickle
import os

#make song list
#song list (1 midi file) -> track list -> pattern list -> each notes
def preparse():
    song_list = []
    count = 0
    
    #midis/MIDI/melody/**/*.mid
    for file in glob.glob('midis/MIDI/melody/**/*.mid',recursive=True):
        print(file)
        try:
            track_list = midiparser.make_score(file,True)

            if not track_list:
                print('Cannot open this midi')
                continue
        except:
            print('parsing error')
            continue

        #insert one midi data to song_list
        song_list.append(track_list)
        count += 1

        if len(song_list) == 200:
            with open('data/notes_{}_files.bin'.format(count), 'ab') as file:
                pickle.dump(song_list, file)
                song_list = []

    with open('data/notes_{}_files.bin'.format(count), 'ab') as file:
         pickle.dump(song_list, file)

def show_files():
    for file in glob.glob("data/*.bin"):
        with open(file,'rb') as song:
            song_list = pickle.load(song)

        for song in song_list:
            for track in song:
                if track == song[-1]:
                    print(track)
                    break
                for pat in track:
                    for msg in pat:
                        print(msg.note_string)
                    print()

#main
#preparse()
#show_files()