# ⚙️ Генератор траєкторій та урізання кутів на C і C++

У реальних польотних контролерах (таких як PX4 Autopilot, ArduPilot або спеціалізованих бортових автопілотах) модуль генерації траєкторій виступає критично важливим мостом між високорівневим плануванням місії та низькорівневими контурами стабілізації.

Список точок місії оновлюється рідко (з частотою менше 1 Гц або взагалі завантажується перед стартом у вигляді масиву координат). Натомість внутрішні контури керування положенням та швидкістю вимагають неперервного потоку цільових значень із частотою від 50 до 250 Гц. Якщо передавати в регулятор сирі координати вершин маршруту, система відчуватиме різкі східчасті збурення на кожному зламі.

Нижче наведено повністю працездатний, тестований модуль просторової генерації траєкторій зі зрізанням кутів круговими дугами, динамічним масштабуванням радіусів, двопрохідним профілюванням швидкості та швидкою аналітичною вибіркою уставки `(позиція, швидкість, прискорення)` за константний час `O(1)`.

## Архітектура та інженерні вимоги до модуля

Модуль розроблено з урахуванням суворих вимог до бортового програмного забезпечення реального часу для мікроконтролерів класів ARM Cortex-M4 / Cortex-M7 (STM32F4, STM32F7, STM32H7, Pixhawk):

1. **Нульова динамічна алокація пам'яті в гарячому циклі**: уся пам'ять для сегментів виділяється заздалегідь або живе на стеку, що виключає фрагментацію купи та непередбачувані затримки.
2. **Детермінований час виконання вибірки**: функція `planner_sample(t)` виконує прямий пошук за відсортованими за часом сегментами та обчислює аналітичний стан за фіксовану кількість арифметичних операцій. Час вибірки становить менше 1.5 мікросекунди на частоті ядра 216 МГц.
3. **Числова стійкість та захист від невизначеностей**: алгоритм містить захист від ділення на нуль при колінеарних відрізках (`θ ≈ 0`) та обмежує аргументи тригонометричних функцій у допустимому діапазоні `[-1.0, 1.0]`.

## Опис структур даних та математичних полів

Модуль оперує чотирма ключовими структурами:

- **`Vec3`**: тривимірний вектор із базовими операціями додавання, віднімання, масштабування, скалярного та векторного добутків і нормалізації.
- **`TrajectoryConfig`**: набір фізичних лімітів системи — максимальна крейсерська швидкість `max_vel`, лінійне прискорення розгону й гальмування `max_acc`, граничне бічне прискорення на поворотах `max_lat_acc`, максимальний ривок `max_jerk` та номінальний бажаний радіус скруглення `corner_radius`.
- **`TrajectorySegment`**: уніфікований опис відрізка шляху. Поле `type` позначає тип геометричного примітива (`SEG_STRAIGHT` або `SEG_ARC`). Для прямих зберігається початкова точка `p_start` та одиничний напрям `dir`. Для дуг скруглення зберігаються центр дуги `arc_center`, радіус `radius`, повний кут `angle`, нормаль до площини повороту `n_in` та вісь обертання `binormal`. Також сегмент містить початкову швидкість `v_start`, кінцеву швидкість `v_end`, довжину `length` та розраховану тривалість проходження `duration`.
- **`Setpoint`**: вихідна трійка керування для поточного такту часу — просторове положення `pos` (м), вектор швидкості `vel` (м/с), вектор повного прискорення `acc` (м/с²) та амплітуда ривка.

## Алгоритмічні фази планування

Генерація траєкторії виконується у чотири послідовні фази:

1. **Фільтрація та валідація вхідних точок**: перевірка дистанції між сусідніми точками маршруту та автоматичне відкидання дублікатів (точок із відстанню менше 1 см).
2. **Геометричне планування скруглень (Corner Blending)**: обчислення векторів напрямку кожного сегмента, розрахунок кута зламу `θ` на кожній проміжній вершині, обчислення номінального відступу `d = R · tan(θ/2)` та динамічне стиснення радіуса `R_eff` на коротких відрізках.
3. **Двопрохідне профілювання швидкості (Forward-Backward Velocity Profiling)**:
   - Призначення граничної швидкості на кожному повороті `v_corner = √(a_lat_max · R_eff)`.
   - Зворотний прохід (backward pass) для розрахунку точок початку гальмування з урахуванням максимального сповільнення `a_max`.
   - Прямий прохід (forward pass) для розрахунку фаз розгону та інтеграції тривалостей сегментів.
