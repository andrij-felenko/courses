// Гнати цикл уперед. Викликати ЩООБЕРТУ головного циклу (не рідко!).
void cmd_tick(cmd_loop_t *c)
{
    if (c->state != CMD_WAITING)
        return;                       // активної команди немає

    // Ще не час? — виходимо миттєво, канал не чіпаємо.
    if ((int32_t)(now_ms() - c->deadline_ms) < 0)
        return;

    // Дедлайн збіг: ACK не прийшов вчасно.
    if (c->attempts_left > 0) {
        c->attempts_left--;
        c->confirmation++;            // ← повтор → росте поле пакета
        cmd_send_now(c);              // той самий наказ, новий deadline
    } else {
        c->state = CMD_FAILED;        // спроби скінчились — чесно здаємось
    }
}
