from pymavlink import mavutil

m = mavutil.mavlink_connection('udpin:localhost:14550')
m.wait_heartbeat()
print("апарат на лінії: system %d, component %d"
      % (m.target_system, m.target_component))

# 1) прочитати одну порцію телеметрії — глобальну позицію з висотою
msg = m.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
print("висота над рівнем моря: %.1f м" % (msg.alt / 1000.0))   # alt у міліметрах

# 2) перевести у GUIDED (для ArduPilot режим має номер у таблиці режимів)
m.set_mode('GUIDED')

# 3) arm: команда MAV_CMD_COMPONENT_ARM_DISARM, param1 = 1 (увімкнути)
m.mav.command_long_send(
    m.target_system, m.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,            # confirmation
    1, 0, 0, 0, 0, 0, 0)
m.motors_armed_wait()                       # дочекатися, поки мотори озброєно

# 4) злетіти на 10 м: param7 = цільова висота
m.mav.command_long_send(
    m.target_system, m.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0, 0, 0, 0, 0, 0, 10)

# 5) дочекатися підтвердження виконання команди
ack = m.recv_match(type='COMMAND_ACK', blocking=True)
print("відповідь апарата:", ack.result)
