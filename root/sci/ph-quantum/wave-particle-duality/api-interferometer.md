# 📋 Інтерфейс розрахунку хвильових і корпускулярних параметрів квантових частинок

Вставка містить специфікацію програмного та розрахункового інтерфейсу для обчислення хвилі де Бройля, фазової й групової швидкостей, браґґівських кутів дифракції та теоретичної межі роздільної здатності електронного мікроскопа.

## 1. Загальний опис інтерфейсу та архітектура модуля

Модуль квантово-хвильового аналізу призначений для обчислення кінематичних та хвильових характеристик квантових частинок у широкому діапазоні енергій. Модуль підтримує як нерелятивістський режим для низькоенергетичних теплових частинок, так і повний лоренц-інваріантний релятивістський режим для високоенергетичних пучків у прискорювачах та електронних мікроскопах.

Математична база модуля спирається на універсальні квантові співвідношення де Бройля, фундаментальні рівняння спеціальної теорії відносності та геометрію дифракції Бреґґа — Вульфа. Модуль надає розробникам надійний C++20 API без використання винятків (exception-free design) з обробкою помилок через типізований контейнер `std::expected`.

Фізичні задачі, які розв'язує модуль:
1. **Обчислення релятивістського та нерелятивістського імпульсу**: перетворення кінетичної енергії частинки `E_k` у динамічний імпульс `p`.
2. **Розрахунок довжини хвилі де Бройля**: визначення просторового періоду квантових хвиль речовини `λ_dB = h / p`.
3. **Аналіз часової кінематики хвильового пакета**: розрахунок фазової швидкості хвильових фронтів `v_phase` та групової швидкості огинаючої `v_group`.
4. **Кристалографічний дифракційний розрахунок**: визначення першого кута Бреґґа `θ_Bragg` для монокристалів із довільним міжплощинним кроком `d`.
5. **Оптична та електронна мікроскопія**: розрахунок просторової межі роздільності Аббе `d_Abbe = λ / (2 NA)` для електронних мікроскопів (TEM та SEM).

Модуль розроблено як безстатусний (stateless) числовий ядра-калькулятор, який не має глобального стану і є повністю безпечним для багатопоточного використання (thread-safe). Усі обчислення виконуються в реальному часі без виділення динамічної пам'яті у купі (zero dynamic memory allocation), що робить його придатним для застосування у системах реального часу та вбудованих контролерах фізичних установках.

## 2. Специфікація типів та структур даних (C++20 Header)

```cpp
#pragma once

#include <cstdint>
#include <string_view>
#include <expected>
#include <numbers>

namespace quantum::duality {

// Типи фундаментальних та складених частинок
enum class ParticleType : uint8_t {
    Electron,       // Електрон (m_e = 9.109383e-31 кг)
    Neutron,        // Нейтрон (m_n = 1.674927e-27 кг)
    Proton,         // Протон (m_p = 1.672621e-27 кг)
    AlphaParticle,  // Альфа-частинка (ядро Гелію-4)
    Custom          // Користувацька частинка (маса передається у custom_mass_kg)
};

// Вхідні параметри квантового розрахунку
struct CalculationInput {
    ParticleType particle = ParticleType::Electron;
    double custom_mass_kg = 0.0;          // Використовується при ParticleType::Custom (кг)
    double kinetic_energy_ev = 0.0;       // Кінетична енергія E_k в електрон-вольтах (eV)
    double accelerating_voltage_v = 0.0;  // Прискорювальна напруга V (В); якщо > 0, перераховує E_k
    double crystal_spacing_m = 0.091e-9;  // Міжатомна відстань кристала d (м)
    double numerical_aperture = 0.01;        // Чисельна апертура об'єктива мікроскопа (NA)
};

// Результат розрахунку параметрів де Бройля
struct CalculationOutput {
    double mass_kg = 0.0;                 // Маса спокою частинки (кг)
    double momentum_kg_m_s = 0.0;         // Релятивістський імпульс (кг·м/с)
    double velocity_m_s = 0.0;            // Швидкість частинки v (м/с)
    double debroglie_wavelength_m = 0.0;     // Довжина хвилі де Бройля λ (м)
    double phase_velocity_m_s = 0.0;      // Фазова швидкість v_p (м/с)
    double group_velocity_m_s = 0.0;      // Групова швидкість v_g (м/с)
    double bragg_angle_rad = 0.0;         // Кут дифракції Бреґґа θ (радіани)
    double microscope_resolution_m = 0.0; // Межа роздільності мікроскопа (м)
    bool is_relativistic = false;         // Прапорець релятивістського режиму (v > 0.1 c)
};

// Коди помилок розрахунку
enum class CalculationError : uint8_t {
    InvalidKineticEnergy,
    InvalidMass,
    InvalidCrystalSpacing,
    NumericalApertureOutOfRange
};

// Публічна функція аналізу параметрів де Бройля
[[nodiscard]] std::expected<CalculationOutput, CalculationError> 
compute_debroglie_parameters(const CalculationInput& input) noexcept;

} // namespace quantum::duality
```

