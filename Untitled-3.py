from mido import MidiFile, MidiTrack, Message, MetaMessage
import mido
import threading, time

delta_sum = 0
before_sum = 0


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

class note_thread(threading.Thread):
    t = 0
    def __init__(self,count,k,delta):
        threading.Thread.__init__(self)
        self.count = count
        self.k = k
        self.delta = delta
    def run(self):
        global delta_sum
        global before_sum
        while(1):
            self.t = delta_sum - self.delta
            if self.k.length - self.t == 0:
                track_list[self.count].append(Message('note_off', note=self.k.note, velocity=64, time=0))
                break
            if self.k.length - self.t < 0:
                track_list[self.count].append(Message('note_off', note=self.k.note, velocity=64, time=self.k.length-before_sum))
                lock.acquire()
                delta_sum += self.k.length-before_sum
                lock.release()
                break


lock = threading.Lock()
thread_list = []
        
bpm = 140

track_list = []

ticks = 0

list = []
onlist = []
ListOfList = []
off_flag = False
ontime = 0

minus = 0
timelist = []

msg_list = []

delta = 0


mid_analysis = MidiFile(r'D:\code\py\MMMake\midi\alstroemeria.mid')

ticks = mid_analysis.ticks_per_beat

#학습용 악보 정보 만들기
#현재 모든 메시지가 note_on인 이상한 midi 파일은 아직 파싱하지 못한다
for i, track in enumerate(mid_analysis.tracks):
    print('Track {}: {}'.format(i, track.name))
    for msg in track:
        #노트가 아닌 메시지들도 리스트에 삽입
        if msg.is_meta:
            msg_list.append(msg)
            continue
        if msg.type != 'note_on' and msg.type != 'note_off':
            msg_list.append(msg)
            continue
        #타악기 제외
        if msg.channel == 9:
            break
        msg_list.append(msg)
        if msg.type == 'note_on':
            delta = 0
            #모든 delta time 합산, 현재 메시지 포함
            for count, each_msg in enumerate(reversed(msg_list)):
                if count != 0:    
                    if each_msg.type == 'note_on' or each_msg.type == 'note_off':
                        break
                try:
                    delta += each_msg.time
                except:
                    continue

            ob_note = note(msg.note,delta)
            #note_on에 time이 0이상이면 쉼표로 간주한다.
            if ob_note.ontime != 0:
                #쉼표넣기, rest_note 객체 생성
                ob_rest = rest_note(delta)
                onlist.append(ob_rest)
                list.append(onlist)
                onlist = []
            onlist.append(ob_note)
        if msg.type == 'note_off':
            cal_time = 0
            #onlist가 비어있는 경우는 note_off 메시지가 2번 연속 나온경우
            if onlist:
                #on메시지 다음 첫번째 off 메시지일 경우 지금까지의 on정보를 저장하여 구분
                list.append(onlist)
            
            #해당 노트 길이 계산
            for idx, k in enumerate(reversed(msg_list)):
                if k.type == 'note_on' and msg_list[-1].note == k.note:
                    #한번 참조한 정보는 다시 참조안하게 note=0
                    msg_list[-(idx+1)] = k.copy(note=0)
                    break
                try:
                    cal_time += k.time
                except:
                    continue
 
            #해당 노트 길이 입력, 입력이 안되어 있는 것을 골라서 입력   
            for k in reversed(list):
                if off_flag != False:
                    break       
                for comp in reversed(k):
                    #현재 메시지의 노트와 같은 메시지를 찾는다.
                    if comp.note_string == '':
                        if comp.note == msg.note:
                            #찾은 노트에 '0 - 0' 형식의 스트링을 생성한다.
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

########################## 악보 제작 부분 끝 #############################

               
#for i in ListOfList:
#    for j in i:
#        for k in j:
#            print(k.note_string, end=' ')
#            print()
#        print()
#    print()


#파싱 미디파일 출력
mid_create = MidiFile(ticks_per_beat = ticks)
for i in range(len(ListOfList)):
    track_list.append(MidiTrack())

mid_create.tracks.append(track_list[0])

track_list[0].append(Message('program_change', program=0, time=0))
track_list[0].append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))


for count, i in enumerate(ListOfList):
    delta_sum = 0
    before_sum = 0
    if count != 0:
        mid_create.tracks.append(track_list[count])
    for i_idx, j in enumerate(i):
        for idx, k in enumerate(j):
            before_sum = delta_sum
            if idx == 0:
                shortest = k.length
                minid = 0
            if k.length <= shortest:
                shortest = k.length
                minid = idx
            if type(k) is rest_note:
                ontime += k.length
                delta_sum += ontime
                time.sleep(0.01)
            else:
                track_list[count].append(Message('note_on', note=k.note, velocity=100, time=ontime))
                
                t = note_thread(count,k,delta_sum)
                thread_list.append(t)
                
                if k == j[-1]:
                    track_list[count].append(Message('note_off', note=j[minid].note, velocity=64, time=shortest))
                    delta_sum += shortest
                    thread_list.pop(minid)
                    if thread_list:
                        for th in thread_list:
                            th.start()
                        thread_list=[]
                time.sleep(0.01)    

              

                ontime = 0
    track_list[count].append(MetaMessage('end_of_track'))
    
mid_create.save(r'D:\code\py\MMMake\generated_midi\cnew_song.mid')
print('Done')
