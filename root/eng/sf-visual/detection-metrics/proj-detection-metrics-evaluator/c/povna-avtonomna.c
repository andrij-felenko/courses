/*
 * ============================================================================
 * Embedded Detector Metrics Evaluator (C99 Standard)
 * Автономний бортовий оцінювач метрик детекції для вбудованих систем
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAX_CLASSES 32
#define NUM_IOU_THRESHOLDS 10

typedef enum {
    SCALE_ALL = 0,
    SCALE_SMALL,
    SCALE_MEDIUM,
    SCALE_LARGE
} ScaleRange;

typedef struct {
    float x1, y1, x2, y2;
} BBox;

typedef struct {
    BBox box;
    float score;
    int class_id;
    int image_id;
} Detection;

typedef struct {
    BBox box;
    int class_id;
    int image_id;
    float area;
    bool is_crowd;
    bool matched;
} GroundTruth;

typedef struct {
    float ap_50;
    float ap_75;
    float map_coco;
    float ap_small;
    float ap_medium;
    float ap_large;
    float best_f1;
    float best_threshold;
    int total_gt;
    int total_dets;
} ClassMetrics;

typedef struct {
    ClassMetrics classes[MAX_CLASSES];
    float map_50;
    float map_75;
    float map_coco;
    float map_small;
    float map_medium;
    float map_large;
    int num_evaluated_classes;
} EvaluationSummary;

/* Обчислення площі прямокутника з захистом від інверсії координат */
static inline float bbox_area(const BBox *b) {
    float w = b->x2 - b->x1;
    float h = b->y2 - b->y1;
    return (w > 0.0f && h > 0.0f) ? (w * h) : 0.0f;
}

/* Обчислення коефіцієнта перекриття IoU */
float compute_iou_c(const BBox *a, const BBox *b) {
    float ix1 = (a->x1 > b->x1) ? a->x1 : b->x1;
    float iy1 = (a->y1 > b->y1) ? a->y1 : b->y1;
    float ix2 = (a->x2 < b->x2) ? a->x2 : b->x2;
    float iy2 = (a->y2 < b->y2) ? a->y2 : b->y2;

    float iw = ix2 - ix1;
    float ih = iy2 - iy1;

    if (iw <= 0.0f || ih <= 0.0f) return 0.0f;

    float inter_area = iw * ih;
    float area_a = bbox_area(a);
    float area_b = bbox_area(b);
    float union_area = area_a + area_b - inter_area;

    return (union_area > 0.0f) ? (inter_area / union_area) : 0.0f;
}

/* Компаратор швидкого сортування за спаданням впевненості */
static int det_comparator_desc(const void *a, const void *b) {
    const Detection *da = (const Detection *)a;
    const Detection *db = (const Detection *)b;
    if (db->score > da->score) return 1;
    if (db->score < da->score) return -1;
    return 0;
}

/* Перевірка належності еталона до масштабного діапазону */
static bool is_gt_in_scale(float area, ScaleRange scale) {
    switch (scale) {
        case SCALE_SMALL:  return (area < 1024.0f);
        case SCALE_MEDIUM: return (area >= 1024.0f && area < 9216.0f);
        case SCALE_LARGE:  return (area >= 9216.0f);
        case SCALE_ALL:
        default:           return true;
    }
}

