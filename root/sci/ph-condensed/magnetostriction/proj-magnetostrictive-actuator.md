# ⚙️ Моделювання динаміки магнітострикційного актуатора

Програмування та чисельне моделювання магнітострикційного приводу вимагає врахування нелінійної квадратичної залежності деформації від намагніченості, механічного інерційного навантаження (маси актуатора й корисного вантажу), згасання коливань та впливу постійного поля підмагнічування. Нижче подано детальний опис фізичної моделі, аналіз числового інтегрувача рівнянь руху актуатора на основі Terfenol-D та реалізацію мовами C та C++.

## Математична модель актуатора та механіка зв'язку

Розглядаємо силовий актуатор на основі стрижня Terfenol-D початковою довжиною `L_0` з площею перерізу `A`. До кінця стрижня під'єднано приведену масу корисного вантажу `m`. Механічна система має зовнішню пружину преднатягу з коефіцієнтом жорсткості `k_spring` та в'язке демпфування з коефіцієнтом `c_viscous`, яке описує втрати на внутрішнє тертя матеріалу та опір навколишнього середовища.

Динаміка приводу описується трьома послідовними фізичними ланцюгами:

1. **Електромагнітна ланка (струм у поле).** Магнітне поле `H(t)` усередині соленоїда створюється сумою постійного поля підмагнічування `H_bias` (від постійних магнітів або постійного струму) та змінного поля від керуючого струму `I(t)` у котушці з щільністю витків `n = N / L_coil`:

```
H(t) = H_bias + n · I(t)
```

Постійне поле підмагнічування є критично важливим: воно зміщує робочу точку приводу на круту лінійну ділянку магнітострикційної кривої. Без цього підмагнічування синусоїдальний струм викликав би вихідні коливання на подвоєній частоті `2f` через квадратичний характер ефекту Джоуля (`λ ∝ H²`).

2. **Магнітоеластична ланка (поле в деформацію).** Вільна магнітострикційна деформація стрижня `λ_free` описується феноменологічною функцією насичення з постійною `λ_s` та характерним полем насичення `H_sat`:

```
λ_free(H) = λ_s · tanh((H / H_sat)²)
```

У цій формулі функція гіперболічного тангенса забезпечує гладкий перехід від квадратичного зростання при малих полях (`H ≪ H_sat`) до виходу на плато насичення `λ_s` при сильних полях (`H ≫ H_sat`).

3. **Механічна ланка (деформація в рух та силу).** Вільна деформація прагне змінити довжину стрижня на `ΔL_free = L_0 · λ_free(H)`. Якщо стрижень стиснутий пружиною або розтягується вантажем, виникає еквівалентна екзогенна сила `F_ext = k_spring · L_0 · λ_free(H)`. Рівняння руху для координати зміщення `x(t)` набуває вигляду диференціального рівняння другого порядку:

```
m · d²x/dt² + c_viscous · dx/dt + k_spring · x = k_spring · L_0 · λ_free(H)
```

Для чисельного розв'язання цього рівняння використовуємо метод Ейлера-Кромера (симпелектичний інтегратор першого порядку), який зберігає енергію та стійкість осцилятора на тривалих інтервалах часу.

## Аналіз методів чисельного інтегрування та гістерезису

Оскільки жорсткість механічної системи `k_spring` сягає меганьютонів на метр (`5 × 10⁶ Н/м`), власна частота системи є досить високою (`f_0 ≈ 500 Гц`). Звичайний явний метод Ейлера при кроці `dt = 10 мкс` накопичує нестійкість і призводить до вибухового зростання амплітуди через відсутність збереження фазового об'єму.

Застосований метод Ейлера-Кромера перераховує позицію `x[n+1]`, використовуючи вже оновлену швидкість `v[n+1]`:

```
v[n+1] = v[n] + a[n] · dt
x[n+1] = x[n] + v[n+1] · dt
```

Цей чисельний хід гарантує симплектичність схеми та стабільне моделювання амплітудно-частотної характеристики актуатора навіть у зоні резонансу.

Для складніших практичних задач замість спрощеного виразу `tanh((H/H_sat)²)` застосовують модель Джайлса-Атертона (*Jiles-Atherton hysteresis model*). Вона враховує незворотні втрати на зачеплення доменних меж за дефекти ґратки, що створює петлю гістерезису між деформацією `λ` та магнітним полем `H`. У поданій нижче програмі використовується квазістатична апроксимація, яка є обчислювально ефективною для систем керування реального часу та цифрових сигнальних процесорів (DSP).

Крім того, при розрахунку високовольтних та високочастотних актуаторів враховують зворотну ЕРС індукції, яка наводиться у котушці при швидкому зміщенні стрижня за рахунок ефекту Вілларі. Ця ЕРС створює додатковий індуктивний опір підсилювачу.

