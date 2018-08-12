from mido import MidiFile, MidiTrack, Message, MetaMessage
import mido
import note_tools
import numpy as np

def midi_ticks(dir):
    mid_analysis = MidiFile(dir)
    ticks = mid_analysis.ticks_per_beat
    return ticks

#상관계수 구하기 (pearson)
def cal_corrcoef(rel_list, pitch_list, mode):
    for start in range(12):
        comp_list = []
        for idx in range(start,start+12):
            if idx > 11:
                k = idx - 12
            else:
                k = idx
            comp_list.append(pitch_list[k])
        rel_list.append(np.corrcoef(comp_list, mode)[0][1])
    return rel_list
    

def find_key(pitch_list):
    #Krumhansl-Schmuckler key-finding algorithm 이용
    major = [6.35, 2.23, 3.48, 2.33, 4.38, 
             4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    minor = [6.33, 2.68, 3.52, 5.38, 2.60, 
             3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    rel_list = []
    note_dict = {
        0:'c', 1:'c#', 2:'d', 3:'d#', 4:'e', 
        5:'f', 6:'f#', 7:'g', 8:'g#', 9:'a', 10:'a#', 11:'b'
    }
    key = ''

    #cal correlation coefficient
    rel_list = cal_corrcoef(rel_list, pitch_list, major)
    rel_list = cal_corrcoef(rel_list, pitch_list, minor)

    judge = rel_list.index(max(rel_list))
    key += note_dict[judge%12]
    if judge > 11:
        key += ' minor'
    else:
        key += ' major'

    return key


def make_score(dir,monotrack=False):
    #파싱시 필요한 리스트와 변수
    list = []
    onlist = []
    ListOfList = []
    off_flag = False
    msg_list = []
    delta = 0

    #key찾기 전용 리스트
    pitch_list = [0]*12

    mid_analysis = MidiFile(dir)
    
    #note_off 인식 안되는것 예외처리
    for track in mid_analysis.tracks:
        for msg in track:
            if msg.is_meta:
                continue
            if msg.type == 'note_off':
                off_flag = True
                break
        if off_flag == True:
            break

    if off_flag == False:
        return ListOfList
        
    off_flag = False

    #파일 tick 계산
    tick = midi_ticks(dir)

    #학습용 악보 정보 만들기
    #현재 mido 상에서 모든 메시지가 note_on인 몇몇 midi 파일은 파싱하지 못한다
    for track in mid_analysis.tracks:
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

                ob_note = note_tools.note(msg.note,delta)
                #생성한 노트의 음이름(0~11)에따라 생성 개수를 추가
                pitch_list[msg.note%12] += 1
                #note_on에 time이 0이상이면 쉼표로 간주한다.
                if ob_note.ontime != 0:
                    #쉼표넣기, rest_note 객체 생성
                    ob_rest = note_tools.rest_note(note_tools.cal_tick_to_beat(delta,tick))
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
                                #박자로 변환
                                comp.make_note(note_tools.cal_tick_to_beat(cal_time,tick))

                                off_flag = True
                                break
                off_flag = False
                onlist = []
        #노트 메시지가 없는 트랙은 삽입하지 않는다
        msg_list = []
        if list:
            ListOfList.append(list)
            #첫 트랙만 파싱
            if monotrack == True:
                break
            list = []

   
    #키찾기 알고리즘
    key = find_key(pitch_list)
    #리스트의 끝에 조성 정보 저장
    ListOfList.append(key)

    #리스트 반환
    return ListOfList