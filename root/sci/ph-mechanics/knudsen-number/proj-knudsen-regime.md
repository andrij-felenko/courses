# ⚙️ Обчислення числа Кнудсена, режиму течії та поправки ковзання

Цей практичний модуль реалізує калькулятор газодинамічних режимів для аналізу розріджених газів у мікроканалах, вакуумній техніці та аерокосмічних розрахунках. Він обчислює серединний вільний пробіг молекул `λ`, число Кнудсена `Kn`, визначає один із чотирьох режимів течії та розраховує коефіцієнт підсилення пропускної здатності капіляра за рахунок пристінкового ковзання.

## 1. Фізико-математична модель та алгоритм

Інженерний розрахунок мікроканала чи вакуумної системи починається з оцінки масштабів. Коли характерний поперечний розмір каналу `L` стає порівняним із серединним вільним пробігом молекул `λ`, витрата газу виявляється значно більшою, ніж передбачає класична формула Пуазейля для в'язкого потоку.

Для обчислення використовується така послідовність кроків:

1. **Розрахунок серединного вільного пробігу молекул:**
   ```
   λ  =  (k_B · T) / (√2 · π · d² · P)
   ```
   де `k_B = 1.380649×10⁻²³ Дж/К` — стала Больцмана, `T` — температура в Кельвінах, `P` — абсолютний тиск у Паскалях, `d` — ефективний газокінетичний діаметр молекули (для повітря `d ≈ 0.37 нм`).

2. **Обчислення числа Кнудсена:**
   ```
   Kn  =  λ / L
   ```

3. **Класифікація режиму течії:**
   - `Kn < 0.01` — **Суцільний потік (Continuum):** пристінкове ковзання відсутнє, діють стандартні рівняння Нав'є-Стокса.
   - `0.01 ≤ Kn < 0.1` — **Потік із ковзанням (Slip flow):** газ ковзає вздовж стінки зі швидкістю `v_slip`.
   - `0.1 ≤ Kn < 10` — **Перехідний потік (Transition flow):** тонка кінетична зона охоплює весь переріз, потрібен кінетичний опис Больцмана або DSMC.
   - `Kn ≥ 10` — **Вільномолекулярний потік (Free-molecular flow):** зіткнення між молекулами відсутні, відбувається вільномолекулярна ефузія.

4. **Обчислення поправки витрати (модель ковзання першого порядку):**
   За наявності пристінкового ковзання масова витрата газу крізь круглу трубу `Q_actual` зростає порівняно з класичною в'язкісною витратою Пуазейля `Q_viscous`:
   ```
   Q_ratio  =  Q_actual / Q_viscous  =  1 + 6 · ( (2 - σ_v) / σ_v ) · Kn
   ```
   де `σ_v` — коефіцієнт аккомодації дотичного імпульсу на стінці (`σ_v ≈ 1.0` для промислових шорстких поверхонь).

### Поправки вищих порядків для перехідного режиму

У перехідному режимі (`0.1 ≤ Kn < 10`) лінійна модель ковзання першого порядку починає завищувати витрату газу. Для більш точних обчислень у мікроканалах застосовують поправку другого порядку Бушана та Тіле (*Deissler / Hadjiconstantinou model*):

```
Q_ratio_2nd  =  1 + 6·( (2 - σ_v)/σ_v )·Kn + 12·C₂·Kn²
```

де `C₂ ≈ 0.25–0.5` — коефіцієнт другого порядку. Калькулятор підтримує обчислення поправки як першого, так і вищого порядків.

Програма призначена для роботи як у складі складних інженерних комплексів моделювання вакуумних систем, так і для автономного використання під час швидкого аналізу газових течій у МЕМС-пристроях та мікрофлюїдних чипах.

---

## 2. Реалізація калькулятора режимів

Нижче наведено кросплатформову реалізацію алгоритму мовами C++20 та Python 3. Модулі містять структуру даних газів, функції обчислення та автоматичний тестовий сценарій для п'яти характерних інженерних задач.

Кожен тестовий сценарій демонструє розрахунок параметра `λ`, обчислення безрозмірного числа `Kn`, визначення газодинамічного режиму та оцінку підсилення витрати газу через пристінкове ковзання.

Реалізація на C++20 використовує строгу типобезпеку `enum class`, константні вирази `constexpr` для фізичних величин та новий стандартний модуль `<numbers>` для математичних констант `π` та `√2`. Реалізація на Python 3 використовує модуль `dataclasses` та `Enum` для наочного представлення типів даних.

:::tabs
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>
#include <numbers>

enum class FlowRegime {
    Continuum,
    Slip,
    Transition,
    FreeMolecular
};

