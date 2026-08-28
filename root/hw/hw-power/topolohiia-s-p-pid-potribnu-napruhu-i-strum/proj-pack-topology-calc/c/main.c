#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    BUSBAR_COPPER,
    BUSBAR_NICKEL,
    BUSBAR_NICKEL_PLATED_STEEL
} BusbarMaterial;

typedef struct {
    double v_nom;       /* Номінальна напруга комірки (В), наприклад 3.6 */
    double v_min;       /* Мінімальна напруга розряду (В), наприклад 2.5 */
    double v_max;       /* Максимальна напруга повного заряду (В), наприклад 4.2 */
    double cap_ah;      /* Номінальна ємність (А·год), наприклад 4.5 */
    double i_cont_max;  /* Максимальний тривалий струм розряду (А), наприклад 15.0 */
    double i_peak_max;  /* Максимальний піковий струм розряду (А), наприклад 30.0 */
    double r_internal;  /* Внутрішній опір комірки DCIR (Ом), наприклад 0.020 (20 мОм) */
    double weight_g;    /* Маса однієї комірки (г), наприклад 70.0 */
} CellSpec;

typedef struct {
    double v_target_nom;    /* Цільова номінальна напруга системи (В), наприклад 48.0 */
    double v_inverter_min;  /* Нижній поріг відсічки інвертора (В), наприклад 40.0 */
    double v_inverter_max;  /* Верхній ліміт вхідної напруги інвертора (В), наприклад 58.4 */
    double p_continuous_w;  /* Тривала потужність навантаження (Вт), наприклад 2000.0 */
    double p_peak_w;        /* Пікова потужність навантаження (Вт), наприклад 4000.0 */
    double energy_wh_req;   /* Необхідний запас енергії (Вт·год), наприклад 1000.0 */
} SystemRequirements;

typedef struct {
    int s_count;            /* Кількість послідовних груп (S) */
    int p_count;            /* Кількість паралельних комірок у групі (P) */
    int total_cells;        /* Загальна кількість банок (S * P) */
    double v_pack_nom;      /* Номінальна напруга батареї (В) */
    double v_pack_min;      /* Мінімальна напруга розрядженої батареї (В) */
    double v_pack_max;      /* Максимальна напруга зарядженої батареї (В) */
    double cap_pack_ah;     /* Сумарна ємність пакета (А·год) */
    double energy_pack_wh;  /* Сумарна запасена енергія (Вт·год) */
    double i_cont_max;      /* Максимальний допустимий тривалий струм пакета (А) */
    double i_peak_max;      /* Максимальний допустимий піковий струм пакета (А) */
    double r_pack_total;    /* Еквівалентний внутрішній опір батареї (Ом) */
    double v_sag_continuous;/* Просадка напруги на номінальній потужності (В) */
    double v_sag_peak;      /* Просадка напруги на піковій потужності (В) */
    double busbar_area_mm2; /* Рекомендований переріз головної шини (мм²) */
    double total_weight_kg; /* Орієнтовна маса тільки комірок (кг) */
    bool is_valid;          /* Чи вкладається конфігурація у вікно напруг інвертора */
} PackDesign;

/* Питомий опір у мОм·мм²/м */
double get_busbar_resistivity(BusbarMaterial mat) {
    switch (mat) {
        case BUSBAR_COPPER: return 17.2;
        case BUSBAR_NICKEL: return 96.0;
        case BUSBAR_NICKEL_PLATED_STEEL: return 130.0;
        default: return 17.2;
    }
}

/* Рекомендована щільність струму (А/мм²) */
double get_target_current_density(BusbarMaterial mat) {
    switch (mat) {
        case BUSBAR_COPPER: return 5.0;
        case BUSBAR_NICKEL: return 1.5;
        case BUSBAR_NICKEL_PLATED_STEEL: return 1.0;
        default: return 5.0;
    }
}

