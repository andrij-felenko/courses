#include <math.h>
#include <stdio.h>

// Параметри ОП для розрахунку бюджету постійного струму
typedef struct {
    double vos_base_uv;    // Початковий зсув за 25°C (мкВ)
    double drift_uv_per_c; // Температурний дрейф (мкВ/°C)
    double cmrr_db;        // CMRR (дБ)
    double psrr_db;        // PSRR (дБ)
} OpAmpOffsetSpecs;

// Результат розрахунку бюджету похибки
typedef struct {
    double worst_case_uv;  // Найгірша адитивна похибка (мкВ)
    double rss_uv;         // Статистична середньоквадратична похибка (мкВ)
} OffsetBudgetResult;

// Розрахунок сумарної напруги зсуву, зведеної до входу
OffsetBudgetResult calculate_offset_budget(const OpAmpOffsetSpecs* specs,
                                           double delta_t_c,
                                           double delta_vcm_v,
                                           double delta_vsupply_v) {
    OffsetBudgetResult res;

    double temp_error_uv = specs->drift_uv_per_c * fabs(delta_t_c);
    
    // Переведення дБ у лінійний коефіцієнт послаблення
    double cmrr_ratio = pow(10.0, specs->cmrr_db / 20.0);
    double psrr_ratio = pow(10.0, specs->psrr_db / 20.0);

    // Зведення до мікровольтів (1 В = 1e6 мкВ)
    double cmrr_error_uv = (fabs(delta_vcm_v) / cmrr_ratio) * 1.0e6;
    double psrr_error_uv = (fabs(delta_vsupply_v) / psrr_ratio) * 1.0e6;

    // Найгірший випадок (пряме додавання модулів)
    res.worst_case_uv = specs->vos_base_uv + temp_error_uv + cmrr_error_uv + psrr_error_uv;

    // Статистичне підсумовування (RSS)
    res.rss_uv = sqrt(specs->vos_base_uv * specs->vos_base_uv +
                      temp_error_uv * temp_error_uv +
                      cmrr_error_uv * cmrr_error_uv +
                      psrr_error_uv * psrr_error_uv);

    return res;
}
