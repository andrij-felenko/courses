#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

/* Структура технологічних обмежень виробника друкованих плат */
typedef struct {
    const char *factory_name;
    const char *tier_name;
    double copper_oz;           /* 0.5, 1.0, 2.0 oz */
    double min_track_width;     /* мм */
    double min_track_space;     /* мм */
    double min_drill_dia;       /* мм */
    double min_annular_ring;    /* мм */
    double mask_expansion;      /* мм */
    double min_mask_dam;        /* мм */
    double min_edge_milling;    /* мм */
    double min_edge_vcut;       /* мм */
    double min_hole_to_hole;    /* мм */
    double min_silk_width;      /* мм */
    double min_silk_clearance;  /* мм */
    double fiducial_edge_clear; /* мм */
    double max_aspect_ratio;    /* наприклад, 8.0 або 10.0 */
} factory_profile_t;

/* Вбудовані пресети виробничих ліній */
static const factory_profile_t PROFILES[] = {
    {
        .factory_name = "JLCPCB",
        .tier_name = "Standard 1-2 Layer (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,    /* 6.0 mil */
        .min_track_space = 0.150,    /* 6.0 mil */
        .min_drill_dia = 0.300,      /* 12.0 mil */
        .min_annular_ring = 0.150,   /* 6.0 mil */
        .mask_expansion = 0.050,     /* 2.0 mil */
        .min_mask_dam = 0.100,       /* 4.0 mil */
        .min_edge_milling = 0.300,   /* 12.0 mil */
        .min_edge_vcut = 0.500,      /* 20.0 mil */
        .min_hole_to_hole = 0.500,   /* 20.0 mil */
        .min_silk_width = 0.150,     /* 6.0 mil */
        .min_silk_clearance = 0.150, /* 6.0 mil */
        .fiducial_edge_clear = 5.000,/* 5.0 мм */
        .max_aspect_ratio = 8.0
    },
    {
        .factory_name = "JLCPCB",
        .tier_name = "Advanced 4-6 Layer (0.5 oz)",
        .copper_oz = 0.5,
        .min_track_width = 0.090,    /* 3.5 mil */
        .min_track_space = 0.090,    /* 3.5 mil */
        .min_drill_dia = 0.150,      /* 6.0 mil */
        .min_annular_ring = 0.100,   /* 4.0 mil */
        .mask_expansion = 0.030,     /* 1.2 mil */
        .min_mask_dam = 0.080,       /* 3.1 mil */
        .min_edge_milling = 0.200,   /* 8.0 mil */
        .min_edge_vcut = 0.400,      /* 16.0 mil */
        .min_hole_to_hole = 0.400,   /* 16.0 mil */
        .min_silk_width = 0.120,     /* 4.7 mil */
        .min_silk_clearance = 0.120, /* 4.7 mil */
        .fiducial_edge_clear = 4.000,
        .max_aspect_ratio = 10.0
    },
    {
        .factory_name = "PCBWay",
        .tier_name = "Standard Production (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.300,
        .min_annular_ring = 0.150,
        .mask_expansion = 0.050,
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.250,
        .min_edge_vcut = 0.500,
        .min_hole_to_hole = 0.500,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.150,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.0
    },
    {
        .factory_name = "Eurocircuits",
        .tier_name = "Standard Pool (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.250,      /* 10.0 mil */
        .min_annular_ring = 0.125,   /* 5.0 mil */
        .mask_expansion = 0.040,     /* 1.6 mil */
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.250,
        .min_edge_vcut = 0.450,
        .min_hole_to_hole = 0.450,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.125,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.5
    }
};

static const size_t NUM_PROFILES = sizeof(PROFILES) / sizeof(PROFILES[0]);

