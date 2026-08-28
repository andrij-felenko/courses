# Бік землі: pymavlink. Номери ставимо явно — на замовчування покладатися не можна:
# source_system=255 збігається з номером QGroundControl, а source_component=0 узагалі недійсний.
from pymavlink import mavutil

link = mavutil.mavlink_connection(
    'udpin:0.0.0.0:14550',
    source_system=254,                       # друга станція: 255 уже зайнято
    source_component=mavutil.mavlink.MAV_COMP_ID_MISSIONPLANNER)   # 190

link.wait_heartbeat()                        # звідси беруться адреси апарата
print(link.target_system, link.target_component)

link.mav.command_long_send(
    link.target_system,                      # target_system
    mavutil.mavlink.MAV_COMP_ID_AUTOPILOT1,  # target_component = 1
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,                                       # confirmation
    1, 0, 0, 0, 0, 0, 0)                     # param1 = 1 — зброїти
