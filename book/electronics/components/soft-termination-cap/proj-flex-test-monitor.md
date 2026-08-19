# ⚙️ Автоматизований моніторинг випробувань MLCC на вигин за стандартом AEC-Q200-005

Кваліфікаційне тестування пасивних компонентів для автомобільної та аерокосмічної промисловості вимагає безперервної синхронної реєстрації механічної деформації друкованої плати та електричних параметрів випробовуваного зразка. Стандарт AEC-Q200-005 (тест на вигин підкладки) регламентує опускання натискного пуансона з нормованою швидкістю 1.0 мм/с до досягнення заданого прогину (2.0 мм для звичайних компонентів, 5.0 мм для Soft-Termination) з подальшим утриманням навантаження протягом 60 секунд.

Головна інженерна складність полягає у виявленні моменту зародження мікротріщини. У сухому лабораторному повітрі тріщина кераміки в перші частки секунди не викликає стійкого обриву: опір ізоляції може короткочасно просісти на кілька мікросекунд внаслідок мікророзряду, після чого повернутися до значень понад 100 МОм. Програмно-апаратний комплекс випробувального стенда повинен оцифровувати тензометричний міст, точно контролювати переміщення приводу й одночасно фіксувати швидкоплинні електричні аномалії в реальному часі.

## Апаратна структура випробувального стенда

Стенд для кваліфікації MLCC за стандартом AEC-Q200-005 містить чотири взаємопов'язані апаратні підсистеми:

```
+-----------------------------------------------------------------------------------+
|                        СТРУКТУРА СТЕНДА AEC-Q200-005                              |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Тестова плата FR-4] ───► [Тензоміст 120 Ом]  ───► [24-бітний АЦП]  ──┐         |
|                                                                        │         |
|  [MLCC зразок під Vdc] ──► [LCR / Пікоамперметр] ──► [SPI / DMA] ──────┼─► MCU   |
|                                                                        │         |
|  [Пуансон актуатора]  ◄─── [Драйвер Step/Dir]   ◄─── [Таймер ШІМ] ─────┤         |
|                                                                        │         |
|  [Оптичний енкодер]   ───► [Квадратурний лічильник] ───────────────────┘         |
+-----------------------------------------------------------------------------------+
```

### 1. Тензометричний тракт деформації плати
Для безпосереднього вимірювання поверхневої деформації друкованої плати в мікрострейнах (`με`) використовується фольговий тензорезистор із базою 1.0–2.0 мм та номінальним опором 120 Ом (коефіцієнт тензочутливості `S_g ≈ 2.05...2.15`). Тензодатчик наклеюється на поверхню тестової плати FR-4 безпосередньо поруч із контактним майданчиком конденсатора (на відстані 1.0–1.5 мм паралельно до осі вигину).

Сигнал знімається мостом Вітстона за трипровідною схемою підключення для компенсації температурного дрейфу опору з'єднувальних проводів. Сигнал розбалансу моста підсилюється малошумним інструментальним підсилювачем і оцифровується 24-бітним сигма-дельта АЦП (ADS1232 або ADS1262) із частотою дискретизації 100–1200 вибірок на секунду.

Зв'язок між вихідною диференційною напругою моста `V_out`, напругою живлення моста `V_exc` та деформацією плати `ε` описується рівнянням чверть-мостової схеми:

```
V_out / V_exc = (S_g / 4) · ε
```

Звідси деформація в мікрострейнах визначається як:

```
ε [με] = (4 / S_g) · (V_out / V_exc) · 10⁶
```

Перед початком кожного тесту виконується процедура автоматичного тарування (автонуль): мікроконтролер усереднює 100 вибірок ненавантаженої плати й записує зміщення нуля `V_offset` в оперативну пам'ять.

### 2. Електричний аналізатор конденсатора (Capacitance & Leakage Monitor)
Вимірювальний тракт працює у комбінованому режимі, чергуючи два типи вимірювань:
- **Вимірювання динамічної ємності (AC Mode):** генератор тестового сигналу подає синусоїдальну напругу 1.0 В (RMS) на частоті 1 кГц (для ємностей `C > 10 нФ`) або 100 кГц (для `C ≤ 10 нФ`). Швидкісний синхронний демодулятор фіксує зміну ємності `ΔC` відносно початкового калібрувального значення `C₀`.
- **Контроль опору ізоляції та струму витоку (DC Leakage Mode):** на зразок постійно подається номінальна постійна напруга (наприклад, 16 В або 50 В) через струмообмежувальний захисний резистор 10 кОм. Струм витоку `I_leak` вимірюється трансімпедансним підсилювачем на прецизійному операційному підсилювачі з польовими транзисторами на вході (струм зміщення `< 1 пА`).

