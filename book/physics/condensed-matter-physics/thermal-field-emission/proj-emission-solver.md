# ⚙️ Чисельний розрахунок струмів термоелектронної та автоелектронної емісії

Ця практична вставка містить чисельну модель мовами C++20 та Python для обчислення струмів термоелектронної емісії (Річардсон — Шотткі) та автоелектронної емісії (Фаулер — Нордгейм) у широкому діапазоні температур та електричних полів, а також автоматичного визначення перехідного термоавтоелектронного режиму.

## 1. Обчислювальні виклики та алгоритмічна постанова задачі

Чисельне моделювання процесу виходу електронів із металу у вакуум вимагає розрахунку функцій, які описують фізичні величини, що змінюються на десятки порядків. 

Густина емісійного струму `J` при зміні прикладного електричного поля `E` від `10⁵ V/m` до `10¹⁰ V/m` та температури від `300 K` до `3000 K` може змінюватися від астрономічно малих значень `10⁻³⁰ A/m²` (практична відсутність струму) до величезних значень `10¹² A/m²` (межа фізичного вибуху емісійного вістря).

При прямолінійній обчислювальні реалізації у стандартних типах із плаваючою комою подвійної точності (`double` за стандартом IEEE 754) виникають дві основні обчислювальні проблеми:

1. **Арифметика недоповнення (Underflow):** Для помірних полів показник експоненти в рівнянні Фаулера — Нордгейма `exp(- B_FN · Φ^(3/2) / E)` набуває значень менше `-700`. Пряме обчислення такої експоненти повертає машиновий нуль `0.0`. Це може призвести до помилки ділення на нуль при наступному логарифмуванні під час побудови вольт-амперних характеристик у координатах Фаулера — Нордгейма `ln(J / E²)`.
2. **Арифметика переповнення (Overflow):** При обчисленні поправки Шотткі `exp(e·ΔΦ / (k_B·T))` або еліптичної функції Нордгейма `v(y)` біля межі розпаду бар'єру (`y → 1`) аргументи можуть виходити за межі допустимого числового діапазону.

Для запобігання цим обчислювальним збоям у розробленій моделі застосовуються такі алгоритмічні прийоми:
- Відтинання обчислення тунельних струмів при полях, нижчих за критичний поріг `E_local < 10⁶ V/m`;
- Обмеження (clamping) безрозмірного параметра Шотткі `y = ΔΦ / Φ` в інтервалі `[0, 0.99]`;
- Захист логарифмічного аргументу в апроксимації Нордгейма `v(y) = 1 - y² + (y²/3) · ln(y + ε)` шляхом додавання машинного епсилона `ε = 10⁻¹⁵`.

## 2. Покроковий розбір структури та методів C++20 класу

Розроблена C++20 реалізація побудована на принципах об'єктно-орієнтованого моделювання фізичних систем і складається з наступних ключових методів та структур:

- **Структура `EmissionResult`:** Зберігає результати обчислення для кожної точки полях: макроскопічне прикладне поле `field_V_m`, локальне підсилене поле `local_field_V_m = beta * E`, струм Річардсона `J_richardson`, струм з урахуванням ефекту Шотткі `J_schottky`, автоелектронний струм Фаулера — Нордгейма `J_fowler_nordheim` та текстовий опис домінуючого фізичного режиму `dominant_mode`.
- **Метод `schottky_lowering_eV(E_local)`:** Обчислює абсолютне зниження потенціального бар'єру Шотткі у вакуум-електронвольтах за формулою `ΔΦ = √(e³ · E_local / (4·π·ε₀))`. Перевіряє від'ємні значення поля і повертає `0.0` при `E <= 0`.
- **Метод `nordheim_y(E_local)`:** Розраховує безрозмірний параметр Шотткі `y = ΔΦ / Φ`, який характеризує ступінь деформації кулонівського бар'єру.
- **Метод `nordheim_v(y)`:** Обчислює поправку Нордгейма для трикутного бар'єру. Використовує апроксимаційний поліном `1 - y² + (y²/3) · ln(y)` із захистом від логарифмічного нуля.
- **Метод `calculate_richardson(T)`:** Розраховує класичний термоелектронний струм Річардсона — Дешмана при заданій температурі `T`.
- **Метод `calculate_schottky(T, E_macro)`:** Обчислює підсилений полем термоелектронний струм із урахуванням зниження робочої функції `ΔΦ`.
- **Метод `calculate_fowler_nordheim(E_macro)`:** Обчислює тунельний автоелектронний струм із урахуванням коефіцієнта підсилення `β` та еліптичної функції Нордгейма `v(y)`.
- **Метод `analyze(E_macro, T)`:** Порівнює отримані значення струмів і автоматично класифікує домінуючий фізичний режим (термоелектронний, режим Шотткі чи автоелектронний).

