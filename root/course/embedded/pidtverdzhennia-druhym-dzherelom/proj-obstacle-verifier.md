# ⚙️ Верифікатор виявлення перешкод: трирівневий фільтр арбітражу

Вбудовані системи комп'ютерного зору на базі легковагих згорткових нейромереж генерують гіпотези про наявність перешкод у вигляді прямокутників виявлення (`bounding box`) із певною ймовірністю класифікатора. Проте статистичні моделі не володіють знанням просторової геометрії, законів оптики чи збереження імпульсу. Оптичні артефакти, різкі перепади сонячного освітлення, бруд на захисному склі або текстури на асфальті здатні змусити модель видати максимальну впевненість для об'єкта, якого фізично не існує у тривимірному просторі.

Якщо бортовий автопілот транслює сирі виходи нейромережі безпосередньо у контур керування приводами, робототехнічна платформа отримує небезпечні фантомні гальмування на швидкості, аварійні зриви курсів або навпаки — зіткнення з реальними перешкодами, пропущеними через незвичний ракурс чи складні тіні.

Задача даного інженерного модуля — реалізувати повністю детермінований верифікатор арбітражу для вбудованих мікроконтролерів (MCU) та процесорів реального часу. Верифікатор приймає сирі виявлення детектора і послідовно пропускає кожну гіпотезу крізь три незалежні фізичні бар'єри:
1. **Геометричний бар'єр проєкції:** перевірка відповідності піксельних габаритів прямокутника очікуваному фізичному розміру об'єкта на розрахованій дистанції за моделлю камери-обскури.
2. **Давачевий крос-чекінг:** просторове зіставлення кутового сектора піксельного боксу із фізичним відгуком активного далекоміра (Time-of-Flight / лідар / радар).
3. **Кінематичний строб Ньютона:** фільтрація стрибків координат за допомогою еліпсоїда допустимого переміщення з урахуванням граничного прискорення та швидкості.

Лише ті гіпотези, які пройшли всі три бар'єри та підтвердили просторово-часову стабільність у скінченному автоматі трекера, набувають статусу підтверджених перешкод для планувальника траєкторії.

---

## 1. Математична модель інваріантів та алгоритм

### Геометричний інваріант масштабу
Для каліброваної камери з фокусною відстанню `f_px` (у пікселях) та фізичною висотою об'єкта `H_real` (у метрах), проєкція висоти на матрицю `h_px` на відстані `Z` опиняється у жорсткому геометричному зв'язку:

```
h_expected = (f_px · H_real) / Z
```

Допустимий діапазон піксельного розміру визначається з урахуванням природної варіативності габаритів об'єкта вибраного класу `[H_min, H_max]`:

```
h_min = (f_px · H_min) / Z
h_max = (f_px · H_max) / Z
```

Якщо детектор фіксує прямокутник із висотою `h_measured < h_min · (1 - ε)` або `h_measured > h_max · (1 + ε)`, де `ε` — допустима похибка апроксимації меж нейромережею (зазвичай 25–35%), виявлення класифікується як геометрично неможливе та відкидається ще до обчислення траєкторії.

### Просторово-часове узгодження з далекоміром
Далекомір (одноточковий ToF, матричний лідар або радар) встановлений на шасі із відомим просторовим зсувом відносно оптичного центру камери (вектор трансляції `T = [t_x, t_y, t_z]ᵀ` та матриця повороту `R`). Точка простору `P_sensor = [0, 0, Z_tof]ᵀ` трансформується в систему координат камери:

```
P_cam = R · P_sensor + T
```

Після чого проєктується на площину пікселів матриці:

```
u_proj = c_x + f_x · (X_cam / Z_cam)
v_proj = c_y + f_y · (Y_cam / Z_cam)
```

Якщо точка `(u_proj, v_proj)` потрапляє всередину габаритного прямокутника `[u_min, v_min, u_max, v_max]`, давач відстані підтверджує наявність непроникної твердої поверхні у зоні виявленої нейромережею перешкоди.

### Кінематичний строб Ньютона
Для підтвердженого треку з попереднім вектором стану `x(t-1) = [x, y, z, v_x, v_y, v_z]ᵀ` екстраполюється очікувана позиція в поточному кадрі:

```
x_pred = x + v_x · Δt
y_pred = y + v_y · Δt
z_pred = z + v_z · Δt
```

