#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

#define PANEL_WIDTH_MM       457.0  /* Стандарт 18 дюймів */
#define PANEL_HEIGHT_MM      610.0  /* Стандарт 24 дюйми */
#define PANEL_MARGIN_MM      12.5   /* Технологічні поля панелі */
#define ROUTER_GAP_MM        2.0    /* Ширина фрези між платами */
#define BASE_FR4_COST_SQM    35.0   /* Базова ціна FR-4 за 1 м2 */
#define BASE_NRE_SETUP       120.0  /* Фіксована підготовка лінійки */

typedef enum {
    SURFACE_HASL_LEADFREE = 0,
    SURFACE_OSP           = 1,
    SURFACE_ENIG          = 2,
    SURFACE_ENEPIG        = 3
} SurfaceFinish;

typedef enum {
    TG_STANDARD_130 = 0,
    TG_MID_150      = 1,
    TG_HIGH_170     = 2
} TgRating;

typedef struct {
    double width_mm;
    double height_mm;
    int layer_count;
    double copper_oz;
    double min_trace_mil;
    double min_space_mil;
    TgRating tg;
    SurfaceFinish finish;
    bool has_blind_buried_vias;
    bool has_vippo;
    int vippo_holes_count;
    int order_quantity;
    int turnaround_hours;
} PcbSpecification;

typedef struct {
    int boards_per_panel;
    int panels_needed;
    double panel_utilization_pct;
    double estimated_yield;
    double nre_tooling_cost;
    double panel_unit_cost;
    double total_batch_cost;
    double unit_board_cost;
} PcbCostResult;

static int calculate_nesting(double board_w, double board_h, double panel_w, double panel_h, double margin, double gap) {
    double eff_w = panel_w - 2.0 * margin;
    double eff_h = panel_h - 2.0 * margin;

    if (eff_w <= 0.0 || eff_h <= 0.0 || board_w <= 0.0 || board_h <= 0.0) {
        return 0;
    }

    /* Орієнтація 0 градусів */
    int cols_0 = (int)floor((eff_w + gap) / (board_w + gap));
    int rows_0 = (int)floor((eff_h + gap) / (board_h + gap));
    int count_0 = (cols_0 > 0 && rows_0 > 0) ? (cols_0 * rows_0) : 0;

    /* Орієнтація 90 градусів */
    int cols_90 = (int)floor((eff_w + gap) / (board_h + gap));
    int rows_90 = (int)floor((eff_h + gap) / (board_w + gap));
    int count_90 = (cols_90 > 0 && rows_90 > 0) ? (cols_90 * rows_90) : 0;

    return (count_0 > count_90) ? count_0 : count_90;
}

static double estimate_yield(double board_area_cm2, int layers, double min_feature_mil) {
    double feature = (min_feature_mil < 3.0) ? 3.0 : min_feature_mil;
    /* Базова модель дефектів фотолітографії */
    double defect_density = 0.018 * pow(6.0 / feature, 1.75) * sqrt((double)layers / 2.0);
    double y = exp(-defect_density * (board_area_cm2 / 100.0));
    return (y < 0.40) ? 0.40 : ((y > 0.99) ? 0.99 : y);
}

