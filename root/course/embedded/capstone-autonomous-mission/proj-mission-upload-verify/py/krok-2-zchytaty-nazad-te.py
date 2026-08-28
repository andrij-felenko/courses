def download_mission(master, timeout=0.25, max_retries=5):
    """Зчитати ПОТОЧНУ місію з борту. Повертає список MISSION_ITEM_INT або None."""
    # 1. Попросити борт назвати кількість.
    master.mav.mission_request_list_send(TSYS, TCMP, MTYPE)
    cnt = master.recv_match(type='MISSION_COUNT', blocking=True, timeout=3)
    if cnt is None:
        print("зчитування: борт не назвав MISSION_COUNT")
        return None
    n = cnt.count
    print(f"зчитування: борт каже, у нього {n} пунктів")

    # 2. Просити кожен seq по порядку, з таймаутом і обмеженим числом повторів.
    items = [None] * n
    for seq in range(n):
        tries = 0
        while True:
            master.mav.mission_request_int_send(TSYS, TCMP, seq, MTYPE)
            it = master.recv_match(type='MISSION_ITEM_INT',
                                   blocking=True, timeout=timeout)
            # приймаємо лише ТОЙ пункт, який просили (чужий seq — відкинути й перепитати)
            if it is not None and it.seq == seq:
                items[seq] = it
                break
            tries += 1
            if tries >= max_retries:
                print(f"зчитування: пункт #{seq} не приходить — здаюся")
                return None          # НЕ повертаємо частковий список — він бреше

    # 3. Закрити діалог підтвердженням (ввічливість + сигнал борту «все взяв»).
    master.mav.mission_ack_send(TSYS, TCMP,
                                mavutil.mavlink.MAV_MISSION_ACCEPTED, MTYPE)
    return items
