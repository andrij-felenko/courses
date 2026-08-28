void rover_loop(void)
{
    hbridge_init();

    uint16_t ch_thr = RC_MID, ch_str = RC_MID;  // старт: стіки в центрі
    float    i_total = 0.0f;
    uint32_t next_drive = 0;

    for (;;) {
        uint32_t now = millis();

        // 1) З'їдаємо всі готові кадри з приймача; кожен свіжий — штампуємо час.
        rc_frame_t f;
        while (rc_poll(&f)) {              // неблокуюче читання приймача
            ch_thr = f.channel[RC_CH_THROTTLE];
            ch_str = f.channel[RC_CH_STEER];
            rc_mark_fresh(now);            // ← ось тут оживає годинник failsafe
        }

        // 2) Драйвер тикає своїм тактом (10 мс), незалежно від кадрів приймача.
        if ((int32_t)(now - next_drive) >= 0) {
            next_drive = now + 10;
            i_total = read_total_current_A();   // струм обох бортів (шунт/давач)
            chassis_update(ch_thr, ch_str, i_total, now);
        }

        // 3) Решта: телеметрія, світлодіоди стану, службові задачі.
    }
}
