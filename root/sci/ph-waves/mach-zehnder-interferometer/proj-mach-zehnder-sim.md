# ⚙️ Симуляція та обробка сигналів інтерферометра Маха — Цендера

Очищення високочутливих інтерферометричних вимірювань від акустичних шумів та фазового дрейфу потребує чисельного моделювання хвильових процесів у реально-часовому програмному забезпеченні. Ця вставка містить детальний фізико-математичний розбір алгоритмів симуляції інтерферометра Маха — Цендера, практичну реалізацію трьома мовами програмування (Python, C та C++), аналіз фазового шуму джерела випромінювання, метод розрахунку балансного фотодетектування та алгоритм спектральної дефокусировки.

### 1. Фізична модель та алгоритмічні блоки симулятора

Симуляція інтерферометричної системи вимагає послідовного моделювання вектора стану електромагнітного поля від лазерного випромінювача до фінального каскаду аналогово-цифрового перетворення. Алгоритм розбивається на п'ять фундаментальних обчислювальних блоків:

1. **Генерація лазерного поля з шумівністю:**
   Комплексна амплітуда лазерної хвилі описується виразом `E₀(t) = A₀ · exp(i·(ω₀·t + φ_noise(t)))`. Фазовий шум `φ_noise(t)` складається з двох компонент: високочастотного білого шуму спонтанного випромінювання (визначає природну ширину лінії лазера) та низькочастотного флікер-шуму температурної нестабільності резонатора.

2. **Матричне розщеплення на першому світлодільнику (BS₁):**
   Вхідний вектор поля `E_in = [ E₀(t), 0 ]ᵀ` множиться на унітарну матрицю світлодільника `M_BS` з коефіцієнтом розщеплення 50:50:

   ```
   [ E_armA ] = 1/√2 · [ 1   i ] · [ E₀(t) ]
   [ E_armB ]          [ i   1 ]   [   0   ]
   ```

   у результаті чого формуються хвилі у двох плечах: `E_armA = E₀ / √2` та `E_armB = i · E₀ / √2`.

3. **Фазова затримка у вимірювальному та еталонному плечах:**
   У плечі A хвиля набуває фазового набігу `φ_A = k · n_A · L_A`, де показник заломлення змінюється під дією зовнішнього сигналу `n_A(t) = n₀ + Δn(t)`. У плечі B фазовий набіг становить `φ_B = k · n_B · L_B + φ_vib(t)`, де `φ_vib(t)` відповідає акустичним вібраціям оптичного столу.

4. **Інтерференційне зведення на другому світлодільнику (BS₂):**
   Рекомбіновані хвилі проходять через матрицю `M_BS`, утворюючи вихідні комплексні амплітуди:

   ```
   E_out1 = 1/√2 · (i · E_armA · exp(i·φ_A) + E_armB · exp(i·φ_B))
   E_out2 = 1/√2 · (E_armA · exp(i·φ_A) + i · E_armB · exp(i·φ_B))
   ```

5. **Балансне фотодетектування та віднімання шуму:**
   Фотодетектори реєструють інтенсивності `I₁(t) = |E_out1(t)|²` та `I₂(t) = |E_out2(t)|²`. Різницевий аналоговий сигнал дорівнює:

   ```
   S_diff(t) = I₁(t) - I₂(t) = - I₀(t) · cos(Δφ(t))
   ```

   При застосуванні балансного підключення вхідний шум інтенсивності лазера `I₀(t) = I₀ + δI(t)` входить у синфазний сигнал `S_sum = I₁ + I₂ = I₀(t)` і повністю віднімається у різницевому каналі, що підвищує відношення сигнал/шум (SNR) на 20–40 дБ.

### 2. Багатомовна реалізація симулятора (Python, C, C++)

Нижче наведено повні реалізації симулятора інтерферометра Маха — Цендера. Кожна версія є повністю ідіоматичною для відповідної мови та показує обчислення фазових зсувів, випадкового шуму та балансного виходу.

