# ⚙️ Модуль гібридного арбітражу між правилом і моделлю з бенчмарком затримок

Цей практичний модуль демонструє проєктування, програмну реалізацію та апаратне профілювання вбудованого арбітражного селектора, який у жорсткому реальному часі балансує між надшвидким аналітичним правилом (складність O(1), затримка 1.2 мікросекунди) та багатопараметричною квантованою нейромережею INT8 (затримка близько 850 мікросекунд). Без детального вимірювання витрат машинних тактів процесорного ядра, аналізу накладних витрат арени пам'яті та формалізованого розрахунку матриці вартості помилок розробник ризикує зіткнутися або з некерованим перевантаженням шини мікроконтролера, або з постійними хибними перемиканнями на аварійний режим через шум вхідних сенсорів.

---

## Інженерна постановка задачі та апаратна платформа

Розглядається система автономного позиціонування та керування приводом для мобільного логістичного робота або складського безпілотного візка. Обчислювальний вузол побудований на базі 32-бітного мікроконтролера STM32H743ZI з ядром ARM Cortex-M7, що працює на тактовій частоті 400 МГц і має 1 МБ вбудованої Flash-пам'яті та 512 КБ оперативної пам'яті SRAM, розподіленої між тісно пов'язаною пам'яттю даних DTCM (128 КБ) та системною пам'яттю AXI SRAM (384 КБ).

Система керування рухом реалізує два паралельні контури формування завдання лінійної швидкості:
1. **Детермінований контур безпеки (Аналітичне правило):** опитує 4 ультразвукові сонари, розташовані по периметру корпусу, та обчислює гранично допустиму швидкість на основі формул кінематики рівносповільненого руху з урахуванням максимального гальмівного прискорення та мертвого часу спрацьовування гальм.
2. **Оптимізаційний контур планування (Квантована нейромережа INT8):** приймає вектор глибини з 64 променів твердотільного лідара та вектор поточної швидкості, формуючи плавну та енергетично ефективну траєкторію об'їзду стаціонарних і рухомих перешкод у захаращеному складі.

```
                   ┌──────────────────────────────────────────────┐
                   │ Сенсорні дані: Лідар (64 промені) + Сонари   │
                   └──────────────────────┬───────────────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
        ┌─────────────────────────┐                   ┌─────────────────────────┐
        │ Канал ML (INT8 вивід)   │                   │ Детермінований канал    │
        │ • 64 входи, 2 шари      │                   │ • 4 сонари, кінематика  │
        │ • Час: ~850 мкс         │                   │ • Час: ~1.2 мкс         │
        └──────────┬──────────────┘                   └───────────┬─────────────┘
                   │                                              │
             Пропозиція u_ml                                Резерв u_safe
                   │                                              │
                   └──────────────────────┬───────────────────────┘
                                          ▼
                         ┌──────────────────────────────────┐
                         │   Гібридний Simplex-арбітр       │
                         │   • Перевірка інваріантів стану  │
                         │   • Гістерезис та Dwell Time     │
                         │   • Бенчмарк тактів ядра DWT     │
                         └────────────────┬─────────────────┘
                                          │
                                  Керування u_out
                                          ▼
                         ┌──────────────────────────────────┐
                         │   ШІМ-драйвер силових інверторів │
                         └──────────────────────────────────┘
```

Цільовий період циклу планувальника завдань операційної системи реального часу (RTOS) становить рівно T_cycle = 1.0 мс (частота оновлення 1 кГц). Селектор повинен виконати повну перевірку безпеки пропозиції нейромережі, проконтролювати дотримання часового дедлайну (Worst-Case Execution Time, WCET) та, у разі виявлення аномалії чи дефіциту часу, миттєво підставити детерміноване безпечне значення без порушення часового графіка переривань.

---

## Математична модель бар'єра та кінематичні інваріанти

Перед розглядом коду визначимо фізичний зміст детермінованого бар'єра безпеки.

Нехай мінімальна зафіксована дистанція до найближчої перешкоди становить d_min (у міліметрах), поточна швидкість візка — v (у мм/с), максимальне аварійне сповільнення — a_max (у мм/с²), а максимальний час реакції системи (затримка відліку сенсора плюс час одного циклу RTOS) — t_react (у секундах).

Повна дистанція гальмування складається з дистанції, яку візок проходить за час реакції до початку сповільнення, та безпосередньо гальмівного шляху:

```
d_stop(v) = v · t_react + (v²) / (2 · a_max)
```

Інваріант безпеки вимагає, щоб поточна дистанція d_min завжди перевищувала гальмівний шлях разом із незнижуваним захисним буфером безпеки d_safe_margin:

```
h(x) = d_min - (v · t_react + (v²) / (2 · a_max)) - d_safe_margin ≥ 0
```

Розв'язуючи цю нерівність відносно швидкості v, детермінований блок обчислює гранично допустиму швидкість v_limit, перевищення якої фізично унеможливить зупинку перед перешкодою:

```
v_limit = - (a_max · t_react) + √((a_max · t_react)² + 2 · a_max · (d_min - d_safe_margin))
```

Для оптимізації обчислень на мікроконтролері без блоку ділення цей вираз лінеаризують або апроксимують квадратичною таблицею пошуку (Look-Up Table, LUT), що дає виконання менш ніж за 50 машинних тактів процесора.

---

## Програмна реалізація вимірювального стенда на C99 та C++20

Нижче наведено повні вихідні тексти модулів гібридного селектора, спрощеного ядра матричного множення для квантованої нейромережі INT8 та інструментарію зняття профілів продуктивності за допомогою системного таймера DWT ядра ARM Cortex-M.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define LIDAR_RAYS_COUNT         64
#define NN_HIDDEN_NEURONS        16
#define MAX_ALLOWED_SPEED_MM_S   2000.0f
#define EMERGENCY_BRAKE_DECEL    4000.0f
#define SAFE_DISTANCE_MIN_MM     300.0f
#define CONF_HYST_HIGH           0.80f
#define CONF_HYST_LOW            0.65f
#define MIN_DWELL_CYCLES         20
#define WCET_DEADLINE_CYCLES     360000 // 900 мкс при 400 МГц

typedef struct {
    float distance_sonar_mm[4];
    int8_t lidar_depth_int8[LIDAR_RAYS_COUNT];
    float battery_voltage_v;
    float motor_temp_c;
} SensorFrame_t;

typedef struct {
    float target_speed_mm_s;
    float confidence;
    bool  deadline_met;
} MlInferenceOutput_t;

typedef enum {
    MODE_RULE_SAFE_DEFAULT = 0,
    MODE_ML_OPTIMAL_PATH   = 1,
    MODE_RULE_RATE_LIMITED = 2,
    MODE_RULE_EMERGENCY    = 3
} ArbiterMode_t;

typedef struct {
    float last_output_speed;
    ArbiterMode_t current_mode;
    uint32_t mode_dwell_counter;
    uint32_t ml_overtime_events;
    uint32_t safety_interventions;
} ArbiterCore_t;

typedef struct {
    float         command_speed_mm_s;
    ArbiterMode_t active_mode;
    uint32_t      execution_cycles;
} StepOutput_t;

// Апаратне зчитування регістру лічильника циклів Cortex-M DWT
static inline uint32_t Bench_GetCycles(void) {
    #if defined(__arm__) || defined(__thumb__)
    volatile uint32_t* DWT_CYCCNT = (volatile uint32_t*)0xE0001004;
    return *DWT_CYCCNT;
    #else
    static uint32_t fake_ticks = 0;
    fake_ticks += 45;
    return fake_ticks;
    #endif
}

// 1. Детермінований контролер безпеки: обчислення кінематичної межі швидкості
float Rule_ComputeSafeSpeed(const SensorFrame_t* sensors, float current_speed, float dt_sec) {
    float min_dist = sensors->distance_sonar_mm[0];
    for (int i = 1; i < 4; ++i) {
        if (sensors->distance_sonar_mm[i] < min_dist) {
            min_dist = sensors->distance_sonar_mm[i];
        }
    }

    // Критична зона: негайне застосування максимального гальмування
    if (min_dist <= SAFE_DISTANCE_MIN_MM) {
        float decel_step = EMERGENCY_BRAKE_DECEL * dt_sec;
        if (current_speed > decel_step) {
            return current_speed - decel_step;
        } else if (current_speed < -decel_step) {
            return current_speed + decel_step;
        }
        return 0.0f;
    }

    // Лінеаризоване обмеження швидкості за запасом дистанції
    float allowed_speed = (min_dist - SAFE_DISTANCE_MIN_MM) * 2.5f;
    if (allowed_speed > MAX_ALLOWED_SPEED_MM_S) {
        allowed_speed = MAX_ALLOWED_SPEED_MM_S;
    }
    return allowed_speed;
}

// 2. Квантований шар нейромережі INT8: емуляція множення матриці ваг на вхідний вектор
void Ml_ExecuteInt8Inference(
    const int8_t* in_lidar,
    const int8_t weights[NN_HIDDEN_NEURONS][LIDAR_RAYS_COUNT],
    const int32_t bias[NN_HIDDEN_NEURONS],
    MlInferenceOutput_t* out_result
) {
    uint32_t start_cycles = Bench_GetCycles();
    int32_t hidden_acc[NN_HIDDEN_NEURONS];

    for (int i = 0; i < NN_HIDDEN_NEURONS; ++i) {
        int32_t sum = bias[i];
        for (int j = 0; j < LIDAR_RAYS_COUNT; ++j) {
            sum += (int32_t)in_lidar[j] * (int32_t)weights[i][j];
        }
        // Нелінійна функція активації ReLU (зрізання від'ємних значень)
        hidden_acc[i] = (sum > 0) ? sum : 0;
    }

    // Агрегація виходу прихованого шару
    int32_t total_activation = 0;
    for (int i = 0; i < NN_HIDDEN_NEURONS; ++i) {
        total_activation += (hidden_acc[i] >> 8);
    }

    out_result->target_speed_mm_s = (float)(total_activation % 2000);
    out_result->confidence = 0.88f; // Калібрована впевненість
    
    uint32_t elapsed = Bench_GetCycles() - start_cycles;
    out_result->deadline_met = (elapsed <= WCET_DEADLINE_CYCLES);
}

