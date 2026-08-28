# ⚙️ Промислова реалізація цифрового ПІД-регулятора з анти-windup

Теоретичні підручникові формули неперервного ПІД-регулювання оперують ідеальними сигналами нескінченного діапазону. На практиці мікроконтролер керує реальними виконавчими органами — транзисторними ШІМ-ключами, електроприводами з обмеженою напругою живлення або регулювальними клапанами з кінцевими упорами від 0% до 100%. Щойно виконавчий орган досягає свого упору, зворотний зв'язок розривається: зміна розрахункового керування більше не впливає на керований об'єкт. Якщо в цей час інтегратор продовжує накопичувати похибку, система потрапляє в стан інтегрального насичення (*integrator windup*), з якого виходитиме з величезним запізненням і руйнівним перерегулюванням.

Промисловий цифровий регулятор вимагає не просто формули підсумовування трьох складових, а цілісної обчислювальної архітектури. Вона включає динамічний захист від насичення (*anti-windup*), смугообмежену диференціальну дію за вектором вимірювання (*Derivative on Measurement*) для усунення диференціальних ударів, зважування уставки за пропорційним каналом та механізм безударного переходу між ручним і автоматичним режимами керування (*bumpless transfer*).

### Обчислювальна структура та ланки алгоритму

Цифровий регулятор виконує обчислення дискретно з фіксованим періодом квантування `T_s` (вбудований таймерний перерив або RTOS-задача). Архітектура складається з чотирьох послідовних модулів, які захищають виконавчий механізм від ударних навантажень і перевантаження.

```
       r[k] (уставка)
         │
         ├───[ Ваговий коефіцієнт β ]────(+)
         │                                │
         │   y[k] (датчик)                │
         │     │                          │
         │     ├──[ Інверсія (−) ]────────┴──[ Kp ]────────────────────(+)
         │     │                                                        │
         │     └──[ D-фільтр: −Kd·s/(1+sTf) ]──────────────────────────(+)──> u[k] ──[ sat(·) ]──> u_sat[k]
         │                                                              │         │        │
         └──(+)                                                         │         └──(─)   │
             │                                                          │             │    │
             └──[ e = r − y ]───[ Інтегратор: Kp/Ti ]───(+)─────────────┘             │    │
                                                          │                           │    │
                                                          └─────[ Anti-Windup: 1/Tt ]─┴────┘
```

#### 1. Зважування уставки в пропорційному каналі

Класичний пропорційний член `u_p = K_p · (r - y)` генерує миттєвий стрибок амплітудою `K_p · Δr` при кожній східчастій зміні завдання оператором. Для пом'якшення навантаження на привод вводиться ваговий коефіцієнт уставки `β ∈ [0.0, 1.0]`:

```
e_p[k] = β · r[k] - y[k]
u_p[k] = K_p · e_p[k]
```

Якщо `β = 1.0`, регулятор реалізує стандартну реакцію на похибку. Якщо `β = 0.0`, пропорційний канал реагує тільки на зміну виходу об'єкта `y[k]`, повністю ігноруючи стрибки уставки `r[k]`, що робить перехідний процес максимально плавним (критично для гідравліки та потужних електроприводів).

#### 2. Диференціювання за вимірюванням з аперіодичною фільтрацією

Пряме диференціювання похибки `de/dt = dr/dt - dy/dt` призводить до появи нескінченно великого імпульсу («диференціального удару») у момент зміни уставки, оскільки `dr/dt` на сходинці формально дорівнює дельта-функції Дірака. Щоб усунути цей дефект, диференціювання застосовують винятково до сигналу вимірювання `y(t)`: `u_d = -K_d · dy/dt`.

Крім того, будь-який реальний датчик має шум вимірювання (квантування АЦП, електромагнітні наведення). Операція диференціювання підсилює високочастотний шум пропорційно частоті `ω`. Щоб обмежити смугу пропускання диференціатора, послідовно з ним вмикається фільтр низьких частот першого порядку зі сталою часу `T_f = T_d / N`, де `N` — коефіцієнт фільтрації (типово `N ∈ [8, 20]`):

