#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define BOLTZMANN_K 1.380649e-23
#define TEMP_KELVIN 298.15 // 25 °C

typedef struct {
    double gbp_hz;        // Добуток підсилення на смугу (Гц)
    double en_nv_rt_hz;   // Власний шум напруги (нВ/√Гц)
    double in_pa_rt_hz;   // Власний шум струму (пА/√Гц)
    double vos_uv;        // Вхідна напруга зміщення (мкВ)
    double min_stable_ng; // Мінімальне стабільне шумове підсилення (наприклад, 5.0 або 7.0)
} OpAmpParams;

typedef struct {
    double rin_ohm;       // Вхідний резистор (Ом)
    double rf_ohm;        // Резистор зворотного зв'язку (Ом)
    bool isInverting;     // true — інвертувальний, false — неінвертувальний
} CircuitParams;

typedef struct {
    double signal_gain;       // Підсилення корисного сигналу
    double noise_gain_dc;     // Шумове підсилення на постійному струмі
    double bandwidth_hz;      // Смуга замкненого контуру f_cl (Гц)
    double vos_out_uv;        // Вихідна напруга зміщення (мкВ)
    double en_out_nv_rt_hz;   // Вихідна густина шуму від напруги ОП (нВ/√Гц)
    double total_noise_density_nv_rt_hz; // Повна вихідна густина шуму (нВ/√Гц)
    double total_rms_noise_uv;            // Сумарний шум RMS у робочій смузі (мкВ)
    bool is_stable;           // Чи виконується умова NG >= min_stable_ng
    double r_dummy_ohm;       // Необхідний резистор шунта між входами (Ом)
    double c_dummy_f;         // Необхідний конденсатор шунта (Ф)
} AnalysisResult;

AnalysisResult analyze_circuit(const OpAmpParams *op, const CircuitParams *ckt) {
    AnalysisResult res;
    
    // 1. Розрахунок підсилення сигналу
    if (ckt->isInverting) {
        res.signal_gain = -ckt->rf_ohm / ckt->rin_ohm;
    } else {
        res.signal_gain = 1.0 + (ckt->rf_ohm / ckt->rin_ohm);
    }
    
    // Шумове підсилення завжди 1 + Rf/Rin для обох топологій
    res.noise_gain_dc = 1.0 + (ckt->rf_ohm / ckt->rin_ohm);
    
    // 2. Смуга пропускання замкненого контуру
    res.bandwidth_hz = op->gbp_hz / res.noise_gain_dc;
    
    // 3. Вихідна напруга зміщення
    res.vos_out_uv = op->vos_uv * res.noise_gain_dc;
    
    // 4. Спектральні густини шумів
    res.en_out_nv_rt_hz = op->en_nv_rt_hz * res.noise_gain_dc;
    
    // Тепловий шум Джонсона резисторів: e_th = sqrt(4 * k * T * R)
    double en_rf = sqrt(4.0 * BOLTZMANN_K * TEMP_KELVIN * ckt->rf_ohm) * 1e9; // нВ/√Гц
    double en_rin = sqrt(4.0 * BOLTZMANN_K * TEMP_KELVIN * ckt->rin_ohm) * 1e9;
    
    // Внесок шуму Rin на вихід: en_rin * (Rf / Rin)
    double en_rin_out = en_rin * (ckt->rf_ohm / ckt->rin_ohm);
    
    // Внесок шуму струму ОП: in * Rf
    double in_a = op->in_pa_rt_hz * 1e-12;
    double en_in_out = (in_a * ckt->rf_ohm) * 1e9; // нВ/√Гц
    
    // Сума квадратів незалежних джерел шуму
    double en_total_sq = (res.en_out_nv_rt_hz * res.en_out_nv_rt_hz) +
                         (en_rf * en_rf) +
                         (en_rin_out * en_rin_out) +
                         (en_in_out * en_in_out);
    res.total_noise_density_nv_rt_hz = sqrt(en_total_sq);
    
    // Еквівалентна шумова смуга (ENBW = pi/2 * f_cl)
    double noise_bw = 1.5707963 * res.bandwidth_hz;
    res.total_rms_noise_uv = (res.total_noise_density_nv_rt_hz * sqrt(noise_bw)) * 1e-3;
    
    // 5. Перевірка стійкості для декомпенсованого ОП
    if (res.noise_gain_dc >= op->min_stable_ng) {
        res.is_stable = true;
        res.r_dummy_ohm = 0.0;
        res.c_dummy_f = 0.0;
    } else {
        res.is_stable = false;
        // Потрібно: 1 + Rf / (Rin || R_dummy) = min_stable_ng
        double req_target = ckt->rf_ohm / (op->min_stable_ng - 1.0);
        
        // 1/R_dummy = 1/req_target - 1/Rin
        double g_dummy = (1.0 / req_target) - (1.0 / ckt->rin_ohm);
        if (g_dummy > 0.0) {
            res.r_dummy_ohm = 1.0 / g_dummy;
            // Нуль ланцюга корекції ставимо на рівні 1/10 від цільової частоти перетину
            double f_cross_target = op->gbp_hz / op->min_stable_ng;
            double f_zero = f_cross_target / 10.0;
            res.c_dummy_f = 1.0 / (2.0 * 3.14159265 * res.r_dummy_ohm * f_zero);
        } else {
            res.r_dummy_ohm = 0.0;
            res.c_dummy_f = 0.0;
        }
    }
    
    return res;
}

