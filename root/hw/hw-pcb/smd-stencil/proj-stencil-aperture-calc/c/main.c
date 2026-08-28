#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define M_PI_CONST 3.14159265358979323846

typedef enum {
    PAD_RECTANGULAR,
    PAD_CIRCULAR,
    PAD_ROUNDED_RECT,
    PAD_OBROUND,
    PAD_HOME_PLATE,
    PAD_THERMAL_EXPOSED,
    PAD_THROUGH_HOLE_THR
} PadType;

typedef struct {
    char component_name[32];
    char footprint_name[32];
    PadType pad_type;
    double width_mm;          /* Ширина або діаметр */
    double length_mm;         /* Довжина (0 для круглих) */
    double corner_radius_mm;  /* Радіус скруглення кутів */
    double home_plate_cut_mm; /* Довжина скосу Home-Plate */
    /* Параметри для Through-Hole Reflow */
    double pcb_thickness_mm;
    double hole_diameter_mm;
    double pin_diameter_mm;
} ComponentPad;

typedef struct {
    double foil_thickness_mm; /* Товщина фольги трафарету T (типово 0.10 - 0.15 мм) */
    bool has_nano_coating;    /* Наявність гідрофобного нанопокриття */
    double target_thermal_coverage; /* Цільовий відсоток покриття теплових падів (0.50 - 0.70) */
    double min_web_width_mm;  /* Мінімальна ширина сталевої перемички (0.25 - 0.35 мм) */
} StencilConfig;

typedef struct {
    double area_pad_mm2;
    double area_walls_mm2;
    double theoretical_volume_mm3;
    double area_ratio;
    double aspect_ratio;
    double transfer_efficiency;
    double expected_volume_mm3;
    bool pass_area_ratio;
    bool pass_aspect_ratio;
    /* Дані оптимізації редукції */
    double opt_width_mm;
    double opt_length_mm;
    double reduction_percent;
    /* Дані віконної решітки для теплових площадок */
    int grid_nx;
    int grid_ny;
    double window_width_mm;
    double window_length_mm;
    double actual_coverage_percent;
    /* Дані Through-Hole Reflow */
    double thr_paste_required_mm3;
    double thr_overprint_size_mm;
} ApertureEvaluation;

/* Розрахунок критеріїв IPC-7525 для прямокутної апертури */
static void evaluate_rectangular(const ComponentPad* pad, const StencilConfig* cfg, ApertureEvaluation* eval) {
    double w = pad->width_mm;
    double l = pad->length_mm;
    double t = cfg->foil_thickness_mm;

    eval->area_pad_mm2 = w * l;
    eval->area_walls_mm2 = 2.0 * (w + l) * t;
    eval->theoretical_volume_mm3 = eval->area_pad_mm2 * t;

    eval->area_ratio = eval->area_pad_mm2 / eval->area_walls_mm2;
    eval->aspect_ratio = (w < l ? w : l) / t;

    double ar_threshold = cfg->has_nano_coating ? 0.55 : 0.66;
    eval->pass_area_ratio = (eval->area_ratio >= ar_threshold);
    eval->pass_aspect_ratio = (eval->aspect_ratio >= 1.50);

    /* Модель Transfer Efficiency */
    double k = cfg->has_nano_coating ? 14.0 : 11.0;
    double ar0 = cfg->has_nano_coating ? 0.45 : 0.55;
    eval->transfer_efficiency = 0.96 / (1.0 + exp(-k * (eval->area_ratio - ar0)));
    eval->expected_volume_mm3 = eval->theoretical_volume_mm3 * eval->transfer_efficiency;

    /* Оптимізація редукції розмірів: зменшення на 10-15% за умови збереження AR >= threshold */
    double opt_w = w * 0.90;
    double opt_l = l * 0.90;
    double opt_ar = (opt_w * opt_l) / (2.0 * (opt_w + opt_l) * t);

    if (opt_ar >= ar_threshold) {
        eval->opt_width_mm = opt_w;
        eval->opt_length_mm = opt_l;
        eval->reduction_percent = 19.0; /* 1.0 - (0.9 * 0.9) */
    } else {
        eval->opt_width_mm = w;
        eval->opt_length_mm = l;
        eval->reduction_percent = 0.0;
    }
}

