class Radio:                     # друга межа: синхронний драйвер заліза
    def __init__(self): self.reads = 0
    def read(self, id):
        self.reads += 1                                  # кожне читання — перехід
        return "on"

class HubLive:
    def __init__(self, radio):
        self._devices, self.radio = {}, radio
    # ... register / ids ...
    def snapshot(self):
        return [DeviceDTO(1, d.id, d.type(), d.room(),
                          self.radio.read(d.id),          # ← прихований перехід на кожен!
                          d.brightness(), d.last_seen())
                for d in self._devices.values()]
# cloud_link.crossings == 1     ← грубо, як домовлялись
# radio.reads          == 30      ← балакучий N+1, лише сховався всередину