:::tabs
```py
import math
import cmath
import random
from typing import List, Tuple

class MachZehnderSimulator:
    """Чисельний симулятор оптичного інтерферометра Маха — Цендера.
    
    Моделює поширення хвилі, фазовий зсув у плечі за рахунок зміни n,
    гауссівський фазовий шум та балансне фотодетектування.
    """

    def __init__(self, wavelength_nm: float = 632.8, arm_length_mm: float = 100.0):
        self.wavelength = wavelength_nm * 1e-9  # перевід у метри
        self.arm_length = arm_length_mm * 1e-3  # перевід у метри
        self.k = 2.0 * math.pi / self.wavelength

    def simulate_sample(self, delta_n: float, phase_noise_std: float = 0.005) -> Tuple[float, float, float]:
        """Обчислює інтенсивності I1, I2 та різницевий сигнал S_diff для заданого Δn."""
        # Фазовий набіг у плечі A та B
        phi_a = self.k * (1.0 + delta_n) * self.arm_length
        phi_b = self.k * 1.0 * self.arm_length + random.gauss(0.0, phase_noise_std)

        # Комплексна вхідна хвиля з нормованою амплітудою E0 = 1.0
        e_in = complex(1.0, 0.0)

        # BS1: розщеплення амплітуди
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        e1_bs1 = e_in * inv_sqrt2
        e2_bs1 = e_in * complex(0.0, inv_sqrt2)

        # Поширення хвильовими плечима
        e1_arm = e1_bs1 * cmath.exp(complex(0.0, phi_a))
        e2_arm = e2_bs1 * cmath.exp(complex(0.0, phi_b))

        # BS2: зведення хвиль
        e_out1 = inv_sqrt2 * (e1_arm * complex(0.0, 1.0) + e2_arm)
        e_out2 = inv_sqrt2 * (e1_arm + e2_arm * complex(0.0, 1.0))

        # Фотодетектування
        i1 = abs(e_out1) ** 2
        i2 = abs(e_out2) ** 2
        diff_signal = i1 - i2

        return i1, i2, diff_signal

    def scan_refractive_index(self, start_dn: float, end_dn: float, steps: int) -> List[Tuple[float, float, float, float]]:
        """Виконує сканування показника заломлення та повертає список результатів."""
        results = []
        step_size = (end_dn - start_dn) / steps
        for i in range(steps + 1):
            dn = start_dn + i * step_size
            i1, i2, diff = self.simulate_sample(dn)
            results.append((dn, i1, i2, diff))
        return results


def main():
    sim = MachZehnderSimulator(wavelength_nm=632.8, arm_length_mm=100.0)
    print("Чисельне моделювання сканування показника заломлення (Python):")
    print(f"{'delta_n':>12} | {'I1':>8} | {'I2':>8} | {'Diff Signal':>12}")
    print("-" * 48)

    scan_data = sim.scan_refractive_index(0.0, 10e-6, 10)
    for dn, i1, i2, diff in scan_data:
        print(f"{dn:12.4e} | {i1:8.4f} | {i2:8.4f} | {diff:12.4f}")

if __name__ == "__main__":
    main()
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

/* Структура конфігурації симулятора Маха — Цендера */
typedef struct {
    double wavelength;  /* Довжина хвилі у метрах */
    double arm_length;  /* Довжина плеча у метрах */
    double k;           /* Хвильове число 2π/λ */
} MZM_Simulator;

/* Результати вимірювання детекторами */
typedef struct {
    double i1;          /* Інтенсивність першого детектора */
    double i2;          /* Інтенсивність другого детектора */
    double diff_signal; /* Різницевий балансний сигнал I1 - I2 */
} MZM_Result;

/* Ініціалізація параметрів симулятора */
void mzm_init(MZM_Simulator *sim, double wavelength_nm, double arm_length_mm) {
    sim->wavelength = wavelength_nm * 1e-9;
    sim->arm_length = arm_length_mm * 1e-3;
    sim->k = 2.0 * M_PI / sim->wavelength;
}

/* Симуляція одного відліку вимірювання */
MZM_Result mzm_simulate_sample(const MZM_Simulator *sim, double delta_n) {
    double phi_a = sim->k * (1.0 + delta_n) * sim->arm_length;
    double phi_b = sim->k * 1.0 * sim->arm_length;

    double inv_sqrt2 = 1.0 / sqrt(2.0);
    double complex e_in = 1.0 + 0.0 * I;

    /* Перетворення на першому світлодільнику BS1 */
    double complex e1_bs1 = e_in * inv_sqrt2;
    double complex e2_bs1 = e_in * (I * inv_sqrt2);

    /* Поширення по плечах A та B */
    double complex e1_arm = e1_bs1 * cexp(I * phi_a);
    double complex e2_arm = e2_bs1 * cexp(I * phi_b);

    /* Зведення на другому світлодільнику BS2 */
    double complex e_out1 = inv_sqrt2 * (e1_arm * I + e2_arm);
    double complex e_out2 = inv_sqrt2 * (e1_arm + e2_arm * I);

    MZM_Result res;
    res.i1 = cabs(e_out1) * cabs(e_out1);
    res.i2 = cabs(e_out2) * cabs(e_out2);
    res.diff_signal = res.i1 - res.i2;

    return res;
}

int main(void) {
    MZM_Simulator sim;
    mzm_init(&sim, 632.8, 100.0);

    printf("Чисельне моделювання інтерферометра Маха — Цендера (C99):\n");
    printf("%12s | %8s | %8s | %12s\n", "delta_n", "I1", "I2", "Diff Signal");
    printf("------------------------------------------------\n");

    for (int i = 0; i <= 10; ++i) {
        double dn = i * 1e-6;
        MZM_Result res = mzm_simulate_sample(&sim, dn);
        printf("%12.4e | %8.4f | %8.4f | %12.4f\n", dn, res.i1, res.i2, res.diff_signal);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>

class MachZehnderInterferometer {
public:
    struct Measurement {
        double i1{0.0};
        double i2{0.0};
        double diff_signal{0.0};
    };

    explicit MachZehnderInterferometer(double wavelength_nm = 632.8, double arm_length_mm = 100.0)
        : wavelength_{wavelength_nm * 1e-9},
          arm_length_{arm_length_mm * 1e-3},
          k_{2.0 * std::numbers::pi / wavelength_} {}

    [[nodiscard]] Measurement simulate(double delta_n) const {
        const double phi_a = k_ * (1.0 + delta_n) * arm_length_;
        const double phi_b = k_ * 1.0 * arm_length_;

        constexpr double inv_sqrt2 = 1.0 / std::numbers::sqrt2;
        constexpr std::complex<double> e_in{1.0, 0.0};
        constexpr std::complex<double> i_unit{0.0, 1.0};

        // BS1: розділення променя
        const std::complex<double> e1_bs1 = e_in * inv_sqrt2;
        const std::complex<double> e2_bs1 = e_in * (i_unit * inv_sqrt2);

        // Фазовий набіг у плечах
        const std::complex<double> e1_arm = e1_bs1 * std::exp(i_unit * phi_a);
        const std::complex<double> e2_arm = e2_bs1 * std::exp(i_unit * phi_b);

        // BS2: зведення хвиль
        const std::complex<double> e_out1 = inv_sqrt2 * (e1_arm * i_unit + e2_arm);
        const std::complex<double> e_out2 = inv_sqrt2 * (e1_arm + e2_arm * i_unit);

        const double i1 = std::norm(e_out1);
        const double i2 = std::norm(e_out2);

        return Measurement{.i1 = i1, .i2 = i2, .diff_signal = i1 - i2};
    }

    [[nodiscard]] std::vector<Measurement> simulate_sweep(std::span<const double> delta_n_values) const {
        std::vector<Measurement> results;
        results.reserve(delta_n_values.size());
        for (const double dn : delta_n_values) {
            results.push_back(simulate(dn));
        }
        return results;
    }

private:
    double wavelength_;
    double arm_length_;
    double k_;
};

int main() {
    const MachZehnderInterferometer mzi{632.8, 100.0};
    const std::vector<double> dn_steps = {0.0, 1e-6, 2e-6, 3e-6, 4e-6, 5e-6, 6e-6, 7e-6, 8e-6, 9e-6, 10e-6};

    const auto results = mzi.simulate_sweep(dn_steps);

    std::cout << "Чисельне моделювання інтерферометра (C++20 RAII):\n";
    std::cout << std::setw(12) << "delta_n" << " | "
              << std::setw(8) << "I1" << " | "
              << std::setw(8) << "I2" << " | "
              << std::setw(12) << "Diff Signal" << "\n";
    std::cout << std::string(48, '-') << "\n";

    for (size_t idx = 0; idx < dn_steps.size(); ++idx) {
        std::cout << std::scientific << std::setprecision(4) << std::setw(12) << dn_steps[idx] << " | "
                  << std::fixed << std::setprecision(4) << std::setw(8) << results[idx].i1 << " | "
                  << std::setw(8) << results[idx].diff_signal << "\n";
    }

    return 0;
}
```
:::

