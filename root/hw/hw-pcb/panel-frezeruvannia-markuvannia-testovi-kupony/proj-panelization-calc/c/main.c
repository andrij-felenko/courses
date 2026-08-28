#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define FR4_DEFAULT_FLEX_STRENGTH_MPA  380.0
#define FR4_DEFAULT_YOUNG_MODULUS_MPA 22000.0
#define FR4_DEFAULT_SHEAR_STRENGTH_MPA  75.0

typedef struct {
    double length_mm;
    double width_mm;
    double thickness_mm;
} PcbDimensions;

typedef struct {
    double max_length_mm;
    double max_width_mm;
    double rail_width_mm;
    double route_width_mm;
} PanelConstraints;

typedef struct {
    double tab_width_mm;
    double hole_diameter_mm;
    double hole_pitch_mm;
    int hole_count;
    double inset_mm;
    double lever_arm_mm;
} BreakawayTabConfig;

typedef enum {
    MLCC_0402 = 0,
    MLCC_0603,
    MLCC_0805,
    MLCC_1206,
    BGA_FINE_PITCH
} ComponentSensitivity;

typedef struct {
    int count_x;
    int count_y;
    int total_boards;
    double actual_length_mm;
    double actual_width_mm;
    double utilization_pct;
    bool is_rotated;
} PanelLayoutResult;

typedef struct {
    double solid_width_net_mm;
    double net_area_mm2;
    double section_modulus_mm3;
    double breaking_moment_n_mm;
    double breaking_force_n;
    double shear_force_n;
    double stress_concentration_kt;
    double safe_distance_mlcc0402_mm;
    double safe_distance_mlcc0805_mm;
    double safe_distance_mlcc1206_mm;
} TabMechanicalResult;

static double get_component_strain_limit(ComponentSensitivity comp) {
    switch (comp) {
        case MLCC_0402:       return 1000.0e-6;
        case MLCC_0603:       return 750.0e-6;
        case MLCC_0805:       return 500.0e-6;
        case MLCC_1206:       return 350.0e-6;
        case BGA_FINE_PITCH:  return 300.0e-6;
        default:              return 500.0e-6;
    }
}

static double calculate_peterson_kt(double d_hole, double pitch) {
    if (pitch <= 0.0 || d_hole <= 0.0) return 3.0;
    double ratio = d_hole / pitch;
    if (ratio > 0.9) ratio = 0.9;
    return 3.0 - 3.13 * ratio + 3.66 * (ratio * ratio) - 1.53 * (ratio * ratio * ratio);
}

static PanelLayoutResult optimize_panel_layout(const PcbDimensions* board, const PanelConstraints* panel) {
    PanelLayoutResult best = {0};

    // Варіант 1: Пряма орієнтація (0 deg)
    double avail_l1 = panel->max_length_mm - 2.0 * panel->rail_width_mm + panel->route_width_mm;
    double avail_w1 = panel->max_width_mm  - 2.0 * panel->rail_width_mm + panel->route_width_mm;

    int nx1 = (int)floor(avail_l1 / (board->length_mm + panel->route_width_mm));
    int ny1 = (int)floor(avail_w1 / (board->width_mm  + panel->route_width_mm));
    int total1 = (nx1 > 0 && ny1 > 0) ? (nx1 * ny1) : 0;

    double len1 = (nx1 > 0) ? (nx1 * board->length_mm + (nx1 - 1) * panel->route_width_mm + 2.0 * panel->rail_width_mm) : 0.0;
    double wid1 = (ny1 > 0) ? (ny1 * board->width_mm  + (ny1 - 1) * panel->route_width_mm + 2.0 * panel->rail_width_mm) : 0.0;
    double util1 = (len1 > 0.0 && wid1 > 0.0) ? ((total1 * board->length_mm * board->width_mm) / (len1 * wid1) * 100.0) : 0.0;

    // Варіант 2: Розвернута орієнтація (90 deg)
    int nx2 = (int)floor(avail_l1 / (board->width_mm  + panel->route_width_mm));
    int ny2 = (int)floor(avail_w1 / (board->length_mm + panel->route_width_mm));
    int total2 = (nx2 > 0 && ny2 > 0) ? (nx2 * ny2) : 0;

    double len2 = (nx2 > 0) ? (nx2 * board->width_mm  + (nx2 - 1) * panel->route_width_mm + 2.0 * panel->rail_width_mm) : 0.0;
    double wid2 = (ny2 > 0) ? (ny2 * board->length_mm + (ny2 - 1) * panel->route_width_mm + 2.0 * panel->rail_width_mm) : 0.0;
    double util2 = (len2 > 0.0 && wid2 > 0.0) ? ((total2 * board->length_mm * board->width_mm) / (len2 * wid2) * 100.0) : 0.0;

    if (total2 > total1 || (total2 == total1 && util2 > util1)) {
        best.count_x = nx2;
        best.count_y = ny2;
        best.total_boards = total2;
        best.actual_length_mm = len2;
        best.actual_width_mm = wid2;
        best.utilization_pct = util2;
        best.is_rotated = true;
    } else {
        best.count_x = nx1;
        best.count_y = ny1;
        best.total_boards = total1;
        best.actual_length_mm = len1;
        best.actual_width_mm = wid1;
        best.utilization_pct = util1;
        best.is_rotated = false;
    }

    return best;
}

