# ⚙️ Стійкий диференціатор сигналів реального часу для вбудованих систем

Обчислення швидкості та прискорення з зашумлених дискретних вимірів положення вимагає стійких алгоритмів реального часу, які захищають виконавчі механізми від ударних шумів квантування та не втрачають фазу сигналу. У цьому проекті реалізовано бібліотеку чисельного диференціювання для мікроконтролерів (ARM Cortex-M, ESP32, RISC-V): каскадний фільтрований диференціатор Тастіна, відслідковувальний спостерігач стану (Alpha-Beta-Gamma фільтр) із захистом від фазових стрибків і перевантаження, а також тестовий модуль оцінки точності.

---

### 1. Архітектура та математичні моделі

Обчислення похідних у вбудованих системах керування стикається з трьома основними викликами: дискретним квантуванням датчиків (енкодерів, резольверів, АЦП), часовим джиттером періодичних переривань таймера та обмеженими обчислювальними ресурсами процесора.

Бібліотека реалізує три взаємодоповнюючі підходи, адаптовані до специфіки мікроконтролерів:

1. **Каскадний білінійний диференціатор Тастіна (Bilinear Tustin Differentiator):**
   Поєднує передатну функцію диференціювання з фільтром Баттерворта другого порядку: `H(s) = s · ω² / (s² + 2·ζ·ω·s + ω²)`. Дискретизація методом Тастіна зберігає асимптотичну стійкість та пригнічує шум квантування АЦП із нахилом -20 дБ/декада вище частоти зрізу `f_cutoff`.

2. **Стійкий спостерігач стану третього порядку (Alpha-Beta-Gamma Tracking Observer):**
   Містить внутрішню фізичну модель кінематики тіла (`x(t), v(t), a(t)`). Оновлюється через похибку передбачення, що дозволяє отримувати абсолютно неперервні значення швидкості та прискорення навіть при сильних перервах або квантуванні імпульсів енкодера.

3. **Модульне розгортання кута (Phase Unwrapping):**
   Захищає алгоритми диференціювання від фазових стрибків `±2π` при переповненні лічильників циклічних датчиків кута (резольверів та абсолютних енкодерів).

---

### 2. Принцип роботи спостерігача стану (Alpha-Beta-Gamma фільтр)

Спостерігач стану діє як віртуальний цифровий маховик із відомою кінематичною моделлю. На кожному такті він виконує двоетапний цикл:

1. **Етап екстраполяції (Prediction):**
   На основі поточної оцінки положення, швидкості та прискорення інтегруються диференціальні рівняння руху Ньютона:
   ```
   x_pred = x + v·dt + 0.5·a·dt²
   v_pred = v + a·dt
   a_pred = a
   ```

2. **Етап корекції (Correction):**
   Обчислюється похибка інновації виміру `residual = x_meas - x_pred`. Стан коригується пропорційно коефіцієнтам підсилення `α, β, γ`:
   ```
   x_new = x_pred + α · residual
   v_new = v_pred + (β / dt) · residual
   a_new = a_pred + (2·γ / dt²) · residual
   ```

Характеристичне рівняння замкненого спостерігача в дискретній Z-області визначається виразом:
```
P(z) = z³ + (α + β + γ - 3)·z² + (3 - 2α - β + γ)·z + (α - 1) = 0
```
Для забезпечення асимптотичної стійкості всі корені рівняння `z_i` мають лежати строго всередині одиничного кола `|z_i| < 1`. Коефіцієнти `α, β, γ` пов'язані з бажаною власною частотою `ω_n` та коефіцієнтом демпфування `ζ` дискретної системи, що гарантує відсутність перерегулювання та резонансних сплесків.

---

### 3. Реалізація бібліотеки мовами C та C++

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define PI_F 3.14159265358979323846f

/* --- Модульне розгортання кута (Phase Unwrapping) --- */
float unwrap_angle_diff(float measured_pos, float prev_pos) {
    float diff = measured_pos - prev_pos;
    while (diff > PI_F)  diff -= 2.0f * PI_F;
    while (diff < -PI_F) diff += 2.0f * PI_F;
    return diff;
}

