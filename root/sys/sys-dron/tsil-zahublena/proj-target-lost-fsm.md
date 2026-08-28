# ⚙️ Автомат станів обробки втрати цілі та генератор пошукових траєкторій

Коли оптичний трекер на бортовому комп'ютері безпілотника втрачає об'єкт через оклюзію чи вихід із поля зору камери, контур керування не може миттєво зупинятися або перемикатися в аварійний режим. Будь-яка миттєва зупинка на крейсерській швидкості призводить до прольоту повз ціль або розгойдування апарата. Промисловий модуль супроводу реалізує детермінований кінцевий автомат (Finite State Machine, FSM), який послідовно виконує кінематичну екстраполяцію траєкторії, розгортає просторовий пошук підвісом і камерою за спіраллю Архімеда та здійснює сувору просторово-візуальну фільтрацію кандидатів на перезахоплення перед остаточною відмовою від супроводу.

---

### Архітектура автомата станів та структура даних

Модуль відстеження цілі працює з фіксованою частотою дискретизації (зазвичай 50–100 Гц) у складі бортового програмного забезпечення супровідного комп'ютера (Companion Computer) або безпосередньо в системному потоці автопілота. Автомат керує чотирма основними фазами життєвого циклу супроводу:

1. **`TRACKING` (Активний супровід):** кожний кадр постачає валідне вимірювання детектора. Фільтр стану цілі оновлює тривимірні координати, вектори швидкості та прискорення. Коваріація невизначеності мінімальна, а еталонний вектор візуальних ознак (Re-ID embedding) оновлюється з експоненційним згладжуванням для врахування поступової зміни ракурсу та освітлення.
2. **`COAST` (Кінематична екстраполяція):** потік детекцій раптово обірвався. Система продовжує прогнозувати положення цілі за моделлю постійної швидкості (Constant Velocity / Dead Reckoning) або постійного прискорення протягом часового вікна `T_coast` (0.5–2.0 с). Підвіс і дрон утримують прогнозну лінію візування, компенсуючи власний рух носія.
3. **`SEARCH` (Розширений пошук):** екстраполяція вичерпана, але ціль не з'явилася у прогнозованому вікні. Підвіс камери та курсовий канал безпілотника розгортають кутове сканування навколо центру прогнозованої зони за архімедовою спіраллю протягом `T_search` (2–10 с). Одночасно обчислювальний модуль може подати команду оптичного зменшення масштабу (Zoom-out) або невеликого набору висоти для розширення плями огляду на поверхні землі (Ground Footprint).
4. **`DISENGAGED` (Відмова від супроводу):** ліміт часу пошуку вичерпано. Модуль фіксує безповоротну втрату цілі, сповіщає високорівневий планувальник місії та ініціює безпечний маневр: зависання в точці (Loiter / Position Hold), повернення до виконання основного польотного завдання за точками маршруту або аварійне повернення на базу (Return-to-Launch, RTL).

Для захисту від помилкового захоплення чужих об'єктів (ID Switch / False Re-acquisition) будь-яке нове вимірювання детектора перевіряється за двома строгими бар'єрами: просторовим стробом Махаланобіса (Spatial Gating) та косинусною подібністю нейромережевого дескриптора Re-ID.

---

### Математичний апарат стробування та траєкторії пошуку

Просторовий строб відсікає об'єкти, положення яких статистично несумісне з накопиченою невизначеністю прогнозу. Квадрат відстані Махаланобіса обчислюється через вектор нев'язки та коваріаційну матрицю інновації:

```
d_M² = (z_meas - z_pred)ᵀ · S⁻¹ · (z_meas - z_pred)
```

Для вбудованих мікроконтролерів без апаратного блоку векторної алгебри повна матриця коваріації `S` часто апроксимується головними діагональними елементами дисперсій за осями `[s_x, s_y, s_z]`. Поріг стробування `γ_gate` обирається за таблицею розподілу хі-квадрат: для 3 ступенів вільності значення `γ_gate = 9.21` гарантує 99% довірчий інтервал.

