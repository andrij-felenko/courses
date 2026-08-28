from pymavlink import mavutil

# під'єднуємось до SITL рівно так, як під'єдналися б до справжнього дрона:
# змінився б ЛИШЕ цей рядок (порт замість радіо) — решта коду та сама
m = mavutil.mavlink_connection('udpin:127.0.0.1:14550')
m.wait_heartbeat()                          # знайомство: хто на лінії
print("апарат на лінії: system %d" % m.target_system)

m.set_mode('GUIDED')                         # режим, у якому слухають команди
m.arducopter_arm()                           # озброїти мотори
m.motors_armed_wait()                        # дочекатися підтвердження

# команда злетіти на 10 м (param7 — цільова висота)
m.mav.command_long_send(
    m.target_system, m.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,  0, 0, 0, 0, 0, 0, 10)

# стежимо за висотою з телеметрії — апарат справді «злітає» в моделі
while True:
    msg = m.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    alt = msg.relative_alt / 1000.0          # relative_alt у міліметрах
    print("висота: %.1f м" % alt)
    if alt > 9.5:
        break
