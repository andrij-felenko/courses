#include <stdio.h>
#include <math.h>

typedef enum {
    IMPEDANCE_50_OHM = 50,
    IMPEDANCE_75_OHM = 75,
    IMPEDANCE_600_OHM = 600
} Impedance;

/* Перетворення потужності: dBm <-> Вт / мВт */
double dbm_to_mw(double dbm) {
    return pow(10.0, dbm / 10.0);
}

double mw_to_dbm(double mw) {
    return (mw > 0.0) ? 10.0 * log10(mw) : -999.0;
}

double dbm_to_dbw(double dbm) {
    return dbm - 30.0;
}

double dbw_to_dbm(double dbw) {
    return dbw + 30.0;
}

/* Перетворення між dBμV та dBm залежно від опору навантаження */
double dbmuv_to_dbm(double dbmuv, Impedance r) {
    double k = (r == IMPEDANCE_75_OHM) ? 108.75 : 106.99;
    return dbmuv - k;
}

double dbm_to_dbmuv(double dbm, Impedance r) {
    double k = (r == IMPEDANCE_75_OHM) ? 108.75 : 106.99;
    return dbm + k;
}

/* Перетворення напруги у dBV та dBu */
double dbv_to_volts(double dbv) {
    return pow(10.0, dbv / 20.0);
}

double dbu_to_volts(double dbu) {
    return 0.7745966 * pow(10.0, dbu / 20.0);
}

/* Перетворення підсилення антен: dBi <-> dBd */
double dbd_to_dbi(double dbd) {
    return dbd + 2.15;
}

double dbi_to_dbd(double dbi) {
    return dbi - 2.15;
}

/* Розрахунок C/N0 (dBHz) за потужністю сигналу та шумом */
double calculate_cn0(double signal_dbm, double bandwidth_hz) {
    const double noise_floor_dbm_hz = -173.98;
    double total_noise_dbm = noise_floor_dbm_hz + 10.0 * log10(bandwidth_hz);
    double snr_db = signal_dbm - total_noise_dbm;
    return snr_db + 10.0 * log10(bandwidth_hz);
}

int main(void) {
    double p_dbm = 20.0; /* 100 мВт Wi-Fi передавач */
    double gain_dbd = 9.0; /* 9 dBd Ягі-антена */
    
    printf("=== RF Unit Converter (C) ===\n");
    printf("Потужність: %.2f dBm = %.2f мВт = %.2f dBW\n", 
           p_dbm, dbm_to_mw(p_dbm), dbm_to_dbw(p_dbm));
    
    printf("Напруга у 50 Ом: %.2f dBm = %.2f dBuV\n", 
           p_dbm, dbm_to_dbmuv(p_dbm, IMPEDANCE_50_OHM));
           
    printf("Підсилення антени: %.2f dBd = %.2f dBi\n", 
           gain_dbd, dbd_to_dbi(gain_dbd));
           
    double rx_dbm = -90.0;
    double bw_hz = 20e6; /* 20 МГц смуга Wi-Fi */
    printf("C/N0 при %.2f dBm у смузі 20 МГц: %.2f dBHz\n", 
           rx_dbm, calculate_cn0(rx_dbm, bw_hz));
           
    return 0;
}
