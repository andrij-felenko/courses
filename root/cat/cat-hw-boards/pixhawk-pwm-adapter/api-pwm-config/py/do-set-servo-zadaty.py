from pymavlink import mavutil

# Примусово задати ширину імпульсу на виході серворульової машинки.
# УВАГА: команда ОБХОДИТЬ штатне змішування. На реальному апараті з
# увімкненими (озброєними) моторами так робити НЕ можна — лише перевірка
# на столі, без пропелерів.
def servo_set_pwm(master, out_channel, pulse_us):
    # master — відкрите з'єднання mavutil.mavlink_connection();
    # наша наземна станція має sysid 255 (задано при mavlink_connection).
    master.mav.command_long_send(
        master.target_system,        # автопілот зазвичай має system id = 1
        master.target_component,     # MAV_COMP_ID_AUTOPILOT1
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,  # команда «задати вихід серва»
        0,                           # confirmation: 0 = не повтор
        out_channel,                 # param1: номер виходу (гребінки)
        pulse_us,                    # param2: ширина імпульсу, мкс
        0, 0, 0, 0, 0)              # param3..7 не потрібні


# виклик: серво на виході 5 — у нейтраль
servo_set_pwm(master, 5, 1500)
