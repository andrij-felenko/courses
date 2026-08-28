#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define NMS_MAX_INPUT   1024
#define NMS_MAX_OUTPUT  64

/* Структура вхідної/вихідної рамки детектора */
typedef struct {
    int32_t x1;
    int32_t y1;
    int32_t x2;
    int32_t y2;
    int32_t score;      // Масштабований скор упевненості
    int16_t class_id;
} NmsBox;

/* Внутрішній контекст рушія у форматі Structure-of-Arrays (SoA) */
typedef struct {
    int32_t x1[NMS_MAX_INPUT];
    int32_t y1[NMS_MAX_INPUT];
    int32_t x2[NMS_MAX_INPUT];
    int32_t y2[NMS_MAX_INPUT];
    int32_t area[NMS_MAX_INPUT];
    int32_t score[NMS_MAX_INPUT];
    int16_t class_id[NMS_MAX_INPUT];
    uint16_t indices[NMS_MAX_INPUT];
    uint32_t count;
} NmsEngineContext;

/* Конфігурація параметрів NMS */
typedef struct {
    int32_t score_threshold;    // Поріг відсікання фону
    int32_t iou_threshold_num;  // Чисельник порогу IoU (напр. 9 для 0.45)
    int32_t iou_threshold_den;  // Знаменник порогу IoU (напр. 20 для 0.45)
    uint32_t max_output_boxes;  // Максимальна кількість цілей на виході (K)
} NmsConfig;

/* Обчислення площі перетину двох прямокутників */
static inline int32_t calculate_intersection_area(
    int32_t ax1, int32_t ay1, int32_t ax2, int32_t ay2,
    int32_t bx1, int32_t by1, int32_t bx2, int32_t by2)
{
    int32_t ix1 = (ax1 > bx1) ? ax1 : bx1;
    int32_t iy1 = (ay1 > by1) ? ay1 : by1;
    int32_t ix2 = (ax2 < bx2) ? ax2 : bx2;
    int32_t iy2 = (ay2 < by2) ? ay2 : by2;

    int32_t iw = ix2 - ix1;
    int32_t ih = iy2 - iy1;

    if (iw <= 0 || ih <= 0) {
        return 0;
    }
    return iw * ih;
}

/* Розбиття Ломуто для вибору порядкової статистики */
static uint32_t quickselect_partition(NmsEngineContext *ctx, uint32_t left, uint32_t right, uint32_t pivot_idx) {
    int32_t pivot_score = ctx->score[ctx->indices[pivot_idx]];
    
    // Переміщуємо pivot у кінець масиву
    uint16_t tmp = ctx->indices[pivot_idx];
    ctx->indices[pivot_idx] = ctx->indices[right];
    ctx->indices[right] = tmp;

    uint32_t store_idx = left;
    for (uint32_t i = left; i < right; ++i) {
        if (ctx->score[ctx->indices[i]] > pivot_score) { // Сортування за спаданням
            tmp = ctx->indices[store_idx];
            ctx->indices[store_idx] = ctx->indices[i];
            ctx->indices[i] = tmp;
            store_idx++;
        }
    }

    tmp = ctx->indices[store_idx];
    ctx->indices[store_idx] = ctx->indices[right];
    ctx->indices[right] = tmp;

    return store_idx;
}

/* Алгоритм QuickSelect для лінійного відбору Top-K кандидатів */
static void select_top_k(NmsEngineContext *ctx, uint32_t k) {
    if (ctx->count <= k) {
        return;
    }

    uint32_t left = 0;
    uint32_t right = ctx->count - 1;

    while (left < right) {
        uint32_t pivot_idx = left + (right - left) / 2;
        uint32_t new_pivot = quickselect_partition(ctx, left, right, pivot_idx);

        if (new_pivot == k - 1) {
            break;
        } else if (new_pivot > k - 1) {
            right = new_pivot - 1;
        } else {
            left = new_pivot + 1;
        }
    }
}

/* Точне сортування відібраних Top-K елементів */
static void sort_top_k(NmsEngineContext *ctx, uint32_t k) {
    uint32_t n = (ctx->count < k) ? ctx->count : k;
    for (uint32_t i = 1; i < n; ++i) {
        uint16_t key = ctx->indices[i];
        int32_t key_score = ctx->score[key];
        int32_t j = (int32_t)i - 1;

        while (j >= 0 && ctx->score[ctx->indices[j]] < key_score) {
            ctx->indices[j + 1] = ctx->indices[j];
            j--;
        }
        ctx->indices[j + 1] = key;
    }
}

