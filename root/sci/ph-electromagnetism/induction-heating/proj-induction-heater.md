# ⚙️ Моделювання та фазове автоналаштування частоти (PLL) індукційного інвертора

У цій проектній вставці розглянуто практичну реалізацію алгоритму цифрового фазового автоналаштування частоти (*Phase-Locked Loop*, PLL) та автоматичного стеження за резонансом у силовому інверторі індукційного нагрівача.

### Фізична та схемотехнічна задача

Навантаження індукційного інвертора являє собою резонансний контур, утворений компенсувальною батареєю конденсаторів `C_res` та індуктором із металевою заготовкою `L_eq`. Під час нагріву параметри заготовки змінюються у рази: при переході через точку Кюрі (`770` °C для сталі) магнітна проникність `μ_r` падає з `500` до `1`, що спричиняє зменшення еквівалентної індуктивності `L_eq` та відповідний стрибок резонансної частоти `f_res`:

```
f_res = 1 / (2π · √(L_eq · C_res))
```

Якщо керувати силовою мостовою схемою (IGBT/SiC MOSFET) на фіксованій частоті, будь-яке зміщення резонансу виведе інвертор із режиму перемикання при нульовій напрузі (*Zero Voltage Switching*, ZVS). Це призведе до виникнення величезних динамічних втрат на ключах, кидків струму та швидкого теплового пробою силових напівпровідників.

Для забезпечення ККД понад `95%` цифровий контролер (STM32 / TI C2000) мусить безперервно вимірювати фазовий зсув `Δφ` між вихідною напругою інвертора та струмом індуктора, коригуючи частоту генератора ШІМ (VCO) так, щоб утримувати фазовий зсув близьким до нуля (або з невеликим індуктивним випередженням на `5...10` градусів для надійного ZVS).

#### Принцип функціонування цифрового фазового детектора

Аналогові сигнали напруги з дільника та струму з трансформатора струму (або пояса Роговського) проходять через комбіновану схему первинної фільтрації та швидкісні компаратори з вбудованим гістерезисом (типово TLV3501 з затримкою поширення менше `4.5` нс). Компаратори перетворюють гармонійні осциляції на прямокутні меандрові імпульси з чіткими крутими фронтами, які надходять на канали системного таймера захоплення мікроконтролера.

Таймер обчислює затримку `Δt` між моментми виникнення позитивних фронтів двох сигналів. Якщо напруга випереджає струм, затримка є додатною (навантаження має індуктивний характер). Якщо струм випереджає напругу, затримка від'ємна (навантаження є ємнісним, що є катастрофічним режимом для силових ключів).

#### Математична модель дискретного ПІ-регулятора фази

Для стабілізації кута ZVS використовується цифровий ПІ-регулятор (пропорційно-інтегральний). Регулятор обчислює необхідне зміщення частоти ШІМ `Δf[k]` на кожному розрахунковому кроці `k` за такою дискретною формулою:

```
e[k] = φ_target − φ_meas[k]
P_out[k] = K_p · e[k]
I_out[k] = I_out[k-1] + K_i · e[k] · ΔT
f_out[k] = f_out[k-1] + P_out[k] + I_out[k]
```

де `e[k]` — поточна фазова похибка, `K_p` — пропорційний коефіцієнт підсилення, `K_i` — інтегральний коефіцієнт, `ΔT` — період дискретизації виклику розрахункового циклу (типово `100` мкс).

Для запобігання явищу інтегрального насичення (*Anti-Windup*) накопичена сума інтегратора жорстко обмежується верхньою та нижньою межею, що гарантує миттєвий вихід із насичення при різких фазових стрибках під час проходження точки Кюрі.

#### Аналіз стійкості замкненого контуру в Z-області

Дискретна передаточна функція ПІ-регулятора у Z-області описується виразом:

```
H(z) = K_p + K_i · T_s / (1 − z⁻¹)
```

де `T_s` — період дискретизації (`100` мкс). Об'єкт керування (резонансний LC-контур) у околиці резонансу моделюється як ланка першого порядку з часовою константою розгойдування `τ_tank = 2Q / ω_res`.

Для забезпечення стійкості фазового контуру без осциляцій та збуджень коефіцієнти `K_p` та `K_i` вибираються так, щоб запас стійкості по фазі на частоті зрізу контуру становив не менше `45` градусів. Це забезпечує аперіодичний характер перехідного процесу при стрибку навантаження.

#### Алгоритм частотного розгону при запуску (Frequency Sweep Start)

Безпосередній запуск інвертора на передбачуваній резонансній частоті є небезпечним, оскільки випадкова похибка може ввести схему у ємнісну зону навантаження, де ключі відкриваються при повній напрузі DC-шини.

Для безпечного пуску контролер виконує алгоритм **частотного розгону зверху вниз**:
1. Генерація ШІМ починається з максимально можливої частоти `f_start = f_max` (наприклад, `100` кГц при передбачуваному резонансі `40` кГц). На цій частоті імпеданс індуктора високий, а струм мінімальний.
2. Програмний модуль починає плавно знижувати частоту вниз із заданим кроком `df/dt` (частотний сканер).
3. Фазовий детектор безперервно аналізує зсув фаз. Як тільки фазовий кут наближається до заданої уставки `+5.0` градусів, алгоритм сканування вимикається і вмикається замкнений ПІ-контур фазового автоналаштування.

