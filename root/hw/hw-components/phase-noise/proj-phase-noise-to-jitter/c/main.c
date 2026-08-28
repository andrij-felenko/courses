#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double freq_offset_hz;  // Частота відступу f_m (Гц)
    double phase_noise_dbc; // Спектральна густина L(f_m) (дБн/Гц)
} PhaseNoisePoint;

typedef struct {
    double integrated_phase_noise_rad; // RMS фазова похибка (радіани)
    double integrated_phase_noise_deg; // RMS фазова похибка (градуси)
    double rms_jitter_sec;             // RMS часовий джитер (секунди)
    double adc_snr_limit_db;           // Граничний SNR АЦП (дБ)
    double adc_enob_limit;             // Гранична розрядність ENOB (біт)
} JitterResult;

// Інтерполяція спектральної густини у подвійному логарифмічному масштабі
static double interpolate_pn(double f, const PhaseNoisePoint* pts, size_t count) {
    if (f <= pts[0].freq_offset_hz) return pts[0].phase_noise_dbc;
    if (f >= pts[count - 1].freq_offset_hz) return pts[count - 1].phase_noise_dbc;

    for (size_t i = 0; i < count - 1; ++i) {
        if (f >= pts[i].freq_offset_hz && f <= pts[i + 1].freq_offset_hz) {
            double f1 = pts[i].freq_offset_hz;
            double f2 = pts[i + 1].freq_offset_hz;
            double l1 = pts[i].phase_noise_dbc;
            double l2 = pts[i + 1].phase_noise_dbc;
            double slope = (l2 - l1) / log10(f2 / f1);
            return l1 + slope * log10(f / f1);
        }
    }
    return pts[count - 1].phase_noise_dbc;
}

// Посегментне аналітичне інтегрування степеневого спектра
static double integrate_segment(double f1, double l1, double f2, double l2) {
    if (f2 <= f1 || f1 <= 0.0) return 0.0;

    double p1 = pow(10.0, l1 / 10.0);
    double p2 = pow(10.0, l2 / 10.0);
    double slope_alpha = log10(p2 / p1) / log10(f2 / f1);

    if (fabs(slope_alpha + 1.0) < 1e-5) {
        // Випадок спаду -10 дБ/декаду (1/f шум): інтеграл від 1/f дає натуральний логарифм
        return p1 * f1 * log(f2 / f1);
    } else {
        // Загальний степеневий випадок для довільного нахилу alpha
        double k = p1 / pow(f1, slope_alpha);
        double alpha_plus_1 = slope_alpha + 1.0;
        return (k / alpha_plus_1) * (pow(f2, alpha_plus_1) - pow(f1, alpha_plus_1));
    }
}

// Головна функція розрахунку параметрів джитеру
JitterResult calculate_phase_jitter(
    const PhaseNoisePoint* table,
    size_t count,
    double carrier_freq_hz,
    double f_start_hz,
    double f_stop_hz,
    double adc_input_freq_hz
) {
    JitterResult res = {0};
    if (count < 2 || f_start_hz >= f_stop_hz || carrier_freq_hz <= 0.0) {
        return res;
    }

    double total_ssb_power = 0.0;
    double cur_f = f_start_hz;
    double cur_l = interpolate_pn(cur_f, table, count);

    for (size_t i = 0; i < count; ++i) {
        double pt_f = table[i].freq_offset_hz;
        if (pt_f <= f_start_hz) continue;

        double next_f = (pt_f > f_stop_hz) ? f_stop_hz : pt_f;
        double next_l = interpolate_pn(next_f, table, count);

        total_ssb_power += integrate_segment(cur_f, cur_l, next_f, next_l);
        cur_f = next_f;
        cur_l = next_l;

        if (cur_f >= f_stop_hz) break;
    }

    if (cur_f < f_stop_hz) {
        double next_f = f_stop_hz;
        double next_l = interpolate_pn(next_f, table, count);
        total_ssb_power += integrate_segment(cur_f, cur_l, next_f, next_l);
    }

    // Повна двостороння дисперсія фази: sigma_phi^2 = 2 * P_SSB
    double phase_variance = 2.0 * total_ssb_power;
    res.integrated_phase_noise_rad = sqrt(phase_variance);
    res.integrated_phase_noise_deg = res.integrated_phase_noise_rad * (180.0 / PI);

    // Часовий джитер: sigma_t = sigma_phi / (2 * pi * f_carrier)
    res.rms_jitter_sec = res.integrated_phase_noise_rad / (2.0 * PI * carrier_freq_hz);

    // Граничний SNR АЦП, обумовлений виключно апертурним джитером такту
    if (adc_input_freq_hz > 0.0 && res.rms_jitter_sec > 0.0) {
        double snr_linear = 2.0 * PI * adc_input_freq_hz * res.rms_jitter_sec;
        res.adc_snr_limit_db = -20.0 * log10(snr_linear);
        res.adc_enob_limit = (res.adc_snr_limit_db - 1.76) / 6.02;
    }

    return res;
}

int main(void) {
    // Профіль фазового шуму високоякісного термостатованого кварцового генератора (OCXO 100 МГц)
    const PhaseNoisePoint ocxo_profile[] = {
        { 10.0,       -95.0 },
        { 100.0,     -125.0 },
        { 1000.0,    -148.0 },
        { 10000.0,   -160.0 },
        { 100000.0,  -165.0 },
        { 1000000.0, -168.0 },
        { 10000000.0,-170.0 }
    };
    size_t count = sizeof(ocxo_profile) / sizeof(ocxo_profile[0]);

    double f_carrier = 100.0e6; // Несуча частота 100 МГц
    double f_start   = 12.0e3;  // Нижня межа 12 кГц (стандартний зріз SONET/Ethernet)
    double f_stop    = 20.0e6;  // Верхня межа інтегрування 20 МГц
    double f_adc_in  = 50.0e6;  // Вхідна частота аналогового сигналу АЦП 50 МГц

    JitterResult res = calculate_phase_jitter(
        ocxo_profile, count, f_carrier, f_start, f_stop, f_adc_in
    );

    printf("================ РЕЗУЛЬТАТИ РОЗРАХУНКУ ДЖИТЕРУ ================\n");
    printf("Несуча частота генератора: %.1f МГц\n", f_carrier / 1e6);
    printf("Смуга інтегрування шуму:   %.1f кГц — %.1f МГц\n", f_start / 1e3, f_stop / 1e6);
    printf("Інтегральний фазовий шум:  %.4f мрад (%.5f градусів)\n", 
           res.integrated_phase_noise_rad * 1e3, res.integrated_phase_noise_deg);
    printf("Середньоквадратичний джитер: %.2f фс (%.5f пс)\n", 
           res.rms_jitter_sec * 1e15, res.rms_jitter_sec * 1e12);
    printf("---------------------------------------------------------------\n");
    printf("Вхідна частота сигналу АЦП: %.1f МГц\n", f_adc_in / 1e6);
    printf("Теоретична стеля SNR АЦП:   %.2f дБ\n", res.adc_snr_limit_db);
    printf("Максимальний ENOB АЦП:      %.2f біт\n", res.adc_enob_limit);
    printf("===============================================================\n");

    return 0;
}