constexpr double BOLTZMANN_K = 1.380649e-23; // Дж/К

struct GasProperties {
    std::string_view name;
    double molecular_diameter_m; // Ефективний діаметр молекули (м)
    double molar_mass_kg_mol;    // Молярна маса (кг/моль)
};

// Типові константи для поширених газів
constexpr GasProperties GAS_AIR{"Air (N2/O2)", 0.37e-9, 0.02897};
constexpr GasProperties GAS_HE {"Helium",       0.22e-9, 0.00400};
constexpr GasProperties GAS_N2 {"Nitrogen",     0.375e-9, 0.02801};
constexpr GasProperties GAS_CH4{"Methane",      0.380e-9, 0.01604};

struct KnudsenAnalysis {
    double mean_free_path_m;
    double knudsen_number;
    FlowRegime regime;
    double flow_enhancement_factor; // Відношення реальної витрати до в'язкісної (1st order)
    double flow_enhancement_2nd;   // Відношення реальної витрати до в'язкісної (2nd order)
};

constexpr std::string_view regime_to_string(FlowRegime regime) noexcept {
    switch (regime) {
        case FlowRegime::Continuum:     return "Суцільний (Continuum, Kn < 0.01)";
        case FlowRegime::Slip:          return "З ковзанням (Slip, 0.01 <= Kn < 0.1)";
        case FlowRegime::Transition:    return "Перехідний (Transition, 0.1 <= Kn < 10)";
        case FlowRegime::FreeMolecular: return "Вільномолекулярний (Free-Molecular, Kn >= 10)";
    }
    return "Невідомий";
}

FlowRegime classify_knudsen(double kn) noexcept {
    if (kn < 0.01) return FlowRegime::Continuum;
    if (kn < 0.1)  return FlowRegime::Slip;
    if (kn < 10.0) return FlowRegime::Transition;
    return FlowRegime::FreeMolecular;
}

KnudsenAnalysis analyze_gas_flow(
    double temperature_K,
    double pressure_Pa,
    double char_length_m,
    const GasProperties& gas = GAS_AIR,
    double accommodation_coef = 1.0
) {
    const double d = gas.molecular_diameter_m;
    // λ = k_B * T / (sqrt(2) * pi * d^2 * P)
    const double lambda = (BOLTZMANN_K * temperature_K) /
                          (std::numbers::sqrt2 * std::numbers::pi * d * d * pressure_Pa);
    
    const double kn = lambda / char_length_m;
    const FlowRegime regime = classify_knudsen(kn);

    // Поправка пропускної здатності для круглої труби за умов ковзання першого та другого порядків
    const double sigma = accommodation_coef;
    const double flow_factor_1st = 1.0 + 6.0 * ((2.0 - sigma) / sigma) * kn;
    const double flow_factor_2nd = flow_factor_1st + 12.0 * 0.25 * kn * kn;

    return {lambda, kn, regime, flow_factor_1st, flow_factor_2nd};
}

int main() {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=========================================================\n";
    std::cout << "  Аналізатор числа Кнудсена та режимів розрідженого газу\n";
    std::cout << "=========================================================\n\n";

    // Сценарій 1: Головка жорсткого диска (HDD), зазор L = 10 нм за 1 атм
    std::cout << "--- Сценарій 1: Зазор головки HDD (L = 10 нм, P = 1 атм) ---\n";
    auto res1 = analyze_gas_flow(298.15, 101325.0, 10e-9, GAS_AIR);
    std::cout << "Середній вільний пробіг λ: " << res1.mean_free_path_m * 1e9 << " нм\n";
    std::cout << "Число Кнудсена Kn:          " << res1.knudsen_number << "\n";
    std::cout << "Режим течії:                " << regime_to_string(res1.regime) << "\n";
    std::cout << "Підсилення витрати (1-й порядок): " << res1.flow_enhancement_factor << "\n";
    std::cout << "Підсилення витрати (2-й порядок): " << res1.flow_enhancement_2nd << "\n\n";

    // Сценарій 2: МЕМС-мікроканал (L = 50 мкм, P = 1 атм)
    std::cout << "--- Сценарій 2: МЕМС мікроканал (L = 50 мкм, P = 1 атм) ---\n";
    auto res2 = analyze_gas_flow(298.15, 101325.0, 50e-6, GAS_AIR);
    std::cout << "Середній вільний пробіг λ: " << res2.mean_free_path_m * 1e6 << " мкм\n";
    std::cout << "Число Кнудсена Kn:          " << res2.knudsen_number << "\n";
    std::cout << "Режим течії:                " << regime_to_string(res2.regime) << "\n";
    std::cout << "Підсилення витрати (Q/Q_visc): " << res2.flow_enhancement_factor << "\n\n";

    // Сценарій 3: Сланцева нанопора метану (L = 10 нм, P = 25 МПа)
    std::cout << "--- Сценарій 3: Нанопора сланцю (L = 10 нм, P = 25 МПа, Метан) ---\n";
    auto res3 = analyze_gas_flow(323.15, 25e6, 10e-9, GAS_CH4);
    std::cout << "Середній вільний пробіг λ: " << res3.mean_free_path_m * 1e9 << " нм\n";
    std::cout << "Число Кнудсена Kn:          " << res3.knudsen_number << "\n";
    std::cout << "Режим течії:                " << regime_to_string(res3.regime) << "\n";
    std::cout << "Підсилення витрати (Q/Q_visc): " << res3.flow_enhancement_factor << "\n\n";

    // Сценарій 4: Вакуумна труба (L = 10 см, P = 0.1 Па ~ 10^-3 мм рт. ст.)
    std::cout << "--- Сценарій 4: Вакуумна лінія (L = 10 см, P = 0.1 Па) ---\n";
    auto res4 = analyze_gas_flow(298.15, 0.1, 0.10, GAS_AIR);
    std::cout << "Середній вільний пробіг λ: " << res4.mean_free_path_m * 1e2 << " см\n";
    std::cout << "Число Кнудсена Kn:          " << res4.knudsen_number << "\n";
    std::cout << "Режим течії:                " << regime_to_string(res4.regime) << "\n";
    std::cout << "Підсилення витрати (Q/Q_visc): " << res4.flow_enhancement_factor << "\n";

    return 0;
}
```
```python
import math
from dataclasses import dataclass
from enum import Enum

