// Надійна відправка команди: повтори з нарощуванням confirmation,
// розбір MAV_RESULT, обмеження спроб. Псевдо-C у стилі pymavlink-виклику.
typedef enum { CMD_OK, CMD_RETRY_LATER, CMD_REFUSED, CMD_TIMEOUT } cmd_outcome_t;

cmd_outcome_t send_command_reliable(mavlink_conn_t *m, uint16_t command,
                                    const float p[7], int max_tries)
{
    for (int confirmation = 0; confirmation < max_tries; confirmation++) {
        command_long_send(m, m->target_system, m->target_component,
                          command, confirmation,
                          p[0], p[1], p[2], p[3], p[4], p[5], p[6]);

        uint32_t deadline = millis() + 1000;          // таймер на ACK: 1 с
        for (;;) {
            mavlink_message_t *ack = recv_match(m, "COMMAND_ACK",
                                                deadline - millis());
            if (!ack) break;                          // таймаут → зовнішній повтор

            if (ack->command != command) continue;    // ACK не на нашу команду
            switch (ack->result) {
                case MAV_RESULT_ACCEPTED:      return CMD_OK;
                case MAV_RESULT_IN_PROGRESS:   deadline = millis() + 5000;
                                               continue;   // довга дія: чекаємо далі
                case MAV_RESULT_TEMPORARILY_REJECTED: return CMD_RETRY_LATER;
                case MAV_RESULT_DENIED:
                case MAV_RESULT_UNSUPPORTED:
                case MAV_RESULT_FAILED:        return CMD_REFUSED;  // повтор марний
                default:                       return CMD_REFUSED;
            }
        }
    }
    return CMD_TIMEOUT;                                // вичерпали спроби
}
