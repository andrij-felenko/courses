#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Перелік підтримуваних типів виводів компонентів за IPC-7351 */
typedef enum {
    LEAD_GULL_WING = 0,   /* SOIC, TSSOP, QFP */
    LEAD_FLAT_NO_LEAD,    /* QFN, DFN */
    LEAD_RECTANGULAR_CHIP,/* 0402, 0603, 0805 */
    LEAD_J_LEAD,          /* PLCC, SOJ */
    LEAD_BGA              /* Ball Grid Array */
} LeadType;

/* Рівні густини монтажу за IPC-7351 */
typedef enum {
    DENSITY_LEVEL_A_MOST = 0, /* Максимальний (аерокосмічна, високонадійна техніка) */
    DENSITY_LEVEL_B_NOMINAL,  /* Номінальний (стандартна промислова електроніка) */
    DENSITY_LEVEL_C_LEAST     /* Мінімальний (ультращільні портативні прилади) */
} DensityLevel;

/* Геометричні розміри компонента з допуском min/max (у мм) */
typedef struct {
    double l_min, l_max; /* Повний габарит по зовнішніх краях виводів */
    double s_min, s_max; /* Внутрішній просвіт між виводами */
    double w_min, w_max; /* Ширина виводу */
    double t_min, t_max; /* Довжина стопи або контактної площадки виводу */
    double pitch;        /* Крок між виводами */
} ComponentDimensions;

/* Технологічні допуски виробництва (у мм) */
typedef struct {
    double fabrication_f; /* Похибка травлення плати F (типово 0.10 або 0.05 мм) */
    double placement_p;   /* Похибка встановлення Pick-and-Place P (типово 0.05 мм) */
    double mask_expansion;/* Розширення вікна маски на сторону (типово 0.05 мм) */
    double min_mask_dam;  /* Мінімальний технологічний місток маски (типово 0.075 мм) */
} ProcessTolerances;

/* Результуючі розміри контактної площадки та зони дворика */
typedef struct {
    double z_max;              /* Зовнішній габарит між площадками */
    double g_min;              /* Внутрішній просвіт між площадками */
    double x_max;              /* Ширина контактної площадки */
    double pad_length_y;       /* Індивідуальна довжина площадки Y */
    double center_dist_c;      /* Відстань між центрами протилежних площадок */
    double courtyard_x;        /* Габарит дворика по осі X */
    double courtyard_y;        /* Габарит дворика по осі Y */
    double actual_mask_dam;    /* Фактичний місток маски між сусідніми падами */
    bool is_mask_dam_ok;       /* Прапорець достатності містка маски */
    bool is_nsmd_recommended;  /* Рекомендація конфігурації NSMD */
} LandPatternResult;

/* Структура для розрахунку вікон трафарету під тепловий пад */
typedef struct {
    int matrix_cols;           /* Кількість вікон по горизонталі */
    int matrix_rows;           /* Кількість вікон по вертикалі */
    double window_width;       /* Ширина одного вікна трафарету */
    double window_length;      /* Довжина одного вікна трафарету */
    double total_paste_area;   /* Сумарна площа пасти */
    double coverage_ratio;     /* Фактичний відсоток покриття міді пастою */
} ThermalPadStencilResult;

/* Табличні коефіцієнти галтелей IPC-7351 */
typedef struct {
    double jt; /* Носок */
    double jh; /* П'ята */
    double js; /* Бік */
    double excess; /* Запас дворика */
} FilletGoals;

