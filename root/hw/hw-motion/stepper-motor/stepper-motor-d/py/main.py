import time
import RPi.GPIO as GPIO

# чотири виходи на входи драйвера/ключів котушок A, B, A', B'
COIL = [PIN_A, PIN_B, PIN_NA, PIN_NB]

# одна активна фаза за раз; рядок таблиці = яку котушку живимо
PHASE = [
    (1, 0, 0, 0),   # живиться A
    (0, 1, 0, 0),   # живиться B
    (0, 0, 1, 0),   # живиться A'
    (0, 0, 0, 1),   # живиться B'
]

# один крок: виставити фазу за індексом
def apply_phase(idx):
    for c in range(4):
        GPIO.output(COIL[c], PHASE[idx][c])

# провернути на steps кроків; dir = +1 (вперед) або -1 (назад)
def stepper_move(steps, direction, delay_us):
    for _ in range(steps):
        # phase зберігається як атрибут функції — стан між викликами
        stepper_move.phase = (stepper_move.phase + (1 if direction > 0 else 3)) & 3
        apply_phase(stepper_move.phase)         # +1 уперед, +3 (=−1 mod 4) назад
        time.sleep(delay_us / 1_000_000)        # пауза задає швидкість

stepper_move.phase = 0                          # пам'ятаємо, де ми у послідовності

# провернути вал на 90° для мотора з кроком 1.8° (200 кроків/оберт)
def quarter_turn():
    stepper_move(50, +1, 2000)                  # 50 кроків уперед, 2 мс між кроками
