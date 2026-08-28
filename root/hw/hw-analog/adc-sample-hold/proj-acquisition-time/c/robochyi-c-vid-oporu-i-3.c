void adc_setup_channel(uint8_t ch, double r_src_ohm)
{
    uint8_t smp = adc_pick_smp_code(r_src_ohm, /*n_bits=*/12,
                                    /*f_adc_hz=*/12.0e6);

    if (smp == ADC_SMP_NEED_BUFFER) {
        /* Джерело задобре для внутрішнього набору — сюди має стояти
         * зовнішній буфер. Не приховуємо проблему, а сигналимо. */
        error_high_impedance_source(ch);
        smp = 7;   /* аварійно беремо найдовший, показ буде занижений */
    }

    /* Записати SMP[2:0] у потрібне поле SMPR2 для каналу ch (0..9).
     * Кожен канал займає 3 біти. */
    uint32_t shift = 3u * ch;
    ADC1->SMPR2 = (ADC1->SMPR2 & ~(0x7u << shift)) | ((uint32_t)smp << shift);
}