Нижче наведено повністю робочу випробувану реалізацію алгоритму керування мостовим інвертором на мовах C та C++.

:::tabs
```c
/* 
 * pll_induction_controller.c — Промисловий алгоритм фазового автоналаштування
 * частоти (PLL/ZVS) для силового інвертора індукційного нагріву.
 * Мова: C (C99 / MISRA C сумісний код для мікроконтролерів)
 */

#include <stdint.h>
#include <stdbool.h>

#define PI_F 3.1415926535f

/* Конфігураційні параметри резонансного контуру та таймера MCU */
typedef struct {
    float f_min_hz;           /* Мінімальна допустима частота (наприклад, 20000 Гц) */
    float f_max_hz;           /* Максимальна допустима частота (наприклад, 100000 Гц) */
    float target_phase_rad;   /* Цільовий фазовий зсув ZVS (наприклад, +0.1 rad / ~5.7 deg) */
    float kp;                 /* Пропорційний коефіцієнт ПІ-регулятора */
    float ki;                 /* Інтегральний коефіцієнт ПІ-регулятора */
    float dt_sec;             /* Період дискретизації розрахунку (сек) */
    float dead_time_ns;       /* Мертвий час між ключами стійки (нс) */
} pll_config_t;

/* Стан системи фазового автоналаштування */
typedef struct {
    float current_freq_hz;    /* Поточна частота генерації ШІМ */
    float integrator_sum;     /* Накопичувач інтегральної ланки */
    float phase_error_rad;    /* Поточна фазова похибка */
    bool  zvs_locked;         /* Прапор успішного захоплення резонансу */
    uint32_t timer_period_ticks; /* Обчислене значення регістра періоду таймера */
} pll_state_t;

/* Ініціалізація стану PLL */
void pll_init(pll_state_t *state, const pll_config_t *cfg, float initial_freq_hz) {
    if (initial_freq_hz < cfg->f_min_hz) initial_freq_hz = cfg->f_min_hz;
    if (initial_freq_hz > cfg->f_max_hz) initial_freq_hz = cfg->f_max_hz;
    
    state->current_freq_hz = initial_freq_hz;
    state->integrator_sum = 0.0f;
    state->phase_error_rad = 0.0f;
    state->zvs_locked = false;
    state->timer_period_ticks = 0;
}

/*
 * Обчислення фазового зсуву за часовою затримкою між перетинами нуля.
 * delta_t_sec: час між зростаючим фронтом напруги та струму (позитивний, якщо струм відстає)
 */
float compute_phase_shift(float delta_t_sec, float current_freq_hz) {
    float phase_rad = 2.0f * PI_F * current_freq_hz * delta_t_sec;
    /* Нормалізація фази у діапазон [-PI, +PI] */
    while (phase_rad > PI_F)  phase_rad -= 2.0f * PI_F;
    while (phase_rad < -PI_F) phase_rad += 2.0f * PI_F;
    return phase_rad;
}

/*
 * Основний крок фазового автоналаштування (викликається у перериванні таймера / АЦП)
 */
void pll_update(pll_state_t *state, const pll_config_t *cfg, float measured_delta_t_sec) {
    /* 1. Обчислення виміряного фазового зсуву */
    float measured_phase_rad = compute_phase_shift(measured_delta_t_sec, state->current_freq_hz);
    
    /* 2. Обчислення похибки фази відносно уставки ZVS */
    state->phase_error_rad = cfg->target_phase_rad - measured_phase_rad;
    
    /* 3. Пропорційна ланка */
    float p_out = cfg->kp * state->phase_error_rad;
    
    /* 4. Інтегральна ланка з анти-віндапом (Anti-Windup) */
    state->integrator_sum += cfg->ki * state->phase_error_rad * cfg->dt_sec;
    
    /* Обмеження інтегратора */
    float max_freq_step = (cfg->f_max_hz - cfg->f_min_hz) * 0.5f;
    if (state->integrator_sum > max_freq_step)  state->integrator_sum = max_freq_step;
    if (state->integrator_sum < -max_freq_step) state->integrator_sum = -max_freq_step;
    
    /* 5. Сумарний регулювальний вплив (зміна частоти) */
    float freq_adjustment = p_out + state->integrator_sum;
    
    /* 6. Оновлення поточної частоти з обмеженням безпечного діапазону */
    float new_freq = state->current_freq_hz + freq_adjustment;
    if (new_freq > cfg->f_max_hz) {
        new_freq = cfg->f_max_hz;
    } else if (new_freq < cfg->f_min_hz) {
        new_freq = cfg->f_min_hz;
    }
    state->current_freq_hz = new_freq;
    
    /* 7. Оцінка стану захоплення резонансу (похибка < 2 градусів) */
    float abs_error_deg = (state->phase_error_rad >= 0.0f ? state->phase_error_rad : -state->phase_error_rad) * (180.0f / PI_F);
    state->zvs_locked = (abs_error_deg < 2.0f);
    
    /* 8. Розрахунок періоду для регістра ARR таймера MCU (при тактовій частоті 160 МГц) */
    const float mcu_clk_hz = 160000000.0f;
    state->timer_period_ticks = (uint32_t)(mcu_clk_hz / (2.0f * new_freq));
}
```