Радіус стробу валідації `R_gate` обмежується максимально можливим фізичним прискоренням `a_max` для даного класу перешкоди:

```
R_gate = 0.5 · a_max · Δt² + σ_meas
```

Якщо евклідова відстань `||P_meas - P_pred|| > R_gate`, нове виявлення не прив'язується до наявного треку, запобігаючи стрибкам трекера між випадковими оптичними відблисками та різними цілями.

---

## 2. Реалізація верифікатора

Нижче наведено модульну реалізацію конвеєра валідації та арбітражу двома мовами програмування: на чистому ANSI C (C99) з фіксованими статичними пулами пам'яті без динамічних алокацій (відповідно до вимог стандартів безпеки MISRA C), та на ідіоматичному C++20 із застосуванням сильної типізації, просторів імен, методів інкапсуляції та контейнерів фіксованого розміру `std::array` і `std::span`.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define MAX_TRACKS 8
#define CONFIRMATION_THRESHOLD_M 3
#define HISTORY_WINDOW_N 4
#define MAX_LOST_FRAMES 5

/* Класифікація статусу арбітражу */
typedef enum {
    ARBITRATION_TENTATIVE = 0,
    ARBITRATION_VALIDATING,
    ARBITRATION_CONFIRMED,
    ARBITRATION_COASTING,
    ARBITRATION_REJECTED
} ArbitrationState;

/* Класи об'єктів та їхні фізичні габарити */
typedef enum {
    CLASS_PERSON = 0,
    CLASS_VEHICLE,
    CLASS_OBSTACLE_BOX,
    CLASS_COUNT
} ObjectClass;

typedef struct {
    float h_min; /* мінімальна фізична висота (м) */
    float h_max; /* максимальна фізична висота (м) */
    float v_max; /* максимальна швидкість (м/с) */
    float a_max; /* максимальне прискорення (м/с^2) */
} ClassPhysicsLimits;

static const ClassPhysicsLimits CLASS_LIMITS[CLASS_COUNT] = {
    [CLASS_PERSON]       = { .h_min = 0.6f, .h_max = 2.0f, .v_max = 8.0f,  .a_max = 12.0f },
    [CLASS_VEHICLE]      = { .h_min = 1.2f, .h_max = 3.5f, .v_max = 40.0f, .a_max = 15.0f },
    [CLASS_OBSTACLE_BOX] = { .h_min = 0.2f, .h_max = 2.5f, .v_max = 2.0f,  .a_max = 5.0f  }
};

/* Внутрішні параметри камери (Intrinsics) */
typedef struct {
    float fx;
    float fy;
    float cx;
    float cy;
} CameraIntrinsics;

/* Вихід детектора нейромережі */
typedef struct {
    float u_min;
    float v_min;
    float u_max;
    float v_max;
    float score;
    ObjectClass cls;
} BoundingBoxDetection;

/* Дані активного далекоміра (ToF / Radar) */
typedef struct {
    float distance_m; /* дистанція за променем */
    float offset_x;   /* зсув сенсора від камери X */
    float offset_y;   /* зсув сенсора від камери Y */
    float offset_z;   /* зсув сенсора від камери Z */
    bool valid;       /* прапорець валідності сигналу */
} RangeSensorData;

/* Трек об'єкта */
typedef struct {
    uint32_t track_id;
    ArbitrationState state;
    ObjectClass cls;
    float pos_x;
    float pos_y;
    float pos_z;
    float vel_x;
    float vel_y;
    float vel_z;
    uint8_t hit_history; /* бітова маска останніх N кадрів */
    uint8_t lost_counter;
    bool is_active;
} ObjectTrack;

typedef struct {
    CameraIntrinsics cam;
    ObjectTrack tracks[MAX_TRACKS];
    uint32_t next_track_id;
} ObstacleVerifier;

void verifier_init(ObstacleVerifier* v, float fx, float fy, float cx, float cy) {
    v->cam.fx = fx;
    v->cam.fy = fy;
    v->cam.cx = cx;
    v->cam.cy = cy;
    v->next_track_id = 1;
    for (int i = 0; i < MAX_TRACKS; ++i) {
        v->tracks[i].is_active = false;
        v->tracks[i].state = ARBITRATION_REJECTED;
    }
}

