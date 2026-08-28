// Тік точного часу: пробуємо видати одну повну, скориговану позначку
// межі секунди. Повертає 1, якщо цього разу вийшла свіжа пара.
static uint32_t timtp_seen = 0;

int pps_solve(uint64_t *edge_ticks_out, int32_t *qErr_out, uint32_t *tow_ms_out) {
    pps_drain();                          // забрати свіжі фронти в чергу

    uint32_t mc = timtp_count;            // скільки повідомлень уже є
    if (mc == timtp_seen) {
        return 0;                          // нового повідомлення нема
    }

    // Свіже повідомлення з індексом (mc-1) описує фронт із тим самим індексом.
    uint32_t idx = mc - 1;
    uint64_t edge;
    if (edge_lookup(idx, &edge) != 0) {
        // Мітки цього фронту в черзі вже нема (UART відстав > PPS_Q секунд,
        // або фронт випав) — цю пару чесно ПРОПУСКАЄМО, а не зшиваємо навмання.
        timtp_seen = mc;
        return -1;
    }

    // Прочитати поля повідомлення атомарно щодо UART-ISR.
    __disable_irq();
    int32_t  q  = timtp_msg.qErr;         // пікосекунди, знакова
    uint32_t tw = timtp_msg.towMS;        // мс тижня
    __enable_irq();

    *edge_ticks_out = edge;
    *qErr_out       = q;
    *tow_ms_out     = tw;
    timtp_seen      = mc;
    return 1;
}
