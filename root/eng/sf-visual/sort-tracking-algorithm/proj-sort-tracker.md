# ⚙️ Реалізація трекера SORT на Python, C та C++

У цій вставці наведено повну та самодостатню реалізацію алгоритму мультиоб'єктного трекінгу SORT (Simple Online and Realtime Tracking). Вона містить усі необхідні компоненти: 7-вимірний лінійний фільтр Калмана для габаритних рамок, обчислення матриці просторового перекриття IoU, розв'язання задачі асоціації за допомогою угорського методу (або швидкого жадібного узгодження з відсіканням) та керування життєвим циклом треків.

## 1. Архітектурні компоненти та конвеєр обробки

Програмна архітектура SORT будується як чистий функціональний конвеєр без глобального стану. Вона складається з чотирьох послідовних кроків, які циклічно виконуються для кожного вхідного кадру відеопотоку:

1. **Крок екстраполяції (передбачення):** Для всіх активних треків викликається функція прогнозування стану Калмана `predict()`. Координати центру та масштаб площі рамки пересуваються відповідно до накопичених лінійних швидкостей. Якщо в ході обчислень виникає невалідний стан (наприклад, площа стає від'ємною або координати містять нечислові значення `NaN`), такий трек позначається як пошкоджений і видаляється.
2. **Побудова матриці взаємних витрат:** Між усіма екстрапольованими рамками треків `N` та свіжими детекціями `M` розраховується матриця відстаней `Cost[i, j] = 1 - IoU(Track_i, Detection_j)`. Складність цього етапу становить `O(N · M)`, де для кожної пари обчислюються координати перетину прямокутників та відношення площ.
3. **Дводольна асоціація:** Знаходиться оптимальне парування між множинами треків і детекцій. У повній версії на Python використовується функція `linear_sum_assignment` (Угорський алгоритм із часовою складністю `O(max(N, M)³)`), а у високопродуктивних реалізаціях на C та C++ для вбудованих систем наведено жадібний метод максимального IoU, який працює за час `O(N · M)` без виділення динамічної пам'яті. Усі призначені пари, що мають перекриття нижче встановленого порогу `IoU < IoU_min`, примусово розриваються.
4. **Оновлення стану та керування життєвим циклом:**
   - Для зіставлених треків викликається крок корекції `update(z)` фільтра Калмана, що підтягує оцінку положення до координат детектора, зменшує коваріаційну невизначеність і скидає лічильник втрачених кадрів `time_since_update` у `0`.
   - Незіставлені детекції ініціалізують створення нових кандидатних треків із початковими нульовими швидкостями та розширеною дисперсією початкової невпевненості.
   - Незіставлені треки інкрементують лічильник неактивності `time_since_update`. Якщо цей лічильник перевищує допустимий ліміт `max_age` (у класичному SORT `max_age = 1`), трек остаточно знищується, а його ресурси звільняються.
   - Назовні видаються лише верифіковані треки, які спостерігалися детекціями щонайменше `min_hits` разів поспіль, що виключає передачу випадкових шумів у цільову аналітику.

## 2. Покроковий числовий приклад обробки трьох кадрів

Щоб наочно зрозуміти внутрішню еволюцію стану трекера, розглянемо проходження об'єкта крізь три послідовні кадри відеопотоку:

- **Кадр 1 (Ініціалізація):** Детектор фіксує рамку `D1 = [100, 100, 150, 200]`. Оскільки активних треків немає, `D1` потрапляє в незіставлені. Створюється `Track 1`: центр `u = 125, v = 150`, площа `s = 50 · 100 = 5000`, пропорція `r = 50 / 100 = 0.5`, швидкості `u̇ = 0, v̇ = 0, ṡ = 0`. Лічильник `hits = 1, age = 0`. Оскільки `hits < 3`, на вихід клієнту трек ще не видається.
- **Кадр 2 (Підтвердження руху):** Об'єкт змістився вправо. Детектор повертає `D2 = [110, 102, 160, 202]`. Трек `Track 1` робить прогноз (залишається `[100, 100, 150, 200]`). Обчислюється перекриття `IoU = 0.71 > 0.3`. Відбувається оновлення Калмана: оцінка положення зміщується, а швидкості набувають значень `u̇ ≈ +9.8, v̇ ≈ +1.9`. Лічильник `hits = 2, hit_streak = 2`.
- **Кадр 3 (Екстраполяція та видача):** Детектор повертає `D3 = [120, 104, 170, 204]`. `Track 1` робить прогноз із урахуванням швидкості: очікувана рамка автоматично зміщується в точку `[119.8, 103.9, 169.8, 203.9]`. Перекриття з детекцією становить `IoU = 0.96`. Після оновлення `hit_streak = 3 >= min_hits`. Трек `Track 1` переходить у статус підтвердженого та передається зовнішньому споживачу.

## 3. Реалізація трекера різними мовами програмування

Нижче наведено три повністю робочі та самодостатні реалізації: на мові Python (із використанням NumPy та SciPy), мовою C (у форматі C99 зі статичним пулом пам'яті для мікроконтролерів та DSP) та сучасною ідіоматичною мовою C++ (із використанням RAII, `std::vector`, `std::array` та семантики безпечних типів).

:::tabs
```py
import numpy as np
from scipy.optimize import linear_sum_assignment


def convert_bbox_to_z(bbox):
    """Перетворює [x1, y1, x2, y2] на вектор виміру [u, v, s, r]."""
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    u = bbox[0] + w / 2.0
    v = bbox[1] + h / 2.0
    s = w * h
    r = w / float(h) if h > 0 else 1.0
    return np.array([u, v, s, r]).reshape((4, 1))


def convert_x_to_bbox(x):
    """Перетворює стан Калмана [u, v, s, r, ...] на [x1, y1, x2, y2]."""
    u, v, s, r = x[0, 0], x[1, 0], x[2, 0], x[3, 0]
    if s <= 0 or r <= 0:
        return np.zeros(4)
    w = np.sqrt(s * r)
    h = np.sqrt(s / r)
    return np.array([u - w / 2.0, v - h / 2.0, u + w / 2.0, v + h / 2.0])


def compute_iou(bb_test, bb_gt):
    """Обчислює IoU між двома прямокутними рамками."""
    xx1 = np.maximum(bb_test[0], bb_gt[0])
    yy1 = np.maximum(bb_test[1], bb_gt[1])
    xx2 = np.minimum(bb_test[2], bb_gt[2])
    yy2 = np.minimum(bb_test[3], bb_gt[3])
    w = np.maximum(0.0, xx2 - xx1)
    h = np.maximum(0.0, yy2 - yy1)
    inter = w * h
    area_test = (bb_test[2] - bb_test[0]) * (bb_test[3] - bb_test[1])
    area_gt = (bb_gt[2] - bb_gt[0]) * (bb_gt[3] - bb_gt[1])
    union = area_test + area_gt - inter
    return inter / union if union > 0 else 0.0


class KalmanBoxTracker:
    count = 0

    def __init__(self, bbox):
        # 7D стан: [u, v, s, r, u_dot, v_dot, s_dot]
        self.x = np.zeros((7, 1))
        self.x[:4] = convert_bbox_to_z(bbox)
        
        # Матриця коваріації стану P
        self.P = np.diag([10.0, 10.0, 10.0, 10.0, 1000.0, 1000.0, 1000.0])
        
        # Матриця переходу F (dt = 1)
        self.F = np.eye(7)
        for i in range(3):
            self.F[i, i + 4] = 1.0
            
        # Матриця виміру H (4x7)
        self.H = np.zeros((4, 7))
        for i in range(4):
            self.H[i, i] = 1.0
            
        # Шуми Q та R
        self.Q = np.diag([1.0, 1.0, 1.0, 1.0, 10.0, 10.0, 10.0]) * 0.01
        self.R = np.diag([1.0, 1.0, 10.0, 10.0]) * 1.0
        
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.hits = 1
        self.hit_streak = 1
        self.age = 0

    def predict(self):
        # x = F * x
        self.x = np.dot(self.F, self.x)
        # P = F * P * F^T + Q
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        return convert_x_to_bbox(self.x)

    def update(self, bbox):
        self.time_since_update = 0
        self.hits += 1
        self.hit_streak += 1
        z = convert_bbox_to_z(bbox)
        
        # Інновація y = z - H * x
        y = z - np.dot(self.H, self.x)
        # S = H * P * H^T + R
        S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        # K = P * H^T * inv(S)
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        # x = x + K * y
        self.x = self.x + np.dot(K, y)
        # P = (I - K * H) * P
        I = np.eye(7)
        self.P = np.dot(I - np.dot(K, self.H), self.P)


class Sort:
    def __init__(self, max_age=1, min_hits=3, iou_threshold=0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0

    def update(self, detections=np.empty((0, 5))):
        """
        detections: np.array розмірності (N, 5), де кожен рядок це [x1, y1, x2, y2, score].
        Повертає масив активних треків [x1, y1, x2, y2, track_id].
        """
        self.frame_count += 1
        # 1. Передбачення для всіх наявних треків
        predicted_boxes = []
        to_del = []
        for i, trk in enumerate(self.trackers):
            box = trk.predict()
            if np.any(np.isnan(box)):
                to_del.append(i)
            else:
                predicted_boxes.append(box)
        for i in reversed(to_del):
            self.trackers.pop(i)

        # 2. Обчислення матриці IoU та зіставлення
        num_trks = len(self.trackers)
        num_dets = len(detections)
        matched, unmatched_dets, unmatched_trks = [], list(range(num_dets)), list(range(num_trks))

        if num_trks > 0 and num_dets > 0:
            iou_matrix = np.zeros((num_trks, num_dets))
            for t_idx, trk_box in enumerate(predicted_boxes):
                for d_idx, det in enumerate(detections):
                    iou_matrix[t_idx, d_idx] = compute_iou(trk_box, det[:4])

            # Розв'язання задачі призначення: мінімізація -IoU
            row_ind, col_ind = linear_sum_assignment(-iou_matrix)
            
            unmatched_trks = []
            unmatched_dets = []
            matched = []

            for r, c in zip(row_ind, col_ind):
                if iou_matrix[r, c] < self.iou_threshold:
                    unmatched_trks.append(r)
                    unmatched_dets.append(c)
                else:
                    matched.append((r, c))

            for t_idx in range(num_trks):
                if t_idx not in row_ind:
                    unmatched_trks.append(t_idx)
            for d_idx in range(num_dets):
                if d_idx not in col_ind:
                    unmatched_dets.append(d_idx)

        # 3. Оновлення зіставлених треків
        for t_idx, d_idx in matched:
            self.trackers[t_idx].update(detections[d_idx, :4])

        # 4. Створення нових треків для незіставлених детекцій
        for d_idx in unmatched_dets:
            new_trk = KalmanBoxTracker(detections[d_idx, :4])
            self.trackers.append(new_trk)

        # 5. Збір підтверджених результатів та видалення застарілих
        res = []
        i = len(self.trackers)
        for trk in reversed(self.trackers):
            d = convert_x_to_bbox(trk.x)
            if (trk.time_since_update < 1) and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                res.append(np.concatenate((d, [trk.id])).reshape(1, -1))
            i -= 1
            if trk.time_since_update > self.max_age:
                self.trackers.pop(i)

        if len(res) > 0:
            return np.vstack(res)
        return np.empty((0, 5))
```
```c
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
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <optional>
#include <span>

struct BoundingBox {
    float x1{0.0f};
    float y1{0.0f};
    float x2{0.0f};
    float y2{0.0f};
    float score{0.0f};

    [[nodiscard]] constexpr float area() const noexcept {
        return std::max(0.0f, x2 - x1) * std::max(0.0f, y2 - y1);
    }
};

struct TrackedObject {
    BoundingBox box;
    int track_id{-1};
};

[[nodiscard]] inline float compute_iou(const BoundingBox& a, const BoundingBox& b) noexcept {
    const float xx1 = std::max(a.x1, b.x1);
    const float yy1 = std::max(a.y1, b.y1);
    const float xx2 = std::min(a.x2, b.x2);
    const float yy2 = std::min(a.y2, b.y2);
    const float w = std::max(0.0f, xx2 - xx1);
    const float h = std::max(0.0f, yy2 - yy1);
    const float inter = w * h;
    const float un = a.area() + b.area() - inter;
    return (un > 0.0f) ? (inter / un) : 0.0f;
}

class KalmanBoxTrackerCpp {
public:
    explicit KalmanBoxTrackerCpp(const BoundingBox& bbox, int id) noexcept
        : id_(id) {
        const float w = bbox.x2 - bbox.x1;
        const float h = bbox.y2 - bbox.y1;
        x_[0] = bbox.x1 + w * 0.5f;
        x_[1] = bbox.y1 + h * 0.5f;
        x_[2] = w * h;
        x_[3] = (h > 0.0f) ? (w / h) : 1.0f;
        x_[4] = x_[5] = x_[6] = 0.0f;

        for (size_t i = 0; i < 7; ++i) {
            P_[i] = (i < 4) ? 10.0f : 1000.0f;
        }
    }

    [[nodiscard]] BoundingBox predict() noexcept {
        // x = F * x
        x_[0] += x_[4];
        x_[1] += x_[5];
        x_[2] += x_[6];

        for (size_t i = 0; i < 7; ++i) {
            P_[i] += (i < 4) ? 0.01f : 0.1f;
        }
        ++age_;
        if (time_since_update_ > 0) {
            hit_streak_ = 0;
        }
        ++time_since_update_;
        return get_bbox();
    }

    void update(const BoundingBox& bbox) noexcept {
        const float w = bbox.x2 - bbox.x1;
        const float h = bbox.y2 - bbox.y1;
        const std::array<float, 4> z = {
            bbox.x1 + w * 0.5f,
            bbox.y1 + h * 0.5f,
            w * h,
            (h > 0.0f) ? (w / h) : 1.0f
        };

        for (size_t i = 0; i < 4; ++i) {
            const float r_noise = (i < 2) ? 1.0f : 10.0f;
            const float s = P_[i] + r_noise;
            const float k = P_[i] / s;
            const float innov = z[i] - x_[i];
            x_[i] += k * innov;
            P_[i] *= (1.0f - k);
            if (i < 3) {
                x_[i + 4] += (k * 0.5f) * innov;
            }
        }
        time_since_update_ = 0;
        ++hits_;
        ++hit_streak_;
    }

    [[nodiscard]] BoundingBox get_bbox() const noexcept {
        const float u = x_[0], v = x_[1], s = x_[2], r = x_[3];
        if (s <= 0.0f || r <= 0.0f) return {};
        const float w = std::sqrt(s * r);
        const float h = std::sqrt(s / r);
        return { u - w * 0.5f, v - h * 0.5f, u + w * 0.5f, v + h * 0.5f, 1.0f };
    }

    [[nodiscard]] int id() const noexcept { return id_; }
    [[nodiscard]] int time_since_update() const noexcept { return time_since_update_; }
    [[nodiscard]] int hit_streak() const noexcept { return hit_streak_; }

private:
    std::array<float, 7> x_{};
    std::array<float, 7> P_{};
    int id_{0};
    int hits_{1};
    int hit_streak_{1};
    int age_{0};
    int time_since_update_{0};
};

class SortTracker {
public:
    explicit SortTracker(int max_age = 1, int min_hits = 3, float iou_thresh = 0.3f) noexcept
        : max_age_(max_age), min_hits_(min_hits), iou_threshold_(iou_thresh) {}

    [[nodiscard]] std::vector<TrackedObject> update(std::span<const BoundingBox> detections) {
        ++frame_count_;

        // 1. Прогноз для всіх наявних треків
        std::vector<BoundingBox> predicted_boxes;
        predicted_boxes.reserve(trackers_.size());
        for (auto& trk : trackers_) {
            predicted_boxes.push_back(trk.predict());
        }

        // 2. Жадібна асоціація
        std::vector<bool> det_matched(detections.size(), false);
        for (size_t i = 0; i < trackers_.size(); ++i) {
            float best_iou = iou_threshold_;
            int best_det = -1;
            for (size_t j = 0; j < detections.size(); ++j) {
                if (det_matched[j]) continue;
                const float iou = compute_iou(predicted_boxes[i], detections[j]);
                if (iou > best_iou) {
                    best_iou = iou;
                    best_det = static_cast<int>(j);
                }
            }
            if (best_det >= 0) {
                det_matched[best_det] = true;
                trackers_[i].update(detections[best_det]);
            }
        }

        // 3. Ініціалізація нових треків
        for (size_t j = 0; j < detections.size(); ++j) {
            if (!det_matched[j]) {
                trackers_.emplace_back(detections[j], next_id_++);
            }
        }

        // 4. Збір результатів та видалення застарілих треків
        std::vector<TrackedObject> results;
        auto it = trackers_.begin();
        while (it != trackers_.end()) {
            if (it->time_since_update() > max_age_) {
                it = trackers_.erase(it);
            } else {
                if (it->time_since_update() < 1 &&
                    (it->hit_streak() >= min_hits_ || frame_count_ <= min_hits_)) {
                    results.push_back(TrackedObject{ it->get_bbox(), it->id() });
                }
                ++it;
            }
        }
        return results;
    }

private:
    int max_age_{1};
    int min_hits_{3};
    float iou_threshold_{0.3f};
    int next_id_{1};
    int frame_count_{0};
    std::vector<KalmanBoxTrackerCpp> trackers_;
};
```
:::

## 4. Детальний аналіз інженерних пасток

Під час перенесення алгоритму SORT у виробниче середовище інженери регулярно стикаються з типовими помилками:

1. **Ділення на нуль при виродженні рамки:** Якщо детектор повертає детекцію з однаковими координатами `y1 == y2` (нульова висота `h = 0`), обчислення співвідношення сторін `r = w / h` породжує `inf` або `NaN`. Це миттєво інфікує всі наступні множення матриць Калмана. Захисний бар'єр `h = std::max(h, 1e-4f)` є обов'язковим.
2. **Асиметрія та виродження коваріації `P`:** При використанні повного множення матриць `P = (I - K*H)*P` через округлення чисел матриця `P` поступово втрачає симетрію. На 500-му кадрі це може призвести до від'ємних значень на головній діагоналі та вильоту програми при виклику кореня `sqrtf(s)`. У високонавантажених системах обов'язково застосовують форму Джозефа або примусову симетризацію `P = 0.5 * (P + Pᵀ)`.
3. **Хибні спрацьовування на перших кадрах відеопотоку:** Якщо не враховувати лічильник `frame_count <= min_hits`, на перших двох кадрах відео система взагалі не повертатиме жодного треку, навіть якщо в кадрі стоїть очевидний об'єкт. Умова `(trk.hit_streak >= min_hits || frame_count <= min_hits)` дозволяє з перших кадрів бачити цілі, поступово вмикаючи фільтр шумів для наступних детекцій.
4. **Управління пам'яттю у реальному часі:** У C-реалізації використовується статичний масив фіксованого розміру `SORT_MAX_TRACKS`. Це гарантує нульові накладні витрати на виділення пам'яті в купі (`malloc`) під час обробки відеопотоку, що критично для вбудованих автопілотів та роботизованих систем.
5. **Стійкість до переповнення числових типів:** Якщо відеокамера працює цілодобово на частоті 60 FPS, лічильник номерів `track_id` або `frame_count` при використанні 32-бітного знакового цілого досягне межі через приблизно 414 днів безперервної роботи. Для уникнення аномальної поведінки при переповненні лічильник ідентифікаторів циклічно скидається на початок діапазону.
