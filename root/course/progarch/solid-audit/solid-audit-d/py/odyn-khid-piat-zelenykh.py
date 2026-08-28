class Notifier(Protocol):
    async def send(self, msg: Message) -> None: ...     # вузька абстракція: рівно одна дія

class Clock(Protocol):
    def now(self) -> datetime: ...

# Стабільне ядро — чиста політика, і нічого крім неї
class AlarmPolicy:
    def __init__(self, notify: Notifier, clock: Clock):  # деталі подано ЗЗОВНІ
        self.notify, self.clock = notify, clock
    async def handle(self, ev: SensorEvent) -> None:
        if ev.type != "motion" or not self.armed: return
        if ev.zone == "pet-safe": return
        t = self.clock.now().strftime("%H:%M:%S")
        await self.notify.send(Message(to="owner", body=f"Рух у зоні «{ev.zone}» о {t}"))

# Волатильні деталі — окремі адаптери. Twilio живе ТУТ, і лише тут.
class SmsNotifier:   # implements Notifier — Twilio всередині
    async def send(self, m): ...
class PushNotifier:  # implements Notifier — канал застосунку
    async def send(self, m): ...
