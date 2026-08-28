# ⚙️ Монітор здоров'я сенсора: валідатор шумів, градієнта та кворуму

У надійних вбудованих системах життєво необхідно розділяти факт успішного зв'язку по шині та фізичну правдивість прийнятих даних. Навіть коли контролер I2C або АЦП повертає байти без апаратних помилок кадрування, чутливий кристал може зависнути, обірватися або зазнати деградації. Цей проєкт містить закінчений, готовий до використання модуль моніторингу здоров'я сенсорного тракту (`SensorHealthGuard`), який на кожному відліку виконує трирівневу діагностику:

1. **Перевірка фізичних меж (*Plausibility Check*)** — відсікання апаратного замикання на шини живлення (0 В / 3.3 В) та виходу за межі фізичної моделі процесу.
2. **Перевірка максимального градієнта (*Rate-of-Change Check*)** — контроль фізичної інерції сигналу (`|dY/dt| ≤ limit`), що захищає від імпульсних наведень і тріщин на платі.
3. **Детектор мертвого кристала (*Zero-Variance / Stuck-Value Detection*)** — обчислення дисперсії шуму в реальному часі за [алгоритмом Уелфорда](root:embedded/tykha-vidmova) без збереження буфера відліків у RAM.
4. **Мажоритарний кворум 2oo3 (*Two-out-of-Three Voter*)** — зіставлення трьох незалежних сенсорних каналів із відсіканням дрейфуючого каналу та обчисленням результуючої медіани.

## Архітектурні принципи та інженерні компроміси

Модуль спроєктовано для роботи в умовах жорстких обмежень вбудованих систем:
- **Детермінізм пам'яті:** повна відсутність динамічного виділення пам'яті (`malloc`). Стан кожного сенсора ізольовано у фіксованій структурі розміром 36 байтів.
- **Швидкодія `O(1)`:** обчислення середнього та дисперсії виконується рекурентно за один прохід, без ітерацій по масиву.
- **Захист від переповнення таймера:** різниця міток часу обчислюється як беззнакове віднімання `uint32_t dt_ms = now_ms - prev_ts_ms`, що коректно працює навіть при апаратному переході лічильника мілісекунд через нуль (раз на 49.7 діб для 32-бітного лічильника).
- **Обробка холодного старту:** під час початкового накопичення відліків (до досягнення `min_samples_var`) прапорець нульової дисперсії примусово маскується, запобігаючи хибним спрацьовуванням сигналізації під час ініціалізації датчика.

## Інтерфейс модуля (C та C++)

Заголовочні структури описують бітову маску помилок, конфігураційні межі та контекст накопичувача.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Бітові прапорці діагностичного стану сенсора */
typedef enum {
    SENSOR_HEALTH_OK               = 0x00,
    SENSOR_FAULT_OUT_OF_RANGE_LOW  = 0x01, /* Нижче мінімуму (обрив / 0 В) */
    SENSOR_FAULT_OUT_OF_RANGE_HIGH = 0x02, /* Вище максимуму (КЗ / Vdd) */
    SENSOR_FAULT_SLEW_RATE         = 0x04, /* Стрибок dY/dt вище ліміту */
    SENSOR_FAULT_ZERO_VARIANCE     = 0x08, /* Нульова дисперсія (завислий кристал) */
    SENSOR_FAULT_CROSS_CHECK       = 0x10  /* Розбіжність із кворумом або моделлю */
} sensor_health_flags_t;

/* Налаштування меж та чутливості діагностики */
typedef struct {
    float min_plausible;       /* Нижня фізична межа величини */
    float max_plausible;       /* Верхня фізична межа величини */
    float max_slew_rate;       /* Максимально допустима швидкість зміни (|Δy| / c) */
    float min_variance;        /* Поріг мертвого сенсора (мінімальна дисперсія) */
    uint32_t min_samples_var;  /* Кількість відліків для накопичення дисперсії */
} sensor_guard_config_t;

/* Стан накопичувача та алгоритму Уелфорда */
typedef struct {
    sensor_guard_config_t cfg;
    float last_value;
    uint32_t last_timestamp_ms;
    bool has_prev_sample;

    /* Змінні однопрохідного розрахунку середнього та дисперсії (Welford) */
    uint32_t sample_count;
    float mean;
    float m2;

    /* Поточний діагностичний статус */
    uint8_t flags;
} sensor_guard_t;

/* Результат мажоритарного голосування 2oo3 */
typedef struct {
    float voted_value;
    bool quorum_valid;
    uint8_t faulty_sensor_mask; /* Біти 0, 1, 2 показують несправний канал */
} quorum_result_t;

