#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Технологічні обмеження фабрики (усі розміри в міліметрах) */
typedef struct {
    double min_trace_width;       /* Мінімальна ширина доріжки */
    double min_trace_space;       /* Мінімальний зазор між доріжками */
    double min_drill_dia;         /* Мінімальний діаметр свердла */
    double min_annular_ring;      /* Мінімальний поясок металізації */
    double min_mask_dam;          /* Мінімальний місток паяльної маски */
    double mask_expansion;        /* Стандартне розширення маски */
    double min_edge_milling;      /* Зазор до фрезерованого краю */
    double min_edge_vcut;         /* Зазор до осі скрайбування (V-cut) */
} pcb_capabilities_t;

/* Геометричний елемент топології для перевірки */
typedef struct {
    double trace_width;
    double trace_space;
    double pad_dia;
    double drill_dia;
    double pad_to_pad_copper_space;
    double copper_to_edge_dist;
    bool is_vcut_edge;
} pcb_feature_t;

/* Результат DFM-перевірки */
typedef struct {
    bool passed;
    int violation_count;
} dfm_result_t;

/* Перевірка топології на відповідність обмеженням фабрики */
dfm_result_t validate_pcb_features(const pcb_capabilities_t *cap, const pcb_feature_t *feat) {
    dfm_result_t res = { .passed = true, .violation_count = 0 };

    /* 1. Перевірка ширини провідника */
    if (feat->trace_width < cap->min_trace_width - 1e-5) {
        printf("[DFM ERROR] Ширина доріжки %.3f мм < мін. %.3f мм\n",
               feat->trace_width, cap->min_trace_width);
        res.passed = false;
        res.violation_count++;
    }

    /* 2. Перевірка зазору між провідниками */
    if (feat->trace_space < cap->min_trace_space - 1e-5) {
        printf("[DFM ERROR] Зазор між доріжками %.3f мм < мін. %.3f мм\n",
               feat->trace_space, cap->min_trace_space);
        res.passed = false;
        res.violation_count++;
    }

    /* 3. Перевірка діаметра свердла */
    if (feat->drill_dia < cap->min_drill_dia - 1e-5) {
        printf("[DFM ERROR] Діаметр свердла %.3f мм < мін. %.3f мм\n",
               feat->drill_dia, cap->min_drill_dia);
        res.passed = false;
        res.violation_count++;
    }

    /* 4. Розрахунок і перевірка пояска металізації (Annular Ring) */
    double annular_ring = (feat->pad_dia - feat->drill_dia) / 2.0;
    if (annular_ring < cap->min_annular_ring - 1e-5) {
        printf("[DFM ERROR] Поясок металізації %.3f мм < мін. %.3f мм (Pad=%.3f, Drill=%.3f)\n",
               annular_ring, cap->min_annular_ring, feat->pad_dia, feat->drill_dia);
        res.passed = false;
        res.violation_count++;
    }

    /* 5. Розрахунок і перевірка містка паяльної маски (Solder Mask Dam) */
    double mask_dam = feat->pad_to_pad_copper_space - 2.0 * cap->mask_expansion;
    if (mask_dam < cap->min_mask_dam - 1e-5) {
        printf("[DFM ERROR] Місток паяльної маски %.3f мм < мін. %.3f мм (Sliver risk!)\n",
               mask_dam, cap->min_mask_dam);
        res.passed = false;
        res.violation_count++;
    }

    /* 6. Перевірка зазору до краю плати */
    double required_edge_dist = feat->is_vcut_edge ? cap->min_edge_vcut : cap->min_edge_milling;
    if (feat->copper_to_edge_dist < required_edge_dist - 1e-5) {
        printf("[DFM ERROR] Відступ до краю плати %.3f мм < мін. %.3f мм (%s)\n",
               feat->copper_to_edge_dist, required_edge_dist,
               feat->is_vcut_edge ? "V-cut" : "Milling");
        res.passed = false;
        res.violation_count++;
    }

    return res;
}

int main(void) {
    /* Стандартні правила Standard Pool для 1 oz міді (розміри в мм) */
    pcb_capabilities_t jlcpcb_standard = {
        .min_trace_width = 0.150,    /* 6 mil */
        .min_trace_space = 0.150,    /* 6 mil */
        .min_drill_dia   = 0.300,    /* 12 mil */
        .min_annular_ring= 0.150,    /* 6 mil */
        .min_mask_dam    = 0.100,    /* 4 mil */
        .mask_expansion  = 0.050,    /* 2 mil */
        .min_edge_milling= 0.300,    /* 12 mil */
        .min_edge_vcut   = 0.500     /* 20 mil */
    };

    /* Тестовий елемент із порушенням пояска та зазору V-cut */
    pcb_feature_t sample_via = {
        .trace_width = 0.180,
        .trace_space = 0.160,
        .pad_dia     = 0.500,        /* Pad 0.5 мм зі свердлом 0.3 мм дає AR = 0.10 мм (< 0.15 мм) */
        .drill_dia   = 0.300,
        .pad_to_pad_copper_space = 0.250, /* Dam = 0.25 - 2*0.05 = 0.15 мм (> 0.10 мм) */
        .copper_to_edge_dist = 0.350,     /* 0.35 мм для V-cut (< 0.50 мм) */
        .is_vcut_edge = true
    };

    printf("=== Перевірка топології за правилами Standard Pool ===\n");
    dfm_result_t report = validate_pcb_features(&jlcpcb_standard, &sample_via);
    if (report.passed) {
        printf("Перевірку пройдено успішно: топологія відповідає нормам фабрики.\n");
    } else {
        printf("Знайдено %d порушень технологічних обмежень!\n", report.violation_count);
    }

    return report.passed ? 0 : 1;
}
