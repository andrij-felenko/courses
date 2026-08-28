// Каркас бортового циклу: нічого не блокує; усе рухається за таймерами.
void companion_loop(mavlink_conn_t *m)
{
    uint32_t last_hb_seen = millis();
    for (;;) {
        // 1) вичерпуємо все, що вже прийшло — без блокування
        mavlink_message_t *msg;
        while ((msg = recv_match(m, NULL, /*timeout=*/0)) != NULL) {
            switch (msg->msgid) {
                case MAVLINK_MSG_ID_HEARTBEAT:
                    last_hb_seen = millis();          // лінія жива
                    break;
                case MAVLINK_MSG_ID_ATTITUDE:
                    update_attitude(msg);             // оновили стан
                    break;
                // …інші типи…
            }
        }

        // 2) власна логіка за таймером (зір, план, регулятор)
        run_control_step(m);

        // 3) нагляд за обривом: серцебиття мовчить понад 3 с
        if (millis() - last_hb_seen > 3000) {
            handle_link_loss(m);                       // безпечний режим / повторне під'єднання
            last_hb_seen = millis();
        }

        sleep_ms(10);                                 // не крутимо цикл марно на 100%
    }
}