/* 1. Геометрична верифікація масштабу */
bool verify_geometry(const CameraIntrinsics* cam, const BoundingBoxDetection* det, float distance_m) {
    if (distance_m < 0.1f) return false;
    
    float h_measured_px = det->v_max - det->v_min;
    if (h_measured_px <= 1.0f) return false;

    const ClassPhysicsLimits* lim = &CLASS_LIMITS[det->cls];
    float h_expected_min_px = (cam->fy * lim->h_min) / distance_m;
    float h_expected_max_px = (cam->fy * lim->h_max) / distance_m;

    /* Допуск 30% на кути нахилу камери та неточності регресії меж */
    float tol = 0.30f;
    if (h_measured_px < h_expected_min_px * (1.0f - tol)) return false;
    if (h_measured_px > h_expected_max_px * (1.0f + tol)) return false;

    return true;
}

/* 2. Сенсорний крос-чекінг із далекоміром */
bool verify_sensor_cross_check(const CameraIntrinsics* cam, const BoundingBoxDetection* det, const RangeSensorData* rng) {
    if (!rng->valid || rng->distance_m <= 0.05f) return false;

    /* Проєкція точки відбиття далекоміра на матрицю камери */
    float z_cam = rng->distance_m + rng->offset_z;
    if (z_cam <= 0.05f) return false;

    float x_cam = rng->offset_x;
    float y_cam = rng->offset_y;

    float u_proj = cam->cx + cam->fx * (x_cam / z_cam);
    float v_proj = cam->cy + cam->fy * (y_cam / z_cam);

    /* Перевіряємо потрапляння проєкції променя у bounding box */
    if (u_proj >= det->u_min && u_proj <= det->u_max &&
        v_proj >= det->v_min && v_proj <= det->v_max) {
        return true;
    }

    return false;
}

/* 3. Кінематичний строб */
bool verify_kinematics(const ObjectTrack* trk, float meas_x, float meas_y, float meas_z, float dt_sec) {
    if (dt_sec <= 0.0f) return false;

    float pred_x = trk->pos_x + trk->vel_x * dt_sec;
    float pred_y = trk->pos_y + trk->vel_y * dt_sec;
    float pred_z = trk->pos_z + trk->vel_z * dt_sec;

    float dx = meas_x - pred_x;
    float dy = meas_y - pred_y;
    float dz = meas_z - pred_z;
    float dist_sq = dx * dx + dy * dy + dz * dz;

    const ClassPhysicsLimits* lim = &CLASS_LIMITS[trk->cls];
    /* Максимальний радіус стробу: 0.5 * a_max * dt^2 + похибка вимірювання (0.35 м) */
    float r_gate = 0.5f * lim->a_max * dt_sec * dt_sec + 0.35f;
    
    return (dist_sq <= (r_gate * r_gate));
}