/* Розрахунок середньої точності AP для окремого класу, порогу IoU та масштабу */
float evaluate_ap_single(
    const Detection *dets, int num_dets,
    GroundTruth *gts, int num_gts,
    int target_class, float iou_threshold, ScaleRange scale,
    float *out_best_f1, float *out_best_thresh
) {
    int total_gt = 0;
    for (int i = 0; i < num_gts; ++i) {
        if (gts[i].class_id == target_class && is_gt_in_scale(gts[i].area, scale)) {
            total_gt++;
        }
        gts[i].matched = false;
    }

    if (total_gt == 0) {
        if (out_best_f1) *out_best_f1 = 0.0f;
        if (out_best_thresh) *out_best_thresh = 0.5f;
        return 0.0f;
    }

    /* Фільтрація детекцій цільового класу */
    Detection *class_dets = malloc(sizeof(Detection) * (num_dets > 0 ? num_dets : 1));
    int num_class_dets = 0;
    for (int i = 0; i < num_dets; ++i) {
        if (dets[i].class_id == target_class) {
            class_dets[num_class_dets++] = dets[i];
        }
    }

    if (num_class_dets == 0) {
        free(class_dets);
        if (out_best_f1) *out_best_f1 = 0.0f;
        if (out_best_thresh) *out_best_thresh = 0.5f;
        return 0.0f;
    }

    /* Впорядкування детекцій за спаданням впевненості */
    qsort(class_dets, num_class_dets, sizeof(Detection), det_comparator_desc);

    bool *tp = calloc(num_class_dets, sizeof(bool));
    bool *fp = calloc(num_class_dets, sizeof(bool));

    for (int i = 0; i < num_class_dets; ++i) {
        float best_iou = 0.0f;
        int best_gt_idx = -1;

        for (int j = 0; j < num_gts; ++j) {
            if (gts[j].class_id != target_class || gts[j].image_id != class_dets[i].image_id) {
                continue;
            }
            if (!is_gt_in_scale(gts[j].area, scale)) {
                continue;
            }

            float iou = compute_iou_c(&class_dets[i].box, &gts[j].box);
            if (iou > best_iou) {
                best_iou = iou;
                best_gt_idx = j;
            }
        }

        if (best_iou >= iou_threshold && best_gt_idx >= 0) {
            if (!gts[best_gt_idx].matched) {
                tp[i] = true;
                gts[best_gt_idx].matched = true;
            } else {
                fp[i] = true; /* Дублікат цілі */
            }
        } else {
            fp[i] = true; /* Промах або низький IoU */
        }
    }

    /* Розрахунок накопичувальних векторів Precision та Recall */
    float *rec = malloc(sizeof(float) * num_class_dets);
    float *prec = malloc(sizeof(float) * num_class_dets);
    int cum_tp = 0, cum_fp = 0;
    float max_f1 = 0.0f;
    float opt_thresh = class_dets[0].score;

    for (int i = 0; i < num_class_dets; ++i) {
        if (tp[i]) cum_tp++;
        if (fp[i]) cum_fp++;
        rec[i] = (float)cum_tp / (float)total_gt;
        prec[i] = (float)cum_tp / (float)(cum_tp + cum_fp);

        float denom = prec[i] + rec[i];
        if (denom > 1e-6f) {
            float f1 = 2.0f * (prec[i] * rec[i]) / denom;
            if (f1 > max_f1) {
                max_f1 = f1;
                opt_thresh = class_dets[i].score;
            }
        }
    }

    if (out_best_f1) *out_best_f1 = max_f1;
    if (out_best_thresh) *out_best_thresh = opt_thresh;

    /* Монотонна інтерполяція огинаючої справа наліво */
    float max_p = 0.0f;
    for (int i = num_class_dets - 1; i >= 0; --i) {
        if (prec[i] > max_p) max_p = prec[i];
        else prec[i] = max_p;
    }

    /* Чисельна неперервна інтеграція площі під кривою (AUC) */
    float ap = 0.0f;
    float prev_r = 0.0f;
    for (int i = 0; i < num_class_dets; ++i) {
        if (rec[i] != prev_r) {
            ap += (rec[i] - prev_r) * prec[i];
            prev_r = rec[i];
        }
    }

    free(class_dets);
    free(tp);
    free(fp);
    free(rec);
    free(prec);

    return ap;
}

/* Комплексна оцінка всього тестового набору даних за стандартом MS COCO */
EvaluationSummary run_full_evaluation_c(
    const Detection *dets, int num_dets,
    GroundTruth *gts, int num_gts,
    int num_classes
) {
    EvaluationSummary summary;
    memset(&summary, 0, sizeof(EvaluationSummary));

    float thresholds[NUM_IOU_THRESHOLDS];
    for (int t = 0; t < NUM_IOU_THRESHOLDS; ++t) {
        thresholds[t] = 0.50f + (float)t * 0.05f;
    }

    float sum_map_50 = 0.0f, sum_map_75 = 0.0f, sum_map_coco = 0.0f;
    float sum_map_s = 0.0f, sum_map_m = 0.0f, sum_map_l = 0.0f;
    int valid_classes = 0;

    for (int c = 0; c < num_classes && c < MAX_CLASSES; ++c) {
        ClassMetrics *cm = &summary.classes[c];

        for (int i = 0; i < num_gts; ++i) {
            if (gts[i].class_id == c) cm->total_gt++;
        }
        for (int i = 0; i < num_dets; ++i) {
            if (dets[i].class_id == c) cm->total_dets++;
        }

        if (cm->total_gt == 0) continue;

        cm->ap_50 = evaluate_ap_single(dets, num_dets, gts, num_gts, c, 0.50f, SCALE_ALL, &cm->best_f1, &cm->best_threshold);
        cm->ap_75 = evaluate_ap_single(dets, num_dets, gts, num_gts, c, 0.75f, SCALE_ALL, NULL, NULL);

        float ap_sum = 0.0f;
        for (int t = 0; t < NUM_IOU_THRESHOLDS; ++t) {
            ap_sum += evaluate_ap_single(dets, num_dets, gts, num_gts, c, thresholds[t], SCALE_ALL, NULL, NULL);
        }
        cm->map_coco = ap_sum / (float)NUM_IOU_THRESHOLDS;

        /* Масштабні метрики */
        cm->ap_small = evaluate_ap_single(dets, num_dets, gts, num_gts, c, 0.50f, SCALE_SMALL, NULL, NULL);
        cm->ap_medium = evaluate_ap_single(dets, num_dets, gts, num_gts, c, 0.50f, SCALE_MEDIUM, NULL, NULL);
        cm->ap_large = evaluate_ap_single(dets, num_dets, gts, num_gts, c, 0.50f, SCALE_LARGE, NULL, NULL);

        sum_map_50 += cm->ap_50;
        sum_map_75 += cm->ap_75;
        sum_map_coco += cm->map_coco;
        sum_map_s += cm->ap_small;
        sum_map_m += cm->ap_medium;
        sum_map_l += cm->ap_large;
        valid_classes++;
    }

    if (valid_classes > 0) {
        summary.num_evaluated_classes = valid_classes;
        summary.map_50 = sum_map_50 / (float)valid_classes;
        summary.map_75 = sum_map_75 / (float)valid_classes;
        summary.map_coco = sum_map_coco / (float)valid_classes;
        summary.map_small = sum_map_s / (float)valid_classes;
        summary.map_medium = sum_map_m / (float)valid_classes;
        summary.map_large = sum_map_l / (float)valid_classes;
    }

    return summary;
}

