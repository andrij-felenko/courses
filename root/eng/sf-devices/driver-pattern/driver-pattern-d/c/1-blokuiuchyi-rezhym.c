/* Безпечне очікування прапорця з дедлайном */
static driver_status_t wait_flag_timeout(volatile uint32_t* reg, uint32_t flag,
                                         bool wait_for_set, uint32_t timeout_cycles) {
    while (timeout_cycles > 0) {
        bool is_set = (*reg & flag) != 0;
        if (is_set == wait_for_set) {
            return DRIVER_STATUS_OK;
        }
        timeout_cycles--;
        __NOP(); /* Запобігає агресивній оптимізації доступу до шини */
    }
    return DRIVER_STATUS_TIMEOUT;
}