Генератор траєкторії пошуку формує кути панорамування `pan` та нахилу `tilt` підвісу за рівнянням спіралі Архімеда у полярних координатах `r(θ) = a + b · θ`, де радіус `r` визначає кутове відхилення від прогнозованого центру, а кут `θ(t) = ω_s · t` зростає з постійною кутовою швидкістю. Крок витка `b` розраховується таким чином, щоб сусідні витки перекривалися на 20–30% миттєвого поля зору камери (FOV), що виключає появу «сліпих зон» між сканувальними колами.

---

### Реалізація на мовах C99 та C++20

:::tabs
@tab c
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define REID_EMBEDDING_DIM 128
#define PI_CONST 3.14159265358979323846f

typedef enum {
    TRACKER_STATE_TRACKING = 0,
    TRACKER_STATE_COAST,
    TRACKER_STATE_SEARCH,
    TRACKER_STATE_DISENGAGED
} tracker_state_t;

typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

typedef struct {
    float pan;
    float tilt;
} gimbal_angles_t;

typedef struct {
    vec3_t pos;
    vec3_t vel;
    float cov_pos[3];       /* діагональні елементи коваріації позиції */
    float descriptor[REID_EMBEDDING_DIM];
    bool valid;
} detection_t;

typedef struct {
    float t_coast_limit;    /* секунди */
    float t_search_limit;   /* секунди */
    float spiral_a;         /* початковий радіус спіралі (рад) */
    float spiral_b;         /* крок витка спіралі (рад/рад) */
    float spiral_omega;     /* кутова швидкість обходу (рад/с) */
    float gate_threshold;   /* квадрат відстані Махаланобіса */
    float reid_threshold;   /* мінімальна косинусна схожість */
    float process_noise;    /* приріст дисперсії при екстраполяції */
    float max_gimbal_rate;  /* обмеження кутової швидкості підвісу (рад/с) */
} tracker_config_t;

typedef struct {
    tracker_state_t state;
    vec3_t est_pos;
    vec3_t est_vel;
    float cov_pos[3];
    float ref_descriptor[REID_EMBEDDING_DIM];
    float state_timer;
    float search_theta;
    gimbal_angles_t gimbal_cmd;
    tracker_config_t config;
} target_lost_fsm_t;

/* Обчислення косинусної схожості дескрипторів Re-ID */
static float calc_reid_similarity(const float *a, const float *b, uint16_t dim) {
    float dot = 0.0f;
    float norm_a = 0.0f;
    float norm_b = 0.0f;
    for (uint16_t i = 0; i < dim; ++i) {
        dot += a[i] * b[i];
        norm_a += a[i] * a[i];
        norm_b += b[i] * b[i];
    }
    float denom = sqrtf(norm_a) * sqrtf(norm_b);
    return (denom > 1e-6f) ? (dot / denom) : 0.0f;
}

/* Перевірка просторового стробу Махаланобіса (діагональне наближення) */
static bool check_spatial_gate(const vec3_t *meas, const vec3_t *est, const float cov[3], float thresh) {
    float dx = meas->x - est->x;
    float dy = meas->y - est->y;
    float dz = meas->z - est->z;
    
    float sx = cov[0] > 1e-4f ? cov[0] : 1e-4f;
    float sy = cov[1] > 1e-4f ? cov[1] : 1e-4f;
    float sz = cov[2] > 1e-4f ? cov[2] : 1e-4f;

    float dist_sq = (dx * dx) / sx + (dy * dy) / sy + (dz * dz) / sz;
    return dist_sq <= thresh;
}

/* Ініціалізація автомата */
void target_lost_fsm_init(target_lost_fsm_t *fsm, const tracker_config_t *cfg) {
    fsm->state = TRACKER_STATE_DISENGAGED;
    fsm->est_pos = (vec3_t){0.0f, 0.0f, 0.0f};
    fsm->est_vel = (vec3_t){0.0f, 0.0f, 0.0f};
    fsm->cov_pos[0] = 1.0f;
    fsm->cov_pos[1] = 1.0f;
    fsm->cov_pos[2] = 1.0f;
    fsm->state_timer = 0.0f;
    fsm->search_theta = 0.0f;
    fsm->gimbal_cmd = (gimbal_angles_t){0.0f, 0.0f};
    fsm->config = *cfg;
}