/* Оновлення автомата станів арбітражу */
void verifier_update(ObstacleVerifier* v, const BoundingBoxDetection* detections, size_t det_count,
                     const RangeSensorData* range, float dt_sec) {
    /* 1. Позначити всі треки як неоновлені в цьому кадрі */
    bool track_matched[MAX_TRACKS] = { false };

    /* 2. Обробка виявлень */
    for (size_t i = 0; i < det_count; ++i) {
        const BoundingBoxDetection* det = &detections[i];
        if (det->score < 0.40f) continue;

        /* Використовуємо далекомір або проєкційну глибину */
        float est_dist = range->valid ? range->distance_m : 2.5f;

        /* Геометричний фільтр */
        if (!verify_geometry(&v->cam, det, est_dist)) {
            continue; /* Галюцинація розміру відкинута */
        }

        /* Оцінка 3D координат центру об'єкта */
        float u_c = (det->u_min + det->u_max) * 0.5f;
        float v_c = (det->v_min + det->v_max) * 0.5f;
        float pos_z = est_dist;
        float pos_x = (u_c - v->cam.cx) * pos_z / v->cam.fx;
        float pos_y = (v_c - v->cam.cy) * pos_z / v->cam.fy;

        /* Зіставлення з наявними треками */
        int matched_idx = -1;
        float min_dist_sq = 1e9f;

        for (int t = 0; t < MAX_TRACKS; ++t) {
            if (!v->tracks[t].is_active || track_matched[t]) continue;
            if (v->tracks[t].cls != det->cls) continue;

            if (verify_kinematics(&v->tracks[t], pos_x, pos_y, pos_z, dt_sec)) {
                float dx = pos_x - v->tracks[t].pos_x;
                float dy = pos_y - v->tracks[t].pos_y;
                float dz = pos_z - v->tracks[t].pos_z;
                float d_sq = dx * dx + dy * dy + dz * dz;
                if (d_sq < min_dist_sq) {
                    min_dist_sq = d_sq;
                    matched_idx = t;
                }
            }
        }

        if (matched_idx >= 0) {
            /* Оновлення існуючого треку */
            ObjectTrack* trk = &v->tracks[matched_idx];
            track_matched[matched_idx] = true;
            trk->lost_counter = 0;
            trk->hit_history = ((trk->hit_history << 1) | 1) & ((1 << HISTORY_WINDOW_N) - 1);

            /* Оцінка швидкості згладженим фільтром */
            trk->vel_x = 0.7f * trk->vel_x + 0.3f * ((pos_x - trk->pos_x) / dt_sec);
            trk->vel_y = 0.7f * trk->vel_y + 0.3f * ((pos_y - trk->pos_y) / dt_sec);
            trk->vel_z = 0.7f * trk->vel_z + 0.3f * ((pos_z - trk->pos_z) / dt_sec);
            trk->pos_x = pos_x;
            trk->pos_y = pos_y;
            trk->pos_z = pos_z;

            /* Рахуємо кількість попадань у вікні N */
            int hits = 0;
            for (int b = 0; b < HISTORY_WINDOW_N; ++b) {
                if (trk->hit_history & (1 << b)) hits++;
            }

            /* Зміна станів FSM */
            if (trk->state == ARBITRATION_TENTATIVE && hits >= 2) {
                trk->state = ARBITRATION_VALIDATING;
            }
            if (trk->state == ARBITRATION_VALIDATING && hits >= CONFIRMATION_THRESHOLD_M) {
                trk->state = ARBITRATION_CONFIRMED;
            }
            if (trk->state == ARBITRATION_COASTING) {
                trk->state = ARBITRATION_CONFIRMED;
            }
        } else {
            /* Створення нового треку-кандидата у вільному слоті */
            for (int t = 0; t < MAX_TRACKS; ++t) {
                if (!v->tracks[t].is_active) {
                    v->tracks[t].track_id = v->next_track_id++;
                    v->tracks[t].is_active = true;
                    v->tracks[t].state = ARBITRATION_TENTATIVE;
                    v->tracks[t].cls = det->cls;
                    v->tracks[t].pos_x = pos_x;
                    v->tracks[t].pos_y = pos_y;
                    v->tracks[t].pos_z = pos_z;
                    v->tracks[t].vel_x = 0.0f;
                    v->tracks[t].vel_y = 0.0f;
                    v->tracks[t].vel_z = 0.0f;
                    v->tracks[t].hit_history = 1;
                    v->tracks[t].lost_counter = 0;
                    track_matched[t] = true;
                    break;
                }
            }
        }
    }

    /* 3. Оновлення незбіжних треків (Coast / Drop) */
    for (int t = 0; t < MAX_TRACKS; ++t) {
        if (!v->tracks[t].is_active || track_matched[t]) continue;

        ObjectTrack* trk = &v->tracks[t];
        trk->lost_counter++;
        trk->hit_history = (trk->hit_history << 1) & ((1 << HISTORY_WINDOW_N) - 1);

        /* Екстраполяція руху */
        trk->pos_x += trk->vel_x * dt_sec;
        trk->pos_y += trk->vel_y * dt_sec;
        trk->pos_z += trk->vel_z * dt_sec;

        if (trk->state == ARBITRATION_CONFIRMED) {
            trk->state = ARBITRATION_COASTING;
        }

        if (trk->lost_counter >= MAX_LOST_FRAMES || trk->state == ARBITRATION_TENTATIVE) {
            trk->state = ARBITRATION_REJECTED;
            trk->is_active = false;
        }
    }
}
```
```cpp
#include <array>
#include <cstdint>
#include <cmath>
#include <optional>
#include <span>

