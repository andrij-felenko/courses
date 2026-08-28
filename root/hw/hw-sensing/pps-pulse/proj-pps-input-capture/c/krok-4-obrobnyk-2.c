// У головному циклі: чи прийшов новий фронт від останньої перевірки?
static uint32_t last_seen = 0;

int pps_take(uint64_t *stamp_out, uint32_t *index_out) {
    uint32_t cnt = pps_count;              // знімок лічильника фронтів
    if (cnt == last_seen) {
        return 0;                           // нового фронту не було
    }
    // Прочитати мітку АТОМАРНО щодо ISR: коротко закрити переривання таймера.
    NVIC_DisableIRQ(TIM2_IRQn);
    *stamp_out = pps_stamp;
    *index_out = cnt;
    NVIC_EnableIRQ(TIM2_IRQn);

    last_seen = cnt;
    return 1;                               // є свіжий фронт
}