```
u_d(s) = - (K_p · T_d · s / (1 + s · T_d / N)) · Y(s)
```

Дискретизація цього виразу методом Ейлера назад дає рекурентну формулу для кроку `k`:

```
α = T_d / (T_d + N · T_s)
β_d = (K_p · T_d · N) / (T_d + N · T_s)
u_d[k] = α · u_d[k-1] - β_d · (y[k] - y[k-1])
```

#### 3. Інтегральний канал та механізми Anti-Windup

Інтегратор відповідає за усунення статичної похибки системи в усталеному режимі. У неперервному часі він обчислює `x_i(t) = (K_p / T_i) · ∫ e(τ) dτ`. Реалізація підтримує два промислові варіанти захисту від насичення:

- **Метод умовного інтегрування (*Clamping / Conditional Integration*):** перед додаванням чергової порції інтеграла алгоритм перевіряє стан виходу на попередньому такті. Якщо вихід уже уперся в межу (`u ≥ u_max` або `u ≤ u_min`), і знак поточної похибки збігається зі знаком переповнення (`e > 0` для верхньої межі або `e < 0` для нижньої), інтегрування тимчасово зупиняється (`Δx_i = 0`). Якщо ж похибка має протилежний знак, інтегрування дозволяється, оскільки воно сприяє виходу із насичення.
- **Метод зворотного перерахунку (*Back-Calculation / Tracking Anti-Windup*):** обчислюється різниця між фактично реалізованим обмеженим сигналом `u_sat[k-1]` та розрахунковим ненасиченим значенням `u[k-1]`. Ця різниця `e_s = u_sat - u` множиться на коефіцієнт `T_s / T_t` і додається до інтегратора, динамічно розряджаючи його до величини, що відповідає межі насичення.

#### 4. Безударне перемикання режимів (Bumpless Transfer)

В автоматизованих системах керування технологічним процесом (АСУ ТП) оператор часто перемикає контур у ручний режим (*Manual Mode*), щоб безпосередньо виставити потужність чи положення заслінки, а потім повертає його в автоматичний (*Auto Mode*). Якщо при поверненні в автомат стан інтегратора виявиться застарілим або довільним, вихід регулятора миттєво підскочить, викликавши гідроудар або аварійний викид параметрів.

Для забезпечення абсолютної безударності в ручному режимі інтегратор працює як «слідкуюча пам'ять»: на кожному кроці його стан примусово коригується за формулою:

```
x_i[k] = u_manual - u_p[k] - u_d[k]
```

Завдяки цьому в момент перемикання `Manual -> Auto` розрахунковий вихід регулятора `u_auto = u_p + x_i + u_d` точно дорівнює останньому ручному значенню `u_manual`, і перехід відбувається ідеально плавно.

### Промислова реалізація мовами C та C++