Вихід трансімпедансного підсилювача підключений до швидкодіючого апаратного компаратора, що генерує немасковане переривання (NMI) при виникненні імпульсного струму витоку понад 50 нА тривалістю більше 100 нс.

### 3. Привод пуансона з замкненим контуром за положенням
Лінійний актуатор на базі кульково-гвинтової пари (КГП) із кроком 2.0 мм приводиться в рух гібридним кроковим двигуном із мікрокроковим драйвером (1/32 кроку, 6400 імпульсів на міліметр ходу). Контролер формує імпульси частотою 6.4 кГц, що забезпечує стабільну лінійну швидкість опускання пуансона `v = 1.00 ± 0.02 мм/с`.

Для незалежного контролю прогину використовується оптична лінійка з роздільною здатністю 0.5 мкм, сигнал з якої надходить на квадратурний декодер мікроконтролера. Це виключає похибки, викликані пружною деформацією самої рами випробувального стенда під навантаженням.

## Детектування високочастотних мікророзрядів за допомогою DMA

Для надійної фіксації надкоротких мікротріщин у кераміці аналоговий сигнал витоку струму оцифровується допоміжним швидкісним 12-бітним SAR АЦП із частотою дискретизації 1 Мвиб/с у кільцевий буфер через прямий доступ до пам'яті (DMA).

Коли компаратор реєструє перевищення порогу струму 50 нА, потік DMA зупиняється з затримкою у 256 вибірок, фіксуючи осцилограму «передподії» (Pre-trigger buffer). Це дозволяє відрізнити справжній діелектричний пробій у тріщині від випадкової електромагнітної завади комутації двигуна.

## Цифрова фільтрація та калібрування шунтом

Тензометричний сигнал із низьким рівнем (мікровольти) вразливий до мережевих завад 50/60 Гц та електромагнітного шуму обмоток крокового двигуна. Вбудоване ПЗ застосовує рекурсивний цифровий фільтр низьких частот першого порядку (експоненційне рухоме середнє EMA):

```
y[n] = α · x[n] + (1 - α) · y[n-1]
```

де коефіцієнт згладжування `α = 0.15` обирається для забезпечення смуги пропускання 15 Гц, що повністю відсікає високочастотний джиттер кроків двигуна, не спотворюючи динаміку деформації при швидкості навантаження 1.0 мм/с.

Для перевірки коефіцієнта підсилення тракту перед кожною серією тестів вмикається аналоговий ключ шунтувального калібрування: паралельно до плеча моста 120 Ом підключається прецизійний резистор 100.0 кОм (допуск 0.01%), що створює еквівалентний калібрувальний розбаланс `ε_cal = 598.5 με`.

## Алгоритм кінцевого автомата випробувань (FSM)

Процедура тестування керується скінченним автоматом стану (FSM, англ. *Finite State Machine*), що включає шість послідовних фаз:

```
+-----------------------------------------------------------------------------------+
|                        ГРАФ СТАНІВ КВАЛІФІКАЦІЙНОГО ТЕСТУ                         |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [IDLE] ──(Старт)──► [CALIBRATE] ──(Тарування)──► [DESCEND] (v = 1 мм/с)          |
|                           ▲                             │                         |
|                           │                       (h >= h_target)                 |
|                     (Скидання)                          ▼                         |
|                           │                       [DWELL] (60 секунд)             |
|                           │                             │                         |
|  [FAILED] ◄──(Аварія)─────┴───────(Успіх)────────► [RETRACT] (Підйом пуансона)    |
|                                                         │                         |
|                                                         ▼                         |
|                                                    [PASSED]                       |
+-----------------------------------------------------------------------------------+
```

