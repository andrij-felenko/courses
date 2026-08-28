# Крок 1: попросити борт вивантажити його поточну місію.
master.mav.mission_request_list_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_MISSION_TYPE_MISSION)

# Крок 2: борт відповість MISSION_COUNT; далі просимо кожен пункт по seq.
count = master.recv_match(type='MISSION_COUNT', blocking=True).count
for seq in range(count):
    master.mav.mission_request_int_send(       # MISSION_REQUEST_INT(seq)
        master.target_system, master.target_component, seq)
    it = master.recv_match(type='MISSION_ITEM_INT', blocking=True)

    # Крок 3: звірити з тим, що ЗАДУМАНО (не з тим, що «мали б надіслати»).
    if it.command == mavutil.mavlink.MAV_CMD_NAV_WAYPOINT:
        lat = it.x * 1e-7              # 10⁻⁷ градуса → градуси
        lon = it.y * 1e-7
        alt = it.z                     # метри над точкою старту
        print(f"#{seq}  {lat:.7f}, {lon:.7f}  alt={alt:.1f} m")
