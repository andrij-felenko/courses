# ⚙️ Автономний тестер герметичності на спад вакууму (Vacuum Decay Testing)

Традиційний польовий метод перевірки вологозахисту зануренням зібраного приладу у ванну з водою несе критичний ризик: якщо ущільнення встановлено з перекосом або кабель не обтиснуто сальником, вода миттєво затоплює дорогі електронні компоненти, безповоротно виводячи їх із ладу ще до першого вмикання. Інженерним стандартом неруйнівного контролю герметичності оболонок (стандарти ASTM F2338 та ISO 20484) є метод **спаду вакууму** (англ. *Vacuum Decay Testing*).

Суть методу полягає у відкачуванні невеликої кількості повітря з внутрішнього об'єму приладу через технологічний сервісний порт (наприклад, клапан Шредера або швидкорознімний штуцер) до створення помірного розрідження −20...−40 кПа, перекритті клапана та прецизійному відстеженні швидкості наростання тиску `dP/dt` за допомогою цифрового давача. Якщо корпус герметичний, тиск залишається стабільним. Якщо є мікротріщина чи нещільність прокладки, зовнішнє атмосферне повітря просочується всередину, викликаючи лінійний спад вакууму.

Нижче наведено математичну модель випробування, розрахунок еквівалентного мікроотвору за законом Пуазейля, фізику теплових артефактів та повноцінну вбудовану реалізацію алгоритму діагностики мовами C та C++.

---

## 1. Фізична модель та розрахунок еквівалентного дефекту

Об'ємний потік витоку `Q_leak` (в Па·м³/с або мбар·л/с) пов'язаний зі швидкістю зміни тиску `dP/dt` та внутрішнім вільним об'ємом боксу `V_box` залежністю:

```
Q_leak = V_box · (dP / dt)   [Па·м³/с]
```

Для оцінки розміру фізичного дефекту (наприклад, пори в зварному шві або зазору між жилами кабелю) застосовують рівняння Пуазейля для ламінарного перетікання стисливого газу крізь циліндричний капіляр діаметром `d` і довжиною `L`:

```
Q_leak = (π · d⁴ · (P_ext² − P_int²)) / (256 · μ · L)
```

де:
- `d` — еквівалентний гідравлічний діаметр отвору витоку `[м]`;
- `L` — довжина каналу витоку (наприклад, ширина паза O-ring або довжина сальника) `[м]`;
- `μ` — динамічна в'язкість повітря (`μ ≈ 1.81 · 10⁻⁵ Па·с` при +20 °C);
- `P_ext` — зовнішній атмосферний тиск (`≈ 101 325 Па`);
- `P_int` — внутрішній тиск у боксі під час тесту (`≈ 71 325 Па`, тобто вакуум −30 кПа).

Через залежність потоку від четвертого степеня діаметра (`d⁴`) навіть мікроскопічний капіляр діаметром `d = 10 мкм` (удвічі тонший за людську волосину) при довжині `L = 3 мм` створює потік витоку:

```
Q_leak ≈ (3.1415 · (10⁻⁵)⁴ · (101325² − 71325²)) / (256 · 1.81 · 10⁻⁵ · 0.003)
       ≈ (3.1415 · 10⁻²⁰ · 5.18 · 10⁹) / (1.39 · 10⁻⁵)
       ≈ 1.17 · 10⁻⁴ Па·м³/с = 1.17 · 10⁻³ мбар·л/с
```

У 3-літровому корпусі такий дефект дає швидкість спаду вакууму:

```
dP / dt = Q_leak / V_box = (1.17 · 10⁻⁴ Па·м³/с) / 0.003 м³ = 0.039 Па/с = 2.34 Па/хв
```

Така швидкість надійно детектується сучасними 24-бітними барометричними давачами з роздільною здатністю 0.1–0.5 Па.

---

## 2. Фази вимірювального циклу та температурна фільтрація

Вимірювальний цикл розбивається на чотири послідовні фази:

1. **Фаза відкачування (Evacuation Phase, 5–15 с):** мікровакуумний насос створює розрідження до цільового рівня `P_target` (зазвичай 70 кПа абсолютного тиску при нормальному атмосферному 101.3 кПа, тобто `ΔP = −31.3 кПа`). Якщо за 30 секунд цільовий рівень не досягнуто, фіксується груба розгерметизація або відсутність ущільнення.
2. **Фаза стабілізації (Settling / Equalization Phase, 15–30 с):** електромагнітний клапан перекриває магістраль насоса. Під час відкачування повітря зазнає адіабатичного розширення й охолоджується на 1.5–3 °C. У фазі стабілізації повітря забирає тепло від масивних алюмінієвих стінок корпусу, нагріваючись назад до температури конструкції, через що тиск тимчасово зростає за законом Шарля незалежно від наявності витоку. Одночасно відбувається механічна в'язкопружна релаксація гумового O-ring у пазу. Вимірювання у цей період не проводяться.
3. **Фаза вимірювання (Testing / Decay Phase, 30–120 с):** періодичне опитування давача тиску з фіксованим інтервалом (наприклад, кожні 500 мс). Для виключення випадкового шуму АЦП та квантування кутовий коефіцієнт `dP/dt` обчислюється методом лінійної регресії за найменшими квадратами (OLS):
   ```
   dP/dt = (N · Σ(t_i · P_i) − Σ(t_i) · Σ(P_i)) / (N · Σ(t_i²) − (Σ(t_i))²)
   ```
4. **Оцінка результату (Verdict Phase):** якщо `dP/dt ≤ (dP/dt)_max` (де пороговий спад зазвичай становить `0.05...0.15 кПа/хв`), оболонка вважається придатною для занурення на клас IP67/IP68.

---

## 3. Реалізація діагностичного автомата мовами C та C++

Модуль приймає параметри тесту, керує станами скінченного автомата (FSM), накопичує вибірки тиску та розраховує лінійний нахил із перевіркою критеріїв проходження.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX_SAMPLES 128

typedef enum {
    TEST_STATE_IDLE = 0,
    TEST_STATE_EVACUATION,
    TEST_STATE_SETTLING,
    TEST_STATE_MEASURING,
    TEST_STATE_PASSED,
    TEST_STATE_FAILED_LEAK,
    TEST_STATE_FAILED_TIMEOUT
} vacuum_test_state_t;

typedef struct {
    float target_vacuum_kpa;     /* Цільове розрідження (наприклад, 30.0 кПа) */
    float max_leak_rate_kpa_min;  /* Граничний витік (наприклад, 0.10 кПа/хв) */
    uint32_t settling_time_ms;    /* Час стабілізації (наприклад, 15000 мс) */
    uint32_t measure_time_ms;     /* Час вимірювання (наприклад, 45000 мс) */
} vacuum_config_t;

typedef struct {
    vacuum_config_t config;
    vacuum_test_state_t state;
    uint32_t state_start_ms;
    float start_pressure_kpa;
    float current_pressure_kpa;
    float calculated_leak_rate_kpa_min;

    /* Буфер регресії OLS */
    float time_sec[MAX_SAMPLES];
    float pressure_kpa[MAX_SAMPLES];
    size_t sample_count;
    uint32_t last_sample_ms;
} vacuum_tester_t;

void vacuum_tester_init(vacuum_tester_t *t, const vacuum_config_t *cfg) {
    if (!t || !cfg) return;
    t->config = *cfg;
    t->state = TEST_STATE_IDLE;
    t->calculated_leak_rate_kpa_min = 0.0f;
    t->sample_count = 0;
}

void vacuum_tester_start(vacuum_tester_t *t, float ambient_pressure_kpa, uint32_t now_ms) {
    if (!t) return;
    t->start_pressure_kpa = ambient_pressure_kpa;
    t->current_pressure_kpa = ambient_pressure_kpa;
    t->state = TEST_STATE_EVACUATION;
    t->state_start_ms = now_ms;
    t->sample_count = 0;
    t->last_sample_ms = now_ms;
}

static float compute_linear_slope_ols(const float *x, const float *y, size_t n) {
    if (n < 2) return 0.0f;
    float sum_x = 0.0f, sum_y = 0.0f, sum_xy = 0.0f, sum_xx = 0.0f;
    for (size_t i = 0; i < n; ++i) {
        sum_x += x[i];
        sum_y += y[i];
        sum_xy += x[i] * y[i];
        sum_xx += x[i] * x[i];
    }
    float denom = (float)n * sum_xx - sum_x * sum_x;
    if (denom == 0.0f) return 0.0f;
    return ((float)n * sum_xy - sum_x * sum_y) / denom;
}

