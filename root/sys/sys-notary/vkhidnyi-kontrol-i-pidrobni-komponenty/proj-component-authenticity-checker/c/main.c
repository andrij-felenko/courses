#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAX_SAMPLES_PER_CURVE 256
#define MAX_PINS_PER_DEVICE   144
#define SIGNATURE_VOLTAGE_REF 5.0f   /* Вольт */
#define SIGNATURE_CURRENT_REF 0.010f /* 10 мА */

typedef enum {
    PIN_TYPE_UNKNOWN = 0,
    PIN_TYPE_IO_DIGITAL,
    PIN_TYPE_IO_ANALOG,
    PIN_TYPE_POWER_VDD,
    PIN_TYPE_POWER_GND,
    PIN_TYPE_RESET,
    PIN_TYPE_CLOCK
} PinElectricalType;

typedef enum {
    VERDICT_PASS = 0,
    VERDICT_SUSPECT_CLONE,
    VERDICT_SUSPECT_REMARK,
    VERDICT_DAMAGED_ESD,
    VERDICT_OPEN_CIRCUIT,
    VERDICT_SHORT_CIRCUIT
} InspectionVerdict;

typedef struct {
    float voltage[MAX_SAMPLES_PER_CURVE]; /* В */
    float current[MAX_SAMPLES_PER_CURVE]; /* А */
    uint16_t sample_count;
    float test_freq_hz;
    float source_resistor_ohm;
} CurveSignature;

typedef struct {
    float v_forward_v;   /* Пряме падіння при 1 мА */
    float r_dynamic_ohm; /* Диференційний опір */
    float i_leak_ua;     /* Зворотний витік при -4 В */
    float cap_pf;        /* Бар'єрна ємність */
} ExtractedJunctionParams;

typedef struct {
    uint16_t pin_number;
    char pin_name[16];
    PinElectricalType pin_type;
    CurveSignature signature;
    ExtractedJunctionParams params;
} PinGoldenProfile;

typedef struct {
    char device_part_number[32];
    char manufacturer[32];
    uint16_t total_pins;
    PinGoldenProfile pins[MAX_PINS_PER_DEVICE];
} DeviceGoldenDatabase;

typedef struct {
    uint16_t pin_number;
    float euclidean_discrepancy; /* 0.0 .. 1.0 */
    float dtw_distance;
    ExtractedJunctionParams uut_params;
    InspectionVerdict verdict;
    char defect_description[64];
} PinInspectionResult;

typedef struct {
    char uut_serial_lot[32];
    uint16_t total_tested_pins;
    uint16_t passed_pins;
    uint16_t failed_pins;
    float max_pin_discrepancy;
    InspectionVerdict overall_verdict;
    PinInspectionResult pin_results[MAX_PINS_PER_DEVICE];
} DeviceInspectionReport;

/* Цифрова фільтрація вибірок за алгоритмом Савіцького-Голея */
void filter_signature_savitzky_golay(CurveSignature* sig) {
    if (!sig || sig->sample_count < 5) return;

    float temp_v[MAX_SAMPLES_PER_CURVE];
    float temp_i[MAX_SAMPLES_PER_CURVE];

    /* Крайові точки копіюються без змін */
    temp_v[0] = sig->voltage[0];
    temp_v[1] = sig->voltage[1];
    temp_i[0] = sig->current[0];
    temp_i[1] = sig->current[1];
    temp_v[sig->sample_count - 2] = sig->voltage[sig->sample_count - 2];
    temp_v[sig->sample_count - 1] = sig->voltage[sig->sample_count - 1];
    temp_i[sig->sample_count - 2] = sig->current[sig->sample_count - 2];
    temp_i[sig->sample_count - 1] = sig->current[sig->sample_count - 1];

    /* Зважене вікно з 5 точок (поліном 2-го порядку: коєфіцієнти -3, 12, 17, 12, -3 / 35) */
    for (uint16_t k = 2; k < sig->sample_count - 2; ++k) {
        temp_v[k] = (-3.0f * sig->voltage[k - 2] + 12.0f * sig->voltage[k - 1] +
                      17.0f * sig->voltage[k] + 12.0f * sig->voltage[k + 1] -
                      3.0f * sig->voltage[k + 2]) / 35.0f;

        temp_i[k] = (-3.0f * sig->current[k - 2] + 12.0f * sig->current[k - 1] +
                      17.0f * sig->current[k] + 12.0f * sig->current[k + 1] -
                      3.0f * sig->current[k + 2]) / 35.0f;
    }

    memcpy(sig->voltage, temp_v, sizeof(float) * sig->sample_count);
    memcpy(sig->current, temp_i, sizeof(float) * sig->sample_count);
}

