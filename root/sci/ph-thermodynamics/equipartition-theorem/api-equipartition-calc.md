# 🛠️ Інтерфейс обчислення термодинамічних властивостей за рівнорозподілом (API Reference)

Цей документ описує програмний інтерфейс (API) бібліотечного модуля `EquipartitionCalc`, призначеного для розрахунку термодинамічних характеристик газів, кристалів та мікроелектромеханічних систем (МЕМС) з урахуванням класичної теореми рівнорозподілу енергії та ефектів квантового виморожування ступенів вільності.

---

### 1. Архітектура бібліотеки та типи даних

Обчислювальний модуль `EquipartitionCalc` спроектовано як високопродуктивну обчислювальну бібліотеку для чисельного розрахунку термодинамічних параметрів газів, кристалічних ґраток та елементів мікросистемотехніки. 

Бібліотека реалізує точні математичні моделі статистичної фізики для обчислення внутрішньої теплової енергії, молярної теплоємності при постійному об'ємі `C_V`, молярної теплоємності при постійному тиску `C_P`, адіабатичного показника (коефіцієнта Пуассона `γ = C_P / C_V`), середньоквадратичних амплітуд флуктуацій мікромеханічних осциляторів, а також спектральної густини електричного шуму Джонсона — Найквіста.

#### Базові концепції та структурні поля конфігурації:

1. **`MoleculeType` (Тип геометрії молекули):**
   Енумератор, який визначає просторову симетрію та геометрію молекули:
   - `Monatomic`: Одноатомний газ (гелій, аргон), який має лише поступальні ступені вільності.
   - `Diatomic`: Двоатомна молекула (азот, кисень, водень), яка має 3 поступальні та 2 обертальні ступені вільності.
   - `PolyatomicLinear`: Лінійна багатоатомна молекула (вуглекислий газ CO₂), яка має 2 обертальні та `3N − 5` коливальних мод.
   - `PolyatomicNonLinear`: Об'ємна нелінійна багатоатомна молекула (вода H₂O, метан CH₄), яка має 3 обертальні та `3N − 6` коливальних мод.

2. **`MoleculeConfig` (Структура параметрів молекули):**
   - `degrees_trans`: Кількість поступальних ступенів вільності (зазвичай 3 для тривимірного простору).
   - `degrees_rot`: Кількість обертальних ступенів вільності (0 для одноатомного, 2 для лінійного, 3 для нелінійного газу).
   - `vib_temperatures`: Вектор дійсних чисел, що містить характеристичні коливальні температури `Θ_vib = ℏ ω / k_B` у кельвінах (K) для кожної нормальної коливальної моди.
   - `rot_temperature`: Характеристична обертальна температура `Θ_rot = ℏ² / (2 I k_B)` у кельвінах (K), яка визначає температурну межу квантового розморожування обертального руху.

---

### 2. Детальний опис функціонального інтерфейсу та математичних алгоритмів

Бібліотека надає наступні основні обчислювальні методи для розрахунку термодинамічних величин:

1. **`classical_molar_heat_capacity_cv` (Класична молярна теплоємність):**
   Обчислює граничне класичне значення молярної теплоємності при постійному об'ємі `C_V` за точним формулюванням теореми рівнорозподілу енергії Больцмана. Метод підраховує загальну кількість квадратичних термів у гамільтоніані:
   ```
   C_V = ½ · (f_trans + f_rot + 2 · f_vib) · R
   ```
   де `R ≈ 8.314 Дж/(моль·К)` — універсальна газова стала.

2. **`quantum_molar_heat_capacity_cv` (Квантова молярна теплоємність):**
   Обчислює реальну молярну теплоємність газу або кристала при довільній температурі `T` з урахуванням ефектів квантового виморожування мод за формулою Планка — Ейнштейна:
   ```
   C_V(T) = ½ (f_trans + f_rot) R + R · ∑_{i} (Θ_i / T)² · exp(Θ_i / T) / [exp(Θ_i / T) − 1]²
   ```
   Цей метод автоматично обробляє квантове замерзання високочастотних мод при низьких температурах (`T << Θ_vib`).

3. **`adiabatic_index_gamma` (Показник адіабати):**
   Розраховує коефіцієнт адіабатичного розширення `γ = C_P / C_V = 1 + R / C_V`. Приснований як для класичного, так і для квантового розрахунку теплоємності.

4. **`mems_cantilever_noise_rms` (Теплове тремтіння МЕМС-консолі):**
   Обчислює середня квадратичну амплітуду флуктуацій механічного зміщення кремнієвої консолі атомно-силового мікроскопа (АФМ) масою `m` та жорсткістю `k` при температурі `T` на основі рівнорозподілу потенціальної енергії `½ k ⟨x²⟩ = ½ k_B T`:
   ```
   x_rms = √(k_B T / k)
   ```