void vacuum_tester_update(vacuum_tester_t *t, float p_kpa, uint32_t now_ms, bool *pump_en, bool *valv_en) {
    if (!t) return;
    t->current_pressure_kpa = p_kpa;
    uint32_t elapsed = now_ms - t->state_start_ms;

    switch (t->state) {
        case TEST_STATE_EVACUATION:
            if (pump_en) *pump_en = true;
            if (valv_en) *valv_en = true;
            /* Перевіряємо досягнення розрідження */
            if ((t->start_pressure_kpa - p_kpa) >= t->config.target_vacuum_kpa) {
                t->state = TEST_STATE_SETTLING;
                t->state_start_ms = now_ms;
                if (pump_en) *pump_en = false;
            } else if (elapsed > 30000) { /* Таймаут відкачування 30 с */
                t->state = TEST_STATE_FAILED_TIMEOUT;
                if (pump_en) *pump_en = false;
                if (valv_en) *valv_en = false;
            }
            break;

        case TEST_STATE_SETTLING:
            if (pump_en) *pump_en = false;
            if (valv_en) *valv_en = true;
            if (elapsed >= t->config.settling_time_ms) {
                t->state = TEST_STATE_MEASURING;
                t->state_start_ms = now_ms;
                t->sample_count = 0;
                t->last_sample_ms = now_ms;
            }
            break;

        case TEST_STATE_MEASURING:
            if (pump_en) *pump_en = false;
            if (valv_en) *valv_en = true;

            /* Вибірка раз на 500 мс */
            if (now_ms - t->last_sample_ms >= 500 && t->sample_count < MAX_SAMPLES) {
                t->time_sec[t->sample_count] = (float)elapsed / 1000.0f;
                t->pressure_kpa[t->sample_count] = p_kpa;
                t->sample_count++;
                t->last_sample_ms = now_ms;
            }

            if (elapsed >= t->config.measure_time_ms) {
                float slope_kpa_per_sec = compute_linear_slope_ols(t->time_sec, t->pressure_kpa, t->sample_count);
                /* Переводимо в кПа/хв */
                t->calculated_leak_rate_kpa_min = slope_kpa_per_sec * 60.0f;

                if (t->calculated_leak_rate_kpa_min <= t->config.max_leak_rate_kpa_min) {
                    t->state = TEST_STATE_PASSED;
                } else {
                    t->state = TEST_STATE_FAILED_LEAK;
                }
                if (valv_en) *valv_en = false;
            }
            break;

        default:
            if (pump_en) *pump_en = false;
            if (valv_en) *valv_en = false;
            break;
    }
}
```

@tab C++
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <numeric>

enum class TestState : uint8_t {
    Idle,
    Evacuating,
    Settling,
    Measuring,
    Passed,
    FailedLeak,
    FailedTimeout
};

struct TestConfig {
    float target_vacuum_kpa{30.0f};
    float max_leak_rate_kpa_min{0.10f};
    uint32_t settling_time_ms{15000};
    uint32_t measure_time_ms{45000};
};

struct ActuatorControl {
    bool pump_enable{false};
    bool valve_enable{false};
};

class VacuumDecayTester {
public:
    static constexpr size_t kMaxSamples = 128;

    explicit constexpr VacuumDecayTester(const TestConfig& config) noexcept
        : config_(config) {}

    void start(float ambient_pressure_kpa, uint32_t now_ms) noexcept {
        start_pressure_kpa_ = ambient_pressure_kpa;
        current_pressure_kpa_ = ambient_pressure_kpa;
        state_ = TestState::Evacuating;
        state_start_ms_ = now_ms;
        sample_count_ = 0;
        last_sample_ms_ = now_ms;
        calculated_leak_rate_ = 0.0f;
    }

    ActuatorControl update(float p_kpa, uint32_t now_ms) noexcept {
        current_pressure_kpa_ = p_kpa;
        const uint32_t elapsed = now_ms - state_start_ms_;
        ActuatorControl ctrl{};

        switch (state_) {
            case TestState::Evacuating:
                ctrl.pump_enable = true;
                ctrl.valve_enable = true;
                if ((start_pressure_kpa_ - p_kpa) >= config_.target_vacuum_kpa) {
                    state_ = TestState::Settling;
                    state_start_ms_ = now_ms;
                    ctrl.pump_enable = false;
                } else if (elapsed > 30000) {
                    state_ = TestState::FailedTimeout;
                    ctrl.pump_enable = false;
                    ctrl.valve_enable = false;
                }
                break;

            case TestState::Settling:
                ctrl.pump_enable = false;
                ctrl.valve_enable = true;
                if (elapsed >= config_.settling_time_ms) {
                    state_ = TestState::Measuring;
                    state_start_ms_ = now_ms;
                    sample_count_ = 0;
                    last_sample_ms_ = now_ms;
                }
                break;

            case TestState::Measuring:
                ctrl.pump_enable = false;
                ctrl.valve_enable = true;
                if (now_ms - last_sample_ms_ >= 500 && sample_count_ < kMaxSamples) {
                    time_samples_[sample_count_] = static_cast<float>(elapsed) / 1000.0f;
                    pressure_samples_[sample_count_] = p_kpa;
                    ++sample_count_;
                    last_sample_ms_ = now_ms;
                }

                if (elapsed >= config_.measure_time_ms) {
                    float slope_sec = compute_ols_slope(
                        std::span(time_samples_.data(), sample_count_),
                        std::span(pressure_samples_.data(), sample_count_)
                    );
                    calculated_leak_rate_ = slope_sec * 60.0f;

                    state_ = (calculated_leak_rate_ <= config_.max_leak_rate_kpa_min)
                             ? TestState::Passed
                             : TestState::FailedLeak;
                    ctrl.valve_enable = false;
                }
                break;

            default:
                ctrl.pump_enable = false;
                ctrl.valve_enable = false;
                break;
        }
        return ctrl;
    }

    [[nodiscard]] TestState state() const noexcept { return state_; }
    [[nodiscard]] float leak_rate_kpa_min() const noexcept { return calculated_leak_rate_; }

private:
    static float compute_ols_slope(std::span<const float> x, std::span<const float> y) noexcept {
        if (x.size() < 2 || x.size() != y.size()) return 0.0f;
        const auto n = static_cast<float>(x.size());
        float sum_x = 0.0f, sum_y = 0.0f, sum_xy = 0.0f, sum_xx = 0.0f;
        for (size_t i = 0; i < x.size(); ++i) {
            sum_x += x[i];
            sum_y += y[i];
            sum_xy += x[i] * y[i];
            sum_xx += x[i] * x[i];
        }
        const float denom = n * sum_xx - sum_x * sum_x;
        if (denom == 0.0f) return 0.0f;
        return (n * sum_xy - sum_x * sum_y) / denom;
    }

    TestConfig config_{};
    TestState state_{TestState::Idle};
    uint32_t state_start_ms_{0};
    uint32_t last_sample_ms_{0};
    float start_pressure_kpa_{101.3f};
    float current_pressure_kpa_{101.3f};
    float calculated_leak_rate_{0.0f};

    std::array<float, kMaxSamples> time_samples_{};
    std::array<float, kMaxSamples> pressure_samples_{};
    size_t sample_count_{0};
};
```
:::

