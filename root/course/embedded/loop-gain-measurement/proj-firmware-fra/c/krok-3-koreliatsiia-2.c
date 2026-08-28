typedef struct { float mag_db; float phase_deg; int valid; } loop_point_t;

// Виміряти одну точку петлевого підсилення на частоті f_test.
// amp — амплітуда збурення (частка керування), cycles — скільки цілих періодів накопичити.
loop_point_t measure_point(float f_test, float fs, uint32_t cycles, float amp)
{
    uint32_t N    = whole_period_N(f_test, fs, cycles);  // рівно цілі періоди
    uint32_t step = phase_step(f_test, fs);              // крок фазового акумулятора

    // Бін збурення у вікні N: за побудовою це рівно `cycles`.
    int k = (int)cycles;

    goertzel_t g_out, g_ref;
    g_set_bin(&g_out, k, N);
    g_set_bin(&g_ref, k, N);

    uint32_t phase = 0;
    for (uint32_t n = 0; n < N; n++) {
        float drive = amp * sine_from_phase(phase);  // збурення з таблиці
        phase += step;                                // фаза сама обгортається

        ctrl_inject(drive);            // вкинути в керування поверх робочого
        float y = adc_read_output();   // відгук виходу через АЦП

        g_push(&g_out, y);             // меле відгук
        g_push(&g_ref, drive);         // меле опору (те, що вкинули)
    }

    float out_re, out_im, ref_re, ref_im;
    g_result(&g_out, k, N, &out_re, &out_im);
    g_result(&g_ref, k, N, &ref_re, &ref_im);

    // L = (вихід) / (збурення) — ділення комплексних чисел.
    float den  = ref_re * ref_re + ref_im * ref_im;
    loop_point_t p = { 0.0f, 0.0f, 0 };
    if (den < 1e-20f) return p;        // збурення згасло — точка недійсна
    float L_re = (out_re * ref_re + out_im * ref_im) / den;
    float L_im = (out_im * ref_re - out_re * ref_im) / den;

    p.mag_db    = 10.0f * log10f(L_re * L_re + L_im * L_im);  // 20·log10|L| = 10·log10|L|²
    p.phase_deg = atan2f(L_im, L_re) * (180.0f / (float)M_PI);
    p.valid     = 1;
    return p;
}
