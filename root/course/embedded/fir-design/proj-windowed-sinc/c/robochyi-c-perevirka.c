// |H(f)| для КІХ із коефіцієнтами b[0..N-1] — точно, через ДПФ в одній точці.
// Жодного фільтрування й усталення: для КІХ характеристика = спектр коефіцієнтів.
static float fir_mag_at(const float *b, int N, float f, float fs_sample)
{
    const double w = 2.0 * M_PI * (double)f / fs_sample;   // норм. частота, рад
    double re = 0.0, im = 0.0;
    for (int k = 0; k < N; ++k) {
        re += (double)b[k] * cos(w * k);
        im -= (double)b[k] * sin(w * k);
    }
    return (float)sqrt(re * re + im * im);     // модуль |H| у разах
}