---

## 4. Інженерні пастки та компенсація дрейфу

1. **Температурний дрейф стінок:** зміна внутрішньої температури повітря всього на 0.1 °C за хвилину за законом Шарля (`P / T = const`) викликає хибну зміну тиску:
   ```
   ΔP = P · (ΔT / T) ≈ 100 кПа · (0.1 / 293.15) ≈ 0.034 кПа
   ```
   Якщо бокс щойно внесли з холодної вулиці в теплий цех або якщо оператор тримає алюмінієвий корпус теплими руками під час тесту, нагрівання повітря скомпенсує спад вакууму й замаскує реальний витік. Тест слід проводити на термоізольованій підставці лише після повної температурної стабілізації виробу.
2. **Дегазація полімерів (Outgassing):** свіжозалитий силіконовий або поліуретановий компаунд у вакуумі виділяє мікробульбашки розчиненого повітря та залишкових летких речовин, створюючи позірне зростання тиску, яке згасає лише після 2–3 циклів попереднього вакуумування.
3. **Еластична релаксація O-Ring:** під час створення перепаду тиску еластомірний шнур зміщується до внутрішньої стінки паза. Якщо час стабілізації задати менше 10 секунд, деформація матеріалу спотворюватиме нахил кривої `dP/dt`.
4. **Виробнича фіксація результатів:** за успішного проходження тесту прошивка може записувати значення `calculated_leak_rate_kpa_min` разом із датою калібрування в захищену область пам'яті EEPROM/Flash, формуючи незмінний паспорт герметичності виробу.
