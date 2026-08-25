# ⚙️ Моделювання вентильного перетворювача HVDC

Ця вставка містить розробку, математичне виведення та числове моделювання алгоритму автоматичного керування вентильним перетворювачем лінії постійного струму високої напруги (HVDC). Подано фізичне обґрунтування контуру регулювання, математичні формули дискретизації, порівняльний аналіз архітектури LCC та VSC, а також повні робочі реалізації мовами C та C++ з вичерпним аналізом інженерних пасток, аварійних режимів, збоїв комутації та методів запобігання насиченню інтегратора.

---

### 1. Постановка задачі та фізична модель контуру керування

Головне завдання автоматичного керування підстанцією HVDC — підтримання заданого струму полюса `I_ref` (або активної потужності `P_ref`) при динамічних коливаннях напруги в мережі змінного струму, змінах навантаження та перехідних процесах у лінії.

Для класичного вентильного мосту LCC (*Line-Commutated Converter*) регулювальним органом є **кут відмикання тиристорів `α`** (фазовий зсув імпульсів відкривання відносно точки природного перетину фазних напруг AC).

Зміна кута `α` безпосередньо впливає на середнє значення випрямленої напруги `U_dc`:
- Для випрямляча (`0° ≤ α < 90°`): Збільшення `α` зменшує напругу `U_dc`, що приводить до падіння струму `I_dc`.
- Для інвертора (`90° < α < 180°`): Регулювання здійснюється за допомогою підтримки постійного кута погасання `γ = 180° - α - μ`, де `μ` — кут комутаційного перекриття.

Дискретна система керування повинна на кожному кроці дискретизації `dt` (типово 1–10 мс) виконувати такий цикл розрахунку:
1. Зчитувати виміряний струм полюса `I_dc` та лінійну напругу AC мережі `U_LL`.
2. Обчислювати відхилення (помилку) `e(t) = I_ref - I_dc`.
3. Розраховувати нове значення кута `α` за допомогою пропорційно-інтегрального (ПІ) регулятора.
4. Обмежувати значення `α` в діапазоні `[α_min, α_max]` із застосуванням алгоритму захисту від інтегрального насичення (*Anti-windup*).
5. Розраховувати очікувану напругу мосту `U_dc`, кут комутаційного перекриття `μ` та кут погасання `γ`.
6. Перевіряти критерій аварійного збою комутації: якщо `α > 90°` та `γ < γ_min`, генерувати аварійний сигнал `Commutation Failure`.

---

### 2. Математична модель та алгоритм розрахунку

Дискретизація аналогового контуру регулювання виконується за методом прямого Ейлера або тапецієподібного інтегрування.

#### Дискретний ПІ-регулятор
Помилка регулювання на кроці `k`:
```
e[k] = I_ref - I_dc[k]
```
Сума інтегратора з обмеженням:
```
I_sum[k] = I_sum[k-1] + e[k] · dt
α_calc = α[k-1] - (K_p · e[k] + K_i · I_sum[k])
```
*Примітка:* Знак мінус перед коефіцієнтами зумовлений тим, що для випрямляча збільшення `α` зменшує напругу та струм.

#### Випрямлена напруга та струм DC кола
Ідеальна напруга без навантаження:
```
U_dc0[k] = (3 · √2 / π) · U_LL · cos(α[k])
```
Еквівалентний опір комутації:
```
R_eq = (3 / π) · X_c
```
Струм у DC колі з опором лінії `R_line`:
```
I_dc[k] = U_dc0[k] / (R_line + R_eq)
```
Дійсна напруга DC шини:
```
U_dc[k] = U_dc0[k] - R_eq · I_dc[k]
```

#### Розрахунок комутаційного кута μ та кута погасання γ
З рівняння комутації 6-пульсного мосту:
```
cos(α + μ) = cos(α) - (2 · X_c · I_dc) / (√2 · U_LL)
```
Звідси кут перекриття:
```
μ = acos( cos(α) - (2 · X_c · I_dc) / (√2 · U_LL) ) - α
```
Кут погасання для інвертора:
```
γ = 180° - (α + μ)
```

---

### 3. Структура реалізації та описи функцій

Алгоритм реалізовано у двох варіантах. Варіант мовою C спирається на процедурний підхід із явними структурами даних та передачею вказівників, що відповідає вимогам вбудованих систем реального часу (Firmware/DSP). Варіант мовою C++20 використовує строгу типізацію, ООП-обгортку підстанції, семантику `std::expected` для безпечної обробки аварій без винятків та стандартизовані математичні константи `std::numbers::pi`.

---

### 4. Програмний код симулятора

