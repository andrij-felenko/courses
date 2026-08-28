// Живий монітор прогресу: показує активний пункт і ловить момент досягнення.
// (Мовою прошивки для ясності; на практиці — pymavlink-цикл на землі.)
uint16_t last_seq = 0xFFFF;
for (;;) {
    mavlink_message_t msg;
    if (!recv_any(&msg, /*timeout_ms=*/1000)) { puts("тиша від борту — перевір лінк"); continue; }

    switch (msg.msgid) {
    case MAVLINK_MSG_ID_MISSION_CURRENT: {           // борт шле активний пункт
        mavlink_mission_current_t mc;
        mavlink_msg_mission_current_decode(&msg, &mc);
        if (mc.seq != last_seq) {                    // індекс зрушив — покажемо перехід
            printf("активний пункт місії: #%u\n", mc.seq);
            last_seq = mc.seq;
        }
        break;
    }
    case MAVLINK_MSG_ID_MISSION_ITEM_REACHED: {      // борт підтвердив: пункт виконано
        mavlink_mission_item_reached_t mr;
        mavlink_msg_mission_item_reached_decode(&msg, &mr);
        printf("  досягнуто #%u — перехід далі\n", mr.seq);
        break;
    }
    }
}