/* Розрахунок для круглої апертури BGA / CSP */
static void evaluate_circular(const ComponentPad* pad, const StencilConfig* cfg, ApertureEvaluation* eval) {
    double d = pad->width_mm;
    double t = cfg->foil_thickness_mm;

    eval->area_pad_mm2 = (M_PI_CONST * d * d) / 4.0;
    eval->area_walls_mm2 = M_PI_CONST * d * t;
    eval->theoretical_volume_mm3 = eval->area_pad_mm2 * t;

    eval->area_ratio = d / (4.0 * t);
    eval->aspect_ratio = d / t;

    double ar_threshold = cfg->has_nano_coating ? 0.55 : 0.66;
    eval->pass_area_ratio = (eval->area_ratio >= ar_threshold);
    eval->pass_aspect_ratio = (eval->aspect_ratio >= 1.50);

    double k = cfg->has_nano_coating ? 14.0 : 11.0;
    double ar0 = cfg->has_nano_coating ? 0.45 : 0.55;
    eval->transfer_efficiency = 0.96 / (1.0 + exp(-k * (eval->area_ratio - ar0)));
    eval->expected_volume_mm3 = eval->theoretical_volume_mm3 * eval->transfer_efficiency;

    eval->opt_width_mm = d;
    eval->opt_length_mm = d;
    eval->reduction_percent = 0.0;
}

/* Розрахунок для прямокутника із скругленими кутами */
static void evaluate_rounded_rect(const ComponentPad* pad, const StencilConfig* cfg, ApertureEvaluation* eval) {
    double w = pad->width_mm;
    double l = pad->length_mm;
    double r = pad->corner_radius_mm;
    double t = cfg->foil_thickness_mm;

    if (r > w / 2.0) r = w / 2.0;
    if (r > l / 2.0) r = l / 2.0;

    eval->area_pad_mm2 = (w * l) - (4.0 - M_PI_CONST) * (r * r);
    double perimeter = 2.0 * (w + l) - (8.0 - 2.0 * M_PI_CONST) * r;
    eval->area_walls_mm2 = perimeter * t;
    eval->theoretical_volume_mm3 = eval->area_pad_mm2 * t;

    eval->area_ratio = eval->area_pad_mm2 / eval->area_walls_mm2;
    eval->aspect_ratio = (w < l ? w : l) / t;

    double ar_threshold = cfg->has_nano_coating ? 0.55 : 0.66;
    eval->pass_area_ratio = (eval->area_ratio >= ar_threshold);
    eval->pass_aspect_ratio = (eval->aspect_ratio >= 1.50);

    double k = cfg->has_nano_coating ? 14.0 : 11.0;
    double ar0 = cfg->has_nano_coating ? 0.45 : 0.55;
    eval->transfer_efficiency = 0.97 / (1.0 + exp(-k * (eval->area_ratio - ar0)));
    eval->expected_volume_mm3 = eval->theoretical_volume_mm3 * eval->transfer_efficiency;

    eval->opt_width_mm = w;
    eval->opt_length_mm = l;
    eval->reduction_percent = 0.0;
}

/* Розрахунок для форми Home-Plate */
static void evaluate_home_plate(const ComponentPad* pad, const StencilConfig* cfg, ApertureEvaluation* eval) {
    double w = pad->width_mm;
    double l = pad->length_mm;
    double c = pad->home_plate_cut_mm > 0.0 ? pad->home_plate_cut_mm : w * 0.35;
    double t = cfg->foil_thickness_mm;

    if (c >= l) c = l * 0.5;

    eval->area_pad_mm2 = (w * l) - (0.5 * w * c);
    double hypotenuse = sqrt(c * c + (w / 2.0) * (w / 2.0));
    double perimeter = 2.0 * (l - c) + w + 2.0 * hypotenuse;
    eval->area_walls_mm2 = perimeter * t;
    eval->theoretical_volume_mm3 = eval->area_pad_mm2 * t;

    eval->area_ratio = eval->area_pad_mm2 / eval->area_walls_mm2;
    eval->aspect_ratio = (w < l ? w : l) / t;

    double ar_threshold = cfg->has_nano_coating ? 0.55 : 0.66;
    eval->pass_area_ratio = (eval->area_ratio >= ar_threshold);
    eval->pass_aspect_ratio = (eval->aspect_ratio >= 1.50);

    double k = cfg->has_nano_coating ? 14.0 : 11.0;
    double ar0 = cfg->has_nano_coating ? 0.45 : 0.55;
    eval->transfer_efficiency = 0.96 / (1.0 + exp(-k * (eval->area_ratio - ar0)));
    eval->expected_volume_mm3 = eval->theoretical_volume_mm3 * eval->transfer_efficiency;

    eval->opt_width_mm = w;
    eval->opt_length_mm = l;
    eval->reduction_percent = (0.5 * w * c) / (w * l) * 100.0;
}

