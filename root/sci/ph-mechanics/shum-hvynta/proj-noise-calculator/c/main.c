#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define P_REF 20e-6        /* Опорний акустичний тиск: 20 мкПа */
#define RHO_AIR 1.225      /* Густина повітря на рівні моря, кг/м³ */
#define C_SOUND 343.0      /* Швидкість звуку в повітрі (20 °C), м/с */
#define MAX_HARMONICS 6

typedef struct {
    double diameter_m;     /* Діаметр гвинта, м */
    int num_blades;        /* Кількість лопатей B */
    double rpm;            /* Оберти за хвилину */
    double thrust_n;       /* Сила тяги T, Н */
    double power_w;        /* Споживана потужність P, Вт */
    double chord_m;        /* Середня аеродинамічна хорда лопаті, м */
    double thickness_m;    /* Максимальна товщина профілю лопаті, м */
    double distance_m;     /* Відстань до спостерігача r0, м */
    double angle_deg;      /* Кут спрямованості theta від осі тяги, градуси */
} PropellerParams;

typedef struct {
    double bpf_hz;
    double m_tip;
    double u_tip_mps;
    double harmonic_freq[MAX_HARMONICS];
    double harmonic_spl_db[MAX_HARMONICS];
    double harmonic_spl_dba[MAX_HARMONICS];
    double broadband_peak_freq;
    double broadband_spl_db;
    double total_spl_db;
    double total_spl_dba;
} AcousticResult;

/* Обчислення функції Бесселя першого роду J_n(x) степеневим рядом */
static double bessel_jn_series(int n, double x) {
    if (n < 0) {
        return (n % 2 == 0) ? bessel_jn_series(-n, x) : -bessel_jn_series(-n, x);
    }
    if (x == 0.0) {
        return (n == 0) ? 1.0 : 0.0;
    }
    
    double half_x = 0.5 * x;
    double term = 1.0;
    for (int i = 1; i <= n; ++i) {
        term *= (half_x / (double)i);
    }
    
    double sum = term;
    double half_x_sq = half_x * half_x;
    for (int k = 1; k < 60; ++k) {
        term *= -half_x_sq / ((double)k * (double)(n + k));
        sum += term;
        if (fabs(term) < 1e-15 * fabs(sum)) {
            break;
        }
    }
    return sum;
}

/* Коригувальна вага фільтра A-зважування за стандартом IEC 61672-1 */
static double a_weighting_delta(double freq_hz) {
    if (freq_hz < 10.0) return -70.0;
    double f2 = freq_hz * freq_hz;
    double num = 12194.0 * 12194.0 * f2 * f2;
    double den = (f2 + 20.6 * 20.6) * 
                 sqrt((f2 + 107.7 * 107.7) * (f2 + 737.9 * 737.9)) * 
                 (f2 + 12194.0 * 12194.0);
    double ra = num / den;
    return 20.0 * log10(ra) + 2.0;
}

