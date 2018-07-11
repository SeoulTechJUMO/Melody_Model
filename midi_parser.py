from mido import MidiFile, MidiTrack, Message, MetaMessage
import mido
import threading, time

class note:
    note = 0
    ontime = 0
    length = 0
    note_string = ''
    def __init__(self, note, ontime):
        self.note = note
        self.ontime = ontime
    def make_note(self, length):
        self.length = length
        self.note_string += str(self.note) + '-' + str(self.length)

class rest_note(note):
    def __init__(self, length):
        self.length = length
        self.note_string += 'r' + '-' + str(self.length)

    

def cal_tick_to_beat(time, ticks):
    if time/ticks <= 0.0625:
        beat = 64
    elif time/ticks <= 0.125:
        beat = 32
    elif time/ticks <= 0.25:
        beat = 16
    elif time/ticks <= 0.5:
        beat = 8
    elif time/ticks <= 1:
        beat = 4
    elif time/ticks <= 2:
        beat = 2
    elif time/ticks <= 4:
        beat = 1
    else:
        beat = 0.5
    return beat


def cal_beat_to_tick(beat, ticks):
    cal = int((ticks*4)/int(beat))
    return cal



bpm = 140

track_list = []

ticks = 0

list = []
onlist = []
ListOfList = []
off_flag = False
ontime = 0

minus = 0

msg_list = []


mid_analysis = MidiFile(r'D:\code\py\MMMake\midi\testmidi.mid')

ticks = mid_analysis.ticks_per_beat

#악보 정보 만들기
for i, track in enumerate(mid_analysis.tracks):
    print('Track {}: {}'.format(i, track.name))    
    for msg in track:
        if msg.type == 'note_on' or msg.type == 'note_off':
            msg_list.append(msg)
        if msg.type == 'note_on':
            ob_note = note(msg.note,msg.time)
            if ob_note.ontime != 0:
                #이전 on정보 삽입
                list.append(onlist)
                onlist = []
                #쉼표넣기
                ob_rest = rest_note(msg.time)
                onlist.append(ob_rest)
                list.append(onlist)
                onlist = []
            onlist.append(ob_note)
        if msg.type == 'note_off':
            cal_time = 0
            #onlist가 비어있는 경우는 note_off 메시지가 2번 연속 나온경우
            if onlist:
                #on메시지 다음 첫번째 off 메시지일 경우 지금까지의 on정보를 저장
                list.append(onlist)
            
            #노트 길이 계산
            for idx, k in enumerate(reversed(msg_list)):
                if k.type == 'note_on' and msg_list[-1].note == k.note:
                    #한번 참조한 정보는 다시 참조안하게 note=0
                    msg_list[-(idx+1)] = k.copy(note=0)
                    break
                cal_time += k.time
                
            #노트 길이 입력, 입력이 안되어 있는 것만    
            for k in reversed(list):
                if off_flag != False:
                    break       
                for comp in reversed(k):
                    if comp.note_string == '':
                        if comp.note == msg.note:
                            comp.make_note(cal_time)
                            off_flag = True
                            break
            off_flag = False
            onlist = []
    #노트 메시지가 없는 트랙은 삽입하지 않는다
    msg_list = []
    if list:        
        ListOfList.append(list)
        list = []

               
for i in ListOfList:
    for j in i:
        for k in j:
            print(k.note_string, end=' ')
            print()
        print()
    print()


#파싱 미디파일 출력
mid_create = MidiFile(ticks_per_beat = ticks)
for i in range(len(ListOfList)):
    track_list.append(MidiTrack())

mid_create.tracks.append(track_list[0])

track_list[0].append(Message('program_change', program=0, time=0))
track_list[0].append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))

for count, i in enumerate(ListOfList):
    if count != 0:
        mid_create.tracks.append(track_list[count])
    for j in i:  
        for k in j:
            if type(k) is rest_note:
                ontime += k.length
            else:
                track_list[count].append(Message('note_on', note=k.note, velocity=100, time=ontime))
                
                
                track_list[count].append(Message('note_off', note=k.note, velocity=100, time=k.length))


                ontime = 0
    track_list[count].append(MetaMessage('end_of_track'))
    
mid_create.save('D:\code\py\MMMake\generated_midi\cnew_song.mid')
print('Done')