:::tabs
```c
/* hvdc_converter_sim.c - Моделювання контуру керування HVDC мостом (C99) */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура параметрів HVDC перетворювального мосту */
typedef struct {
    double u_ll_rms;     /* Лінійна напруга AC мережі (В) */
    double x_c;          /* Комутаційний опір трансформатора (Ом) */
    double r_line;       /* Активний опір DC лінії (Ом) */
    double i_ref;        /* Заданий струм полюса (А) */
    double kp;           /* Пропорційний коефіцієнт ПІ-регулятора */
    double ki;           /* Інтегральний коефіцієнт ПІ-регулятора */
    double alpha_min_deg;/* Мінімальний кут відкривання (град) */
    double alpha_max_deg;/* Максимальний кут відкривання (град) */
    double gamma_min_deg;/* Мінімальний кут погасання для інвертора (град) */
} HvdcConfig;

/* Стан контуру керування */
typedef struct {
    double alpha_deg;    /* Поточний кут відкривання тиристорів (град) */
    double integrator;   /* Аккумулятор інтегратора ПІ */
    double u_dc;         /* Поточна напруга DC (В) */
    double i_dc;         /* Поточний струм DC (А) */
    double mu_deg;       /* Кут комутаційного перекриття (град) */
    double gamma_deg;    /* Кут погасання інвертора (град) */
    bool comm_failure;   /* Прапорець збою комутації */
} HvdcState;

/* Ініціалізація стану */
void hvdc_init(HvdcState *state, double initial_alpha) {
    state->alpha_deg = initial_alpha;
    state->integrator = 0.0;
    state->u_dc = 0.0;
    state->i_dc = 0.0;
    state->mu_deg = 0.0;
    state->gamma_deg = 0.0;
    state->comm_failure = false;
}

/* Обчислення кута комутаційного перекриття mu (в радіанах) */
static double calc_commutation_overlap(double u_ll_rms, double x_c, double i_dc, double alpha_rad) {
    double cos_alpha = cos(alpha_rad);
    double drop = (2.0 * x_c * i_dc) / (sqrt(2.0) * u_ll_rms);
    double cos_alpha_mu = cos_alpha - drop;

    if (cos_alpha_mu < -1.0) cos_alpha_mu = -1.0;
    if (cos_alpha_mu > 1.0)  cos_alpha_mu = 1.0;

    double alpha_mu = acos(cos_alpha_mu);
    double mu_rad = alpha_mu - alpha_rad;
    return (mu_rad < 0.0) ? 0.0 : mu_rad;
}

/* Один крок дискретного моделювання контуру (dt в секундах) */
void hvdc_step(const HvdcConfig *cfg, HvdcState *st, double dt) {
    /* 1. Обчислення помилки регулювання струму */
    double err = cfg->i_ref - st->i_dc;

    /* 2. ПІ-регулятор кута alpha */
    st->integrator += err * dt;
    double alpha_calc = st->alpha_deg - (cfg->kp * err + cfg->ki * st->integrator);

    /* Обмеження насичення регулятора (Anti-windup) */
    if (alpha_calc < cfg->alpha_min_deg) {
        alpha_calc = cfg->alpha_min_deg;
        st->integrator -= err * dt;
    } else if (alpha_calc > cfg->alpha_max_deg) {
        alpha_calc = cfg->alpha_max_deg;
        st->integrator -= err * dt;
    }
    st->alpha_deg = alpha_calc;

    /* 3. Фізика мосту: розрахунок U_dc з урахуванням комутаційного падіння */
    double alpha_rad = st->alpha_deg * (M_PI / 180.0);
    double u_dc0 = (3.0 * sqrt(2.0) / M_PI) * cfg->u_ll_rms * cos(alpha_rad);
    double r_eq = (3.0 / M_PI) * cfg->x_c;

    /* Реакція навантаження */
    st->i_dc = u_dc0 / (cfg->r_line + r_eq);
    if (st->i_dc < 0.0) st->i_dc = 0.0;
    st->u_dc = u_dc0 - r_eq * st->i_dc;

    /* 4. Розрахунок комутаційного кута mu та кута погасання gamma */
    double mu_rad = calc_commutation_overlap(cfg->u_ll_rms, cfg->x_c, st->i_dc, alpha_rad);
    st->mu_deg = mu_rad * (180.0 / M_PI);
    st->gamma_deg = 180.0 - (st->alpha_deg + st->mu_deg);

    /* 5. Перевірка аварійної умови збою комутації інвертора */
    if (st->alpha_deg > 90.0 && st->gamma_deg < cfg->gamma_min_deg) {
        st->comm_failure = true;
    } else {
        st->comm_failure = false;
    }
}

int main(void) {
    HvdcConfig cfg = {
        .u_ll_rms = 400000.0,    /* 400 кВ AC */
        .x_c = 15.0,             /* 15 Ом комутаційний опір */
        .r_line = 100.0,         /* 100 Ом опір DC лінії */
        .i_ref = 2000.0,         /* Заданий струм 2000 А */
        .kp = 0.005,
        .ki = 0.05,
        .alpha_min_deg = 5.0,    /* Мін. кут 5° */
        .alpha_max_deg = 150.0,  /* Макс. кут 150° */
        .gamma_min_deg = 15.0    /* Поріг аварії 15° */
    };

    HvdcState state;
    hvdc_init(&state, 30.0);

    printf("=== Симуляція контуру керування HVDC (C99) ===\n");
    printf("Крок |  Alpha (°) |    U_dc (кВ) |    I_dc (А) |   Mu (°) |  Gamma (°) | Стан\n");
    printf("-----+------------+--------------+-------------+----------+------------+------\n");

    double dt = 0.01; /* 10 мс крок */
    for (int step = 1; step <= 10; ++step) {
        hvdc_step(&cfg, &state, dt);
        printf("%4d | %10.2f | %12.2f | %11.1f | %8.2f | %10.2f | %s\n",
               step, state.alpha_deg, state.u_dc / 1000.0, state.i_dc,
               state.mu_deg, state.gamma_deg,
               state.comm_failure ? "АВАРІЯ (CommFail)" : "ОК");
    }

    return 0;
}
```

