def upload_mission(master, items, timeout=0.25, max_retries=5):
    """Завантажити список пунктів рукостисканням. True — борт прийняв (ACK)."""
    n = len(items)

    # 1. Оголосити кількість. Далі темп задає БОРТ своїми запитами.
    master.mav.mission_count_send(TSYS, TCMP, n, MTYPE)

    # 2. Відповідати на запити борту, доки не роздамо всі пункти.
    #    Борт САМ вирішує, який seq просити наступним (зазвичай по порядку,
    #    але при втраті пакета — перепитує той самий).
    sent = 0
    retries = 0
    while sent < n:
        # Чекаємо запит пункту — від борту. Ловимо ОБИДВІ форми: _INT і стару.
        req = master.recv_match(
            type=['MISSION_REQUEST_INT', 'MISSION_REQUEST'],
            blocking=True, timeout=timeout)

        if req is None:                      # тиша: пакет загубився в той чи той бік
            retries += 1
            if retries > max_retries:
                print("завантаження: борт мовчить — скасовую")
                return False
            # Не сидимо склавши руки: повторно оголосимо count, щоб струснути діалог.
            master.mav.mission_count_send(TSYS, TCMP, n, MTYPE)
            continue

        retries = 0                          # прийшов запит — лічильник тиші скинуто
        seq = req.seq
        if seq >= n:                         # борт просить неіснуючий пункт — ігноруємо
            continue

        it = items[seq]                      # віддаємо саме той seq, що просять
        master.mav.mission_item_int_send(
            TSYS, TCMP, it['seq'], it['frame'], it['command'],
            0,                               # current
            it['autocontinue'],
            it['p1'], it['p2'], it['p3'], it['p4'],
            it['x'], it['y'], it['z'], MTYPE)
        sent = max(sent, seq + 1)            # відстежуємо найдальший відданий

    # 3. Дочекатися фінального підтвердження.
    ack = master.recv_match(type='MISSION_ACK', blocking=True, timeout=3)
    if ack is None:
        print("завантаження: немає MISSION_ACK — борт не підтвердив")
        return False
    if ack.type != mavutil.mavlink.MAV_MISSION_ACCEPTED:   # ACCEPTED == 0
        print(f"завантаження: борт відхилив, код MAV_MISSION_RESULT={ack.type}")
        return False
    print(f"завантаження: борт прийняв усі {n} пунктів (ACK=ACCEPTED)")
    return True
