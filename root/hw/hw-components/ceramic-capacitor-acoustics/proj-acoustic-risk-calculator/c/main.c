#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Константи фізичних середовищ
#define AIR_DENSITY       1.204f     // кг/м3 (повітря @ 20°C)
#define AIR_SPEED_SOUND   343.0f     // м/с
#define FR4_DENSITY       1850.0f    // кг/м3
#define FR4_YOUNG_MODULUS 22.0e9f    // Па (22 ГПа)
#define FR4_POISSON_RATIO 0.14f
#define P_REF_ACOUSTIC    20.0e-6f   // 20 мкПа (поріг чутності)

// Параметри кераміки X7R BaTiO3
#define X7R_D33_ZERO      200.0e-12f // м/В
#define X7R_M33_ELECTRO   2.0e-16f   // м2/В2
#define X7R_POISSON_RATIO 0.30f
#define X7R_YOUNG_MODULUS 110.0e9f   // Па

typedef struct {
    float length_m;        // Довжина корпусу (наприклад, 0.0032 м для 1206)
    float width_m;         // Ширина корпусу (наприклад, 0.0016 м)
    float height_m;        // Висота корпусу (наприклад, 0.0016 м)
    float layer_thick_m;   // Товщина одного шару діелектрика (типово 2.0e-6 м)
    float v_dc;            // Постійна напруга зміщення, В
    float v_ripple_pk;     // Амплітуда змінної напруги пульсацій (пікова), В
    float f_ripple_hz;     // Частота пульсацій, Гц
} MLCC_Params;

typedef struct {
    float length_m;        // Довжина плати, м
    float width_m;         // Ширина плати, м
    float thickness_m;     // Товщина текстоліту (типово 0.0016 м)
    float q_factor;        // Механічна добротність резонансу FR4 (типово 25.0)
    float dist_m;          // Відстань до слухача (типово 0.5 м)
} PCB_Params;

typedef struct {
    float d_eff;           // Ефективний п'єзомодуль, пм/В
    float delta_l_nm;      // Динамічне видовження корпусу, нм
    float f_closest_mode;  // Найближча резонансна частота плати, Гц
    float q_amplification; // Фактор підсилення на резонансі
    float spl_db;          // Рівень звукового тиску, дБ
    float spl_dba;         // Рівень звукового тиску з A-зважуванням, дБА
    const char* risk_level;// Категорія ризику
} Acoustic_Result;

// A-зважування кривої чутливості слуху (МЕК 61672-1)
static float a_weighting_delta(float f_hz) {
    if (f_hz < 10.0f) f_hz = 10.0f;
    float f2 = f_hz * f_hz;
    float num = 12194.0f * 12194.0f * f2 * f2;
    float den = (f2 + 20.6f * 20.6f) *
                sqrtf((f2 + 107.7f * 107.7f) * (f2 + 737.9f * 737.9f)) *
                (f2 + 12194.0f * 12194.0f);
    if (den <= 0.0f) return 0.0f;
    float ra = num / den;
    return 20.0f * log10f(ra) + 2.0f;
}

