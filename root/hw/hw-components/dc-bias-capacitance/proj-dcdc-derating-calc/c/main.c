#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    DIELECTRIC_C0G,
    DIELECTRIC_X7R,
    DIELECTRIC_X5R,
    DIELECTRIC_Y5V
} DielectricClass;

typedef enum {
    PKG_0402,
    PKG_0603,
    PKG_0805,
    PKG_1206,
    PKG_1210
} PackageSize;

typedef struct {
    double nom_cap_uf;       /* Номінальна ємність одного конденсатора, мкФ */
    double rated_voltage;    /* Номінальна гранична напруга за каталогом, В */
    DielectricClass dielectric;
    PackageSize package_size;
    double esr_mohm;         /* Еквівалентний послідовний опір (ESR), мОм */
    int count;               /* Кількість паралельно з'єднаних конденсаторів */
} MlccArray;

typedef struct {
    double v_in;             /* Вхідна напруга живлення, В */
    double v_out;            /* Вихідна стабілізована напруга, В */
    double f_sw_khz;         /* Частота комутації перетворювача, кГц */
    double l_ind_uh;         /* Індуктивність силового дроселя, мкГн */
    double i_step_a;         /* Величина динамічного стрибка струму навантаження, А */
    double t_resp_us;        /* Характерний час реакції контуру зворотного зв'язку, мкс */
} BuckCircuit;

typedef struct {
    double eff_cap_per_unit_uf;
    double eff_total_cap_uf;
    double cap_retention_pct;
    double inductor_ripple_a;
    double v_ripple_nom_mv;
    double v_ripple_actual_mv;
    double pole_nom_khz;
    double pole_actual_khz;
    double v_sag_actual_mv;
    bool is_stable;
} SimulationResult;

static const char* dielectric_to_str(DielectricClass d) {
    switch (d) {
        case DIELECTRIC_C0G: return "C0G/NP0 (Клас I)";
        case DIELECTRIC_X7R: return "X7R (Клас II)";
        case DIELECTRIC_X5R: return "X5R (Клас II)";
        case DIELECTRIC_Y5V: return "Y5V (Клас III)";
        default:             return "Невідомий";
    }
}

static const char* package_to_str(PackageSize p) {
    switch (p) {
        case PKG_0402: return "0402 (1.0x0.5 мм)";
        case PKG_0603: return "0603 (1.6x0.8 мм)";
        case PKG_0805: return "0805 (2.0x1.25 мм)";
        case PKG_1206: return "1206 (3.2x1.6 мм)";
        case PKG_1210: return "1210 (3.2x2.5 мм)";
        default:       return "Невідомий";
    }
}

/* Обчислення відносного залишку ємності за моделлю насичення поляризації */
static double compute_dc_bias_factor(DielectricClass d, PackageSize p, double v_dc, double v_rated) {
    if (d == DIELECTRIC_C0G || v_dc <= 0.0) {
        return 1.0;
    }

    double v_half_ratio;
    double gamma;

    /* Геометричний фактор: більший корпус має товстіший діелектричний шар d */
    switch (p) {
        case PKG_0402: v_half_ratio = 0.30; break;
        case PKG_0603: v_half_ratio = 0.45; break;
        case PKG_0805: v_half_ratio = 0.60; break;
        case PKG_1206: v_half_ratio = 0.85; break;
        case PKG_1210: v_half_ratio = 1.10; break;
        default:       v_half_ratio = 0.50; break;
    }

    /* Фізико-хімічний фактор сегнетоелектричного матеріалу */
    switch (d) {
        case DIELECTRIC_X7R:
            gamma = 1.40;
            break;
        case DIELECTRIC_X5R:
            gamma = 1.65;
            v_half_ratio *= 0.85;
            break;
        case DIELECTRIC_Y5V:
            gamma = 2.40;
            v_half_ratio *= 0.40;
            break;
        default:
            gamma = 1.50;
            break;
    }

    double v_half = v_rated * v_half_ratio;
    double normalized = v_dc / v_half;
    double derating = 1.0 / (1.0 + pow(normalized, gamma));

    /* Нижнє фізичне плато залишкової ємності */
    if (derating < 0.02) {
        derating = 0.02;
    }
    return derating;
}

SimulationResult simulate_buck_output(const MlccArray* cap, const BuckCircuit* ckt) {
    SimulationResult res;
    double v_dc = ckt->v_out;
    double derate_factor = compute_dc_bias_factor(cap->dielectric, cap->package_size, v_dc, cap->rated_voltage);

    res.eff_cap_per_unit_uf = cap->nom_cap_uf * derate_factor;
    res.eff_total_cap_uf = res.eff_cap_per_unit_uf * (double)cap->count;
    res.cap_retention_pct = derate_factor * 100.0;

    double nom_total_cap_uf = cap->nom_cap_uf * (double)cap->count;

    /* Розрахунок струму пульсацій силового дроселя */
    double f_sw_hz = ckt->f_sw_khz * 1e3;
    double l_h = ckt->l_ind_uh * 1e-6;
    res.inductor_ripple_a = (ckt->v_in - ckt->v_out) * ckt->v_out / (f_sw_hz * l_h * ckt->v_in);

    /* Пульсації напруги при ідеальній номінальній ємності */
    double c_nom_f = nom_total_cap_uf * 1e-6;
    double esr_total_ohm = (cap->esr_mohm * 1e-3) / (double)cap->count;
    double v_rip_cap_nom = res.inductor_ripple_a / (8.0 * f_sw_hz * c_nom_f);
    double v_rip_esr = res.inductor_ripple_a * esr_total_ohm;
    res.v_ripple_nom_mv = (v_rip_cap_nom + v_rip_esr) * 1e3;

    /* Пульсації напруги з урахуванням реального DC-bias дератингу */
    double c_eff_f = res.eff_total_cap_uf * 1e-6;
    double v_rip_cap_act = res.inductor_ripple_a / (8.0 * f_sw_hz * c_eff_f);
    res.v_ripple_actual_mv = (v_rip_cap_act + v_rip_esr) * 1e3;

    /* Розрахунок резонансної частоти LC-полюса */
    res.pole_nom_khz = (1.0 / (2.0 * M_PI * sqrt(l_h * c_nom_f))) * 1e-3;
    res.pole_actual_khz = (1.0 / (2.0 * M_PI * sqrt(l_h * c_eff_f))) * 1e-3;

    /* Динамічне просідання напруги під час стрибка навантаження */
    double t_resp_s = ckt->t_resp_us * 1e-6;
    res.v_sag_actual_mv = (ckt->i_step_a * t_resp_s / c_eff_f) * 1e3;

    /* Інженерний критерій стійкості: зсув полюса фільтра не більше ніж у 1.6 раза */
    res.is_stable = (res.pole_actual_khz / res.pole_nom_khz) <= 1.60;

    return res;
}