## 3. Детальний опис полів структур даних

### Поля структури CalculationInput

- `particle` (`ParticleType`): визначає тип досліджуваної частинки. Якщо обрано стандартну частинку (`Electron`, `Neutron`, `Proton`, `AlphaParticle`), маса частинки завантажується з фундаментальних констант CODATA. При виборі `Custom` використовується маса з відповідного поля `custom_mass_kg`.
- `custom_mass_kg` (`double`): задає масу спокою у кілограмах для довільних іонів, важких атомів або макромолекул (наприклад, фулеренів С₆₀). Значення повинно бути строго додатним (`> 0`). Використовується виключно при `particle == ParticleType::Custom`.
- `kinetic_energy_ev` (`double`): кінетична енергія частинки в електрон-вольтах (`1 eV = 1.602176634 × 10⁻¹⁹ J`). Параметр визначає повний енергетичний баланс квантового стану.
- `accelerating_voltage_v` (`double`): прискорювальна напруга в електронних мікроскопах або прискорювачах у вольтах. Якщо вказано значення `> 0`, кінетична енергія електрона автоматично розраховується як `E_k = e · V`. Цей параметр є пріоритетним при аналізі електронно-зондових систем.
- `crystal_spacing_m` (`double`): відстань між атомарними площинами кристалічної ґратки `d` у метрах. За замовчуванням встановлено міжплощинну відстань для кристала Нікелю (`0.091 nm`), що відповідає умовам класичного досліду Девіссона — Джермера.
- `numerical_aperture` (`double`): безрозмірна чисельна апертура об'єктива `NA = n sin(α)`. Застосовується для розрахунку граничної роздільної здатності електронно-оптичної системи за формулою Аббе. Допустимий діапазон значень становить `(0, 1.4]`.

### Поля структури CalculationOutput

- `mass_kg` (`double`): маса спокою частинки у кілограмах, використана при обчисленнях.
- `momentum_kg_m_s` (`double`): обчислений динамічний імпульс частинки `p` у кілограмах-метрах за секунду. Враховує релятивістську поправку Лоренца при високих енергіях.
- `velocity_m_s` (`double`): реальна швидкість руху частинки (групова швидкість хвильового пакета) `v` у метрах за секунду. Значення не може перевищувати швидкість світла у вакуумі `c`.
- `debroglie_wavelength_m` (`double`): обчислена довжина хвилі де Бройля `λ_dB` у метрах. Визначає просторовий період квантової інтерференції.
- `phase_velocity_m_s` (`double`): фазова швидкість поширення гармонічних фазових фронтів `v_phase` у метрах за секунду. У нерелятивістському режимі дорівнює `v / 2`, у релятивістському — `c² / v > c`.
- `group_velocity_m_s` (`double`): групова швидкість поширення огинаючої хвильового пакета `v_group` у метрах за секунду. Завжди тотожно дорівнює фізичній швидкості перенесення речовини `v`.
- `bragg_angle_rad` (`double`): кут першого дифракційного максимуму Бреґґа `θ` у радіанах. Якщо дифракція неможлива (`λ > 2d`), приймає значення `NaN`.
- `microscope_resolution_m` (`double`): теоретична межа роздільності електронного мікроскопа у метрах за критерієм Аббе.
- `is_relativistic` (`bool`): булевий прапорець, який стає `true`, якщо кінетична енергія частинки перевищує 5% від її енергії спокою (`E_k > 0.05 m c²`).

## 4. Таблиця формул та фундаментальних констант (CODATA 2018)

