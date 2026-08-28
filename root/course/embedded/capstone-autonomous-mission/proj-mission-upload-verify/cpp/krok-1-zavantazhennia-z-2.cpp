// 1 — борт прийняв усі пункти (ACK). Точно та сама стан-машина, що в Python.
int upload_mission(const wp_t *items, uint16_t n) {
    mavlink_message_t msg;
    // 1. Оголосити кількість. Далі темп задає БОРТ своїми запитами.
    mavlink_msg_mission_count_pack(SYSID, COMPID, &msg, TSYS, TCMP, n, MTYPE);
    send_msg(&msg);

    // 2. Відповідати на запити борту, доки не роздамо всі пункти. Ловимо ОБИДВІ форми.
    const uint8_t want_req[] = { MAVLINK_MSG_ID_MISSION_REQUEST_INT,
                                 MAVLINK_MSG_ID_MISSION_REQUEST };
    uint16_t sent = 0; int retries = 0;
    while (sent < n) {
        if (!recv_match(want_req, 2, &msg, 0.25)) {   // тиша: пакет загубився
            if (++retries > 5) { puts("завантаження: борт мовчить — скасовую"); return 0; }
            mavlink_msg_mission_count_pack(SYSID, COMPID, &msg, TSYS, TCMP, n, MTYPE);
            send_msg(&msg);                            // струснути діалог
            continue;
        }
        retries = 0;                                  // прийшов запит — тишу скинуто
        uint16_t seq;                                 // борт САМ називає, який seq дати
        if (msg.msgid == MAVLINK_MSG_ID_MISSION_REQUEST_INT) {
            mavlink_mission_request_int_t q;
            mavlink_msg_mission_request_int_decode(&msg, &q); seq = q.seq;
        } else {
            mavlink_mission_request_t q;
            mavlink_msg_mission_request_decode(&msg, &q); seq = q.seq;
        }
        if (seq >= n) continue;                       // просить неіснуючий — ігноруємо

        const wp_t *it = &items[seq];                 // віддаємо саме той seq, що просять
        mavlink_msg_mission_item_int_pack(SYSID, COMPID, &msg, TSYS, TCMP,
            it->seq, it->frame, it->command,
            0,                                        // current
            it->autocontinue,
            it->p1, it->p2, it->p3, it->p4,
            it->x, it->y, it->z, MTYPE);
        send_msg(&msg);
        if (seq + 1 > sent) sent = seq + 1;           // відстежуємо найдальший відданий
    }

    // 3. Дочекатися фінального підтвердження.
    const uint8_t want_ack[] = { MAVLINK_MSG_ID_MISSION_ACK };
    if (!recv_match(want_ack, 1, &msg, 3.0)) {
        puts("завантаження: немає MISSION_ACK — борт не підтвердив"); return 0;
    }
    mavlink_mission_ack_t ack; mavlink_msg_mission_ack_decode(&msg, &ack);
    if (ack.type != MAV_MISSION_ACCEPTED) {           // ACCEPTED == 0
        printf("завантаження: борт відхилив, код MAV_MISSION_RESULT=%u\n", ack.type);
        return 0;
    }
    printf("завантаження: борт прийняв усі %u пунктів (ACK=ACCEPTED)\n", n);
    return 1;
}
