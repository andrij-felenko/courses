#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Профілі стандартів надійності */
typedef enum {
    STANDARD_MIL_HDBK_338B,
    STANDARD_IPC_9592B_CLASS2,
    STANDARD_COMMERCIAL
} DeratingStandard;

/* Типи електронних компонентів */
typedef enum {
    COMP_RESISTOR_FILM,
    COMP_CAP_CERAMIC_X7R,
    COMP_CAP_TANTALUM_MNO2,
    COMP_CAP_ALU_ELECTROLYTIC,
    COMP_SEMICONDUCTOR_MOSFET,
    COMP_SEMICONDUCTOR_DIODE,
    COMP_INDUCTOR_POWER
} ComponentType;

/* Паспортні номінали компонента (Ratings) */
typedef struct {
    const char *designator;      /* Позиційне позначення (наприклад, "R12", "Q1") */
    ComponentType type;
    double v_rated;              /* Максимальна робоча напруга, В */
    double i_rated;              /* Максимальний постійний струм, А */
    double p_rated;              /* Паспортна потужність при Т <= 70 °C, Вт */
    double t_knee;               /* Температура зламу кривої потужності, °C (70 °C) */
    double t_max;                /* Максимальна температура компонента, °C */
    double rth_ja;               /* Тепловий опір кристал-довкілля, °C/Вт */
} ComponentRating;

/* Фактичний робочий режим (Operating Conditions) */
typedef struct {
    double v_actual_peak;        /* Пікова робоча напруга, В */
    double i_actual_rms;         /* Середньоквадратичний робочий струм, А */
    double p_actual_diss;        /* Фактична розсіювана потужність, Вт */
    double ta_ambient;           /* Температура довкілля всередині корпусу, °C */
} OperatingCondition;

/* Результат аудиту дератингу */
typedef struct {
    bool passed;
    double s_v;                  /* Фактичний коефіцієнт напруги */
    double s_i;                  /* Фактичний коефіцієнт струму */
    double s_p;                  /* Фактичний коефіцієнт потужності */
    double tj_actual;            /* Розрахована температура кристала/вузла, °C */
    double p_allowed_derated;    /* Допустима потужність з урахуванням дератингу, Вт */
    const char *failure_reason;
} DeratingResult;

/* Нормативні коефіцієнти для обраного стандарту */
typedef struct {
    double max_s_v;
    double max_s_i;
    double max_s_p;
    double max_tj;
} StandardLimits;

static StandardLimits get_limits(ComponentType type, DeratingStandard std) {
    StandardLimits lim = { 0.80, 0.80, 0.70, 125.0 };

    if (std == STANDARD_MIL_HDBK_338B) {
        lim.max_tj = 105.0;
        switch (type) {
            case COMP_RESISTOR_FILM:        lim.max_s_v = 0.70; lim.max_s_p = 0.50; lim.max_s_i = 0.70; break;
            case COMP_CAP_TANTALUM_MNO2:    lim.max_s_v = 0.50; lim.max_s_p = 0.50; lim.max_s_i = 0.50; break;
            case COMP_CAP_CERAMIC_X7R:      lim.max_s_v = 0.60; lim.max_s_p = 0.60; lim.max_s_i = 0.70; break;
            case COMP_CAP_ALU_ELECTROLYTIC: lim.max_s_v = 0.70; lim.max_s_p = 0.50; lim.max_s_i = 0.70; lim.max_tj = 85.0; break;
            case COMP_SEMICONDUCTOR_MOSFET: lim.max_s_v = 0.75; lim.max_s_p = 0.50; lim.max_s_i = 0.70; lim.max_tj = 110.0; break;
            case COMP_SEMICONDUCTOR_DIODE:  lim.max_s_v = 0.70; lim.max_s_p = 0.50; lim.max_s_i = 0.50; break;
            case COMP_INDUCTOR_POWER:       lim.max_s_v = 0.80; lim.max_s_p = 0.60; lim.max_s_i = 0.70; break;
        }
    } else if (std == STANDARD_IPC_9592B_CLASS2) {
        lim.max_tj = 115.0;
        switch (type) {
            case COMP_RESISTOR_FILM:        lim.max_s_v = 0.80; lim.max_s_p = 0.65; lim.max_s_i = 0.80; break;
            case COMP_CAP_TANTALUM_MNO2:    lim.max_s_v = 0.50; lim.max_s_p = 0.65; lim.max_s_i = 0.70; break;
            case COMP_CAP_CERAMIC_X7R:      lim.max_s_v = 0.70; lim.max_s_p = 0.70; lim.max_s_i = 0.75; break;
            case COMP_CAP_ALU_ELECTROLYTIC: lim.max_s_v = 0.80; lim.max_s_p = 0.70; lim.max_s_i = 0.75; lim.max_tj = 105.0; break;
            case COMP_SEMICONDUCTOR_MOSFET: lim.max_s_v = 0.80; lim.max_s_p = 0.65; lim.max_s_i = 0.75; lim.max_tj = 120.0; break;
            case COMP_SEMICONDUCTOR_DIODE:  lim.max_s_v = 0.80; lim.max_s_p = 0.70; lim.max_s_i = 0.70; break;
            case COMP_INDUCTOR_POWER:       lim.max_s_v = 0.85; lim.max_s_p = 0.70; lim.max_s_i = 0.80; break;
        }
    } else { /* STANDARD_COMMERCIAL */
        lim.max_tj = 130.0;
        lim.max_s_v = 0.90;
        lim.max_s_i = 0.85;
        lim.max_s_p = 0.80;
    }
    return lim;
}

