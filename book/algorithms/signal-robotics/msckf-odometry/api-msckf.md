# 📋 Інтерфейс та конфігурація модуля оцінювача MSCKF

Програмний контракт оцінювача MSCKF приймає високочастотний потік інерційних вимірів IMU та пакети спостережень оптичного трекінгу точок, повертає поточну 6-DOF позу зі швидкістю і зсувами давачів та видає діагностику чисельної стійкості. Робота модуля визначається структурами конфігурації, форматами вхідних і вихідних повідомлень, кодами помилок, інваріантами пам'яті, правилами налаштування параметрів та сигнатурами функцій керування станом фільтра.

## Структури конфігурації

Перед початком роботи оцінювач налаштовується структурою `MsckfConfig`. Вона визначає фізичні шуми сенсорів, просторові екстринсики, розміри буферів та критерії відсіювання викидів.

Кожен параметр конфігурації має чітке фізичне значення:
- `body_T_cam` та `body_R_cam`: вектор зміщення (у метрах) та кватерніон повороту оптичного центру камери відносно центру вимірювань IMU. Точність екстринсиків критично впливає на якість клонування стану. Помилка калібрування в 1 см або 0.5° призводить до появи систематичного дрейфу оцінки швидкості під час маневрів обертання.
- `max_window_size`: максимальна кількість поз камери в ковзному вікні (типово 15–20 поз). Більше вікно покращує тріангуляцію повільно рухомих об'єктів за рахунок довшого базового плеча спостереження, але збільшує обчислювальне навантаження на крок маргіналізації як `O(N³)`.
- `min_track_length`: мінімальна кількість спостережень однієї точки (типово 3), необхідна для спроби тріангуляції та корекції Калмана.
- `gyro_noise_density` та `accel_noise_density`: спектральна густина шуму давачів, що визначає матрицю шуму процесу `Q`. Заниження цих параметрів робить фільтр занадто самовпевненим у власному інтегруванні IMU, що веде до розбіжності. Завищення призводить до надмірної чутливості до шумів оптичного трекінгу.
- `gyro_bias_random_walk` та `accel_bias_random_walk`: параметри нестабільності нулів сенсорів (випадкового блукання зсувів). Визначають швидкість адаптації фільтра до повільного температурного дрейфу давачів.
- `pixel_noise_std`: середньоквадратичне відхилення похибки знаходження кутів на кадрі в нормованих координатах (типово 1–2 пікселі, поділені на фокусну відстань).
- `min_triangulation_deg`: мінімальний просторовий кут між променями зору (типово 1.5–2.5 градуси). Захищає фільтр від спроб розрахунку орієнтирів із виродженою нескінченною глибиною під час чистого обертання або руху по прямій на точку.
- `chi2_rejection_prob`: квантиль розподілу хі-квадрат для відсіювання викидів (outliers).
- `enable_fej`: активація режиму Першої Оцінки Якобіанів (First-Estimate Jacobians) для запобігання штучній спостережуваності кута курсу.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    double x, y, z;
} MsckfVec3;

typedef struct {
    double w, x, y, z;
} MsckfQuat;

typedef struct {
    /* Геометричне калібрування камери відносно IMU (Body -> Camera) */
    MsckfVec3 body_T_cam;         /* вектор зміщення камери у системі корпусу, м */
    MsckfQuat body_R_cam;         /* кватерніон повороту камери відносно корпусу */
    
    /* Параметри ковзного вікна */
    uint32_t max_window_size;     /* максимальна кількість поз камери (типово 15–20) */
    uint32_t min_track_length;    /* мінімальна довжина треку для тріангуляції (типово 3) */
    
    /* Шумові характеристики давачів */
    double gyro_noise_density;    /* спектральна густина шуму гіроскопа, рад/(с·√Гц) */
    double accel_noise_density;   /* спектральна густина шуму акселерометра, м/(с²·√Гц) */
    double gyro_bias_random_walk; /* випадкове блукання зсуву гіроскопа, рад/(с²·√Гц) */
    double accel_bias_random_walk;/* випадкове блукання зсуву акселерометра, м/(с³·√Гц) */
    double pixel_noise_std;       /* СКП похибки детектора точок, нормовані пікселі */
    
    /* Чисельні пороги та перевірки */
    double min_triangulation_deg; /* мінімальний паралакс для тріангуляції, градуси (типово 1.5–2.0) */
    double chi2_rejection_prob;   /* рівень довіри для тесту χ² (типово 0.95 або 0.99) */
    bool enable_fej;              /* увімкнення Першої Оцінки Якобіанів (First-Estimate Jacobians) */
} MsckfConfig;
```
```cpp
#include <cstdint>
#include <array>

