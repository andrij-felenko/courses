# ⚙️ Алгоритм динамічної компенсації самонагріву плати для термодавача на C та C++

У компактних вбудованих пристроях — бездротових сенсорних вузлах, трекерах, натільній електроніці та герметичних промислових датчиках стандарту IP67 — часто неможливо фізично віддалити термодавач від мікроконтролера, радіотрансивера чи стабілізатора на безпечну відстань. Навіть при застосуванні фрезерованих прорізів у текстоліті теплове випромінювання та передача тепла крізь залишки плати й замкнений об'єм корпусу піднімають температуру термодавача на кілька градусів вище за реальну температуру навколишнього середовища.

Цей проєкт демонструє створення вбудованого модуля динамічної компенсації самонагріву: відстеження робочих станів апаратної частини, безперервне оцінювання тепловиділення, розрахунок відгуку багатоланкової теплової моделі та відновлення істинної температури середовища в режимі реального часу.

## Принцип роботи спостерігача теплового стану

Алгоритм динамічної компенсації побудовано за архітектурою спостерігача стану (англ. *state observer*). Замість намагання встановити додаткові фізичні датчики температури на кожен гарячий чип, мікроконтролер використовує математичну модель власної друкованої плати.

Вхідними даними для моделі слугують внутрішні програмні події та вимірювання струму:
1. **Поточна тактова частота та режим завантаження ядра CPU:** У режимі активних обчислень на максимальній частоті 240 МГц процесор виділяє значно більше тепла, ніж у стані очікування переривань (WFI) або легкому сні (Light-sleep).
2. **Коефіцієнт активності радіопередавача (TX Duty Cycle):** Радіотрансивер Wi-Fi, Bluetooth або стільникового зв'язку споживає найбільший струм імпульсно. Прошивка відстежує частку часу, протягом якої вихідний підсилювач потужності (PA) був увімкнений протягом ковзного вікна усереднення.
3. **Падіння напруги на лінійному стабілізаторі:** За наявності вбудованого вимірювача струму акумулятора або фіксованого профілю живлення споживана потужність перераховується у вати тепловиділення.

Отримана миттєва потужність `P_heat(t)` подається на вхід дволанкового цифрового фільтра низьких частот із нескінченною імпульсною характеристикою (IIR), який моделює теплову інерцію системи:

```
[Стани периферії: CPU f, Wi-Fi TX, LDO I_load]
                   ↓
        [Оцінювач потужності P_heat]
                   ↓ P(t)
    [Цифровий 2-полюсний IIR фільтр (τ1, τ2)]
                   ↓
          [Змодельована похибка ΔT_self]
                   ↓
   [T_raw] ────► [ ( − ) ] ────► [T_ambient_est]
```

Перша ланка моделі з постійною часу `τ_1 ≈ 5–15 с` відповідає за швидкий нагрів кремнієвого кристала та пластикового корпусу інтегральної мікросхеми. Друга ланка з постійною часу `τ_2 ≈ 60–300 с` моделює повільний тепловий розгін усього масиву склотекстоліту друкованої плати, мідних шарів та внутрішнього повітря герметичного корпусу.

Сумарний змодельований перегрів `ΔT_self = ΔT_1 + ΔT_2` віднімається від необроблених показань термодавача `T_raw`, повертаючи виправлену температуру довкілля `T_ambient_est`.

## Програмна реалізація на C та C++

Нижче наведено модульну бібліотеку компенсатора для вбудованих систем. Реалізація мовою C орієнтована на чистий C99 без динамічного виділення пам'яті (статична алокація), що дозволяє використовувати її в bare-metal прошивках та операційних системах реального часу FreeRTOS/Zephyr. Вкладка C++ містить строго типізований клас у стилі C++17/20 із використанням просторів імен, `std::chrono` для безпечного обліку часових інтервалів та інкапсуляцією внутрішніх станів.