1. **CALIBRATE (Калібрування та тарування):** плата встановлюється на опори. Пуансон опускається до моменту торкання плати (детектується за зростанням сили на тензодатчику до 0.1 Н). Поточна координата скидається в `h = 0.000 мм`. Виконується шунтувальне калібрування та вимірюються початкові значення `C₀` та `I₀`.
2. **DESCEND (Навантаження вигином):** пуансон рухається вниз зі швидкістю 1.0 мм/с. Кожні 10 мс мікроконтролер опитує датчик деформації, фільтрує сигнал, вимірює ємність і струм витоку.
3. **DWELL (Витримка під навантаженням):** після досягнення цільового прогину (2.0 мм для стандартного тесту, 5.0 мм для Soft-Termination) пуансон зупиняється і утримує деформацію протягом 60 секунд. У цей час фіксується релаксація напружень у полімерному шарі.
4. **RETRACT (Розвантаження):** пуансон піднімається у вихідне положення зі швидкістю 5.0 мм/с.
5. **EVALUATION (Класифікація результату):** після зняття навантаження виконується фінальний вимір залишкової ємності та опору ізоляції. За відсутності відхилень генерується статус `PASSED`. У разі фіксації аномалії на будь-якому етапі формується статус `FAILED` із точним зазначенням типу відмови та деформації руйнування `ε_fail`.

## Програмна реалізація системи збору даних

Нижче наведено модуль вбудованого ПЗ моніторингу випробувального стенда. Реалізація мовою C призначена для мікроконтролерів без підтримки динамічної пам'яті (C99/C11 для ARM Cortex-M), а реалізація на C++ демонструє сучасний підхід з використанням концептів C++20, строгих типів фізичних величин та обробки помилок через `std::expected`.

