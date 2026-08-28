#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define METROLOGY_MAX_COMPONENTS 8

/* Типи апріорних розподілів ймовірностей для оцінювання за Типом B */
typedef enum {
    DISTRIBUTION_RECTANGULAR, /* Прямокутний: u = a / sqrt(3) */
    DISTRIBUTION_TRIANGULAR,  /* Трикутний:   u = a / sqrt(6) */
    DISTRIBUTION_NORMAL_K2,   /* Нормальний 95.45%: u = U / 2.0 */
    DISTRIBUTION_NORMAL_K3,   /* Нормальний 99.73%: u = U / 3.0 */
    DISTRIBUTION_U_SHAPED     /* U-подібний (гармонічний): u = a / sqrt(2) */
} pdf_type_t;

/* Окреме джерело невизначеності в бюджеті */
typedef struct {
    const char *name;
    double std_uncertainty;    /* Стандартна невизначеність u(x_i) */
    double sensitivity;        /* Коефіцієнт чутливості c_i = df/dx_i */
    double degrees_of_freedom; /* Ступені вільності (для типу B часто INFINITY) */
} uncertainty_item_t;

/* Бюджет невизначеності вимірювального каналу */
typedef struct {
    uncertainty_item_t items[METROLOGY_MAX_COMPONENTS];
    size_t count;
} uncertainty_budget_t;

/* Однопрохідний накопичувач Велфорда для оцінки за Типом A */
typedef struct {
    uint32_t count;
    double mean;
    double m2; /* Сума квадратів відхилень від поточного середнього */
} welford_acc_t;

/* Результат метрологічного звіту */
typedef struct {
    double value;           /* Оцінка вимірюваної величини */
    double u_type_a;        /* Стандартна невизначеність типу A (s / sqrt(N)) */
    double u_combined;      /* Сумарна стандартна невизначеність u_c */
    double expanded_u;      /* Розширена невизначеність U = k * u_c */
    double eff_dof;         /* Ефективні ступені вільності (Велч-Саттерзвейт) */
    double coverage_factor; /* Застосований коефіцієнт охоплення k */
} metrology_report_t;

/* Ініціалізація накопичувача вибірки */
void welford_init(welford_acc_t *acc) {
    acc->count = 0;
    acc->mean = 0.0;
    acc->m2 = 0.0;
}

/* Додавання нового відліку за алгоритмом Велфорда */
void welford_update(welford_acc_t *acc, double x) {
    acc->count++;
    double delta = x - acc->mean;
    acc->mean += delta / (double)acc->count;
    double delta2 = x - acc->mean;
    acc->m2 += delta * delta2;
}

/* Обчислення статистичної невизначеності типу A: s / sqrt(N) */
bool welford_get_type_a(const welford_acc_t *acc, double *mean_out, double *u_a_out) {
    if (acc->count < 2) {
        return false;
    }
    *mean_out = acc->mean;
    double variance = acc->m2 / (double)(acc->count - 1);
    double s = sqrt(variance);
    *u_a_out = s / sqrt((double)acc->count);
    return true;
}

/* Розрахунок стандартної невизначеності за Типом B з напівширини a */
double eval_type_b(double half_width, pdf_type_t dist) {
    switch (dist) {
        case DISTRIBUTION_RECTANGULAR:
            return half_width / sqrt(3.0);
        case DISTRIBUTION_TRIANGULAR:
            return half_width / sqrt(6.0);
        case DISTRIBUTION_NORMAL_K2:
            return half_width / 2.0;
        case DISTRIBUTION_NORMAL_K3:
            return half_width / 3.0;
        case DISTRIBUTION_U_SHAPED:
            return half_width / sqrt(2.0);
        default:
            return half_width / sqrt(3.0);
    }
}

/* Розрахунок невизначеності квантування АЦП для кроку LSB = Vref / 2^bits */
double eval_adc_quantization_unc(double v_ref, uint8_t bits) {
    double lsb = v_ref / (double)(1ULL << bits);
    return lsb / sqrt(12.0); /* Рівномірний розподіл на інтервалі [-LSB/2, +LSB/2] */
}

/* Ініціалізація бюджету */
void budget_init(uncertainty_budget_t *b) {
    b->count = 0;
}