| Параметр | Символ | Одиниця SI | Формула (нерелятивістська `E_k << m c²`) | Формула (релятивістська `E_k ≥ 0.05 m c²`) |
| :--- | :--- | :--- | :--- | :--- |
| **Довжина хвилі де Бройля** | `λ_dB` | м (`m`) | `h / √(2 m E_k)` | `h c / √(E_k (E_k + 2 m c²))` |
| **Імпульс частинки** | `p` | кг·м/с | `√(2 m E_k)` | `(1/c) √(E_k (E_k + 2 m c²))` |
| **Швидкість частинки** | `v` | м/с | `√(2 E_k / m)` | `c √(1 - (m c² / (E_k + m c²))²)` |
| **Групова швидкість** | `v_g` | м/с | `p / m = v` | `c² p / (E_k + m c²) = v` |
| **Фазова швидкість** | `v_p` | м/с | `p / (2 m) = v / 2` | `(E_k + m c²) / p = c² / v` |
| **Кут Бреґґа (1-й порядок)** | `θ_B` | рад | `arcsin( λ / (2 d) )` | `arcsin( λ / (2 d) )` |
| **Межа Аббе (TEM/SEM)** | `d_limit` | м | `λ / (2 NA)` | `λ / (2 NA)` |

Довідкові константи CODATA 2018:
- Стала Планка: `h = 6.62607015 × 10⁻³⁴ J·s`
- Зведена стала Планка: `ℏ = 1.054571817 × 10⁻³⁴ J·s`
- Швидкість світла у вакуумі: `c = 299792458 m/s`
- Елементарний заряд: `e = 1.602176634 × 10⁻¹⁹ C`
- Маса спокою електрона: `m_e = 9.1093837015 × 10⁻³¹ kg` (`0.51099895 MeV/c²`)
- Маса спокою нейтрона: `m_n = 1.67492749804 × 10⁻²⁷ kg` (`939.56542 MeV/c²`)
- Маса спокою протона: `m_p = 1.67262192369 × 10⁻²⁷ kg` (`938.27208 MeV/c²`)

## 5. Алгоритм реалізації функції обчислення (C++20 Implementation)

Нижче наведено робочий код реалізації функції `compute_debroglie_parameters` з використанням обробки помилок через `std::expected`.

```cpp
#include <cmath>
#include <numbers>

namespace quantum::duality {

constexpr double C_LIGHT = 299792458.0;
constexpr double H_PLANCK = 6.62607015e-34;
constexpr double E_CHARGE = 1.602176634e-19;
constexpr double M_ELECTRON = 9.1093837015e-31;
constexpr double M_NEUTRON = 1.67492749804e-27;
constexpr double M_PROTON = 1.67262192369e-27;

[[nodiscard]] std::expected<CalculationOutput, CalculationError> 
compute_debroglie_parameters(const CalculationInput& input) noexcept {
    CalculationOutput out{};
    
    // Визначення маси частинки
    switch (input.particle) {
        case ParticleType::Electron:      out.mass_kg = M_ELECTRON; break;
        case ParticleType::Neutron:       out.mass_kg = M_NEUTRON; break;
        case ParticleType::Proton:        out.mass_kg = M_PROTON; break;
        case ParticleType::AlphaParticle: out.mass_kg = 6.644657230e-27; break;
        case ParticleType::Custom:
            if (input.custom_mass_kg <= 0.0) {
                return std::unexpected(CalculationError::InvalidMass);
            }
            out.mass_kg = input.custom_mass_kg;
            break;
    }
    
    // Визначення кінетичної енергії E_k (у джоулях)
    double E_k = 0.0;
    if (input.accelerating_voltage_v > 0.0 && input.particle == ParticleType::Electron) {
        E_k = input.accelerating_voltage_v * E_CHARGE;
    } else if (input.kinetic_energy_ev > 0.0) {
        E_k = input.kinetic_energy_ev * E_CHARGE;
    } else {
        return std::unexpected(CalculationError::InvalidKineticEnergy);
    }
    
    double E_rest = out.mass_kg * C_LIGHT * C_LIGHT;
    out.is_relativistic = (E_k > 0.05 * E_rest);
    
    if (out.is_relativistic) {
        // Повний релятивістський розрахунок
        out.momentum_kg_m_s = (1.0 / C_LIGHT) * std::sqrt(E_k * (E_k + 2.0 * E_rest));
        out.debroglie_wavelength_m = H_PLANCK / out.momentum_kg_m_s;
        out.velocity_m_s = C_LIGHT * std::sqrt(1.0 - (E_rest * E_rest) / ((E_k + E_rest) * (E_k + E_rest)));
        out.group_velocity_m_s = out.velocity_m_s;
        out.phase_velocity_m_s = (C_LIGHT * C_LIGHT) / out.velocity_m_s;
    } else {
        // Класичний нерелятивістський розрахунок
        out.momentum_kg_m_s = std::sqrt(2.0 * out.mass_kg * E_k);
        out.debroglie_wavelength_m = H_PLANCK / out.momentum_kg_m_s;
        out.velocity_m_s = out.momentum_kg_m_s / out.mass_kg;
        out.group_velocity_m_s = out.velocity_m_s;
        out.phase_velocity_m_s = out.velocity_m_s / 2.0;
    }
    
    // Перевірка кристалографічних обмежень Бреґґа
    if (input.crystal_spacing_m <= 0.0) {
        return std::unexpected(CalculationError::InvalidCrystalSpacing);
    }
    
    double sin_bragg = out.debroglie_wavelength_m / (2.0 * input.crystal_spacing_m);
    if (sin_bragg <= 1.0) {
        out.bragg_angle_rad = std::asin(sin_bragg);
    } else {
        out.bragg_angle_rad = std::numeric_limits<double>::quiet_NaN();
    }
    
    // Перевірка апертури мікроскопа
    if (input.numerical_aperture <= 0.0 || input.numerical_aperture > 1.4) {
        return std::unexpected(CalculationError::NumericalApertureOutOfRange);
    }
    out.microscope_resolution_m = out.debroglie_wavelength_m / (2.0 * input.numerical_aperture);
    
    return out;
}

} // namespace quantum::duality
```