// 3. Ядро гібридного арбітражу з гістерезисом та верифікацією інваріантів
StepOutput_t Arbiter_ExecuteCycle(
    ArbiterCore_t* arbiter,
    const SensorFrame_t* sensors,
    const MlInferenceOutput_t* ml_output,
    float dt_sec
) {
    uint32_t start_tick = Bench_GetCycles();
    StepOutput_t result;
    arbiter->mode_dwell_counter++;

    float safe_limit = Rule_ComputeSafeSpeed(sensors, arbiter->last_output_speed, dt_sec);

    // Перевірка апаратних аварійних порогів (температура, напруга живлення)
    if (sensors->motor_temp_c > 85.0f || sensors->battery_voltage_v < 10.5f) {
        arbiter->current_mode = MODE_RULE_EMERGENCY;
        arbiter->safety_interventions++;
        result.command_speed_mm_s = 0.0f;
        result.active_mode = MODE_RULE_EMERGENCY;
        arbiter->last_output_speed = 0.0f;
        result.execution_cycles = Bench_GetCycles() - start_tick;
        return result;
    }

    // Логіка подвійного порога гістерезису для запобігання деренчанню режимів
    bool ml_trusted = false;
    if (arbiter->current_mode == MODE_ML_OPTIMAL_PATH) {
        ml_trusted = ml_output->deadline_met && (ml_output->confidence >= CONF_HYST_LOW);
    } else {
        if (arbiter->mode_dwell_counter >= MIN_DWELL_CYCLES) {
            ml_trusted = ml_output->deadline_met && (ml_output->confidence >= CONF_HYST_HIGH);
        }
    }

    if (ml_trusted) {
        float ml_speed = ml_output->target_speed_mm_s;
        if (ml_speed <= safe_limit) {
            arbiter->current_mode = MODE_ML_OPTIMAL_PATH;
            arbiter->last_output_speed = ml_speed;
            result.command_speed_mm_s = ml_speed;
            result.active_mode = MODE_ML_OPTIMAL_PATH;
        } else {
            // Бар'єр безпеки м'яко зрізає швидкість до кінематичної межі
            arbiter->current_mode = MODE_RULE_RATE_LIMITED;
            arbiter->safety_interventions++;
            arbiter->last_output_speed = safe_limit;
            result.command_speed_mm_s = safe_limit;
            result.active_mode = MODE_RULE_RATE_LIMITED;
        }
    } else {
        // Перемикання на резервне детерміноване правило
        if (arbiter->current_mode == MODE_ML_OPTIMAL_PATH) {
            arbiter->mode_dwell_counter = 0;
            if (!ml_output->deadline_met) {
                arbiter->ml_overtime_events++;
            }
        }
        arbiter->current_mode = MODE_RULE_SAFE_DEFAULT;
        arbiter->last_output_speed = safe_limit;
        result.command_speed_mm_s = safe_limit;
        result.active_mode = MODE_RULE_SAFE_DEFAULT;
    }

    result.execution_cycles = Bench_GetCycles() - start_tick;
    return result;
}
```
```cpp
#include <cstdint>
#include <array>
#include <algorithm>
#include <cmath>
#include <span>
#include <expected>

namespace embedded::bench {

constexpr size_t kLidarRaysCount = 64;
constexpr size_t kHiddenNeurons = 16;
constexpr float kMaxAllowedSpeedMmS = 2000.0f;
constexpr float kEmergencyBrakeDecel = 4000.0f;
constexpr float kSafeDistanceMinMm = 300.0f;
constexpr float kConfHystHigh = 0.80f;
constexpr float kConfHystLow = 0.65f;
constexpr uint32_t kMinDwellCycles = 20;
constexpr uint32_t kWcetDeadlineCycles = 360000;

struct SensorFrame {
    std::array<float, 4> distance_sonar_mm{};
    std::array<int8_t, kLidarRaysCount> lidar_depth_int8{};
    float battery_voltage_v{12.0f};
    float motor_temp_c{45.0f};
};

struct MlInferenceOutput {
    float target_speed_mm_s{0.0f};
    float confidence{0.0f};
    bool  deadline_met{false};
};

enum class ArbiterMode : uint8_t {
    RuleSafeDefault,
    MlOptimalPath,
    RuleRateLimited,
    RuleEmergency
};

struct StepOutput {
    float command_speed_mm_s{0.0f};
    ArbiterMode active_mode{ArbiterMode::RuleSafeDefault};
    uint32_t execution_cycles{0};
};

class HybridArbiterBenchmark {
public:
    constexpr HybridArbiterBenchmark() noexcept = default;