static FilletGoals get_fillet_goals(LeadType type, DensityLevel level) {
    FilletGoals g = {0};
    switch (type) {
        case LEAD_GULL_WING:
            if (level == DENSITY_LEVEL_A_MOST) { g.jt = 0.55; g.jh = 0.45; g.js = 0.05; g.excess = 0.50; }
            else if (level == DENSITY_LEVEL_B_NOMINAL) { g.jt = 0.35; g.jh = 0.35; g.js = 0.03; g.excess = 0.25; }
            else { g.jt = 0.15; g.jh = 0.25; g.js = 0.01; g.excess = 0.10; }
            break;
        case LEAD_FLAT_NO_LEAD:
            if (level == DENSITY_LEVEL_A_MOST) { g.jt = 0.30; g.jh = 0.00; g.js = 0.05; g.excess = 0.50; }
            else if (level == DENSITY_LEVEL_B_NOMINAL) { g.jt = 0.20; g.jh = 0.00; g.js = 0.00; g.excess = 0.25; }
            else { g.jt = 0.10; g.jh = 0.00; g.js = -0.04; g.excess = 0.10; }
            break;
        case LEAD_RECTANGULAR_CHIP:
            if (level == DENSITY_LEVEL_A_MOST) { g.jt = 0.40; g.jh = 0.00; g.js = 0.10; g.excess = 0.50; }
            else if (level == DENSITY_LEVEL_B_NOMINAL) { g.jt = 0.30; g.jh = 0.00; g.js = 0.05; g.excess = 0.25; }
            else { g.jt = 0.15; g.jh = 0.00; g.js = 0.00; g.excess = 0.10; }
            break;
        case LEAD_J_LEAD:
            if (level == DENSITY_LEVEL_A_MOST) { g.jt = 0.70; g.jh = 0.35; g.js = 0.10; g.excess = 0.50; }
            else if (level == DENSITY_LEVEL_B_NOMINAL) { g.jt = 0.50; g.jh = 0.25; g.js = 0.05; g.excess = 0.25; }
            else { g.jt = 0.30; g.jh = 0.15; g.js = 0.00; g.excess = 0.10; }
            break;
        default:
            g.jt = 0.25; g.jh = 0.25; g.js = 0.03; g.excess = 0.25;
            break;
    }
    return g;
}

LandPatternResult calculate_ipc7351_land(const ComponentDimensions *comp,
                                        LeadType lead_type,
                                        DensityLevel level,
                                        const ProcessTolerances *proc) {
    LandPatternResult res = {0};
    FilletGoals f = get_fillet_goals(lead_type, level);

    /* Розрахунок допусків компонента */
    double c_l = comp->l_max - comp->l_min;
    double c_s = comp->s_max - comp->s_min;
    double c_w = comp->w_max - comp->w_min;

    /* Розрахунок сумарних статистичних допусків за методом RSS */
    double f2_p2 = (proc->fabrication_f * proc->fabrication_f) + 
                   (proc->placement_p * proc->placement_p);
    double t_l = sqrt((c_l * c_l) + f2_p2);
    double t_s = sqrt((c_s * c_s) + f2_p2);
    double t_w = sqrt((c_w * c_w) + f2_p2);

    /* Розрахунок габаритних меж площадок */
    res.z_max = comp->l_min + (2.0 * f.jt) + t_l;
    res.g_min = comp->s_max - (2.0 * f.jh) - t_s;
    res.x_max = comp->w_min + (2.0 * f.js) + t_w;

    /* Коригування довжини площадки Y та міжцентрової відстані */
    res.pad_length_y = (res.z_max - res.g_min) / 2.0;
    res.center_dist_c = (res.z_max + res.g_min) / 2.0;

    /* Габарити дворика Courtyard */
    res.courtyard_x = res.z_max + (2.0 * f.excess);
    res.courtyard_y = comp->w_max + (2.0 * f.excess);

    /* Перевірка містка паяльної маски */
    if (comp->pitch > 0.0) {
        double copper_clearance = comp->pitch - res.x_max;
        res.actual_mask_dam = copper_clearance - (2.0 * proc->mask_expansion);
        res.is_mask_dam_ok = (res.actual_mask_dam >= proc->min_mask_dam);
        res.is_nsmd_recommended = (comp->pitch <= 0.50);
    } else {
        res.actual_mask_dam = 0.0;
        res.is_mask_dam_ok = true;
        res.is_nsmd_recommended = false;
    }

    return res;
}

ThermalPadStencilResult calculate_thermal_pad_stencil(double pad_w, double pad_h,
                                                      int cols, int rows,
                                                      double bridge_width,
                                                      double target_coverage_ratio) {
    ThermalPadStencilResult res = {0};
    res.matrix_cols = cols;
    res.matrix_rows = rows;

    double total_pad_area = pad_w * pad_h;
    
    /* Розрахунок розмірів одного вікна з урахуванням захисних перемичок */
    res.window_width = (pad_w - ((cols - 1) * bridge_width)) / cols;
    res.window_length = (pad_h - ((rows - 1) * bridge_width)) / rows;
    
    res.total_paste_area = (res.window_width * res.window_length) * (cols * rows);
    res.coverage_ratio = res.total_paste_area / total_pad_area;

    return res;
}