Acoustic_Result calculate_mlcc_acoustics(const MLCC_Params* cap, const PCB_Params* pcb) {
    Acoustic_Result res;

    // 1. Електромеханічний розрахунок кераміки
    float e_dc = cap->v_dc / cap->layer_thick_m;
    float e_ac = cap->v_ripple_pk / cap->layer_thick_m;
    float d_eff = X7R_D33_ZERO + 2.0f * X7R_M33_ELECTRO * e_dc;
    res.d_eff = d_eff * 1.0e12f; // у пм/В

    // Поперечна деформація (стискання по X)
    float strain_x = X7R_POISSON_RATIO * d_eff * e_ac;
    float delta_l = strain_x * cap->length_m;
    res.delta_l_nm = delta_l * 1.0e9f; // у нм

    // 2. Механічні параметри плати FR4
    float t3 = pcb->thickness_m * pcb->thickness_m * pcb->thickness_m;
    float d_rigidity = (FR4_YOUNG_MODULUS * t3) /
                       (12.0f * (1.0f - FR4_POISSON_RATIO * FR4_POISSON_RATIO));
    float m_surface = FR4_DENSITY * pcb->thickness_m;
    float c_plate = sqrtf(d_rigidity / m_surface);

    // Пошук найближчої резонансної моди f_(m,n)
    float min_diff = 1.0e9f;
    float closest_mode = 0.0f;

    for (int m = 1; m <= 6; ++m) {
        for (int n = 1; n <= 6; ++n) {
            float term_m = (float)m / pcb->length_m;
            float term_n = (float)n / pcb->width_m;
            float f_mn = (M_PI / 2.0f) * c_plate * (term_m * term_m + term_n * term_n);
            float diff = fabsf(f_mn - cap->f_ripple_hz);
            if (diff < min_diff) {
                min_diff = diff;
                closest_mode = f_mn;
            }
        }
    }
    res.f_closest_mode = closest_mode;

    // Резонансне підсилення амплітуди
    float f_ratio = cap->f_ripple_hz / closest_mode;
    float q = pcb->q_factor;
    float denom = sqrtf(powf(1.0f - f_ratio * f_ratio, 2.0f) + powf(f_ratio / q, 2.0f));
    float q_amp = (denom > 0.001f) ? (1.0f / denom) : q;
    if (q_amp > q) q_amp = q;
    res.q_amplification = q_amp;

    // 3. Динамічний прогин та швидкість коливань поверхні плати
    float static_w0 = delta_l * (pcb->thickness_m / (2.0f * cap->length_m));
    float w_pk = static_w0 * q_amp;
    float omega = 2.0f * M_PI * cap->f_ripple_hz;
    float v_rms = (omega * w_pk) / sqrtf(2.0f);

    // 4. Акустичне випромінювання
    float f_crit = (AIR_SPEED_SOUND * AIR_SPEED_SOUND / (2.0f * M_PI)) *
                   sqrtf(m_surface / d_rigidity);
    float sigma_rad = (cap->f_ripple_hz < f_crit) ?
                      (0.20f * (cap->f_ripple_hz / f_crit)) : 1.0f;
    if (sigma_rad < 0.02f) sigma_rad = 0.02f;

    float pcb_area = pcb->length_m * pcb->width_m;
    float z_air = AIR_DENSITY * AIR_SPEED_SOUND;
    float w_acoustic = sigma_rad * z_air * pcb_area * (v_rms * v_rms);

    // Звуковий тиск у вільному півпросторі (Q_dir = 2)
    float intensity = (w_acoustic * 2.0f) / (4.0f * M_PI * pcb->dist_m * pcb->dist_m);
    float p_rms = sqrtf(intensity * z_air);

    if (p_rms < 1.0e-9f) p_rms = 1.0e-9f;
    res.spl_db = 20.0f * log10f(p_rms / P_REF_ACOUSTIC);
    res.spl_dba = res.spl_db + a_weighting_delta(cap->f_ripple_hz);

    // Оцінка рівня ризику
    if (res.spl_dba < 25.0f) {
        res.risk_level = "НЕЧУТНО (Безпечно)";
    } else if (res.spl_dba < 38.0f) {
        res.risk_level = "ПОМІРНИЙ (Чутно в тихій кімнаті)";
    } else if (res.spl_dba < 52.0f) {
        res.risk_level = "ВИСОКИЙ (Дратівливий тональний писк)";
    } else {
        res.risk_level = "КРИТИЧНИЙ (Нестерпний гучний свист)";
    }

    return res;
}

int main(void) {
    MLCC_Params cap = {
        .length_m = 0.0032f,       // 1206 (3.2 мм)
        .width_m = 0.0016f,
        .height_m = 0.0016f,
        .layer_thick_m = 2.0e-6f,  // 2.0 мкм
        .v_dc = 12.0f,             // 12 В зміщення
        .v_ripple_pk = 1.0f,       // 1.0 В пікових пульсацій
        .f_ripple_hz = 3450.0f     // 3.45 кГц (частота пакетів PFM)
    };

    PCB_Params pcb = {
        .length_m = 0.12f,         // 120 мм
        .width_m = 0.08f,          // 80 мм
        .thickness_m = 0.0016f,    // 1.6 мм FR4
        .q_factor = 25.0f,
        .dist_m = 0.5f             // 50 см
    };

    Acoustic_Result res = calculate_mlcc_acoustics(&cap, &pcb);

    printf("=====================================================\n");
    printf("   АНАЛІЗ АКУСТИЧНОГО ШУМУ КЕРАМІЧНОГО КОНДЕНСАТОРА   \n");
    printf("=====================================================\n");
    printf("Ефективний п'єзомодуль d_eff : %.1f пм/В\n", res.d_eff);
    printf("Амплітуда коливань корпусу dL: %.2f нм\n", res.delta_l_nm);
    printf("Найближча резонансна мода PCB: %.1f Гц\n", res.f_closest_mode);
    printf("Фактор підсилення резонансу Q: %.2f x\n", res.q_amplification);
    printf("Рівень звукового тиску SPL   : %.1f дБ (лінійний)\n", res.spl_db);
    printf("Рівень звукового тиску dBA   : %.1f дБА (A-зважений)\n", res.spl_dba);
    printf("Категорія акустичного ризику : %s\n", res.risk_level);
    printf("=====================================================\n");

    return 0;
}