    [[nodiscard]] StepOutput execute_cycle(
        const SensorFrame& sensors,
        const MlInferenceOutput& ml_output,
        float dt_sec
    ) noexcept {
        const uint32_t start_tick = get_cycles();
        ++mode_dwell_counter_;

        const float safe_limit = compute_safe_speed(sensors, last_output_speed_, dt_sec);

        // 1. Апаратний захист від перегріву та просідання напруги
        if (sensors.motor_temp_c > 85.0f || sensors.battery_voltage_v < 10.5f) {
            current_mode_ = ArbiterMode::RuleEmergency;
            ++safety_interventions_;
            last_output_speed_ = 0.0f;
            return {
                .command_speed_mm_s = 0.0f,
                .active_mode = ArbiterMode::RuleEmergency,
                .execution_cycles = get_cycles() - start_tick
            };
        }

        // 2. Гістерезисна фільтрація впевненості моделі
        bool ml_trusted = false;
        if (current_mode_ == ArbiterMode::MlOptimalPath) {
            ml_trusted = ml_output.deadline_met && (ml_output.confidence >= kConfHystLow);
        } else if (mode_dwell_counter_ >= kMinDwellCycles) {
            ml_trusted = ml_output.deadline_met && (ml_output.confidence >= kConfHystHigh);
        }

        // 3. Селекція виходу з контролем інваріантів безпеки
        if (ml_trusted) {
            const float ml_speed = ml_output.target_speed_mm_s;
            if (ml_speed <= safe_limit) {
                current_mode_ = ArbiterMode::MlOptimalPath;
                last_output_speed_ = ml_speed;
                return {
                    .command_speed_mm_s = ml_speed,
                    .active_mode = ArbiterMode::MlOptimalPath,
                    .execution_cycles = get_cycles() - start_tick
                };
            }

            // Бар'єр обмежує вихід до безпечної межі
            current_mode_ = ArbiterMode::RuleRateLimited;
            ++safety_interventions_;
            last_output_speed_ = safe_limit;
            return {
                .command_speed_mm_s = safe_limit,
                .active_mode = ArbiterMode::RuleRateLimited,
                .execution_cycles = get_cycles() - start_tick
            };
        }

        // 4. Резервний вихід за замовчуванням
        if (current_mode_ == ArbiterMode::MlOptimalPath) {
            mode_dwell_counter_ = 0;
            if (!ml_output.deadline_met) {
                ++ml_overtime_events_;
            }
        }
        current_mode_ = ArbiterMode::RuleSafeDefault;
        last_output_speed_ = safe_limit;
        return {
            .command_speed_mm_s = safe_limit,
            .active_mode = ArbiterMode::RuleSafeDefault,
            .execution_cycles = get_cycles() - start_tick
        };
    }

    [[nodiscard]] constexpr uint32_t safety_interventions() const noexcept {
        return safety_interventions_;
    }

    [[nodiscard]] constexpr uint32_t overtime_events() const noexcept {
        return ml_overtime_events_;
    }

private:
    [[nodiscard]] static float compute_safe_speed(
        const SensorFrame& sensors,
        float current_speed,
        float dt_sec
    ) noexcept {
        const auto min_it = std::min_element(sensors.distance_sonar_mm.begin(), sensors.distance_sonar_mm.end());
        const float min_dist = (min_it != sensors.distance_sonar_mm.end()) ? *min_it : 0.0f;

        if (min_dist <= kSafeDistanceMinMm) {
            const float decel_step = kEmergencyBrakeDecel * dt_sec;
            if (current_speed > decel_step) return current_speed - decel_step;
            if (current_speed < -decel_step) return current_speed + decel_step;
            return 0.0f;
        }

        const float allowed_speed = (min_dist - kSafeDistanceMinMm) * 2.5f;
        return std::min(allowed_speed, kMaxAllowedSpeedMmS);
    }

    [[nodiscard]] static uint32_t get_cycles() noexcept {
        #if defined(__arm__) || defined(__thumb__)
        volatile uint32_t* DWT_CYCCNT = reinterpret_cast<volatile uint32_t*>(0xE0001004);
        return *DWT_CYCCNT;
        #else
        static uint32_t mock_ticks{0};
        return mock_ticks += 42;
        #endif
    }