5. **`johnson_nyquist_noise_voltage` (Шум Джонсона — Найквіста):**
   Обчислює середньоквадратичну напругу теплового шуму опору `R` в заданій смузі частот `Δf` при температурі `T` за формулою Найквіста:
   ```
   V_rms = √(4 · k_B · T · R · Δf)
   ```

---

### 3. Повна реалізація інтерфейсу (C++, C, Python)

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <iomanip>

namespace StatisticalPhysics {

constexpr double kBoltzmann = 1.380649e-23; // Дж/К
constexpr double kAvogadro  = 6.02214076e23; // моль^-1
constexpr double kGasConstant = kBoltzmann * kAvogadro; // Дж/(моль·К)

enum class MoleculeType {
    Monatomic,
    Diatomic,
    PolyatomicLinear,
    PolyatomicNonLinear
};

struct MoleculeConfig {
    MoleculeType type{MoleculeType::Diatomic};
    int degrees_trans{3};
    int degrees_rot{2};
    std::vector<double> vib_temperatures; // Θ_vib у Кельвінах
    double rot_temperature{85.4};          // Θ_rot у Кельвінах
};

class EquipartitionCalculator {
public:
    explicit EquipartitionCalculator(MoleculeConfig config)
        : config_(std::move(config)) {
        validate_config();
    }

    [[nodiscard]] double classical_molar_heat_capacity_cv() const noexcept {
        const int f_vib = static_cast<int>(config_.vib_temperatures.size());
        const double f_total_quad = config_.degrees_trans + config_.degrees_rot + 2.0 * f_vib;
        return 0.5 * f_total_quad * kGasConstant;
    }

    [[nodiscard]] double quantum_molar_heat_capacity_cv(double temp_kelvin) const {
        if (temp_kelvin <= 0.0) {
            throw std::invalid_argument("Температура повинна бути строго додатною.");
        }

        // Поступальний внесок (завжди 1.5 R у класичній області)
        double cv_sum = 0.5 * config_.degrees_trans * kGasConstant;

        // Обертальний внесок (класичний при T > Θ_rot, виморожений при T < Θ_rot)
        if (config_.degrees_rot > 0) {
            if (temp_kelvin > config_.rot_temperature) {
                cv_sum += 0.5 * config_.degrees_rot * kGasConstant;
            } else {
                // Спрощене дворівневе виморожування обертань
                double ratio = config_.rot_temperature / temp_kelvin;
                cv_sum += 0.5 * config_.degrees_rot * kGasConstant * std::exp(-ratio);
            }
        }

        // Коливальний внесок Планка - Ейнштейна для кожної нормальної моди
        for (double theta_vib : config_.vib_temperatures) {
            double x = theta_vib / temp_kelvin;
            if (x > 100.0) {
                // Виморожена мода (забігання експоненціальної переповненості)
                continue;
            }
            double exp_x = std::exp(x);
            double einstein_factor = (x * x * exp_x) / ((exp_x - 1.0) * (exp_x - 1.0));
            cv_sum += kGasConstant * einstein_factor;
        }

        return cv_sum;
    }

    [[nodiscard]] double adiabatic_index_gamma(double temp_kelvin, bool use_quantum = true) const {
        double cv = use_quantum ? quantum_molar_heat_capacity_cv(temp_kelvin)
                                : classical_molar_heat_capacity_cv();
        double cp = cv + kGasConstant;
        return cp / cv;
    }

    [[nodiscard]] static double mems_cantilever_noise_rms(double stiffness, double temp_kelvin) {
        if (stiffness <= 0.0 || temp_kelvin <= 0.0) {
            throw std::invalid_argument("Жорсткість та температура повинні бути додатними.");
        }
        return std::sqrt((kBoltzmann * temp_kelvin) / stiffness);
    }

    [[nodiscard]] static double johnson_nyquist_noise_voltage(double resistance, double temp_kelvin, double bandwidth_hz) {
        if (resistance < 0.0 || temp_kelvin <= 0.0 || bandwidth_hz <= 0.0) {
            throw std::invalid_argument("Некоректні параметри для обчислення шуму Найквіста.");
        }
        return std::sqrt(4.0 * kBoltzmann * temp_kelvin * resistance * bandwidth_hz);
    }

private:
    void validate_config() const {
        if (config_.degrees_trans < 1 || config_.degrees_trans > 3) {
            throw std::invalid_argument("Поступальних ступенів вільності має бути від 1 до 3.");
        }
    }

    MoleculeConfig config_;
};

} // namespace StatisticalPhysics

