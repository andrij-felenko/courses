# НА ХАБІ — справжні об'єкти з поведінкою. Геттери локальні, тобто дарові.
class Device:
    def __init__(self, id, type, room, state, brightness, last_seen):
        self.id = id
        self._type, self._room, self._state = type, room, state
        self._brightness, self._last_seen = brightness, last_seen
    def type(self):       return self._type
    def room(self):       return self._room
    def state(self):      return self._state
    def brightness(self): return self._brightness
    def last_seen(self):  return self._last_seen

class Hub:
    def __init__(self):
        self._devices = {}
    def register(self, d): self._devices[d.id] = d
    def get(self, id):     return self._devices[id]
    def ids(self):         return list(self._devices)