:::tabs
```c
/* thermal_compensator.h - C99 референтна реалізація */
#ifndef THERMAL_COMPENSATOR_H
#define THERMAL_COMPENSATOR_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Параметри теплової моделі плати (визначаються під час калібрування)
 */
typedef struct {
    float r_th1;        /* Тепловий опір 1-ї ланки (корпус чіпа), К/Вт */
    float tau1;         /* Постійна часу 1-ї ланки, секунди */
    float r_th2;        /* Тепловий опір 2-ї ланки (масив плати), К/Вт */
    float tau2;         /* Постійна часу 2-ї ланки, секунди */
    float p_quiescent;  /* Базове статичне споживання плати у спокої, Вт */
    float p_wifi_tx;    /* Теплова потужність радіопередавача під час TX, Вт */
    float p_cpu_active; /* Додаткове тепловиділення CPU при 100% завантаженні, Вт */
} thermal_config_t;

/**
 * @brief Стан та контекст теплового фільтра
 */
typedef struct {
    thermal_config_t cfg;
    float dt;           /* Період дискретизації оновлення фільтра, секунди */
    float alpha1;       /* Коефіцієнт експоненційного згладжування 1-ї ланки */
    float alpha2;       /* Коефіцієнт експоненційного згладжування 2-ї ланки */
    float state_t1;     /* Поточний перегрів 1-ї ланки, °C */
    float state_t2;     /* Поточний перегрів 2-ї ланки, °C */
    bool initialized;   /* Прапорець успішної ініціалізації */
} thermal_filter_t;

/**
 * @brief Ініціалізація компенсатора та розрахунок коефіцієнтів
 * @param filter Вказівник на екземпляр структури фільтра
 * @param cfg Вказівник на конфігурацію калібрувальних параметрів
 * @param dt_seconds Період опитування в секундах (наприклад, 1.0f для 1 Гц)
 */
void thermal_filter_init(thermal_filter_t *filter, const thermal_config_t *cfg, float dt_seconds);

/**
 * @brief Скидання накопиченого тепла (застосовується при холодному старті)
 */
void thermal_filter_reset(thermal_filter_t *filter);

/**
 * @brief Встановлення початкового теплового стану (наприклад, після теплого перезавантаження)
 * @param filter Вказівник на фільтр
 * @param initial_self_heat Початкова оцінка перегріву плати, °C
 */
void thermal_filter_set_state(thermal_filter_t *filter, float initial_self_heat);

/**
 * @brief Основна функція оновлення фільтра та розрахунку компенсації
 * @param filter Вказівник на екземпляр фільтра
 * @param t_raw_celsius Необроблене вимірювання термодавача, °C
 * @param cpu_load Відносне завантаження процесора (0.0f - 1.0f)
 * @param tx_duty_cycle Частка активності радіопередавача (0.0f - 1.0f)
 * @return Відновлена температура навколишнього середовища, °C
 */
float thermal_filter_update(thermal_filter_t *filter, float t_raw_celsius,
                            float cpu_load, float tx_duty_cycle);

/**
 * @brief Отримання поточної змодельованої поправки перегріву
 */
float thermal_filter_get_delta(const thermal_filter_t *filter);

#ifdef __cplusplus
}
#endif

#endif /* THERMAL_COMPENSATOR_H */

/* thermal_compensator.c */
#include "thermal_compensator.h"
#include <math.h>

void thermal_filter_init(thermal_filter_t *filter, const thermal_config_t *cfg, float dt_seconds) {
    if (!filter || !cfg || dt_seconds <= 0.0f) {
        return;
    }
    filter->cfg = *cfg;
    filter->dt = dt_seconds;

    /* Розрахунок дискретних коефіцієнтів фільтра першого порядку:
     * alpha = exp(-dt / tau). При малих dt/tau це еквівалентно 1 - dt/tau */
    filter->alpha1 = (cfg->tau1 > 0.0f) ? expf(-dt_seconds / cfg->tau1) : 0.0f;
    filter->alpha2 = (cfg->tau2 > 0.0f) ? expf(-dt_seconds / cfg->tau2) : 0.0f;

    filter->state_t1 = 0.0f;
    filter->state_t2 = 0.0f;
    filter->initialized = true;
}

void thermal_filter_reset(thermal_filter_t *filter) {
    if (!filter) return;
    filter->state_t1 = 0.0f;
    filter->state_t2 = 0.0f;
}

void thermal_filter_set_state(thermal_filter_t *filter, float initial_self_heat) {
    if (!filter) return;
    /* Розподіляємо початковий перегрів пропорційно тепловим опорам ланок */
    float r_total = filter->cfg.r_th1 + filter->cfg.r_th2;
    if (r_total > 0.0f) {
        filter->state_t1 = initial_self_heat * (filter->cfg.r_th1 / r_total);
        filter->state_t2 = initial_self_heat * (filter->cfg.r_th2 / r_total);
    } else {
        filter->state_t1 = 0.0f;
        filter->state_t2 = initial_self_heat;
    }
}

float thermal_filter_update(thermal_filter_t *filter, float t_raw_celsius,
                            float cpu_load, float tx_duty_cycle) {
    if (!filter || !filter->initialized) {
        return t_raw_celsius;
    }

    /* Захисне насичення вхідних коефіцієнтів у діапазоні від 0.0 до 1.0 */
    if (cpu_load < 0.0f) cpu_load = 0.0f;
    if (cpu_load > 1.0f) cpu_load = 1.0f;
    if (tx_duty_cycle < 0.0f) tx_duty_cycle = 0.0f;
    if (tx_duty_cycle > 1.0f) tx_duty_cycle = 1.0f;

    /* 1. Розрахунок поточної теплової потужності активних вузлів */
    float p_total = filter->cfg.p_quiescent +
                    (filter->cfg.p_cpu_active * cpu_load) +
                    (filter->cfg.p_wifi_tx * tx_duty_cycle);

    /* 2. Чисельне інтегрування 1-ї ланки (кристал та корпус чіпа) */
    float target_t1 = filter->cfg.r_th1 * p_total;
    filter->state_t1 = (filter->alpha1 * filter->state_t1) +
                       ((1.0f - filter->alpha1) * target_t1);

    /* 3. Чисельне інтегрування 2-ї ланки (масив друкованої плати) */
    float target_t2 = filter->cfg.r_th2 * p_total;
    filter->state_t2 = (filter->alpha2 * filter->state_t2) +
                       ((1.0f - filter->alpha2) * target_t2);

    /* 4. Сумарна паразитна температурна добавка */
    float delta_t_self = filter->state_t1 + filter->state_t2;

    /* 5. Відновлення істинної температури середовища */
    return t_raw_celsius - delta_t_self;
}

float thermal_filter_get_delta(const thermal_filter_t *filter) {
    if (!filter) return 0.0f;
    return filter->state_t1 + filter->state_t2;
}
```
```cpp
// ThermalCompensator.hpp - Ідіоматична C++17/20 реалізація
#pragma once

#include <algorithm>
#include <chrono>
#include <cmath>

namespace embedded::thermal {

/**
 * @brief Калібрувальні константи теплової моделі друкованої плати
 */
struct ThermalConfig {
    float r_th1{12.0f};         // Тепловий опір 1-ї ланки (корпус), К/Вт
    float tau1{8.0f};           // Постійна часу 1-ї ланки, секунди
    float r_th2{45.0f};         // Тепловий опір 2-ї ланки (текстоліт плати), К/Вт
    float tau2{120.0f};         // Постійна часу 2-ї ланки, секунди
    float p_quiescent{0.080f};  // Базова теплова потужність у спокої, Вт
    float p_wifi_tx{0.650f};    // Теплова потужність радіопередавача під час TX, Вт
    float p_cpu_active{0.200f}; // Тепловиділення CPU при повному завантаженні, Вт
};

/**
 * @brief Клас динамічного спостерігача теплового стану
 */
class ThermalCompensator {
public:
    explicit ThermalCompensator(const ThermalConfig& config, std::chrono::milliseconds sample_period)
        : config_(config), dt_(std::chrono::duration<float>(sample_period).count()) {
        recalculate_coefficients();
    }

    void reset() noexcept {
        state_t1_ = 0.0f;
        state_t2_ = 0.0f;
    }

    void set_state(float initial_self_heat) noexcept {
        const float r_total = config_.r_th1 + config_.r_th2;
        if (r_total > 0.0f) {
            state_t1_ = initial_self_heat * (config_.r_th1 / r_total);
            state_t2_ = initial_self_heat * (config_.r_th2 / r_total);
        } else {
            state_t1_ = 0.0f;
            state_t2_ = initial_self_heat;
        }
    }

    void set_sample_period(std::chrono::milliseconds period) noexcept {
        dt_ = std::chrono::duration<float>(period).count();
        recalculate_coefficients();
    }

    [[nodiscard]] float update(float raw_temperature_celsius,
                               float cpu_load,
                               float tx_duty_cycle) noexcept {
        const float clamped_cpu = std::clamp(cpu_load, 0.0f, 1.0f);
        const float clamped_tx = std::clamp(tx_duty_cycle, 0.0f, 1.0f);

        // 1. Оцінка сумарної теплової потужності компонентів
        const float p_total = config_.p_quiescent +
                              (config_.p_cpu_active * clamped_cpu) +
                              (config_.p_wifi_tx * clamped_tx);

        // 2. Чисельне оновлення швидкої ланки кристала
        const float target_t1 = config_.r_th1 * p_total;
        state_t1_ = (alpha1_ * state_t1_) + ((1.0f - alpha1_) * target_t1);

        // 3. Чисельне оновлення повільної ланки масиву плати
        const float target_t2 = config_.r_th2 * p_total;
        state_t2_ = (alpha2_ * state_t2_) + ((1.0f - alpha2_) * target_t2);

        // 4. Віднімання динамічної поправки від показань сенсора
        const float self_heat_delta = state_t1_ + state_t2_;
        return raw_temperature_celsius - self_heat_delta;
    }

    [[nodiscard]] float estimated_self_heating() const noexcept {
        return state_t1_ + state_t2_;
    }

private:
    void recalculate_coefficients() noexcept {
        alpha1_ = (config_.tau1 > 0.0f) ? std::exp(-dt_ / config_.tau1) : 0.0f;
        alpha2_ = (config_.tau2 > 0.0f) ? std::exp(-dt_ / config_.tau2) : 0.0f;
    }

    ThermalConfig config_;
    float dt_{1.0f};
    float alpha1_{0.0f};
    float alpha2_{0.0f};
    float state_t1_{0.0f};
    float state_t2_{0.0f};
};

} // namespace embedded::thermal
```
:::

