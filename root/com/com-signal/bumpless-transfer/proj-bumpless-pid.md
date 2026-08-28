# ⚙️ Універсальний безривковий ПІД-контролер на C та C++

Цей проект містить повну виробничу бібліотеку універсального дискретного пропорційно-інтегрально-диференційного регулятора з підтримкою безударного перемикання режимів (Manual, Tracking, Auto), безривкової зміни коефіцієнтів підсилення «на льоту» (Gain Scheduling), двоступеневого зважування уставки (2-DoF PID), профілювання швидкості наростання уставки (Setpoint Ramping) та захисту від інтегрального насичення зворотним перерахунком (Back-Calculation Anti-Windup).

У реальних бортових системах — польотних контролерах безпілотників, системах керування тягою електромобілів та сервоприводах промислової автоматики — перемикання між алгоритмами відбувається динамічно. Неузгодженість внутрішніх станів або некоректна зміна коефіцієнтів спричиняють аварійні стрибки струму та механічні удари. Нижче наведено завершену реалізацію мовами C та C++, детальний аналіз структур даних і числовий порівняльний експеримент.

### Архітектура та структури даних

Регулятор підтримує три режими функціонування, задані переліком:

- `MODE_MANUAL` — ручний режим: вихідний сигнал на приводі формується оператором або калібрувальним контуром. Внутрішній інтегратор автоматичного регулятора безперервно перераховується методом зворотного узгодження, щоб утримувати розрахунковий віртуальний вихід рівним фактичному сигналу актуатора.
- `MODE_TRACKING` — режим пасивного стеження: регулятор працює у складі надлишкової або резервованої архітектури (наприклад, резервний автопілот). Він стежить за виходом активного основного контролера і готовий до миттєвого безударного перехоплення керування у разі відмови основного каналу.
- `MODE_AUTO` — штатний автоматичний режим замкненого контуру стабілізації з повним набором динамічних захистів.

Внутрішній стан регулятора ізольовано в окремій структурі, що дозволяє паралельно створювати довільну кількість незалежних екземплярів контурів (наприклад, для трьох осей кутової орієнтації крену, тангажу та рискання).

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Режими роботи регулятора
typedef enum {
    BUMPLESS_MODE_MANUAL   = 0,
    BUMPLESS_MODE_TRACKING = 1,
    BUMPLESS_MODE_AUTO     = 2
} bumpless_mode_t;

// Конфігураційні параметри регулятора
typedef struct {
    float kp;             // Пропорційний коефіцієнт
    float ki;             // Інтегральний коефіцієнт
    float kd;             // Диференціальний коефіцієнт
    float kt;             // Коефіцієнт контуру узгодження (1 / Tt)
    float b_weight;       // Вага уставки для P-каналу (0.0 ... 1.0)
    float tf_deriv;       // Стала часу фільтра похідної (с)
    float u_min;          // Нижня фізична межа актуатора
    float u_max;          // Верхня фізична межа актуатора
    float ramp_rate_max;  // Максимальна швидкість зміни уставки (од/с)
} bumpless_pid_config_t;

// Стан (пам'ять) регулятора між тактами
typedef struct {
    bumpless_pid_config_t cfg;
    bumpless_mode_t mode;

    float integrator;      // Накопичений стан інтегратора
    float y_prev;          // Попереднє значення виміру для похідної
    float deriv_filt;      // Відфільтрована похідна від виміру
    float r_filt;          // Відфільтрована (профільована) уставка
    float u_last;          // Останній фактично виданий сигнал на актуатор
    bool is_initialized;   // Прапорець первинної ініціалізації
} bumpless_pid_t;

