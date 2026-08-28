#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_BOXES 256

typedef struct {
    float x1;
    float y1;
    float x2;
    float y2;
    float score;
    int class_id;
} BoundingBox;

/* Обчислення метрики IoU між двома прямокутниками */
static inline float calculate_iou(const BoundingBox *a, const BoundingBox *b) {
    float inter_x1 = a->x1 > b->x1 ? a->x1 : b->x1;
    float inter_y1 = a->y1 > b->y1 ? a->y1 : b->y1;
    float inter_x2 = a->x2 < b->x2 ? a->x2 : b->x2;
    float inter_y2 = a->y2 < b->y2 ? a->y2 : b->y2;

    float inter_w = inter_x2 - inter_x1;
    float inter_h = inter_y2 - inter_y1;

    if (inter_w <= 0.0f || inter_h <= 0.0f) {
        return 0.0f;
    }

    float inter_area = inter_w * inter_h;
    float area_a = (a->x2 - a->x1) * (a->y2 - a->y1);
    float area_b = (b->x2 - b->x1) * (b->y2 - b->y1);
    float union_area = area_a + area_b - inter_area;

    return (union_area > 0.0f) ? (inter_area / union_area) : 0.0f;
}

/* Сортування масиву індексів за спаданням упевненості (In-place Selection/Insertion) */
static void sort_indices_by_score(const BoundingBox *boxes, int *indices, int count) {
    for (int i = 0; i < count - 1; ++i) {
        int max_idx = i;
        for (int j = i + 1; j < count; ++j) {
            if (boxes[indices[j]].score > boxes[indices[max_idx]].score) {
                max_idx = j;
            }
        }
        if (max_idx != i) {
            int tmp = indices[i];
            indices[i] = indices[max_idx];
            indices[max_idx] = tmp;
        }
    }
}

/* Жадібний алгоритм NMS зі статичною пам'яттю */
int nms_greedy_c(const BoundingBox *input_boxes, int input_count,
                 float score_threshold, float nms_threshold,
                 BoundingBox *output_boxes, int max_output) {
    if (input_count <= 0 || max_output <= 0) {
        return 0;
    }

    int valid_indices[MAX_BOXES];
    bool suppressed[MAX_BOXES] = {false};
    int valid_count = 0;

    // 1. Фільтрація за скором
    for (int i = 0; i < input_count && valid_count < MAX_BOXES; ++i) {
        if (input_boxes[i].score >= score_threshold) {
            valid_indices[valid_count++] = i;
        }
    }

    if (valid_count == 0) {
        return 0;
    }

    // 2. Сортування відфільтрованих кандидатів
    sort_indices_by_score(input_boxes, valid_indices, valid_count);

    // 3. Жадібне придушення перекриттів
    int output_count = 0;
    for (int i = 0; i < valid_count; ++i) {
        if (suppressed[i]) {
            continue;
        }

        int curr_idx = valid_indices[i];
        output_boxes[output_count++] = input_boxes[curr_idx];
        if (output_count >= max_output) {
            break;
        }

        for (int j = i + 1; j < valid_count; ++j) {
            if (suppressed[j]) {
                continue;
            }

            int next_idx = valid_indices[j];
            // Мультикласовий фільтр: придушуємо лише рамки одного класу
            if (input_boxes[curr_idx].class_id == input_boxes[next_idx].class_id) {
                float iou = calculate_iou(&input_boxes[curr_idx], &input_boxes[next_idx]);
                if (iou >= nms_threshold) {
                    suppressed[j] = true;
                }
            }
        }
    }

    return output_count;
}