:::tabs
```c
/* Промисловий цифровий ПІД-регулятор з Anti-Windup (C99 / C11) */

#include <stdbool.h>
#include <stddef.h>
#include <math.h>

typedef enum {
    PID_ANTI_WINDUP_NONE = 0,
    PID_ANTI_WINDUP_CLAMPING,
    PID_ANTI_WINDUP_BACK_CALCULATION
} pid_anti_windup_mode_t;

typedef struct {
    /* Параметри налаштування регулятора */
    float kp;               /* Пропорційний коефіцієнт підсилення */
    float ti;               /* Стала часу інтегрування (с) */
    float td;               /* Стала часу диференціювання (с) */
    float tt;               /* Стала часу стеження anti-windup (с) */
    float nd;               /* Коефіцієнт фільтрації D-члена (типово 10.0) */
    float beta;             /* Ваговий коефіцієнт уставки для P-члена (0.0..1.0) */
    float ts;               /* Період дискретизації квантування (с) */
    float out_min;          /* Нижня фізична межа насичення виходу */
    float out_max;          /* Верхня фізична межа насичення виходу */
    pid_anti_windup_mode_t aw_mode; /* Обраний режим захисту від windup */

    /* Внутрішні змінні стану */
    float integrator_state; /* Накопичений стан інтегратора */
    float deriv_filter_state; /* Стан аперіодичного фільтра D-члена */
    float prev_pv;          /* Значення вимірюваної величини на попередньому кроці */
    float prev_unsat_out;   /* Повний ненасичений вихід на попередньому кроці */
    float prev_sat_out;     /* Реальний обмежений вихід на попередньому кроці */
    bool is_manual;         /* Прапорець ручного режиму керування */
} pid_controller_t;

void pid_init(pid_controller_t *pid, float kp, float ti, float td, float ts,
              float out_min, float out_max, pid_anti_windup_mode_t aw_mode) {
    if (!pid || ts <= 0.0f) return;

    pid->kp = kp;
    pid->ti = (ti > 0.0f) ? ti : 1e-3f;
    pid->td = (td >= 0.0f) ? td : 0.0f;
    pid->tt = (ti > 0.0f) ? ti : 1e-3f; /* За замовчуванням Tt = Ti */
    pid->nd = 10.0f;
    pid->beta = 1.0f;
    pid->ts = ts;
    pid->out_min = out_min;
    pid->out_max = out_max;
    pid->aw_mode = aw_mode;

    pid->integrator_state = 0.0f;
    pid->deriv_filter_state = 0.0f;
    pid->prev_pv = 0.0f;
    pid->prev_unsat_out = 0.0f;
    pid->prev_sat_out = 0.0f;
    pid->is_manual = false;
}

void pid_reset(pid_controller_t *pid, float current_pv) {
    if (!pid) return;
    pid->integrator_state = 0.0f;
    pid->deriv_filter_state = 0.0f;
    pid->prev_pv = current_pv;
    pid->prev_unsat_out = 0.0f;
    pid->prev_sat_out = 0.0f;
}

void pid_set_manual_output(pid_controller_t *pid, float manual_out, float current_pv) {
    if (!pid) return;
    pid->is_manual = true;
    pid->prev_pv = current_pv;

    /* Обмеження сигналу за фізичними межами */
    if (manual_out > pid->out_max) manual_out = pid->out_max;
    if (manual_out < pid->out_min) manual_out = pid->out_min;

    pid->prev_sat_out = manual_out;
    pid->prev_unsat_out = manual_out;

    /* Підгонка інтегратора для безударного переходу (Bumpless Transfer) */
    float p_term = pid->kp * (pid->beta * current_pv - current_pv);
    pid->integrator_state = manual_out - p_term;
}

void pid_set_auto_mode(pid_controller_t *pid) {
    if (!pid) return;
    pid->is_manual = false;
}

float pid_update(pid_controller_t *pid, float sp, float pv) {
    if (!pid) return 0.0f;

    /* У ручному режимі вихід жорстко зафіксовано оператором */
    if (pid->is_manual) {
        return pid->prev_sat_out;
    }

    float error = sp - pv;

    /* 1. Пропорційний канал із вагою уставки beta */
    float p_term = pid->kp * (pid->beta * sp - pv);

    /* 2. Диференціювання за вимірюванням з аперіодичним фільтром */
    float d_term = 0.0f;
    if (pid->td > 0.0f) {
        float denom = pid->td + pid->nd * pid->ts;
        float alpha = pid->td / denom;
        float beta_d = (pid->kp * pid->td * pid->nd) / denom;
        float delta_pv = pv - pid->prev_pv;

        pid->deriv_filter_state = alpha * pid->deriv_filter_state - beta_d * delta_pv;
        d_term = pid->deriv_filter_state;
    }

    /* 3. Оновлення стану інтегратора залежно від алгоритму Anti-Windup */
    float ki_gain = (pid->kp / pid->ti) * pid->ts;

    switch (pid->aw_mode) {
        case PID_ANTI_WINDUP_CLAMPING: {
            bool saturated_high = (pid->prev_unsat_out >= pid->out_max);
            bool saturated_low  = (pid->prev_unsat_out <= pid->out_min);
            bool error_positive = (error > 0.0f);
            bool error_negative = (error < 0.0f);

            /* Заморожуємо інтегрування, якщо насичено і похибка діє на поглиблення насичення */
            bool clamp = (saturated_high && error_positive) || (saturated_low && error_negative);
            if (!clamp) {
                pid->integrator_state += ki_gain * error;
            }
            break;
        }

        case PID_ANTI_WINDUP_BACK_CALCULATION: {
            float tracking_error = pid->prev_sat_out - pid->prev_unsat_out;
            float tracking_correction = (pid->ts / pid->tt) * tracking_error;
            pid->integrator_state += ki_gain * error + tracking_correction;
            break;
        }

        case PID_ANTI_WINDUP_NONE:
        default:
            pid->integrator_state += ki_gain * error;
            break;
    }

    /* 4. Формування повного розрахункового сигналу */
    float unsat_out = p_term + pid->integrator_state + d_term;

    /* 5. Фізичне насичення виконавчого органу sat(u) */
    float sat_out = unsat_out;
    if (sat_out > pid->out_max) sat_out = pid->out_max;
    if (sat_out < pid->out_min) sat_out = pid->out_min;

    /* Збереження стану для наступного циклу */
    pid->prev_pv = pv;
    pid->prev_unsat_out = unsat_out;
    pid->prev_sat_out = sat_out;

    return sat_out;
}
```
```cpp
// Промисловий цифровий ПІД-регулятор з Anti-Windup (C++20)

#include <algorithm>
#include <cmath>
#include <concepts>
#include <cstdint>

enum class AntiWindupMode : uint8_t {
    None,
    Clamping,
    BackCalculation
};

struct PidGains {
    float kp{1.0f};          // Пропорційний коефіцієнт
    float ti{1.0f};          // Стала часу інтегрування (с)
    float td{0.0f};          // Стала часу диференціювання (с)
    float tt{1.0f};          // Стала часу стеження anti-windup (с)
    float nd{10.0f};         // Коефіцієнт фільтра D-члена (типово 10)
    float beta{1.0f};        // Ваговий коефіцієнт уставки P-члена (0..1)
};

struct PidLimits {
    float out_min{0.0f};
    float out_max{100.0f};
};

class PidController {
public:
    constexpr PidController(PidGains gains, PidLimits limits, float ts,
                            AntiWindupMode mode = AntiWindupMode::BackCalculation) noexcept
        : gains_{sanitize_gains(gains)},
          limits_{limits},
          ts_{ts > 0.0f ? ts : 0.01f},
          mode_{mode} {}

    void reset(float current_pv = 0.0f) noexcept {
        integrator_state_ = 0.0f;
        deriv_filter_state_ = 0.0f;
        prev_pv_ = current_pv;
        prev_unsat_out_ = 0.0f;
        prev_sat_out_ = 0.0f;
        is_manual_ = false;
    }

    void set_manual(float manual_output, float current_pv) noexcept {
        is_manual_ = true;
        prev_pv_ = current_pv;
        prev_sat_out_ = std::clamp(manual_output, limits_.out_min, limits_.out_max);
        prev_unsat_out_ = prev_sat_out_;

        // Безударний перехід: підгонка інтегратора під поточний вихід
        const float p_term = gains_.kp * (gains_.beta * current_pv - current_pv);
        integrator_state_ = prev_sat_out_ - p_term;
    }

    void set_auto() noexcept {
        is_manual_ = false;
    }

    [[nodiscard]] float update(float setpoint, float process_variable) noexcept {
        if (is_manual_) {
            return prev_sat_out_;
        }

        const float error = setpoint - process_variable;

        // 1. Пропорційний канал із вагою уставки
        const float p_term = gains_.kp * (gains_.beta * setpoint - process_variable);

        // 2. Диференціювання за вимірюванням з аперіодичним фільтром
        float d_term = 0.0f;
        if (gains_.td > 0.0f) {
            const float denom = gains_.td + gains_.nd * ts_;
            const float alpha = gains_.td / denom;
            const float beta_d = (gains_.kp * gains_.td * gains_.nd) / denom;
            const float delta_pv = process_variable - prev_pv_;

            deriv_filter_state_ = alpha * deriv_filter_state_ - beta_d * delta_pv;
            d_term = deriv_filter_state_;
        }

        // 3. Інтегральний канал із захистом Anti-Windup
        const float ki_gain = (gains_.kp / gains_.ti) * ts_;

        switch (mode_) {
            case AntiWindupMode::Clamping: {
                const bool saturated_high = (prev_unsat_out_ >= limits_.out_max);
                const bool saturated_low  = (prev_unsat_out_ <= limits_.out_min);
                const bool pushes_high    = (error > 0.0f);
                const bool pushes_low     = (error < 0.0f);

                const bool clamp = (saturated_high && pushes_high) || (saturated_low && pushes_low);
                if (!clamp) {
                    integrator_state_ += ki_gain * error;
                }
                break;
            }

            case AntiWindupMode::BackCalculation: {
                const float tracking_error = prev_sat_out_ - prev_unsat_out_;
                const float tracking_correction = (ts_ / gains_.tt) * tracking_error;
                integrator_state_ += ki_gain * error + tracking_correction;
                break;
            }

            case AntiWindupMode::None:
            default:
                integrator_state_ += ki_gain * error;
                break;
        }

        // 4. Повний ненасичений сигнал
        const float unsat_out = p_term + integrator_state_ + d_term;

        // 5. Фізичне насичення
        const float sat_out = std::clamp(unsat_out, limits_.out_min, limits_.out_max);

        // Оновлення збереженого стану
        prev_pv_ = process_variable;
        prev_unsat_out_ = unsat_out;
        prev_sat_out_ = sat_out;

        return sat_out;
    }

    [[nodiscard]] float integrator_state() const noexcept { return integrator_state_; }
    [[nodiscard]] bool is_saturated() const noexcept {
        return prev_unsat_out_ != prev_sat_out_;
    }

private:
    static constexpr PidGains sanitize_gains(PidGains g) noexcept {
        if (g.ti <= 0.0f) g.ti = 1e-3f;
        if (g.td < 0.0f)  g.td = 0.0f;
        if (g.tt <= 0.0f) g.tt = g.ti;
        if (g.nd <= 0.0f) g.nd = 10.0f;
        g.beta = std::clamp(g.beta, 0.0f, 1.0f);
        return g;
    }

    PidGains gains_;
    PidLimits limits_;
    float ts_{0.01f};
    AntiWindupMode mode_{AntiWindupMode::BackCalculation};

    float integrator_state_{0.0f};
    float deriv_filter_state_{0.0f};
    float prev_pv_{0.0f};
    float prev_unsat_out_{0.0f};
    float prev_sat_out_{0.0f};
    bool is_manual_{false};
};
```
:::