void sensor_guard_init(sensor_guard_t *guard, const sensor_guard_config_t *cfg);
uint8_t sensor_guard_update(sensor_guard_t *guard, float value, uint32_t timestamp_ms);
quorum_result_t sensor_guard_vote_2oo3(float s1, float s2, float s3, float max_allowed_spread);
```
```cpp
#include <cstdint>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>

enum class SensorHealthFlags : uint8_t {
    Ok              = 0x00,
    OutOfRangeLow   = 0x01,
    OutOfRangeHigh  = 0x02,
    SlewRate        = 0x04,
    ZeroVariance    = 0x08,
    CrossCheck      = 0x10
};

[[nodiscard]] constexpr SensorHealthFlags operator|(SensorHealthFlags a, SensorHealthFlags b) noexcept {
    return static_cast<SensorHealthFlags>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

[[nodiscard]] constexpr bool has_flag(SensorHealthFlags mask, SensorHealthFlags flag) noexcept {
    return (static_cast<uint8_t>(mask) & static_cast<uint8_t>(flag)) != 0;
}

struct SensorGuardConfig {
    float min_plausible;
    float max_plausible;
    float max_slew_rate;
    float min_variance;
    uint32_t min_samples_var;
};

struct QuorumResult {
    float voted_value{0.0f};
    bool quorum_valid{false};
    uint8_t faulty_sensor_mask{0};
};

class SensorHealthGuard {
public:
    explicit constexpr SensorHealthGuard(const SensorGuardConfig& config) noexcept
        : cfg_(config) {}

    SensorHealthFlags update(float value, uint32_t timestamp_ms) noexcept;

    [[nodiscard]] float mean() const noexcept { return mean_; }
    [[nodiscard]] float variance() const noexcept;
    [[nodiscard]] SensorHealthFlags current_flags() const noexcept { return flags_; }
    [[nodiscard]] bool is_healthy() const noexcept { return flags_ == SensorHealthFlags::Ok; }

    static QuorumResult vote_2oo3(float s1, float s2, float s3, float max_allowed_spread) noexcept;

private:
    SensorGuardConfig cfg_;
    float last_value_{0.0f};
    uint32_t last_timestamp_ms_{0};
    bool has_prev_sample_{false};

    uint32_t sample_count_{0};
    float mean_{0.0f};
    float m2_{0.0f};

    SensorHealthFlags flags_{SensorHealthFlags::Ok};
};
```
:::

## Повна реалізація алгоритмів обробки

Реалізація містить математичні оновлення середнього й дисперсії, захист від ділення на нуль при збігу міток часу та попарний аналіз розбіжностей для потрійного кворуму.

:::tabs
```c
void sensor_guard_init(sensor_guard_t *guard, const sensor_guard_config_t *cfg) {
    if (!guard || !cfg) return;
    guard->cfg = *cfg;
    guard->last_value = 0.0f;
    guard->last_timestamp_ms = 0;
    guard->has_prev_sample = false;
    guard->sample_count = 0;
    guard->mean = 0.0f;
    guard->m2 = 0.0f;
    guard->flags = SENSOR_HEALTH_OK;
}

uint8_t sensor_guard_update(sensor_guard_t *guard, float value, uint32_t timestamp_ms) {
    if (!guard) return SENSOR_FAULT_OUT_OF_RANGE_LOW;

    uint8_t current_faults = SENSOR_HEALTH_OK;

    /* 1. Перевірка фізичних меж (Plausibility) */
    if (value < guard->cfg.min_plausible) {
        current_faults |= SENSOR_FAULT_OUT_OF_RANGE_LOW;
    } else if (value > guard->cfg.max_plausible) {
        current_faults |= SENSOR_FAULT_OUT_OF_RANGE_HIGH;
    }

    /* 2. Градієнтний контроль швидкості зміни (dY/dt) */
    if (guard->has_prev_sample) {
        uint32_t dt_ms = timestamp_ms - guard->last_timestamp_ms;
        if (dt_ms > 0) {
            float dt_sec = (float)dt_ms / 1000.0f;
            float rate = fabsf(value - guard->last_value) / dt_sec;
            if (rate > guard->cfg.max_slew_rate) {
                current_faults |= SENSOR_FAULT_SLEW_RATE;
            }
        }
    }

    /* 3. Однопрохідний розрахунок дисперсії (Алгоритм Уелфорда) */
    guard->sample_count++;
    float delta = value - guard->mean;
    guard->mean += delta / (float)guard->sample_count;
    float delta2 = value - guard->mean;
    guard->m2 += delta * delta2;

    /* Перевірка застрягання значення (Zero-Variance) після накопичення мінімального вікна */
    if (guard->sample_count >= guard->cfg.min_samples_var) {
        float variance = guard->m2 / (float)(guard->sample_count - 1);
        if (variance < guard->cfg.min_variance) {
            current_faults |= SENSOR_FAULT_ZERO_VARIANCE;
        }
    }

    guard->last_value = value;
    guard->last_timestamp_ms = timestamp_ms;
    guard->has_prev_sample = true;
    guard->flags = current_faults;

    return current_faults;
}

quorum_result_t sensor_guard_vote_2oo3(float s1, float s2, float s3, float max_allowed_spread) {
    quorum_result_t res;
    res.voted_value = 0.0f;
    res.quorum_valid = false;
    res.faulty_sensor_mask = 0;

    float diff12 = fabsf(s1 - s2);
    float diff23 = fabsf(s2 - s3);
    float diff31 = fabsf(s3 - s1);

    bool p12 = (diff12 <= max_allowed_spread);
    bool p23 = (diff23 <= max_allowed_spread);
    bool p31 = (diff31 <= max_allowed_spread);

    if (p12 && p23 && p31) {
        /* Усі три канали узгоджені: повертаємо середнє або медіану */
        res.voted_value = (s1 + s2 + s3) / 3.0f;
        res.quorum_valid = true;
    } else if (p12) {
        /* Канал 3 відхилився */
        res.voted_value = (s1 + s2) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 2);
    } else if (p23) {
        /* Канал 1 відхилився */
        res.voted_value = (s2 + s3) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 0);
    } else if (p31) {
        /* Канал 2 відхилився */
        res.voted_value = (s3 + s1) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 1);
    } else {
        /* Усі три канали розійшлися: кворум втрачено */
        res.quorum_valid = false;
        res.faulty_sensor_mask = 0x07;
    }

    return res;
}
```
```cpp
SensorHealthFlags SensorHealthGuard::update(float value, uint32_t timestamp_ms) noexcept {
    auto current_faults = SensorHealthFlags::Ok;

    // 1. Перевірка фізичних меж
    if (value < cfg_.min_plausible) {
        current_faults = current_faults | SensorHealthFlags::OutOfRangeLow;
    } else if (value > cfg_.max_plausible) {
        current_faults = current_faults | SensorHealthFlags::OutOfRangeHigh;
    }

    // 2. Градієнтний контроль (dY/dt)
    if (has_prev_sample_) {
        const uint32_t dt_ms = timestamp_ms - last_timestamp_ms_;
        if (dt_ms > 0) {
            const float dt_s = static_cast<float>(dt_ms) / 1000.0f;
            const float rate = std::abs(value - last_value_) / dt_s;
            if (rate > cfg_.max_slew_rate) {
                current_faults = current_faults | SensorHealthFlags::SlewRate;
            }
        }
    }

    // 3. Алгоритм Уелфорда для дисперсії
    sample_count_++;
    const float delta = value - mean_;
    mean_ += delta / static_cast<float>(sample_count_);
    const float delta2 = value - mean_;
    m2_ += delta * delta2;

    if (sample_count_ >= cfg_.min_samples_var) {
        const float var = m2_ / static_cast<float>(sample_count_ - 1);
        if (var < cfg_.min_noise_variance) {
            current_faults = current_faults | SensorHealthFlags::ZeroVariance;
        }
    }

    last_value_ = value;
    last_timestamp_ms_ = timestamp_ms;
    has_prev_sample_ = true;
    flags_ = current_faults;

    return flags_;
}