int main() {
    using namespace StatisticalPhysics;

    // Конфігурація для азоту (N2): 3 поступальні, 2 обертальні, 1 коливальна мода (Θ_vib = 3371 K)
    MoleculeConfig n2_config{
        MoleculeType::Diatomic,
        3, 2, {3371.0}, 2.88
    };

    EquipartitionCalculator calc(n2_config);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Класична C_V: " << calc.classical_molar_heat_capacity_cv() << " Дж/(моль·К)\n\n";

    std::cout << "Т, K\tC_V (квантова)\tGamma\n";
    for (double T : {50.0, 300.0, 1500.0, 3000.0}) {
        double cv_q = calc.quantum_molar_heat_capacity_cv(T);
        double gamma = calc.adiabatic_index_gamma(T, true);
        std::cout << T << "\t" << cv_q << "\t\t" << gamma << "\n";
    }

    double cant_noise = EquipartitionCalculator::mems_cantilever_noise_rms(0.1, 300.0);
    std::cout << "\nТеплове тремтіння кантилевера (k=0.1 N/m, 300K): " << cant_noise * 1e9 << " нм\n";

    double noise_v = EquipartitionCalculator::johnson_nyquist_noise_voltage(1000.0, 300.0, 1e6);
    std::cout << "Шум Найквіста резистора (1 kOhm, 1 MHz, 300K): " << noise_v * 1e6 << " мкВ\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define K_BOLTZMANN 1.380649e-23
#define K_AVOGADRO 6.02214076e23
#define K_GAS_CONSTANT (K_BOLTZMANN * K_AVOGADRO)

typedef struct {
    int degrees_trans;
    int degrees_rot;
    size_t num_vib_modes;
    const double* vib_temperatures;
    double rot_temperature;
} MoleculeConfigC;

double classical_molar_heat_capacity_cv_c(const MoleculeConfigC* config) {
    double f_total_quad = (double)config->degrees_trans + (double)config->degrees_rot + 2.0 * (double)config->num_vib_modes;
    return 0.5 * f_total_quad * K_GAS_CONSTANT;
}

double quantum_molar_heat_capacity_cv_c(const MoleculeConfigC* config, double temp_kelvin) {
    if (temp_kelvin <= 0.0) return -1.0;

    double cv_sum = 0.5 * (double)config->degrees_trans * K_GAS_CONSTANT;

    if (config->degrees_rot > 0) {
        if (temp_kelvin > config->rot_temperature) {
            cv_sum += 0.5 * (double)config->degrees_rot * K_GAS_CONSTANT;
        } else {
            double ratio = config->rot_temperature / temp_kelvin;
            cv_sum += 0.5 * (double)config->degrees_rot * K_GAS_CONSTANT * exp(-ratio);
        }
    }

    for (size_t i = 0; i < config->num_vib_modes; ++i) {
        double x = config->vib_temperatures[i] / temp_kelvin;
        if (x > 100.0) continue;
        double exp_x = exp(x);
        double einstein_factor = (x * x * exp_x) / ((exp_x - 1.0) * (exp_x - 1.0));
        cv_sum += K_GAS_CONSTANT * einstein_factor;
    }

    return cv_sum;
}

int main(void) {
    double n2_vib_temps[1] = {3371.0};
    MoleculeConfigC n2_cfg = {
        .degrees_trans = 3,
        .degrees_rot = 2,
        .num_vib_modes = 1,
        .vib_temperatures = n2_vib_temps,
        .rot_temperature = 2.88
    };

    printf("Класична C_V (C): %.2f Дж/(моль·К)\n", classical_molar_heat_capacity_cv_c(&n2_cfg));
    printf("Квантова C_V при 300K (C): %.2f Дж/(моль·К)\n", quantum_molar_heat_capacity_cv_c(&n2_cfg, 300.0));

    return 0;
}
```
```py
import math

K_BOLTZMANN = 1.380649e-23
K_AVOGADRO = 6.02214076e23
K_GAS_CONSTANT = K_BOLTZMANN * K_AVOGADRO

class EquipartitionCalculatorPy:
    def __init__(self, degrees_trans=3, degrees_rot=2, vib_temperatures=None, rot_temperature=85.4):
        self.degrees_trans = degrees_trans
        self.degrees_rot = degrees_rot
        self.vib_temperatures = vib_temperatures if vib_temperatures is not None else []
        self.rot_temperature = rot_temperature

    def classical_molar_heat_capacity_cv(self) -> float:
        f_total_quad = self.degrees_trans + self.degrees_rot + 2.0 * len(self.vib_temperatures)
        return 0.5 * f_total_quad * K_GAS_CONSTANT

    def quantum_molar_heat_capacity_cv(self, temp_kelvin: float) -> float:
        if temp_kelvin <= 0.0:
            raise ValueError("Температура повинна бути додатною")

        cv_sum = 0.5 * self.degrees_trans * K_GAS_CONSTANT

        if self.degrees_rot > 0:
            if temp_kelvin > self.rot_temperature:
                cv_sum += 0.5 * self.degrees_rot * K_GAS_CONSTANT
            else:
                ratio = self.rot_temperature / temp_kelvin
                cv_sum += 0.5 * self.degrees_rot * K_GAS_CONSTANT * math.exp(-ratio)

        for theta_vib in self.vib_temperatures:
            x = theta_vib / temp_kelvin
            if x > 100.0:
                continue
            exp_x = math.exp(x)
            einstein_factor = (x * x * exp_x) / ((exp_x - 1.0) ** 2)
            cv_sum += K_GAS_CONSTANT * einstein_factor

        return cv_sum

if __name__ == "__main__":
    calc = EquipartitionCalculatorPy(degrees_trans=3, degrees_rot=2, vib_temperatures=[3371.0], rot_temperature=2.88)
    print(f"Класична C_V (Py): {calc.classical_molar_heat_capacity_cv():.2f} Дж/(моль·К)")
    print(f"Квантова C_V 300K (Py): {calc.quantum_molar_heat_capacity_cv(300.0):.2f} Дж/(моль·К)")
```
:::

---

### 4. Розрахунок газів та багатокомпонентних сумішей

Для газової суміші, що складається з `K` різних типів компонентів із молярними частками `x_i` (де `∑ x_i = 1`), середня молярна теплоємність суміші описується принципом адитивності теплоємностей за законом Дальтона:

```
C_V_mix(T) = ∑_{i=1}^{K} x_i · C_V_i(T)
```

Цей метод дозволяє обчислювати теплофізичні параметри атмосфери планет (наприклад, суміші `N₂`, `O₂`, `CO₂`, `Ar`), а також робочих тіл газових турбін та двигунів внутрішнього згоряння при змінних температурах у широкому діапазоні від 50 K до 3000 K.

---

### 5. Похибки, чисельна стійкість та потокобезпечність

#### 5.1. Потокобезпечність та відсутність мутабельного стану
Усі обчислювальні методи класу `EquipartitionCalculator` позначені як `const` у C++ та `nodiscard`. Вони не змінюють внутрішній стан екземпляра після ініціалізації. Це гарантує повну потокобезпечність (*thread-safety*) при паралельних термодинамічних розрахунках у багатопотокових симуляціях без використання блокувальних примітивів синхронізації (м'ютексів).

#### 5.2. Запобігання чисельному переповненню експоненти
При низьких температурах (`T → 0`) аргумент експоненціальної функції `x = Θ_vib / T` прямує до нескінченності. Прямий виклику функції `std::exp(x)` у C++ або C при `x > 709` викликає чисельне переповнення з плаваючою крапкою та повертає нескінченність (`inf`).

Для запобігання цьому у бібліотеці реалізовано умовну перевірку `if (x > 100.0) continue;`. Оскільки при `x = 100` значення фактора Планка — Ейнштейна менше за `10⁻³⁸`, ця мода практично повністю виморожена, і її чисельний внесок тотожно прирівнюється до нуля без втрати точності.

#### 5.3. Межі гармонічного наближення
Модуль використовує наближення незалежних гармонічних мод. Для екстремально високих температур (`T > 3000 K`), де суттєвим стає ангармонізм міжмолекулярного потенціалу, розширення зв'язків та термічна дисоціація молекул, реальна теплоємність відхиляється від розрахованої гармонічної моделі.

---

### 6. Практичні приклади застосування та підключення модуля

- **Аеронавтика та гіперзвукова аеродинаміка:** При розрахунку обтікання космічних апаратів газами у верхніх шарах атмосфери показник адіабати `γ(T)` змінюється від 1.40 (при 300 K) до 1.28 (при 2000 K) через розморожування коливань, що кардинально змінює температуру ударної хвилі.
- **Кріогенна техніка та розрахунок теплоприпливів:** Обчислення квантового спаду теплоємності конструкційних матеріалів при рідкогелієвих температурах (`4.2 K`) необхідне для проектування надпровідних магнітів та кріостатів.
- **Проектування мікросистем (MEMS/NEMS):** Розрахунок теплового тремтіння кантилеверів та мікрогіроскопів визначає граничне відношення сигнал/шум у високовлучних сенсорах тиску та прискорення.
- **Малошумна аналогова електроніка:** Розрахунок теплового шуму опору за формулою Найквіста дозволяє оптимізувати вхідні каскади малошумних підсилювачів та датчиків.