/* Екстракція параметрів напівпровідникового переходу */
ExtractedJunctionParams extract_junction_parameters(const CurveSignature* sig) {
    ExtractedJunctionParams p;
    memset(&p, 0, sizeof(p));
    if (!sig || sig->sample_count == 0) return p;

    float v_at_1ma = 0.0f;
    float min_diff = 1e9f;
    float target_i = 0.001f; /* 1 мА */

    for (uint16_t k = 0; k < sig->sample_count; ++k) {
        float diff = fabsf(sig->current[k] - target_i);
        if (diff < min_diff && sig->voltage[k] > 0.1f) {
            min_diff = diff;
            v_at_1ma = sig->voltage[k];
        }
    }
    p.v_forward_v = v_at_1ma;

    /* Розрахунок r_dynamic між 2 мА та 5 мА */
    float v1 = 0.0f, v2 = 0.0f, i1 = 0.002f, i2 = 0.005f;
    float d1 = 1e9f, d2 = 1e9f;
    for (uint16_t k = 0; k < sig->sample_count; ++k) {
        if (fabsf(sig->current[k] - i1) < d1) { d1 = fabsf(sig->current[k] - i1); v1 = sig->voltage[k]; }
        if (fabsf(sig->current[k] - i2) < d2) { d2 = fabsf(sig->current[k] - i2); v2 = sig->voltage[k]; }
    }
    if (fabsf(i2 - i1) > 1e-6f && fabsf(v2 - v1) > 1e-4f) {
        p.r_dynamic_ohm = (v2 - v1) / (i2 - i1);
    } else {
        p.r_dynamic_ohm = 15.0f; /* Типове значення */
    }

    /* Зворотний витік при V = -4.0 В */
    float leak_i = 0.0f;
    float d_rev = 1e9f;
    for (uint16_t k = 0; k < sig->sample_count; ++k) {
        if (fabsf(sig->voltage[k] - (-4.0f)) < d_rev) {
            d_rev = fabsf(sig->voltage[k] - (-4.0f));
            leak_i = fabsf(sig->current[k]);
        }
    }
    p.i_leak_ua = leak_i * 1e6f;

    /* Оцінка ємності через інтеграл площі петлі методом трапецій */
    float loop_area = 0.0f;
    for (uint16_t k = 0; k < sig->sample_count - 1; ++k) {
        float dv = sig->voltage[k + 1] - sig->voltage[k];
        float avg_i = (sig->current[k] + sig->current[k + 1]) * 0.5f;
        loop_area += avg_i * dv;
    }
    loop_area = fabsf(loop_area);
    float omega = 2.0f * 3.14159265f * (sig->test_freq_hz > 1.0f ? sig->test_freq_hz : 100.0f);
    float v_pk_sq = SIGNATURE_VOLTAGE_REF * SIGNATURE_VOLTAGE_REF;
    p.cap_pf = (loop_area / (3.14159265f * omega * v_pk_sq)) * 1e12f;

    return p;
}

/* Розрахунок нормованого евклідового відхилення сигнатур */
float compute_euclidean_discrepancy(const CurveSignature* gold, const CurveSignature* uut) {
    if (!gold || !uut || gold->sample_count == 0 || uut->sample_count == 0) return 1.0f;

    uint16_t n = gold->sample_count < uut->sample_count ? gold->sample_count : uut->sample_count;
    float sum_sq = 0.0f;

    for (uint16_t k = 0; k < n; ++k) {
        float dv = (uut->voltage[k] - gold->voltage[k]) / SIGNATURE_VOLTAGE_REF;
        float di = (uut->current[k] - gold->current[k]) / SIGNATURE_CURRENT_REF;
        sum_sq += (dv * dv + di * di);
    }

    return sqrtf(sum_sq / (float)n);
}

