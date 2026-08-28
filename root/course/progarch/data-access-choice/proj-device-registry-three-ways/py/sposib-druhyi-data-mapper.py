# ── ЧИСТИЙ домен: жодного натяку на базу ──────────────────────
class Device:
    def __init__(self, type, room, state="unknown", last_seen=None, id=None):
        self.type, self.room = type, room
        self.state, self.last_seen, self.id = state, last_seen, id

    def is_silent(self, now: int, threshold: int) -> bool:
        return self.last_seen is None or now - self.last_seen > threshold

class Telemetry:                       # так само чистий — рядок потоку серцебиття
    def __init__(self, at, device_id=None, id=None):
        self.at, self.device_id, self.id = at, device_id, id
