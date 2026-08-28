# Клієнт протоколу на pymavlink: віддати місію з двох пунктів.
from pymavlink import mavutil

TGT_SYS  = 1
TGT_COMP = mavutil.mavlink.MAV_COMP_ID_AUTOPILOT1
MISSION  = mavutil.mavlink.MAV_MISSION_TYPE_MISSION
FRAME    = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT

m = mavutil.mavlink_connection('udpout:127.0.0.1:14550', source_system=254)
m.wait_heartbeat()

# (команда, p1..p4, широта, довгота, висота)
items = [
    (mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  0, 0, 0, 0, 50.4501, 30.5234, 30.0),
    (mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 50.4510, 30.5250, 30.0),
]

m.mav.mission_count_send(TGT_SYS, TGT_COMP, len(items), MISSION)

todo = set(range(len(items)))
while todo:
    msg = m.recv_match(type=['MISSION_REQUEST_INT', 'MISSION_REQUEST', 'MISSION_ACK'],
                       blocking=True, timeout=1.5)
    if msg is None:                                  # тиша — повторюємо лічильник
        m.mav.mission_count_send(TGT_SYS, TGT_COMP, len(items), MISSION)
        continue
    if msg.get_type() == 'MISSION_ACK':              # ack посеред запису = відмова
        raise RuntimeError('борт обірвав обмін, код %d' % msg.type)

    cmd, p1, p2, p3, p4, lat, lon, alt = items[msg.seq]
    m.mav.mission_item_int_send(
        TGT_SYS, TGT_COMP,
        msg.seq,                    # номер — рівно той, який попросили
        FRAME, cmd,
        1 if msg.seq == 0 else 0,   # current
        1,                          # autocontinue
        p1, p2, p3, p4,
        int(round(lat * 1e7)),      # x — градуси · 10⁷
        int(round(lon * 1e7)),      # y — градуси · 10⁷
        alt,                        # z — метри, дробове
        MISSION)
    todo.discard(msg.seq)           # борт має право попросити той самий номер удруге

ack = m.recv_match(type='MISSION_ACK', blocking=True, timeout=1.5)
print('результат:', ack.type)       # 0 == MAV_MISSION_ACCEPTED
