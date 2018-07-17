from mido import MidiFile, MidiTrack, Message, MetaMessage
import mido
import note_tools

def midi_ticks(dir):
    mid_analysis = MidiFile(dir)
    ticks = mid_analysis.ticks_per_beat
    return ticks

def make_score(dir):
    list = []
    onlist = []
    ListOfList = []
    off_flag = False
    msg_list = []
    delta = 0

    mid_analysis = MidiFile(dir)
    
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

                ob_note = note_tools.note(msg.note,delta)
                #note_on에 time이 0이상이면 쉼표로 간주한다.
                if ob_note.ontime != 0:
                    #쉼표넣기, rest_note 객체 생성
                    ob_rest = note_tools.rest_note(delta)
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
    #리스트 반환
    return ListOfList