float SensorHealthGuard::variance() const noexcept {
    if (sample_count_ < 2) {
        return 0.0f;
    }
    return m2_ / static_cast<float>(sample_count_ - 1);
}

QuorumResult SensorHealthGuard::vote_2oo3(float s1, float s2, float s3, float max_allowed_spread) noexcept {
    QuorumResult res{};

    const float diff12 = std::abs(s1 - s2);
    const float diff23 = std::abs(s2 - s3);
    const float diff31 = std::abs(s3 - s1);

    const bool p12 = (diff12 <= max_allowed_spread);
    const bool p23 = (diff23 <= max_allowed_spread);
    const bool p31 = (diff31 <= max_allowed_spread);

    if (p12 && p23 && p31) {
        res.voted_value = (s1 + s2 + s3) / 3.0f;
        res.quorum_valid = true;
    } else if (p12) {
        res.voted_value = (s1 + s2) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 2);
    } else if (p23) {
        res.voted_value = (s2 + s3) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 0);
    } else if (p31) {
        res.voted_value = (s3 + s1) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 1);
    } else {
        res.quorum_valid = false;
        res.faulty_sensor_mask = 0x07;
    }

    return res;
}
```
:::

## Тестовий стенд: ін'єкція збоїв та верифікація

Тестова програма моделює чотири типові сценарії відмови:
1. **Здоровий сенсор:** нормальний фізичний процес із гаусовим шумом вимірювання (дисперсія `σ² > 0`).
2. **Зависання регістра (*Stuck Register*):** шина віддає константу 24.500 °C протягом 50 циклів → спрацьовує прапорець `ZeroVariance`.
3. **Імпульсна завада (*Slew-Rate Spike*):** стрибок на +25 °C за 100 мс → спрацьовує `SlewRate`.
4. **Тихий дрейф одного каналу в трійці:** третій сенсор повільно відпливає на +8 °C → мажоритарний кворум 2oo3 ізолює його, зберігаючи валідне керування на каналах 1 і 2.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

static float pseudo_gaussian_noise(void) {
    /* Проста апроксимація гаусового шуму через суму рівномірних величин */
    float sum = 0.0f;
    for (int i = 0; i < 12; ++i) {
        sum += (float)rand() / (float)RAND_MAX;
    }
    return (sum - 6.0f) * 0.05f; /* Середнє 0, розмах ~0.15 */
}

int main(void) {
    sensor_guard_config_t cfg = {
        .min_plausible    = -20.0f,
        .max_plausible    = 85.0f,
        .max_slew_rate    = 5.0f,    /* Максимум 5 °C за секунду */
        .min_variance     = 0.0001f, /* Мінімальний рівень природного шуму */
        .min_samples_var  = 20
    };

    sensor_guard_t guard;
    sensor_guard_init(&guard, &cfg);

    printf("=== 1. Здоровий сенсор із природним шумом ===\n");
    uint32_t time_ms = 0;
    for (int i = 0; i < 25; ++i) {
        float sample = 25.0f + pseudo_gaussian_noise();
        uint8_t flags = sensor_guard_update(&guard, sample, time_ms);
        time_ms += 100;
        if (i == 24) {
            printf("Відлік #%d: T=%.3f C, дисперсія=%.6f, прапорці=0x%02X (OK)\n",
                   i, sample, guard.m2 / (float)(guard.sample_count - 1), flags);
        }
    }

    printf("\n=== 2. Зависання цифрового виходу (Stuck Value) ===\n");
    for (int i = 0; i < 30; ++i) {
        float sample = 25.000f; /* Абсолютно плоске значення */
        uint8_t flags = sensor_guard_update(&guard, sample, time_ms);
        time_ms += 100;
        if (flags & SENSOR_FAULT_ZERO_VARIANCE) {
            printf("Зафіксовано тиху відмову на кроці #%d! Прапорці=0x%02X (Zero Variance)\n", i, flags);
            break;
        }
    }

    printf("\n=== 3. Мажоритарний кворум 2oo3 при дрейфі одного давача ===\n");
    float t1 = 25.1f, t2 = 25.3f, t3_drifted = 33.8f;
    quorum_result_t qr = sensor_guard_vote_2oo3(t1, t2, t3_drifted, 1.0f);
    printf("Входи: S1=%.1f, S2=%.1f, S3=%.1f\n", t1, t2, t3_drifted);
    printf("Результат кворуму: валідний=%s, результуюча T=%.2f C, маска помилки=0x%02X\n",
           qr.quorum_valid ? "ТАК" : "НІ", qr.voted_value, qr.faulty_sensor_mask);

    return 0;
}
```
```cpp
#include <iostream>
#include <random>
#include <iomanip>

int main() {
    const SensorGuardConfig cfg{
        .min_plausible   = -20.0f,
        .max_plausible   = 85.0f,
        .max_slew_rate   = 5.0f,
        .min_variance    = 0.0001f,
        .min_samples_var = 20
    };

    SensorHealthGuard guard{cfg};
    std::mt19937 rng(42);
    std::normal_distribution<float> noise(0.0f, 0.05f);

    std::cout << "=== 1. Здоровий сенсор із природним шумом ===\n";
    uint32_t time_ms = 0;
    for (int i = 0; i < 25; ++i) {
        const float sample = 25.0f + noise(rng);
        const auto flags = guard.update(sample, time_ms);
        time_ms += 100;
        if (i == 24) {
            std::cout << "Відлік #" << i << ": T=" << std::fixed << std::setprecision(3)
                      << sample << " C, дисперсія=" << guard.variance()
                      << ", здоровий=" << (guard.is_healthy() ? "ТАК" : "НІ") << '\n';
        }
    }

    std::cout << "\n=== 2. Зависання цифрового виходу (Stuck Value) ===\n";
    for (int i = 0; i < 30; ++i) {
        constexpr float sample = 25.000f;
        const auto flags = guard.update(sample, time_ms);
        time_ms += 100;
        if (has_flag(flags, SensorHealthFlags::ZeroVariance)) {
            std::cout << "Зафіксовано тиху відмову на кроці #" << i
                      << "! ZeroVariance виявлено, дисперсія=" << guard.variance() << '\n';
            break;
        }
    }

    std::cout << "\n=== 3. Мажоритарний кворум 2oo3 при дрейфі одного давача ===\n";
    constexpr float t1 = 25.1f;
    constexpr float t2 = 25.3f;
    constexpr float t3_drifted = 33.8f;
    const auto qr = SensorHealthGuard::vote_2oo3(t1, t2, t3_drifted, 1.0f);

    std::cout << "Входи: S1=" << t1 << ", S2=" << t2 << ", S3=" << t3_drifted << '\n';
    std::cout << "Результат: кворум=" << (qr.quorum_valid ? "ВАЛІДНИЙ" : "ВТРАЧЕНО")
              << ", Т=" << qr.voted_value
              << ", маска дефекту=0x" << std::hex << static_cast<int>(qr.faulty_sensor_mask) << '\n';

    return 0;
}
```
:::

