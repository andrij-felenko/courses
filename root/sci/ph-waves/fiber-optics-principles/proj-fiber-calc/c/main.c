#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_VAL 3.14159265358979323846

/* Структура параметрів оптичного волокна */
typedef struct {
    double n1;           /* Показник заломлення серцевини */
    double n2;           /* Показник заломлення оболонки */
    double core_radius;  /* Радіус серцевини (в метрах) */
    double alpha_dB_km;  /* Коефіцієнт згасання (дБ/км) */
} FiberParams;

/* Структура результатів розрахунку */
typedef struct {
    double na;                  /* Числова апертура NA */
    double acceptance_angle_deg;/* Апертурний кут вводу в повітрі (градуси) */
    double v_number;            /* Нормована частота V */
    bool is_single_mode;        /* Прапорець одномодового режиму */
    unsigned long mode_count;   /* Оцінка кількості мод M */
    double cutoff_wavelength_nm;/* Довжина хвилі відсічки (нм) */
} FiberAnalysis;

/* Структура бюджету потужності траси */
typedef struct {
    double length_km;       /* Довжина лінійного кабелю (км) */
    int splice_count;       /* Кількість зварних зрощувань */
    double splice_loss_dB;  /* Втрати на одне зварювання (дБ) */
    int connector_count;    /* Кількість роз'ємів */
    double conn_loss_dB;    /* Втрати на один роз'єм (дБ) */
    double tx_power_dBm;    /* Потужність передавача (дБм) */
    double rx_sens_dBm;     /* Чутливість приймача (дБм) */
} LinkBudgetInput;

typedef struct {
    double total_attenuation_dB; /* Загальні втрати траси (дБ) */
    double power_margin_dB;      /* Оптичний запас потужності (дБ) */
    bool is_link_viable;         /* Прапорець працездатності лінії */
} LinkBudgetResult;

/* Обчислення оптичних характеристик волокна */
bool analyze_fiber(const FiberParams *fiber, double wavelength_nm, FiberAnalysis *out) {
    if (!fiber || !out || fiber->n1 <= fiber->n2 || fiber->core_radius <= 0.0 || wavelength_nm <= 0.0) {
        return false;
    }

    double n1_sq = fiber->n1 * fiber->n1;
    double n2_sq = fiber->n2 * fiber->n2;
    out->na = sqrt(n1_sq - n2_sq);

    double sin_theta_a = out->na / 1.0; /* для повітря n0 = 1.0 */
    if (sin_theta_a > 1.0) sin_theta_a = 1.0;
    out->acceptance_angle_deg = asin(sin_theta_a) * (180.0 / M_PI_VAL);

    double wavelength_m = wavelength_nm * 1e-9;
    out->v_number = (2.0 * M_PI_VAL * fiber->core_radius / wavelength_m) * out->na;
    out->is_single_mode = (out->v_number < 2.405);

    if (out->is_single_mode) {
        out->mode_count = 1;
    } else {
        out->mode_count = (unsigned long)round((out->v_number * out->v_number) / 2.0);
    }

    out->cutoff_wavelength_nm = ((2.0 * M_PI_VAL * fiber->core_radius * out->na) / 2.405) * 1e9;
    return true;
}

/* Обчислення бюджету оптичного сигналу */
bool calculate_link_budget(const FiberParams *fiber, const LinkBudgetInput *link, LinkBudgetResult *out) {
    if (!fiber || !link || !out || link->length_km < 0.0) {
        return false;
    }

    double fiber_loss = link->length_km * fiber->alpha_dB_km;
    double splices_loss = link->splice_count * link->splice_loss_dB;
    double conns_loss = link->connector_count * link->conn_loss_dB;

    out->total_attenuation_dB = fiber_loss + splices_loss + conns_loss;
    double available_power = link->tx_power_dBm - link->rx_sens_dBm;
    out->power_margin_dB = available_power - out->total_attenuation_dB;
    out->is_link_viable = (out->power_margin_dB >= 3.0); /* вимога запасу мінімум 3 дБ */

    return true;
}

int main(void) {
    /* Приклад: Одномодове волокно SMF-28 (1310 нм) */
    FiberParams smf = {
        .n1 = 1.4677,
        .n2 = 1.4624,
        .core_radius = 4.1e-6, /* 8.2 мкм діаметр */
        .alpha_dB_km = 0.35
    };

    FiberAnalysis analysis;
    if (analyze_fiber(&smf, 1310.0, &analysis)) {
        printf("--- Аналіз волокна SMF-28 (1310 нм) ---\n");
        printf("Числова апертура (NA): %.4f\n", analysis.na);
        printf("Апертурний кут вводу:  %.2f deg\n", analysis.acceptance_angle_deg);
        printf("Параметр V:           %.3f (%s)\n", analysis.v_number,
               analysis.is_single_mode ? "Одномодове" : "Багатомодове");
        printf("Довжина хвилі відсічки: %.1f nm\n\n", analysis.cutoff_wavelength_nm);
    }

    LinkBudgetInput link = {
        .length_km = 40.0,
        .splice_count = 8,
        .splice_loss_dB = 0.05,
        .connector_count = 4,
        .conn_loss_dB = 0.30,
        .tx_power_dBm = 0.0,    /* 1 мВт */
        .rx_sens_dBm = -30.0   /* 1 мкВт */
    };

    LinkBudgetResult budget;
    if (calculate_link_budget(&smf, &link, &budget)) {
        printf("--- Бюджет оптичної траси (40 км) ---\n");
        printf("Загальні втрати траси:   %.2f dB\n", budget.total_attenuation_dB);
        printf("Запас потужності:        %.2f dB\n", budget.power_margin_dB);
        printf("Статус траси:            %s\n", budget.is_link_viable ? "ПРОЙШЛА (OK)" : "НЕВДАЧА (Втрати перевищують норматив)");
    }

    return 0;
}
