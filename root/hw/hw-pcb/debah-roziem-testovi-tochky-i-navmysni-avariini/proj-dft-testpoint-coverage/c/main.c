#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define MAX_NETS           1024
#define MAX_TESTPOINTS     2048
#define MAX_COMPONENTS     1024
#define MAX_NAME_LEN       48
#define GRID_CELL_SIZE_MM  5.0f
#define GRID_DIM_X         64
#define GRID_DIM_Y         64

typedef enum {
    NET_CLASS_POWER,
    NET_CLASS_RESET,
    NET_CLASS_CLOCK,
    NET_CLASS_ANALOG,
    NET_CLASS_HIGH_SPEED,
    NET_CLASS_GENERAL
} NetClass;

typedef enum {
    PROBE_TIP_CROWN_4PT,   /* 4-зубчаста корона для пласких майданчиків ENIG */
    PROBE_TIP_SPEAR_30DEG, /* Гострий спис 30° для проколювання флюсу OSP */
    PROBE_TIP_SERRATED,    /* Пилоподібний наконечник для окисленого припою */
    PROBE_TIP_CUP_CONCAVE  /* Сферична чашка для штирів THT */
} ProbeTipType;

typedef struct {
    char name[MAX_NAME_LEN];
    NetClass net_class;
    bool has_testpoint;
    uint32_t tp_index;
    float weight;
    uint32_t pin_count;
} NetRecord;

typedef struct {
    char net_name[MAX_NAME_LEN];
    char label[MAX_NAME_LEN];
    float x_mm;
    float y_mm;
    float diameter_mm;
    bool on_bottom_layer;
    ProbeTipType recommended_tip;
    float stub_length_mm;
    bool has_clearance_violation;
} TestPointRecord;

typedef struct {
    char ref_des[MAX_NAME_LEN];
    float x_mm;
    float y_mm;
    float width_mm;
    float height_mm;
    float z_height_mm; /* Висота компонента над поверхнею плати */
    bool on_bottom_layer;
} ComponentRecord;

typedef struct {
    uint32_t total_nets;
    uint32_t covered_nets;
    uint32_t power_nets_total;
    uint32_t power_nets_covered;
    uint32_t reset_nets_total;
    uint32_t reset_nets_covered;
    uint32_t analog_nets_total;
    uint32_t analog_nets_covered;
    uint32_t clock_nets_total;
    uint32_t clock_nets_covered;
    uint32_t high_speed_nets_total;
    uint32_t high_speed_stubs_flagged;
    uint32_t clearance_violations;
    uint32_t layer_violations;
    float dft_weighted_score;
    float total_probe_force_newtons;
    float center_of_force_x_mm;
    float center_of_force_y_mm;
} DftAuditReport;

/* Класифікація електричного ланцюга за його назвою */
static NetClass classify_net(const char *name) {
    if (strstr(name, "VCC") || strstr(name, "VDD") || strstr(name, "GND") ||
        strstr(name, "+3V3") || strstr(name, "+5V") || strstr(name, "+12V") ||
        strstr(name, "+1V8") || strstr(name, "+1V2") || strstr(name, "VBAT") ||
        strstr(name, "VBUS") || strstr(name, "AGND") || strstr(name, "DGND")) {
        return NET_CLASS_POWER;
    }
    if (strstr(name, "RESET") || strstr(name, "NRST") || strstr(name, "RST_N") || strstr(name, "POR")) {
        return NET_CLASS_RESET;
    }
    if (strstr(name, "CLK") || strstr(name, "OSC") || strstr(name, "MCLK") || strstr(name, "TCK")) {
        return NET_CLASS_CLOCK;
    }
    if (strstr(name, "ADC") || strstr(name, "SENSE") || strstr(name, "VREF") || strstr(name, "ANALOG")) {
        return NET_CLASS_ANALOG;
    }
    if (strstr(name, "USB") || strstr(name, "ETH") || strstr(name, "DDR") ||
        strstr(name, "PCIE") || strstr(name, "MIPI") || strstr(name, "SGMII")) {
        return NET_CLASS_HIGH_SPEED;
    }
    return NET_CLASS_GENERAL;
}

