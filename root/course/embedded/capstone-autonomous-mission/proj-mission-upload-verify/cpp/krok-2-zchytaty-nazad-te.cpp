// Зчитати ПОТОЧНУ місію з борту в out[] (місткість cap). *out_n — скільки пунктів.
// 1 — успіх; 0 — не вдалося (і тоді out[] НЕ містить часткового списку — він бреше).
int download_mission(mavlink_mission_item_int_t *out, uint16_t cap, uint16_t *out_n) {
    mavlink_message_t msg;
    // 1. Попросити борт назвати кількість.
    mavlink_msg_mission_request_list_pack(SYSID, COMPID, &msg, TSYS, TCMP, MTYPE);
    send_msg(&msg);
    const uint8_t want_cnt[] = { MAVLINK_MSG_ID_MISSION_COUNT };
    if (!recv_match(want_cnt, 1, &msg, 3.0)) { puts("зчитування: немає MISSION_COUNT"); return 0; }
    mavlink_mission_count_t mc; mavlink_msg_mission_count_decode(&msg, &mc);
    uint16_t n = mc.count;
    if (n > cap) { puts("зчитування: місія більша за буфер"); return 0; }
    printf("зчитування: борт каже, у нього %u пунктів\n", n);

    // 2. Просити кожен seq по порядку, з таймаутом і обмеженим числом повторів.
    const uint8_t want_item[] = { MAVLINK_MSG_ID_MISSION_ITEM_INT };
    for (uint16_t seq = 0; seq < n; seq++) {
        int ok = 0;
        for (int tries = 0; tries < 5 && !ok; tries++) {
            mavlink_msg_mission_request_int_pack(SYSID, COMPID, &msg, TSYS, TCMP, seq, MTYPE);
            send_msg(&msg);
            mavlink_message_t r;
            if (recv_match(want_item, 1, &r, 0.25)) {   // таймаут рятує від вічного чекання
                mavlink_mission_item_int_t it; mavlink_msg_mission_item_int_decode(&r, &it);
                if (it.seq == seq) { out[seq] = it; ok = 1; }   // лише ТОЙ, що просили
            }
        }
        if (!ok) {                                      // здався — НЕ віддаємо частковий список
            printf("зчитування: пункт #%u не приходить — здаюся\n", seq); return 0;
        }
    }
    // 3. Закрити діалог підтвердженням (ввічливість + сигнал борту «все взяв»).
    mavlink_msg_mission_ack_pack(SYSID, COMPID, &msg, TSYS, TCMP, MAV_MISSION_ACCEPTED, MTYPE);
    send_msg(&msg);
    *out_n = n;
    return 1;
}
