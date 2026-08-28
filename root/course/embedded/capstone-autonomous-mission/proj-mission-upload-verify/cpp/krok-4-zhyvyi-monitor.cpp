// Живий монітор: показує активний пункт і момент його досягнення.
// Крутити паралельно польоту; Ctrl-C — вихід.
void monitor_mission(void) {
    uint16_t last_seq = 0xFFFF;
    const uint8_t want[] = { MAVLINK_MSG_ID_MISSION_CURRENT,
                             MAVLINK_MSG_ID_MISSION_ITEM_REACHED };
    for (;;) {
        mavlink_message_t msg;
        if (!recv_match(want, 2, &msg, 1.0)) { puts("… тиша від борту — перевір лінк"); continue; }

        if (msg.msgid == MAVLINK_MSG_ID_MISSION_CURRENT) {
            mavlink_mission_current_t mc; mavlink_msg_mission_current_decode(&msg, &mc);
            if (mc.seq != last_seq) {                // індекс зрушив — покажемо перехід
                printf("→ активний пункт місії: #%u\n", mc.seq);
                last_seq = mc.seq;
            }
        } else {  // MISSION_ITEM_REACHED
            mavlink_mission_item_reached_t mr; mavlink_msg_mission_item_reached_decode(&msg, &mr);
            printf("  ✓ досягнуто #%u — борт переходить далі\n", mr.seq);
        }
    }
}
