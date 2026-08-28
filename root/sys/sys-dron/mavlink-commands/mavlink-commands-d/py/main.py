# MAV_CMD_NAV_TAKEOFF — команда взльоту; висота йде в param7 (pymavlink).
from pymavlink import mavutil

# з'єднання зі станції 255/190; бібліотека сама складе кадр і CRC
master = mavutil.mavlink_connection("/dev/ttyUSB0", baud=57600,
                                    source_system=255, source_component=190)

master.mav.command_long_send(
    1,                                        # target_system — якому апарату
    1,                                        # target_component — автопілоту
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,      # яка команда
    0,                                        # confirmation — перша відправка
    0, 0, 0, 0, 0, 0,                         # param1..param6 — не вжиті
    10.0)                                     # param7 — цільова висота, метри

# далі — чекаємо COMMAND_ACK і дивимося ack.result
ack = master.recv_match(type="COMMAND_ACK", blocking=True)