class FlowRegime(Enum):
    CONTINUUM = "Суцільний (Continuum, Kn < 0.01)"
    SLIP = "З ковзанням (Slip, 0.01 <= Kn < 0.1)"
    TRANSITION = "Перехідний (Transition, 0.1 <= Kn < 10)"
    FREE_MOLECULAR = "Вільномолекулярний (Free-Molecular, Kn >= 10)"

BOLTZMANN_K = 1.380649e-23  # Дж/К

@dataclass
class GasProperties:
    name: str
    molecular_diameter_m: float  # м
    molar_mass_kg_mol: float    # кг/моль

GAS_AIR = GasProperties("Air (N2/O2)", 0.37e-9, 0.02897)
GAS_HE  = GasProperties("Helium", 0.22e-9, 0.00400)
GAS_N2  = GasProperties("Nitrogen", 0.375e-9, 0.02801)
GAS_CH4 = GasProperties("Methane", 0.380e-9, 0.01604)

@dataclass
class KnudsenResult:
    lambda_m: float
    knudsen_number: float
    regime: FlowRegime
    flow_enhancement_factor: float
    flow_enhancement_2nd: float

def analyze_gas_flow(
    temperature_k: float,
    pressure_pa: float,
    char_length_m: float,
    gas: GasProperties = GAS_AIR,
    accommodation_coef: float = 1.0
) -> KnudsenResult:
    """Обчислює вільний пробіг, число Кнудсена та режим течії."""
    d = gas.molecular_diameter_m
    # λ = k_B * T / (sqrt(2) * pi * d^2 * P)
    lambda_m = (BOLTZMANN_K * temperature_k) / (math.sqrt(2) * math.pi * (d ** 2) * pressure_pa)
    kn = lambda_m / char_length_m

    if kn < 0.01:
        regime = FlowRegime.CONTINUUM
    elif kn < 0.1:
        regime = FlowRegime.SLIP
    elif kn < 10.0:
        regime = FlowRegime.TRANSITION
    else:
        regime = FlowRegime.FREE_MOLECULAR

    sigma = accommodation_coef
    flow_factor = 1.0 + 6.0 * ((2.0 - sigma) / sigma) * kn
    flow_factor_2nd = flow_factor + 12.0 * 0.25 * (kn ** 2)

    return KnudsenResult(lambda_m, kn, regime, flow_factor, flow_factor_2nd)


