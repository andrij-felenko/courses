// Оцінка середнього часу доступу за різної частки влучань.
// (Ілюстративний розрахунок, не прошивковий гарячий шлях.)
#include <stdio.h>

double avg_access_ns(double hit_rate, double t_cache, double t_dram) {
    return hit_rate * t_cache + (1.0 - hit_rate) * t_dram;
}

int main(void) {
    double t_cache = 1.0, t_dram = 100.0;  // наносекунди

    // h = 0.90:  0.90·1 + 0.10·100 = 0.9 + 10.0 = 10.9 нс
    printf("%.1f ns\n", avg_access_ns(0.90, t_cache, t_dram));

    // h = 0.99:  0.99·1 + 0.01·100 = 0.99 + 1.0 = 1.99 нс
    printf("%.2f ns\n", avg_access_ns(0.99, t_cache, t_dram));
    return 0;
}