namespace msckf {

struct Vector3d {
    double x{0.0}, y{0.0}, z{0.0};
};

struct Quaterniond {
    double w{1.0}, x{0.0}, y{0.0}, z{0.0};
};

struct MsckfConfig {
    // Геометричне калібрування екстринсиків (Body -> Camera)
    Vector3d body_T_cam{0.0, 0.0, 0.0};
    Quaterniond body_R_cam{1.0, 0.0, 0.0, 0.0};
    
    // Параметри ковзного вікна
    uint32_t max_window_size{20};
    uint32_t min_track_length{3};
    
    // Шумові характеристики давачів
    double gyro_noise_density{1.5e-4};      // рад/(с·√Гц)
    double accel_noise_density{2.0e-3};     // м/(с²·√Гц)
    double gyro_bias_random_walk{1.0e-5};   // рад/(с²·√Гц)
    double accel_bias_random_walk{1.0e-4};  // м/(с³·√Гц)
    double pixel_noise_std{1.0 / 500.0};    // нормовані пікселі
    
    // Чисельні пороги
    double min_triangulation_deg{2.0};      // градуси
    double chi2_rejection_prob{0.95};
    bool enable_fej{true};                  // конзистентність FEJ
};

} // namespace msckf
```
:::

## Вхідні структури даних: IMU та оптичний трекінг

Оцінювач працює з двома незалежними чергами даних, синхронізованими за єдиною часовою шкалою.

| Структура | Призначення | Частота надходження | Критичні інваріанти |
| :--- | :--- | :--- | :--- |
| `MsckfImuMeasurement` | Прискорення та кутова швидкість | 200–1000 Гц | Монотонно зростаючі мітки часу `timestamp`, відсутність NaN |
| `MsckfFeatureFrame` | Масив відстежених точок кадру | 20–60 Гц | Координати точок усунуті від дисторсії та нормалізовані `(u = (px - cx)/fx)` |

Вхідні піксельні координати точок мають подаватися вже виправленими від радіальної та тангенціальної дисторсії камери: `u = (x_px - c_x) / f_x` та `v = (y_px - c_y) / f_y`. Це переносить усю роботу з геометричними калібруваннями об'єктива за межі внутрішнього циклу фільтра.

:::tabs
```c
typedef struct {
    double timestamp;             /* секунди */
    MsckfVec3 linear_accel;       /* покази акселерометра, м/с² */
    MsckfVec3 angular_vel;        /* покази гіроскопа, рад/с */
} MsckfImuMeasurement;

typedef struct {
    uint32_t feature_id;          /* унікальний глобальний ідентифікатор треку */
    double u, v;                  /* нормовані координати на площині камери */
} MsckfFeaturePoint;

typedef struct {
    double timestamp;             /* час експозиції кадру, с */
    uint32_t num_features;        /* кількість точок у поточному кадрі */
    const MsckfFeaturePoint* features;
} MsckfFeatureFrame;
```
```cpp
namespace msckf {

struct ImuMeasurement {
    double timestamp{0.0};
    Vector3d linear_accel;
    Vector3d angular_vel;
};

struct FeaturePoint {
    uint32_t id{0};
    double u{0.0};
    double v{0.0};
};

struct FeatureFrame {
    double timestamp{0.0};
    std::vector<FeaturePoint> features;
};

} // namespace msckf
```
:::

## Вихідна навігаційна оцінка та діагностика

Структура `MsckfEstimate` містить повну кінематику апарата, актуалізовану на момент останнього вимірювання IMU, разом із поточною дисперсією оцінки.

Діагностична структура `MsckfDiagnostics` дає системі моніторингу змогу контролювати працездатність одометрії: кількість активних треків, відсоток відсіяних викидів та факт завершення початкової гравітаційної ініціалізації. Якщо кількість активних точок падає нижче безпечного порогу (наприклад, менше 10 точок), автопілот може вчасно перейти в аварійний режим утримання висоти за барометром.

:::tabs
```c
typedef struct {
    double timestamp;             /* поточний час оцінки, с */
    MsckfVec3 position;           /* положення корпусу у світовій системі, м */
    MsckfVec3 velocity;           /* лінійна швидкість корпусу, м/с */
    MsckfQuat orientation;        /* орієнтація корпусу (світ -> корпус) */
    MsckfVec3 gyro_bias;          /* поточна оцінка зсуву гіроскопа, рад/с */
    MsckfVec3 accel_bias;         /* поточна оцінка зсуву акселерометра, м/с² */
    
    /* Діагональ матриці коваріацій (СКП похибок) */
    MsckfVec3 pos_std;            /* невизначеність положення, м */
    MsckfVec3 vel_std;            /* невизначеність швидкості, м/с */
    MsckfVec3 att_std;            /* невизначеність кутів орієнтації, рад */
} MsckfEstimate;

