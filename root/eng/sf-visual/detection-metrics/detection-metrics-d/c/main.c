#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

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
    bool matched;
} GroundTruth;

/* Обчислення Intersection over Union для пари прямокутників */
float bbox_iou(const BBox *a, const BBox *b) {
    float ix1 = fmaxf(a->x1, b->x1);
    float iy1 = fmaxf(a->y1, b->y1);
    float ix2 = fminf(a->x2, b->x2);
    float iy2 = fminf(a->y2, b->y2);

    float iw = fmaxf(0.0f, ix2 - ix1);
    float ih = fmaxf(0.0f, iy2 - iy1);
    float inter_area = iw * ih;

    if (inter_area <= 0.0f) return 0.0f;

    float area_a = (a->x2 - a->x1) * (a->y2 - a->y1);
    float area_b = (b->x2 - b->x1) * (b->y2 - b->y1);
    float union_area = area_a + area_b - inter_area;

    return (union_area > 0.0f) ? (inter_area / union_area) : 0.0f;
}

/* Компаратор для сортування детекцій за спаданням впевненості */
int compare_detections_desc(const void *a, const void *b) {
    float diff = ((const Detection *)b)->score - ((const Detection *)a)->score;
    if (diff > 0.0f) return 1;
    if (diff < 0.0f) return -1;
    return 0;
}

/* Розрахунок Average Precision за стандартом неперервної інтеграції */
float compute_single_ap(Detection *dets, int num_dets, GroundTruth *gts, int num_gts, int target_class, float iou_thresh) {
    int total_gt = 0;
    for (int i = 0; i < num_gts; ++i) {
        if (gts[i].class_id == target_class) {
            total_gt++;
            gts[i].matched = false;
        }
    }
    if (total_gt == 0) return (num_dets == 0) ? 1.0f : 0.0f;

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
        return 0.0f;
    }

    qsort(class_dets, num_class_dets, sizeof(Detection), compare_detections_desc);

    bool *tp = calloc(num_class_dets, sizeof(bool));
    bool *fp = calloc(num_class_dets, sizeof(bool));

    for (int i = 0; i < num_class_dets; ++i) {
        float best_iou = 0.0f;
        int best_gt_idx = -1;

        for (int j = 0; j < num_gts; ++j) {
            if (gts[j].class_id != target_class || gts[j].image_id != class_dets[i].image_id) continue;
            float iou = bbox_iou(&class_dets[i].box, &gts[j].box);
            if (iou > best_iou) {
                best_iou = iou;
                best_gt_idx = j;
            }
        }

        if (best_iou >= iou_thresh && best_gt_idx >= 0) {
            if (!gts[best_gt_idx].matched) {
                tp[i] = true;
                gts[best_gt_idx].matched = true;
            } else {
                fp[i] = true; /* Дублікат */
            }
        } else {
            fp[i] = true;
        }
    }

    /* Накопичення Precision та Recall */
    float *rec = malloc(sizeof(float) * num_class_dets);
    float *prec = malloc(sizeof(float) * num_class_dets);
    int cum_tp = 0, cum_fp = 0;

    for (int i = 0; i < num_class_dets; ++i) {
        if (tp[i]) cum_tp++;
        if (fp[i]) cum_fp++;
        rec[i] = (float)cum_tp / (float)total_gt;
        prec[i] = (float)cum_tp / (float)(cum_tp + cum_fp);
    }

    /* Монотонна інтерполяція справа наліво */
    float max_p = 0.0f;
    for (int i = num_class_dets - 1; i >= 0; --i) {
        if (prec[i] > max_p) max_p = prec[i];
        else prec[i] = max_p;
    }

    /* Інтеграція площі під східчастою кривою */
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

/* Розрахунок інтегральної метрики COCO mAP@[0.50:0.95] за 10 порогами */
float compute_coco_map(Detection *dets, int num_dets, GroundTruth *gts, int num_gts, int num_classes) {
    float total_map = 0.0f;
    int evaluated_classes = 0;

    for (int c = 0; c < num_classes; ++c) {
        float class_ap_sum = 0.0f;
        for (int step = 0; step < 10; ++step) {
            float thresh = 0.50f + (float)step * 0.05f;
            class_ap_sum += compute_single_ap(dets, num_dets, gts, num_gts, c, thresh);
        }
        total_map += (class_ap_sum / 10.0f);
        evaluated_classes++;
    }

    return (evaluated_classes > 0) ? (total_map / (float)evaluated_classes) : 0.0f;
}