namespace obstacle_fusion {

constexpr size_t MaxTracks = 8;
constexpr uint8_t ConfirmationThresholdM = 3;
constexpr uint8_t HistoryWindowN = 4;
constexpr uint8_t MaxLostFrames = 5;

enum class ArbitrationState : uint8_t {
    Tentative = 0,
    Validating,
    Confirmed,
    Coasting,
    Rejected
};

enum class ObjectClass : uint8_t {
    Person = 0,
    Vehicle,
    ObstacleBox,
    Count
};

struct ClassPhysicsLimits {
    float h_min;
    float h_max;
    float v_max;
    float a_max;
};

constexpr std::array<ClassPhysicsLimits, static_cast<size_t>(ObjectClass::Count)> Limits = {{
    { 0.6f, 2.0f, 8.0f,  12.0f }, // Person
    { 1.2f, 3.5f, 40.0f, 15.0f }, // Vehicle
    { 0.2f, 2.5f, 2.0f,  5.0f  }  // ObstacleBox
}};

struct CameraIntrinsics {
    float fx;
    float fy;
    float cx;
    float cy;
};

struct BoundingBoxDetection {
    float u_min;
    float v_min;
    float u_max;
    float v_max;
    float score;
    ObjectClass cls;
};

struct RangeSensorData {
    float distance_m{0.0f};
    float offset_x{0.0f};
    float offset_y{0.0f};
    float offset_z{0.0f};
    bool valid{false};
};

struct Vector3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3D operator+(const Vector3D& o) const noexcept {
        return { x + o.x, y + o.y, z + o.z };
    }
    constexpr Vector3D operator-(const Vector3D& o) const noexcept {
        return { x - o.x, y - o.y, z - o.z };
    }
    constexpr float length_squared() const noexcept {
        return x * x + y * y + z * z;
    }
};

class ObjectTrack {
public:
    uint32_t track_id{0};
    ArbitrationState state{ArbitrationState::Tentative};
    ObjectClass cls{ObjectClass::ObstacleBox};
    Vector3D position;
    Vector3D velocity;
    uint8_t hit_history{0};
    uint8_t lost_counter{0};
    bool is_active{false};

    [[nodiscard]] uint8_t hit_count() const noexcept {
        uint8_t count = 0;
        for (uint8_t b = 0; b < HistoryWindowN; ++b) {
            if ((hit_history >> b) & 1U) ++count;
        }
        return count;
    }
};

class ObstacleVerifier {
public:
    constexpr explicit ObstacleVerifier(CameraIntrinsics cam) noexcept
        : cam_(cam) {}

    [[nodiscard]] bool verify_geometry(const BoundingBoxDetection& det, float distance_m) const noexcept {
        if (distance_m < 0.1f) return false;
        
        const float h_measured = det.v_max - det.v_min;
        if (h_measured <= 1.0f) return false;

        const auto& lim = Limits[static_cast<size_t>(det.cls)];
        const float h_exp_min = (cam_.fy * lim.h_min) / distance_m;
        const float h_exp_max = (cam_.fy * lim.h_max) / distance_m;

        constexpr float Tolerance = 0.30f;
        return (h_measured >= h_exp_min * (1.0f - Tolerance) &&
                h_measured <= h_exp_max * (1.0f + Tolerance));
    }

    [[nodiscard]] bool verify_sensor_cross_check(const BoundingBoxDetection& det,
                                                 const RangeSensorData& rng) const noexcept {
        if (!rng.valid || rng.distance_m <= 0.05f) return false;

        const float z_cam = rng.distance_m + rng.offset_z;
        if (z_cam <= 0.05f) return false;

        const float u_proj = cam_.cx + cam_.fx * (rng.offset_x / z_cam);
        const float v_proj = cam_.cy + cam_.fy * (rng.offset_y / z_cam);

        return (u_proj >= det.u_min && u_proj <= det.u_max &&
                v_proj >= det.v_min && v_proj <= det.v_max);
    }

    [[nodiscard]] bool verify_kinematics(const ObjectTrack& trk, const Vector3D& meas_pos,
                                         float dt_sec) const noexcept {
        if (dt_sec <= 0.0f) return false;

        const Vector3D pred_pos = trk.position + Vector3D{ trk.velocity.x * dt_sec,
                                                           trk.velocity.y * dt_sec,
                                                           trk.velocity.z * dt_sec };
        const float dist_sq = (meas_pos - pred_pos).length_squared();

        const auto& lim = Limits[static_cast<size_t>(trk.cls)];
        const float r_gate = 0.5f * lim.a_max * dt_sec * dt_sec + 0.35f;

        return dist_sq <= (r_gate * r_gate);
    }