typedef struct {
    uint32_t current_window_size; /* кількість активних поз у вікні */
    uint32_t active_tracks_count; /* кількість точок, що супроводжуються */
    uint32_t updated_features;    /* кількість орієнтирів, утилізованих у корекції */
    uint32_t rejected_outliers;   /* кількість викидів, відсіяних тестом χ² */
    bool is_initialized;          /* чи завершено початкове вирівнювання гравітації */
} MsckfDiagnostics;
```
```cpp
namespace msckf {

struct EstimatorOutput {
    double timestamp{0.0};
    Vector3d position;
    Vector3d velocity;
    Quaterniond orientation;
    Vector3d gyro_bias;
    Vector3d accel_bias;
    
    Vector3d pos_std;
    Vector3d vel_std;
    Vector3d att_std;
};

struct Diagnostics {
    uint32_t current_window_size{0};
    uint32_t active_tracks_count{0};
    uint32_t updated_features{0};
    uint32_t rejected_outliers{0};
    bool is_initialized{false};
};

} // namespace msckf
```
:::

## Скінченний автомат станів та коди помилок

Модуль MSCKF функціонує як детермінований скінченний автомат із чотирма основними фазами життєвого циклу:

1. **Фаза початкового спокою (Статичне вирівнювання):**
   Після виклику `msckf_create()` оцінювач очікує близько 100–200 вимірювань IMU від нерухомої платформи. На основі осередненого вектора уявного прискорення алгоритм визначає вектор гравітації, початковий крен і тангаж (roll/pitch), а також нульовий рівень гіроскопів. У цей період `msckf_get_estimate()` повертає код `MSCKF_ERROR_NOT_INITIALIZED`.

2. **Фаза динамічного супроводу:**
   Після завершення ініціалізації система переходить у штатний режим: швидкі пакети IMU виконують пророкування стану, а прихід оптичного кадру ініціює стохастичне клонування, тріангуляцію, нуль-просторову проєкцію та маргіналізацію.

3. **Фаза деградації візуального каналу (Dead Reckoning):**
   Якщо камера засліплена або надходить кадр без характерних точок, фільтр тимчасово веде оцінку винятково за інерційними давачами. Кроки корекції пропускаються, а діагональні елементи коваріаційної матриці зростають відповідно до накопиченої невизначеності.

4. **Фаза аварійного скидання:**
   Якщо коваріаційна матриця втрачає додатну визначеність через чисельні збої або виникає часова регресія вхідних пакетів (помилка синхронізації годинників), алгоритм повертає помилку `MSCKF_ERROR_NUMERICAL_DIVERGENCE` або `MSCKF_ERROR_TIME_REGRESSION`. Автопілот зобов'язаний виконати виклик `msckf_reset()`.

Дотримання інваріантів реального часу гарантується відсутністю динамічного виділення пам'яті (відсутність викликів `malloc` / `new`) після завершення фази створення екземпляра.

## Діагностика чисельної стійкості та правила налаштування

Для забезпечення надійної експлуатації оцінювача в польотних автопілотах розробник повинен контролювати числові інваріанти фільтра:

1. **Число обумовленості матриці інновації (Condition Number):**
   Під час розрахунку оберненої матриці `(H P Hᵀ + R)⁻¹` співвідношення між максимальним і мінімальним власними значеннями не повинно перевищувати `10⁸`. Якщо число обумовленості стрімко зростає, це сигналізує про вироджені спостереження або занижений шум `pixel_noise_std`.

2. **Відсіювання викидів за відстанню Махаланобіса:**
   Кожна спроєктована нев'язка перевіряється на відповідність критерію `γ = r_oᵀ S⁻¹ r_o ≤ χ²(p)`. Для типового рівня довіри `p = 0.95` та степеня вільності `k = 2M - 3` порогове значення береться зі стандартних статистичних таблиць. Це усуває хибні треки оптичного потоку від динамічних об'єктів.

3. **Буферизація та синхронізація потоків:**
   Оскільки кадри надходять із затримкою експозиції та обробки оптичного потоку (10–30 мс), модуль веде кільцевий буфер вимірювань IMU. При отриманні кадру оцінювач відкатує стан до точного часу експозиції, виконує клонування та повторно інтегрує накопичений буфер IMU вперед до поточного фізичного часу.

:::tabs
```c
/* Коди помилок функцій бібліотеки */
typedef enum {
    MSCKF_SUCCESS = 0,
    MSCKF_ERROR_INVALID_ARGUMENT = -1,
    MSCKF_ERROR_NOT_INITIALIZED = -2,
    MSCKF_ERROR_TIME_REGRESSION = -3,
    MSCKF_ERROR_NUMERICAL_DIVERGENCE = -4
} MsckfStatus;