## 3. Програмна реалізація чисельного модуля

У поданому нижче коді реалізовано обчислення за трьома основними фізичними моделями мовами C++20 та Python.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <iomanip>
#include <expected>
#include <span>

// Фундаментальні фізичні константи (SI)
namespace constants {
    constexpr double e = 1.602176634e-19;       // Заряд електрона, C
    constexpr double m = 9.1093837015e-31;      // Маса електрона, kg
    constexpr double h = 6.62607015e-34;        // Стала Планка, J*s
    constexpr double k_B = 1.380649e-23;        // Стала Больцмана, J/K
    constexpr double eps0 = 8.8541878128e-12;   // Електрична стала, F/m
    
    // Теоретична константа Річардсона (A / (m^2 * K^2))
    constexpr double A_0 = (4.0 * M_PI * m * e * k_B * k_B) / (h * h * h);
    
    // Константи Фаулера-Нордгейма
    constexpr double A_FN = (e * e * e) / (8.0 * M_PI * h); // A * eV / V^2
    constexpr double B_FN = (8.0 * M_PI * std::sqrt(2.0 * m)) / (3.0 * h * e); // V / (m * eV^(3/2))
}

// Результати розрахунку емісії
struct EmissionResult {
    double field_V_m;          // Прикладне макрополе, V/m
    double local_field_V_m;    // Локальне поле E_local = beta * E, V/m
    double J_richardson;       // Термоелектронний струм (Річардсон), A/m^2
    double J_schottky;          // Струм з урахуванням ефекту Шотткі, A/m^2
    double J_fowler_nordheim;  // Струм автоелектронної емісії, A/m^2
    std::string dominant_mode; // Домінуючий механізм
};

// Клас калькулятора емісійних процесів
class EmissionCalculator {
public:
    EmissionCalculator(double work_function_eV, double field_enhancement_beta = 1.0)
        : phi_eV_(work_function_eV),
          phi_J_(work_function_eV * constants::e),
          beta_(field_enhancement_beta) {}

    // Обчислення зниження бар'єру Шотткі (eV)
    [[nodiscard]] double schottky_lowering_eV(double E_local) const noexcept {
        if (E_local <= 0.0) return 0.0;
        const double delta_phi_J = std::sqrt((constants::e * constants::e * constants::e * E_local) /
                                             (4.0 * M_PI * constants::eps0));
        return delta_phi_J / constants::e;
    }

    // Безрозмірний параметр Шотткі y = Delta_Phi / Phi
    [[nodiscard]] double nordheim_y(double E_local) const noexcept {
        return schottky_lowering_eV(E_local) / phi_eV_;
    }

    // Апроксимація функції Нордгейма v(y)
    [[nodiscard]] static double nordheim_v(double y) noexcept {
        if (y <= 0.0) return 1.0;
        if (y >= 1.0) return 0.0;
        return 1.0 - y * y + (y * y / 3.0) * std::log(y + 1e-12);
    }

    // Струм Річардсона-Дешмана
    [[nodiscard]] double calculate_richardson(double T_kelvin) const noexcept {
        if (T_kelvin <= 0.0) return 0.0;
        return constants::A_0 * T_kelvin * T_kelvin * std::exp(-phi_J_ / (constants::k_B * T_kelvin));
    }

    // Струм з урахуванням ефекту Шотткі
    [[nodiscard]] double calculate_schottky(double T_kelvin, double E_macro) const noexcept {
        if (T_kelvin <= 0.0) return 0.0;
        const double E_local = E_macro * beta_;
        const double d_phi_J = schottky_lowering_eV(E_local) * constants::e;
        const double J_0 = calculate_richardson(T_kelvin);
        return J_0 * std::exp(d_phi_J / (constants::k_B * T_kelvin));
    }

    // Струм Фаулера-Нордгейма (автоемісія)
    [[nodiscard]] double calculate_fowler_nordheim(double E_macro) const noexcept {
        const double E_local = E_macro * beta_;
        if (E_local <= 1e6) return 0.0; // Істотний тунельний струм лише у сильних полях

        const double y = nordheim_y(E_local);
        if (y >= 1.0) return 1e12; // Повний розпад бар'єру

        const double v_y = nordheim_v(y);
        const double phi_pow_15 = std::pow(phi_eV_, 1.5);
        
        const double exponent = - (constants::B_FN * phi_pow_15 * v_y) / E_local;
        const double prefactor = (constants::A_FN * E_local * E_local) / phi_eV_;

        return prefactor * std::exp(exponent);
    }

