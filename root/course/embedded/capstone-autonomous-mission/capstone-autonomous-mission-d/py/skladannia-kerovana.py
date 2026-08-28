# Живий монітор прогресу: показує активний пункт і ловить момент досягнення.
last_seq = None
while True:
    msg = master.recv_match(type=['MISSION_CURRENT', 'MISSION_ITEM_REACHED'],
                            blocking=True, timeout=1.0)
    if msg is None:                                  # тиша за секунду — перевір лінк
        print("тиша від борту — перевір лінк")
        continue

    if msg.get_type() == 'MISSION_CURRENT':          # борт шле активний пункт
        if msg.seq != last_seq:                      # індекс зрушив — покажемо перехід
            print(f"активний пункт місії: #{msg.seq}")
            last_seq = msg.seq
    elif msg.get_type() == 'MISSION_ITEM_REACHED':   # борт підтвердив: пункт виконано
        print(f"  досягнуто #{msg.seq} — перехід далі")
