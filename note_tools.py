#define of note
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

#define of rest note
class rest_note(note):
    def __init__(self, length):
        self.length = length
        self.note_string += 'r' + '-' + str(self.length)

class pred_note(note):
    def __init__(self, note, length):
        self.note = note
        self.length = length
        self.note_string += str(note) + '-' + str(length)

#return tick to beat, ex) 480 -> 4, 960 -> 2 etc.
def cal_tick_to_beat(time, ticks):
    if time/ticks <= 0.03125:
        beat = 128
    elif time/ticks <= 0.046875:
        beat = 96
    elif time/ticks <= 0.0625:
        beat = 64
    elif time/ticks <= 0.09375:
        beat = 48
    elif time/ticks <= 0.125:
        beat = 32
    elif time/ticks <= 0.1875:
        beat = 24
    elif time/ticks <= 0.25:
        beat = 16
    elif time/ticks <= 0.375:
        beat = 12
    elif time/ticks <= 0.5:
        beat = 8
    elif time/ticks <= 0.75:
        beat = 6
    elif time/ticks <= 1:
        beat = 4
    elif time/ticks <= 1.5:
        beat = 3
    elif time/ticks <= 2:
        beat = 2
    elif time/ticks <= 3:
        beat = 1.5
    elif time/ticks <= 4:
        beat = 1
    elif time/ticks <= 6:
        beat = 0.75
    else:
        beat = 0.5
    return str(beat)

#return beat to tick, ex) 4 -> 480, 2 -> 960 etc.
def cal_beat_to_tick(beat, ticks):
    cal = int((ticks*4)/float(beat))
    return cal

#return note name to string, ex) c5 e3 f#4
def cal_note_name(pitch):
    note_dict = {
        0:'c', 1:'c#', 2:'d', 3:'d#', 4:'e', 5:'f', 6:'f#', 7:'g', 8:'g#', 9:'a', 10:'a#', 11:'b'
    }
    
    octa = int(pitch/12)
    note_name = pitch%12

    return str(note_dict[note_name])+str(octa)

