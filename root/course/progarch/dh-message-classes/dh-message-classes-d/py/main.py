from dataclasses import dataclass
from enum import Enum

class Intent(Enum):   COMMAND = "command"; DOCUMENT = "document"; EVENT = "event"   # намір за EIP
class Fanout(Enum):   ONE = "one-addressed"; POOL = "worker-pool"; INDEP = "many-independent"; UNKNOWN = "many-unknown"
class Delivery(Enum): ONCE = "effectively-once"; AT_LEAST = "at-least-once"
class Channel(Enum):  QUEUE = "queue"; WORK = "work-queue"; LOG = "log"; TOPIC = "topic"

@dataclass(frozen=True)          # незмінне оголошення: форма класу не «пливе» в рантаймі
class TrafficClass:
    intent: Intent
    fanout: Fanout
    waits: bool                  # хтось синхронно чекає відповідь?
    delivery: Delivery
    replayable: bool             # чи треба тримати історію й переграти?
    channel: Channel             # сюди — і тільки сюди — лягає цей клас

DH_TRAFFIC = {
    "device_command": TrafficClass(Intent.COMMAND,  Fanout.ONE,     True,  Delivery.ONCE,     False, Channel.QUEUE),
    "telemetry":      TrafficClass(Intent.DOCUMENT, Fanout.INDEP,   False, Delivery.AT_LEAST, True,  Channel.LOG),
    "domain_event":   TrafficClass(Intent.EVENT,    Fanout.UNKNOWN, False, Delivery.AT_LEAST, False, Channel.TOPIC),
    "heavy_job":      TrafficClass(Intent.COMMAND,  Fanout.POOL,    False, Delivery.AT_LEAST, False, Channel.WORK),
}