/* Основний такт оновлення FSM */
void target_lost_fsm_update(target_lost_fsm_t *fsm, const detection_t *det, float dt) {
    bool reacquired = false;

    /* Валідація вхідної детекції, якщо вона надійшла */
    if (det != NULL && det->valid) {
        bool in_gate = true;
        bool reid_ok = true;

        if (fsm->state == TRACKER_STATE_COAST || fsm->state == TRACKER_STATE_SEARCH) {
            in_gate = check_spatial_gate(&det->pos, &fsm->est_pos, fsm->cov_pos, fsm->config.gate_threshold);
            float sim = calc_reid_similarity(det->descriptor, fsm->ref_descriptor, REID_EMBEDDING_DIM);
            reid_ok = (sim >= fsm->config.reid_threshold);
        }

        if (in_gate && reid_ok) {
            reacquired = true;
            fsm->est_pos = det->pos;
            fsm->est_vel = det->vel;
            fsm->cov_pos[0] = det->cov_pos[0];
            fsm->cov_pos[1] = det->cov_pos[1];
            fsm->cov_pos[2] = det->cov_pos[2];
            /* Експоненційне оновлення еталонного дескриптора */
            for (uint16_t i = 0; i < REID_EMBEDDING_DIM; ++i) {
                fsm->ref_descriptor[i] = 0.9f * fsm->ref_descriptor[i] + 0.1f * det->descriptor[i];
            }
        }
    }

    /* Логіка станів */
    switch (fsm->state) {
    case TRACKER_STATE_TRACKING:
        if (reacquired) {
            fsm->state_timer = 0.0f;
        } else {
            fsm->state = TRACKER_STATE_COAST;
            fsm->state_timer = 0.0f;
        }
        break;

    case TRACKER_STATE_COAST:
        if (reacquired) {
            fsm->state = TRACKER_STATE_TRACKING;
            fsm->state_timer = 0.0f;
        } else {
            fsm->state_timer += dt;
            /* Кінематична екстраполяція положення цілі */
            fsm->est_pos.x += fsm->est_vel.x * dt;
            fsm->est_pos.y += fsm->est_vel.y * dt;
            fsm->est_pos.z += fsm->est_vel.z * dt;

            /* Зростання невизначеності коваріації */
            fsm->cov_pos[0] += fsm->config.process_noise * dt;
            fsm->cov_pos[1] += fsm->config.process_noise * dt;
            fsm->cov_pos[2] += fsm->config.process_noise * dt;

            if (fsm->state_timer >= fsm->config.t_coast_limit) {
                fsm->state = TRACKER_STATE_SEARCH;
                fsm->state_timer = 0.0f;
                fsm->search_theta = 0.0f;
            }
        }
        break;

    case TRACKER_STATE_SEARCH:
        if (reacquired) {
            fsm->state = TRACKER_STATE_TRACKING;
            fsm->state_timer = 0.0f;
        } else {
            fsm->state_timer += dt;
            /* Генерація траєкторії Архімедової спіралі для підвісу */
            fsm->search_theta += fsm->config.spiral_omega * dt;
            float r = fsm->config.spiral_a + fsm->config.spiral_b * fsm->search_theta;
            fsm->gimbal_cmd.pan = r * cosf(fsm->search_theta);
            fsm->gimbal_cmd.tilt = r * sinf(fsm->search_theta);

            /* Продовження повільного дрейфу екстраполяції */
            fsm->est_pos.x += fsm->est_vel.x * dt * 0.5f;
            fsm->est_pos.y += fsm->est_vel.y * dt * 0.5f;
            fsm->cov_pos[0] += fsm->config.process_noise * dt * 2.0f;
            fsm->cov_pos[1] += fsm->config.process_noise * dt * 2.0f;

            if (fsm->state_timer >= fsm->config.t_search_limit) {
                fsm->state = TRACKER_STATE_DISENGAGED;
                fsm->state_timer = 0.0f;
            }
        }
        break;

    case TRACKER_STATE_DISENGAGED:
        if (reacquired) {
            fsm->state = TRACKER_STATE_TRACKING;
            fsm->state_timer = 0.0f;
        }
        break;
    }
}
```
@tab c++
```cpp
#include <array>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>

namespace drone::tracking {

inline constexpr std::size_t kReIdEmbeddingDim = 128;

enum class TrackerState : uint8_t {
    Tracking = 0,
    Coast,
    Search,
    Disengaged
};

struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    constexpr Vec3& operator+=(const Vec3& rhs) noexcept {
        x += rhs.x;
        y += rhs.y;
        z += rhs.z;
        return *this;
    }
};