    void update(std::span<const BoundingBoxDetection> detections,
                const RangeSensorData& range, float dt_sec) noexcept {
        std::array<bool, MaxTracks> matched{};

        for (const auto& det : detections) {
            if (det.score < 0.40f) continue;

            const float est_dist = range.valid ? range.distance_m : 2.5f;
            if (!verify_geometry(det, est_dist)) continue;

            const float u_c = (det.u_min + det.u_max) * 0.5f;
            const float v_c = (det.v_min + det.v_max) * 0.5f;
            const Vector3D meas_pos{
                (u_c - cam_.cx) * est_dist / cam_.fx,
                (v_c - cam_.cy) * est_dist / cam_.fy,
                est_dist
            };

            std::optional<size_t> best_idx;
            float min_d_sq = 1e9f;

            for (size_t t = 0; t < MaxTracks; ++t) {
                if (!tracks_[t].is_active || matched[t]) continue;
                if (tracks_[t].cls != det.cls) continue;

                if (verify_kinematics(tracks_[t], meas_pos, dt_sec)) {
                    const float d_sq = (meas_pos - tracks_[t].position).length_squared();
                    if (d_sq < min_d_sq) {
                        min_d_sq = d_sq;
                        best_idx = t;
                    }
                }
            }

            if (best_idx.has_value()) {
                const size_t idx = *best_idx;
                auto& trk = tracks_[idx];
                matched[idx] = true;
                trk.lost_counter = 0;
                trk.hit_history = static_cast<uint8_t>(((trk.hit_history << 1) | 1U) & ((1U << HistoryWindowN) - 1U));

                trk.velocity.x = 0.7f * trk.velocity.x + 0.3f * ((meas_pos.x - trk.position.x) / dt_sec);
                trk.velocity.y = 0.7f * trk.velocity.y + 0.3f * ((meas_pos.y - trk.position.y) / dt_sec);
                trk.velocity.z = 0.7f * trk.velocity.z + 0.3f * ((meas_pos.z - trk.position.z) / dt_sec);
                trk.position = meas_pos;

                const uint8_t hits = trk.hit_count();
                if (trk.state == ArbitrationState::Tentative && hits >= 2) {
                    trk.state = ArbitrationState::Validating;
                }
                if (trk.state == ArbitrationState::Validating && hits >= ConfirmationThresholdM) {
                    trk.state = ArbitrationState::Confirmed;
                }
                if (trk.state == ArbitrationState::Coasting) {
                    trk.state = ArbitrationState::Confirmed;
                }
            } else {
                for (auto& trk : tracks_) {
                    if (!trk.is_active) {
                        trk.track_id = next_track_id_++;
                        trk.is_active = true;
                        trk.state = ArbitrationState::Tentative;
                        trk.cls = det.cls;
                        trk.position = meas_pos;
                        trk.velocity = { 0.0f, 0.0f, 0.0f };
                        trk.hit_history = 1;
                        trk.lost_counter = 0;
                        break;
                    }
                }
            }
        }

        for (size_t t = 0; t < MaxTracks; ++t) {
            if (!tracks_[t].is_active || matched[t]) continue;

            auto& trk = tracks_[t];
            trk.lost_counter++;
            trk.hit_history = static_cast<uint8_t>((trk.hit_history << 1) & ((1U << HistoryWindowN) - 1U));

            trk.position.x += trk.velocity.x * dt_sec;
            trk.position.y += trk.velocity.y * dt_sec;
            trk.position.z += trk.velocity.z * dt_sec;

            if (trk.state == ArbitrationState::Confirmed) {
                trk.state = ArbitrationState::Coasting;
            }

            if (trk.lost_counter >= MaxLostFrames || trk.state == ArbitrationState::Tentative) {
                trk.state = ArbitrationState::Rejected;
                trk.is_active = false;
            }
        }
    }

