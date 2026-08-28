/* ========================================================================= */
/* fai_validator.c - Мова C (C99)                                            */
/* Промисловий валідатор звітів першої виробничої партії (AS9102 Form 3)    */
/* ========================================================================= */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define FAI_MAX_SAMPLES 128
#define FAI_MAX_PARAMS  32
#define FAI_STR_LEN     64

typedef enum {
    PARAM_TYPE_ANALOG_TWO_SIDED,  /* Двосторонній допуск: LSL <= x <= USL */
    PARAM_TYPE_UPPER_BOUND_ONLY,   /* Односторонній верхній: x <= USL */
    PARAM_TYPE_DIGITAL_HASH        /* Побітовий збіг SHA-256 хешу */
} fai_param_type_t;

typedef enum {
    STATUS_PASS,                  /* Повний успіх: усі зразки в нормі, Cpk >= 1.33 */
    STATUS_WARNING_LOW_CPK,       /* Усі зразки в нормі, але Cpk < 1.33 (ризик браку в серії) */
    STATUS_FAIL_OUT_OF_SPEC,      /* Фізичний вихід хоча б одного зразка за межі допуску */
    STATUS_FAIL_HASH_MISMATCH     /* Невідповідність цифрового хешу еталону Golden Sample */
} fai_status_t;

typedef struct {
    char name[FAI_STR_LEN];
    char unit[16];
    fai_param_type_t type;
    double golden_nominal;
    double lsl;
    double usl;
    char golden_hash[65];
} fai_spec_item_t;

typedef struct {
    char board_serial[FAI_STR_LEN];
    double analog_values[FAI_MAX_PARAMS];
    char hash_values[FAI_MAX_PARAMS][65];
} fai_board_record_t;

typedef struct {
    double mean;
    double std_dev;
    double cp;
    double cpu;
    double cpl;
    double cpk;
    double golden_drift;
    size_t out_of_spec_count;
    size_t outlier_count;
    fai_status_t status;
} fai_param_analysis_t;

typedef struct {
    size_t total_boards;
    size_t total_params;
    size_t passed_params;
    size_t warning_params;
    size_t failed_params;
    bool overall_pass;
} fai_summary_t;

/* Аналіз одного параметра за вибіркою з N плат */
void fai_analyze_parameter(const fai_spec_item_t* spec,
                           const fai_board_record_t* boards,
                           size_t num_boards,
                           size_t param_idx,
                           fai_param_analysis_t* out_analysis) {
    memset(out_analysis, 0, sizeof(fai_param_analysis_t));
    out_analysis->status = STATUS_PASS;

    /* Обробка цифрового хешу */
    if (spec->type == PARAM_TYPE_DIGITAL_HASH) {
        for (size_t i = 0; i < num_boards; i++) {
            if (strncmp(boards[i].hash_values[param_idx], spec->golden_hash, 64) != 0) {
                out_analysis->out_of_spec_count++;
                out_analysis->status = STATUS_FAIL_HASH_MISMATCH;
            }
        }
        return;
    }

    /* Накопичення статистики за алгоритмом Велфорда */
    double mean = 0.0;
    double m2 = 0.0;
    size_t count = 0;

    for (size_t i = 0; i < num_boards; i++) {
        double val = boards[i].analog_values[param_idx];
        count++;
        double delta = val - mean;
        mean += delta / (double)count;
        double delta2 = val - mean;
        m2 += delta * delta2;

        /* Пряма перевірка допусків */
        if (spec->type == PARAM_TYPE_ANALOG_TWO_SIDED) {
            if (val < spec->lsl || val > spec->usl) {
                out_analysis->out_of_spec_count++;
            }
        } else if (spec->type == PARAM_TYPE_UPPER_BOUND_ONLY) {
            if (val > spec->usl) {
                out_analysis->out_of_spec_count++;
            }
        }
    }

    double variance = (count > 1) ? (m2 / (double)(count - 1)) : 0.0;
    double std_dev = sqrt(variance);
    if (std_dev < 1e-9) {
        std_dev = 1e-9; /* Захист від ділення на нуль при однаковому ряді вимірів */
    }

    out_analysis->mean = mean;
    out_analysis->std_dev = std_dev;
    out_analysis->golden_drift = mean - spec->golden_nominal;

    /* Детекція викидів за Z-критерієм (Z > 3.5) */
    for (size_t i = 0; i < num_boards; i++) {
        double val = boards[i].analog_values[param_idx];
        double z_score = fabs(val - mean) / std_dev;
        if (z_score > 3.5) {
            out_analysis->outlier_count++;
        }
    }

    /* Обчислення індексів придатності */
    if (spec->type == PARAM_TYPE_ANALOG_TWO_SIDED) {
        double spec_width = spec->usl - spec->lsl;
        out_analysis->cp = spec_width / (6.0 * std_dev);
        out_analysis->cpu = (spec->usl - mean) / (3.0 * std_dev);
        out_analysis->cpl = (mean - spec->lsl) / (3.0 * std_dev);
        out_analysis->cpk = (out_analysis->cpu < out_analysis->cpl) ? 
                             out_analysis->cpu : out_analysis->cpl;
    } else if (spec->type == PARAM_TYPE_UPPER_BOUND_ONLY) {
        out_analysis->cp = (spec->usl - spec->golden_nominal) / (3.0 * std_dev);
        out_analysis->cpu = (spec->usl - mean) / (3.0 * std_dev);
        out_analysis->cpl = 0.0;
        out_analysis->cpk = out_analysis->cpu;
    }

    /* Формування вердикту */
    if (out_analysis->out_of_spec_count > 0) {
        out_analysis->status = STATUS_FAIL_OUT_OF_SPEC;
    } else if (out_analysis->cpk < 1.33) {
        out_analysis->status = STATUS_WARNING_LOW_CPK;
    } else {
        out_analysis->status = STATUS_PASS;
    }
}

