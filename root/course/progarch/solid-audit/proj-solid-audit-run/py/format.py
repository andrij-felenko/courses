# format.py — окремий актор (тон), чиста функція. Час беремо ЯВНО.
from datetime import datetime

def format_alarm(zone: str, at: datetime) -> str:
    return f"Рух у зоні «{zone}» о {at:%H:%M}"

# policy.py — стабільне ядро. Залежить ЛИШЕ від портів.
from ports import Notifier, Clock
from models import SensorEvent, Message

class AlarmPolicy:
    def __init__(self, notifier: Notifier, clock: Clock) -> None:
        self._notifier, self._clock = notifier, clock   # подано ЗЗОВНІ
        self._armed = False

    def arm(self)    -> None: self._armed = True
    def disarm(self) -> None: self._armed = False

    async def handle(self, ev: SensorEvent) -> None:
        if ev.type != "motion" or not self._armed: return  # політика тривоги…
        if ev.zone == "pet-safe": return                   # …і тільки вона
        body = format_alarm(ev.zone, self._clock.now())
        await self._notifier.send(Message(to="owner", body=body))