    [[nodiscard]] std::span<const ObjectTrack> tracks() const noexcept {
        return tracks_;
    }

private:
    CameraIntrinsics cam_;
    std::array<ObjectTrack, MaxTracks> tracks_{};
    uint32_t next_track_id_{1};
};

} // namespace obstacle_fusion
```
:::

---

## 3. Покрокове простеження обробки сигналу

Щоб зрозуміти динаміку роботи трьох бар'єрів, простежимо реакцію системи на два послідовні сценарії: раптову оптичну галюцинацію детектора та реальну фізичну перешкоду.

### Сценарій А: Відблиск сонця (Галюцинація детектора)
1. **Кадр t=0:** Камера фіксує спалах світла на відполірованому корпусі верстата. Детектор видає прямокутник з координатами `[u_min=300, v_min=200, u_max=310, v_max=215]` пікселів, що відповідає висоті `h = 15` пікселів. Клас розпізнавання — «Людина», скор `P = 0.95`.
2. **Геометрична фільтрація:** Далекомір повідомляє про відсутність сигналу або дистанцію до стіни цеху `Z = 2.0` м. Очікувана висота людини на дистанції 2 метри для камери з `f_y = 600` становить `h_exp ∈ [180, 600]` пікселів. Виміряна висота 15 пікселів у 12 разів менша за допустиму межу.
3. **Вердикт:** Верифікатор негайно відкидає гіпотезу на геометричному етапі. Жодного треку не створюється, FSM залишається у стані спокою.

### Сценарій Б: Поява пішохода на шляху руху
1. **Кадр t=0 (Первинне виявлення):** Пішохід виходить із-за колони на відстані `Z = 3.5` м. Детектор повертає бокс висотою `h = 300` пікселів (`h_exp ∈ [100, 350]`). Геометрія валідна. Далекомір реєструє `Z_tof = 3.4` м. Промінь потрапляє всередину прямокутника. Створюється новий трек у стані `TENTATIVE`. Автопілот продовжує плановий рух, не смикаючи гальма.
2. **Кадр t=1 (Підтвердження геометрії, t + 33 мс):** Виявлення повторюється на дистанції `Z = 3.4` м із плавним зсувом координат. Кінематичний строб підтверджує переміщення менше 0.1 м. Стан переходить у `VALIDATING`.
3. **Кадр t=2 (Фіксація цілі, t + 66 мс):** Третє успішне зіставлення (`hit_history = 0b0111`). Умова «3 з 4» виконана. Стан FSM переходить у `CONFIRMED`.
4. **Реакція планувальника:** Лише на 66-й мілісекунді підтверджений тривимірний вектор перешкоди надходить у контур планування траєкторії, ініціюючи плавне гальмування або побудову кривої об'їзду.

---

## 4. Інженерні пастки та крайові випадки

Під час інтеграції даного верифікатора на реальні бортові контролери виникають типові підводні камені, що вимагають апаратного та алгоритмічного узгодження:

1. **Несинхронність часових міток (Latency Jitter):** нейромережевий інференс на NPU або GPU займає від 15 до 60 мс, тоді як далекомір ToF опитується по шині I2C/SPI за 2 мс. Якщо зіставляти поточний кадр ToF із запізнілим кадром детектора, швидкий поворот корпусу дрона чи робота зсуває просторовий конус. *Рішення:* збереження кільцевого буфера одометрії та позиціонування сенсорів із прив'язкою вимірювань за точними мітками апаратного таймера `timestamp_us`.
2. **Сліпі зони та дзеркальне поглинання ToF:** чорні матові тканини або поліровані похилі металеві поверхні не повертають відбитий промінь інфрачервоного далекоміра (сигнал `range.valid == false`). У такому випадку верифікатор переходить у режим геометрично-кінематичного спостереження (`VALIDATING`), але вимагає довшої часової вибірки (наприклад, 4 з 5 кадрів замість 2 з 3), перш ніж передати уставку на гальмування.
3. **Паралакс при близьких дистанціях:** коли об'єкт наближається ближче 30 см, фізична відстань між об'єктивом камери та емітером лідара створює значний кутовий паралакс. Формула крос-чекінгу обов'язково повинна враховувати вектор статичного зсуву сенсорів `[offset_x, offset_y, offset_z]`, інакше промінь вийде за межі bounding box при повній фізичній наявності перешкоди.
4. **Чисельна стабільність матричних операцій:** під час обчислення дистанції Махаланобіса на 32-бітних мікроконтролерах із ядром ARM Cortex-M4F операції обернення коваріаційної матриці `S⁻¹` можуть страждати від втрати точності через малі власні числа. Рекомендується додавати регуляризаційний діагональний шум `S = S + ε · I` (де `ε = 10⁻⁴`), що гарантує додатну визначеність матриці та захищає FPU від виникнення переповнень `NaN`.
