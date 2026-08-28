// Підбір амплітуди збурення на одній частоті: ростемо знизу, доки SNR не досить,
// але не вище стелі лінійності. Повертає вибрану амплітуду (частку керування).
float pick_amplitude(float f_test, float fs, float amp_ceiling, float snr_min)
{
    float amp = amp_ceiling * 0.05f;   // старт — дрібний, явно в лінійній зоні
    for (int tries = 0; tries < 6; tries++) {
        float p_sig = probe_power(f_test,        fs, amp);  // потужність на частоті збурення
        float p_nz  = probe_power(f_test * 1.7f, fs, amp);  // на сусідній — лише шум
        float snr   = p_sig / (p_nz + 1e-12f);
        if (snr >= snr_min) return amp;       // досить чисто — лишаємо цю амплітуду
        amp *= 2.0f;                          // інакше — голосніше
        if (amp > amp_ceiling) return amp_ceiling;  // але не за стелю лінійності
    }
    return amp_ceiling;
}