/* Отримання вагового коефіцієнта для розрахунку індексу DFT */
static float get_net_weight(NetClass nc) {
    switch (nc) {
        case NET_CLASS_POWER:      return 10.0f;
        case NET_CLASS_RESET:      return 8.0f;
        case NET_CLASS_ANALOG:     return 6.0f;
        case NET_CLASS_CLOCK:      return 5.0f;
        case NET_CLASS_HIGH_SPEED: return 2.0f;
        default:                   return 1.0f;
    }
}

/* Назва типу зонду для карти свердління */
static const char* probe_tip_to_string(ProbeTipType pt) {
    switch (pt) {
        case PROBE_TIP_CROWN_4PT:   return "Crown-4pt (100mil/2.0N)";
        case PROBE_TIP_SPEAR_30DEG: return "Spear-30deg (75mil/2.5N)";
        case PROBE_TIP_SERRATED:    return "Serrated (100mil/2.0N)";
        case PROBE_TIP_CUP_CONCAVE: return "Concave-Cup (100mil/1.5N)";
        default:                    return "Standard-Crown";
    }
}

/* Евклідова відстань між точками */
static float calc_dist(float x1, float y1, float x2, float y2) {
    float dx = x1 - x2;
    float dy = y1 - y2;
    return sqrtf(dx * dx + dy * dy);
}