/* Генерація файлу правил .kicad_dru для САПР KiCad 8/9 */
bool export_kicad_dru(const factory_profile_t *p, const char *filepath) {
    if (!p || !filepath) return false;

    FILE *f = fopen(filepath, "w");
    if (!f) {
        perror("Не вдалося відкрити файл для запису");
        return false;
    }

    /* Заголовок та метадані */
    fprintf(f, ";; ===================================================================\n");
    fprintf(f, ";; KiCad 8/9 Custom DRC Rules\n");
    fprintf(f, ";; Factory Profile: %s - %s\n", p->factory_name, p->tier_name);
    fprintf(f, ";; Copper Weight: %.1f oz | Max Aspect Ratio: %.1f:1\n", p->copper_oz, p->max_aspect_ratio);
    fprintf(f, ";; Generated automatically by DFM Rules Importer\n");
    fprintf(f, ";; ===================================================================\n\n");
    fprintf(f, "(version 1)\n\n");

    /* 1. Мінімальна ширина провідників */
    fprintf(f, "(rule \"Factory_Min_Track_Width\"\n");
    fprintf(f, "  (priority 100)\n");
    fprintf(f, "  (constraint track_width (min %.3fmm))\n", p->min_track_width);
    fprintf(f, "  (condition \"A.Type == 'Track'\"))\n\n");

    /* 2. Мінімальний ізоляційний зазор */
    fprintf(f, "(rule \"Factory_Min_Clearance\"\n");
    fprintf(f, "  (priority 100)\n");
    fprintf(f, "  (constraint clearance (min %.3fmm))\n", p->min_track_space);
    fprintf(f, "  (condition \"A.NetClass != B.NetClass\"))\n\n");

    /* 3. Мінімальний діаметр свердла */
    fprintf(f, "(rule \"Factory_Min_Drill\"\n");
    fprintf(f, "  (priority 110)\n");
    fprintf(f, "  (constraint hole_size (min %.3fmm))\n", p->min_drill_dia);
    fprintf(f, "  (condition \"A.Type == 'Via' || A.Type == 'Pad'\"))\n\n");

    /* 4. Мінімальний поясок металізації (Annular Ring) */
    fprintf(f, "(rule \"Factory_Min_Annular_Ring\"\n");
    fprintf(f, "  (priority 110)\n");
    fprintf(f, "  (constraint annular_width (min %.3fmm))\n", p->min_annular_ring);
    fprintf(f, "  (condition \"A.Type == 'Via'\"))\n\n");

    /* 5. Відступ міді до контуру плати (фрезерування) */
    fprintf(f, "(rule \"Factory_Edge_Milling_Clearance\"\n");
    fprintf(f, "  (priority 120)\n");
    fprintf(f, "  (constraint edge_clearance (min %.3fmm))\n", p->min_edge_milling);
    fprintf(f, "  (condition \"A.Type == 'Track' || A.Type == 'Zone' || A.Type == 'Pad'\"))\n\n");

    /* 6. Спеціальне правило для зон скрайбування (V-Cut) */
    fprintf(f, "(rule \"Factory_VCut_Scoring_Clearance\"\n");
    fprintf(f, "  (priority 130)\n");
    fprintf(f, "  (constraint edge_clearance (min %.3fmm))\n", p->min_edge_vcut);
    fprintf(f, "  (condition \"A.Type == 'Zone' && A.NetClass == 'Power'\"))\n\n");

    /* 7. Зазор між отворами (Hole-to-Hole) */
    fprintf(f, "(rule \"Factory_Hole_To_Hole\"\n");
    fprintf(f, "  (priority 105)\n");
    fprintf(f, "  (constraint hole_clearance (min %.3fmm))\n", p->min_hole_to_hole);
    fprintf(f, "  (condition \"A.Type == 'Via' || A.Type == 'Pad'\"))\n\n");

    /* 8. Відступ шовкографії від паяльних майданчиків */
    fprintf(f, "(rule \"Factory_Silk_To_Mask_Clearance\"\n");
    fprintf(f, "  (priority 90)\n");
    fprintf(f, "  (constraint silk_clearance (min %.3fmm))\n", p->min_silk_clearance);
    fprintf(f, "  (condition \"A.Type == 'Graphic' && A.Layer == 'F.SilkS'\"))\n\n");

    /* 9. Відступ оптичних реперів від краю плати */
    fprintf(f, "(rule \"Factory_Fiducial_Edge_Clearance\"\n");
    fprintf(f, "  (priority 140)\n");
    fprintf(f, "  (constraint edge_clearance (min %.3fmm))\n", p->fiducial_edge_clear);
    fprintf(f, "  (condition \"A.Type == 'Footprint' && A.Reference == 'FID*'\"))\n\n");

    fclose(f);
    return true;
}

int main(int argc, char *argv[]) {
    printf("=== DFM Rules Importer CLI (C99) ===\n\n");

    if (argc < 2) {
        printf("Використання: %s <індекс_профілю> [вихідний_файл.kicad_dru]\n", argv[0]);
        printf("Доступні профілі фабрик:\n");
        for (size_t i = 0; i < NUM_PROFILES; ++i) {
            printf("  [%zu] %s — %s (Мідь: %.1f oz, Min W/S: %.2f/%.2f мм)\n",
                   i, PROFILES[i].factory_name, PROFILES[i].tier_name,
                   PROFILES[i].copper_oz, PROFILES[i].min_track_width, PROFILES[i].min_track_space);
        }
        return 1;
    }

    size_t idx = (size_t)atoi(argv[1]);
    if (idx >= NUM_PROFILES) {
        fprintf(stderr, "Помилка: некоректний індекс профілю %zu (діапазон 0..%zu)\n", idx, NUM_PROFILES - 1);
        return 1;
    }

    const char *outfile = (argc >= 3) ? argv[2] : "factory_rules.kicad_dru";
    const factory_profile_t *p = &PROFILES[idx];

    printf("Експорт профілю '%s (%s)' у файл '%s'...\n", p->factory_name, p->tier_name, outfile);
    if (export_kicad_dru(p, outfile)) {
        printf("Файл правил успішно згенеровано!\n");
        return 0;
    } else {
        fprintf(stderr, "Помилка під час генерації файлу!\n");
        return 1;
    }
}