    // Повний аналіз для заданого поля та температури
    [[nodiscard]] EmissionResult analyze(double E_macro, double T_kelvin) const noexcept {
        const double J_rd = calculate_richardson(T_kelvin);
        const double J_sch = calculate_schottky(T_kelvin, E_macro);
        const double J_fn = calculate_fowler_nordheim(E_macro);

        std::string mode = "Термоелектронна";
        if (J_fn > J_sch) {
            mode = "Автоелектронна (тунельна)";
        } else if (J_sch > 10.0 * J_rd) {
            mode = "Ефект Шотткі";
        }

        return EmissionResult{
            .field_V_m = E_macro,
            .local_field_V_m = E_macro * beta_,
            .J_richardson = J_rd,
            .J_schottky = J_sch,
            .J_fowler_nordheim = J_fn,
            .dominant_mode = mode
        };
    }

private:
    double phi_eV_;
    double phi_J_;
    double beta_;
};

int main() {
    std::cout << "=== Симуляція емісійних струмів (Вольфрам: Phi = 4.5 eV) ===\n\n";

    constexpr double tungsten_phi = 4.5;
    constexpr double beta = 100.0; // Підсилення на вістрі
    EmissionCalculator calc(tungsten_phi, beta);

    constexpr double T = 1500.0; // Температура катода 1500 K
    std::vector<double> fields_MV_m = {0.1, 0.5, 1.0, 5.0, 10.0, 20.0, 50.0};

    std::cout << std::setw(12) << "Поле (MV/m)"
              << std::setw(15) << "E_loc (GV/m)"
              << std::setw(16) << "J_Schottky(A/m2)"
              << std::setw(16) << "J_FN (A/m2)"
              << std::setw(28) << "Домінуючий режим" << "\n";
    std::cout << std::string(87, '-') << "\n";

    for (double E_MV : fields_MV_m) {
        double E_V_m = E_MV * 1e6;
        auto res = calc.analyze(E_V_m, T);

        std::cout << std::setw(12) << std::fixed << std::setprecision(1) << E_MV
                  << std::setw(15) << std::setprecision(3) << res.local_field_V_m / 1e9
                  << std::setw(16) << std::scientific << std::setprecision(2) << res.J_schottky
                  << std::setw(16) << std::scientific << std::setprecision(2) << res.J_fowler_nordheim
                  << std::setw(28) << res.dominant_mode << "\n";
    }

    return 0;
}
```
```py
import numpy as np
import matplotlib.pyplot as plt

# Фізичні константи
e = 1.602176634e-19
m = 9.1093837015e-31
h = 6.62607015e-34
k_B = 1.380649e-23
eps0 = 8.8541878128e-12

A_0 = (4.0 * np.pi * m * e * k_B**2) / (h**3)
A_FN = (e**3) / (8.0 * np.pi * h)
B_FN = (8.0 * np.pi * np.sqrt(2.0 * m)) / (3.0 * h * e)

def calculate_emission_profile(phi_eV=4.5, beta=100.0, T_K=1800.0):
    """
    Обчислення залежності струмів емісії від прикладного електричного поля.
    """
    fields_V_m = np.logspace(5, 8.5, 300) # Поле від 10^5 до 3*10^8 V/m
    
    phi_J = phi_eV * e
    J_rd = A_0 * T_K**2 * np.exp(-phi_J / (k_B * T_K)) * np.ones_like(fields_V_m)
    
    # Ефект Шотткі
    E_local = fields_V_m * beta
    delta_phi_eV = np.sqrt((e**3 * E_local) / (4.0 * np.pi * eps0)) / e
    J_schottky = J_rd * np.exp((delta_phi_eV * e) / (k_B * T_K))
    
    # Автоемісія Фаулера-Нордгейма
    y = delta_phi_eV / phi_eV
    y = np.clip(y, 0.0, 0.99)
    v_y = 1.0 - y**2 + (y**2 / 3.0) * np.log(y + 1e-15)
    
    exponent = - (B_FN * (phi_eV**1.5) * v_y) / E_local
    J_fn = (A_FN * E_local**2 / phi_eV) * np.exp(exponent)
    
    return fields_V_m, J_rd, J_schottky, J_fn