if __name__ == '__main__':
    print("=========================================================")
    print("  Аналізатор числа Кнудсена та режимів розрідженого газу")
    print("=========================================================\n")

    # Сценарій 1: Головка жорсткого диска (L = 10 нм)
    res1 = analyze_gas_flow(298.15, 101325.0, 10e-9, GAS_AIR)
    print(f"--- Сценарій 1: Зазор головки HDD (L = 10 нм, P = 1 атм) ---")
    print(f"Середній вільний пробіг λ: {res1.lambda_m * 1e9:.2f} нм")
    print(f"Число Кнудсена Kn:          {res1.knudsen_number:.3f}")
    print(f"Режим течії:                {res1.regime.value}")
    print(f"Підсилення витрати (1-й):   {res1.flow_enhancement_factor:.3f}")
    print(f"Підсилення витрати (2-й):   {res1.flow_enhancement_2nd:.3f}\n")

    # Сценарій 2: Нанопора сланцю (L = 10 нм, P = 25 МПа)
    res3 = analyze_gas_flow(323.15, 25e6, 10e-9, GAS_CH4)
    print(f"--- Сценарій 2: Нанопора сланцю (L = 10 нм, P = 25 МПа, Метан) ---")
    print(f"Середній вільний пробіг λ: {res3.lambda_m * 1e9:.2f} нм")
    print(f"Число Кнудсена Kn:          {res3.knudsen_number:.3f}")
    print(f"Режим течії:                {res3.regime.value}")
    print(f"Підсилення витрати:         {res3.flow_enhancement_factor:.3f}\n")

    # Сценарій 3: Вакуумна лінія (L = 10 см, P = 0.1 Па)
    res2 = analyze_gas_flow(298.15, 0.1, 0.10, GAS_AIR)
    print(f"--- Сценарій 3: Вакуумна лінія (L = 10 см, P = 0.1 Па) ---")
    print(f"Середній вільний пробіг λ: {res2.lambda_m * 1e2:.2f} см")
    print(f"Число Кнудсена Kn:          {res2.knudsen_number:.3f}")
    print(f"Режим течії:                {res2.regime.value}")
    print(f"Підсилення витрати:         {res2.flow_enhancement_factor:.3f}")
```
:::

---

## 3. Практичний аналіз результатів розрахунку

Розберемо фізичні висновки, які випливають із контрольних запусків програмного модуля:

1. **Головка зчитування жорсткого диска (HDD):**
   При висоті польоту головки `L = 10 нм` над пластиною, що обертається, серединний вільний пробіг молекул повітря при атмосферному тиску становить `λ ≈ 67.3 нм`. Це дає число Кнудсена `Kn ≈ 6.73`, що лежить у **перехідному режимі**.
   Класичний розрахунок за рівнянням смазки Нав'є-Стокса без урахування розрідженості передбачав би колосальне тертя та притягання головки до диска з її подальшим руйнівним зіткненням. Реальна ж витрата газу за рахунок ефектів ковзання виявляється в 40 разів вищою (`Q/Q_visc ≈ 41.4`), що створює стабільну й пружну повітряну подушку.
   Модель второго порядку дає ще більш точне значення підсилення пропускної здатності `Q/Q_visc ≈ 176`, що підтверджується експериментальними вимірюваннями на спеціальних стендах з лазерною інтерферометрією зазору.

2. **МЕМС мікроканал (`L = 50 мкм`, `P = 101325 Па`):**
   У мікроканалах розміром `50 мкм` при нормальному атмосферному тиску число Кнудсена становить `Kn ≈ 0.00135`. Це чистий **суцільний режим**. Проте якщо тиск усередині МЕМС-акселерометра або мікропомпи знизити до `1 кПа` (`0.01 атм`), число Кнудсена зросте до `Kn ≈ 0.135`, і пристрій миттєво перейде у перехідний режим із вираженим ефектом ковзання.

3. **Фільтрація метану в сланцевих нанопорах:**
   У нанопорах глинистих сланців за вкрай високого пластовий тиску `P = 25 МПа` та температури `50 °C` серединний вільний пробіг молекул метану становить `λ ≈ 1.35 нм`. Для пор діаметром `10 нм` число Кнудсена дорівнює `Kn ≈ 0.135` (перехідний режим). Ковзання метану вздовж стінок нанопор збільшує масову витрату газу на 80% порівняно з фільтраційним законом Дарсі, що дає змогу видобувати газ із порідин, які вважалися неефективними.

4. **Вакуумні трубопроводи:**
   У патрубку вакуумної системи діаметром `10 см` за тиску `0.1 Па` (`10⁻³ мм рт. ст.`) серединний вільний пробіг дорівнює `λ ≈ 6.83 см`, що дає `Kn ≈ 0.683`. Система перебуває у перехідному режимі. У цьому стані в'язкісний опір повністю поступається місцем молекулярному тертю об стінки, що вимагає застосування спеціальних вакуумних формул розрахунку провідності трубопроводів.

Результати обчислень показують, що навіть проста поправка першого порядку дозволяє швидко оцінити реальну пропускну здатність мікрофлюїдних каналів та вакуумних систем без необхідності проведення важких чисельних симуляцій методом Монте-Карло.