/* Основний аналітичний модуль аудиту тестопридатності плати */
void execute_dft_analysis(NetRecord *nets, uint32_t net_count,
                          TestPointRecord *tps, uint32_t tp_count,
                          ComponentRecord *comps, uint32_t comp_count,
                          DftAuditReport *report) {
    memset(report, 0, sizeof(DftAuditReport));
    report->total_nets = net_count;

    float sum_weighted_covered = 0.0f;
    float sum_weighted_total = 0.0f;
    float sum_force_x = 0.0f;
    float sum_force_y = 0.0f;

    /* [1] Класифікація ланцюгів та перевірка наявності тестових точок */
    for (uint32_t i = 0; i < net_count; ++i) {
        nets[i].net_class = classify_net(nets[i].name);
        nets[i].weight = get_net_weight(nets[i].net_class);
        nets[i].has_testpoint = false;

        sum_weighted_total += nets[i].weight;

        switch (nets[i].net_class) {
            case NET_CLASS_POWER:      report->power_nets_total++; break;
            case NET_CLASS_RESET:      report->reset_nets_total++; break;
            case NET_CLASS_ANALOG:     report->analog_nets_total++; break;
            case NET_CLASS_CLOCK:      report->clock_nets_total++; break;
            case NET_CLASS_HIGH_SPEED: report->high_speed_nets_total++; break;
            default: break;
        }

        for (uint32_t j = 0; j < tp_count; ++j) {
            if (strcmp(nets[i].name, tps[j].net_name) == 0) {
                nets[i].has_testpoint = true;
                nets[i].tp_index = j;
                break;
            }
        }

        if (nets[i].has_testpoint) {
            report->covered_nets++;
            sum_weighted_covered += nets[i].weight;

            switch (nets[i].net_class) {
                case NET_CLASS_POWER:      report->power_nets_covered++; break;
                case NET_CLASS_RESET:      report->reset_nets_covered++; break;
                case NET_CLASS_ANALOG:     report->analog_nets_covered++; break;
                case NET_CLASS_CLOCK:      report->clock_nets_covered++; break;
                default: break;
            }
        }
    }

    if (sum_weighted_total > 0.0f) {
        report->dft_weighted_score = (sum_weighted_covered / sum_weighted_total) * 100.0f;
    }

    /* [2] Фізичний аналіз тестових точок, вибір зондів та перевірка колізій */
    for (uint32_t i = 0; i < tp_count; ++i) {
        tps[i].has_clearance_violation = false;

        /* Перевірка сторони доступу: виключно Secondary (Bottom) Layer */
        if (!tps[i].on_bottom_layer) {
            report->layer_violations++;
            printf("  [WARN Layer] Точка %s на сигналі %s розташована на TOP шарі (вимагає Clamshell)!\n",
                   tps[i].label, tps[i].net_name);
        }

        /* Вибір типу наконечника зонду за діаметром площадки */
        if (tps[i].diameter_mm >= 1.0f) {
            tps[i].recommended_tip = PROBE_TIP_CROWN_4PT;
        } else if (tps[i].diameter_mm >= 0.75f) {
            tps[i].recommended_tip = PROBE_TIP_SPEAR_30DEG;
        } else {
            tps[i].recommended_tip = PROBE_TIP_SERRATED;
        }

        /* Перевірка відводів на високошвидкісних лініях */
        NetClass nc = classify_net(tps[i].net_name);
        if (nc == NET_CLASS_HIGH_SPEED && tps[i].stub_length_mm > 2.5f) {
            report->high_speed_stubs_flagged++;
            printf("  [WARN Stub] Точка %s створює відвід довжиною %.2f мм на швидкісному сигналі %s!\n",
                   tps[i].label, tps[i].stub_length_mm, tps[i].net_name);
        }

        /* Колізія: відстань між центрами сусідніх голок */
        for (uint32_t j = i + 1; j < tp_count; ++j) {
            float d_points = calc_dist(tps[i].x_mm, tps[i].y_mm, tps[j].x_mm, tps[j].y_mm);
            if (d_points < 1.27f) {
                report->clearance_violations++;
                tps[i].has_clearance_violation = true;
                tps[j].has_clearance_violation = true;
                printf("  [FAIL Clearance] Точки %s та %s занадто близько: d=%.3f мм (< 1.27 мм мінімум)!\n",
                       tps[i].label, tps[j].label, d_points);
            }
        }

        /* Колізія: відстань до компонентів на тому ж шарі */
        for (uint32_t k = 0; k < comp_count; ++k) {
            if (comps[k].on_bottom_layer != tps[i].on_bottom_layer) {
                continue; /* Різні боки плати */
            }

            float d_comp = calc_dist(tps[i].x_mm, tps[i].y_mm, comps[k].x_mm, comps[k].y_mm);
            float min_clearance = (comps[k].z_height_mm >= 4.0f) ? 3.5f : 1.27f;

            if (d_comp < min_clearance) {
                report->clearance_violations++;
                tps[i].has_clearance_violation = true;
                printf("  [FAIL Collision] Точка %s колізіює з %s (h=%.1f мм): d=%.3f мм (< %.2f мм)!\n",
                       tps[i].label, comps[k].ref_des, comps[k].z_height_mm, d_comp, min_clearance);
            }
        }

        /* Розрахунок внеску в механічний тиск */
        const float pin_force_n = 2.0f; /* 2.0 Ньютона на пін */
        sum_force_x += tps[i].x_mm * pin_force_n;
        sum_force_y += tps[i].y_mm * pin_force_n;
    }

    report->total_probe_force_newtons = (float)tp_count * 2.0f;
    if (tp_count > 0) {
        report->center_of_force_x_mm = sum_force_x / report->total_probe_force_newtons;
        report->center_of_force_y_mm = sum_force_y / report->total_probe_force_newtons;
    }
}