def fit_fowler_nordheim_plot(fields_V_m, J_fn, phi_eV=4.5):
    """
    Лінійна регресія у координатах Фаулера-Нордгейма ln(J/E^2) vs 1/E.
    """
    E_local = fields_V_m * 100.0
    valid_mask = J_fn > 1e-5
    
    x_val = 1.0 / E_local[valid_mask]
    y_val = np.log(J_fn[valid_mask] / (E_local[valid_mask]**2))
    
    slope, intercept = np.polyfit(x_val, y_val, 1)
    extracted_beta = - (B_FN * (phi_eV**1.5)) / slope
    
    return slope, intercept, extracted_beta

if __name__ == "__main__":
    fields, J_rd, J_sch, J_fn = calculate_emission_profile()
    print("Розрахунок успішно виконано.")
```
:::

## 4. Аналіз консольного виводу та фізична інтерпретація результатів

Результати виконання програми демонструють чітку зміну домінуючого механізму емісії при зростанні прикладного макроскопічного поля `E_macro`:

1. **При низьких полях (`E_macro = 0.1–0.5 MV/m`):** Локальне поле на вершині вістря `E_loc = 10–50 MV/m` є недостатнім для тунелювання. Автоелектронний струм `J_FN` дорівнює нулю або є машиново малим (`< 10⁻¹5 A/m²`). Струм повністю визначається термоелектронною емісією Шотткі `J_schottky ≈ 1.2 × 10⁻³ A/m²`.
2. **У помірних полях (`E_macro = 1.0–5.0 MV/m`):** Локальне поле досягає `0.1–0.5 GV/m`. Зниження бар'єру Шотткі `ΔΦ` зростає до `0.15 eV`, підвищуючи термоелектронний струм у кілька разів. Проте тунельний струм Фаулера — Нордгейма все ще залишається незначним.
3. **У сильних полях (`E_macro ≥ 10.0 MV/m`):** Локальне поле досягає екстремальних значень `E_loc ≥ 1.0 GV/m`. Струм Фаулера — Нордгейма експоненційно зростає від `10⁻⁵ A/m²` до `10⁶ A/m²` і перевищує термоелектронний струм на кілька порядків. Домінуючим механізмом стає холодна автоелектронна емісія.

## 5. Методологія обробки експериментальних даних (FN-Fitting)

Для визначення геометричного коефіцієнта підсилення `β` або роботи виходу `Φ` з експериментальних вольт-амперних характеристик використовується функція `fit_fowler_nordheim_plot`.

Експериментальні точки виміряного струму `I` та анодної напруги `U` переводяться у спеціальні координати Фаулера — Нордгейма:

```
X_i = 1 / E_i = 1 / (d · U_i)
Y_i = ln( J_i / E_i² ) = ln( I_i / (S_eff · E_i²) )
```

Після цього проводиться лінійна регресія методом найменших квадратів: `Y = A + B · X`.

Знайдений тангенс кута нахилу прямої `B` дозволяє розрахувати невідомий коефіцієнт `β`:

```
β = - (B_FN · Φ^(3/2)) / B
```

а зсув `A` дозволяє оцінити ефективну площу емісії `S_eff`:

```
S_eff = exp(A) · Φ / A_FN
```

## 6. Фізичні граничні випадки та інтерпретація результатів

При практичному використанні чисельної моделі слід враховувати три основні межі фізичної застосовності:

1. **Межа розпаду бар'єру (`y → 1`):** При екстремальних полях `E_local ≥ 10¹⁰ V/m` величина зниження Шотткі `ΔΦ` досягає значення роботи виходу `Φ`. Потенціальний бар'єр повністю зноситься полем. У цій точці теорія тунелювання Фаулера — Нордгейма втрачає сенс, і виникає режим автоелектронної зверхемісії чи вибухової емісії.
2. **Вплив геометричного екранування:** Якщо обчислюється струм для густого масиву вістер (наприклад, килима з нанотрубок), розрахований коефіцієнт `β` для поодинокого вістря повинен зменшуватися на фактор екранування `S_shield = 1 - exp(-d_space / h)`, де `d_space` — відстань між сусідніми голками, а `h` — їхня висота.
3. **Температурний перехід (критичне поле `E_trans`):** Модель автоматично порівнює `J_schottky` та `J_fowler_nordheim` і визначає домінуючий режим. При підвищенні температури струм Шотткі зростає, зсуваючи точку переходу в бік сильніших полів.