/* Непрозора структура рушія */
typedef struct MsckfContext MsckfContext;

/* 1. Створення та ініціалізація екземпляра */
MsckfContext* msckf_create(const MsckfConfig* config);
void msckf_destroy(MsckfContext* ctx);
MsckfStatus msckf_reset(MsckfContext* ctx);

/* 2. Подання вимірів */
MsckfStatus msckf_feed_imu(MsckfContext* ctx, const MsckfImuMeasurement* imu);
MsckfStatus msckf_feed_frame(MsckfContext* ctx, const MsckfFeatureFrame* frame);

/* 3. Зчитування результатів */
MsckfStatus msckf_get_estimate(const MsckfContext* ctx, MsckfEstimate* out_est);
MsckfStatus msckf_get_diagnostics(const MsckfContext* ctx, MsckfDiagnostics* out_diag);
```
```cpp
#include <memory>
#include <expected>

namespace msckf {

enum class Status {
    Success = 0,
    InvalidArgument,
    NotInitialized,
    TimeRegression,
    NumericalDivergence
};

class MsckfEngine {
public:
    explicit MsckfEngine(const MsckfConfig& config);
    ~MsckfEngine();

    MsckfEngine(const MsckfEngine&) = delete;
    MsckfEngine& operator=(const MsckfEngine&) = delete;
    MsckfEngine(MsckfEngine&&) noexcept;
    MsckfEngine& operator=(MsckfEngine&&) noexcept;

    // Скидання стану фільтра
    void reset();

    // Передача первинних даних
    std::expected<void, Status> feedImu(const ImuMeasurement& imu);
    std::expected<void, Status> feedFrame(const FeatureFrame& frame);

    // Отримання оцінки навігації
    [[nodiscard]] std::expected<EstimatorOutput, Status> getEstimate() const noexcept;
    [[nodiscard]] Diagnostics getDiagnostics() const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace msckf
```
:::

## Приклад повного циклу використання

Нижче наведено типовий сценарій роботи головного потоку автопілота: ініціалізація модуля, періодичне згодовування пакетів та зчитування свіжої позиції.

:::tabs
```c
int run_msckf_example(void) {
    MsckfConfig cfg;
    /* Заповнення типових параметрів */
    cfg.body_T_cam = (MsckfVec3){0.1, 0.0, -0.05};
    cfg.body_R_cam = (MsckfQuat){1.0, 0.0, 0.0, 0.0};
    cfg.max_window_size = 15;
    cfg.min_track_length = 3;
    cfg.gyro_noise_density = 1.5e-4;
    cfg.accel_noise_density = 2.0e-3;
    cfg.gyro_bias_random_walk = 1.0e-5;
    cfg.accel_bias_random_walk = 1.0e-4;
    cfg.pixel_noise_std = 0.002;
    cfg.min_triangulation_deg = 2.0;
    cfg.chi2_rejection_prob = 0.95;
    cfg.enable_fej = true;

    MsckfContext* ctx = msckf_create(&cfg);
    if (!ctx) return -1;

    /* Симуляція надходження IMU */
    MsckfImuMeasurement imu;
    imu.timestamp = 100.002;
    imu.linear_accel = (MsckfVec3){0.0, 0.0, 9.81};
    imu.angular_vel = (MsckfVec3){0.0, 0.0, 0.0};
    msckf_feed_imu(ctx, &imu);

    /* Зчитування навігаційної оцінки */
    MsckfEstimate est;
    if (msckf_get_estimate(ctx, &est) == MSCKF_SUCCESS) {
        printf("Положення: X=%.3f, Y=%.3f, Z=%.3f\n", est.position.x, est.position.y, est.position.z);
    }

    msckf_destroy(ctx);
    return 0;
}
```
```cpp
int runMsckfExample() {
    using namespace msckf;

    MsckfConfig cfg;
    cfg.body_T_cam = {0.1, 0.0, -0.05};
    cfg.max_window_size = 15;

    MsckfEngine engine(cfg);

    ImuMeasurement imu;
    imu.timestamp = 100.002;
    imu.linear_accel = {0.0, 0.0, 9.81};
    imu.angular_vel = {0.0, 0.0, 0.0};

    auto imu_res = engine.feedImu(imu);
    if (!imu_res) {
        return -1;
    }

    auto est_res = engine.getEstimate();
    if (est_res) {
        const auto& est = *est_res;
        // Використання оцінки у контурі керування
        (void)est.position;
    }

    return 0;
}
```
:::
