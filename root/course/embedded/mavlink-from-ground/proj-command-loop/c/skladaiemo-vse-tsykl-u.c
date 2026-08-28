cmd_loop_t arm_loop;

void command_loop_init(void)
{
    memset(&arm_loop, 0, sizeof(arm_loop));
    arm_loop.state        = CMD_IDLE;
    arm_loop.timeout_ms   = 1000;   // ~секунда на ACK
    arm_loop.max_attempts = 5;      // перша + до чотирьох повторів
}

// Головний цикл прошивки (спрощено).
void main_loop_iteration(void)
{
    // 1) Прийом: читаємо канал, парсимо кадри
    uint8_t byte;
    mavlink_message_t msg;
    mavlink_status_t  status;
    while (link_read(&byte)) {                    // поки є вхідні байти
        if (mavlink_parse_char(MAVLINK_COMM_0, byte, &msg, &status)) {
            switch (msg.msgid) {
            case MAVLINK_MSG_ID_COMMAND_ACK:
                cmd_on_ack(&arm_loop, &msg);      // ← наш ACK?
                break;
            case MAVLINK_MSG_ID_HEARTBEAT:
                /* оновлення присутності — інша тема */
                break;
            /* … телеметрія, параметри тощо … */
            }
        }
    }

    // 2) Хід часу: тікаємо командний цикл (неблокувально)
    cmd_tick(&arm_loop);

    // 3) Реакція на завершення команди
    if (arm_loop.state == CMD_DONE) {
        arm_loop.state = CMD_IDLE;
        ui_notify("Армовано");                    // зелене — чесно
    } else if (arm_loop.state == CMD_FAILED) {
        arm_loop.state = CMD_IDLE;
        ui_notify_fail(arm_loop.last_result);     // з причиною, не мовчанка
    }
}
