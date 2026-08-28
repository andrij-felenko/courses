void check_two_rates(void) {
    loop_t m = {
        .Kp = 5.0, .Ki = 8.0, .Kd = 0.06, .tau_d = 0.001,
        .tau_p1 = 0.02, .tau_p2 = 0.008, .tau_sensor = 0.004,
        .t_compute = 0.0,             // видаємо в тому ж такті
    };

    m.Ts = 1.0 / 200.0;              // 200 Гц
    margins_t a = measure_margins(&m, 1.0, 6000.0, 8000);
    printf("fs=200:  PM=%.1f deg,  GM=%.1f dB,  fc=%.1f Hz\n",
           a.phase_margin_deg, a.gain_margin_db, a.wc / (2 * M_PI));

    m.Ts = 1.0 / 1000.0;             // 1000 Гц
    margins_t b = measure_margins(&m, 1.0, 6000.0, 8000);
    printf("fs=1000: PM=%.1f deg,  GM=%.1f dB,  fc=%.1f Hz\n",
           b.phase_margin_deg, b.gain_margin_db, b.wc / (2 * M_PI));
}

/* Виведе приблизно:
   fs=200:  PM=14.4 deg,  GM=1.9 dB,  fc=40.4 Hz     ← грань зриву
   fs=1000: PM=43.5 deg,  GM=9.2 dB,  fc=40.4 Hz     ← здоровий запас
   Той самий контур, ті самі коефіцієнти — лише рідший семпл, і запас упав
   із 43° до 14°: дискретність з'їла майже 30° рівно на ωc·(T/2). */