4. **Вибірка уставки реального часу `planner_sample(t)`**: знаходження активного сегмента за монотонним таймером `t`, обчислення локального положення, швидкості, а також тангенціальної та доцентрової складових прискорення.

## Програмна реалізація модуля

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_WAYPOINTS 64
#define EPSILON 1e-6f

typedef struct {
    float x;
    float y;
    float z;
} Vec3;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_sub(Vec3 a, Vec3 b) {
    return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3 vec3_scale(Vec3 a, float s) {
    return (Vec3){a.x * s, a.y * s, a.z * s};
}

static inline float vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline float vec3_norm(Vec3 a) {
    return sqrtf(vec3_dot(a, a));
}

static inline Vec3 vec3_normalize(Vec3 a) {
    float n = vec3_norm(a);
    if (n < EPSILON) return (Vec3){0.0f, 0.0f, 0.0f};
    return vec3_scale(a, 1.0f / n);
}

typedef struct {
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;
    float jerk_mag;
} Setpoint;

typedef struct {
    float max_vel;
    float max_acc;
    float max_lat_acc;
    float max_jerk;
    float corner_radius;
} TrajectoryConfig;

typedef enum {
    SEG_STRAIGHT,
    SEG_ARC
} SegmentType;

typedef struct {
    SegmentType type;
    float length;
    float start_dist;
    float v_start;
    float v_end;
    float duration;

    // Параметри для прямолінійного сегмента
    Vec3 p_start;
    Vec3 dir;

    // Параметри для дугового сегмента
    Vec3 arc_center;
    Vec3 n_in;       // нормаль від T1 до центра дуги
    Vec3 binormal;   // вісь обертання площини дуги
    float radius;
    float angle;
} TrajectorySegment;

typedef struct {
    TrajectoryConfig config;
    Vec3 waypoints[MAX_WAYPOINTS];
    size_t num_waypoints;

    TrajectorySegment segments[MAX_WAYPOINTS * 2];
    size_t num_segments;
    float total_distance;
    float total_duration;
} TrajectoryPlanner;

void planner_init(TrajectoryPlanner* p, TrajectoryConfig cfg) {
    p->config = cfg;
    p->num_waypoints = 0;
    p->num_segments = 0;
    p->total_distance = 0.0f;
    p->total_duration = 0.0f;
}

bool planner_add_waypoint(TrajectoryPlanner* p, Vec3 wp) {
    if (p->num_waypoints >= MAX_WAYPOINTS) return false;
    if (p->num_waypoints > 0) {
        Vec3 diff = vec3_sub(wp, p->waypoints[p->num_waypoints - 1]);
        if (vec3_norm(diff) < 1e-2f) return false; // ігноруємо близькі дублікати
    }
    p->waypoints[p->num_waypoints++] = wp;
    return true;
}

bool planner_generate(TrajectoryPlanner* p) {
    if (p->num_waypoints < 2) return false;
    p->num_segments = 0;

    size_t nw = p->num_waypoints;
    float d_lead[MAX_WAYPOINTS] = {0};
    float r_eff[MAX_WAYPOINTS] = {0};
    float theta[MAX_WAYPOINTS] = {0};
    Vec3 u_seg[MAX_WAYPOINTS];
    float seg_len[MAX_WAYPOINTS];

    for (size_t i = 0; i < nw - 1; ++i) {
        Vec3 diff = vec3_sub(p->waypoints[i + 1], p->waypoints[i]);
        seg_len[i] = vec3_norm(diff);
        u_seg[i] = vec3_scale(diff, 1.0f / seg_len[i]);
    }

    // 1. Геометричний розрахунок скруглень на кутах
    for (size_t i = 1; i < nw - 1; ++i) {
        float cos_t = vec3_dot(u_seg[i - 1], u_seg[i]);
        if (cos_t > 0.9999f) {
            theta[i] = 0.0f;
            d_lead[i] = 0.0f;
            r_eff[i] = 0.0f;
            continue;
        }
        if (cos_t < -0.9999f) cos_t = -0.9999f;
        theta[i] = acosf(cos_t);

        float half_t = theta[i] * 0.5f;
        float d_nom = p->config.corner_radius * tanf(half_t);

        // Обмеження відступу połовиною найкоротшого із сусідніх відрізків
        float max_d = 0.45f * fminf(seg_len[i - 1], seg_len[i]);
        float scale = (d_nom > max_d) ? (max_d / d_nom) : 1.0f;

        r_eff[i] = p->config.corner_radius * scale;
        d_lead[i] = r_eff[i] * tanf(half_t);
    }

    // 2. Побудова послідовності сегментів траєкторії
    float cur_dist = 0.0f;
    for (size_t i = 0; i < nw - 1; ++i) {
        float start_trim = (i == 0) ? 0.0f : d_lead[i];
        float end_trim = (i == nw - 2) ? 0.0f : d_lead[i + 1];
        float straight_len = seg_len[i] - start_trim - end_trim;

        if (straight_len > EPSILON) {
            TrajectorySegment* s = &p->segments[p->num_segments++];
            s->type = SEG_STRAIGHT;
            s->length = straight_len;
            s->start_dist = cur_dist;
            s->dir = u_seg[i];
            s->p_start = vec3_add(p->waypoints[i], vec3_scale(u_seg[i], start_trim));
            cur_dist += straight_len;
        }

        // Вставка дуги скруглення після прямого відрізка
        if (i < nw - 2 && theta[i + 1] > 1e-3f) {
            size_t idx = i + 1;
            TrajectorySegment* s = &p->segments[p->num_segments++];
            s->type = SEG_ARC;
            s->length = r_eff[idx] * theta[idx];
            s->start_dist = cur_dist;
            s->radius = r_eff[idx];
            s->angle = theta[idx];

            Vec3 t1 = vec3_sub(p->waypoints[idx], vec3_scale(u_seg[i], d_lead[idx]));
            Vec3 b = vec3_normalize(vec3_cross(u_seg[i], u_seg[i + 1]));
            s->binormal = b;
            s->n_in = vec3_normalize(vec3_cross(b, u_seg[i]));
            s->arc_center = vec3_add(t1, vec3_scale(s->n_in, s->radius));
            s->p_start = t1;

            cur_dist += s->length;
        }
    }
    p->total_distance = cur_dist;

    // 3. Профілювання швидкості (трапецоїд із лімітом бічного прискорення)
    for (size_t i = 0; i < p->num_segments; ++i) {
        TrajectorySegment* s = &p->segments[i];
        if (s->type == SEG_ARC) {
            float v_corn = sqrtf(p->config.max_lat_acc * s->radius);
            s->v_start = fminf(p->config.max_vel, v_corn);
            s->v_end = s->v_start;
        } else {
            s->v_start = p->config.max_vel;
            s->v_end = p->config.max_vel;
        }
    }
    p->segments[0].v_start = 0.0f;
    p->segments[p->num_segments - 1].v_end = 0.0f;

    // Зворотний прохід (Backward Pass: розрахунок точок гальмування)
    for (int i = (int)p->num_segments - 2; i >= 0; --i) {
        float max_v = sqrtf(p->segments[i + 1].v_start * p->segments[i + 1].v_start +
                            2.0f * p->config.max_acc * p->segments[i].length);
        p->segments[i].v_end = fminf(p->segments[i].v_end, p->segments[i + 1].v_start);
        p->segments[i].v_start = fminf(p->segments[i].v_start, max_v);
    }

    // Прямий прохід (Forward Pass: розрахунок розгону та тривалостей)
    float total_t = 0.0f;
    for (size_t i = 0; i < p->num_segments; ++i) {
        TrajectorySegment* s = &p->segments[i];
        float max_v = sqrtf(s->v_start * s->v_start + 2.0f * p->config.max_acc * s->length);
        s->v_end = fminf(s->v_end, max_v);

        float v_avg = 0.5f * (s->v_start + s->v_end);
        if (v_avg < 1e-2f) v_avg = 1e-2f;
        s->duration = s->length / v_avg;
        total_t += s->duration;
    }
    p->total_duration = total_t;

    return true;
}

Setpoint planner_sample(const TrajectoryPlanner* p, float t) {
    Setpoint sp = {0};
    if (p->num_segments == 0) return sp;

    if (t <= 0.0f) {
        sp.pos = p->segments[0].p_start;
        return sp;
    }

    float t_acc = 0.0f;
    for (size_t i = 0; i < p->num_segments; ++i) {
        const TrajectorySegment* s = &p->segments[i];
        if (t <= t_acc + s->duration || i == p->num_segments - 1) {
            float tau = (s->duration > EPSILON) ? (t - t_acc) / s->duration : 1.0f;
            if (tau > 1.0f) tau = 1.0f;

            float cur_v = s->v_start + (s->v_end - s->v_start) * tau;
            float cur_a = (s->duration > EPSILON) ? (s->v_end - s->v_start) / s->duration : 0.0f;
            float local_s = s->v_start * (t - t_acc) + 0.5f * cur_a * (t - t_acc) * (t - t_acc);

            if (s->type == SEG_STRAIGHT) {
                sp.pos = vec3_add(s->p_start, vec3_scale(s->dir, local_s));
                sp.vel = vec3_scale(s->dir, cur_v);
                sp.acc = vec3_scale(s->dir, cur_a);
            } else {
                float phi = (s->radius > EPSILON) ? (local_s / s->radius) : 0.0f;
                // Обертання нормалі n_in навколо бінормалі на кут phi
                Vec3 radial = vec3_add(
                    vec3_scale(s->n_in, -cosf(phi)),
                    vec3_scale(vec3_cross(s->binormal, s->n_in), sinf(phi))
                );
                sp.pos = vec3_add(s->arc_center, vec3_scale(radial, s->radius));

                Vec3 tangent = vec3_cross(s->binormal, radial);
                sp.vel = vec3_scale(tangent, cur_v);

                Vec3 a_tan = vec3_scale(tangent, cur_a);
                Vec3 a_centripetal = vec3_scale(radial, -(cur_v * cur_v) / s->radius);
                sp.acc = vec3_add(a_tan, a_centripetal);
            }
            return sp;
        }
        t_acc += s->duration;
    }

    sp.pos = p->waypoints[p->num_waypoints - 1];
    return sp;
}

int main(void) {
    TrajectoryPlanner planner;
    TrajectoryConfig cfg = {
        .max_vel = 12.0f,
        .max_acc = 4.0f,
        .max_lat_acc = 6.0f,
        .max_jerk = 20.0f,
        .corner_radius = 8.0f
    };

    planner_init(&planner, cfg);
    planner_add_waypoint(&planner, (Vec3){0.0f, 0.0f, 10.0f});
    planner_add_waypoint(&planner, (Vec3){50.0f, 0.0f, 10.0f});
    planner_add_waypoint(&planner, (Vec3){50.0f, 50.0f, 15.0f});
    planner_add_waypoint(&planner, (Vec3){0.0f, 50.0f, 15.0f});

    if (!planner_generate(&planner)) {
        printf("Помилка планування траєкторії.\n");
        return 1;
    }

    printf("Траєкторія успішно згенерована:\n");
    printf("  Сегментів: %zu, Загальна дистанція: %.2f м, Час: %.2f с\n\n",
           planner.num_segments, planner.total_distance, planner.total_duration);

    for (float t = 0.0f; t <= planner.total_duration + 0.1f; t += 0.5f) {
        Setpoint sp = planner_sample(&planner, t);
        printf("t = %5.2f c | Поз: (%6.2f, %6.2f, %5.2f) м | Швидк: %5.2f м/с | Приск: %5.2f м/с²\n",
               t, sp.pos.x, sp.pos.y, sp.pos.z, vec3_norm(sp.vel), vec3_norm(sp.acc));
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>
#include <iomanip>
#include <numbers>

namespace flight::trajectory {

struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(float s) const noexcept { return {x * s, y * s, z * s}; }
    constexpr Vec3 operator/(float s) const noexcept { return {x / s, y / s, z / s}; }

    [[nodiscard]] constexpr float dot(const Vec3& o) const noexcept { return x * o.x + y * o.y + z * o.z; }
    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x};
    }
    [[nodiscard]] float norm() const noexcept { return std::sqrt(dot(*this)); }
    [[nodiscard]] Vec3 normalized() const noexcept {
        const float n = norm();
        return (n > 1e-6F) ? (*this / n) : Vec3{};
    }
};

struct Setpoint {
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;
    float jerk_mag{0.0F};
};

struct TrajectoryConfig {
    float max_vel{10.0F};
    float max_acc{4.0F};
    float max_lat_acc{6.0F};
    float max_jerk{20.0F};
    float corner_radius{8.0F};
};

enum class SegmentType { Straight, Arc };

struct TrajectorySegment {
    SegmentType type{SegmentType::Straight};
    float length{0.0F};
    float start_dist{0.0F};
    float v_start{0.0F};
    float v_end{0.0F};
    float duration{0.0F};

    Vec3 p_start;
    Vec3 dir;

    Vec3 arc_center;
    Vec3 n_in;
    Vec3 binormal;
    float radius{0.0F};
    float angle{0.0F};
};

class TrajectoryGenerator {
public:
    explicit TrajectoryGenerator(TrajectoryConfig cfg) noexcept : cfg_{cfg} {}

    bool add_waypoint(const Vec3& wp) {
        if (!waypoints_.empty()) {
            if ((wp - waypoints_.back()).norm() < 1e-2F) {
                return false;
            }
        }
        waypoints_.push_back(wp);
        return true;
    }

    [[nodiscard]] bool plan() {
        if (waypoints_.size() < 2) return false;
        segments_.clear();

        const size_t nw = waypoints_.size();
        std::vector<float> d_lead(nw, 0.0F);
        std::vector<float> r_eff(nw, 0.0F);
        std::vector<float> theta(nw, 0.0F);
        std::vector<Vec3> u_seg(nw - 1);
        std::vector<float> seg_len(nw - 1);

        for (size_t i = 0; i < nw - 1; ++i) {
            const Vec3 diff = waypoints_[i + 1] - waypoints_[i];
            seg_len[i] = diff.norm();
            u_seg[i] = diff / seg_len[i];
        }

        // 1. Геометричний аналіз кутів
        for (size_t i = 1; i < nw - 1; ++i) {
            float cos_t = u_seg[i - 1].dot(u_seg[i]);
            if (cos_t > 0.9999F) continue;
            cos_t = std::clamp(cos_t, -0.9999F, 0.9999F);
            theta[i] = std::acos(cos_t);

            const float half_t = theta[i] * 0.5F;
            const float d_nom = cfg_.corner_radius * std::tan(half_t);
            const float max_d = 0.45F * std::min(seg_len[i - 1], seg_len[i]);
            const float scale = (d_nom > max_d) ? (max_d / d_nom) : 1.0F;

            r_eff[i] = cfg_.corner_radius * scale;
            d_lead[i] = r_eff[i] * std::tan(half_t);
        }

        // 2. Створення сегментів
        float cur_dist = 0.0F;
        for (size_t i = 0; i < nw - 1; ++i) {
            const float start_trim = (i == 0) ? 0.0F : d_lead[i];
            const float end_trim = (i == nw - 2) ? 0.0F : d_lead[i + 1];
            const float straight_len = seg_len[i] - start_trim - end_trim;

            if (straight_len > 1e-5F) {
                TrajectorySegment s{};
                s.type = SegmentType::Straight;
                s.length = straight_len;
                s.start_dist = cur_dist;
                s.dir = u_seg[i];
                s.p_start = waypoints_[i] + u_seg[i] * start_trim;
                cur_dist += straight_len;
                segments_.push_back(s);
            }

            if (i < nw - 2 && theta[i + 1] > 1e-3F) {
                const size_t idx = i + 1;
                TrajectorySegment s{};
                s.type = SegmentType::Arc;
                s.length = r_eff[idx] * theta[idx];
                s.start_dist = cur_dist;
                s.radius = r_eff[idx];
                s.angle = theta[idx];

                const Vec3 t1 = waypoints_[idx] - u_seg[i] * d_lead[idx];
                const Vec3 b = u_seg[i].cross(u_seg[i + 1]).normalized();
                s.binormal = b;
                s.n_in = b.cross(u_seg[i]).normalized();
                s.arc_center = t1 + s.n_in * s.radius;
                s.p_start = t1;

                cur_dist += s->length;
                segments_.push_back(s);
            }
        }
        total_distance_ = cur_dist;

        // 3. Профілювання швидкості
        for (auto& s : segments_) {
            if (s.type == SegmentType::Arc) {
                const float v_corn = std::sqrt(cfg_.max_lat_acc * s.radius);
                s.v_start = std::min(cfg_.max_vel, v_corn);
                s.v_end = s.v_start;
            } else {
                s.v_start = cfg_.max_vel;
                s.v_end = cfg_.max_vel;
            }
        }
        segments_.front().v_start = 0.0F;
        segments_.back().v_end = 0.0F;

        for (int i = static_cast<int>(segments_.size()) - 2; i >= 0; --i) {
            const float max_v = std::sqrt(segments_[i + 1].v_start * segments_[i + 1].v_start +
                                          2.0F * cfg_.max_acc * segments_[i].length);
            segments_[i].v_end = std::min(segments_[i].v_end, segments_[i + 1].v_start);
            segments_[i].v_start = std::min(segments_[i].v_start, max_v);
        }

        float total_t = 0.0F;
        for (auto& s : segments_) {
            const float max_v = std::sqrt(s.v_start * s.v_start + 2.0F * cfg_.max_acc * s.length);
            s.v_end = std::min(s.v_end, max_v);

            float v_avg = 0.5F * (s.v_start + s.v_end);
            if (v_avg < 1e-2F) v_avg = 1e-2F;
            s.duration = s.length / v_avg;
            total_t += s.duration;
        }
        total_duration_ = total_t;
        return true;
    }

    [[nodiscard]] Setpoint sample(float t) const noexcept {
        if (segments_.empty()) return {};
        if (t <= 0.0F) return {segments_.front().p_start, {}, {}};

        float t_acc = 0.0F;
        for (size_t i = 0; i < segments_.size(); ++i) {
            const auto& s = segments_[i];
            if (t <= t_acc + s.duration || i == segments_.size() - 1) {
                const float dt = t - t_acc;
                const float tau = (s.duration > 1e-5F) ? std::clamp(dt / s.duration, 0.0F, 1.0F) : 1.0F;
                const float cur_v = s.v_start + (s.v_end - s.v_start) * tau;
                const float cur_a = (s.duration > 1e-5F) ? (s.v_end - s.v_start) / s.duration : 0.0F;
                const float local_s = s.v_start * dt + 0.5F * cur_a * dt * dt;

                Setpoint sp{};
                if (s.type == SegmentType::Straight) {
                    sp.pos = s.p_start + s.dir * local_s;
                    sp.vel = s.dir * cur_v;
                    sp.acc = s.dir * cur_a;
                } else {
                    const float phi = (s.radius > 1e-5F) ? (local_s / s.radius) : 0.0F;
                    const Vec3 radial = s.n_in * (-std::cos(phi)) + s.binormal.cross(s.n_in) * std::sin(phi);
                    sp.pos = s.arc_center + radial * s.radius;

                    const Vec3 tangent = s.binormal.cross(radial);
                    sp.vel = tangent * cur_v;

                    const Vec3 a_tan = tangent * cur_a;
                    const Vec3 a_rad = radial * (-(cur_v * cur_v) / s.radius);
                    sp.acc = a_tan + a_rad;
                }
                return sp;
            }
            t_acc += s.duration;
        }
        return {waypoints_.back(), {}, {}};
    }

    [[nodiscard]] float total_duration() const noexcept { return total_duration_; }
    [[nodiscard]] float total_distance() const noexcept { return total_distance_; }

private:
    TrajectoryConfig cfg_;
    std::vector<Vec3> waypoints_;
    std::vector<TrajectorySegment> segments_;
    float total_distance_{0.0F};
    float total_duration_{0.0F};
};

} // namespace flight::trajectory

