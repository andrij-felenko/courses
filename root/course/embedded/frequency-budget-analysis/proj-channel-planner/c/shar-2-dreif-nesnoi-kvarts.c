// Дрейф несної з ОДНОГО боку: кварцовий + доплерівський, Гц.
// Усе вже в герцах і м/с — мішанки одиниць тут бути не може.
static double carrier_drift_one_side(const radio_spec *r) {
    // Кварц: Δf = f₀ · (ppm · 10⁻⁶).
    // КЛЮЧОВО: спершу ppm·1e-6 (мала частка), ТОДІ множимо на несну.
    double quartz_hz = r->carrier_hz * (r->ppm * 1e-6);

    // Доплер: f_доплер = f₀ · v / c.  c — швидкість світла, м/с.
    const double C_LIGHT = 299792458.0;          // точне значення, м/с
    double doppler_hz = r->carrier_hz * (r->rel_speed_ms / C_LIGHT);

    return quartz_hz + doppler_hz;
}
