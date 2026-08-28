#include <stdio.h>
#include <math.h>

// Граничний SNR ідеального N-розрядного АЦП (повношкальна синусоїда), дБ.
float ideal_adc_snr_db(int bits) {
    return 6.02f * bits + 1.76f;
}

// Скільки розрядів треба, щоб дотягти до заданого SNR (округлення вгору).
int bits_for_snr(float target_db) {
    float n = (target_db - 1.76f) / 6.02f;   // обернена формула
    return (int)ceilf(n);                    // дробовий розряд не буває — вгору
}

int main(void) {
    float need = 80.0f;
    int n = bits_for_snr(need);              // (80 - 1.76)/6.02 = 13.0 -> 13
    printf("Для %.0f дБ треба %d розрядів; вони дають %.1f дБ\n",
           need, n, ideal_adc_snr_db(n));    // 13 біт -> 80.0 дБ
    printf("14 розрядів дали б %.1f дБ (запас на залізо)\n",
           ideal_adc_snr_db(14));            // 86.0 дБ
    return 0;
}
