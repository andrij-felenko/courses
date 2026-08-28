/*
 * dfm_audit_core.c — Базовий модуль верифікації топологічних норм DFM (C99).
 * Перевіряє запас пояска металізації та зазор до контуру плати.
 */

#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    DFM_OK = 0,
    DFM_ERR_ANNULAR_BREAKOUT = (1 << 0),
    DFM_ERR_ANNULAR_TANGENCY = (1 << 1),
    DFM_ERR_COPPER_TO_EDGE   = (1 << 2)
} dfm_status_t;

typedef struct {
    double min_annular_ring_mm;    /* Мінімально допустимий поясок (Class 3: >= 0.05 мм) */
    double min_copper_to_edge_mm;  /* Мінімальний відступ до контуру (Milling: >= 0.30 мм) */
    double drill_tool_oversize_mm; /* Технологічне розширення свердла під металізацію (0.10 мм) */
} dfm_rules_t;

typedef struct {
    double pad_diameter_mm;
    double finished_hole_mm;
    double drill_misreg_mm;        /* Розрахункове радіальне зміщення свердління (наприклад 0.05 мм) */
    double dist_to_outline_mm;     /* Найкоротша відстань від краю міді до контуру плати */
} via_metric_t;

dfm_status_t audit_via_dfm(const via_metric_t *via, const dfm_rules_t *rules)
{
    dfm_status_t status = DFM_OK;

    /* Розрахунок діаметра інструментального свердла */
    double actual_drill_tool = via->finished_hole_mm + rules->drill_tool_oversize_mm;

    /* Номінальний поясок без урахування зміщення */
    double nominal_ar = (via->pad_diameter_mm - actual_drill_tool) / 2.0;

    /* Фактичний залишковий поясок у найгіршому напрямку зміщення свердла */
    double worst_case_ar = nominal_ar - via->drill_misreg_mm;

    if (worst_case_ar < 0.0) {
        /* Отвір повністю прорвав майданчик (Breakout) */
        status |= DFM_ERR_ANNULAR_BREAKOUT;
    } else if (worst_case_ar < rules->min_annular_ring_mm) {
        /* Поясок тонший за вимогу IPC Class 3 або утворився дотик (Tangency) */
        status |= DFM_ERR_ANNULAR_TANGENCY;
    }

    /* Перевірка зазору до контуру обрізки плати */
    if (via->dist_to_outline_mm < rules->min_copper_to_edge_mm) {
        status |= DFM_ERR_COPPER_TO_EDGE;
    }

    return status;
}

int main(void)
{
    dfm_rules_t standard_rules = {
        .min_annular_ring_mm = 0.05,
        .min_copper_to_edge_mm = 0.30,
        .drill_tool_oversize_mm = 0.10
    };

    via_metric_t test_via = {
        .pad_diameter_mm = 0.50,
        .finished_hole_mm = 0.30,
        .drill_misreg_mm = 0.04,
        .dist_to_outline_mm = 0.22
    };

    dfm_status_t res = audit_via_dfm(&test_via, &standard_rules);

    if (res != DFM_OK) {
        printf("Виявлено DFM-порушення (код 0x%X):\n", res);
        if (res & DFM_ERR_ANNULAR_BREAKOUT) printf(" - Критичний прорив пояска металізації!\n");
        if (res & DFM_ERR_ANNULAR_TANGENCY) printf(" - Поясок менший за ліміт Class 3 (ризик дотику)\n");
        if (res & DFM_ERR_COPPER_TO_EDGE)   printf(" - Мідь занадто близько до контуру плати!\n");
    } else {
        printf("Параметри переходу повністю відповідають технологічним нормам.\n");
    }

    return 0;
}
