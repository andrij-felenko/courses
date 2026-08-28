#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_CELLS 256
#define MAX_SERIES 32
#define MAX_PARALLEL 16

/* Структура виміряних параметрів окремої комірки */
typedef struct {
    uint32_t id;          /* Серійний номер або штрихкод */
    uint32_t capacity_mah;/* Дійсна ємність, мА·год */
    uint32_t ir_uohm;     /* Внутрішній опір AC IR, мікрооми (мкОм) */
    uint16_t ocv_mv;      /* Напруга спокою, мВ */
} CellData;

/* Паралельна група (одна послідовна ланка пакета) */
typedef struct {
    CellData cells[MAX_PARALLEL];
    uint32_t cell_count;
    uint32_t total_capacity_mah;
    double eq_resistance_mohm; /* 1 / R_eq = sum(1 / R_i) */
} SeriesGroup;

/* Акумуляторний пакет */
typedef struct {
    SeriesGroup groups[MAX_SERIES];
    uint32_t series_count;
    uint32_t parallel_count;
    uint32_t min_group_capacity_mah;
    uint32_t max_group_capacity_mah;
    double capacity_imbalance_pct;
    double max_ir_diff_mohm;
} BatteryPack;

/* Компаратор для qsort: сортування комірок за ємністю (спадно) */
static int compare_capacity_desc(const void *a, const void *b) {
    const CellData *cell_a = (const CellData *)a;
    const CellData *cell_b = (const CellData *)b;
    if (cell_b->capacity_mah != cell_a->capacity_mah) {
        return (cell_b->capacity_mah > cell_a->capacity_mah) ? 1 : -1;
    }
    /* Якщо ємність однакова — сортуємо за зростанням опору */
    if (cell_a->ir_uohm != cell_b->ir_uohm) {
        return (cell_a->ir_uohm > cell_b->ir_uohm) ? 1 : -1;
    }
    return (cell_a->id > cell_b->id) ? 1 : -1;
}

/* Перерахунок сумарної ємності та еквівалентного опору групи */
static void update_group_metrics(SeriesGroup *group) {
    uint32_t cap_sum = 0;
    double conductance_sum = 0.0;

    for (uint32_t i = 0; i < group->cell_count; i++) {
        cap_sum += group->cells[i].capacity_mah;
        double r_mohm = (double)group->cells[i].ir_uohm / 1000.0;
        if (r_mohm > 0.001) {
            conductance_sum += 1.0 / r_mohm;
        }
    }

    group->total_capacity_mah = cap_sum;
    group->eq_resistance_mohm = (conductance_sum > 0.0) ? (1.0 / conductance_sum) : 0.0;
}

/* Оновлення метрик дисбалансу всього пакета */
static void update_pack_metrics(BatteryPack *pack) {
    if (pack->series_count == 0) return;

    uint32_t min_cap = pack->groups[0].total_capacity_mah;
    uint32_t max_cap = pack->groups[0].total_capacity_mah;
    double min_r = pack->groups[0].eq_resistance_mohm;
    double max_r = pack->groups[0].eq_resistance_mohm;

    for (uint32_t s = 1; s < pack->series_count; s++) {
        uint32_t cap = pack->groups[s].total_capacity_mah;
        double r = pack->groups[s].eq_resistance_mohm;

        if (cap < min_cap) min_cap = cap;
        if (cap > max_cap) max_cap = cap;
        if (r < min_r) min_r = r;
        if (r > max_r) max_r = r;
    }

    pack->min_group_capacity_mah = min_cap;
    pack->max_group_capacity_mah = max_cap;
    pack->capacity_imbalance_pct = (max_cap > 0) 
        ? ((double)(max_cap - min_cap) * 100.0 / (double)max_cap) 
        : 0.0;
    pack->max_ir_diff_mohm = max_r - min_r;
}

/* Алгоритм змійки (Serpentine Bin-Packing) */
bool pack_cells_serpentine(CellData *cells, uint32_t total_cells, 
                           uint32_t series, uint32_t parallel, 
                           BatteryPack *out_pack) {
    if (total_cells < series * parallel) {
        return false; /* Недостатньо комірок для побудови пакета */
    }
    if (series > MAX_SERIES || parallel > MAX_PARALLEL || series == 0 || parallel == 0) {
        return false;
    }

    /* 1. Сортуємо комірки за ємністю від найбільшої до найменшої */
    qsort(cells, total_cells, sizeof(CellData), compare_capacity_desc);

    out_pack->series_count = series;
    out_pack->parallel_count = parallel;

    for (uint32_t s = 0; s < series; s++) {
        out_pack->groups[s].cell_count = 0;
    }

    /* 2. Розподіл змійкою: 0..S-1, потім S-1..0 */
    uint32_t cell_idx = 0;
    for (uint32_t p = 0; p < parallel; p++) {
        bool forward = (p % 2 == 0);
        for (uint32_t s = 0; s < series; s++) {
            uint32_t target_group = forward ? s : (series - 1 - s);
            SeriesGroup *grp = &out_pack->groups[target_group];
            grp->cells[grp->cell_count++] = cells[cell_idx++];
        }
    }

    /* 3. Розрахунок результуючих показників для кожної групи */
    for (uint32_t s = 0; s < series; s++) {
        update_group_metrics(&out_pack->groups[s]);
    }

    update_pack_metrics(out_pack);
    return true;
}

/* Друк звіту про скомплектований пакет */
void print_pack_report(const BatteryPack *pack) {
    printf("=== ЗВІТ КОМПЛЕКТУВАННЯ БАТАРЕЇ %uS%uP ===\n", 
           pack->series_count, pack->parallel_count);
    printf("Дисбаланс ємності: %.3f%% (мін: %u мА·год, макс: %u мА·год, різниця: %u мА·год)\n",
           pack->capacity_imbalance_pct,
           pack->min_group_capacity_mah,
           pack->max_group_capacity_mah,
           pack->max_group_capacity_mah - pack->min_group_capacity_mah);
    printf("Максимальний розкид еквівалентного опору: %.3f мОм\n\n", pack->max_ir_diff_mohm);

    for (uint32_t s = 0; s < pack->series_count; s++) {
        const SeriesGroup *g = &pack->groups[s];
        printf("  Ланка S%02u: Q = %5u мА·год | R_eq = %6.3f мОм | Комірки ID: [",
               s + 1, g->total_capacity_mah, g->eq_resistance_mohm);
        for (uint32_t p = 0; p < g->cell_count; p++) {
            printf("%u%s", g->cells[p].id, (p + 1 < g->cell_count) ? ", " : "");
        }
        printf("]\n");
    }
}