/* --- 1. Спостерігач стану Alpha-Beta-Gamma --- */
typedef struct {
    float pos;          /* оцінене положення x̂ */
    float vel;          /* оцінена швидкість v̂ */
    float acc;          /* оцінене прискорення â */
    float alpha;        /* коефіцієнт корекції положення */
    float beta;         /* коефіцієнт корекції швидкості */
    float gamma;        /* коефіцієнт корекції прискорення */
    float max_accel;    /* обмеження максимального фізичного прискорення */
    bool initialized;
} TrackingDifferentiator;

void track_diff_init(TrackingDifferentiator* td, float alpha, float beta, float gamma, float max_accel) {
    td->pos = 0.0f;
    td->vel = 0.0f;
    td->acc = 0.0f;
    td->alpha = (alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.6f;
    td->beta = (beta > 0.0f && beta <= 1.0f) ? beta : 0.3f;
    td->gamma = (gamma >= 0.0f && gamma <= 1.0f) ? gamma : 0.05f;
    td->max_accel = (max_accel > 0.0f) ? max_accel : 10000.0f;
    td->initialized = false;
}

void track_diff_reset(TrackingDifferentiator* td, float initial_pos) {
    td->pos = initial_pos;
    td->vel = 0.0f;
    td->acc = 0.0f;
    td->initialized = true;
}

void track_diff_update(TrackingDifferentiator* td, float measured_pos, float dt) {
    if (dt <= 0.000001f || dt > 1.0f) {
        return; /* Захист від збою таймера або джиттера */
    }

    if (!td->initialized) {
        track_diff_reset(td, measured_pos);
        return;
    }

    /* 1. Етап прогнозу (інтегрування моделі кінематики) */
    const float pos_pred = td->pos + td->vel * dt + 0.5f * td->acc * dt * dt;
    const float vel_pred = td->vel + td->acc * dt;
    const float acc_pred = td->acc;

    /* 2. Інновація виміру з розгортанням кута */
    const float residual = unwrap_angle_diff(measured_pos, pos_pred);

    /* 3. Етап корекції стану */
    td->pos = pos_pred + td->alpha * residual;
    td->vel = vel_pred + (td->beta / dt) * residual;
    
    float new_acc = acc_pred + (2.0f * td->gamma / (dt * dt)) * residual;

    /* Обмеження прискорення фізичними межами привода */
    if (new_acc > td->max_accel) {
        new_acc = td->max_accel;
    } else if (new_acc < -td->max_accel) {
        new_acc = -td->max_accel;
    }
    td->acc = new_acc;
}

/* --- 2. Диференціатор Тастіна другого порядку --- */
typedef struct {
    float x1, x2;       /* стан фільтра прямої форми II */
    float y_prev;       /* попереднє значення виходу */
    float cutoff_rad;   /* частота зрізу в рад/с */
} TustinDifferentiator2nd;

void tustin2_init(TustinDifferentiator2nd* td, float cutoff_hz) {
    td->x1 = 0.0f;
    td->x2 = 0.0f;
    td->y_prev = 0.0f;
    td->cutoff_rad = 2.0f * PI_F * ((cutoff_hz > 0.1f) ? cutoff_hz : 10.0f);
}

float tustin2_update(TustinDifferentiator2nd* td, float input, float dt) {
    if (dt <= 0.000001f) {
        return td->y_prev;
    }

    /* H(s) = s * omega^2 / (s^2 + 2*zeta*omega*s + omega^2), де zeta = 0.7071 */
    const float w = td->cutoff_rad;
    const float zeta = 0.70710678f;
    const float c = 2.0f / dt;

    const float a0 = c * c + 2.0f * zeta * w * c + w * w;
    const float b0 = (c * w * w) / a0;
    const float b2 = -b0;
    const float a1 = (2.0f * w * w - 2.0f * c * c) / a0;
    const float a2 = (c * c - 2.0f * zeta * w * c + w * w) / a0;

    /* Пряма форма II */
    const float x0 = input - a1 * td->x1 - a2 * td->x2;
    const float output = b0 * x0 + b2 * td->x2;

    td->x2 = td->x1;
    td->x1 = x0;
    td->y_prev = output;

    return output;
}
```
```cpp
#include <algorithm>
#include <array>
#include <concepts>
#include <numbers>
#include <optional>

/* --- Модульне розгортання кута (Phase Unwrapping C++20) --- */
[[nodiscard]] constexpr float unwrap_angle_diff(float measured_pos, float prev_pos) noexcept {
    constexpr float pi = std::numbers::pi_v<float>;
    constexpr float two_pi = 2.0f * pi;
    float diff = measured_pos - prev_pos;
    while (diff > pi)  diff -= two_pi;
    while (diff < -pi) diff += two_pi;
    return diff;
}

/* --- 1. Спостерігач стану Alpha-Beta-Gamma на C++20 --- */
class TrackingDifferentiator {
public:
    struct State {
        float position{0.0f};
        float velocity{0.0f};
        float acceleration{0.0f};
    };

    struct Gains {
        float alpha{0.6f};
        float beta{0.3f};
        float gamma{0.05f};
        float max_acceleration{10000.0f};
    };

    constexpr explicit TrackingDifferentiator(Gains gains = {}) noexcept
        : gains_{validate_gains(gains)} {}

    void reset(float initial_position = 0.0f) noexcept {
        state_.position = initial_position;
        state_.velocity = 0.0f;
        state_.acceleration = 0.0f;
        initialized_ = true;
    }

    void update(float measured_position, float dt) noexcept {
        if (dt <= 1e-6f || dt > 1.0f) {
            return;
        }

        if (!initialized_) {
            reset(measured_position);
            return;
        }

        /* 1. Кінематичний прогноз */
        const float pos_pred = state_.position + state_.velocity * dt + 0.5f * state_.acceleration * dt * dt;
        const float vel_pred = state_.velocity + state_.acceleration * dt;
        const float acc_pred = state_.acceleration;

        /* 2. Нев'язка вимірювання з захистом від стрибка 2*pi */
        const float residual = unwrap_angle_diff(measured_position, pos_pred);

        /* 3. Корекція за коефіцієнтами спостерігача */
        state_.position = pos_pred + gains_.alpha * residual;
        state_.velocity = vel_pred + (gains_.beta / dt) * residual;
        
        const float raw_acc = acc_pred + (2.0f * gains_.gamma / (dt * dt)) * residual;
        state_.acceleration = std::clamp(raw_acc, -gains_.max_acceleration, gains_.max_acceleration);
    }

    [[nodiscard]] constexpr State state() const noexcept { return state_; }
    [[nodiscard]] constexpr float velocity() const noexcept { return state_.velocity; }
    [[nodiscard]] constexpr float acceleration() const noexcept { return state_.acceleration; }

private:
    static constexpr Gains validate_gains(Gains g) noexcept {
        g.alpha = std::clamp(g.alpha, 0.01f, 1.0f);
        g.beta = std::clamp(g.beta, 0.001f, 1.0f);
        g.gamma = std::clamp(g.gamma, 0.0001f, 1.0f);
        g.max_acceleration = (g.max_acceleration > 0.0f) ? g.max_acceleration : 10000.0f;
        return g;
    }

    Gains gains_;
    State state_{};
    bool initialized_{false};
};

/* --- 2. Диференціатор Тастіна другого порядку (C++20) --- */
class TustinDifferentiator2nd {
public:
    explicit TustinDifferentiator2nd(float cutoff_hz = 10.0f) noexcept
        : cutoff_rad_{2.0f * std::numbers::pi_v<float> * std::max(cutoff_hz, 0.1f)} {}

    [[nodiscard]] float update(float input, float dt) noexcept {
        if (dt <= 1e-6f) {
            return y_prev_;
        }

        constexpr float zeta = 0.70710678f;
        const float w = cutoff_rad_;
        const float c = 2.0f / dt;

        const float a0 = c * c + 2.0f * zeta * w * c + w * w;
        const float b0 = (c * w * w) / a0;
        const float b2 = -b0;
        const float a1 = (2.0f * w * w - 2.0f * c * c) / a0;
        const float a2 = (c * c - 2.0f * zeta * w * c + w * w) / a0;

        const float x0 = input - a1 * x1_ - a2 * x2_;
        const float output = b0 * x0 + b2 * x2_;

        x2_ = x1_;
        x1_ = x0;
        y_prev_ = output;

        return output;
    }

    constexpr void reset() noexcept {
        x1_ = 0.0f;
        x2_ = 0.0f;
        y_prev_ = 0.0f;
    }

    [[nodiscard]] constexpr float value() const noexcept { return y_prev_; }

private:
    float cutoff_rad_{20.0f * std::numbers::pi_v<float>};
    float x1_{0.0f};
    float x2_{0.0f};
    float y_prev_{0.0f};
};
```
:::

---

### 4. Тестовий стенд та аналіз точності

Для перевірки стійкості алгоритмів створено симуляційний бенчмарк: гармонійний рух положення `x(t) = sin(2·π·f·t)` квантується до рівня 12-бітного енкодера (`4096` відліків на оберт), до сигналу додається часовий джиттер виклику переривань `±2% dt`, і порівнюються виходи наївної зворотної різниці, фільтра Тастіна та спостерігача `Alpha-Beta-Gamma`:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

void run_differentiator_benchmark(void) {
    TrackingDifferentiator track;
    track_diff_init(&track, 0.45f, 0.15f, 0.02f, 5000.0f);

    TustinDifferentiator2nd tustin;
    tustin2_init(&tustin, 20.0f);

    const float dt_nominal = 0.001f; /* 1 кГц */
    const float freq = 2.0f;          /* 2 Гц рух */
    float prev_meas = 0.0f;
    float peak_naive_err = 0.0f;
    float peak_tustin_err = 0.0f;
    float peak_track_err = 0.0f;

    for (int step = 0; step < 2000; ++step) {
        float t = step * dt_nominal;
        float true_pos = sinf(2.0f * PI_F * freq * t);
        float true_vel = 2.0f * PI_F * freq * cosf(2.0f * PI_F * freq * t);

        /* Моделювання квантування енкодера: 4096 поділок на діапазон [-1, 1] */
        float quant_step = 2.0f / 4096.0f;
        float meas_pos = roundf(true_pos / quant_step) * quant_step;

        /* Моделювання часового джиттера таймера ±2% */
        float jitter = ((float)rand() / (float)RAND_MAX - 0.5f) * 0.04f * dt_nominal;
        float dt = dt_nominal + jitter;

        /* 1. Наївна зворотна різниця */
        float naive_vel = (step == 0) ? 0.0f : (meas_pos - prev_meas) / dt;
        prev_meas = meas_pos;

        /* 2. Фільтр Тастіна */
        float tustin_vel = tustin2_update(&tustin, meas_pos, dt);

        /* 3. Спостерігач Tracking */
        track_diff_update(&track, meas_pos, dt);
        float track_vel = track.vel;

        if (step > 100) { /* пропуск перехідного процесу */
            float err_naive = fabsf(naive_vel - true_vel);
            float err_tustin = fabsf(tustin_vel - true_vel);
            float err_track = fabsf(track_vel - true_vel);

            if (err_naive > peak_naive_err)   peak_naive_err = err_naive;
            if (err_tustin > peak_tustin_err) peak_tustin_err = err_tustin;
            if (err_track > peak_track_err)   peak_track_err = err_track;
        }
    }

    printf("=== Результати тестування чисельного диференціювання ===\n");
    printf("Наївна різниця (Δx/Δt):  пікова похибка = %.2f рад/с\n", peak_naive_err);
    printf("Фільтр Тастіна (20 Гц):   пікова похибка = %.2f рад/с\n", peak_tustin_err);
    printf("Спостерігач Alpha-Beta-Gamma: пікова похибка = %.2f рад/с\n", peak_track_err);
}
```
```cpp
#include <cmath>
#include <iostream>
#include <numbers>
#include <random>

void run_differentiator_benchmark_cpp() {
    TrackingDifferentiator track({.alpha = 0.45f, .beta = 0.15f, .gamma = 0.02f, .max_acceleration = 5000.0f});
    TustinDifferentiator2nd tustin(20.0f);

    constexpr float dt_nominal = 0.001f;
    constexpr float freq = 2.0f;
    constexpr float pi = std::numbers::pi_v<float>;

    float prev_meas = 0.0f;
    float peak_naive_err = 0.0f;
    float peak_tustin_err = 0.0f;
    float peak_track_err = 0.0f;

    std::mt19937 gen(42);
    std::uniform_real_distribution<float> jitter_dist(-0.02f * dt_nominal, 0.02f * dt_nominal);

    for (int step = 0; step < 2000; ++step) {
        const float t = static_cast<float>(step) * dt_nominal;
        const float true_pos = std::sin(2.0f * pi * freq * t);
        const float true_vel = 2.0f * pi * freq * std::cos(2.0f * pi * freq * t);

        constexpr float quant_step = 2.0f / 4096.0f;
        const float meas_pos = std::round(true_pos / quant_step) * quant_step;
        const float dt = dt_nominal + jitter_dist(gen);

        const float naive_vel = (step == 0) ? 0.0f : (meas_pos - prev_meas) / dt;
        prev_meas = meas_pos;

        const float tustin_vel = tustin.update(meas_pos, dt);

        track.update(meas_pos, dt);
        const float track_vel = track.velocity();

        if (step > 100) {
            peak_naive_err = std::max(peak_naive_err, std::abs(naive_vel - true_vel));
            peak_tustin_err = std::max(peak_tustin_err, std::abs(tustin_vel - true_vel));
            peak_track_err = std::max(peak_track_err, std::abs(track_vel - true_vel));
        }
    }

    std::cout << "=== Результати тестування чисельного диференціювання (C++20) ===\n";
    std::cout << "Наївна різниця (Δx/Δt):  пікова похибка = " << peak_naive_err << " рад/с\n";
    std::cout << "Фільтр Тастіна (20 Гц):   пікова похибка = " << peak_tustin_err << " рад/с\n";
    std::cout << "Спостерігач Alpha-Beta-Gamma: пікова похибка = " << peak_track_err << " рад/с\n";
}
```
:::

---

### 5. Практичні висновки та інженерні рекомендації

1. **Ініціалізація та плавний пуск (Cold Start):**
   При першому ввімкненні приладу початковий стан спостерігача не повинен дорівнювати нулю, якщо виміряне положення вже має певне зміщення `x_0 ≠ 0`. Спроба стартувати з нуля спричинить миттєву похибку `residual = x_0`, що згенерує фальшивий ударний стрибок швидкості `v = β · x_0 / dt`. Виклик функції `track_diff_reset(initial_pos)` у першому циклі або перевірка прапорця `initialized` гарантує плавний безударний запуск контуру керування.

2. **Вибір частоти зрізу фільтра низьких частот `f_cutoff`:**
   Частоту зрізу обирають на основі максимальної смуги пропускання механічного контуру керування (зазвичай у 5–10 разів вище бажаної частоти зрізу контуру швидкості, але значно нижче резонансної частоти механіки та частоти дискретизації Найквіста). Занадто низька частота зрізу створює небезпечний фазовий зсув `φ = -arctan(f / f_cutoff)`, що веде до автоколивань привода.

3. **Вибір коефіцієнтів спостерігача `α, β, γ`:**
   Коефіцієнти спостерігача пов'язані з власною частотою `ω_n` та коефіцієнтом демпфування `ζ` дискретної системи:
   - При високому рівні шуму квантування обирають менші значення `α = 0.3…0.5`, `β = 0.05…0.15`, що забезпечує глибоку фільтрацію;
   - При високій динаміці руху збільшують `α = 0.6…0.8`, `β = 0.2…0.4` для запобігання запізненню фази при різких прискореннях.

4. **Захист від ділення на нуль при джиттері:**
   Якщо мікроконтролер пропустив переривання таймера або обробник викликався двічі з однаковим відліком системного таймера `micros()`, різниця `dt` може дорівнювати нулю. Ділення на нуль у системі реального часу призводить до генерації `+Inf` або `NaN`, що виводить регулятор із ладу та спричиняє аварійне відключення привода. Перевірка `if (dt <= 1e-6f)` є обов'язковою у першому рядку функції оновлення.

5. **Обробка переривань та апаратна синхронізація:**
   Для мінімізації джиттера `dt` зчитування енкодера та виклик диференціатора слід прив'язувати до апаратного тригера таймера або DMA-перенесення. Це усуває програмні затримки диспетчеризації операційної системи реального часу (RTOS).

6. **Обчислювальна складність на ARM Cortex-M:**
   - Алгоритм спостерігача займає менше 40 тактів процесора на ядрі Cortex-M4 з апаратним блоком FPU, що становить менше 0.05% завантаження при частоті виклику 1 кГц (при тактовій частоті 168 МГц).
   - Повна відсутність динамічного виділення пам'яті гарантує детермінізм часу виконання та надійність у критичних системах реального часу за стандартом MISRA C.
   - Для мікроконтролерів без апаратного блоку FPU (наприклад, Cortex-M0/M3) алгоритм легко масштабується у фіксовану кому `Q15` або `Q31`, де операції ділення на `dt` замінюються множенням на заздалегідь підрахований обернений коефіцієнт `inv_dt`.