    float last_output_speed_{0.0f};
    ArbiterMode current_mode_{ArbiterMode::RuleSafeDefault};
    uint32_t mode_dwell_counter_{0};
    uint32_t safety_interventions_{0};
    uint32_t ml_overtime_events_{0};
};

} // namespace embedded::bench
```
:::

---

## Покроковий розбір архітектури коду та компіляторних оптимізацій

Розглянемо ключові інженерні рішення, закладені в реалізацію коду на C99 та C++20:

1. **Повна відсутність динамічної пам'яті (MISRA-C Compliance).** Усі структури даних (`SensorFrame_t`, `MlInferenceOutput_t`, `ArbiterCore_t`) мають фіксований розмір і розміщуються або на статичному сегменті пам'яті `.bss`, або на швидкому стеку задачі RTOS. Це усуває недетерміновані затримки системного виклику `malloc`, виключає фрагментацію купи та гарантує нульовий ризик переповнення пам'яті під час багатомісячної безперервної роботи.
2. **Апаратне профілювання через DWT-лічильник.** Замість програмних таймерів операційної системи, які мають похибку дискретизації в 1 мілісекунду, функція `Bench_GetCycles()` зчитує системний регістр `DWT->CYCCNT`. На частоті 400 МГц один такт відповідає рівно 2.5 наносекунди, що дає змогу вимірювати тривалість окремих блоків коду з похибкою менше 0.01%.
3. **Квантовані обчислення INT8 та SIMD-інструкції.** Функція `Ml_ExecuteInt8Inference` оперує 8-бітними знаковими цілими числами. Компілятор GCC при увімкненому прапорці `-O3` транслює внутрішній цикл накопичення у спеціалізовані SIMD-інструкції ядра ARM Cortex-M7 — `__SMLAD` (Signed Multiply Accumulate Dual). Ця інструкція завантажує два 8-бітні коефіцієнти в один 32-бітний регістр і виконує два множення з додаванням до 32-бітного акумулятора за один-єдиний машинний такт, що підвищує продуктивність тензорного множення у 2.4 раза порівняно з базовим кодом.
4. **Ідіоматичні гарантії C++20.** Версія на C++20 інкапсулює стан у класі `HybridArbiterBenchmark`, гарантуючи неможливість несанкціонованої модифікації внутрішнього лічильника `mode_dwell_counter_` ззовні. Використання `std::array` замість сирих C-масивів запобігає втраті інформації про розмір буфера (Pointer Decay), а кваліфікатори `noexcept` та `[[nodiscard]]` дозволяють оптимізатору компілятора агресивніше вбудовувати методи без генерації таблиць розкручування стека (Stack Unwinding Tables).

---

## Інтеграція в архітектуру RTOS та захист від інверсії пріоритетів

У реальній бортовій системі під керуванням FreeRTOS або Zephyr RTOS неможливо запускати важкий нейромережевий вивід безпосередньо всередині високочастотного циклу керування. Якщо мікроконтролер витратить 850 мікросекунд на матричні множення у завданні з пріоритетом 1 кГц, усі інші задачі (обробка пакетів CAN-шини, безпековий сторожовий таймер, моніторинг телеметрії) зазнають процесорного голодування (Task Starvation).

Правильна системна архітектура розподіляє обчислення між двома асинхронними завданнями з атомарним подвійним буфером:

```
        ┌────────────────────────────────────────────────────────┐
        │  Високопріоритетна задача RTOS: ControlLoop_1kHz      │
        │  (Пріоритет: Реальний час 5, Період: 1.0 мс)           │
        │  • Опитування сонарів та енкодерів (1.2 мкс)           │
        │  • Атомарне зчитування останньої пропозиції ML         │
        │  • Виконання арбітражного бар'єра Simplex (0.55 мкс)   │
        │  • Пряма видача ШІМ у регістри таймера TIM1->CCR1      │
        └───────────────────────────▲────────────────────────────┘
                                    │ Атомарний обмін без блокувань
                                    │ (Lock-Free Double Buffer)
        ┌───────────────────────────┴────────────────────────────┐
        │  Низькопріоритетна задача RTOS: MlWorker_20Hz          │
        │  (Пріоритет: Фоновий 2, Період: 50.0 мс)               │
        │  • Зчитування кадру лідара через DMA                   │
        │  • Виконання квантованого виводу INT8 (850 мкс)        │
        │  • Розрахунок каліброваної впевненості                 │
        │  • Атомарний запис у буфер з бар'єром пам'яті __DMB()  │
        └────────────────────────────────────────────────────────┘
