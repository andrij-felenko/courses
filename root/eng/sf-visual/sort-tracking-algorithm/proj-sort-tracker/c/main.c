#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define SORT_MAX_TRACKS 128
#define SORT_MAX_DETECTIONS 128

typedef struct {
    float x1, y1, x2, y2;
    float score;
} sort_bbox_t;

typedef struct {
    float x[7];      // Стан: [u, v, s, r, u_dot, v_dot, s_dot]
    float P[7][7];   // Коваріація стану
    int id;
    int hits;
    int hit_streak;
    int age;
    int time_since_update;
    bool active;
} sort_track_t;

typedef struct {
    sort_track_t tracks[SORT_MAX_TRACKS];
    int next_id;
    int frame_count;
    int max_age;
    int min_hits;
    float iou_threshold;
} sort_tracker_t;

static float compute_iou_c(const sort_bbox_t *a, const sort_bbox_t *b) {
    float xx1 = fmaxf(a->x1, b->x1);
    float yy1 = fmaxf(a->y1, b->y1);
    float xx2 = fminf(a->x2, b->x2);
    float yy2 = fminf(a->y2, b->y2);
    float w = fmaxf(0.0f, xx2 - xx1);
    float h = fmaxf(0.0f, yy2 - yy1);
    float inter = w * h;
    float area_a = (a->x2 - a->x1) * (a->y2 - a->y1);
    float area_b = (b->x2 - b->x1) * (b->y2 - b->y1);
    float un = area_a + area_b - inter;
    return (un > 0.0f) ? (inter / un) : 0.0f;
}

static sort_bbox_t state_to_bbox_c(const float x[7]) {
    sort_bbox_t b = {0};
    float u = x[0], v = x[1], s = x[2], r = x[3];
    if (s <= 0.0f || r <= 0.0f) return b;
    float w = sqrtf(s * r);
    float h = sqrtf(s / r);
    b.x1 = u - w * 0.5f;
    b.y1 = v - h * 0.5f;
    b.x2 = u + w * 0.5f;
    b.y2 = v + h * 0.5f;
    return b;
}

static void kalman_predict_c(sort_track_t *t) {
    // x = F * x (модель сталої швидкості)
    t->x[0] += t->x[4];
    t->x[1] += t->x[5];
    t->x[2] += t->x[6];
    
    // Спрощене збільшення діагональної дисперсії Q
    for (int i = 0; i < 7; i++) {
        t->P[i][i] += (i < 4) ? 0.01f : 0.1f;
    }
    t->age++;
    if (t->time_since_update > 0) t->hit_streak = 0;
    t->time_since_update++;
}

static void kalman_update_c(sort_track_t *t, const sort_bbox_t *det) {
    float w = det->x2 - det->x1;
    float h = det->y2 - det->y1;
    float z[4] = { det->x1 + w * 0.5f, det->y1 + h * 0.5f, w * h, (h > 0.0f) ? (w / h) : 1.0f };
    
    // Діагональне наближення фільтра для швидкого інференсу
    for (int i = 0; i < 4; i++) {
        float r_noise = (i < 2) ? 1.0f : 10.0f;
        float s_val = t->P[i][i] + r_noise;
        float k_gain = t->P[i][i] / s_val;
        float innov = z[i] - t->x[i];
        t->x[i] += k_gain * innov;
        t->P[i][i] *= (1.0f - k_gain);
        
        // Поправка швидкості для координат
        if (i < 3) {
            t->x[i + 4] += (k_gain * 0.5f) * innov;
        }
    }
    t->time_since_update = 0;
    t->hits++;
    t->hit_streak++;
}

void sort_tracker_init(sort_tracker_t *st, int max_age, int min_hits, float iou_thresh) {
    st->next_id = 1;
    st->frame_count = 0;
    st->max_age = max_age;
    st->min_hits = min_hits;
    st->iou_threshold = iou_thresh;
    for (int i = 0; i < SORT_MAX_TRACKS; i++) {
        st->tracks[i].active = false;
    }
}

int sort_tracker_update(sort_tracker_t *st, const sort_bbox_t *dets, int num_dets,
                        sort_bbox_t *out_boxes, int *out_ids, int max_out) {
    st->frame_count++;

    // 1. Прогноз Калмана
    for (int i = 0; i < SORT_MAX_TRACKS; i++) {
        if (st->tracks[i].active) {
            kalman_predict_c(&st->tracks[i]);
        }
    }

    // 2. Жадібна асоціація за матрицею IoU (O(N*M))
    bool det_matched[SORT_MAX_DETECTIONS] = {false};
    bool trk_matched[SORT_MAX_TRACKS] = {false};

    for (int i = 0; i < SORT_MAX_TRACKS; i++) {
        if (!st->tracks[i].active) continue;
        sort_bbox_t trk_b = state_to_bbox_c(st->tracks[i].x);
        float best_iou = st->iou_threshold;
        int best_det = -1;

        for (int j = 0; j < num_dets; j++) {
            if (det_matched[j]) continue;
            float iou = compute_iou_c(&trk_b, &dets[j]);
            if (iou > best_iou) {
                best_iou = iou;
                best_det = j;
            }
        }

        if (best_det >= 0) {
            det_matched[best_det] = true;
            trk_matched[i] = true;
            kalman_update_c(&st->tracks[i], &dets[best_det]);
        }
    }

    // 3. Створення нових треків
    for (int j = 0; j < num_dets; j++) {
        if (!det_matched[j]) {
            for (int i = 0; i < SORT_MAX_TRACKS; i++) {
                if (!st->tracks[i].active) {
                    sort_track_t *t = &st->tracks[i];
                    t->active = true;
                    t->id = st->next_id++;
                    t->hits = 1;
                    t->hit_streak = 1;
                    t->age = 0;
                    t->time_since_update = 0;
                    float w = dets[j].x2 - dets[j].x1;
                    float h = dets[j].y2 - dets[j].y1;
                    t->x[0] = dets[j].x1 + w * 0.5f;
                    t->x[1] = dets[j].y1 + h * 0.5f;
                    t->x[2] = w * h;
                    t->x[3] = (h > 0.0f) ? (w / h) : 1.0f;
                    t->x[4] = t->x[5] = t->x[6] = 0.0f;
                    for (int r = 0; r < 7; r++) {
                        for (int c = 0; c < 7; c++) t->P[r][c] = 0.0f;
                        t->P[r][r] = (r < 4) ? 10.0f : 1000.0f;
                    }
                    break;
                }
            }
        }
    }

    // 4. Фільтрація вихідних треків та очищення застарілих
    int count = 0;
    for (int i = 0; i < SORT_MAX_TRACKS; i++) {
        if (!st->tracks[i].active) continue;
        if (st->tracks[i].time_since_update > st->max_age) {
            st->tracks[i].active = false;
            continue;
        }
        if (st->tracks[i].time_since_update < 1 &&
            (st->tracks[i].hit_streak >= st->min_hits || st->frame_count <= st->min_hits)) {
            if (count < max_out) {
                out_boxes[count] = state_to_bbox_c(st->tracks[i].x);
                out_ids[count] = st->tracks[i].id;
                count++;
            }
        }
    }
    return count;
}
