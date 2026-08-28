# Крок 1: попросити борт вивантажити його ПОТОЧНУ місію (не ту, що ми «мали б» залити).
master.mav.mission_request_list_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_MISSION_TYPE_MISSION)
mc = master.recv_match(type='MISSION_COUNT', blocking=True, timeout=5)  # борт відповість MISSION_COUNT
if mc is None:
    return
count = mc.count

# Крок 2: по одному пункту, з таймаутом і обмеженим числом повторів.
for seq in range(count):
    it = None
    for tries in range(5):
        master.mav.mission_request_int_send(              # MISSION_REQUEST_INT(seq)
            master.target_system, master.target_component, seq)
        it = master.recv_match(type='MISSION_ITEM_INT', blocking=True, timeout=0.25)
        if it is not None and it.seq == seq:
            break
        it = None
    else:                                                 # здався — не звіряємо частковий список
        abort_readback()
        return

    # Крок 3: звірити з тим, що ЗАДУМАНО, декодувавши цілі назад у градуси.
    if it.command == mavutil.mavlink.MAV_CMD_NAV_WAYPOINT:
        lat = it.x * 1e-7           # 10⁻⁷ градуса → градуси
        lon = it.y * 1e-7
        alt = it.z                  # метри — але В ЯКІЙ системі? див. it.frame нижче
        print(f"#{seq}  {lat:.7f}, {lon:.7f}  alt={alt:.1f}  frame={it.frame}")
