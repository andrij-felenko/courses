# ⚙️ Симуляція розділення ізотопів: Мас-спектрометрія та каскад газових центрифуг

Розділення ізотопів — одна з найскладніших та найважливіших фізико-технічних задач ядерної фізики, ядерної енергетики та хімічної інженерії. Оскільки всі ізотопи даного хімічного елемента мають тотожний заряд ядра `Z` і абсолютно однакову структуру електронних оболонок, їхні хімічні властивості є практично ідентичними. Класичні хімічні методи (фракційна кристалізація, екстракція, осадження) є полностью недієвими для промислового збагачення важких елементів.

Промислове та лабораторне розділення ізотопів спирається на дрібні відмінності в масах атомних ядер `Δm` за допомогою двох принципово різних фізичних механізмів:
1. **Електромагнітного розділення іонів у магнітному полі (мас-спектрометрія та калутрони):** пучок прискорених іонів відхиляється силою Лоренца, причому важчі іони описують колові траєкторії більшого радіуса, ніж легкі. Це забезпечує високу чистоту відокремлення за один прохід, але володіє вкрай низькою продуктивністю та колосальними енерговитратами.
2. **Багатоступеневого збагачувального каскаду газових центрифуг:** газова суміш (наприклад, гексафлуорид урану `UF₆`) піддається впливу надвисокого відцентрового поля в роторі центрифуги, що обертається зі швидкістю до 100 000 обертів за хвилину. Важчий ізотоп `²³⁸UF₆` концентрується біля периферійної стінки ротора, тоді як легший ізотоп `²³⁵UF₆` збагачується біля осі обертання.

У цій вставці наведено чисельну симуляцію обох технологічних процесів: розрахунок просторового розділення іонів на колекторній пластині мас-спектрометра та чисельне моделювання протиточного каскаду газових центрифуг.

---

### Фізико-математична модель

#### 1. Електромагнітне розділення іонів
У мас-спектрометрі секторального типу або калутроні пучок однократно іонізованих атомів (`q = e`) спочатку прискорюється в електричному полі з напругою `U`. Кінетична енергія, набута іоном під дією прискорювального поля, дорівнює:

```
1/2 · m · v² = q · U  ⇒  v = √((2 · q · U) / m)
```

Після цього іони пролітають крізь селектор швидкостей (фільтр Віна), де на них діють взаємно перпендикулярні електричне `E` та магнітне `B_0` поля, що пропускає лише частинки з строго фіксованою швидкістю `v = E / B_0`.

Далі пучок входить у область однорідного аналітичного магнітного поля `B`, спрямованого перпендикулярно до площини руху. Сила Лоренца `F_L = q · v · B` надає іону центрострімкого прискорення `m · v² / r`. Зрівнюючи ці сили, отримуємо радіус колової траєкторії іона `r`:

```
r = (m · v) / (q · B) = 1/B · √((2 · m · U) / q)
```

При повороті пучка іонів на 180° (класична схема мас-спектрографа Демпстера) відстань `Δx` між центрами плям двох ізотопів з масами `m_1` та `m_2` на колекторній пластині дорівнює подвійній різниці радіусів траєкторій:

```
Δx = 2 · (r_2 - r_1) = 2/B · √(2 · U / q) · (√m_2 - √m_1)
```

Роздільна здатність мас-спектрометра `R` визначається як відношення середньої маси до мінімальної розділюваної різниці мас `Δm`:

```
R = m / Δm = (m_1 + m_2) / (2 · |m_2 - m_1|)
```

#### 2. Протиточний каскад газових центрифуг
У циліндричному роторі газової центрифуги радіусом `r_rot`, що обертається з кутовою швидкістю `ω`, на молекули газу діє гігантське центробіжне прискорення `a = ω² · r_rot` (що в сотні тисяч разів перевищує прискорення вільного падіння `g`).

Одноступеневий фактор розділення `α` визначається рівноважним барометричним розподілом густини газів у відцентровому полі:

```
α = e^( (Δm · ω² · r_rot²) / (2 · R_gas · T) ) = e^( (Δm · v_periph²) / (2 · R_gas · T) )
```

де `Δm = m(²³⁸UF₆) - m(²³⁵UF₆) = 0.003 кг / моль`, `v_periph = ω · r_rot` — периферійна лінійна швидкість ротора, `R_gas = 8.314 Дж / (моль · К)`.

Оскільки одноступеневий коефіцієнт збагачення є дуже малим (`α ≈ 1.005...1.015`), центрифуги об'єднують у послідовно-паралельний **збагачувальний каскад**. 

Матеріальний баланс потоків сировини `F` (Feed), збагаченого продукту `P` (Product) та збідненого відвалу `W` (Tails):

```
F = P + W                                 [загальний масовий баланс]
F · z_f = P · y_p + W · x_w              [баланс цільового ізотопу 235U]
```

де `z_f`, `y_p`, `x_w` — мольні частки ізотопу `²³⁵U` відповідно у вхідній сировині, готовому продукті та відвалі.

Мінімальна кількість послідовних ступенів каскаду `N_min` обчислюється за рівнянням Фенске:

```
N_min = ln[ (y_p / (1 - y_p)) / (x_w / (1 - x_w)) ] / ln(α)
```

Частка відбору готового продукту від відносного вхідного потоку `P / F`:

```
P / F = (z_f - x_w) / (y_p - x_w)
```

Обсяг роздільної роботи, виражений в Одиницях Роботи Розділення (*Separative Work Units, SWU*), визначається через потенціальну функцію цінності `V(x)`:

```
V(x) = (2 x - 1) · ln(x / (1 - x))
SWU = P · V(y_p) + W · V(x_w) - F · V(z_f)
```

#### 3. Енергетика та порівняльний аналіз технологій
Фізична ефективність розділення ізотопів кардинально різниться між технологіями. 

У газодифузійному меді для стискання мільйонів кубометрів газу `UF₆` крізь тисячі дрібнопористих мембран на 1 SWU витрачається близько `2400...3000 кВт·год` електроенергії. 

У технології газового центрифугування обертання роторів на магнітних підвісах у глибокому вакуумі вимагає лише `50...60 кВт·год` на 1 SWU (що в 50 разів ефективніше за газову дифузію). 

Лазерний метод (SILEX / AVLIS) теоретично дозволяє знизити енерговитрати ще в 5 разів завдяки вибірковому збудженню лише молекул `²³⁵UF₆` квантами лазерного світла з настроєною довжиною хвилі `16 мкм`.

Така драматична різниця пояснюється тим, що електромагнітні та дифузійні методи дають масовий вихід пропорційно загальному об'єму газу, тоді як відцентровий та лазерний методи діють безпосередньо на мікроскопічний дефект маси або квантовий спектральний зсув цільового ізотопу.

---

### Опис програмного коду

Нижче наведено чисельний симулятор розділення ізотопів мовами C та C++. 

Код виконує три ключові фізичні розрахунки:
1. Для електромагнітного сепаратора розраховуються кінетична швидкість іонів у магнітному полі, радіуси траєкторій легкого та важкого ізотопів, геометрична відстань між колекторними кишенями у міліметрах та роздільна здатність `m / Δm`.
2. Для ротора газової центрифуги обчислюється периферійна швидкість ротора у м/с, одноступеневий коефіцієнт збагачення `α` за квантово-статистичним барометричним розподілом та мінімальна кількість збагачувальних ступенів каскаду за рівнянням Фенске.
3. Програма обчислює відносний масовий вихід продукту `P / F`, показавши, скільки кілограмів природного урану необхідно переробити для одержання 1 кг ядерного палива з різними ступенями збагачення (енергетичний уран 4.5% `²³⁵U` проти високозбагаченого збройового урану 90% `²³⁵U`).