:::tabs
```c
/* aec_q200_flex_monitor.h / .c — Драйвер випробування на вигин MLCC */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define FLEX_CRIT_CAP_DROP_PERCENT   5.0f     /* Граничний спад ємності за AEC-Q200: 5% */
#define FLEX_CRIT_LEAKAGE_NA         50.0f    /* Граничний струм витоку: 50 нА */
#define FLEX_DEFAULT_SPAN_MM         90.0f    /* Відстань між опорами стенда L */
#define FLEX_PCB_THICKNESS_MM        1.6f     /* Товщина тестової плати FR-4 t */
#define FLEX_DWELL_TIME_SEC          60.0f    /* Час витримки на максимумі навантаження */
#define FLEX_FILTER_ALPHA            0.15f    /* Коефіцієнт цифрового фільтра EMA */

typedef enum {
    FLEX_STATE_IDLE = 0,
    FLEX_STATE_CALIBRATING,
    FLEX_STATE_DESCENDING,
    FLEX_STATE_DWELLING,
    FLEX_STATE_RETRACTING,
    FLEX_STATE_PASSED,
    FLEX_STATE_FAILED_CAP_DROP,
    FLEX_STATE_FAILED_SHORT_CIRCUIT,
    FLEX_STATE_FAILED_OPEN_CIRCUIT,
    FLEX_STATE_EMERGENCY_STOP
} flex_state_t;

typedef struct {
    float initial_cap_pf;        /* Базова ємність C0 перед вигином */
    float target_deflection_mm;  /* Цільовий прогин (2.0 мм або 5.0 мм) */
    float speed_mm_per_sec;      /* Швидкість опускання (1.0 мм/с) */
    float gauge_factor;          /* Чутливість тензорезистора S_g */
    float span_length_mm;        /* Проліт L */
    float pcb_thickness_mm;      /* Товщина плати t */
} flex_config_t;

typedef struct {
    float current_deflection_mm; /* Поточний прогин пуансона h */
    float current_microstrain;   /* Поточна деформація плати (με) */
    float filtered_strain_ppm;   /* Згладжена деформація після ФНЧ */
    float current_cap_pf;        /* Виміряна поточна ємність */
    float current_leakage_na;    /* Виміряний струм витоку */
    float cap_change_percent;    /* Відхилення Delta C / C0 (%) */
    float dwell_timer_sec;       /* Таймер утримання навантаження */
    float failure_deflection_mm; /* Прогин, на якому сталася відмова */
    float failure_microstrain;   /* Деформація в момент відмови */
    flex_state_t state;          /* Поточний стан випробування */
} flex_telemetry_t;

/* Обчислення теоретичної деформації поверхні балки: eps = 6 * t * h / L^2 */
static inline float calculate_surface_strain_ppm(float h_mm, float t_mm, float l_mm) {
    if (l_mm <= 0.0f) return 0.0f;
    return (6.0f * t_mm * h_mm / (l_mm * l_mm)) * 1.0e6f;
}

/* Ініціалізація структури моніторингу */
void flex_monitor_init(flex_telemetry_t *t, const flex_config_t *cfg, float c0_pf, float leak0_na) {
    t->current_deflection_mm = 0.0f;
    t->current_microstrain = 0.0f;
    t->filtered_strain_ppm = 0.0f;
    t->current_cap_pf = c0_pf;
    t->current_leakage_na = leak0_na;
    t->cap_change_percent = 0.0f;
    t->dwell_timer_sec = 0.0f;
    t->failure_deflection_mm = 0.0f;
    t->failure_microstrain = 0.0f;
    t->state = FLEX_STATE_DESCENDING;
}

/* Періодичний крок опитування стенда (викликається кожні dt_sec, наприклад 0.01 с) */
flex_state_t flex_monitor_step(flex_telemetry_t *t,
                               const flex_config_t *cfg,
                               float measured_cap_pf,
                               float measured_leak_na,
                               float raw_adc_strain_ppm,
                               float dt_sec) {
    if (t->state != FLEX_STATE_DESCENDING && t->state != FLEX_STATE_DWELLING) {
        return t->state;
    }

    t->current_cap_pf = measured_cap_pf;
    t->current_leakage_na = measured_leak_na;

    /* Цифрова фільтрація сигналу тензомоста */
    t->filtered_strain_ppm = FLEX_FILTER_ALPHA * raw_adc_strain_ppm +
                             (1.0f - FLEX_FILTER_ALPHA) * t->filtered_strain_ppm;

    /* Оновлення переміщення під час фази опускання */
    if (t->state == FLEX_STATE_DESCENDING) {
        t->current_deflection_mm += cfg->speed_mm_per_sec * dt_sec;
        if (t->current_deflection_mm >= cfg->target_deflection_mm) {
            t->current_deflection_mm = cfg->target_deflection_mm;
            t->state = FLEX_STATE_DWELLING;
            t->dwell_timer_sec = 0.0f;
        }
    } else if (t->state == FLEX_STATE_DWELLING) {
        t->dwell_timer_sec += dt_sec;
        if (t->dwell_timer_sec >= FLEX_DWELL_TIME_SEC) {
            t->state = FLEX_STATE_PASSED;
            return t->state;
        }
    }

    /* Розрахунок деформації в мікрострейнах за геометрією балки */
    t->current_microstrain = calculate_surface_strain_ppm(
        t->current_deflection_mm, cfg->pcb_thickness_mm, cfg->span_length_mm
    );

    /* Розрахунок відносного відхилення ємності */
    if (cfg->initial_cap_pf > 0.0f) {
        t->cap_change_percent = fabsf(measured_cap_pf - cfg->initial_cap_pf) / cfg->initial_cap_pf * 100.0f;
    }

    /* 1. Контроль короткого замикання (пробій ізоляції / спалах витоку) */
    if (t->current_leakage_na >= FLEX_CRIT_LEAKAGE_NA) {
        t->state = FLEX_STATE_FAILED_SHORT_CIRCUIT;
        t->failure_deflection_mm = t->current_deflection_mm;
        t->failure_microstrain = t->current_microstrain;
        return t->state;
    }

    /* 2. Контроль деградації ємності */
    if (t->cap_change_percent >= FLEX_CRIT_CAP_DROP_PERCENT) {
        t->failure_deflection_mm = t->current_deflection_mm;
        t->failure_microstrain = t->current_microstrain;
        if (measured_cap_pf < (cfg->initial_cap_pf * 0.1f)) {
            t->state = FLEX_STATE_FAILED_OPEN_CIRCUIT;
        } else {
            t->state = FLEX_STATE_FAILED_CAP_DROP;
        }
        return t->state;
    }

    return t->state;
}
```
```cpp
/* aec_q200_flex_monitor.hpp — Ідіоматична C++20 імплементація */
#pragma once
#include <concepts>
#include <chrono>
#include <expected>
#include <cmath>
#include <string_view>

namespace aec_q200 {

enum class FailureMode {
    CapacitanceDegradation,
    LowOhmicShortCircuit,
    OpenCircuitFracture
};

enum class ExecutionPhase {
    Idle,
    Calibrating,
    Descending,
    Dwelling,
    Retracting,
    Completed
};

struct QualificationParameters {
    float initial_capacitance_pf{100'000.0f};  // 100 нФ
    float target_deflection_mm{5.0f};          // 5.0 мм за AEC-Q200 Soft-Term
    float actuator_speed_mm_s{1.0f};           // 1.0 мм/с
    float pcb_thickness_mm{1.6f};              // Плата 1.6 мм FR-4
    float support_span_mm{90.0f};              // Проліт 90 мм
    float dwell_duration_s{60.0f};             // Витримка 60 с
    float filter_alpha{0.15f};                 // Коефіцієнт ФНЧ
};

struct TelemetryFrame {
    float measured_capacitance_pf{0.0f};
    float leakage_current_na{0.0f};
    float raw_strain_ppm{0.0f};
};

struct FailureReport {
    float failure_deflection_mm{0.0f};
    float failure_microstrain{0.0f};
    float final_capacitance_pf{0.0f};
    float final_leakage_na{0.0f};
    FailureMode failure_type{};
};

class FlexQualificationStation {
public:
    static constexpr float kMaxAllowedCapDropPercent = 5.0f;
    static constexpr float kMaxAllowedLeakageCurrentNA = 50.0f;

    explicit constexpr FlexQualificationStation(const QualificationParameters& params) noexcept
        : params_(params) {}

    [[nodiscard]] constexpr float calculate_strain_ppm(float deflection_mm) const noexcept {
        if (params_.support_span_mm <= 0.0f) return 0.0f;
        const float numerator = 6.0f * params_.pcb_thickness_mm * deflection_mm;
        const float denominator = params_.support_span_mm * params_.support_span_mm;
        return (numerator / denominator) * 1.0e6f;
    }

    [[nodiscard]] std::expected<ExecutionPhase, FailureReport> process_step(
        const TelemetryFrame& telemetry,
        float delta_time_s
    ) noexcept {
        if (phase_ == ExecutionPhase::Completed || phase_ == ExecutionPhase::Idle) {
            return phase_;
        }

        // Цифрова фільтрація тензосигналу
        filtered_strain_ppm_ = params_.filter_alpha * telemetry.raw_strain_ppm +
                               (1.0f - params_.filter_alpha) * filtered_strain_ppm_;

        // Оновлення переміщення пуансона
        if (phase_ == ExecutionPhase::Descending) {
            current_deflection_mm_ += params_.actuator_speed_mm_s * delta_time_s;
            if (current_deflection_mm_ >= params_.target_deflection_mm) {
                current_deflection_mm_ = params_.target_deflection_mm;
                phase_ = ExecutionPhase::Dwelling;
                dwell_elapsed_s_ = 0.0f;
            }
        } else if (phase_ == ExecutionPhase::Dwelling) {
            dwell_elapsed_s_ += delta_time_s;
            if (dwell_elapsed_s_ >= params_.dwell_duration_s) {
                phase_ = ExecutionPhase::Completed;
                return phase_;
            }
        }

        current_microstrain_ = calculate_strain_ppm(current_deflection_mm_);

        const float cap_delta_pct = (params_.initial_capacitance_pf > 0.0f)
            ? (std::abs(telemetry.measured_capacitance_pf - params_.initial_capacitance_pf) /
               params_.initial_capacitance_pf * 100.0f)
            : 0.0f;

        // Перевірка 1: Сплеск струму витоку (КЗ через розтріскування)
        if (telemetry.leakage_current_na >= kMaxAllowedLeakageCurrentNA) {
            phase_ = ExecutionPhase::Completed;
            return std::unexpected(FailureReport{
                .failure_deflection_mm = current_deflection_mm_,
                .failure_microstrain = current_microstrain_,
                .final_capacitance_pf = telemetry.measured_capacitance_pf,
                .final_leakage_na = telemetry.leakage_current_na,
                .failure_type = FailureMode::LowOhmicShortCircuit
            });
        }

        // Перевірка 2: Відхилення ємності понад 5%
        if (cap_delta_pct >= kMaxAllowedCapDropPercent) {
            phase_ = ExecutionPhase::Completed;
            const auto mode = (telemetry.measured_capacitance_pf < params_.initial_capacitance_pf * 0.1f)
                ? FailureMode::OpenCircuitFracture
                : FailureMode::CapacitanceDegradation;

            return std::unexpected(FailureReport{
                .failure_deflection_mm = current_deflection_mm_,
                .failure_microstrain = current_microstrain_,
                .final_capacitance_pf = telemetry.measured_capacitance_pf,
                .final_leakage_na = telemetry.leakage_current_na,
                .failure_type = mode
            });
        }

        return phase_;
    }

    [[nodiscard]] constexpr float current_deflection() const noexcept { return current_deflection_mm_; }
    [[nodiscard]] constexpr float current_microstrain() const noexcept { return current_microstrain_; }
    [[nodiscard]] constexpr float filtered_strain() const noexcept { return filtered_strain_ppm_; }
    [[nodiscard]] constexpr ExecutionPhase current_phase() const noexcept { return phase_; }

private:
    QualificationParameters params_{};
    ExecutionPhase phase_{ExecutionPhase::Descending};
    float current_deflection_mm_{0.0f};
    float current_microstrain_{0.0f};
    float filtered_strain_ppm_{0.0f};
    float dwell_elapsed_s_{0.0f};
};

} // namespace aec_q200
```
:::