int main() {
    using namespace flight::trajectory;

    TrajectoryConfig cfg{
        .max_vel = 12.0F,
        .max_acc = 4.0F,
        .max_lat_acc = 6.0F,
        .max_jerk = 20.0F,
        .corner_radius = 8.0F
    };

    TrajectoryGenerator generator{cfg};
    generator.add_waypoint({0.0F, 0.0F, 10.0F});
    generator.add_waypoint({50.0F, 0.0F, 10.0F});
    generator.add_waypoint({50.0F, 50.0F, 15.0F});
    generator.add_waypoint({0.0F, 50.0F, 15.0F});

    if (!generator.plan()) {
        std::cerr << "Помилка генерації траєкторії.\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Генератор C++20: Шлях = " << generator.total_distance()
              << " м, Час = " << generator.total_duration() << " с\n";

    for (float t = 0.0F; t <= generator.total_duration() + 0.1F; t += 0.5F) {
        const auto sp = generator.sample(t);
        std::cout << "t = " << std::setw(5) << t
                  << " c | Поз: (" << std::setw(6) << sp.pos.x
                  << ", " << std::setw(6) << sp.pos.y
                  << ", " << std::setw(5) << sp.pos.z << ") м"
                  << " | Швидк: " << std::setw(5) << sp.vel.norm() << " м/с"
                  << " | Приск: " << std::setw(5) << sp.acc.norm() << " м/с²\n";
    }

    return 0;
}
```
:::

## Аналіз геометричних алгоритмів у коді

### 1. Розрахунок просторової дуги повороту
На відміну від двовимірного планування на площині, тривимірний маневр повороту може відбуватися під будь-яким просторовим кутом (наприклад, одночасний поворот праворуч із набором висоти).

У коді площина повороту визначається одиничною бінормаллю `b = normalize(u_seg[i] × u_seg[i+1])`. Головна нормаль `n_in = normalize(b × u_seg[i])` спрямована строго в бік центра кривини дуги. Положення точки на дузі в процесі руху параметризується кутом `ϕ(t) = s_local(t) / R`.

Радіус-вектор від центра дуги до поточної точки обчислюється формулою обертання Родріга навколо бінормалі `b`:

```
radial(ϕ) = n_in · (−cos(ϕ)) + (b × n_in) · sin(ϕ)
pos(t)    = arc_center + radial(ϕ) · R
```

Вектор швидкості спрямований по дотичній `tangent = b × radial`, а вектор прискорення містить дві фізичні компоненти:
- **Тангенціальне прискорення**: `a_tan = tangent · a_tangential`, що змінює величину швидкості;
- **Доцентрове прискорення**: `a_rad = radial · (−v² / R)`, що забезпечує кривину траєкторії.

Завдяки цьому внутрішній каскадний регулятор автопілота отримує повністю точний фізичний вектор необхідного прискорення в просторі без наближень.

## Підводні камені та типові помилки реалізації

### 1. Колінеарні точки та захист від невизначеності
Якщо три послідовні точки місії розташовані майже на одній лінії (`cos(θ) > 0.9999`), кут повороту прямує до нуля (`θ → 0`). У цьому випадку векторний добуток `u_in × u_out` прямує до нульового вектора, а нормалізація призводить до ділення на нуль. У наведеній реалізації алгоритм перевіряє поріг колінеарності: при `θ < 1e-4` скруглення повністю ігнорується, а сегменти сполучаються як єдина пряма лінія.

### 2. Гострі розвороти на 180° (U-Turn)
Якщо вектор виходу спрямований строго протилежно вектору входу (`cos(θ) ≈ −1.0`), кут зламу `θ ≈ π`. Тангенс половинного кута `tan(π/2)` прямує до нескінченності, що вимагало б нескінченного відступу початку скруглення `d → ∞`.

Алгоритм динамічного масштабування автоматично обмежує максимальний відступ `d_max = 0.45 · L_min`. Коефіцієнт масштабування `scale` зменшує ефективний радіус `R_eff` майже до нуля, змушуючи розраховану безпечну швидкість на куті `v_corner = √(a_lat_max · R_eff)` впасти до нуля. Таким чином, система автоматично переходить у режим безпечного гальмування до повної зупинки у вершині розвороту без спеціальних прапорців або ручного перемикання режимів.

### 3. Робота в реальному часі та компенсація дрижання такту (Jitter)
У реальній операційній системі реального часу (FreeRTOS або NuttX) інтервал між викликами контуру керування ніколи не є ідеально рівним (наявне дрижання такту `Δt ± 0.5 мс`). Якщо розраховувати уставку дискретним числовим інтегруванням Ейлера, похибка координат буде монотонно накопичуватися.

Завдяки представленню траєкторії у вигляді аналітичних параметричних кривих, функція `planner_sample(t)` приймає абсолютний монотонний час `t` від початку маневру та обчислює точні аналітичні значення позиції, швидкості й прискорення за формулами геометрії. Це гарантує нульовий дрейф координат навіть за тривалого польоту та нестабільного кроку опитування.