/* Генерація та вивід підсумкового звіту FAI Form 3 */
void fai_generate_report(const fai_spec_item_t* specs,
                         size_t num_params,
                         const fai_board_record_t* boards,
                         size_t num_boards,
                         fai_summary_t* summary) {
    memset(summary, 0, sizeof(fai_summary_t));
    summary->total_boards = num_boards;
    summary->total_params = num_params;
    summary->overall_pass = true;

    printf("==================================================================================================\n");
    printf("                    ПРОТОКОЛ ВАЛІДАЦІЇ ПЕРШОЇ ВИРОБНИЧОЇ ПАРТІЇ (AS9102 FORM 3)                  \n");
    printf("==================================================================================================\n");
    printf("Розмір вибірки: N = %zu плат | Кількість контрольованих параметрів: %zu\n\n", 
           num_boards, num_params);

    printf("%-22s | %-6s | %-8s | %-16s | %-8s | %-6s | %-6s | %-14s\n",
           "Параметр", "Один.", "Еталон", "Поле допуску", "Факт (μ)", "σ", "Cpk", "Вердикт");
    printf("--------------------------------------------------------------------------------------------------\n");

    for (size_t p = 0; p < num_params; p++) {
        fai_param_analysis_t a;
        fai_analyze_parameter(&specs[p], boards, num_boards, p, &a);

        char spec_range_str[32];
        char nominal_str[16];
        char mean_str[16];
        char std_str[16];
        char cpk_str[16];
        const char* verdict_str = "[ PASS ]";

        if (specs[p].type == PARAM_TYPE_DIGITAL_HASH) {
            snprintf(spec_range_str, sizeof(spec_range_str), "Exact Match");
            snprintf(nominal_str, sizeof(nominal_str), "SHA-256");
            snprintf(mean_str, sizeof(mean_str), "MATCH");
            snprintf(std_str, sizeof(std_str), "N/A");
            snprintf(cpk_str, sizeof(cpk_str), "N/A");
        } else {
            if (specs[p].type == PARAM_TYPE_ANALOG_TWO_SIDED) {
                snprintf(spec_range_str, sizeof(spec_range_str), "[%.3f..%.3f]", specs[p].lsl, specs[p].usl);
            } else {
                snprintf(spec_range_str, sizeof(spec_range_str), "[ <= %.3f ]", specs[p].usl);
            }
            snprintf(nominal_str, sizeof(nominal_str), "%.3f", specs[p].golden_nominal);
            snprintf(mean_str, sizeof(mean_str), "%.3f", a.mean);
            snprintf(std_str, sizeof(std_str), "%.4f", a.std_dev);
            snprintf(cpk_str, sizeof(cpk_str), "%.2f", a.cpk);
        }

        switch (a.status) {
            case STATUS_PASS:
                verdict_str = "[ PASS ]";
                summary->passed_params++;
                break;
            case STATUS_WARNING_LOW_CPK:
                verdict_str = "[!CPK < 1.33!]";
                summary->warning_params++;
                break;
            case STATUS_FAIL_OUT_OF_SPEC:
                verdict_str = "[*FAIL OOS*]";
                summary->failed_params++;
                summary->overall_pass = false;
                break;
            case STATUS_FAIL_HASH_MISMATCH:
                verdict_str = "[*FAIL HASH*]";
                summary->failed_params++;
                summary->overall_pass = false;
                break;
        }

        printf("%-22s | %-6s | %-8s | %-16s | %-8s | %-6s | %-6s | %-14s\n",
               specs[p].name, specs[p].unit, nominal_str, spec_range_str,
               mean_str, std_str, cpk_str, verdict_str);
    }

    printf("==================================================================================================\n");
    printf("ПІДСУМОК: Успішно: %zu | Попередження Cpk: %zu | Критичних дефектів: %zu\n",
           summary->passed_params, summary->warning_params, summary->failed_params);
    printf("ФІНАЛЬНИЙ СТАТУС ПАРТІЇ: %s\n", 
           summary->overall_pass ? 
               (summary->warning_params > 0 ? "УМОВНО СХВАЛЕНО (Потрібен контроль Cpk)" : 
                                              "ПОВНІСТЮ СХВАЛЕНО ДЛЯ СЕРІЙНОГО ВИПУСКУ") :
               "ВІДХИЛЕНО — ПАРТІЯ ЗАБЛОКОВАНА ДЛЯ ВІДВАНТАЖЕННЯ");
    printf("==================================================================================================\n\n");
}