int main(void) {
    // Параметри ультрашвидкісного декомпенсованого ОП (наприклад, OPA847)
    OpAmpParams op = {
        .gbp_hz = 3.9e9,        // 3.9 ГГц GBP
        .en_nv_rt_hz = 0.85,    // 0.85 нВ/√Гц наднизький шум
        .in_pa_rt_hz = 2.5,     // 2.5 пА/√Гц
        .vos_uv = 100.0,        // 100 мкВ зміщення
        .min_stable_ng = 12.0   // Стійкий лише при NG >= 12 (+21.6 дБ)
    };
    
    // Потрібно реалізувати інвертувальний атенюатор G = -0.5
    CircuitParams ckt = {
        .rin_ohm = 1000.0,      // Rin = 1 кОм
        .rf_ohm = 500.0,        // Rf = 500 Ом
        .isInverting = true
    };
    
    AnalysisResult r = analyze_circuit(&op, &ckt);
    
    printf("===================================================\n");
    printf("   АНАЛІЗ ТА СИНТЕЗ КАСКАДУ НА ДЕКОМПЕНСОВАНОМУ ОП \n");
    printf("===================================================\n");
    printf("Підсилення сигналу G_сигн   : %.2f\n", r.signal_gain);
    printf("Шумове підсилення NG (DC)  : %.2f (потрібно >= %.1f)\n", r.noise_gain_dc, op.min_stable_ng);
    printf("Смуга пропускання f_cl     : %.2f МГц\n", r.bandwidth_hz / 1e6);
    printf("Вихідне зміщення Vos(out)  : %.2f мкВ\n", r.vos_out_uv);
    printf("Власний шум ОП на виході   : %.2f нВ/√Гц\n", r.en_out_nv_rt_hz);
    printf("Повна вихідна густина шуму : %.2f нВ/√Гц\n", r.total_noise_density_nv_rt_hz);
    printf("Інтегральний RMS шум виходу: %.2f мкВ\n", r.total_rms_noise_uv);
    printf("Стан без корекції          : %s\n", r.is_stable ? "СТІЙКИЙ" : "НЕСТІЙКИЙ (самозбудження!)");
    
    if (!r.is_stable) {
        printf("\n---------------------------------------------------\n");
        printf("   ПАРАМЕТРИ ЛАНЦЮГА СТАБІЛІЗАЦІЇ (R_dummy || C_dummy)\n");
        printf("---------------------------------------------------\n");
        printf("Шунтувальний резистор R_dummy : %.1f Ом\n", r.r_dummy_ohm);
        printf("Розділовий конденсатор C_dummy: %.2f пФ\n", r.c_dummy_f * 1e12);
        printf("Результат: на ВЧ шумове підсилення зростає до %.1f,\n", op.min_stable_ng);
        printf("коефіцієнт сигналу G = %.2f не змінюється, схема абсолютно стійка.\n", r.signal_gain);
    }
    printf("===================================================\n");
    
    return 0;
}
