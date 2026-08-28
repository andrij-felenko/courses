// Продовжити (чи скасувати) таймаут довгої операції.
#define IN_PROGRESS_TIMEOUT_MS  30000u   // калібрування тощо — десятки секунд

// Зреагувати на результат НАШОГО ACK.
static void cmd_apply_result(cmd_loop_t *c, const mavlink_command_ack_t *ack)
{
    switch (ack->result) {

    case MAV_RESULT_ACCEPTED:
        c->state = CMD_DONE;                 // готово, вихід з циклу
        break;

    case MAV_RESULT_IN_PROGRESS:
        // Борт чесно працює. Не вважаємо це спробою й НЕ повторюємо —
        // лише РІЗКО відсуваємо дедлайн, чекаючи фінального ACK.
        c->progress     = ack->progress;     // 0..100 (чи UINT8_MAX)
        c->deadline_ms  = now_ms() + IN_PROGRESS_TIMEOUT_MS;
        // лишаємось у CMD_WAITING
        break;

    case MAV_RESULT_TEMPORARILY_REJECTED:
        // Минуща причина. Дамо їй розсмоктатись і повторимо — АЛЕ як спробу.
        if (c->attempts_left > 0) {
            c->attempts_left--;
            c->confirmation++;
            c->deadline_ms = now_ms() + c->timeout_ms;
            cmd_send_now(c);                 // той самий наказ, згодом
        } else {
            c->state = CMD_FAILED;           // так і не дочекались вікна
        }
        break;

    case MAV_RESULT_DENIED:
    case MAV_RESULT_UNSUPPORTED:
    case MAV_RESULT_FAILED:
    case MAV_RESULT_CANCELLED:
    default:
        // Повтор безнадійний: причина стала (для цих кодів) або невідома.
        // Не сиплемо пакети в канал — одразу підсумок оператору.
        c->state = CMD_FAILED;
        break;
    }
}