struct GimbalAngles {
    float pan{0.0F};
    float tilt{0.0F};
};

struct Detection {
    Vec3 pos{};
    Vec3 vel{};
    std::array<float, 3> cov_pos{1.0F, 1.0F, 1.0F};
    std::array<float, kReIdEmbeddingDim> descriptor{};
};

struct TrackerConfig {
    float t_coast_limit{1.5F};
    float t_search_limit{5.0F};
    float spiral_a{0.05F};
    float spiral_b{0.02F};
    float spiral_omega{2.5F};
    float gate_threshold{9.21F};     // 99% квантиль хі-квадрат для 3 DoF
    float reid_threshold{0.65F};
    float process_noise{2.0F};
    float max_gimbal_rate{3.14F};
};

class TargetLostFsm {
public:
    explicit TargetLostFsm(const TrackerConfig& config) noexcept
        : config_{config} {}

    void update(const std::optional<Detection>& det, float dt) noexcept {
        const bool reacquired = try_reacquire(det);

        switch (state_) {
        case TrackerState::Tracking:
            if (reacquired) {
                state_timer_ = 0.0F;
            } else {
                state_ = TrackerState::Coast;
                state_timer_ = 0.0F;
            }
            break;

        case TrackerState::Coast:
            if (reacquired) {
                state_ = TrackerState::Tracking;
                state_timer_ = 0.0F;
            } else {
                state_timer_ += dt;
                extrapolate_target(dt, 1.0F);

                if (state_timer_ >= config_.t_coast_limit) {
                    state_ = TrackerState::Search;
                    state_timer_ = 0.0F;
                    search_theta_ = 0.0F;
                }
            }
            break;

        case TrackerState::Search:
            if (reacquired) {
                state_ = TrackerState::Tracking;
                state_timer_ = 0.0F;
            } else {
                state_timer_ += dt;
                generate_search_pattern(dt);
                extrapolate_target(dt, 0.5F);

                if (state_timer_ >= config_.t_search_limit) {
                    state_ = TrackerState::Disengaged;
                    state_timer_ = 0.0F;
                }
            }
            break;

        case TrackerState::Disengaged:
            if (reacquired) {
                state_ = TrackerState::Tracking;
                state_timer_ = 0.0F;
            }
            break;
        }
    }

    [[nodiscard]] TrackerState state() const noexcept { return state_; }
    [[nodiscard]] Vec3 estimated_position() const noexcept { return est_pos_; }
    [[nodiscard]] GimbalAngles gimbal_command() const noexcept { return gimbal_cmd_; }

private:
    [[nodiscard]] static float compute_reid_similarity(
        std::span<const float, kReIdEmbeddingDim> a,
        std::span<const float, kReIdEmbeddingDim> b) noexcept {
        float dot = 0.0F;
        float norm_a = 0.0F;
        float norm_b = 0.0F;
        for (std::size_t i = 0; i < kReIdEmbeddingDim; ++i) {
            dot += a[i] * b[i];
            norm_a += a[i] * a[i];
            norm_b += b[i] * b[i];
        }
        const float denom = std::sqrt(norm_a) * std::sqrt(norm_b);
        return (denom > 1e-6F) ? (dot / denom) : 0.0F;
    }

    [[nodiscard]] bool check_spatial_gate(const Vec3& meas) const noexcept {
        const float dx = meas.x - est_pos_.x;
        const float dy = meas.y - est_pos_.y;
        const float dz = meas.z - est_pos_.z;

        const float sx = std::max(cov_pos_[0], 1e-4F);
        const float sy = std::max(cov_pos_[1], 1e-4F);
        const float sz = std::max(cov_pos_[2], 1e-4F);

        const float dist_sq = (dx * dx) / sx + (dy * dy) / sy + (dz * dz) / sz;
        return dist_sq <= config_.gate_threshold;
    }