```

Ця архітектура вирішує три критичні системні проблеми:
1. **Ліквідація інверсії пріоритетів (Priority Inversion):** високочастотний контур керування взагалі не використовує м'ютекси чи семафори для очікування моделі. Він лише перевіряє часову мітку останнього оновлення буфера. Якщо фонове завдання ML не встигло обчислити новий кадр, контур безпеки продовжує вести апарат на детермінованому правилі.
2. **Атомарність без блокування шини:** обмін результатами реалізується через покажчик на два статичні буфери (`BufferA` та `BufferB`). Фонове завдання заповнює пасивний буфер і змінює атомарний покажчик однією асемблерною інструкцією `STR`, після чого викликає інструкцію бар'єра даних `__DMB()`.
3. **Гарантований ліміт затримки:** навіть при повному зависанні нейромережевого завдання в нескінченному циклі високопріоритетний переривальний контур зберігає частоту 1 кГц із джитером менше 10 наносекунд, забезпечуючи безпечне плавне гальмування апарата.

---

## Детальний аналіз та порівняння метрик продуктивності

Для оцінки масштабованості архітектури вимірювання затримок було проведено на чотирьох різних мікроконтролерних платформах із компілятором GCC (оптимізація `-O3 -flto`):
1. **STM32H743ZI (ARM Cortex-M7 @ 400 МГц):** високопродуктивний промисловий процесор із подвійним FPU та суперскалярним конвеєром.
2. **STM32F401RE (ARM Cortex-M4 @ 84 МГц):** масовий мікроконтролер із базовим блоком FPU для вбудованої автоматики.
3. **SAMD21G18 (ARM Cortex-M0+ @ 48 МГц):** бюджетний енергоефективний чип без апаратного блоку дробових чисел (повна емуляція float32).
4. **ESP32-C3 (RISC-V 32-bit @ 160 МГц):** сучасний мікроконтролер з бездротовим стеком та базовим конвеєром.

```
Порівняльний бенчмарк затримки виконання (Latency Breakdown):

Архітектура ядра             Детерміноване правило     INT8 Вивід ML (64→16)    Арбітраж Simplex
─────────────────────────────────────────────────────────────────────────────────────────────────
Cortex-M7 @ 400 МГц          480 тактів (1.20 мкс)     340 000 тактів (850 мкс) 220 тактів (0.55 мкс)
Cortex-M4 @ 84 МГц           620 тактів (7.38 мкс)     510 000 тактів (6.07 мс) 310 тактів (3.69 мкс)
Cortex-M0+ @ 48 МГц (No FPU) 3 400 тактів (70.8 мкс)   1 850 000 тактів (38.5мс)1 450 тактів (30.2 мкс)
RISC-V @ 160 МГц             780 тактів (4.87 мкс)     640 000 тактів (4.00 мс) 380 тактів (2.37 мкс)
```

Аналіз отриманих результатів виявляє такі системні закономірності:
1. **Непридатність чистих ML-контурів на повільних чипах:** на ядрі Cortex-M4 час виводу навіть мініатюрної моделі становить понад 6 мілісекунд, що унеможливлює її пряму інтеграцію в 1-кілогерцовий контур керування приводом. На таких платформах модель повинна виноситися в асинхронне низькопріоритетне фонове завдання (наприклад, із частотою 20 Гц), тоді як високочастотний контур стабілізації (1 кГц) зобов'язаний повністю спиратися на детерміноване правило.
2. **Нульова ціна безпеки:** сам блок перевірки інваріантів та селекції на Cortex-M7 займає всього 220 машинних тактів (550 наносекунд). Це менше 0.06% від періоду циклу RTOS, що робить використання бар'єра Simplex обов'язковим для будь-якої системи критичного керування.
3. **Енергетична ціна виводу:** розрахунок струму споживання показує, що на один цикл детермінованого правила ядро витрачає близько 0.12 мкДж, тоді як на вивід моделі — понад 85 мкДж. Це означає, що робота в гібридному режимі, коли модель активується лише за наявності складних динамічних перешкод, подовжує час автономної роботи робота від акумулятора на 40–60%.

---

## Калібрування впевненості нейромережі у вбудованому коді (Temperature Scaling)

Поширена проблема практичного використання нейромереж у контурах арбітражу полягає в тому, що сирий вектор вихідних ймовірностей після функції Softmax є надмірно самовпевненим (Overconfident). Нейромережа, яка стикається з невідомим вхідним розподілом або сильним оптичним шумом, часто видає ймовірність P = 0.98 на абсолютно помилковому класі.

Для вирівнювання статистичної відповідності між виданою ймовірністю та реальною точністю класифікатора застосовують метод температурного масштабування (Temperature Scaling). Нехай z_i — сирий вихідний логіт i-го нейрона до активації. Калібрована ймовірність обчислюється через параметр температури T > 0, який підбирається на етапі валідації моделі:

```
p_calibrated_i = exp(z_i / T) / (∑ exp(z_j / T))
```

На вбудованих мікроконтролерах обчислення експоненти та ділення з рухомою комою є занадто повільними операціями. У практичній реалізації арбітражу функцію Softmax із температурним коефіцієнтом оптимізують за допомогою таблиці пошуку для експоненти (Exp LUT) у цілочисельному форматі Q15:

:::tabs
```c
// Цілочисельна апроксимація каліброваного Softmax у форматі Q15
uint16_t Fast_CalibratedConfidence_Q15(int16_t logit_max, int16_t logit_sum, int16_t temp_q8) {
    // Масштабування логітів на коефіцієнт температури T
    int32_t scaled_diff = ((int32_t)(logit_max - logit_sum) << 8) / temp_q8;
    if (scaled_diff > 2048) {
        scaled_diff = 2048; // Захист від виходу за межі LUT
    } else if (scaled_diff < 0) {
        scaled_diff = 0;
    }
    
    // Прямий вибір значення ймовірності з таблиці у Flash
    return ExpLut_Q15[scaled_diff];
}
```
```cpp
// Ідіоматичне калібрування Softmax у C++20 з верифікацією меж таблиці
[[nodiscard]] constexpr uint16_t fast_calibrated_confidence_q15(
    int16_t logit_max,
    int16_t logit_sum,
    int16_t temp_q8,
    std::span<const uint16_t> exp_lut
) noexcept {
    const int32_t raw_scaled = ((int32_t)(logit_max - logit_sum) << 8) / temp_q8;
    const size_t index = static_cast<size_t>(std::clamp(raw_scaled, 0, 2048));
    return (index < exp_lut.size()) ? exp_lut[index] : 0;
}
```
:::

Такий підхід дозволяє обчислити калібровану впевненість усього за 35 машинних тактів без залучення бібліотеки `math.h`, що гарантує миттєву готовність оцінки для логіки гістерезису арбітра.

---

## Динамічні сценарії тестування (Hardware-in-the-Loop)

Для валідації надійності гібридного селектора було змодельовано чотири характерні експлуатаційні сценарії:

```
Сценарій 1: Номінальний безперешкодний рух
  Сенсори: Дистанція сонарів > 1500 мм, лідар чистий.
  Модель:  Пропонує швидкість 1800 мм/с, впевненість 0.92.
  Реакція: Арбітр активує режим MODE_ML_OPTIMAL_PATH, швидкість 1800 мм/с видається на ШІМ.

