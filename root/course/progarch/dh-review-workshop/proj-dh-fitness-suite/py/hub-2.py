# hub.py — локальне правило НЕ ходить у хмару
THRESHOLD = 20.0

class DeadLink:
    """Обірваний лінк до хмари: будь-яка спроба заговорити — вибух."""
    def publish(self, *a, **k): raise OSError("хмара недосяжна")
    def connect(self, *a, **k): raise OSError("хмара недосяжна")

class Hub:
    def __init__(self):
        self.cloud = DeadLink()          # у тесті — мертвий; у бою — MQTT-клієнт
        self.local_sensor = lambda: 21.0 # давач біля хаба, без мережі
        self.on_actuate = lambda ev: None
    def tick(self):
        t = self.local_sensor()
        self.on_actuate(("heater", "on" if t < THRESHOLD else "off"))
