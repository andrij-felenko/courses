#include <stdint.h>

// Сталі плати: міряються один раз при калібруванні й далі живуть у прошивці.
#define RS_MOHM     45      // послідовний опір ДО ключа: вхідний FET + шунт + доріжки
#define KAPPA_PPM   30000   // κ = (t_r + t_f)·f_sw = 20 нс × 1.5 МГц = 0.03
#define VHEAD_MV    300     // запас, нижче якого понижувач випадає з регулювання
#define VSTEP_MV    200     // крок сітки, у яку однаково доведеться округлити

// ⌊∛n⌋ цілими: двійковий пошук по бітах результату.
// 21 біта досить — (2²¹)³ = 2⁶³ перекриває весь uint64_t.
static uint32_t icbrt64(uint64_t n) {
    uint32_t r = 0;
    for (int b = 20; b >= 0; b--) {
        uint32_t t = r | (1u << b);
        if ((uint64_t)t * t * t <= n) r = t;
    }
    return r;
}

// V* = ∛(4·Vb²·Io·Rs/κ). У мВ/мА/мОм множник 1000 вирівнює степені десятки.
static uint32_t vbus_optimum_mv(uint32_t vbat_mv, uint32_t ichg_ma) {
    uint64_t v3 = 4ull * vbat_mv * vbat_mv;   // 4·Vb²
    v3 = v3 * ichg_ma / KAPPA_PPM;            // ·Io/κ — ділимо РАНО, поки не рознесло
    v3 = v3 * RS_MOHM * 1000ull;              // ·Rs та вирівнювання одиниць → мВ³
    return icbrt64(v3);
}

// Модель дає ідеал; реальність затискає його підлогою й сіткою.
uint32_t vbus_target_mv(uint32_t vbat_mv, uint32_t ichg_ma) {
    uint32_t v = vbus_optimum_mv(vbat_mv, ichg_ma);

    // Підлога: під повним струмом на вході ключа мусить лишитись Vb + запас.
    uint32_t iin_ma   = (uint32_t)((uint64_t)ichg_ma * vbat_mv / v);  // Iвх = Io·Vb/V
    uint32_t floor_mv = vbat_mv + (iin_ma * RS_MOHM) / 1000 + VHEAD_MV;
    if (v < floor_mv) v = floor_mv;

    // Округлюємо ВГОРУ: яма перекошена, промах угору дешевший за промах униз.
    return ((v + VSTEP_MV - 1) / VSTEP_MV) * VSTEP_MV;
}