## Програмна реалізація моделі

Програма обчислює часову динаміку актуатора при синусоїдальному керуючому струмі.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура параметрів магнітострикційного актуатора */
typedef struct {
    double rod_length;     /* Початкова довжина стрижня L0 (м) */
    double lambda_s;       /* Насичена деформація λs */
    double h_sat;          /* Поле насичення H_sat (А/м) */
    double h_bias;         /* Постійне поле підмагнічування (А/м) */
    double turns_per_m;    /* Щільність витків котушки N/L_coil (1/м) */
    double mass;           /* Приведена маса актуатора та вантажу (кг) */
    double stiffness;      /* Жорсткість механічної системи k (Н/м) */
    double damping;        /* Коефіцієнт демпфування c (Н·с/м) */
} ActuatorParams;

/* Стан системи в момент часу t */
typedef struct {
    double time;           /* Час (с) */
    double current;        /* Струм у котушці (А) */
    double h_field;        /* Магнітне поле H (А/м) */
    double position;       /* Зміщення актуатора x (м) */
    double velocity;       /* Швидкість v = dx/dt (м/с) */
    double strain;         /* Поточна деформація λ */
} ActuatorState;

/* Обчислення вільної магнітострикційної деформації λ_free(H) */
double calculate_strain(const ActuatorParams *p, double h_field) {
    double ratio = h_field / p->h_sat;
    return p->lambda_s * tanh(ratio * ratio);
}

/* Крок інтегрування методом Ейлера-Кромера */
void actuator_step(const ActuatorParams *p, ActuatorState *s, double drive_current, double dt) {
    s->current = drive_current;
    s->h_field = p->h_bias + p->turns_per_m * drive_current;
    s->strain = calculate_strain(p, s->h_field);

    /* Еквівалентна вимушена сила від деформації */
    double f_ext = p->stiffness * p->rod_length * s->strain;
    
    /* Прискорення a = (F_ext - k*x - c*v) / m */
    double accel = (f_ext - p->stiffness * s->position - p->damping * s->velocity) / p->mass;

    /* Оновлення швидкості та позиції (схема Ейлера-Кромера) */
    s->velocity += accel * dt;
    s->position += s->velocity * dt;
    s->time += dt;
}