int main(void) {
    /* Базові технологічні допуски плати 4-го класу точності */
    ProcessTolerances proc = {
        .fabrication_f = 0.10,
        .placement_p = 0.05,
        .mask_expansion = 0.05,
        .min_mask_dam = 0.075
    };

    printf("=== IPC-7351 LAND PATTERN CALCULATOR VERIFICATION ===\n\n");

    /* Тест 1: Мікросхема SOIC-8 (Gull-Wing Leads, Pitch = 1.27 mm) */
    ComponentDimensions soic8 = {
        .l_min = 5.80, .l_max = 6.20,
        .s_min = 3.80, .s_max = 4.00,
        .w_min = 0.33, .w_max = 0.51,
        .t_min = 0.40, .t_max = 0.90,
        .pitch = 1.27
    };
    LandPatternResult r_soic = calculate_ipc7351_land(&soic8, LEAD_GULL_WING, DENSITY_LEVEL_B_NOMINAL, &proc);
    printf("[TEST 1: SOIC-8 Gull-Wing]\n");
    printf("  Z_max = %.3f mm, G_min = %.3f mm, X_max = %.3f mm\n", r_soic.z_max, r_soic.g_min, r_soic.x_max);
    printf("  Контактна площадка Y x X: %.2f x %.2f mm (C_land = %.2f mm)\n", r_soic.pad_length_y, r_soic.x_max, r_soic.center_dist_c);
    printf("  Місток маски: %.3f mm (Статус: %s)\n\n", r_soic.actual_mask_dam, r_soic.is_mask_dam_ok ? "OK" : "ПОМИЛКА");

    /* Тест 2: Мікроконтролер QFN-32 (Pitch = 0.50 mm) з тепловим падом */
    ComponentDimensions qfn32 = {
        .l_min = 4.90, .l_max = 5.10,
        .s_min = 4.10, .s_max = 4.30,
        .w_min = 0.20, .w_max = 0.30,
        .t_min = 0.30, .t_max = 0.50,
        .pitch = 0.50
    };
    LandPatternResult r_qfn = calculate_ipc7351_land(&qfn32, LEAD_FLAT_NO_LEAD, DENSITY_LEVEL_B_NOMINAL, &proc);
    printf("[TEST 2: QFN-32 Flat No-Lead (Pitch 0.50 mm)]\n");
    printf("  Контактна площадка Y x X: %.2f x %.2f mm\n", r_qfn.pad_length_y, r_qfn.x_max);
    printf("  Місток маски: %.3f mm (Рекомендація: %s)\n", r_qfn.actual_mask_dam, r_qfn.is_nsmd_recommended ? "NSMD" : "SMD");

    /* Розрахунок матриці 2x2 вікон під тепловий пад 3.20 x 3.20 мм */
    ThermalPadStencilResult st_qfn = calculate_thermal_pad_stencil(3.20, 3.20, 2, 2, 0.25, 0.60);
    printf("  Тепловий трафарет (2x2 вікна): Вікно %.2f x %.2f mm, Покриття: %.1f%%\n\n",
           st_qfn.window_width, st_qfn.window_length, st_qfn.coverage_ratio * 100.0);

    /* Тест 3: Керамічний конденсатор 0603 */
    ComponentDimensions cap0603 = {
        .l_min = 1.45, .l_max = 1.75,
        .s_min = 0.70, .s_max = 0.90,
        .w_min = 0.65, .w_max = 0.95,
        .t_min = 0.20, .t_max = 0.50,
        .pitch = 0.0
    };
    LandPatternResult r_cap = calculate_ipc7351_land(&cap0603, LEAD_RECTANGULAR_CHIP, DENSITY_LEVEL_B_NOMINAL, &proc);
    printf("[TEST 3: Chip 0603 Rectangular]\n");
    printf("  Контактна площадка Y x X: %.2f x %.2f mm (Просвіт G_min = %.2f mm)\n",
           r_cap.pad_length_y, r_cap.x_max, r_cap.g_min);

    return 0;
}