/* Додавання джерела до бюджету */
bool budget_add(uncertainty_budget_t *b, const char *name, double u, double c, double dof) {
    if (b->count >= METROLOGY_MAX_COMPONENTS) {
        return false;
    }
    b->items[b->count].name = name;
    b->items[b->count].std_uncertainty = u;
    b->items[b->count].sensitivity = c;
    b->items[b->count].degrees_of_freedom = dof;
    b->count++;
    return true;
}

/* Зведення бюджету та розрахунок сумарної й розширеної невизначеності */
bool budget_evaluate(const uncertainty_budget_t *b, double meas_val, double k, metrology_report_t *rep) {
    if (b->count == 0) {
        return false;
    }

    double sum_sq = 0.0;
    double ws_denom = 0.0;

    for (size_t i = 0; i < b->count; ++i) {
        double c_u = b->items[i].sensitivity * b->items[i].std_uncertainty;
        double contribution_sq = c_u * c_u;
        sum_sq += contribution_sq;

        if (isfinite(b->items[i].degrees_of_freedom) && b->items[i].degrees_of_freedom > 0.0) {
            double c_u_quad = contribution_sq * contribution_sq;
            ws_denom += c_u_quad / b->items[i].degrees_of_freedom;
        }
    }

    rep->value = meas_val;
    rep->u_combined = sqrt(sum_sq);
    rep->coverage_factor = k;
    rep->expanded_u = k * rep->u_combined;

    /* Формула Велча-Саттерзвейта для ефективних ступенів вільності */
    if (ws_denom > 1e-15) {
        double u_c_quad = sum_sq * sum_sq;
        rep->eff_dof = u_c_quad / ws_denom;
    } else {
        rep->eff_dof = INFINITY;
    }

    return true;
}

int main(void) {
    /* Демонстрація: Вимірювання тиску тензометричним давачем з 16-бітним АЦП */
    welford_acc_t adc_sampler;
    welford_init(&adc_sampler);

    /* 16 послідовних вибірок тиску в барах */
    const double raw_samples[16] = {
        10.042, 10.038, 10.045, 10.040, 10.048, 10.037, 10.041, 10.044,
        10.039, 10.046, 10.040, 10.043, 10.036, 10.047, 10.041, 10.042
    };

    for (size_t i = 0; i < 16; ++i) {
        welford_update(&adc_sampler, raw_samples[i]);
    }

    double mean_pressure = 0.0;
    double u_a = 0.0;
    welford_get_type_a(&adc_sampler, &mean_pressure, &u_a);

    /* Формування бюджету невизначеності */
    uncertainty_budget_t budget;
    budget_init(&budget);

    /* 1. Статистичний шум вибірки (Тип A) */
    budget_add(&budget, "Випадковий шум вибірки", u_a, 1.0, 16 - 1);

    /* 2. Квантування АЦП: діапазон 20 бар на 16 біт (Тип B) */
    double u_quant = (20.0 / 65536.0) / sqrt(12.0);
    budget_add(&budget, "Шум квантування АЦП", u_quant, 1.0, INFINITY);

    /* 3. Паспортна похибка калібрування давача: +/-0.05 бар (прямокутний) */
    double u_cal = eval_type_b(0.05, DISTRIBUTION_RECTANGULAR);
    budget_add(&budget, "Калібрування давача", u_cal, 1.0, INFINITY);

    /* 4. Температурний дрейф нуля: +/-0.02 бар (трикутний) */
    double u_temp = eval_type_b(0.02, DISTRIBUTION_TRIANGULAR);
    budget_add(&budget, "Температурний дрейф", u_temp, 1.0, INFINITY);

    metrology_report_t report;
    budget_evaluate(&budget, mean_pressure, 2.0, &report);

    printf("=== Метрологічний звіт вимірювання тиску ===\n");
    printf("Оцінка значення (середнє): %.4f бар\n", report.value);
    printf("Статистична невизначеність u_A: %.5f бар\n", u_a);
    printf("Сумарна невизначеність u_c:     %.5f бар\n", report.u_combined);
    printf("Розширена невизначеність U(k=2): %.5f бар (P = 95.45%%)\n", report.expanded_u);
    printf("Ефективні ступені вільності nu:  %.1f\n", report.eff_dof);
    printf("Результат для запису: P = (%.4f +/- %.4f) бар, k=2\n",
           report.value, report.expanded_u);

    return 0;
}
