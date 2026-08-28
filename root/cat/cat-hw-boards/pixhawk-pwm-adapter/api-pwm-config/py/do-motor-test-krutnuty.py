from pymavlink import mavutil

# Стендова перевірка одного мотора: крутнути на малому газі й дати
# команді САМІЙ зупинити його за таймаутом.
# УВАГА: ТІЛЬКИ БЕЗ ПРОПЕЛЕРІВ. Мотор крутнеться фізично.
def motor_test(master, motor_num, throttle_percent, seconds):
    master.mav.command_long_send(
        master.target_system,        # кому: система 1, автопілот
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0,                           # не повтор
        motor_num,                   # param1: номер мотора (1..N)
        0,                           # param2: тип газу 0 = відсоток
        throttle_percent,            # param3: значення газу (%)
        seconds,                     # param4: таймаут, с — САМ зупинить
        0,                           # param5: один мотор
        0, 0)                        # param6..7 не потрібні


# виклик: мотор 1, 10% газу, 3 секунди, тоді автостоп
motor_test(master, 1, 10.0, 3.0)
