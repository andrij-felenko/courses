// Стани завантаження місії.
enum UploadState { UP_IDLE, UP_SENT_COUNT, UP_SENDING_ITEMS, UP_DONE, UP_FAILED };

// Відіслати MISSION_COUNT — це СТАРТ завантаження.
static void send_mission_count(uint16_t count) {
    mavlink_message_t m;
    mavlink_msg_mission_count_pack(MY_SYSID, MY_COMPID, &m,
        TARGET_SYS, TARGET_COMP, count, MAV_MISSION_TYPE_MISSION);
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    serial_write(buf, mavlink_msg_to_send_buffer(buf, &m));
}

// Відіслати один елемент із масиву у відповідь на запит апарата.
static void send_mission_item(const mavlink_mission_item_int_t *it) {
    mavlink_message_t m;
    mavlink_msg_mission_item_int_pack(MY_SYSID, MY_COMPID, &m,
        it->target_system, it->target_component, it->seq, it->frame, it->command,
        it->current, it->autocontinue,
        it->param1, it->param2, it->param3, it->param4,
        it->x, it->y, it->z, it->mission_type);
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    serial_write(buf, mavlink_msg_to_send_buffer(buf, &m));
}

// Завантажити зібрану місію. Неблокувально-циклічна логіка: одна функція
// веде весь діалог. Повертає true при MAV_MISSION_ACCEPTED, false при відмові/тиші.
static bool upload_mission(const mavlink_mission_item_int_t *items, uint16_t count) {
    send_mission_count(count);
    UploadState st = UP_SENT_COUNT;
    uint32_t deadline = millis() + 1500;     // скільки чекати наступного запиту/ACK
    uint8_t retries = 0;

    while (st != UP_DONE && st != UP_FAILED) {
        mavlink_message_t msg;
        if (poll_mavlink(&msg)) {            // згодувати лінк парсеру, віддати кадр, якщо зібрався
            if (msg.msgid == MAVLINK_MSG_ID_MISSION_REQUEST_INT) {
                mavlink_mission_request_int_t req;
                mavlink_msg_mission_request_int_decode(&msg, &req);
                if (req.seq < count) {
                    send_mission_item(&items[req.seq]);   // апарат сам каже, який індекс
                    st = UP_SENDING_ITEMS;
                    deadline = millis() + 1500;           // отримали запит — таймер наново
                    retries = 0;
                }
            } else if (msg.msgid == MAVLINK_MSG_ID_MISSION_ACK) {
                mavlink_mission_ack_t ack;
                mavlink_msg_mission_ack_decode(&msg, &ack);
                st = (ack.type == MAV_MISSION_ACCEPTED) ? UP_DONE : UP_FAILED;
            }
            // решту повідомлень (телеметрію) тут-таки віддаємо своїй логіці
        }

        if ((int32_t)(deadline - millis()) <= 0) {        // апарат замовк
            if (++retries > 3) { st = UP_FAILED; break; }
            // повторюємо КРОК, що завис: на старті — COUNT; усередині — нічого
            // нового слати не треба, апарат сам перепитає загублений пункт,
            // тож просто чекаємо ще одне вікно (count повторюємо лише в UP_SENT_COUNT)
            if (st == UP_SENT_COUNT) send_mission_count(count);
            deadline = millis() + 1500;
        }
    }
    return st == UP_DONE;
}