/* Розрахунок відстані динамічного вирівнювання часової шкали (DTW) */
float compute_dtw_distance(const CurveSignature* gold, const CurveSignature* uut) {
    if (!gold || !uut) return 1.0f;
    uint16_t n = gold->sample_count;
    uint16_t m = uut->sample_count;
    if (n > 64) n = 64; /* Обмеження сітки для швидкодії */
    if (m > 64) m = 64;

    float dtw_matrix[64][64];

    for (uint16_t i = 0; i < n; ++i) {
        for (uint16_t j = 0; j < m; ++j) {
            float dv = (uut->voltage[j] - gold->voltage[i]) / SIGNATURE_VOLTAGE_REF;
            float di = (uut->current[j] - gold->current[i]) / SIGNATURE_CURRENT_REF;
            float cost = sqrtf(dv * dv + di * di);

            if (i == 0 && j == 0) {
                dtw_matrix[i][j] = cost;
            } else if (i == 0) {
                dtw_matrix[i][j] = cost + dtw_matrix[i][j - 1];
            } else if (j == 0) {
                dtw_matrix[i][j] = cost + dtw_matrix[i - 1][j];
            } else {
                float min_prev = dtw_matrix[i - 1][j];
                if (dtw_matrix[i][j - 1] < min_prev) min_prev = dtw_matrix[i][j - 1];
                if (dtw_matrix[i - 1][j - 1] < min_prev) min_prev = dtw_matrix[i - 1][j - 1];
                dtw_matrix[i][j] = cost + min_prev;
            }
        }
    }
    return dtw_matrix[n - 1][m - 1] / (float)(n + m);
}

/* Аналіз одного виводу та формування вердикту */
PinInspectionResult inspect_pin(const PinGoldenProfile* gold, const CurveSignature* uut_sig) {
    PinInspectionResult res;
    memset(&res, 0, sizeof(res));
    res.pin_number = gold->pin_number;

    CurveSignature filtered_uut = *uut_sig;
    filter_signature_savitzky_golay(&filtered_uut);

    res.uut_params = extract_junction_parameters(&filtered_uut);
    res.euclidean_discrepancy = compute_euclidean_discrepancy(&gold->signature, &filtered_uut);
    res.dtw_distance = compute_dtw_distance(&gold->signature, &filtered_uut);

    /* Детекція типу дефекту */
    if (res.uut_params.v_forward_v < 0.1f && res.uut_params.r_dynamic_ohm < 2.0f) {
        res.verdict = VERDICT_SHORT_CIRCUIT;
        snprintf(res.defect_description, sizeof(res.defect_description), "Коротке замикання на землю (R < 2 Ом)");
    } else if (res.uut_params.v_forward_v > 4.5f) {
        res.verdict = VERDICT_OPEN_CIRCUIT;
        snprintf(res.defect_description, sizeof(res.defect_description), "Обрив виводу (відсутній ESD діод)");
    } else if (res.uut_params.i_leak_ua > 50.0f) {
        res.verdict = VERDICT_SUSPECT_REMARK;
        snprintf(res.defect_description, sizeof(res.defect_description), "Аномальний витік (I_leak = %.1f uA > 50 uA)", res.uut_params.i_leak_ua);
    } else if (res.euclidean_discrepancy > 0.08f || res.dtw_distance > 0.06f) {
        res.verdict = VERDICT_SUSPECT_CLONE;
        snprintf(res.defect_description, sizeof(res.defect_description), "Кристал-клон: відхилення сигнатури %.1f%%", res.euclidean_discrepancy * 100.0f);
    } else {
        res.verdict = VERDICT_PASS;
        snprintf(res.defect_description, sizeof(res.defect_description), "Автентичний (Δ = %.2f%%)", res.euclidean_discrepancy * 100.0f);
    }

    return res;
}

/* Повна перевірка ІС за еталонною базою */
DeviceInspectionReport run_full_component_inspection(
    const DeviceGoldenDatabase* db,
    const char* lot_number,
    const CurveSignature uut_signatures[MAX_PINS_PER_DEVICE]
) {
    DeviceInspectionReport rep;
    memset(&rep, 0, sizeof(rep));
    snprintf(rep.uut_serial_lot, sizeof(rep.uut_serial_lot), "%s", lot_number);
    rep.total_tested_pins = db->total_pins;
    rep.overall_verdict = VERDICT_PASS;

    for (uint16_t i = 0; i < db->total_pins; ++i) {
        rep.pin_results[i] = inspect_pin(&db->pins[i], &uut_signatures[i]);
        if (rep.pin_results[i].euclidean_discrepancy > rep.max_pin_discrepancy) {
            rep.max_pin_discrepancy = rep.pin_results[i].euclidean_discrepancy;
        }
        if (rep.pin_results[i].verdict == VERDICT_PASS) {
            rep.passed_pins++;
        } else {
            rep.failed_pins++;
            if (rep.overall_verdict == VERDICT_PASS) {
                rep.overall_verdict = rep.pin_results[i].verdict;
            }
        }
    }
    return rep;
}

