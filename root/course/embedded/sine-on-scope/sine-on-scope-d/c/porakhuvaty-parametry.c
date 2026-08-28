#include <stdint.h>
#include <math.h>

// Одним проходом: мінімум, максимум і сума квадратів навколо середнього.
// Повертає Vpp (розмах) і Vrms (True RMS) у вольтах.
void measure_sine(const uint16_t *buf, uint32_t n,
                  float lsb_volts,            // вольтів на один код АЦП
                  float *vpp_out, float *vrms_out)
{
    uint16_t vmin = 0xFFFF, vmax = 0;
    double sum = 0.0;                          // для середнього (постійна складова)
    for (uint32_t i = 0; i < n; i++) {
        uint16_t s = buf[i];
        if (s < vmin) vmin = s;
        if (s > vmax) vmax = s;
        sum += s;
    }
    double mean = sum / n;                     // рівень постійної складової в кодах

    // True RMS ЗМІННОЇ складової: віднімаємо середнє, тоді √(середнє квадратів).
    double sq = 0.0;
    for (uint32_t i = 0; i < n; i++) {
        double ac = (double)buf[i] - mean;     // прибрали постамент (як AC-зв'язок)
        sq += ac * ac;
    }
    double rms_codes = sqrt(sq / n);

    *vpp_out  = (float)(vmax - vmin) * lsb_volts;
    *vrms_out = (float)rms_codes * lsb_volts;
}