/* Виконавчий конвеєр вбудованого NMS */
uint32_t nms_engine_process(
    const NmsBox *input_boxes,
    uint32_t input_count,
    const NmsConfig *config,
    NmsBox *output_boxes,
    uint32_t max_output)
{
    if (input_boxes == NULL || output_boxes == NULL || input_count == 0 || max_output == 0) {
        return 0;
    }

    static NmsEngineContext ctx; // Статична пам'ять без виділення в купі
    ctx.count = 0;

    // 1. Завантаження у структуру SoA та фільтрація фонового шуму
    uint32_t limit = (input_count < NMS_MAX_INPUT) ? input_count : NMS_MAX_INPUT;
    for (uint32_t i = 0; i < limit; ++i) {
        if (input_boxes[i].score >= config->score_threshold) {
            uint32_t idx = ctx.count;
            ctx.x1[idx] = input_boxes[i].x1;
            ctx.y1[idx] = input_boxes[i].y1;
            ctx.x2[idx] = input_boxes[i].x2;
            ctx.y2[idx] = input_boxes[i].y2;
            ctx.score[idx] = input_boxes[i].score;
            ctx.class_id[idx] = input_boxes[i].class_id;

            int32_t w = input_boxes[i].x2 - input_boxes[i].x1;
            int32_t h = input_boxes[i].y2 - input_boxes[i].y1;
            ctx.area[idx] = (w > 0 && h > 0) ? (w * h) : 0;
            ctx.indices[idx] = (uint16_t)idx;
            ctx.count++;
        }
    }

    if (ctx.count == 0) {
        return 0;
    }

    // 2. Селективний відбір Top-K елементів через QuickSelect
    uint32_t k_target = (config->max_output_boxes < max_output) ? config->max_output_boxes : max_output;
    if (k_target > NMS_MAX_OUTPUT) {
        k_target = NMS_MAX_OUTPUT;
    }

    select_top_k(&ctx, k_target);
    sort_top_k(&ctx, k_target);

    // 3. Ітеративне придушення перекриттів без ділення
    uint32_t active_candidates = (ctx.count < k_target) ? ctx.count : k_target;
    uint32_t out_count = 0;
    bool suppressed[NMS_MAX_OUTPUT] = {false};

    for (uint32_t i = 0; i < active_candidates; ++i) {
        if (suppressed[i]) {
            continue;
        }

        uint16_t lead_idx = ctx.indices[i];
        
        output_boxes[out_count].x1 = ctx.x1[lead_idx];
        output_boxes[out_count].y1 = ctx.y1[lead_idx];
        output_boxes[out_count].x2 = ctx.x2[lead_idx];
        output_boxes[out_count].y2 = ctx.y2[lead_idx];
        output_boxes[out_count].score = ctx.score[lead_idx];
        output_boxes[out_count].class_id = ctx.class_id[lead_idx];
        out_count++;

        if (out_count >= max_output) {
            break;
        }

        int32_t lead_x1 = ctx.x1[lead_idx];
        int32_t lead_y1 = ctx.y1[lead_idx];
        int32_t lead_x2 = ctx.x2[lead_idx];
        int32_t lead_y2 = ctx.y2[lead_idx];
        int32_t lead_area = ctx.area[lead_idx];
        int16_t lead_class = ctx.class_id[lead_idx];

        for (uint32_t j = i + 1; j < active_candidates; ++j) {
            if (suppressed[j]) {
                continue;
            }

            uint16_t cand_idx = ctx.indices[j];
            if (ctx.class_id[cand_idx] != lead_class) {
                continue; // Рамки різних класів не придушуються
            }

            int32_t inter_area = calculate_intersection_area(
                lead_x1, lead_y1, lead_x2, lead_y2,
                ctx.x1[cand_idx], ctx.y1[cand_idx], ctx.x2[cand_idx], ctx.y2[cand_idx]);

            if (inter_area <= 0) {
                continue;
            }

            int32_t union_area = lead_area + ctx.area[cand_idx] - inter_area;

            // Перевірка цілочисельного перехресного множення
            if ((int64_t)inter_area * config->iou_threshold_den >= (int64_t)union_area * config->iou_threshold_num) {
                suppressed[j] = true;
            }
        }
    }

    return out_count;
}