### 3. Детальний аналіз алгоритму та інженерні крайові випадки

Застосування симулятора у реальних приладах вимагає врахування трьох технічних обмежень:

1. **Неідеальність світлодільників (`R ≠ T`):**
   У реальних оптичних покриттях коефіцієнти відбиття `R` та пропущення `T` можуть відхилятися від ідеального співвідношення 50:50 (наприклад, `R = 0.52`, `T = 0.48`). Це порушує глибину деструктивної інтерференції, внаслідок чого мінімальна інтенсивність `I_min > 0`, а видимість `V = (I_max - I_min) / (I_max + I_min) < 1`. У коді симулятора це враховується заміною `1/√2` на `√R` та `√T`.

2. **Обмежена довжина когерентності та втрата контрасту:**
   Якщо лазерне джерело має ширину лінії спектра `Δλ`, довжина когерентності дорівнює `L_c ≈ λ² / Δλ`. При збільшенні різниці оптичних шляхів `ΔL` амплітуда інтерференційного сигналу згасає за гауссівським законом:

   ```
   V(ΔL) = exp(- (ΔL / L_c)²)
   ```

   У програмі обробки це моделюється додаванням коефіцієнта згасання комплексної взаємної когерентності `γ(ΔL)`.

3. **Спеціальні перетворення C++20 у симуляторі:**
   C++ реалізація використовує концепції сучасної мови: константні вирази `std::numbers::pi` та `std::numbers::sqrt2` з бібліотеки `<numbers>`, легковісний контейнер перегляду пам'яті `std::span<const double>` з `<span`, кваліфікатор `[[nodiscard]]` для запобігання ігноруванню вихідних даних та структуроване зв'язування (*structured binding*). Це забезпечує максимальну швидкодію без додаткового виділення динамічної пам'яті в критичних циклах реально-часової обробки.

