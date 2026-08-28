armed = False   # за замовчуванням DISARMED — безпечно

# Найнижча ланка: розрахунок сигналу на кожен двигун.
# Хоч би що порахувала логіка керування — у disarmed виходить нуль.
def motors_output(thr):
    if not armed:
        for i in range(NUM_MOTORS):
            esc_write(i, THROTTLE_MIN)   # мертвий вихід, крапка
        return
    for i in range(NUM_MOTORS):
        esc_write(i, thr[i])             # сюди доходимо ЛИШЕ коли armed