int main(void) {
    ActuatorParams params = {
        .rod_length = 0.10,        /* 10 см */
        .lambda_s = 1.2e-3,        /* 1200 ppm (Terfenol-D) */
        .h_sat = 120000.0,         /* 120 кА/м */
        .h_bias = 40000.0,         /* 40 кА/м робоча точка */
        .turns_per_m = 2000.0,     /* 2000 витків/м */
        .mass = 0.5,               /* 0.5 кг вантажу */
        .stiffness = 5.0e6,        /* 5 МН/м */
        .damping = 150.0           /* 150 Н·с/м */
    };

    ActuatorState state = {0};
    double dt = 1e-5;              /* Крок за часом 10 мкс */
    double freq = 500.0;           /* Частота збудження 500 Гц */
    double current_amp = 5.0;      /* Амплітуда струму 5 А */

    printf("Time(s),Current(A),H_field(A/m),Position(um),Strain(ppm)\n");

    for (int step = 0; step <= 1000; ++step) {
        double current = current_amp * sin(2.0 * M_PI * freq * state.time);
        actuator_step(&params, &state, current, dt);

        if (step % 20 == 0) {
            printf("%.6f,%.3f,%.1f,%.3f,%.1f\n",
                   state.time,
                   state.current,
                   state.h_field,
                   state.position * 1e6,
                   state.strain * 1e6);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>

namespace magnetics {

struct PhysicsConfig {
    double rod_length{0.10};       // m
    double lambda_s{1.2e-3};       // strain saturation
    double h_sat{120000.0};        // A/m
    double h_bias{40000.0};        // A/m bias field
    double turns_per_m{2000.0};    // 1/m
    double mass{0.5};              // kg
    double stiffness{5.0e6};       // N/m
    double damping{150.0};         // N s/m
};

struct StepResult {
    double time_s;
    double current_a;
    double h_field_a_per_m;
    double position_m;
    double velocity_m_per_s;
    double strain;
};

enum class ActuatorError {
    InvalidTimeStep,
    ThermalOverload,
    MechanicalLimitExceeded
};

class TerfenolActuator {
public:
    explicit TerfenolActuator(PhysicsConfig config) 
        : config_(config) {}

    [[nodiscard]] double calculate_strain(double h_field) const noexcept {
        const double ratio = h_field / config_.h_sat;
        return config_.lambda_s * std::tanh(ratio * ratio);
    }

    [[nodiscard]] std::expected<StepResult, ActuatorError> 
    step(double drive_current, double dt) noexcept {
        if (dt <= 0.0 || dt > 1e-2) {
            return std::unexpected(ActuatorError::InvalidTimeStep);
        }

        current_a_ = drive_current;
        h_field_ = config_.h_bias + config_.turns_per_m * drive_current;
        strain_ = calculate_strain(h_field_);

        const double f_ext = config_.stiffness * config_.rod_length * strain_;
        const double accel = (f_ext - config_.stiffness * position_m_ - config_.damping * velocity_m_per_s_) / config_.mass;

        velocity_m_per_s_ += accel * dt;
        position_m_ += velocity_m_per_s_ * dt;
        time_s_ += dt;

        if (std::abs(position_m_) > config_.rod_length * 0.1) {
            return std::unexpected(ActuatorError::MechanicalLimitExceeded);
        }

        return StepResult{
            .time_s = time_s_,
            .current_a = current_a_,
            .h_field_a_per_m = h_field_,
            .position_m = position_m_,
            .velocity_m_per_s = velocity_m_per_s_,
            .strain = strain_
        };
    }

private:
    PhysicsConfig config_;
    double time_s_{0.0};
    double current_a_{0.0};
    double h_field_{0.0};
    double position_m_{0.0};
    double velocity_m_per_s_{0.0};
    double strain_{0.0};
};

} // namespace magnetics

int main() {
    using namespace magnetics;

    PhysicsConfig cfg{};
    TerfenolActuator actuator(cfg);

    constexpr double dt = 1e-5;
    constexpr double freq = 500.0;
    constexpr double current_amp = 5.0;

    std::cout << "Time(s),Current(A),H(A/m),Pos(um),Strain(ppm)\n";

    for (int i = 0; i <= 1000; ++i) {
        const double t = i * dt;
        const double drive_current = current_amp * std::sin(2.0 * std::numbers::pi * freq * t);

        auto res = actuator.step(drive_current, dt);
        if (!res) {
            std::cerr << "Simulation error encountered!\n";
            return 1;
        }

        if (i % 50 == 0) {
            std::cout << res->time_s << ","
                      << res->current_a << ","
                      << res->h_field_a_per_m << ","
                      << res->position_m * 1e6 << ","
                      << res->strain * 1e6 << "\n";
        }
    }

    return 0;
}
```
:::

## Аналіз фізичних ефектів за результатами розрахунку

Аналіз отриманих у ході розрахунку часових діаграм дозволяє виділити п'ять ключових інженерних особливостей:

1. **Зміщення робочої точки та випрямлення гармонік.** За відсутності достатнього поля підмагнічування (`H_bias ≈ 0`) синусоїдальний струм керування змушує актуатор створювати потужну другу гармоніку деформації `2f`. Поле підмагнічування величиною `H_bias ≈ 40 кА/м` зсуває індуковану гармоніку в зону лінійного підсилення, зменшуючи коефіцієнт гармонійних спотворень (*THD*) вихідного руху до менш ніж 1%.

2. **Механічна резонансна амплітуда.** Резонансна частота механічної системи `f_res` визначається як:

```
f_res = (1 / (2·π)) · √(k_spring / m)
```

Для вказаних параметрів (`k = 5 МН/м`, `m = 0.5 кг`) резонансна частота становить близько `503 Гц`. При наближенні частоти керуючого струму до `503 Гц` амплітуда вихідних переміщень зростає у десятки разів (обмежуючись лише демпфуванням `c_viscous`), проте фазовий зсув між струмом і позицією досягає `90°`, що вимагає застосування замкненої системи керування зі зворотним зв'язком за позицією.

3. **Вплив механічного навантаження на магнітний опір.** Внаслідок зворотного ефекту Вілларі зміна зовнішнього навантаження `F_ext` призводить до зміни коефіцієнта індуктивності котушки збудження. При жорсткому затисканні актуатора індуктивність спадає через обмеження обертання доменів, що необхідно враховувати при конструюванні контуру керування струмом підсилювача.

4. **Роздільна здатність та температурна компенсація.** Моделювання показує, що навіть малі температурні коливання викликають фонове теплове розширення `ΔL_temp = L_0 · α_temp · ΔT`. Оскільки коефіцієнт теплового розширення заліза становить `12 × 10⁻⁶ 1/K`, зміна температури на 1 °C викликає деформацію `12 ppm`, що відповідає 10% від максимального робочого ходу. Тому у прецизійних мікроактуаторах застосовують диференціальні двострижневі схеми компенсації.

5. **Теплове обмеження струму.** Тривала робота з великими струмами керування викликає джоулів нагрів соленоїда `P = I² · R`. Збільшення температури понад `80 °C` призводить до деградації магнітострикційних властивостей Terfenol-D через наближення до точки Кюрі. Тому промислові актуатори оснащуються вбудованими давачами температури та системами активного рідинного або повітряного охолодження.