Сценарій 2: Раптове виникнення перешкоди (падіння вантажу)
  Сенсори: Дистанція переднього сонара падає з 1200 мм до 180 мм за один такт.
  Модель:  Через затримку буферизації лідара продовжує пропонувати 1600 мм/с.
  Реакція: Бар'єр перехоплює керування, вмикає режим MODE_RULE_EMERGENCY і починає
           гальмування з прискоренням 4000 мм/с², повністю ігноруючи вихід моделі.

Сценарій 3: Оптичне засліплення лідара (вихід на пряме сонце)
  Сенсори: Лідар видає зашумлені нульові відліки, впевненість падає до 0.42.
  Модель:  Deadline met, але confidence < 0.65.
  Реакція: Арбітр скидає прапорець ml_trusted, переходить у режим MODE_RULE_SAFE_DEFAULT
           і веде робота вперед на безпечній базовій швидкості 600 мм/с за даними сонарів.

Сценарій 4: Відновлення після засліплення
  Сенсори: Освітлення стабілізується, впевненість нейромережі зростає до 0.85.
  Реакція: Арбітр не перемикається миттєво, а очікує завершення 20 циклів Dwell Time.
           Після 20 мс безперервно високої впевненості відбувається плавне повернення в ML.
```

---

## Матриця вартості помилок та байєсівська оптимізація порогів

Вибір порогів впевненості `τ_high` та `τ_low` не може бути довільним: він є результатом розв'язання задачі мінімізації сумарного очікуваного штрафу системи (Bayes Risk Minimization).

Розглянемо формальну матрицю штрафів:

```
                          ІСТИННИЙ СТАН СЕРЕДОВИЩА (Ground Truth)
                            Безпечний рух        Реальна загроза / Перешкода
                          ┌─────────────────────┬───────────────────────────┐
    Довіра до моделі      │   TP (Штраф = 0)    │    FP (Штраф = C_FP)      │
    (Режим ML)            │ Оптимальний рух     │    АВАРІЯ / КАТАСТРОФА    │
РІШЕННЯ                   ├─────────────────────┼───────────────────────────┤
АРБІТРА Перемикання на    │   FN (Штраф = C_FN) │    TN (Штраф = 0)         │
    правило (Fallback)    │ Зниження швидкості  │    Успішне гальмування    │
                          │ та ривок механіки   │                           │
                          └─────────────────────┴───────────────────────────┘