/* Розрахунок віконної решітки для великих теплових майданчиків QFN/DFN/PowerPAK */
static void evaluate_thermal_pad(const ComponentPad* pad, const StencilConfig* cfg, ApertureEvaluation* eval) {
    double w = pad->width_mm;
    double l = pad->length_mm;
    double t = cfg->foil_thickness_mm;
    double cov = cfg->target_thermal_coverage;
    double web = cfg->min_web_width_mm;

    eval->area_pad_mm2 = w * l;
    eval->theoretical_volume_mm3 = eval->area_pad_mm2 * t;

    /* Вибір розмірності сітки: крок вікон не більше 1.5 мм */
    int nx = (int)floor(w / 1.5);
    int ny = (int)floor(l / 1.5);
    if (nx < 2) nx = 2;
    if (ny < 2) ny = 2;
    if (nx > 5) nx = 5;
    if (ny > 5) ny = 5;

    eval->grid_nx = nx;
    eval->grid_ny = ny;

    /* Розрахунок розмірів кожного окремого вікна для забезпечення цільового покриття cov */
    double target_window_area_sum = eval->area_pad_mm2 * cov;
    double single_win_area = target_window_area_sum / (double)(nx * ny);

    /* Пропорційне масштабування ширини та довжини вікна */
    double aspect = w / l;
    double win_l = sqrt(single_win_area / aspect);
    double win_w = win_l * aspect;

    /* Перевірка обмеження перемичок */
    double max_allowed_w = (w - (nx - 1) * web) / (double)nx;
    double max_allowed_l = (l - (ny - 1) * web) / (double)ny;

    if (win_w > max_allowed_w) win_w = max_allowed_w;
    if (win_l > max_allowed_l) win_l = max_allowed_l;

    eval->window_width_mm = win_w;
    eval->window_length_mm = win_l;

    double actual_paste_area = (double)(nx * ny) * (win_w * win_l);
    eval->actual_coverage_percent = (actual_paste_area / eval->area_pad_mm2) * 100.0;

    /* Розрахунок AR для одного окремого вікна */
    double a_win_pad = win_w * win_l;
    double a_win_walls = 2.0 * (win_w + win_l) * t;
    eval->area_ratio = a_win_pad / a_win_walls;
    eval->aspect_ratio = (win_w < win_l ? win_w : win_l) / t;

    double ar_threshold = cfg->has_nano_coating ? 0.55 : 0.66;
    eval->pass_area_ratio = (eval->area_ratio >= ar_threshold);
    eval->pass_aspect_ratio = (eval->aspect_ratio >= 1.50);

    eval->transfer_efficiency = 0.95;
    eval->expected_volume_mm3 = actual_paste_area * t * eval->transfer_efficiency;
}