bool pcb_calculate_cost(const PcbSpecification* spec, PcbCostResult* res) {
    if (!spec || !res || spec->width_mm <= 0.0 || spec->height_mm <= 0.0 || spec->order_quantity <= 0) {
        return false;
    }

    int n_per_panel = calculate_nesting(
        spec->width_mm, spec->height_mm,
        PANEL_WIDTH_MM, PANEL_HEIGHT_MM,
        PANEL_MARGIN_MM, ROUTER_GAP_MM
    );

    if (n_per_panel == 0) {
        return false;
    }

    double board_area_sqm = (spec->width_mm * spec->height_mm) / 1000000.0;
    double board_area_cm2 = (spec->width_mm * spec->height_mm) / 100.0;
    double panel_area_sqm = (PANEL_WIDTH_MM * PANEL_HEIGHT_MM) / 1000000.0;

    double util_pct = ((double)n_per_panel * board_area_sqm / panel_area_sqm) * 100.0;

    double min_feature = (spec->min_trace_mil < spec->min_space_mil) ? spec->min_trace_mil : spec->min_space_mil;
    double yield_val = estimate_yield(board_area_cm2, spec->layer_count, min_feature);

    /* Множник матеріалів за шаруватістю */
    double layer_mult = 1.0;
    if (spec->layer_count > 2) {
        layer_mult = 1.0 + 0.42 * (double)(spec->layer_count - 2);
    }

    /* Множник матеріалу Tg */
    double tg_mult = 1.0;
    if (spec->tg == TG_MID_150) tg_mult = 1.20;
    else if (spec->tg == TG_HIGH_170) tg_mult = 1.45;

    /* Множник міді */
    double cu_mult = 1.0 + 0.38 * (spec->copper_oz > 1.0 ? (spec->copper_oz - 1.0) : 0.0);

    /* Множник покриття */
    double finish_cost_panel = 0.0;
    if (spec->finish == SURFACE_ENIG) finish_cost_panel = 14.5 * panel_area_sqm;
    else if (spec->finish == SURFACE_ENEPIG) finish_cost_panel = 32.0 * panel_area_sqm;
    else if (spec->finish == SURFACE_OSP) finish_cost_panel = -2.0 * panel_area_sqm;

    /* Вартість глухих отворів та VIPPO */
    double via_complexity_mult = 1.0;
    if (spec->has_blind_buried_vias) {
        via_complexity_mult += 0.65;
    }
    double vippo_cost = 0.0;
    if (spec->has_vippo && spec->vippo_holes_count > 0) {
        vippo_cost = (double)spec->vippo_holes_count * 0.035;
    }

    /* Базова собівартість панелі */
    double panel_cost = (panel_area_sqm * BASE_FR4_COST_SQM * tg_mult * layer_mult * cu_mult * via_complexity_mult)
                      + finish_cost_panel + vippo_cost;

    /* Терміновість */
    double rush_mult = 1.0;
    if (spec->turnaround_hours < 120) {
        double delta = (120.0 - (double)spec->turnaround_hours) / 120.0;
        rush_mult = 1.0 + pow(delta, 1.6) * 2.8;
    }

    panel_cost *= rush_mult;

    /* Розрахунок NRE */
    double nre = BASE_NRE_SETUP;
    if (spec->layer_count > 2) nre += (double)(spec->layer_count - 2) * 28.0;
    if (spec->has_blind_buried_vias) nre += 85.0;
    if (spec->min_trace_mil < 4.0 || spec->min_space_mil < 4.0) nre += 50.0;
    nre *= (rush_mult > 1.5) ? 1.5 : rush_mult;

    /* Кількість панелей для виконання замовлення з урахуванням виходу */
    int effective_boards_per_panel = (int)floor((double)n_per_panel * yield_val);
    if (effective_boards_per_panel < 1) effective_boards_per_panel = 1;

    int panels_needed = (spec->order_quantity + effective_boards_per_panel - 1) / effective_boards_per_panel;
    if (panels_needed < 1) panels_needed = 1;

    double total_variable = (double)panels_needed * panel_cost;
    double total_cost = nre + total_variable;

    res->boards_per_panel = n_per_panel;
    res->panels_needed = panels_needed;
    res->panel_utilization_pct = util_pct;
    res->estimated_yield = yield_val;
    res->nre_tooling_cost = nre;
    res->panel_unit_cost = panel_cost;
    res->total_batch_cost = total_cost;
    res->unit_board_cost = total_cost / (double)spec->order_quantity;

    return true;
}

int main(void) {
    PcbSpecification spec = {
        .width_mm = 85.0,
        .height_mm = 54.0,
        .layer_count = 4,
        .copper_oz = 1.0,
        .min_trace_mil = 5.0,
        .min_space_mil = 5.0,
        .tg = TG_MID_150,
        .finish = SURFACE_ENIG,
        .has_blind_buried_vias = false,
        .has_vippo = false,
        .vippo_holes_count = 0,
        .order_quantity = 500,
        .turnaround_hours = 120
    };

    PcbCostResult res;
    if (pcb_calculate_cost(&spec, &res)) {
        printf("=== Результати розрахунку собівартості PCB ===\n");
        printf("Розмір плати: %.1f x %.1f мм\n", spec.width_mm, spec.height_mm);
        printf("Кількість шарів: %d, Покриття: ENIG, Партія: %d шт.\n", spec.layer_count, spec.order_quantity);
        printf("Плат на панелі 18\"x24\": %d шт. (Утилізація: %.1f%%)\n", res.boards_per_panel, res.panel_utilization_pct);
        printf("Оціночний вихід (Yield): %.2f%%\n", res.estimated_yield * 100.0);
        printf("Потрібно виробничих панелей: %d шт.\n", res.panels_needed);
        printf("Фіксовані витрати (NRE Tooling): $%.2f\n", res.nre_tooling_cost);
        printf("Собівартість 1 панелі: $%.2f\n", res.panel_unit_cost);
        printf("Повна вартість партії: $%.2f\n", res.total_batch_cost);
        printf("Ціна за 1 готову плату: $%.2f\n", res.unit_board_cost);
    }
    return 0;
}