static double calculate_component_keepout(double f_break, double lever, double tab_w, double thickness, double strain_limit) {
    if (strain_limit <= 0.0 || thickness <= 0.0 || tab_w <= 0.0) return 0.0;
    double nominal_moment = f_break * lever;
    double numerator = 6.0 * nominal_moment;
    double denominator = tab_w * thickness * thickness * FR4_DEFAULT_YOUNG_MODULUS_MPA * strain_limit;

    if (numerator <= denominator) {
        return 0.5; // Мінімальний технологічний зазор
    }

    double ratio = numerator / denominator;
    double d_keepout = 2.0 * thickness * log(ratio);
    return (d_keepout > 0.5) ? d_keepout : 0.5;
}

static TabMechanicalResult analyze_breakaway_tab(const BreakawayTabConfig* tab, double pcb_thickness) {
    TabMechanicalResult res = {0};

    double hole_subtraction = tab->hole_count * tab->hole_diameter_mm;
    res.solid_width_net_mm = tab->tab_width_mm - hole_subtraction;
    if (res.solid_width_net_mm < 0.2) res.solid_width_net_mm = 0.2;

    res.net_area_mm2 = res.solid_width_net_mm * pcb_thickness;
    res.section_modulus_mm3 = (res.solid_width_net_mm * pcb_thickness * pcb_thickness) / 6.0;

    res.breaking_moment_n_mm = FR4_DEFAULT_FLEX_STRENGTH_MPA * res.section_modulus_mm3;
    double lever = (tab->lever_arm_mm > 1.0) ? tab->lever_arm_mm : 15.0;
    res.breaking_force_n = res.breaking_moment_n_mm / lever;
    res.shear_force_n = FR4_DEFAULT_SHEAR_STRENGTH_MPA * res.net_area_mm2;

    res.stress_concentration_kt = calculate_peterson_kt(tab->hole_diameter_mm, tab->hole_pitch_mm);

    res.safe_distance_mlcc0402_mm = calculate_component_keepout(res.breaking_force_n, lever, tab->tab_width_mm, pcb_thickness, get_component_strain_limit(MLCC_0402));
    res.safe_distance_mlcc0805_mm = calculate_component_keepout(res.breaking_force_n, lever, tab->tab_width_mm, pcb_thickness, get_component_strain_limit(MLCC_0805));
    res.safe_distance_mlcc1206_mm = calculate_component_keepout(res.breaking_force_n, lever, tab->tab_width_mm, pcb_thickness, get_component_strain_limit(MLCC_1206));

    return res;
}

