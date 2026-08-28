// Викликати з диспетчера прийому, коли розпарсено COMMAND_ACK.
// msg — увесь кадр (з нього беремо sysid/compid = ХТО відповів).
void cmd_on_ack(cmd_loop_t *c, const mavlink_message_t *msg)
{
    if (c->state != CMD_WAITING)
        return;                       // ми нічого не чекаємо — ігноруємо

    mavlink_command_ack_t ack;
    mavlink_msg_command_ack_decode(msg, &ack);

    // ── ФІЛЬТР «свій» ACK: джерело кадру + номер команди ──────────────
    if (msg->sysid  != c->target_sys)  return;   // інший апарат
    if (msg->compid != c->target_comp) return;   // інший компонент (напр. камера)
    if (ack.command != c->command)     return;   // інша команда того ж борту

    // Це наш ACK. Запам'ятаємо результат і зреагуємо за ним.
    c->last_result = ack.result;
    cmd_apply_result(c, &ack);        // ← розбір MAV_RESULT нижче
}