## Методика експериментальної ідентифікації параметрів

Для того щоб компенсатор працював із високою точністю, коефіцієнти `r_th1`, `tau1`, `r_th2` та `tau2` необхідно виміряти на реальному серійному зразку пристрою у зібраному корпусі:

1. **Термостатування та витримка початкового стану:** Зібраний виріб із вимкненим живленням розміщують у кліматичній камері або теплоізольованому боксі з нерухомим повітрям при стабільній еталонній температурі (наприклад, +25.0 °C) щонайменше на 45 хвилин для досягнення повної теплової рівноваги.
2. **Ступінчасте навантаження (Step Response):** Запускається спеціальна тестова прошивка, яка подає живлення та вмикає постійну безперервну передачу радіотрансивера або фіксоване 100% завантаження обчислювальних ядер процесора з точно відомою потужністю тепловиділення `P_step` (наприклад, 0.85 Вт).
3. **Логування перехідного процесу:** Протягом 20 хвилин кожну секунду (`Δt = 1 с`) зчитуються та записуються в пам'ять показання цифрового термодавача.
4. **Апроксимація кривої нагріву:** Отримана крива розігріву `T_raw(t)` описується двоекспоненційним аналітичним рівнянням:
   ```
   T_raw(t) = T_0 + P_step · (r_th1 · (1 − exp(−t / tau1)) + r_th2 · (1 − exp(−t / tau2)))
   ```
   За допомогою алгоритму нелінійної оптимізації методом найменших квадратів (наприклад, Levenberg-Marquardt у Python або MATLAB) обчислюються точні значення чотирьох параметрів. Отримані коефіцієнти зашиваються у flash-пам'ять або файл конфігурації прошивки.

