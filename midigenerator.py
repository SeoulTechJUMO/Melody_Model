from mido import MidiFile, MidiTrack, Message, MetaMessage
import mido
import note_tools

#global,델타변화량
delta_sum = 0
track_list = []

def off_maker(complist, count, flag):
    min_list = []
    global delta_sum
    for cal_i in reversed(complist):
        if flag == True:
            if cal_i == complist[-1]:
                continue
        for cal_j in cal_i:
            if cal_j.note != 0:
                min_list.append(cal_j)
    if min_list:
        min_list = sorted(min_list, key=lambda note: note.last_len)
        for cal_j in min_list:
            cal_j.cal_delta(delta_sum)
            cal_j.cal_last()
        for cal_j in min_list:
            if cal_j.now_delta == cal_j.length:
                track_list[count].append(Message('note_off', note=cal_j.note, velocity=64, time=0))
                cal_j.note = 0 
            if cal_j.now_delta > cal_j.length:
                track_list[count].append(Message('note_off', note=cal_j.note, velocity=64, time=cal_j.last_len))
                delta_sum += cal_j.last_len
                for idx, sub in enumerate(min_list):
                    if idx != 0:
                        if sub.last_len - cal_j.last_len >= 0:
                            sub.last_len -= cal_j.last_len
                cal_j.note = 0 

def create_midi(ListOfList,dir,bpm,ticks):
    msg_list = []
    ontime = 0

    mid_create = MidiFile(ticks_per_beat = ticks)
    for i in range(len(ListOfList)):
        track_list.append(MidiTrack())

    mid_create.tracks.append(track_list[0])

    track_list[0].append(Message('program_change', program=0, time=0))
    track_list[0].append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))

    for count, i in enumerate(ListOfList):
        delta_sum = 0
        if count != 0:
            mid_create.tracks.append(track_list[count])
        for i_idx, j in enumerate(i):
            for idx, k in enumerate(j):
                complist = i[:i_idx+1]
                #쉼표노트 1개만 있는 것 처리
                if len(j) == 1:
                    if type(k) is note_tools.rest_note:
                        ontime += k.length
                        delta_sum += ontime
                        break  
                if idx == 0:
                    shortest = k.length
                    minid = 0
                if k.length <= shortest:
                    shortest = k.length
                    minid = idx
                #무조건 동시노트의 마지막 쉼표 때 실행됨
                if type(k) is note_tools.rest_note:
                    ontime += k.length

                    delta_sum += shortest
                    off_maker(complist,count,True)

                    for msg in msg_list:
                        track_list[count].append(msg)
                    msg_list = []
                    if j[minid].note != 0:
                        track_list[count].append(Message('note_off', note=j[minid].note, velocity=64, time=shortest))
                        j[minid].note = 0
                    off_maker(complist,count,False)
                else:
                    msg_list.append(Message('note_on', note=k.note, velocity=100, time=ontime))
                    k.set_delta(delta_sum)
                    if k == j[-1]:
                        delta_sum += shortest

                        #off_maker(complist,count,True)

                        for msg in msg_list:
                            track_list[count].append(msg)
                        msg_list = []
                        track_list[count].append(Message('note_off', note=j[minid].note, velocity=64, time=shortest))
                        j[minid].note = 0
                        off_maker(complist,count,False)
                    ontime = 0
        track_list[count].append(MetaMessage('end_of_track'))
        
    mid_create.save(dir)