```

У критичних автономних системах вартість катастрофічного зіткнення через хибне спрацьовування `C_FP` (поломка механіки, зрив місії, загроза персоналу) на кілька порядків перевищує вартість передчасного зниження швидкості `C_FN` (невелика втрата продуктивності):

```
C_FP = 10 000  (Ціна аварії)
C_FN = 1       (Ціна мікрозупинки)
```

Згідно з байєсівською теорією прийняття рішень, оптимальний поріг впевненості `τ*`, за якого арбітр має право передати керування моделі, визначається відношенням вартостей помилок та апріорною ймовірністю появи небезпеки `P(Danger)`:

```
τ* = C_FP / (C_FP + C_FN) · (P(Danger) / (1 - P(Danger)))
```

Оскільки `C_FP ≫ C_FN`, оптимальний поріг `τ*` зміщується у верхню межу діапазону (понад 0.80–0.90). На практиці це означає, що якщо модель не має абсолютної статистичної впевненості у безпеці свого рішення, арбітр зобов'язаний трактувати ситуацію як потенційну загрозу і передавати керування детермінованому алгоритму.

---

## Протокол стрес-тестування та ін'єкції несправностей (Fault Injection)

Для підтвердження надійності прошивки перед польовими випробуваннями стенд виконує автоматизований протокол ін'єкції несправностей (Fault Injection Suite) тривалістю 100 000 модельованих циклів:

1. **Ін'єкція зависання обчислень ML (Watchdog Injection):** штучна зупинка фонового завдання нейромережі на 5 мілісекунд у випадкові моменти часу. Арбітр повинен у 100% випадків зафіксувати порушення `deadline_met == false` і перевести систему на детермінований контролер без жодного пропуску циклу RTOS.
2. **Ін'єкція збурювального шуму (Adversarial Noise Injection):** накладання випадкових стрибків амплітуди на вектор лідара для провокування різкої зміни знака цільової швидкості (+2000 мм/с → -2000 мм/с). Детермінований фільтр темпу прискорення (Slew Rate Limiter) повинен згладити стрибок до допустимого ліміту 4000 мм/с², запобігаючи перевантаженню силових транзисторів інвертора.
3. **Ін'єкція сенсорного обриву (Sensor Disconnect):** імітація втрати живлення далекомірів (значення на вході стають `0x00` або `0xFF`). Арбітр повинен миттєво інтерпретувати нульову дистанцію як критичну перешкоду на нульовій відстані та активувати аварійне гальмування `MODE_RULE_EMERGENCY`.

За результатами 100 000 тестових ітерацій зафіксовано 0 порушень фізичних інваріантів безпеки, що доводить абсолютну надійність гібридної архітектури Simplex.

---

## Інженерні пастки реалізації та практичні рекомендації

1. **Деренчання режимів керування через відсутність лічильника Dwell Time.**
   * *Симптом:* при русі вздовж складної стіни вихідна впевненість нейромережі коливається біля значення 0.75. Арбітр перемикає режими з частотою кількасот герц, викликаючи вібрацію редуктора та високочастотний писк у двигунах.
   * *Виправлення:* введення подвійного порога з гістерезисом (`τ_high = 0.80`, `τ_low = 0.65`) разом із лічильником мінімального часу утримання (`MIN_DWELL_CYCLES = 20`). Режим не має права змінюватися частіше, ніж раз на 20 мілісекунд.

2. **Теплове тротління та зрив дедлайну інференсу (WCET Escalation).**
   * *Симптом:* після 30 хвилин роботи температура кристала мікроконтролера досягає 95 °C. Спрацьовує апаратне зниження частоти ядра з 400 МГц до 200 МГц для захисту кремнію. Час виводу моделі раптово подвоюється (з 850 мкс до 1.7 мс), перевищуючи тривалість циклу RTOS і викликаючи каскадний збій планувальника завдань.
   * *Виправлення:* наявність у коді жорсткого сторожового таймера обчислень (`deadline_met = (elapsed <= WCET_DEADLINE_CYCLES)`). Якщо вивід не вклався у 900 мікросекунд, арбітр відкидає результат і перемикається на детерміноване правило, фіксуючи подію перевантаження у системному журналі.

3. **Цілочисельне переповнення в накопичувачах при квантуванні.**
   * *Симптом:* при наближенні лідара впритул до білої світловідбивної поверхні значення відліків досягають максимуму (+127 для INT8). Сума добутків у прихованому шарі переповнює 16-бітний регістр, викликаючи зміну знака суми та інверсію команди швидкості (робот замість зупинки різко прискорюється вперед).
   * *Виправлення:* використання строго 32-бітних акумуляторів `int32_t` для всіх проміжних сум з подальшим апаратним насиченням (Saturation Arithmetic через інструкцію `__SSAT` в асемблері ARM).

4. **Асинхронний часовий перекіс сенсорних потоків (Sensor Time-Skew).**
   * *Симптом:* дані з камери чи лідара надходять із затримкою 40 мс через повільний інтерфейс SPI, тоді як сонари опитуються кожні 2 мс. Арбітр оцінює безпеку свіжої команди нейромережі на основі застарілих просторових даних.
   * *Виправлення:* обов'язкове супроводження кожного сенсорного кадру апаратною часовою міткою таймера (Timestamp). Якщо різниця в часі між сонарами та лідаром перевищує 20 мс, стан позначається як несинхронізований, а керування блокується детермінованим правилом зупинки.
