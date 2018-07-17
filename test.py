import time
import midiparser
import midigenerator
import note_tools
 
bpm = 140
ticks = 0


################# << main start >> #################

################# << 악보 제작 부분 >> #################

ListOfList = midiparser.make_score(r'D:\code\py\MMMake\midi\gunmul.mid')
ticks = midiparser.midi_ticks(r'D:\code\py\MMMake\midi\gunmul.mid')

########################## 악보 제작 부분 끝 #############################

#for count, i in enumerate(ListOfList):
#    print('Track {}'.format(count))
#    for j in i:
#        for k in j:
#            print(k.note_string, end=' ')
#            print()
#        print()
#    print()


########################## 악보를 미디파일로 변환 #############################
midigenerator.create_midi(ListOfList,r'D:\code\py\MMMake\generated_midi\cnew_song.mid',bpm,ticks)
print('Done')

########################## 악보를 미디파일로 부분 끝 #############################

########################## << end of main >> #############################