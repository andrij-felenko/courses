#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Обчислення смуги когерентності та перевірка ризику ISI */
void analyze_channel(double rms_delay_spread_ns, double symbol_rate_ksps) {
    /* Переведення затримки у секунди */
    double sigma_sec = rms_delay_spread_ns * 1e-9;
    
    /* Смуга когерентності (50%) у кГц */
    double bc_50_khz = (1.0 / (5.0 * sigma_sec)) / 1000.0;
    
    /* Період символу у мікросекундах */
    double t_symbol_us = 1000.0 / symbol_rate_ksps;
    double rms_us = rms_delay_spread_ns / 1000.0;
    
    bool has_isi_risk = (t_symbol_us < 10.0 * rms_us);

    printf("RMS Delay Spread: %.1f нс\n", rms_delay_spread_ns);
    printf("Смуга когерентності B_c (50%%): %.1f кГц\n", bc_50_khz);
    printf("Період символу T_s: %.2f мкс (при %.1f кСимв/с)\n", t_symbol_us, symbol_rate_ksps);
    printf("Статус ISI: %s\n\n", has_isi_risk ? "НЕБЕЗПЕКА (потрібен еквалайзер/OFDM)" : "БЕЗПЕЧНО (плоске завмирання)");
}

int main(void) {
    /* Кімнатний Wi-Fi канал */
    analyze_channel(40.0, 1000.0);
    /* Міський стільниковий канал */
    analyze_channel(1500.0, 1000.0);
    return 0;
}