DeratingResult evaluate_derating(const ComponentRating *rat, const OperatingCondition *op, DeratingStandard std) {
    DeratingResult res = { true, 0.0, 0.0, 0.0, 0.0, 0.0, "OK" };
    StandardLimits lim = get_limits(rat->type, std);

    /* 1. Розрахунок коефіцієнтів напруги та струму */
    res.s_v = (rat->v_rated > 0.0) ? (op->v_actual_peak / rat->v_rated) : 0.0;
    res.s_i = (rat->i_rated > 0.0) ? (op->i_actual_rms / rat->i_rated) : 0.0;

    /* 2. Температурний спад паспортної потужності */
    double p_nominal_at_temp = rat->p_rated;
    if (op->ta_ambient > rat->t_knee) {
        if (op->ta_ambient >= rat->t_max) {
            p_nominal_at_temp = 0.0;
        } else {
            p_nominal_at_temp = rat->p_rated * ((rat->t_max - op->ta_ambient) / (rat->t_max - rat->t_knee));
        }
    }

    /* Дератована допустима потужність */
    res.p_allowed_derated = p_nominal_at_temp * lim.max_s_p;
    res.s_p = (p_nominal_at_temp > 0.0) ? (op->p_actual_diss / p_nominal_at_temp) : 999.0;

    /* 3. Розрахунок температури переходу */
    res.tj_actual = op->ta_ambient + (op->p_actual_diss * rat->rth_ja);

    /* 4. Перевірка відповідності нормам */
    if (res.s_v > lim.max_s_v) {
        res.passed = false;
        res.failure_reason = "Перевищення допустимого коефіцієнта напруги (Voltage Overstress)";
    } else if (res.s_i > lim.max_s_i) {
        res.passed = false;
        res.failure_reason = "Перевищення допустимого коефіцієнта струму (Current Overstress)";
    } else if (op->p_actual_diss > res.p_allowed_derated) {
        res.passed = false;
        res.failure_reason = "Перевищення дератованої потужності (Thermal Power Overstress)";
    } else if (res.tj_actual > lim.max_tj) {
        res.passed = false;
        res.failure_reason = "Перевищення дератованої температури кристала Tj";
    }

    return res;
}

int main(void) {
    ComponentRating mosfet = {
        .designator = "Q1_PowerMOS",
        .type = COMP_SEMICONDUCTOR_MOSFET,
        .v_rated = 60.0,       /* 60 В */
        .i_rated = 40.0,       /* 40 А */
        .p_rated = 45.0,       /* 45 Вт при 25 °C */
        .t_knee = 25.0,
        .t_max = 150.0,
        .rth_ja = 2.8          /* Радіатор на платі */
    };

    OperatingCondition op = {
        .v_actual_peak = 48.0, /* 48 В у колі 24 В при індуктивному комутаційному викиді */
        .i_actual_rms = 18.0,  /* 18 А робочий струм */
        .p_actual_diss = 12.0, /* 12 Вт розсіюваної потужності */
        .ta_ambient = 65.0     /* +65 °C всередині корпусу */
    };

    printf("=== АУДИТ ДЕРАТИНГУ ДЛЯ %s ===\n", mosfet.designator);
    DeratingResult res_mil = evaluate_derating(&mosfet, &op, STANDARD_MIL_HDBK_338B);
    printf("[MIL-HDBK-338B] Статус: %s | S_v: %.2f (max 0.75) | Tj: %.1f C (max 110 C) | Причина: %s\n",
           res_mil.passed ? "ВІДПОВІДАЄ" : "ДЕФЕКТ", res_mil.s_v, res_mil.tj_actual, res_mil.failure_reason);

    DeratingResult res_ipc = evaluate_derating(&mosfet, &op, STANDARD_IPC_9592B_CLASS2);
    printf("[IPC-9592B-Cl2]  Статус: %s | S_v: %.2f (max 0.80) | Tj: %.1f C (max 120 C) | Причина: %s\n",
           res_ipc.passed ? "ВІДПОВІДАЄ" : "ДЕФЕКТ", res_ipc.s_v, res_ipc.tj_actual, res_ipc.failure_reason);

    return 0;
}