/* Форматоване виведення результатів у термінал */
void print_evaluation_report_c(const EvaluationSummary *s) {
    printf("\n========================================================================\n");
    printf("         БОРТОВИЙ ЗВIТ ОЦIНКИ МЕТРИК ДЕТЕКТОРА (MS COCO PROTOCOL)       \n");
    printf("========================================================================\n");
    printf("| Клас |    GT | Dets |  AP@0.50 |  AP@0.75 | mAP@[.5:.95] |  AP_s  |  AP_m  |\n");
    printf("|------|-------|------|----------|----------|--------------|--------|--------|\n");

    for (int c = 0; c < MAX_CLASSES; ++c) {
        const ClassMetrics *cm = &s->classes[c];
        if (cm->total_gt == 0) continue;
        printf("| %4d | %5d | %4d |  %7.3f |  %7.3f |      %7.3f | %6.3f | %6.3f |\n",
               c, cm->total_gt, cm->total_dets,
               cm->ap_50, cm->ap_75, cm->map_coco,
               cm->ap_small, cm->ap_medium);
    }

    printf("========================================================================\n");
    printf(" ЗВЕДЕНI МЕТРИКИ (Усереднено по %d класах):\n", s->num_evaluated_classes);
    printf("   mAP@[0.50:0.95] (Основний бал якості) : %7.4f (%5.1f%%)\n", s->map_coco, s->map_coco * 100.0f);
    printf("   mAP@0.50        (VOC поріг 0.50)      : %7.4f (%5.1f%%)\n", s->map_50, s->map_50 * 100.0f);
    printf("   mAP@0.75        (Жорсткий поріг 0.75) : %7.4f (%5.1f%%)\n", s->map_75, s->map_75 * 100.0f);
    printf("   mAP_small       (Малорозмiрнi цiлi)   : %7.4f (%5.1f%%)\n", s->map_small, s->map_small * 100.0f);
    printf("   mAP_medium      (Середнi цiлi)        : %7.4f (%5.1f%%)\n", s->map_medium, s->map_medium * 100.0f);
    printf("   mAP_large       (Великi цiлi)         : %7.4f (%5.1f%%)\n", s->map_large, s->map_large * 100.0f);
    printf("========================================================================\n\n");
}

/* Серіалізація структури звіту в компактний рядок JSON для телеметрії */
int serialize_summary_json_c(const EvaluationSummary *s, char *out_buf, size_t buf_size) {
    int written = snprintf(out_buf, buf_size,
        "{\"map\":%.4f,\"map50\":%.4f,\"map75\":%.4f,\"maps\":%.4f,\"mapm\":%.4f,\"mapl\":%.4f,\"classes\":[",
        s->map_coco, s->map_50, s->map_75, s->map_small, s->map_medium, s->map_large);

    bool first = true;
    for (int c = 0; c < MAX_CLASSES; ++c) {
        if (s->classes[c].total_gt == 0) continue;
        if (!first) {
            written += snprintf(out_buf + written, buf_size - written, ",");
        }
        first = false;
        written += snprintf(out_buf + written, buf_size - written,
            "{\"id\":%d,\"gt\":%d,\"dets\":%d,\"ap50\":%.3f,\"map\":%.3f,\"best_f1\":%.3f,\"opt_t\":%.3f}",
            c, s->classes[c].total_gt, s->classes[c].total_dets,
            s->classes[c].ap_50, s->classes[c].map_coco,
            s->classes[c].best_f1, s->classes[c].best_threshold);
    }

    written += snprintf(out_buf + written, buf_size - written, "]}");
    return written;
}
