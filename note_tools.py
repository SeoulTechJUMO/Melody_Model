class note:
    note = 0
    ontime = 0
    length = 0
    delta_start = 0
    now_delta = 0
    last_len = 0
    note_string = ''
    def __init__(self, note, ontime):
        self.note = note
        self.ontime = ontime
    def make_note(self, length):
        self.length = length
        self.note_string += str(self.note) + '-' + str(self.length)
    def set_delta(self, delta_start):
        self.delta_start = delta_start
    def cal_delta(self, delta_sum):
        self.now_delta = delta_sum - self.delta_start
    def cal_last(self):
        if self.length - self.now_delta >= 0: 
            self.last_len = self.length - self.now_delta


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