```cpp
// hvdc_converter_sim.cpp - Моделювання контуру керування HVDC мостом (C++20)
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <expected>
#include <string_view>

namespace hvdc {

struct Config {
    double u_ll_rms{400'000.0};    // Лінійна напруга AC (В)
    double x_c{15.0};              // Комутаційний опір (Ом)
    double r_line{100.0};          // Опір DC лінії (Ом)
    double i_ref{2000.0};          // Уставка струму (А)
    double kp{0.005};              // ПІ-пропорційний коефіцієнт
    double ki{0.05};               // ПІ-інтегральний коефіцієнт
    double alpha_min_deg{5.0};     // Мінімальний кут alpha
    double alpha_max_deg{150.0};   // Максимальний кут alpha
    double gamma_min_deg{15.0};    // Поріг аварії gamma
};

enum class ControlError {
    CommutationFailure,
    Overcurrent,
    VoltageCollapse
};

constexpr std::string_view to_string(ControlError err) noexcept {
    switch (err) {
        case ControlError::CommutationFailure: return "Аварія: збій комутації інвертора";
        case ControlError::Overcurrent:        return "Аварія: струмове перевантаження";
        case ControlError::VoltageCollapse:    return "Аварія: посадка напруги AC";
    }
    return "Невідома помилка";
}

class ConverterStation {
public:
    explicit ConverterStation(Config config, double initial_alpha_deg = 30.0)
        : config_{config}, alpha_deg_{initial_alpha_deg} {}

    struct Status {
        double alpha_deg;
        double u_dc_kv;
        double i_dc_a;
        double mu_deg;
        double gamma_deg;
    };

    // Оновлення стану підстанції на один крок dt (сек)
    [[nodiscard]] std::expected<Status, ControlError> step(double dt) noexcept {
        const double err = config_.i_ref - i_dc_;
        integrator_ += err * dt;

        double alpha_calc = alpha_deg_ - (config_.kp * err + config_.ki * integrator_);
        if (alpha_calc < config_.alpha_min_deg) {
            alpha_calc = config_.alpha_min_deg;
            integrator_ -= err * dt;
        } else if (alpha_calc > config_.alpha_max_deg) {
            alpha_calc = config_.alpha_max_deg;
            integrator_ -= err * dt;
        }
        alpha_deg_ = alpha_calc;

        const double alpha_rad = alpha_deg_ * (std::numbers::pi / 180.0);
        const double u_dc0 = (3.0 * std::numbers::sqrt2 / std::numbers::pi) * config_.u_ll_rms * std::cos(alpha_rad);
        const double r_eq = (3.0 / std::numbers::pi) * config_.x_c;

        i_dc_ = std::max(0.0, u_dc0 / (config_.r_line + r_eq));
        u_dc_ = u_dc0 - r_eq * i_dc_;

        const double mu_rad = calculate_commutation_overlap(alpha_rad);
        mu_deg_ = mu_rad * (180.0 / std::numbers::pi);
        gamma_deg_ = 180.0 - (alpha_deg_ + mu_deg_);

        if (alpha_deg_ > 90.0 && gamma_deg_ < config_.gamma_min_deg) {
            return std::unexpected(ControlError::CommutationFailure);
        }

        return Status{
            .alpha_deg = alpha_deg_,
            .u_dc_kv = u_dc_ / 1000.0,
            .i_dc_a = i_dc_,
            .mu_deg = mu_deg_,
            .gamma_deg = gamma_deg_
        };
    }

private:
    [[nodiscard]] double calculate_commutation_overlap(double alpha_rad) const noexcept {
        const double cos_alpha = std::cos(alpha_rad);
        const double drop = (2.0 * config_.x_c * i_dc_) / (std::numbers::sqrt2 * config_.u_ll_rms);
        double cos_alpha_mu = std::clamp(cos_alpha - drop, -1.0, 1.0);
        return std::max(0.0, std::acos(cos_alpha_mu) - alpha_rad);
    }

    Config config_;
    double alpha_deg_{30.0};
    double integrator_{0.0};
    double u_dc_{0.0};
    double i_dc_{0.0};
    double mu_deg_{0.0};
    double gamma_deg_{0.0};
};

} // namespace hvdc

int main() {
    hvdc::Config config;
    hvdc::ConverterStation station(config, 30.0);

    std::cout << "=== Симуляція контуру керування HVDC (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Крок |  Alpha (°) |    U_dc (кВ) |    I_dc (А) |   Mu (°) |  Gamma (°) | Стан\n";
    std::cout << "-----+------------+--------------+-------------+----------+------------+------\n";

    constexpr double dt = 0.01;
    for (int step = 1; step <= 10; ++step) {
        auto result = station.step(dt);
        if (result) {
            const auto& st = *result;
            std::cout << std::setw(4) << step << " | "
                      << std::setw(10) << st.alpha_deg << " | "
                      << std::setw(12) << st.u_dc_kv << " | "
                      << std::setw(11) << st.i_dc_a << " | "
                      << std::setw(8) << st.mu_deg << " | "
                      << std::setw(10) << st.gamma_deg << " | ОК\n";
        } else {
            std::cout << std::setw(4) << step << " | "
                      << "  ПОМИЛКА: " << hvdc::to_string(result.error()) << '\n';
        }
    }

    return 0;
}
```
:::