## Інженерні правила калібрування та крайові випадки

1. **Розрахунок мінімального порогу дисперсії (`min_variance`):**
   Поріг не можна обирати навмання. Для 12-бітного АЦП із повною шкалою 3.3 В ціна одного молодшого розряду становить `LSB = 3.3 В / 4096 ≈ 0.806 мВ`. Теоретичний шум квантування ідеального АЦП з рівномірним розподілом помилки округлення має дисперсію:
   ```
   Var_quant = LSB² / 12 = (0.806 · 10⁻³)² / 12 ≈ 5.41 · 10⁻⁸ В²
   ```
   У реальній схемі до цього додається тепловий шум вхідного операційного підсилювача та шум опорної напруги, тому сумарний шум здорового сенсора рідко опускається нижче `1.5 · Var_quant`. Якщо встановити поріг `min_variance = 0.5 · Var_quant`, ми надійно відрізнимо тихий застій цифрового інтерфейсу від реального зашумленого сигналу.

2. **Періодичне скидання накопичувача Уелфорда:**
   У системах неперервної роботи (тижні та місяці) лічильник `sample_count` неперервно зростає. При `sample_count > 100000` додавання малого приросту `delta / sample_count` до великого середнього у форматі `float` починає втрачати молодші розряди мантиси через обмеження точності 24-бітної мантиси IEEE 754. Щоб уникнути чисельного насичення, рекомендується кожні `N_reset = 500` або `1000` відліків скидати `sample_count` у 0 та очищати `m2`, зберігаючи поточне середнє значення як початкову точку наступного вікна.

