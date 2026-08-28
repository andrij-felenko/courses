from pymavlink import mavutil

# Відкрити серійний порт (USB/UART). source_system=255 — ми "наземна станція".
master = mavutil.mavlink_connection('COM3', baud=921600, source_system=255)

# Дочекатися heartbeat: доти не знаємо адреси апарата.
master.wait_heartbeat()
print(f"апарат: sysid={master.target_system} compid={master.target_component}")

# Зброїти = послати ОДНУ команду MAV_CMD_COMPONENT_ARM_DISARM.
master.mav.command_long_send(
    master.target_system,        # кому: sysid апарата
    master.target_component,     # кому: compid (автопілот = 1)
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # ЯКА команда
    0,        # confirmation (0 — перша спроба)
    1,        # param1: 1 = зброїти, 0 = роззброїти
    0, 0, 0, 0, 0, 0)            # param2..7 не потрібні цій команді

# Дочекатися підтвердження: плата відповідає COMMAND_ACK з результатом.
ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
if ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
    print("зброєно")
else:
    print(f"відмова у зброєнні: {ack.result if ack else 'нема відповіді'}")