## Інженерні пастки та крайові випадки

- **Примусова конвекція та обдув:** Якщо виріб потрапляє під потік холодного повітря від зовнішнього кулера або вітру, коефіцієнт тепловіддачі в довкілля різко зростає, а реальний опір `r_th2` падає у 2–4 рази. Модель із фіксованим `r_th2` починає перекомпенсовувати похибку, через що відновлена температура виявиться заниженою. У пристроях із вентиляторами коефіцієнт `r_th2` роблять динамічною функцією від швидкості обертання крильчатки або показань тахометра.
- **Гарячий рестарт (Hot Reboot):** Якщо пристрій несподівано перезавантажився через спрацювання сторожового таймера (Watchdog) або оновлення прошивки «по повітрю» (OTA), внутрішній стан фільтра `state_t1` та `state_t2` у RAM скинеться в нуль. Оскільки плата фізично лишається гарячою, перші 5–10 хвилин після старту показання будуть суттєво завищеними. Для усунення цієї проблеми поточний стан фільтра кожні кілька секунд зберігають в енергонезалежну пам'ять повільних регістрів RTC (RTC Backup SRAM) або вираховують початковий перегрів за різницею між внутрішнім датчиком кристала MCU та виносним термодавачем.
- **Заборона зворотного диференціювання:** Ніколи не намагайтеся оцінити потужність через чисельне диференціювання виміряної температури `P ≈ C · (dT / dt)`. Шум квантування та тепловий джиттер АЦП при взятті похідної створюють гігантські випадкові сплески похибки, які повністю дестабілізують систему керування.