/* Розрахунок акустичного випромінювання гвинта */
void calculate_propeller_noise(const PropellerParams *p, AcousticResult *res) {
    double radius = 0.5 * p->diameter_m;
    double r_eff = 0.80 * radius;
    double n_rps = p->rpm / 60.0;
    double omega = 2.0 * M_PI * n_rps;
    
    res->bpf_hz = (double)p->num_blades * n_rps;
    res->u_tip_mps = omega * radius;
    res->m_tip = res->u_tip_mps / C_SOUND;
    
    double theta_rad = p->angle_deg * M_PI / 180.0;
    double sin_theta = sin(theta_rad);
    double cos_theta = cos(theta_rad);
    
    double torque = (omega > 0.0) ? (p->power_w / omega) : 0.0;
    double blade_volume = p->chord_m * p->thickness_m * radius * 0.68;
    
    double m_eff = 0.80 * res->m_tip;
    double sum_p_sq = 0.0;
    double sum_p_sq_a = 0.0;
    
    for (int m = 1; m <= MAX_HARMONICS; ++m) {
        int order = m * p->num_blades;
        double freq = (double)m * res->bpf_hz;
        res->harmonic_freq[m - 1] = freq;
        
        double arg_bessel = (double)order * m_eff * sin_theta;
        double j_val = bessel_jn_series(order, arg_bessel);
        
        /* 1. Шум навантаження (диполь Гутіна) */
        double gutin_bracket = -p->thrust_n * cos_theta + 
                               (C_SOUND * torque) / (omega * r_eff * r_eff);
        double p_load = ((double)order * omega / (2.0 * sqrt(2.0) * M_PI * C_SOUND * p->distance_m)) *
                        gutin_bracket * j_val;
        
        /* 2. Шум товщини (монополь Демінга) */
        double p_thick = -(RHO_AIR * pow((double)order * omega, 2) / 
                          (2.0 * sqrt(2.0) * M_PI * p->distance_m)) *
                         blade_volume * j_val;
        
        /* Повний RMS акустичний тиск гармоніки */
        double p_total = sqrt(p_load * p_load + p_thick * p_thick);
        if (p_total < 1e-12) p_total = 1e-12;
        
        double spl_db = 20.0 * log10(p_total / P_REF);
        double a_weight = a_weighting_delta(freq);
        double spl_dba = spl_db + a_weight;
        
        res->harmonic_spl_db[m - 1] = spl_db;
        res->harmonic_spl_dba[m - 1] = spl_dba;
        
        sum_p_sq += pow(10.0, spl_db / 10.0);
        sum_p_sq_a += pow(10.0, spl_dba / 10.0);
    }
    
    /* 3. Широкосмуговий шум задньої кромки (апроксимація моделі BPM) */
    double u_eff = 0.75 * res->u_tip_mps;
    double delta_star = 0.003 * p->chord_m;
    res->broadband_peak_freq = 0.10 * u_eff / delta_star;
    
    double p_bb = 1.2e-5 * (RHO_AIR * pow(u_eff, 2.5) * sqrt(delta_star * radius) / 
                           (C_SOUND * p->distance_m));
    if (p_bb < 1e-12) p_bb = 1e-12;
    res->broadband_spl_db = 20.0 * log10(p_bb / P_REF);
    
    sum_p_sq += pow(10.0, res->broadband_spl_db / 10.0);
    double bb_dba = res->broadband_spl_db + a_weighting_delta(res->broadband_peak_freq);
    sum_p_sq_a += pow(10.0, bb_dba / 10.0);
    
    res->total_spl_db = 10.0 * log10(sum_p_sq);
    res->total_spl_dba = 10.0 * log10(sum_p_sq_a);
}

int main(void) {
    PropellerParams drone_prop = {
        .diameter_m = 0.254,      /* 10 дюймів */
        .num_blades = 2,
        .rpm = 6000.0,
        .thrust_n = 7.5,          /* 7.5 Н тяги (висіння 1.5 кг квадрокоптера) */
        .power_w = 85.0,
        .chord_m = 0.022,
        .thickness_m = 0.0025,
        .distance_m = 10.0,       /* 10 метрів */
        .angle_deg = 110.0        /* Кут максимального випромінювання */
    };
    
    AcousticResult result;
    calculate_propeller_noise(&drone_prop, &result);
    
    printf("=== Аероакустичний розрахунок гвинта дрона ===\n");
    printf("Діаметр: %.1f мм | Лопатей: %d | Оберти: %.0f RPM\n", 
           drone_prop.diameter_m * 1000.0, drone_prop.num_blades, drone_prop.rpm);
    printf("Швидкість кінчиків: %.1f м/с (M_tip = %.3f)\n", 
           result.u_tip_mps, result.m_tip);
    printf("Лопатева частота (BPF): %.1f Гц\n\n", result.bpf_hz);
    
    printf("Тональний спектр (формула Гутіна + шум товщини):\n");
    for (int i = 0; i < MAX_HARMONICS; ++i) {
        printf("  Гармоніка %d (%6.1f Гц): %5.1f дБ | %5.1f дБА\n", 
               i + 1, result.harmonic_freq[i], 
               result.harmonic_spl_db[i], result.harmonic_spl_dba[i]);
    }
    
    printf("\nШирокосмуговий шум (вихід з задньої кромки BPM):\n");
    printf("  Пікова частота: %.0f Гц | Рівень: %.1f дБ\n", 
           result.broadband_peak_freq, result.broadband_spl_db);
           
    printf("\nПідсумковий рівень шуму на відстані %.1f м:\n", drone_prop.distance_m);
    printf("  Сумарний SPL:  %.1f дБ (лінійний)\n", result.total_spl_db);
    printf("  Сумарний SPL:  %.1f дБА (A-зважений)\n", result.total_spl_dba);
    
    return 0;
}
