/* Замір часу виконання циклу обчислень безпосередньо з QSPI Flash (C) */
uint32_t benchmark_qspi_execution(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    /* Покажчик на обчислювальну функцію, розташовану за адресою 0x90001000 у QSPI Flash */
    typedef uint32_t (*compute_fn_t)(const uint32_t *data, size_t len);
    compute_fn_t run_from_qspi = (compute_fn_t)(0x90001001U); // Thumb-адреса з непарним LSB

    static const uint32_t test_array[256] = { /* масив вхідних даних */ };

    uint32_t t_start = DWT->CYCCNT;
    uint32_t sum = run_from_qspi(test_array, 256);
    uint32_t t_elapsed = DWT->CYCCNT - t_start;

    (void)sum;
    return t_elapsed;
}