## Статистична обробка та сертифікаційний протокол PPAP

Для схвалення серійного виробництва за процедурою PPAP Level 3 тестується вибірка з щонайменше 30 зразків конденсаторів з різних виробничих партій. За результатами випробувань обчислюється індекс придатності процесу `C_pk`:

```
C_pk = min( (USL - μ) / (3·σ), (μ - LSL) / (3·σ) )
```

де `LSL = 5.0 мм` — нижня межа специфікації за AEC-Q200 для Soft-Termination, `μ` — середнє значення прогину до відмови, `σ` — стандартне відхилення вибірки. Для кваліфікації за автомобільним стандартом значення `C_pk` повинно перевищувати **1.67** (рівень дефектності менше 1 дефекту на мільйон виробів, < 1 PPM).

## Аналіз експериментальних результатів випробувань

За результатами циклу навантаження на стенді формуються діаграми «Деформація — Струм витоку — Відхилення ємності», за якими визначається поведінка зразків різних виробничих серій:

1. **Стандартні комерційні MLCC (жорсткий вивід Cu/Ni/Sn, типорозмір 1206):**
   - При досягненні прогину `h = 1.8...2.3 мм` (`ε ≈ 2130...2720 με`) на кривій струму витоку реєструється різкий імпульсний сплеск до 200–500 мкА.
   - Ємність падає стрибком на 15–30%.
   - Стенд негайно зупиняє привод і фіксує відмову `FailureMode::LowOhmicShortCircuit`.
2. **Конденсатори Open-Mode (зміщена активна зона, типорозмір 1206):**
   - При прогині `h = 2.4...3.2 мм` спостерігається зародження кутової тріщини. Проте струм витоку залишається на фоновому рівні (`I_leak < 0.2 нА`).
   - Ємність зменшується на 2–4% внаслідок відсікання невеликої пасивної ділянки. Примусовий вигин понад 4.5 мм призводить до безпечного повного обриву `FailureMode::OpenCircuitFracture` без короткого замикання.
3. **Конденсатори Soft-Termination (FlexiCap / FT-CAP, типорозмір 1206):**
   - Зразок повністю проходить фазу навантаження до `h = 5.00 мм` (`ε ≈ 5930 με`) і 60-секундну витримку `DWELL`.
   - Протягом усього тесту струм витоку не перевищує 0.15 нА, а максимальне коливання ємності складає `|ΔC / C₀| < 0.4%`.
   - Після розвантаження плати рентгенографічний аналіз (X-ray inspection) та мікрошліфи підтверджують повну відсутність мікротріщин у керамічному тілі. Стенд видає протокол успішної кваліфікації `ExecutionPhase::Completed`.