    bool try_reacquire(const std::optional<Detection>& det) noexcept {
        if (!det.has_value()) {
            return false;
        }

        if (state_ == TrackerState::Coast || state_ == TrackerState::Search) {
            if (!check_spatial_gate(det->pos)) {
                return false;
            }
            const float sim = compute_reid_similarity(det->descriptor, ref_descriptor_);
            if (sim < config_.reid_threshold) {
                return false;
            }
        }

        est_pos_ = det->pos;
        est_vel_ = det->vel;
        cov_pos_ = det->cov_pos;
        /* Експоненційне згладжування дескриптора */
        for (std::size_t i = 0; i < kReIdEmbeddingDim; ++i) {
            ref_descriptor_[i] = 0.9F * ref_descriptor_[i] + 0.1F * det->descriptor[i];
        }
        return true;
    }

    void extrapolate_target(float dt, float vel_scale) noexcept {
        est_pos_.x += est_vel_.x * dt * vel_scale;
        est_pos_.y += est_vel_.y * dt * vel_scale;
        est_pos_.z += est_vel_.z * dt * vel_scale;

        cov_pos_[0] += config_.process_noise * dt;
        cov_pos_[1] += config_.process_noise * dt;
        cov_pos_[2] += config_.process_noise * dt;
    }

    void generate_search_pattern(float dt) noexcept {
        search_theta_ += config_.spiral_omega * dt;
        const float r = config_.spiral_a + config_.spiral_b * search_theta_;
        gimbal_cmd_.pan = r * std::cos(search_theta_);
        gimbal_cmd_.tilt = r * std::sin(search_theta_);
    }

    TrackerConfig config_{};
    TrackerState state_{TrackerState::Disengaged};
    Vec3 est_pos_{};
    Vec3 est_vel_{};
    std::array<float, 3> cov_pos_{1.0F, 1.0F, 1.0F};
    std::array<float, kReIdEmbeddingDim> ref_descriptor_{};
    float state_timer_{0.0F};
    float search_theta_{0.0F};
    GimbalAngles gimbal_cmd_{};
};

} // namespace drone::tracking
```
:::

---

### Тонкощі інтеграції, обчислювальна складність та практичні пастки

Під час практичної інтеграції автомата станів у контур реального часу польотного стека виникають критичні інженерні нюанси, від яких безпосередньо залежить надійність функціонування комплексу:

1. **Необмежене зростання стробу невизначеності (Covariance Explosion):**
   Якщо ціль рухається з високою швидкістю, тривала екстраполяція в умовах відсутності вимірювань розширює коваріаційну матрицю `cov_pos` до десятків метрів. Якщо строб стає суттєво більшим за миттєве поле зору камери, критерій Махаланобіса втрачає селективність і починає пропускати будь-який сторонній об'єкт у кадрі. Щоб уникнути цього, порогову коваріацію обмежують зверху насиченням (Saturation Clamping), а вагу перевірки зміщують у бік візуального дескриптора Re-ID, підвищуючи поріг `reid_threshold`.

2. **Кінематичні обмеження підвісу та зрізання кутових швидкостей (Rate Limiting):**
   Аналітичне рівняння спіралі Архімеда генерує кути `pan` та `tilt` без урахування максимальної кутової швидкості сервоприводів. На перших витках швидкість обходу є високою, а на зовнішніх витках амплітуда може перевищити механічні упори підвісу (Mechanical Endstops). Генератор пошуку обов'язково повинен містити насичення кутів та фільтр швидкості наростання уставки (Slew Rate Limiter), щоб уникнути втрати кроків кроковими двигунами або перегріву безколекторних моторів підвісу.

3. **Синхронізація з курсовим рухом безпілотника та запобігання автоколиванням:**
   Якщо діапазону кутів підвісу недостатньо для покриття всієї зони невизначеності, автопілот переводить безпілотник у курсове сканування за рисканням (Yaw Sweep) або виконує набір висоти. При цьому команди зміщення підвісу комбінуються з орієнтацією дрона у глобальній системі координат NED, щоб уникнути явища паразитної взаємної компенсації поворотів камери та рами.

4. **Дрейф еталонного дескриптора зовнішності:**
   Помилкове оновлення еталонного дескриптора напівпрозорою оклюзією (наприклад, гілками дерев) поступово спотворює еталонний вектор ознак. Оновлення дескриптора через експоненційне згладжування дозволяється виконувати лише тоді, коли оцінка якості вимірювання детектора перевищує жорсткий поріг впевненості (`confidence > 0.85`).
