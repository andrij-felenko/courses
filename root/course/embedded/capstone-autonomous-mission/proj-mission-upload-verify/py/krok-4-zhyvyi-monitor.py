def monitor_mission(master):
    """Живий монітор: показує активний пункт і момент його досягнення.
       Крутити паралельно польоту; Ctrl-C — вихід."""
    last_seq = None
    while True:
        msg = master.recv_match(
            type=['MISSION_CURRENT', 'MISSION_ITEM_REACHED'],
            blocking=True, timeout=1.0)
        if msg is None:
            print("… тиша від борту — перевір лінк")
            continue

        if msg.get_type() == 'MISSION_CURRENT':
            if msg.seq != last_seq:                  # індекс зрушив — покажемо перехід
                print(f"→ активний пункт місії: #{msg.seq}")
                last_seq = msg.seq
        else:  # MISSION_ITEM_REACHED
            print(f"  ✓ досягнуто #{msg.seq} — борт переходить далі")