PackDesign calculate_pack_topology(const CellSpec* cell, 
                                   const SystemRequirements* req, 
                                   BusbarMaterial busbar_mat) {
    PackDesign d;
    d.is_valid = true;

    /* 1. Розрахунок послідовних груп S */
    d.s_count = (int)ceil(req->v_target_nom / cell->v_nom);
    d.v_pack_nom = d.s_count * cell->v_nom;
    d.v_pack_min = d.s_count * cell->v_min;
    d.v_pack_max = d.s_count * cell->v_max;

    /* Перевірка лімітів інвертора */
    if (d.v_pack_max > req->v_inverter_max || d.v_pack_min < req->v_inverter_min) {
        d.is_valid = false;
    }

    /* 2. Розрахунок струмів системи */
    double i_cont_req = req->p_continuous_w / d.v_pack_min;
    double i_peak_req = req->p_peak_w / d.v_pack_min;

    /* 3. Розрахунок паралельних банок P за трьома критеріями */
    int p_by_cont_current = (int)ceil(i_cont_req / cell->i_cont_max);
    int p_by_peak_current = (int)ceil(i_peak_req / cell->i_peak_max);
    int p_by_energy = (int)ceil(req->energy_wh_req / (d.v_pack_nom * cell->cap_ah));

    int p_max = p_by_cont_current;
    if (p_by_peak_current > p_max) p_max = p_by_peak_current;
    if (p_by_energy > p_max) p_max = p_by_energy;
    if (p_max < 1) p_max = 1;

    d.p_count = p_max;
    d.total_cells = d.s_count * d.p_count;

    /* 4. Електричні параметри зібраного пакета */
    d.cap_pack_ah = d.p_count * cell->cap_ah;
    d.energy_pack_wh = d.v_pack_nom * d.cap_pack_ah;
    d.i_cont_max = d.p_count * cell->i_cont_max;
    d.i_peak_max = d.p_count * cell->i_peak_max;

    /* Внутрішній опір: S послідовних груп по P паралельних комірок */
    /* Додаємо умовні 1.5 мОм на комутацію групи (шини + BMS FETs) */
    double r_interconnect_per_s = 0.0015;
    d.r_pack_total = d.s_count * ((cell->r_internal / d.p_count) + r_interconnect_per_s);

    /* 5. Просадка напруги під навантаженням */
    d.v_sag_continuous = i_cont_req * d.r_pack_total;
    d.v_sag_peak = i_peak_req * d.r_pack_total;

    /* 6. Переріз головної силової шини */
    double j_target = get_target_current_density(busbar_mat);
    d.busbar_area_mm2 = i_cont_req / j_target;

    /* 7. Маса батареї */
    d.total_weight_kg = (d.total_cells * cell->weight_g) / 1000.0;

    return d;
}

int main(void) {
    CellSpec cell_21700 = {
        .v_nom = 3.6,
        .v_min = 2.5,
        .v_max = 4.2,
        .cap_ah = 4.5,
        .i_cont_max = 15.0,
        .i_peak_max = 30.0,
        .r_internal = 0.018, /* 18 мОм */
        .weight_g = 70.0
    };

    SystemRequirements drone_req = {
        .v_target_nom = 48.0,
        .v_inverter_min = 38.0,
        .v_inverter_max = 58.8,
        .p_continuous_w = 2500.0,
        .p_peak_w = 5000.0,
        .energy_wh_req = 1200.0
    };

    PackDesign design = calculate_pack_topology(&cell_21700, &drone_req, BUSBAR_COPPER);

    printf("=== Звіт проєктування батареї ===\n");
    printf("Конфігурація: %dS%dP (Всього комірок: %d)\n", 
           design.s_count, design.p_count, design.total_cells);
    printf("Напруга: ном. %.1f В (робоче вікно: %.1f В .. %.1f В)\n", 
           design.v_pack_nom, design.v_pack_min, design.v_pack_max);
    printf("Ємність: %.2f А·год | Енергія: %.1f Вт·год\n", 
           design.cap_pack_ah, design.energy_pack_wh);
    printf("Внутрішній опір пакета (DCIR): %.4f Ом (%.2f мОм)\n", 
           design.r_pack_total, design.r_pack_total * 1000.0);
    printf("Просадка напруги: ном. %.2f В | пік. %.2f В\n", 
           design.v_sag_continuous, design.v_sag_peak);
    printf("Рекомендований переріз мідної шини: %.2f мм²\n", design.busbar_area_mm2);
    printf("Маса комірок: %.2f кг\n", design.total_weight_kg);
    printf("Статус валідації: %s\n", design.is_valid ? "OK" : "ПОМИЛКА НАПРУГИ");

    return 0;
}