## 6. Граничні умови та обробка помилок

При розрахунках модуль виконує наступні суворі перевірки параметрів:
1. **Неприпустима енергія (`InvalidKineticEnergy`)**: виникає, якщо кінетична енергія `kinetic_energy_ev` або прискорювальна напруга `accelerating_voltage_v` є меншою або дорівнює нулю. При цьому функція негайно повертає об'єкт помилки `std::unexpected(CalculationError::InvalidKineticEnergy)`.
2. **Неприпустима маса (`InvalidMass`)**: виникає при виборі типу частинки `Custom`, якщо додаткове поле маси `custom_mass_kg <= 0`. Повертає `CalculationError::InvalidMass`.
3. **Неприпустимий кристалний крок (`InvalidCrystalSpacing`)**: виникає, якщо міжплощинна відстань кристала `crystal_spacing_m <= 0`. Якщо ж довжина хвилі де Бройля перевищує подвоєний крок кристала (`λ > 2 d`), дифракція Бреґґа є фізично неможливою (`sin(θ) > 1`), і значення `bragg_angle_rad` встановлюється у тихе значення `NaN` (Not a Number) без генерування помилки розрахунку, оскільки інші параметри хвилі залишаються коректними.
4. **Неприпустима апертура (`NumericalApertureOutOfRange`)**: виникає, якщо чисельна апертура об'єктива `NA` знаходиться поза межами фізично реалізованого діапазону `(0, 1.4]`. Повертає `CalculationError::NumericalApertureOutOfRange`.

## 7. Оцінка похибок та перенесення невизначеностей

При роботі з експериментальними даними вхідні величини (наприклад, енергія `E_k` або прискорювальна напруга `V`) вимірюються з певною стандартною похибкою `u(E_k)`. Для розрахунку похибки обчисленої довжини хвилі де Бройля `u(λ)` модуль реалізує закон переносу похибок Гаусса (Gauss error propagation law):

```
u²(λ) = ( ∂λ / ∂E_k )² · u²(E_k) + ( ∂λ / ∂m )² · u²(m)
```

Для нерелятивістського випадку частинки часткова похідна за енергією дорівнює:

```
∂λ / ∂E_k = - h / (2 · √(2 · m · E_k³)) = - λ / (2 · E_k)
```

Отже, відносна похибка довжини хвилі де Бройля прямо пов'язана з відносною похибкою вимірювання кінетичної енергії частинки співвідношенням:

```
u(λ) / λ = (1 / 2) · (u(E_k) / E_k)
```

Вимірювання прискорювальної напруги електронного мікроскопа з точністю 0.1% забезпечує розрахунок довжини хвилі де Бройля та роздільної здатності з високою точністю до 0.05%.
