// Виміряти петлеве підсилення на одній частоті f_test.
// Вкидаємо синус у керування, корелюємо відгук виходу з тим самим синусом.
struct loop_point_t { float mag_db; float phase_deg; };

loop_point_t measure_point(float f_test, float fs, uint32_t cycles, float amp)
{
    const float w   = 2.0f * 3.14159265f * f_test / fs;  // фаза за один відлік
    const uint32_t N = (uint32_t)(cycles * fs / f_test);  // ціла к-ть періодів

    float acc_i = 0.0f, acc_q = 0.0f;   // дійсна / уявна частини відгуку
    float ref_i = 0.0f, ref_q = 0.0f;   // те саме для опорного збурення

    for (uint32_t n = 0; n < N; n++) {
        float s = sinf(w * n);
        float drive = amp * s;          // мала добавка до керування
        ctrl_inject(drive);             // вкинути в петлю поверх керування

        float y = adc_read_output();    // відгук виходу через АЦП
        acc_i += y * sinf(w * n);       // кореляція з sin
        acc_q += y * cosf(w * n);       // кореляція з cos
        ref_i += drive * sinf(w * n);   // те саме для збурення
        ref_q += drive * cosf(w * n);
    }

    // Відношення комплексних амплітуд відгук/збурення = L(j2pi f_test)
    float out_re = acc_i, out_im = acc_q;
    float in_re  = ref_i, in_im  = ref_q;
    float den    = in_re * in_re + in_im * in_im;
    float L_re   = (out_re * in_re + out_im * in_im) / den;
    float L_im   = (out_im * in_re - out_re * in_im) / den;

    loop_point_t p;
    p.mag_db    = 10.0f * log10f(L_re * L_re + L_im * L_im);   // 20*log10(|L|) = 10*log10(|L|^2)
    p.phase_deg = atan2f(L_im, L_re) * 57.29578f;              // 180/pi
    return p;
}
