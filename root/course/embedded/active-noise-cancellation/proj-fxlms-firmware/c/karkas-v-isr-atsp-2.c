// головний цикл: чекає готовий блок і перемелює його такт за тактом
void anc_main_loop(void)
{
    if (!identify_secondary_path()) {
        anc_set_passthrough();     // S не виміряли — гасіння НЕ вмикаємо
        return;
    }

    for (;;) {
        if (ready_idx < 0) { cpu_idle(); continue; }   // блоку нема — поспати до IRQ

        int idx = ready_idx;
        uint32_t t0 = cycle_counter();                 // ← заміряти завантаження CPU

        for (int k = 0; k < BLK; ++k) {
            q15_t ref = buf_ref[idx][k];
            q15_t err = buf_err[idx][k];
            q15_t y   = fxlms_step_q15(ref, err);      // бойовий такт
            watchdog(err);                             // рубіж 3
            dac_write_q15(y);                          // анти-шум у динамік
        }

        uint32_t dt = cycle_counter() - t0;            // тактів на весь блок
        update_cpu_load(dt);                           // ← оцінка завантаження

        ready_idx = -1;            // блок оброблено, ISR може дати наступний
    }
}
