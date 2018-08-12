from mido import MidiFile, MidiTrack, Message, MetaMessage
import mido
import note_tools

#단일 트랙, 단일 라인 미디생성
def create_midi(notelist,dir,bpm,ticks):

    #박자를 tick으로 변경
    for note in notelist:
        note.length = note_tools.cal_beat_to_tick((note.length),ticks)

    ontime = 0

    mid_create = MidiFile(ticks_per_beat = ticks)
    track_list = MidiTrack()
    mid_create.tracks.append(track_list)

    track_list.append(Message('program_change', program=0, time=0))
    track_list.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))

    for i in notelist:
        if type(i) is note_tools.rest_note:
            ontime += i.length
        else:
            track_list.append(Message('note_on', note=i.note, velocity=100, time=ontime))
            track_list.append(Message('note_off', note=i.note, velocity=64, time=i.length))
            ontime = 0     
    mid_create.save(dir)