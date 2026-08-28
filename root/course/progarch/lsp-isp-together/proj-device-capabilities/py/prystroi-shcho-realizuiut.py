class TempSensor:                       # лише Readable — і жодного зайвого методу
    def __init__(self, celsius: float):
        self.celsius = celsius
    def read(self) -> float:
        return self.celsius

class SmartSocket:                      # Readable + Switchable, без спадкування
    def __init__(self, watts: float = 60.0):
        self._on, self._watts = False, watts
    def read(self) -> float:  return self._watts if self._on else 0.0
    def turn_on(self)  -> None: self._on = True
    def turn_off(self) -> None: self._on = False
    def is_on(self) -> bool:  return self._on

class DoorLock:                         # лише Lockable
    def __init__(self):
        self._locked = False
    def lock(self)   -> None: self._locked = True
    def unlock(self) -> None: self._locked = False
    def is_locked(self) -> bool: return self._locked

class Camera:                           # лише Streamable
    def __init__(self):
        self._streaming = False
    def start_stream(self) -> str:
        self._streaming = True
        return "rtsp://dh/cam/live"
    def stop_stream(self) -> None:
        self._streaming = False