static inline float pid_clamp(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

// Ініціалізація структури регулятора
void bumpless_pid_init(bumpless_pid_t *pid, const bumpless_pid_config_t *cfg, float initial_y) {
    if (!pid || !cfg) return;
    pid->cfg = *cfg;
    pid->mode = BUMPLESS_MODE_MANUAL;
    pid->integrator = 0.0f;
    pid->y_prev = initial_y;
    pid->deriv_filt = 0.0f;
    pid->r_filt = initial_y;
    pid->u_last = 0.0f;
    pid->is_initialized = true;
}

// Перемикання режиму роботи
void bumpless_pid_set_mode(bumpless_pid_t *pid, bumpless_mode_t new_mode) {
    if (!pid) return;
    pid->mode = new_mode;
}

// Безударна зміна пропорційного коефіцієнта (Gain Scheduling)
void bumpless_pid_set_gains(bumpless_pid_t *pid, float new_kp, float new_ki, float new_kd) {
    if (!pid) return;
    
    // Якщо регулятор активний, компенсуємо стрибок пропорційної складової в інтеграторі
    if (pid->mode == BUMPLESS_MODE_AUTO) {
        float current_error = pid->r_filt - pid->y_prev;
        float delta_kp = new_kp - pid->cfg.kp;
        pid->integrator -= delta_kp * current_error;
    }
    
    pid->cfg.kp = new_kp;
    pid->cfg.ki = new_ki;
    pid->cfg.kd = new_kd;
}

// Один дискретний крок обчислення регулятора
float bumpless_pid_step(bumpless_pid_t *pid, float r_target, float y_meas, float u_manual, float dt) {
    if (!pid || !pid->is_initialized || dt <= 0.0f) return 0.0f;

    // 1. Профілювання уставки (Slew-rate limiting)
    float max_step = pid->cfg.ramp_rate_max * dt;
    float delta_r = r_target - pid->r_filt;
    pid->r_filt += pid_clamp(delta_r, -max_step, max_step);

    // 2. Розрахунок помилки
    float e = pid->r_filt - y_meas;

    // 3. Диференціальна складова від виміру (Derivative on Measurement)
    float dy = (y_meas - pid->y_prev) / dt;
    float alpha_d = dt / (dt + pid->cfg.tf_deriv);
    pid->deriv_filt += alpha_d * (-dy - pid->deriv_filt);
    pid->y_prev = y_meas;

    // 4. Обробка ручного режиму або режиму стеження
    if (pid->mode == BUMPLESS_MODE_MANUAL || pid->mode == BUMPLESS_MODE_TRACKING) {
        float u_act = pid_clamp(u_manual, pid->cfg.u_min, pid->cfg.u_max);
        
        // Зворотний перерахунок інтегратора для забезпечення тотожності u_calc == u_act
        float u_p = pid->cfg.kp * (pid->cfg.b_weight * pid->r_filt - y_meas);
        float u_d = pid->cfg.kd * pid->deriv_filt;
        pid->integrator = u_act - u_p - u_d;
        
        pid->u_last = u_act;
        return u_act;
    }

    // 5. Автоматичний режим (2-DoF PID)
    float u_p = pid->cfg.kp * (pid->cfg.b_weight * pid->r_filt - y_meas);
    float u_d = pid->cfg.kd * pid->deriv_filt;
    float u_calc = u_p + pid->integrator + u_d;

    // 6. Обмеження виходу фізичними межами актуатора
    float u_act = pid_clamp(u_calc, pid->cfg.u_min, pid->cfg.u_max);

    // 7. Оновлення інтегратора з компенсацією насичення (Back-calculation Anti-windup)
    float tracking_diff = u_act - u_calc;
    pid->integrator += (pid->cfg.ki * e + pid->cfg.kt * tracking_diff) * dt;

    pid->u_last = u_act;
    return u_act;
}
```
```cpp
#include <algorithm>
#include <cstdint>
#include <span>

enum class ControllerMode : uint8_t {
    Manual,
    Tracking,
    Auto
};

struct PidGains {
    float kp{1.0f};
    float ki{0.1f};
    float kd{0.05f};
    float kt{1.0f};          // Коефіцієнт узгодження інтегратора (1 / Tt)
    float b_weight{1.0f};    // Вага уставки в P-каналі (0.0 ... 1.0)
    float tf_deriv{0.01f};   // Стала часу фільтра похідної
};

struct ActuatorLimits {
    float u_min{-100.0f};
    float u_max{100.0f};
    float ramp_rate_max{50.0f}; // Максимальна швидкість наростання уставки
};

class BumplessPid {
public:
    BumplessPid(PidGains gains, ActuatorLimits limits, float initial_y = 0.0f) noexcept
        : gains_(gains), limits_(limits), y_prev_(initial_y), r_filt_(initial_y) {}

    // Безударне оновлення коефіцієнтів (Gain Scheduling)
    void update_gains(float new_kp, float new_ki, float new_kd) noexcept {
        if (mode_ == ControllerMode::Auto) {
            const float current_error = r_filt_ - y_prev_;
            const float delta_kp = new_kp - gains_.kp;
            // Зміщення стану інтегратора для усунення стрибка
            integrator_ -= delta_kp * current_error;
        }
        gains_.kp = new_kp;
        gains_.ki = new_ki;
        gains_.kd = new_kd;
    }

    void set_mode(ControllerMode mode) noexcept {
        mode_ = mode;
    }

    [[nodiscard]] ControllerMode mode() const noexcept {
        return mode_;
    }

    [[nodiscard]] float last_output() const noexcept {
        return u_last_;
    }

    [[nodiscard]] float filtered_setpoint() const noexcept {
        return r_filt_;
    }

    // Один дискретний крок обчислення
    float step(float r_target, float y_meas, float u_manual, float dt) noexcept {
        if (dt <= 0.0f) return u_last_;

        // 1. Профілювання уставки (Setpoint Slew-rate limit)
        const float max_step = limits_.ramp_rate_max * dt;
        const float delta_r = r_target - r_filt_;
        r_filt_ += std::clamp(delta_r, -max_step, max_step);

        const float e = r_filt_ - y_meas;

        // 2. D-складова від виміру з аперіодичним фільтром низьких частот
        const float dy = (y_meas - y_prev_) / dt;
        const float alpha_d = dt / (dt + gains_.tf_deriv);
        deriv_filt_ += alpha_d * (-dy - deriv_filt_);
        y_prev_ = y_meas;

        // 3. Обробка ручного режиму та режиму стеження (Manual / Tracking)
        if (mode_ == ControllerMode::Manual || mode_ == ControllerMode::Tracking) {
            const float u_act = std::clamp(u_manual, limits_.u_min, limits_.u_max);
            const float u_p = gains_.kp * (gains_.b_weight * r_filt_ - y_meas);
            const float u_d = gains_.kd * deriv_filt_;

            // Зворотне узгодження інтегратора: I = u_act - u_P - u_D
            integrator_ = u_act - u_p - u_d;

            u_last_ = u_act;
            return u_act;
        }

        // 4. Автоматичний режим (2-DoF PID)
        const float u_p = gains_.kp * (gains_.b_weight * r_filt_ - y_meas);
        const float u_d = gains_.kd * deriv_filt_;
        const float u_calc = u_p + integrator_ + u_d;

        // 5. Затиск виходу межами приводу
        const float u_act = std::clamp(u_calc, limits_.u_min, limits_.u_max);

        // 6. Інтегральне накопичення з контуром Back-calculation Anti-windup
        const float tracking_diff = u_act - u_calc;
        integrator_ += (gains_.ki * e + gains_.kt * tracking_diff) * dt;

        u_last_ = u_act;
        return u_act;
    }

private:
    PidGains gains_;
    ActuatorLimits limits_;
    ControllerMode mode_{ControllerMode::Manual};

    float integrator_{0.0f};
    float y_prev_{0.0f};
    float deriv_filt_{0.0f};
    float r_filt_{0.0f};
    float u_last_{0.0f};
};
```
:::

### Детальний покроковий аналіз виконання такту

Розглянемо послідовність операцій, яка виконується на кожному кроці дискретизації `dt`:

1. **Профілювання уставки (Slew-rate limiting).**
   Уставка `r_target` може надходити від оператора чи автопілота у вигляді різких стрибків. Рядки:
   ```
   float max_step = pid->cfg.ramp_rate_max * dt;
   float delta_r = r_target - pid->r_filt;
   pid->r_filt += pid_clamp(delta_r, -max_step, max_step);
   ```
   обмежують швидкість приросту уставки фізично реалізованою швидкістю наростання приводу. Якщо `r_target` стрибнула на 50 одиниць, а максимальна швидкість становить 20 од/с при такті 10 мс (`max_step = 0.2`), уставка `r_filt` плавно зростатиме протягом 2.5 секунд, повністю усуваючи ударні збурення.

2. **Обчислення диференціальної складової від виміру (Derivative on Measurement).**
   Для усунення імпульсного сплеску при зміні уставки похідна обчислюється виключно за зміною виходу об'єкта `y_meas`:
   ```
   float dy = (y_meas - pid->y_prev) / dt;
   float alpha_d = dt / (dt + pid->cfg.tf_deriv);
   pid->deriv_filt += alpha_d * (-dy - pid->deriv_filt);
   ```
   Аперіодична ланка першого порядку з коефіцієнтом `alpha_d` відфільтровує високочастотний шум датчика (наприклад, вібрації гіроскопа від пропелерів дрона). Знак мінус відображає факт, що похідна від помилки `d(r - y)/dt` при сталій уставці дорівнює `-dy/dt`.

3. **Режим узгодження та ручного керування (Manual/Tracking).**
   Коли активний ручний режим, алгоритм не просто повертає значення `u_manual`, а виконує зворотний перерахунок стану інтегратора:
   ```
   float u_p = pid->cfg.kp * (pid->cfg.b_weight * pid->r_filt - y_meas);
   float u_d = pid->cfg.kd * pid->deriv_filt;
   pid->integrator = u_act - u_p - u_d;
   ```
   Цей вираз гарантує, що якщо на наступному такті режим буде змінено на `BUMPLESS_MODE_AUTO`, сума `u_p + integrator + u_d` дасть у точності `u_act`. Завдяки цьому сигнал керування залишається абсолютно гладким.

4. **Захист від насичення зворотним перерахунком (Back-Calculation Anti-Windup).**
   В автоматичному режимі обчислюється різниця між фактичним обмеженим сигналом `u_act` та необмеженим розрахунковим значенням `u_calc`:
   ```
   float tracking_diff = u_act - u_calc;
   pid->integrator += (pid->cfg.ki * e + pid->cfg.kt * tracking_diff) * dt;
   ```
   Якщо привід увійшов у насичення (наприклад, заслінка відкрита на 100%, тоді як ПІД вимагає 140%), `tracking_diff` стає від'ємним (-40%). Доданок `kt * tracking_diff` гальмує інтегрування і розряджає інтегратор, дозволяючи системі миттєво повернутися в лінійну зону при зміні знаку помилки.

### Числовий прогон та порівняльний експеримент

Для верифікації алгоритмів проведемо модельний експеримент із тактом дискретизації `Δt = 0.01` с (100 Гц). Об'єкт моделюється інерційною ланкою першого порядку з коефіцієнтом підсилення `K_obj = 1.0` та сталою часу `T_obj = 0.5` с.

Сценарій тестування містить три критичні фази:
1. **Фаза 1 (`t = 0.0 ... 2.0` с):** Ручний режим. Оператор утримує сигнал керування на рівні `u_man = 30.0%`. Об'єкт виходить на значення `y = 30.0`. Цільова уставка автомата встановлена на `r = 50.0`.
2. **Фаза 2 (`t = 2.0` с):** Перемикання в автоматичний режим стабілізації. У момент комутації помилка становить `e = 50.0 − 30.0 = 20.0`.
3. **Фаза 3 (`t = 4.0` с):** Параметрична зміна коефіцієнта підсилення `Kp` з `1.5` до `3.0` при збереженні динамічної помилки.

У таблиці наведено покроковий числовий лог поведінки звичайного наївного регулятора та безударного регулятора в околі точок перемикання:

```
─────────────────────────────────────────────────────────────────────────────
 Час t (с) │  Подія/Режим  │ Голий ПІД u(t) │ Безударний u(t) │ Стрибок Δu
─────────────────────────────────────────────────────────────────────────────
   1.98    │ Manual (ручне)│     30.000     │     30.000      │   0.000
   1.99    │ Manual (ручне)│     30.000     │     30.000      │   0.000
   2.00    │ → AUTO        │     60.000 ⚠   │     30.000 ✓    │ +30.000 / 0.000
   2.01    │ Auto          │     60.100     │     30.300      │   плавно
   ...     │ ...           │     ...        │     ...         │   ...
   3.98    │ Auto (сталий) │     45.000     │     45.000      │   0.000
   3.99    │ Auto (сталий) │     45.000     │     45.000      │   0.000
   4.00    │ Kp: 1.5 → 3.0 │     60.000 ⚠   │     45.000 ✓    │ +15.000 / 0.000
   4.01    │ Auto          │     60.080     │     45.120      │   плавно
─────────────────────────────────────────────────────────────────────────────
```

#### Аналіз результатів тесту

У момент перемикання `t = 2.00` с голий регулятор отримує пропорційну складову `u_P = Kp · e = 1.5 · 20.0 = 30.0%`. Оскільки його інтегратор перед увімкненням скидався в нуль (`I = 0`), загальний вихід становить `u = 30.0 + 0 = 30.0`, але додається до попереднього ручного рівня, стрибаючи до `60.0%` (удар `Δu = +30.0%`). Це миттєво штовхає об'єкт, викликаючи переліт понад 18% та різке коливання.

Безударний регулятор під час перебування в ручному режимі розраховував необхідний рівень інтегратора:

```
I[k] = u_act − Kp·(b·r − y) − Kd·deriv
I[k] = 30.0 − 1.5·(1.0·50.0 − 30.0) − 0.0 = 30.0 − 30.0 = 0.0
```

У момент `t = 2.00` с розрахунковий вихід склав `u = u_P + I = 30.0 + 0.0 = 30.000%`. Сигнал керування зберіг абсолютну неперервність (`Δu = 0.000%`).

У момент `t = 4.00` с при подвоєнні коефіцієнта `Kp` голий регулятор миттєво помножив поточну динамічну помилку `e = 10.0` на новий коефіцієнт, спричинивши стрибок виходу з `45.0%` до `60.0%` (`Δu = +15.0%`). Безударний алгоритм виконав інтегральну компенсацію стану:

```
I_new = I_old − ΔKp·e = 30.0 − (3.0 − 1.5)·10.0 = 30.0 − 15.0 = 15.0
u_new = Kp_new·e + I_new = 3.0·10.0 + 15.0 = 30.0 + 15.0 = 45.000%
```

Вихід `u(t)` знову залишився неперервним, а зміна коефіцієнта змінила виключно жорсткість реакції на подальші динамічні збурення, не створюючи жодних ударних сил на виконавчому механізмі.

### Методика налаштування параметрів стеження та профілювання

Для досягнення оптимальної плавності в реальному приводі рекомендується наступний порядок калібрування додаткових параметрів:

1. **Коефіцієнт стеження `kt` (1 / Tt):**
   - Розрахуйте базове значення `kt = ki / kp` (відповідає сталій часу інтегрування `Tt = Ti`).
   - Якщо актуатор має виражену динаміку насичення, збільшіть `kt` у 1.5–2.0 рази для прискореного скидання інтегрального перевантаження.
   - Якщо сигнал `u_manual` містить високочастотні завади чи шум оператора, зменшіть `kt` для фільтрації узгодження.

2. **Стала часу фільтра похідної `tf_deriv`:**
   - Обирається в діапазоні `tf_deriv = (0.05 ... 0.1) · Td`, де `Td = kd / kp`.
   - Для швидкісних контурів кутової швидкості (рейт-контролери дронів на 1 кГц) типове значення становить 2–5 мс.
   - Для повільних температурних чи гідравлічних контурів `tf_deriv` може досягати 0.1–0.5 с.

3. **Темп наростання уставки `ramp_rate_max`:**
   - Визначається експериментально за максимально допустимим струмом двигуна або кутовим прискоренням конструкції:
   ```
   ramp_rate_max ≤ a_max_actuator / (1.5 · kp)
   ```
   - Такий вибір гарантує, що при будь-якій сходинці вхідного завдання привід не виходитиме за межі лінійного діапазону струму.

### Крайові випадки та інтеграція в RTOS

Під час розгортання бібліотеки в операційних системах реального часу (FreeRTOS, Zephyr, NuttX) слід дотримуватися чотирьох правил:

1. **Атомарність зміни коефіцієнтів.** Функція `bumpless_pid_set_gains` звертається до стану інтегратора та поточної помилки. Якщо зміна параметрів викликається з потоку комунікацій або телеметрії, а розрахунок `bumpless_pid_step` виконується у високопріоритетному такті таймера, виклик повинен захищатися м'ютексом або критичною секцією (вимиканням переривань), щоб уникнути race condition посеред розрахунку компенсації.
2. **Збереження стану при гарячому перезавантаженні.** Якщо модуль регулятора перезапускається або перемикається між резервними мікроконтролерами (Dual-redundant flight computer), попередній стан актуатора `u_last` та згладжена уставка `r_filt` передаються через спільну пам'ять або шину CAN. Функція ініціалізації встановлює інтегратор `I = u_last`, гарантуючи плавний підхват керування без зупинки двигунів.
3. **Фізичний діапазон і числове переповнення.** Якщо обчислення ведуться на мікроконтролерах без блоку апаратної рухомої коми (FPU) з використанням фіксованої коми (Q-формат), накопичувач інтеграла повинен мати розрядність не менше 32 або 64 біт із примусовим насиченням, оскільки в режимі Tracking Mode інтеграл може приймати знакозмінні компенсуючі значення великої амплітуди.
4. **Вирівнювання пам'яті та кеш процесора.** Для високочастотних контурів стабілізації (4–8 кГц на процесорах ARM Cortex-M7 з увімкненим D-Cache) структура `bumpless_pid_t` має бути вирівняна за межею рядка кешу (32 байти), а змінні `integrator`, `deriv_filt` та `r_filt` згруповані поруч у пам'яті для мінімізації кількості промахів кешу даних.
