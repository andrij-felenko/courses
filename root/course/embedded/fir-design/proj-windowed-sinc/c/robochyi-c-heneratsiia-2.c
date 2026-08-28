// Згенерувати КІХ-ФНЧ методом вікон у b[0..N-1].
//   fc        — центр переходу, Гц:  (fp + fs)/2  (ставимо «цеглину» посередині)
//   fs_sample — частота дискретизації, Гц
//   N         — число відводів (краще НЕПАРНЕ → точний центральний відвід, чиста симетрія)
//   win, beta — вікно й (для Кайзера) його параметр форми
// Повертає false, якщо аргументи безглузді (N<1 або fc поза (0, fs/2)).
bool firwin_lpf(float *b, int N,
                float fc, float fs_sample,
                WindowKind win, float beta)
{
    if (N < 1 || fc <= 0.0f || fc >= 0.5f * fs_sample) return false;

    const int    M  = N - 1;                              // порядок
    const double wc = 2.0 * M_PI * (double)fc / fs_sample; // норм. частота зрізу
    const double i0_beta = (win == WIN_KAISER) ? bessel_i0((double)beta) : 1.0;

    double sum = 0.0;            // фактична сума ваг — для нормування по DC

    for (int k = 0; k <= M; ++k) {
        int    n = k - M / 2;                       // зсув від центру, симетрично
        double ideal;

        // 1) ідеальний sinc із чесною границею sin(0)/0 = wc/π у центрі
        if (n == 0)  ideal = wc / M_PI;
        else         ideal = sin(wc * n) / (M_PI * n);

        // 2) значення вікна для цього відводу
        double w;
        if (win == WIN_HAMMING) {
            // дві канонічні константи Геммінга
            w = 0.54 - 0.46 * cos(2.0 * M_PI * (double)k / (double)M);
        } else {  // WIN_KAISER
            // ratio = 2k/M − 1 ∈ [−1, +1]; під коренем — 1 − ratio²
            double ratio = 2.0 * (double)k / (double)M - 1.0;
            double arg   = beta * sqrt(1.0 - ratio * ratio);
            w = bessel_i0(arg) / i0_beta;
        }

        double tap = ideal * w;     // 3) завіконений відвід
        b[k] = (float)tap;
        sum += tap;                 // копимо суму у double — точніше
    }

    // 4) нормування по DC: сума ваг = 1  ⇒  підсилення на нульовій частоті = 1.0
    if (sum == 0.0) return false;   // патологія (напр. fc≈0) — не ділимо на нуль
    float inv = (float)(1.0 / sum);
    for (int k = 0; k <= M; ++k)
        b[k] *= inv;

    return true;
}