void print_analysis_report(const MlccArray* cap, const BuckCircuit* ckt, const SimulationResult* res) {
    printf("==================================================================\n");
    printf("  АНАЛІЗ DC-BIAS ЕФЕКТУ ДЛЯ ВИХІДНОГО ФІЛЬТРА DCDC ПЕРЕТВОРЮВАЧА\n");
    printf("==================================================================\n");
    printf("Конфігурація перетворювача:\n");
    printf("  Вхідна / Вихідна напруга:     %.1f В -> %.2f В\n", ckt->v_in, ckt->v_out);
    printf("  Частота комутації / Дросель:   %.0f кГц / %.2f мкГн\n", ckt->f_sw_khz, ckt->l_ind_uh);
    printf("  Стрибок струму / Час реакції:  %.1f А / %.1f мкс\n\n", ckt->i_step_a, ckt->t_resp_us);

    printf("Конденсаторна батарея (вихід):\n");
    printf("  Кількість та тип:             %d x %.1f мкФ (%s, %s)\n",
           cap->count, cap->nom_cap_uf, dielectric_to_str(cap->dielectric), package_to_str(cap->package_size));
    printf("  Номінальна напруга MLCC:      %.1f В\n", cap->rated_voltage);
    printf("  Номінальна сумарна ємність:   %.2f мкФ\n\n", cap->nom_cap_uf * (double)cap->count);

    printf("Результати розрахунку під робочою напругою %.2f В:\n", ckt->v_out);
    printf("  Залишок ємності (DC-bias):    %.1f %% від номіналу\n", res->cap_retention_pct);
    printf("  Ефективна ємність одиниці:    %.2f мкФ (номінал %.1f мкФ)\n",
           res->eff_cap_per_unit_uf, cap->nom_cap_uf);
    printf("  Сумарна ефективна ємність:    %.2f мкФ\n", res->eff_total_cap_uf);
    printf("  Пульсації вихідної напруги:   %.1f мВ (номінально мало бути %.1f мВ)\n",
           res->v_ripple_actual_mv, res->v_ripple_nom_mv);
    printf("  Просідання при навантаженні:  %.1f мВ\n", res->v_sag_actual_mv);
    printf("  Частота полюса LC-фільтра:    %.2f кГц -> %.2f кГц (зсув у %.2fx)\n",
           res->pole_nom_khz, res->pole_actual_khz, res->pole_actual_khz / res->pole_nom_khz);

    if (res->is_stable) {
        printf("  Оцінка стійкості контуру:     [ ДОБРЕ: запас фази збережено ]\n");
    } else {
        printf("  Оцінка стійкості контуру:     [ КРИТИЧНО: ризик генерації/дзвону! ]\n");
        printf("  Рекомендація:                 збільшити корпус до 1206 або додати паралельні MLCC.\n");
    }
    printf("==================================================================\n\n");
}

int main(void) {
    BuckCircuit buck = {
        .v_in = 12.0,
        .v_out = 5.0,
        .f_sw_khz = 1000.0,
        .l_ind_uh = 2.2,
        .i_step_a = 1.5,
        .t_resp_us = 8.0
    };

    /* Сценарій 1: Популярний, але небезпечний вибір — 0603 X5R 22uF 10V */
    MlccArray small_cap = {
        .nom_cap_uf = 22.0,
        .rated_voltage = 10.0,
        .dielectric = DIELECTRIC_X5R,
        .package_size = PKG_0603,
        .esr_mohm = 4.0,
        .count = 2
    };

    /* Сценарій 2: Інженерно грамотний вибір — 1206 X7R 22uF 25V */
    MlccArray robust_cap = {
        .nom_cap_uf = 22.0,
        .rated_voltage = 25.0,
        .dielectric = DIELECTRIC_X7R,
        .package_size = PKG_1206,
        .esr_mohm = 3.0,
        .count = 2
    };

    printf("ТЕСТ 1: Компактні конденсатори 0603 на шині 5 В\n");
    SimulationResult r1 = simulate_buck_output(&small_cap, &buck);
    print_analysis_report(&small_cap, &buck, &r1);

    printf("ТЕСТ 2: Оптимізовані за DC-bias конденсатори 1206 25V на шині 5 В\n");
    SimulationResult r2 = simulate_buck_output(&robust_cap, &buck);
    print_analysis_report(&robust_cap, &buck, &r2);

    return 0;
}