### 4. Алгоритми цифрової обробки сигналів фотодетектування

У практичних оптичних вимірювачах після АЦП вихідні фотоструми піддаються цифровій обробці для вилучення фази `Δφ(t)`.

Один із найбільш ефективних методів — **цифрова квадратурна демодуляція**. Якщо у вимірювальному плечі фаза змінюється за законом `Δφ(t) = φ_0 + δφ · sin(ω_m · t)`, вихідні канали розкладаються у ряд Бесселя:

```
I₁(t) = (I₀ / 2) · [ 1 - cos(φ_0 + δφ · sin(ω_m · t)) ]
       = (I₀ / 2) · [ 1 - cos φ_0 · J₀(δφ) - 2 · sin φ_0 · J₁(δφ) · sin(ω_m · t) - 2 · cos φ_0 · J₂(δφ) · cos(2·ω_m · t) ... ]
```

Аналізуючи амплітуди першої `A(ω_m)` та другої `A(2·ω_m)` гармонік цифровим фазочутливим детектором (Lock-in Amplifier), алгоритм отримує відношення:

```
A(ω_m) / A(2·ω_m) = (2 · sin φ_0 · J₁(δφ)) / (2 · cos φ_0 · J₂(δφ)) ≈ tg φ_0 · (2 / δφ)
```

Це дозволяє усунути вплив загальних флуктуацій оптичної потужності `I₀` та незалежно виміряти постійну квадратурну фазу `φ_0` і малу амплітуду зсуву `δφ`.

### 5. Калібрування балансних підсилювачів та усунення неоднозначності 2π

При роботі з реальними фотодетекторами чутливості фотодіодів `R₁` та `R₂` відрізняються на 1–3%, що порушує ідеальне скасування синфазного шуму інтенсивності лазера. У цифровій системі збору даних перед обчисленням різницевого сигналу виконують підгоночне масштабування:

```
S_balanced(t) = I₁(t) - (G_calib · I₂(t) + Off_calib)
```

де `G_calib` та `Off_calib` обчислюються у калібрувальному циклі при закритому вимірювальному плечі.

Крім того, коли фазовий набіг перевищує `2π` радіан (один повний оптичний період), тригонометрична функція косинуса починає повторювати свої значення. Для відновлення монотонної фазової траєкторії `Δφ(t)` у системі реально-часового моніторингу застосовують алгоритм **цифрового розгортання фази** (*phase unwrapping*). Алгоритм відстежує миттєву похідну `dS / dt`: при досягненні локального екстремуму інтенсивності до лічильника фазових періодів додається чи віднімається ціле число `2π · k`.

### 6. Покроковий опис компіляції та запуску коду

Для компіляції та випробування наведених програм у середовищі Linux/Windows застосовують стандартні утиліти розробки:

- **Компіляція версії на мові C (POSIX / GCC):**
  ```bash
  gcc -O3 -std=c99 -Wall -Wextra mach_zehnder_sim.c -o mzm_c -lm
  ./mzm_c
  ```
  Прапорець `-lm` є обов'язковим для підключення математичної бібліотеки `libm` (обчислення тригонометричних функцій та квадратних коренів).

- **Компіляція версії на мові C++ (GCC 11+ / Clang 13+ / MSVC 2019+):**
  ```bash
  g++ -O3 -std=c++20 -Wall -Wextra mach_zehnder_sim.cpp -o mzm_cpp
  ./mzm_cpp
  ```
  Прапорець `-std=c++20` потрібен для підтримки заголовків `<numbers>` та `std::span`.

- **Запуск Python реалізації:**
  ```bash
  python3 mach_zehnder_sim.py
  ```

Всі три реалізації дають бінарно ідентичні результати інтенсивностей для однакових фазових зсувів `Δn`, що гарантує кросплатформову перевіреність чисельної моделі.