/* Друк інженерного звіту верифікації */
void print_inspection_report(const DeviceInspectionReport* rep, const DeviceGoldenDatabase* db) {
    printf("====================================================================\n");
    printf(" ЗВІТ ВХІДНОГО СИГНАТУРНОГО КОНТРОЛЮ АВТЕНТИЧНОСТІ КОМПОНЕНТА      \n");
    printf("====================================================================\n");
    printf(" Компонент:       %s (%s)\n", db->device_part_number, db->manufacturer);
    printf(" Партія / Лот:    %s\n", rep->uut_serial_lot);
    printf(" Перевірено пінів: %u (Успішно: %u, Дефектних: %u)\n", 
           rep->total_tested_pins, rep->passed_pins, rep->failed_pins);
    printf(" Макс. відхилення: %.2f%%\n", rep->max_pin_discrepancy * 100.0f);
    printf(" ПІДСУМКОВИЙ ВЕРДИКТ: %s\n", 
           rep->overall_verdict == VERDICT_PASS ? "[✓ ПРИДАТНО / ОРИГІНАЛ]" : "[✗ КОНТРАФАКТ / КАРАНТИН]");
    printf("--------------------------------------------------------------------\n");
    printf(" Пін | Назва   | V_F (В) | r_d (Ом) | I_leak (uA) | C_j (пФ) | Статус\n");
    printf("-----+---------+---------+----------+-------------+----------+------\n");

    for (uint16_t i = 0; i < rep->total_tested_pins; ++i) {
        const PinInspectionResult* r = &rep->pin_results[i];
        printf(" %3u | %-7s |  %5.3f  |  %6.1f  |   %7.2f   |  %5.1f   | %s\n",
               r->pin_number, db->pins[i].pin_name,
               r->uut_params.v_forward_v, r->uut_params.r_dynamic_ohm,
               r->uut_params.i_leak_ua, r->uut_params.cap_pf,
               r->defect_description);
    }
    printf("====================================================================\n");
}

/* Генерація тестової сигнатури для переходу База-Емітер BJT */
CurveSignature generate_bjt_be_signature(float v_be_on, float r_bulk, float i_sat, bool is_damaged_leak) {
    CurveSignature sig;
    memset(&sig, 0, sizeof(sig));
    sig.sample_count = 128;
    sig.test_freq_hz = 100.0f;
    sig.source_resistor_ohm = 1000.0f;

    for (uint16_t k = 0; k < sig.sample_count; ++k) {
        float phase = (2.0f * 3.14159265f * (float)k) / (float)sig.sample_count;
        float v_gen = SIGNATURE_VOLTAGE_REF * sinf(phase);
        float v_dut = 0.0f;
        float i_dut = 0.0f;

        if (v_gen > v_be_on) {
            float v_diff = v_gen - v_be_on;
            v_dut = v_be_on + v_diff * (r_bulk / (r_bulk + sig.source_resistor_ohm));
            i_dut = (v_gen - v_dut) / sig.source_resistor_ohm;
        } else if (v_gen < -6.0f) {
            v_dut = -6.0f;
            i_dut = (v_gen - v_dut) / sig.source_resistor_ohm;
        } else {
            float leak = is_damaged_leak ? (v_gen / 80000.0f) : (v_gen < 0.0f ? -i_sat : 0.0f);
            i_dut = leak;
            v_dut = v_gen - i_dut * sig.source_resistor_ohm;
        }
        sig.voltage[k] = v_dut;
        sig.current[k] = i_dut;
    }
    return sig;
}

/* Генерація сигнатури для виводів Gate-Source силового MOSFET */
CurveSignature generate_mosfet_gs_signature(float cap_nF, float r_leak_ohm) {
    CurveSignature sig;
    memset(&sig, 0, sizeof(sig));
    sig.sample_count = 128;
    sig.test_freq_hz = 1000.0f;
    sig.source_resistor_ohm = 10000.0f;

    float omega = 2.0f * 3.14159265f * sig.test_freq_hz;
    float cap_f = cap_nF * 1e-9f;

    for (uint16_t k = 0; k < sig.sample_count; ++k) {
        float phase = (2.0f * 3.14159265f * (float)k) / (float)sig.sample_count;
        float v_gen = SIGNATURE_VOLTAGE_REF * sinf(phase);

        float i_cap = v_gen * omega * cap_f * cosf(phase);
        float i_res = v_gen / r_leak_ohm;
        float i_total = i_cap + i_res;
        float v_dut = v_gen - i_total * sig.source_resistor_ohm;

        sig.voltage[k] = v_dut;
        sig.current[k] = i_total;
    }
    return sig;
}