/* Розрахунок об'єму пасти для технології Through-Hole Reflow (Pin-in-Paste) */
static void evaluate_thr_pin(const ComponentPad* pad, const StencilConfig* cfg, ApertureEvaluation* eval) {
    double d_hole = pad->hole_diameter_mm;
    double d_pin = pad->pin_diameter_mm;
    double h_pcb = pad->pcb_thickness_mm;
    double t_foil = cfg->foil_thickness_mm;

    double v_hole = M_PI_CONST * pow(d_hole / 2.0, 2.0) * h_pcb;
    double v_pin = M_PI_CONST * pow(d_pin / 2.0, 2.0) * h_pcb;
    double v_gap = v_hole - v_pin;

    /* Галтелі зверху та знизу за IPC-A-610 Class 3 */
    double v_fillet_top = 0.25 * v_gap;
    double v_fillet_bot = 0.25 * v_gap;
    double v_solder_target = v_gap + v_fillet_top + v_fillet_bot;

    /* Враховуємо 50% вміст металу в пасті за об'ємом */
    eval->thr_paste_required_mm3 = 2.0 * v_solder_target;

    /* Розрахунок розміру прямокутного оверпринту */
    double required_aperture_area = eval->thr_paste_required_mm3 / t_foil;
    eval->thr_overprint_size_mm = sqrt(required_aperture_area);

    eval->area_pad_mm2 = required_aperture_area;
    eval->area_walls_mm2 = 4.0 * eval->thr_overprint_size_mm * t_foil;
    eval->area_ratio = eval->area_pad_mm2 / eval->area_walls_mm2;
    eval->aspect_ratio = eval->thr_overprint_size_mm / t_foil;
    eval->pass_area_ratio = true;
    eval->pass_aspect_ratio = true;
    eval->transfer_efficiency = 0.95;
    eval->expected_volume_mm3 = eval->thr_paste_required_mm3 * 0.95;
}

void evaluate_component_pad(const ComponentPad* pad, const StencilConfig* cfg, ApertureEvaluation* eval) {
    memset(eval, 0, sizeof(ApertureEvaluation));
    switch (pad->pad_type) {
        case PAD_RECTANGULAR:
            evaluate_rectangular(pad, cfg, eval);
            break;
        case PAD_CIRCULAR:
            evaluate_circular(pad, cfg, eval);
            break;
        case PAD_ROUNDED_RECT:
        case PAD_OBROUND:
            evaluate_rounded_rect(pad, cfg, eval);
            break;
        case PAD_HOME_PLATE:
            evaluate_home_plate(pad, cfg, eval);
            break;
        case PAD_THERMAL_EXPOSED:
            evaluate_thermal_pad(pad, cfg, eval);
            break;
        case PAD_THROUGH_HOLE_THR:
            evaluate_thr_pin(pad, cfg, eval);
            break;
    }
}

void print_report(const ComponentPad pads[], int count, const StencilConfig* cfg) {
    printf("========================================================================================================\n");
    printf("                  ЗВІТ ВАЛІДАЦІЇ ТРАФАРЕТНИХ АПЕРТУР ЗА СТАНДАРТОМ IPC-7525\n");
    printf("  Параметри фольги: Товщина = %.3f мм (%d мкм), Нанопокриття: %s\n", 
           cfg->foil_thickness_mm, (int)(cfg->foil_thickness_mm * 1000.0),
           cfg->has_nano_coating ? "ТАК (Поріг AR >= 0.55)" : "НІ (Поріг AR >= 0.66)");
    printf("========================================================================================================\n");
    printf("%-10s %-12s %-8s %-8s %-7s %-7s %-7s %-8s %-12s %-12s\n",
           "Компонент", "Корпус", "Розмір", "AR", "AR-Стан", "AS", "AS-Стан", "TE %%", "Очік. V(нл)", "Оптимізація");
    printf("--------------------------------------------------------------------------------------------------------\n");

    for (int i = 0; i < count; i++) {
        ApertureEvaluation ev;
        evaluate_component_pad(&pads[i], cfg, &ev);

        char dim_buf[32];
        if (pads[i].pad_type == PAD_CIRCULAR) {
            snprintf(dim_buf, sizeof(dim_buf), "D%.2f", pads[i].width_mm);
        } else {
            snprintf(dim_buf, sizeof(dim_buf), "%.2fx%.2f", pads[i].width_mm, pads[i].length_mm);
        }

        char opt_buf[32];
        if (pads[i].pad_type == PAD_THERMAL_EXPOSED) {
            snprintf(opt_buf, sizeof(opt_buf), "Grid %dx%d (%.0f%%)", 
                     ev.grid_nx, ev.grid_ny, ev.actual_coverage_percent);
        } else if (pads[i].pad_type == PAD_THROUGH_HOLE_THR) {
            snprintf(opt_buf, sizeof(opt_buf), "Overprint %.2f", ev.thr_overprint_size_mm);
        } else if (pads[i].pad_type == PAD_HOME_PLATE) {
            snprintf(opt_buf, sizeof(opt_buf), "HomePlate -%.0f%%", ev.reduction_percent);
        } else if (ev.reduction_percent > 0.1) {
            snprintf(opt_buf, sizeof(opt_buf), "-%.0f%% Редукція", ev.reduction_percent);
        } else {
            snprintf(opt_buf, sizeof(opt_buf), "1:1 Без змін");
        }

        printf("%-10s %-12s %-8s %-8.3f %-7s %-7.2f %-7s %-7.1f%% %-12.3f %-12s\n",
               pads[i].component_name,
               pads[i].footprint_name,
               dim_buf,
               ev.area_ratio,
               ev.pass_area_ratio ? "PASS" : "FAIL",
               ev.aspect_ratio,
               ev.pass_aspect_ratio ? "PASS" : "FAIL",
               ev.transfer_efficiency * 100.0,
               ev.expected_volume_mm3 * 1000.0, /* 1 мм3 = 1000 нл */
               opt_buf);
    }
    printf("========================================================================================================\n");
}

