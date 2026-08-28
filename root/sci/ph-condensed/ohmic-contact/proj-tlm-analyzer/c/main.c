#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура збереження результатів аналізу TLM */
typedef struct {
    double r_sh_ohm_sq;   /* Шаровий опір напівпровідника [Ом/кв] */
    double r_c_ohm;        /* Опір одного контакту [Ом] */
    double l_t_um;         /* Довжина перенесення струму [мкм] */
    double rho_c_ohm_cm2;  /* Питомий опір контакту [Ом·см²] */
    double r2_score;       /* Якість лінійного наближення R^2 */
    double l_ratio;        /* Співвідношення L / L_T */
} tlm_result_t;

/**
 * Розраховує параметри TLM методом найменших квадратів.
 * @param d_um Масив відстаней між контактами [мкм]
 * @param r_ohm Масив виміряних опорів [Ом]
 * @param count Кількість експериментальних точок
 * @param w_um Ширина контакту W [мкм]
 * @param l_um Довжина контакту L [мкм]
 * @param out_res Вказівник на структуру для запису результату
 * @return true при успішному обчисленні, false при фізичній чи математичній помилці
 */
bool tlm_analyze(const double* d_um, const double* r_ohm, size_t count,
                 double w_um, double l_um, tlm_result_t* out_res) {
    if (!d_um || !r_ohm || !out_res || count < 2 || w_um <= 0.0 || l_um <= 0.0) {
        return false;
    }

    double w_cm = w_um * 1e-4;
    double l_cm = l_um * 1e-4;
    double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;

    for (size_t i = 0; i < count; ++i) {
        double x = d_um[i] * 1e-4; /* Переведення мкм у см */
        double y = r_ohm[i];
        sum_x += x;
        sum_y += y;
        sum_xx += x * x;
        sum_xy += x * y;
    }

    double denom = (double)count * sum_xx - sum_x * sum_x;
    if (fabs(denom) < 1e-15) {
        return false;
    }

    double slope = ((double)count * sum_xy - sum_x * sum_y) / denom;
    double intercept = (sum_y * sum_xx - sum_x * sum_xy) / denom;

    /* Фізична перевірка коректності знаків */
    if (slope <= 0.0 || intercept <= 0.0) {
        return false;
    }

    out_res->r_sh_ohm_sq = slope * w_cm;
    out_res->r_c_ohm = intercept / 2.0;
    double l_t_cm = intercept / (2.0 * slope);
    out_res->l_t_um = l_t_cm * 1e4;
    out_res->l_ratio = l_cm / l_t_cm;

    if (out_res->l_ratio < 2.0) {
        out_res->rho_c_ohm_cm2 = out_res->r_c_ohm * w_cm * l_t_cm * tanh(out_res->l_ratio);
    } else {
        out_res->rho_c_ohm_cm2 = out_res->r_c_ohm * w_cm * l_t_cm;
    }

    /* Розрахунок R^2 */
    double y_mean = sum_y / (double)count;
    double ss_tot = 0.0, ss_res = 0.0;
    for (size_t i = 0; i < count; ++i) {
        double x = d_um[i] * 1e-4;
        double y = r_ohm[i];
        double y_pred = slope * x + intercept;
        ss_tot += (y - y_mean) * (y - y_mean);
        ss_res += (y - y_pred) * (y - y_pred);
    }

    out_res->r2_score = (ss_tot > 0.0) ? (1.0 - ss_res / ss_tot) : 0.0;
    return true;
}