/* Генерація сигнатури для діода Шотткі */
CurveSignature generate_schottky_signature(float v_f_knee, float r_series, float i_rev_leak) {
    CurveSignature sig;
    memset(&sig, 0, sizeof(sig));
    sig.sample_count = 128;
    sig.test_freq_hz = 100.0f;
    sig.source_resistor_ohm = 1000.0f;

    for (uint16_t k = 0; k < sig.sample_count; ++k) {
        float phase = (2.0f * 3.14159265f * (float)k) / (float)sig.sample_count;
        float v_gen = SIGNATURE_VOLTAGE_REF * sinf(phase);
        float v_dut = 0.0f;
        float i_dut = 0.0f;

        if (v_gen > v_f_knee) {
            float v_diff = v_gen - v_f_knee;
            v_dut = v_f_knee + v_diff * (r_series / (r_series + sig.source_resistor_ohm));
            i_dut = (v_gen - v_dut) / sig.source_resistor_ohm;
        } else {
            i_dut = (v_gen < 0.0f) ? (-i_rev_leak * fabsf(v_gen) / SIGNATURE_VOLTAGE_REF) : 0.0f;
            v_dut = v_gen - i_dut * sig.source_resistor_ohm;
        }
        sig.voltage[k] = v_dut;
        sig.current[k] = i_dut;
    }
    return sig;
}

/* Демонстраційний запуск розширеного тестування дискретних компонентів */
void run_extended_discrete_inspection_demo(void) {
    printf("\n=== ТЕСТУВАННЯ ДИСКРЕТНИХ КОМПОНЕНТІВ (BJT, MOSFET, SCHOTTKY) ===\n");

    /* 1. Біполярний транзистор 2N3904 (B-E) */
    CurveSignature bjt_gold = generate_bjt_be_signature(0.68f, 12.0f, 1e-8f, false);
    CurveSignature bjt_damaged = generate_bjt_be_signature(0.68f, 12.0f, 1e-8f, true);
    PinGoldenProfile prof_bjt;
    memset(&prof_bjt, 0, sizeof(prof_bjt));
    prof_bjt.pin_number = 1;
    snprintf(prof_bjt.pin_name, sizeof(prof_bjt.pin_name), "B-E");
    prof_bjt.signature = bjt_gold;
    PinInspectionResult res_bjt = inspect_pin(&prof_bjt, &bjt_damaged);
    printf(" [BJT 2N3904] Вердикт: %s (Витік: %.1f uA)\n",
           res_bjt.verdict == VERDICT_PASS ? "PASS" : "FAIL / LEAKAGE", res_bjt.uut_params.i_leak_ua);

    /* 2. Силовий MOSFET IRFP460 (Gate-Source) */
    CurveSignature mos_gold = generate_mosfet_gs_signature(4.2f, 1e8f);
    CurveSignature mos_recycled = generate_mosfet_gs_signature(4.2f, 8e4f); /* Витік через пошкоджений затвор */
    PinGoldenProfile prof_mos;
    memset(&prof_mos, 0, sizeof(prof_mos));
    prof_mos.pin_number = 2;
    snprintf(prof_mos.pin_name, sizeof(prof_mos.pin_name), "G-S");
    prof_mos.signature = mos_gold;
    PinInspectionResult res_mos = inspect_pin(&prof_mos, &mos_recycled);
    printf(" [MOSFET IRFP460] Вердикт: %s (%s)\n",
           res_mos.verdict == VERDICT_PASS ? "PASS" : "FAIL / GATE BREAKDOWN", res_mos.defect_description);

    /* 3. Діод Шотткі 1N5819 */
    CurveSignature sch_gold = generate_schottky_signature(0.28f, 8.0f, 2e-5f);
    CurveSignature sch_clone = generate_schottky_signature(0.55f, 22.0f, 1e-6f); /* Звичайний Si діод замість Шотткі */
    PinGoldenProfile prof_sch;
    memset(&prof_sch, 0, sizeof(prof_sch));
    prof_sch.pin_number = 3;
    snprintf(prof_sch.pin_name, sizeof(prof_sch.pin_name), "Anode");
    prof_sch.signature = sch_gold;
    PinInspectionResult res_sch = inspect_pin(&prof_sch, &sch_clone);
    printf(" [Schottky 1N5819] Вердикт: %s (V_F = %.3f В)\n",
           res_sch.verdict == VERDICT_PASS ? "PASS" : "FAIL / WRONG JUNCTION", res_sch.uut_params.v_forward_v);
}