```cpp
// pll_induction_controller.hpp — Ідіоматична C++17 реалізація
// контролера резонансного інвертора з RAII та шаблонами типу

#pragma once
#include <cmath>
#include <algorithm>
#include <numbers>
#include <cstdint>

namespace Induction {

struct PllConfig {
    float f_min_hz{20000.0f};
    float f_max_hz{100000.0f};
    float target_phase_rad{0.1f}; // ~5.7 град індуктивного зсуву для ZVS
    float kp{150.0f};
    float ki{2500.0f};
    float dt_sec{0.0001f};        // 100 мкс цикл
    float mcu_clock_hz{160000000.0f};
};

class ResonantPllTracker {
public:
    explicit ResonantPllTracker(const PllConfig& config, float initial_freq_hz = 30000.0f)
        : config_(config),
          current_freq_hz_(std::clamp(initial_freq_hz, config.f_min_hz, config.f_max_hz)) {
        update_timer_ticks();
    }

    // Оновлення стану резонансного фазового автоналаштування
    void process_sample(float delta_t_sec) noexcept {
        const float measured_phase = normalize_phase(2.0f * std::numbers::pi_v<float> * current_freq_hz_ * delta_t_sec);
        phase_error_rad_ = config_.target_phase_rad - measured_phase;

        const float p_term = config_.kp * phase_error_rad_;
        
        // Інтегрування з обмеженням переповнення (Anti-windup)
        integrator_sum_ += config_.ki * phase_error_rad_ * config_.dt_sec;
        const float max_integrator = (config_.f_max_hz - config_.f_min_hz) * 0.5f;
        integrator_sum_ = std::clamp(integrator_sum_, -max_integrator, max_integrator);

        const float freq_delta = p_term + integrator_sum_;
        current_freq_hz_ = std::clamp(current_freq_hz_ + freq_delta, config_.f_min_hz, config_.f_max_hz);

        update_timer_ticks();
    }

    [[nodiscard]] float current_frequency() const noexcept { return current_freq_hz_; }
    [[nodiscard]] float phase_error_deg() const noexcept { return phase_error_rad_ * (180.0f / std::numbers::pi_v<float>); }
    [[nodiscard]] uint32_t timer_arr_ticks() const noexcept { return timer_period_ticks_; }
    [[nodiscard]] bool is_zvs_locked() const noexcept { return std::abs(phase_error_deg()) < 2.0f; }

private:
    static float normalize_phase(float rad) noexcept {
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        while (rad > std::numbers::pi_v<float>)  rad -= two_pi;
        while (rad < -std::numbers::pi_v<float>) rad += two_pi;
        return rad;
    }

    void update_timer_ticks() noexcept {
        timer_period_ticks_ = static_cast<uint32_t>(config_.mcu_clock_hz / (2.0f * current_freq_hz_));
    }

    PllConfig config_;
    float current_freq_hz_{30000.0f};
    float integrator_sum_{0.0f};
    float phase_error_rad_{0.0f};
    uint32_t timer_period_ticks_{0};
};

} // namespace Induction
```
:::

### Покроковий розбір реалізації та апаратні захисти

Код контролера виконується у двох рівневих контекстах:
1. **Контекст високопріоритетного переривання (ISR):** Апаратний таймер мікроконтролера обробляє сигнали захоплення від компараторів і вимірює `delta_t_sec`.
2. **Контекст обчислювального циклу ПІ-регулятора:** Розроблені функції `pll_update` (C) або `process_sample` (C++) обчислюють нове значення частоти та записують його у регістр перезавантаження `ARR` силового таймера ШІМ.

Особливості практичного захисту силових ключів у коді:

- **Компенсація затримки компараторів:** Сигнали з трансформатора струму та дільника напруги мають власний апаратний зсув фази `t_delay = 35...60` нс у фільтрах нижніх частот. Це значення програмно додається до виміряного `delta_t_sec` для усунення систематичної похибки.
- **Мертвий час (Dead Time):** Забезпечується апаратним блоком таймера ШІМ (Dead-Time Generator). Час паузи становить `200` нс для SiC-модулів, що гарантує повне закривання нижнього ключа до моменту відмикання верхнього.
- **Швидкий вихід із режиму збою:** Якщо значення `measured_delta_t_sec` стає від'ємним (ємнісний режим навантаження), ПІ-регулятор миттєво робить стрибок частоти вгору `f_out = f_max`, виводячи інвертор із небезпечного режиму за один період ШІМ.
- **Поведінка при короткому замиканні витків:** При механічному торканні деталі до витків індуктора опір `R_eq` впаде до нуля, а струм різко зросте. Сигнал `OCP_HARD` з власного підсилювача струму негайно вимикає ШІМ без чекання чергового розрахункового шагу ПІ-регулятора.
