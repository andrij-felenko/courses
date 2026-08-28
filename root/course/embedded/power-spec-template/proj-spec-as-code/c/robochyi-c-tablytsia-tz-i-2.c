// Дзеркальний опис ТЗ людською мовою — для рев'ю. Кожне речення обчислене
// з полів, тож не може суперечити ні таблиці, ні перевіркам, ні валідації.
void print_spec_review(const power_spec_t *s) {
    // вікно допуску виходу в мВ (для людського «5.00 .. 5.10 В")
    uint32_t tol_mv = (uint32_t)s->vout_mv * s->vout_tol_pct / 100u;
    printf("Опис ТЗ для рев'ю\n=================\n");
    printf("Вхід гуляє від %u до %u мВ; перетворювач мусить тримати вихід\n"
           "на ОБОХ краях, з просіданням до %u мВ під пуском. Гранично\n"
           "допустимий вхід %u мВ — під комутаційні викиди.\n",
           s->vin_min_mv, s->vin_max_mv, s->vin_droop_mv, s->vin_absmax_mv);
    printf("Вихід %u мВ у вікні %u..%u мВ (±%u%%); пульсація <= %u мВ pp,\n"
           "шум <= %u мВ rms.\n",
           s->vout_mv, s->vout_mv - tol_mv, s->vout_mv + tol_mv,
           s->vout_tol_pct, s->vout_ripple_mvpp, s->vout_noise_mvrms);
    printf("Навантаження: %u мА типово, %u мА пік, "
           "стрибки до %u мА зі швидкістю %u мА/мкс.\n",
           s->iout_typ_ma, s->iout_peak_ma,
           s->iout_transient_ma, s->transient_slew_ma_us);
    printf("Середовище: %d..%d °C, дератинг від %d °C, ресурс %u тис.год.\n",
           s->ta_min_c, s->ta_max_c, s->ta_derate_c, s->life_hours_kh);
}