Структура C++20 коду використовує шаблонний тип `std::expected` з переліком помилок `SimulationError` для безпечної обробки крайових нефізичних параметрів (від'ємні напруги, нульові оберти ротора, неможливі границі концентрації продукту) без використання повільних винятків.

:::tabs
```c
/* c — Симуляція мас-спектрометричного розділення та центрифужного каскаду */
#include <stdio.h>
#include <math.h>

#define ELEM_CHARGE 1.602176634e-19
#define AMU_TO_KG   1.660539066e-27
#define GAS_CONST   8.314462618

typedef struct {
    double mass_amu_1;    /* Маса легкого ізотопу (а.о.м.) */
    double mass_amu_2;    /* Маса важкого ізотопу (а.о.м.) */
    double voltage_v;     /* Прискорювальна напруга U (В) */
    double magnetic_b_t;  /* Магнітна індукція B (Тл) */
} em_separator_params_t;

typedef struct {
    double radius_m1;     /* Радіус траєкторії першого ізотопу (м) */
    double radius_m2;     /* Радіус траєкторії другого ізотопу (м) */
    double separation_mm; /* Відстань між плямами на колекторі (мм) */
    double resolution;    /* Роздільна здатність m / delta_m */
} em_separator_result_t;

typedef struct {
    double delta_m_kg;    /* Молярна різниця мас (кг/моль) */
    double rotor_radius_m;/* Радіус ротора центрифуги (м) */
    double rpm;           /* Оберти за хвилину (об/хв) */
    double temp_kelvin;   /* Температура газу (К) */
    double feed_fraction; /* Частка 235U у сировині (z_f) */
    double prod_fraction; /* Бажана частка 235U у продукті (y_p) */
    double tail_fraction; /* Частка 235U у відвалі (x_w) */
} cascade_params_t;

typedef struct {
    double alpha_factor;  /* Коефіцієнт розділення одного ступеня */
    double v_peripheral;  /* Периферійна швидкість ротора (м/с) */
    double min_stages;    /* Мінімальна кількість ступенів N_min */
    double product_flow;  /* Відносний вихід продукту P/F */
} cascade_result_t;

int simulate_em_separator(const em_separator_params_t* p, em_separator_result_t* res) {
    if (!p || !res || p->magnetic_b_t <= 0.0 || p->voltage_v <= 0.0) {
        return -1;
    }

    double m1_kg = p->mass_amu_1 * AMU_TO_KG;
    double m2_kg = p->mass_amu_2 * AMU_TO_KG;

    res->radius_m1 = (1.0 / p->magnetic_b_t) * sqrt((2.0 * m1_kg * p->voltage_v) / ELEM_CHARGE);
    res->radius_m2 = (1.0 / p->magnetic_b_t) * sqrt((2.0 * m2_kg * p->voltage_v) / ELEM_CHARGE);

    res->separation_mm = 2.0 * (res->radius_m2 - res->radius_m1) * 1000.0;
    res->resolution = (p->mass_amu_1 + p->mass_amu_2) / (2.0 * fabs(p->mass_amu_2 - p->mass_amu_1));

    return 0;
}

int simulate_cascade(const cascade_params_t* p, cascade_result_t* res) {
    if (!p || !res || p->rpm <= 0.0 || p->rotor_radius_m <= 0.0) {
        return -1;
    }

    double omega = (p->rpm * 2.0 * M_PI) / 60.0;
    res->v_peripheral = omega * p->rotor_radius_m;

    /* alpha = exp( (delta_m * v_periph^2) / (2 * R * T) ) */
    double exponent = (p->delta_m_kg * res->v_peripheral * res->v_peripheral) / (2.0 * GAS_CONST * p->temp_kelvin);
    res->alpha_factor = exp(exponent);

    /* Рівняння Фенске: N_min */
    double num = (p->prod_fraction / (1.0 - p->prod_fraction)) / (p->tail_fraction / (1.0 - p->tail_fraction));
    res->min_stages = log(num) / log(res->alpha_factor);

    /* Відносний вихід продукту P/F = (z_f - x_w) / (y_p - x_w) */
    res->product_flow = (p->feed_fraction - p->tail_fraction) / (p->prod_fraction - p->tail_fraction);

    return 0;
}

int main(void) {
    printf("=== СИМУЛЯЦІЯ РОЗДІЛЕННЯ ІЗОТОПІВ (C) ===\n\n");

    /* 1. Мас-спектрометр для ізотопів Урану 235U та 238U */
    em_separator_params_t em_p = {
        .mass_amu_1 = 235.0439,
        .mass_amu_2 = 238.0507,
        .voltage_v = 10000.0,    /* 10 кВ */
        .magnetic_b_t = 0.5      /* 0.5 Тл */
    };
    em_separator_result_t em_res;

    if (simulate_em_separator(&em_p, &em_res) == 0) {
        printf("--- Електромагнітний розділювач (180 deg) ---\n");
        printf("Радіус 235U: %.4f м\n", em_res.radius_m1);
        printf("Радіус 238U: %.4f м\n", em_res.radius_m2);
        printf("Просторове розділення на фокусі (2*Delta_r): %.2f мм\n", em_res.separation_mm);
        printf("Роздільна здатність m / Delta_m: %.1f\n\n", em_res.resolution);
    }

    /* 2. Газова центрифуга для збагачення Урану */
    cascade_params_t cas_p = {
        .delta_m_kg = 0.003,       /* 3 г/моль між 238UF6 та 235UF6 */
        .rotor_radius_m = 0.15,    /* 15 см */
        .rpm = 90000.0,            /* 90,000 об/хв */
        .temp_kelvin = 320.0,      /* 47 °C */
        .feed_fraction = 0.0072,   /* Природний уран 0.72% 235U */
        .prod_fraction = 0.045,    /* Енергетичний уран 4.5% 235U */
        .tail_fraction = 0.002     /* Відвал 0.2% 235U */
    };
    cascade_result_t cas_res;

    if (simulate_cascade(&cas_p, &cas_res) == 0) {
        printf("--- Каскад газових центрифуг (UF6) ---\n");
        printf("Периферійна швидкість ротора: %.1f м/с\n", cas_res.v_peripheral);
        printf("Фактор розділення 1 ступеня (alpha): %.5f\n", cas_res.alpha_factor);
        printf("Мінімальна кількість ступенів N_min: %.1f\n", cas_res.min_stages);
        printf("Вихід продукту P/F: %.4f (%.2f%% від входу)\n", cas_res.product_flow, cas_res.product_flow * 100.0);
    }

    return 0;
}
```
```cpp
// cpp — Ідіоматична симуляція розділення ізотопів на C++20
#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <vector>
#include <iomanip>

namespace IsotopePhysics {

constexpr double kElemCharge = 1.602'176'634e-19; // Кл
constexpr double kAmuToKg    = 1.660'539'066e-27; // кг
constexpr double kGasConst   = 8.314'462'618;     // Дж/(моль·К)

enum class SimulationError {
    InvalidParameter,
    NonPhysicalValues
};

struct EMSeparatorParams {
    double massAmu1{235.0439};
    double massAmu2{238.0507};
    double voltageV{10000.0};
    double magneticBT{0.5};
};

struct EMSeparatorResult {
    double radiusM1{0.0};
    double radiusM2{0.0};
    double separationMm{0.0};
    double resolution{0.0};
};

struct CascadeParams {
    double deltaMkg{0.003};
    double rotorRadiusM{0.15};
    double rpm{90000.0};
    double tempKelvin{320.0};
    double feedFraction{0.0072};
    double prodFraction{0.045};
    double tailFraction{0.002};
};

struct CascadeResult {
    double vPeripheral{0.0};
    double alphaFactor{0.0};
    double minStages{0.0};
    double productFlowRatio{0.0};
};

class IsotopeSeparatorSimulator {
public:
    [[nodiscard]] static std::expected<EMSeparatorResult, SimulationError> 
    simulateEM(const EMSeparatorParams& p) noexcept {
        if (p.magneticBT <= 0.0 || p.voltageV <= 0.0 || p.massAmu1 <= 0.0 || p.massAmu2 <= 0.0) {
            return std::unexpected(SimulationError::InvalidParameter);
        }

        const double m1Kg = p.massAmu1 * kAmuToKg;
        const double m2Kg = p.massAmu2 * kAmuToKg;

        EMSeparatorResult res;
        res.radiusM1 = (1.0 / p.magneticBT) * std::sqrt((2.0 * m1Kg * p.voltageV) / kElemCharge);
        res.radiusM2 = (1.0 / p.magneticBT) * std::sqrt((2.0 * m2Kg * p.voltageV) / kElemCharge);
        res.separationMm = 2.0 * std::abs(res.radiusM2 - res.radiusM1) * 1000.0;
        res.resolution = (p.massAmu1 + p.massAmu2) / (2.0 * std::abs(p.massAmu2 - p.massAmu1));

        return res;
    }

    [[nodiscard]] static std::expected<CascadeResult, SimulationError> 
    simulateCascade(const CascadeParams& p) noexcept {
        if (p.rpm <= 0.0 || p.rotorRadiusM <= 0.0 || p.tempKelvin <= 0.0 ||
            p.prodFraction <= p.feedFraction || p.feedFraction <= p.tailFraction) {
            return std::unexpected(SimulationError::InvalidParameter);
        }

        const double omega = (p.rpm * 2.0 * std::numbers::pi) / 60.0;
        CascadeResult res;
        res.vPeripheral = omega * p.rotorRadiusM;

        const double exponent = (p.deltaMkg * res.vPeripheral * res.vPeripheral) / (2.0 * kGasConst * p.tempKelvin);
        res.alphaFactor = std::exp(exponent);

        const double FenskeRatio = (p.prodFraction / (1.0 - p.prodFraction)) / 
                                   (p.tailFraction / (1.0 - p.tailFraction));
        res.minStages = std::log(FenskeRatio) / std::log(res.alphaFactor);
        res.productFlowRatio = (p.feedFraction - p.tailFraction) / (p.prodFraction - p.tailFraction);

        return res;
    }
};

} // namespace IsotopePhysics

int main() {
    using namespace IsotopePhysics;

    std::cout << "=== СИМУЛЯЦІЯ РОЗДІЛЕННЯ ІЗОТОПІВ (C++20) ===\n\n";

    // 1. Електромагнітне розділення
    EMSeparatorParams emParams{.massAmu1 = 235.0439, .massAmu2 = 238.0507, .voltageV = 10000.0, .magneticBT = 0.5};
    if (auto res = IsotopeSeparatorSimulator::simulateEM(emParams); res.has_value()) {
        std::cout << "--- Електромагнітний розділювач ---\n"
                  << std::fixed << std::setprecision(4)
                  << "Радіус 235U: " << res->radiusM1 << " м\n"
                  << "Радіус 238U: " << res->radiusM2 << " м\n"
                  << std::setprecision(2)
                  << "Просторове розділення: " << res->separationMm << " мм\n"
                  << "Роздільна здатність m/Δm: " << res->resolution << "\n\n";
    }

    // 2. Центрифужний каскад
    CascadeParams cascadeParams{
        .deltaMkg = 0.003,
        .rotorRadiusM = 0.15,
        .rpm = 90000.0,
        .tempKelvin = 320.0,
        .feedFraction = 0.0072,
        .prodFraction = 0.045,
        .tailFraction = 0.002
    };

    if (auto res = IsotopeSeparatorSimulator::simulateCascade(cascadeParams); res.has_value()) {
        std::cout << "--- Збагачувальний каскад (UF6) ---\n"
                  << std::fixed << std::setprecision(1)
                  << "Периферійна швидкість ротора: " << res->vPeripheral << " м/с\n"
                  << std::setprecision(5)
                  << "Фактор збагачення α: " << res->alphaFactor << "\n"
                  << std::setprecision(1)
                  << "Необхідно ступенів N_min: " << res->minStages << "\n"
                  << std::setprecision(4)
                  << "Вихід продукту P/F: " << res->productFlowRatio 
                  << " (" << res->productFlowRatio * 100.0 << "%)\n";
    }

    return 0;
}
```
:::
