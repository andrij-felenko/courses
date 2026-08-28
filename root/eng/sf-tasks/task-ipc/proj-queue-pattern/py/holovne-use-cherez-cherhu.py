import queue
import threading
import time
from dataclasses import dataclass
from enum import IntEnum

# ─── тип повідомлення — єдиний «конверт» для будь-яких даних ─────────
class MsgType(IntEnum):
    SAMPLE = 0
    BUTTON = 1
    SETMODE = 2

@dataclass
class Msg:
    type: MsgType
    value: int

# ─── PRODUCER 1: давач ────────────────────────────────────────────────
def task_sensor(q_events: "queue.Queue[Msg]") -> None:
    while True:
        q_events.put(Msg(MsgType.SAMPLE, analog_read(PIN_A)))  # кладемо об'єкт — жодної спільної змінної
        time.sleep(0.100)

# ─── PRODUCER 2: кнопка (fan-in у ту саму q_events) ──────────────────
def task_button(q_events: "queue.Queue[Msg]") -> None:
    while True:
        if digital_read(PIN_BTN) == LOW:
            q_events.put(Msg(MsgType.BUTTON, 1))
            time.sleep(0.050)  # debounce
        time.sleep(0.010)

# ─── CONSUMER + PRODUCER: логіка керування ───────────────────────────
def task_control(q_events: "queue.Queue[Msg]", q_actuator: "queue.Queue[Msg]") -> None:
    mode = 0  # ← стан ПРИВАТНИЙ всередині потоку, не глобальний!
    #            жодного м'ютекса не потрібно
    while True:
        m = q_events.get()  # спить, поки немає пошти
        if m.type == MsgType.SAMPLE:
            if m.value > 512:
                q_actuator.put(Msg(MsgType.SAMPLE, 1))
        elif m.type == MsgType.BUTTON:
            mode = (mode + 1) % 3
        elif m.type == MsgType.SETMODE:
            mode = m.value

# ─── CONSUMER: виконавець на залізі ──────────────────────────────────
def task_actuator(q_actuator: "queue.Queue[Msg]") -> None:
    while True:
        m = q_actuator.get()
        # Якщо реле на спільній шині SPI — лише тут беремо м'ютекс на шину
        # with bus_lock:
        digital_write(PIN_RELAY, bool(m.value))

# ─── Ініціалізація ────────────────────────────────────────────────────
def main() -> None:
    q_events: "queue.Queue[Msg]" = queue.Queue(maxsize=8)   # fan-in: Sensor + Button → Control
    q_actuator: "queue.Queue[Msg]" = queue.Queue(maxsize=4) # Control → Actuator

    for target, args in (
        (task_sensor, (q_events,)),
        (task_button, (q_events,)),
        (task_control, (q_events, q_actuator)),
        (task_actuator, (q_actuator,)),
    ):
        threading.Thread(target=target, args=args, daemon=True).start()

    threading.Event().wait()  # блокуємось назавжди

# ЖОДНОЇ спільної змінної між потоками — лише черги.
# Кожен потік читаємо як окрему просту послідовну програму.