/* Демонстраційний запуск валідатора */
int main(void) {
    fai_spec_item_t specs[5] = {
        {
            .name = "VCC_3V3 (Main Rail)",
            .unit = "V",
            .type = PARAM_TYPE_ANALOG_TWO_SIDED,
            .golden_nominal = 3.300,
            .lsl = 3.135,
            .usl = 3.465
        },
        {
            .name = "VCC_1V1 (Core Rail)",
            .unit = "V",
            .type = PARAM_TYPE_ANALOG_TWO_SIDED,
            .golden_nominal = 1.100,
            .lsl = 1.045,
            .usl = 1.155
        },
        {
            .name = "RTC_CLK (Frequency)",
            .unit = "kHz",
            .type = PARAM_TYPE_ANALOG_TWO_SIDED,
            .golden_nominal = 32.768,
            .lsl = 32.760,
            .usl = 32.776
        },
        {
            .name = "BGA_MCU_Voiding",
            .unit = "%",
            .type = PARAM_TYPE_UPPER_BOUND_ONLY,
            .golden_nominal = 5.0,
            .lsl = 0.0,
            .usl = 15.0
        },
        {
            .name = "FW_SHA256_Hash",
            .unit = "HEX",
            .type = PARAM_TYPE_DIGITAL_HASH,
            .golden_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
    };

    /* Синтетична вибірка з 10 плат першої партії */
    fai_board_record_t sample_boards[10];
    double vcc3v3_data[10] = {3.310, 3.305, 3.315, 3.302, 3.308, 3.312, 3.304, 3.309, 3.311, 3.306};
    double vcc1v1_data[10] = {1.102, 1.098, 1.101, 1.099, 1.103, 1.100, 1.097, 1.102, 1.101, 1.099};
    double rtc_data[10]    = {32.768, 32.769, 32.767, 32.768, 32.769, 32.768, 32.767, 32.768, 32.769, 32.768};
    double voids_data[10]  = {6.2, 7.1, 5.8, 8.4, 6.9, 7.5, 5.2, 6.8, 7.9, 6.4};

    for (size_t i = 0; i < 10; i++) {
        snprintf(sample_boards[i].board_serial, FAI_STR_LEN, "SN-2026-FA-%04zu", i + 1);
        sample_boards[i].analog_values[0] = vcc3v3_data[i];
        sample_boards[i].analog_values[1] = vcc1v1_data[i];
        sample_boards[i].analog_values[2] = rtc_data[i];
        sample_boards[i].analog_values[3] = voids_data[i];
        strncpy(sample_boards[i].hash_values[4], 
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 65);
    }

    fai_summary_t summary;
    fai_generate_report(specs, 5, sample_boards, 10, &summary);

    return summary.overall_pass ? 0 : 1;
}