### Інженерні тонкощі та крайові випадки в реальних системах

Під час впровадження регулятора у вбудовані системи керування необхідно враховувати специфічні апаратні обмеження:

1. **Динамічна зміна меж насичення:**
   У багатьох практичних задачах межі `out_min` та `out_max` не є постійними константами. Наприклад, у безпілотних літальних апаратах максимальна доступна тяга двигунів зменшується зі спаданням напруги літій-полімерного акумулятора під час розряду. У таких випадках межі передаються як динамічні змінні, а контур зворотного перерахунку миттєво підлаштовує стан інтегратора під фактично доступну напругу без виникнення сплесків.

2. **Захист від накопичення похибок квантування:**
   При роботі з 32-розрядними числами одинарної точності (*IEEE 754 float*) додавання дуже малої величини `ki_gain · error` до великого накопиченого числа `integrator_state` може спричинити втрату молодших розрядів (числове затихання). Якщо період дискретизації дуже малий (наприклад, `T_s = 100 мкс`), інтегрування рекомендується виконувати у форматі `double` або 64-розрядному фіксованому форматі `int64_t` на контролерах без апаратного FPU.

3. **Синхронізація зі статусом зовнішнього виконавця:**
   Якщо виконавчий механізм є «розумним» (наприклад, сервопривід із шиною CAN або клапан із цифровим позиціонером), він може сам передавати сигнал реального положення `u_actual` або прапорець апаратного насичення. У такому разі замість розрахункового `sat(u)` у контур зворотного перерахунку подається фактичне виміряне положення привода `u_actual`. Це запобігає інтегральному насиченню навіть у випадку, коли привід механічно заклинило стороннім предметом.