/* Генерація детального звіту тестопридатності та карти свердління ложа */
void generate_full_ict_report(const DftAuditReport *r, const TestPointRecord *tps, uint32_t tp_count) {
    printf("\n====================================================================\n");
    printf("         ЗВЕДЕНИЙ ВИРОБНИЧИЙ ЗВІТ ТЕСТОПРИДАТНОСТІ (DFT & ICT)      \n");
    printf("====================================================================\n");
    printf(" Загальна кількість ланцюгів проекту : %u\n", r->total_nets);
    printf(" Ланцюгів із тестовими точками       : %u (%.1f%%)\n",
           r->covered_nets, ((float)r->covered_nets / (float)r->total_nets) * 100.0f);
    printf(" Інтегральний зважений індекс DFT    : %.2f%% (Ціль >= 90.0%%)\n", r->dft_weighted_score);
    printf("--------------------------------------------------------------------\n");
    printf(" Покриття за класами ланцюгів:\n");
    printf("   • POWER      : %2u / %2u (%5.1f%%) [Критична норма: 100%%]\n",
           r->power_nets_covered, r->power_nets_total,
           r->power_nets_total ? ((float)r->power_nets_covered / (float)r->power_nets_total) * 100.0f : 100.0f);
    printf("   • RESET      : %2u / %2u (%5.1f%%) [Критична норма: 100%%]\n",
           r->reset_nets_covered, r->reset_nets_total,
           r->reset_nets_total ? ((float)r->reset_nets_covered / (float)r->reset_nets_total) * 100.0f : 100.0f);
    printf("   • ANALOG     : %2u / %2u (%5.1f%%) [Норма: >= 85%%]\n",
           r->analog_nets_covered, r->analog_nets_total,
           r->analog_nets_total ? ((float)r->analog_nets_covered / (float)r->analog_nets_total) * 100.0f : 100.0f);
    printf("   • CLOCK      : %2u / %2u (%5.1f%%)\n",
           r->clock_nets_covered, r->clock_nets_total,
           r->clock_nets_total ? ((float)r->clock_nets_covered / (float)r->clock_nets_total) * 100.0f : 100.0f);
    printf("--------------------------------------------------------------------\n");
    printf(" Технологічні дефекти та попередження:\n");
    printf("   • Порушення зазорів / колізії     : %u\n", r->clearance_violations);
    printf("   • Точки на верхньому шарі (Top)   : %u (Вимагає Clamshell оснастки)\n", r->layer_violations);
    printf("   • Небезпечні швидкісні відводи    : %u\n", r->high_speed_stubs_flagged);
    printf("--------------------------------------------------------------------\n");
    printf(" Механічні параметри тестового стенда (Bed-of-Nails Fixture):\n");
    printf("   • Загальна кількість зондів       : %u шт\n", tp_count);
    printf("   • Сумарне зусилля стиснення       : %.1f Н (%.2f кгс)\n",
           r->total_probe_force_newtons, r->total_probe_force_newtons / 9.80665f);
    printf("   • Центр механічного тиску ложа    : X = %.2f мм, Y = %.2f мм\n",
           r->center_of_force_x_mm, r->center_of_force_y_mm);
    printf("====================================================================\n\n");

    printf("ФРАГМЕНТ ТАБЛИЦІ СВЕРДЛІННЯ КОНДУКТОРА (ICT DRILL & WIRING MAP):\n");
    printf("----------------------------------------------------------------------------------------\n");
    printf("%-8s | %-16s | %-8s | %-8s | %-8s | %-26s\n",
           "Мітка", "Електричний ланцюг", "X (мм)", "Y (мм)", "D (мм)", "Рекомендований зонд (Probe)");
    printf("----------------------------------------------------------------------------------------\n");
    uint32_t print_limit = (tp_count < 10) ? tp_count : 10;
    for (uint32_t i = 0; i < print_limit; ++i) {
        printf("%-8s | %-16s | %8.3f | %8.3f | %8.2f | %-26s\n",
               tps[i].label, tps[i].net_name, tps[i].x_mm, tps[i].y_mm,
               tps[i].diameter_mm, probe_tip_to_string(tps[i].recommended_tip));
    }
    if (tp_count > print_limit) {
        printf("... [ще %u тестових точок у повному виробничому файлі]\n", tp_count - print_limit);
    }
    printf("----------------------------------------------------------------------------------------\n");
}
