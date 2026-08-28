# ─── антиприклад — НЕ робити так ────────────────────────────────────
g_has_data = False  # ← перегін: Sensor пише, Control читає
g_sample = 0        # ← перегін без м'ютекса

@dataclass
class Cmd:
    relay_on: bool = False
    level: int = 0

g_command = Cmd()   # ← перегін: Control пише, Actuator читає

# Якби боялись перегонів — довелось би ставити окремий м'ютекс
# на кожну зі змінних: mx_data, mx_cmd = Lock(), Lock()
# і брати/давати у кожному потоці. Це й є той «спагеті».

def task_sensor() -> None:
    global g_sample, g_has_data
    while True:
        g_sample = analog_read(PIN_A)  # пише без захисту
        g_has_data = True              # пише без захисту ← перегін!
        time.sleep(0.100)

def task_control() -> None:
    global g_has_data
    while True:
        if g_has_data:                 # читає без захисту ← перегін!
            g_has_data = False
            g_command.relay_on = g_sample > 512  # пише без захисту
        time.sleep(0.010)