static void print_engineering_report(const PcbDimensions* board, const PanelConstraints* panel,
                                     const BreakawayTabConfig* tab, const PanelLayoutResult* layout,
                                     const TabMechanicalResult* mech) {
    printf("================================================================================\n");
    printf("  ЗВІТ ІНЖЕНЕРНОГО РОЗРАХУНКУ ПАНЕЛІ ТА ПЕРЕМИЧОК ДРУКОВАНИХ ПЛАТ\n");
    printf("================================================================================\n\n");

    printf("1. ВИХІДНІ ДАНІ РОБОЧОЇ ПЛАТИ:\n");
    printf("   Габарити плати (L x W):          %.2f x %.2f мм\n", board->length_mm, board->width_mm);
    printf("   Товщина склотекстоліту (T):       %.2f мм\n", board->thickness_mm);
    printf("   Площа одиничної плати:           %.2f мм²\n\n", board->length_mm * board->width_mm);

    printf("2. ПАРАМЕТРИ ТЕХНОЛОГІЧНОЇ ПАНЕЛІ ТА ОБМЕЖЕННЯ:\n");
    printf("   Ліміт габаритів виробника:       %.2f x %.2f мм\n", panel->max_length_mm, panel->max_width_mm);
    printf("   Ширина технологічних рейок:      %.2f мм\n", panel->rail_width_mm);
    printf("   Ширина паза кінцевої фрези:      %.2f мм\n\n", panel->route_width_mm);

    printf("3. РЕЗУЛЬТАТИ ОПТИМІЗАЦІЇ РОЗКЛАДКИ (2D ARRAY PACKING):\n");
    printf("   Орієнтація плат на панелі:       %s\n", layout->is_rotated ? "Розвернуто на 90°" : "Пряма (0°)");
    printf("   Кількість плат у сітці (Nx x Ny):%d x %d шт.\n", layout->count_x, layout->count_y);
    printf("   Сумарний вихід плат з панелі:    %d шт.\n", layout->total_boards);
    printf("   Фактичні розміри панелі:         %.2f x %.2f мм\n", layout->actual_length_mm, layout->actual_width_mm);
    printf("   Корисне використання міді/FR4:   %.2f %%\n\n", layout->utilization_pct);

    printf("4. МЕХАНІЧНІ ХАРАКТЕРИСТИКИ ПЕРЕМИЧКИ (BREAKAWAY TAB / MOUSE BITES):\n");
    printf("   Повна ширина перемички (W_tab):  %.2f мм\n", tab->tab_width_mm);
    printf("   Конфігурація перфорації:         %d отворів Ø%.2f мм (крок %.2f мм)\n",
           tab->hole_count, tab->hole_diameter_mm, tab->hole_pitch_mm);
    printf("   Чиста залишкова ширина (W_net):  %.2f мм\n", mech->solid_width_net_mm);
    printf("   Осьовий момент опору (Z_net):    %.4f мм³\n", mech->section_modulus_mm3);
    printf("   Коефіцієнт концентрації (Kt):    %.2f (за критерієм Петерсона)\n", mech->stress_concentration_kt);
    printf("   Граничний згинальний момент (M): %.2f Н·мм\n", mech->breaking_moment_n_mm);
    printf("   Зусилля руйнування при вигині:   %.2f Н (%.2f кгс) при плечі %.1f мм\n",
           mech->breaking_force_n, mech->breaking_force_n / 9.80665, tab->lever_arm_mm);
    printf("   Граничне зсувне зусилля (Shear): %.2f Н (%.2f кгс)\n\n",
           mech->shear_force_n, mech->shear_force_n / 9.80665);

    printf("5. ЗОНИ ВІДЧУЖЕННЯ ДЛЯ КОМПОНЕНТІВ ЗА IPC-9704 (STRAIN KEEPOUT):\n");
    printf("   MLCC 0402 (ліміт 1000 µε):        d_keepout >= %.2f мм від лінії злому\n", mech->safe_distance_mlcc0402_mm);
    printf("   MLCC 0805 (ліміт 500 µε):         d_keepout >= %.2f мм від лінії злому\n", mech->safe_distance_mlcc0805_mm);
    printf("   MLCC 1206 / BGA (ліміт 350 µε):   d_keepout >= %.2f мм від лінії злому\n", mech->safe_distance_mlcc1206_mm);
    printf("   Рекомендований заглиб отворів:   %.2f мм всередину контуру плати\n", tab->inset_mm);
    printf("================================================================================\n");
}

int main(int argc, char** argv) {
    PcbDimensions board = {
        .length_mm = 65.0,
        .width_mm = 42.0,
        .thickness_mm = 1.60
    };

    PanelConstraints panel = {
        .max_length_mm = 300.0,
        .max_width_mm = 200.0,
        .rail_width_mm = 7.0,
        .route_width_mm = 2.0
    };

    BreakawayTabConfig tab = {
        .tab_width_mm = 4.0,
        .hole_diameter_mm = 0.60,
        .hole_pitch_mm = 1.00,
        .hole_count = 4,
        .inset_mm = 0.15,
        .lever_arm_mm = 15.0
    };

    if (argc >= 3) {
        board.length_mm = atof(argv[1]);
        board.width_mm = atof(argv[2]);
    }
    if (argc >= 4) {
        board.thickness_mm = atof(argv[3]);
    }

    PanelLayoutResult layout = optimize_panel_layout(&board, &panel);
    TabMechanicalResult mech = analyze_breakaway_tab(&tab, board.thickness_mm);

    print_engineering_report(&board, &panel, &tab, &layout, &mech);

    return 0;
}