int main(void) {
    /* Конфігурація друкованої плати та трафарету */
    StencilConfig cfg_standard = {
        .foil_thickness_mm = 0.120, /* 120 мкм фольга */
        .has_nano_coating = false,
        .target_thermal_coverage = 0.60,
        .min_web_width_mm = 0.30
    };

    StencilConfig cfg_nano = {
        .foil_thickness_mm = 0.120,
        .has_nano_coating = true,
        .target_thermal_coverage = 0.60,
        .min_web_width_mm = 0.30
    };

    /* Набір тестових посадкових місць друкованої плати */
    ComponentPad bom_pads[] = {
        {
            .component_name = "C101",
            .footprint_name = "C_0201",
            .pad_type = PAD_RECTANGULAR,
            .width_mm = 0.30,
            .length_mm = 0.30,
            .corner_radius_mm = 0.05
        },
        {
            .component_name = "R105",
            .footprint_name = "R_0402",
            .pad_type = PAD_ROUNDED_RECT,
            .width_mm = 0.50,
            .length_mm = 0.55,
            .corner_radius_mm = 0.10
        },
        {
            .component_name = "C106",
            .footprint_name = "C_0603",
            .pad_type = PAD_HOME_PLATE,
            .width_mm = 0.80,
            .length_mm = 0.90,
            .home_plate_cut_mm = 0.30
        },
        {
            .component_name = "U2",
            .footprint_name = "QFP-48_P0.5",
            .pad_type = PAD_RECTANGULAR,
            .width_mm = 0.25,
            .length_mm = 1.20,
            .corner_radius_mm = 0.05
        },
        {
            .component_name = "U1_Signals",
            .footprint_name = "QFN-32_P0.4",
            .pad_type = PAD_RECTANGULAR,
            .width_mm = 0.20,
            .length_mm = 0.80,
            .corner_radius_mm = 0.04
        },
        {
            .component_name = "U1_Thermal",
            .footprint_name = "QFN-32_EP",
            .pad_type = PAD_THERMAL_EXPOSED,
            .width_mm = 4.50,
            .length_mm = 4.50,
            .corner_radius_mm = 0.0
        },
        {
            .component_name = "U3_BGA",
            .footprint_name = "BGA-256_P0.5",
            .pad_type = PAD_CIRCULAR,
            .width_mm = 0.28,
            .length_mm = 0.0,
            .corner_radius_mm = 0.0
        },
        {
            .component_name = "J1_Power",
            .footprint_name = "THR_HDR_1x2",
            .pad_type = PAD_THROUGH_HOLE_THR,
            .width_mm = 2.00,
            .length_mm = 2.00,
            .pcb_thickness_mm = 1.60,
            .hole_diameter_mm = 1.10,
            .pin_diameter_mm = 0.64
        }
    };

    int count = sizeof(bom_pads) / sizeof(bom_pads[0]);

    printf("\n[ТЕСТ 1: СТАНДАРТНИЙ ТРАФАРЕТ БЕЗ ПОКРИТТЯ]\n");
    print_report(bom_pads, count, &cfg_standard);

    printf("\n[ТЕСТ 2: ТРАФАРЕТ З ГІДРОФОБНИМ НАНОПОКРИТТЯМ NANO-COATING]\n");
    print_report(bom_pads, count, &cfg_nano);

    return 0;
}
