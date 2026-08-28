# app: після операції злити події й розіслати. Пристрій НЕ знає про підписників.
class EventBus:
    def __init__(self): self._handlers = []
    def subscribe(self, h): self._handlers.append(h)
    def publish(self, events):
        for e in events:
            for h in self._handlers:
                h(e)

class Billing:                                  # активний від commission до retire
    def __init__(self): self.active = set()
    def on(self, e):
        if isinstance(e, DeviceCommissioned): self.active.add(e.device_id)
        elif isinstance(e, DeviceRetired):    self.active.discard(e.device_id)

class Telemetry:                                # приймає покази, поки не списаний
    def __init__(self): self.accepting = set()
    def on(self, e):
        if isinstance(e, DeviceCommissioned): self.accepting.add(e.device_id)
        elif isinstance(e, DeviceRetired):    self.accepting.discard(e.device_id)

bus = EventBus()
billing, telemetry = Billing(), Telemetry()
bus.subscribe(billing.on); bus.subscribe(telemetry.on)

d = Device("lock-42")
d.commission("home-7"); bus.publish(d.pull_events())  # білінг +1, телеметрія приймає
d.mark_offline();       bus.publish(d.pull_events())  # телеметрія ДОСІ приймає: offline ≠ retired
d.retire();             bus.publish(d.pull_events())  # білінг −1, телеметрія глушить прийом