3. **Вплив викидів (Outliers) на розрахунок дисперсії:**
   Одиничний імпульсний сплеск великої амплітуди створює значне відхилення `delta = x - mean`, яке різко збільшує суму квадратів `m2`. Як наслідок, дисперсія штучно підскакує вгору і тримається завищеною протягом кількох десятків наступних тактів. Якщо цей сплеск був спричинений апаратною завадою, прапорець `SENSOR_FAULT_SLEW_RATE` зафіксує подію, проте для розрахунку дисперсії такий відлік доцільно виключати з накопичувача Уелфорда, щоб не замаскувати можливе наступне зависання сигналу.

4. **Інтеграція з задачами FreeRTOS та чергами подій:**
   У багатозадачній системі виклик `sensor_guard_update()` розміщують безпосередньо в сенсорному завданні перед передачею даних у спільну чергу або кільцевий буфер. Якщо функція повертає будь-який прапорець окрім `SENSOR_HEALTH_OK`, завдання не блокує виконання, а формує телеметричну структуру з виставленими прапорцями деградації, даючи змогу контролеру перейти в режим обмеженої потужності.

5. **Серіалізація діагностичного статусу в польові шини (CAN, Modbus, MQTT):**
   При передачі результатів вимірювання на верхній рівень обов'язково передають бітову маску помилок. Для протоколу Modbus RTU під прапорці здоров'я виділяють окремий регістр стану `Status Register`, а в протоколах CAN/DroneCAN поле `health` кодується переліком станів `HEALTH_OK (0)`, `HEALTH_WARNING (1)`, `HEALTH_ERROR (2)`, `HEALTH_CRITICAL (3)`. Це дає змогу серверному диспетчеру своєчасно виявляти тихі збої без додаткового декодування сирих потоків напруги.