---

### 5. Докладний аналіз інженерних пасток та методів захисту

При розробці реальних мікроконтролерних систем керування HVDC інженери стикаються з трьома фундаментальними проблемами:

#### 1. Захист від насичення інтегратора (Anti-Windup)
У разі великого збурення (наприклад, під час короткого замикання в AC мережі) розниця `e = I_ref - I_dc` стає великою. Інтегратор ПІ-регулятора починає швидко накопичувати суму. Коли кут `α` впирається в фізичне обмеження `α_min` (наприклад, 5°), обчислений кут продовжує рости у від'ємну область. Після усунення замикання мережі накопичене значення інтегратора буде секундами утримувати регулятор у насиченні, що спричинить важке надструмове перевантаження. 

У наведеному коді застосовано алгоритм **Anti-windup із зворотним вирахуванням**:
```text
if (alpha_calc < cfg->alpha_min_deg) {
    alpha_calc = cfg->alpha_min_deg;
    st->integrator -= err * dt;  /* Відкочуємо інтеграл */
}
```

#### 2. Динаміка збою комутації інвертора (Commutation Failure)
Коли перетворювач працює в режимі інвертора (`α ≈ 140° ... 150°`), кут погасання `γ = 180° - α - μ` становить всього 15°–20°. Якщо в цей момент у приймальній мережі AC станеться короткочасна посадка напруги `U_LL`, то згідно з рівнянням комутації струм `I_dc` призведе до стрімкого зростання кута комутаційного перекриття `μ`. 

Якщо `μ` зросте на стільки, що `γ` впаде нижче 10°–15°, тиристор, що закривається, не встигне розсмоктати неосновні носії заряду у p-n переходах. Коли напруга на ньому стане позитивною, він самовільно відкриється — виникне коротке замикання плечей мосту. У коді C++ цей стан обробляється через механізм `std::expected` поверненням збою `ControlError::CommutationFailure`.

#### 3. Лінеаризація контуру регулювання (Arc-Cosine Linearization)
Оскільки залежність напруги від кута `U_dc ∝ cos α` є нелінійною, коефіцієнт підсилення контуру регулювання `dU_dc / dα = -1.35 · U_LL · sin α` змінюється втричі в діапазоні від `α = 10°` до `α = 90°`. У промислових системах регулятор вираховує не сам кут `α`, а величина `cos α`, після чого використовується табличний або апаратний арккосинус. Це вирівнює коефіцієнт передачі контуру й забезпечує однакову швидкодію у всьому діапазоні навантажень.

#### 4. Фазова синхронізація через ФАПЧ (PLL)
У реальних підстанціях кут відмикання `α` відраховується від моментів переходу напруги AC через нуль. Оскільки мережева напруга спотворена гармоніками та провалами, для точної фіксації опорного кута використовується трифазна система фазового автопідстроювання частоти (*Phase-Locked Loop*, PLL у dq-координатах). Без PLL вимірювання `α` матиме джиттер у кілька градусів, що викликає появу непарних гармонік у DC струмі.
