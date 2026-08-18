# ⚙️ Чисельна симуляція Вольт-Амперних характеристик та ромбів Кулона

Чисельний алгоритм і програмна реалізація мовами Python, C та C++ розраховують Вольт-Амперні характеристики одноелектронного транзистора (SET) та будують двовимірні карти стабільності (ромби Кулона) на основі ортодоксальної теорії й кінетичного рівняння балансу станів.

## 1. Фізична модель та кінетичні рівняння балансу

Обчислення струму через одноелектронний транзистор ґрунтується на розв'язанні стаціонарного кінетичного рівняння балансу (*Master Equation*) для ймовірностей `P(n)` знаходження `n` надлишкових електронів на острівці.

У системі одноелектронного транзистора заряд на острівці може змінюватися дискретно на величину `±e` через тунелювання електрона крізь один із двох бар'єрів. Для кожного зарядового стану `n` тунельні процеси змінюють кількість електронів `n -> n ± 1`.

Швидкість тунелювання електрона крізь тунельний бар'єр з опором `R_T` при зміні вільної енергії системи `ΔF` обчислюється за золотим правилом Фермі у рамках ортодоксальної теорії:

```
Γ(ΔF) = ΔF / (e² · R_T · (1 - exp(-ΔF / (k_B · T))))
```

### Граничні випадки для функції швидкості тунелювання:

1. **Високоенергетичний режим виділення енергії (`ΔF << -k_B T`):** Експоненційний член `exp(-ΔF / (k_B T))` прямує до нескінченності, і швидкість переходу стає лінійною функцією спаду енергії:

```
Γ(ΔF) ≈ - ΔF / (e² · R_T)
```

2. **Заблокований режим (`ΔF >> k_B T`):** Зміна енергії є додатною (потрібно витратити енергію). За нульової температури перехід повністю заборонений: `Γ(ΔF) = 0`. При скінченній температурі швидкість експоненційно придушена термічним фактором Больцмана:

```
Γ(ΔF) ≈ (ΔF / (e² · R_T)) · exp(-ΔF / (k_B · T))
```

Для кожного зарядового стану `n` обчислюють сумарні швидкості переходів:
- `W⁺(n) = Γ₁⁺(n) + Γ₂⁺(n)` — сумарна швидкість збільшення заряду `n -> n + 1` (інжекція електрона з витоку або стоку).
- `W⁻(n) = Γ₁⁻(n) + Γ₂⁻(n)` — сумарна швидкість зменшення заряду `n -> n - 1` (виліт електрона на витік або стік).

У стаціонарному режимі сумарний потік імовірності між сусідніми зарядовими станами дорівнює нулю:

```
P(n) · W⁺(n) = P(n + 1) · W⁻(n + 1)
```

Звідси стаціонарна ймовірність `P(n)` виражається через відношення швидкостей:

```
P(n + 1) = P(n) · (W⁺(n) / W⁻(n + 1))
```

Нормувальна умова для суми ймовірностей усіх можливих зарядових станів:

```
∑_n P(n) = 1
```

Після розрахунку нормованого розподілу ймовірностей `P(n)` результуючий струм стоку `I_ds` обчислюється як різниця прямих і зворотних переходів крізь перший бар'єр (витік):

```
I_ds = e · ∑_n P(n) · (Γ₁⁺(n) - Γ₁⁻(n))
```

Для чисельного розв'язання обмежують діапазон зарядових станів кінцевим інтервалом `-N_max ≤ n ≤ N_max`. Для типових умов низьких температур достатньо враховувати стани від `N_max = 5` до `N_max = 10`.

Матриця швидкостей переходів формується за значеннями зміні енергій для чотирьох тунельних процесів: збільшення/зменшення заряду через Бар'єр 1 (Source) та збільшення/зменшення заряду через Бар'єр 2 (Drain). Застосування алгоритму ітераційного розрахунку дозволяє уникнути прямого обернення великих розріджених матриць, забезпечуючи високу обчислювальну ефективність при генерації двовимірних карт стабільності розміром 1000 × 1000 точок.

## 2. Обчислювальна оптимізація та запобігання втраті точності

При чисельному обчисленні тунельного функціоналу `Γ(ΔF)` виникають дві комп'ютерні проблеми обчислювальної математики:

1. **Невизначеність типу `0 / 0` при `ΔF -> 0`:** При малих значеннях зміні енергії знаменник `1 - exp(-ΔF / k_B T)` наближається до нуля. У програмній реалізації застосовують граничний перехід за правилом Лопіталя при `|ΔF / k_B T| < 10⁻³⁰`:

```
lim_{ΔF -> 0} Γ(ΔF) = (k_B · T) / (e² · R_T)
```

2. **Переповнення експоненти (Floating-point Overflow):** Якщо відношення `arg = ΔF / (k_B T)` перевищує значення `+100`, член `exp(arg)` викликає числове переповнення змінної типу `double`. Для усунення цієї помилки вводять порогові розгалуження, що явно повертають `0.0` при великих додатних енергетичних бар'єрах.

3. **Спрямований розрахунок ймовірностей:** Для запобігання нагромадженню помилок округлення при низьких температурах ітераційний розрахунок ведеться у два боки від найбільш імовірного нейтрального стану `n = 0`. Спочатку розраховують ненормовані відносні ймовірності для додатних станів `n > 0`, а потім для від'ємних станів `n < 0`. Наприкінці обчислюють нормувальну суму `S = ∑ P(n)` та виконують масштабування масиву `P[i] /= S`.

## 3. Реалізація алгоритму симуляції

Наведений нижче приклад демонструє алгоритм чисельного розрахунку матриці струму `I_ds(V_g, V_ds)` та побудови карти ромбів Кулона.

:::tabs
```py
import numpy as np
import math

class SETSimulator:
    """
    Симулятор одноелектронного транзистора (SET) на основі ортодоксальної теорії.
    """
    def __init__(self, C1=1e-18, C2=1e-18, Cg=2e-18, R1=100e3, R2=100e3, Temp=0.5):
        self.C1 = C1
        self.C2 = C2
        self.Cg = Cg
        self.C_total = C1 + C2 + Cg
        self.R1 = R1
        self.R2 = R2
        self.Temp = Temp
        self.e = 1.602176634e-19
        self.kB = 1.380649e-23
        self.Ec = (self.e ** 2) / (2.0 * self.C_total)

    def _rate(self, delta_F, R_tunnel):
        """Обчислення швидкості тунелювання за теорією Фермі."""
        if abs(delta_F) < 1e-30:
            return (self.kB * self.Temp) / (self.e ** 2 * R_tunnel)
        
        arg = delta_F / (self.kB * self.Temp)
        if arg > 100.0:
            return 0.0
        elif arg < -100.0:
            return -delta_F / (self.e ** 2 * R_tunnel)
        else:
            return delta_F / (self.e ** 2 * R_tunnel * (1.0 - math.exp(-arg)))

    def calculate_current(self, Vds, Vg, n_max=10):
        """Розрахунок струму I_ds при заданих напругах Vds та Vg."""
        n_values = np.arange(-n_max, n_max + 1)
        num_states = len(n_values)
        
        gamma_1_plus = np.zeros(num_states)
        gamma_1_minus = np.zeros(num_states)
        gamma_2_plus = np.zeros(num_states)
        gamma_2_minus = np.zeros(num_states)

        Vs = Vds / 2.0
        Vd = -Vds / 2.0

        for idx, n in enumerate(n_values):
            # Перехід n -> n + 1 через Перехід 1 (Source)
            dF_1_plus = self.Ec * (1.0 + 2.0 * (n - (self.Cg * Vg + self.C1 * Vs + self.C2 * Vd) / self.e)) - self.e * Vs
            gamma_1_plus[idx] = self._rate(dF_1_plus, self.R1)

            # Перехід n -> n - 1 через Перехід 1 (Source)
            dF_1_minus = self.Ec * (1.0 - 2.0 * (n - (self.Cg * Vg + self.C1 * Vs + self.C2 * Vd) / self.e)) + self.e * Vs
            gamma_1_minus[idx] = self._rate(dF_1_minus, self.R1)

            # Перехід n -> n + 1 через Перехід 2 (Drain)
            dF_2_plus = self.Ec * (1.0 + 2.0 * (n - (self.Cg * Vg + self.C1 * Vs + self.C2 * Vd) / self.e)) - self.e * Vd
            gamma_2_plus[idx] = self._rate(dF_2_plus, self.R2)

            # Перехід n -> n - 1 через Перехід 2 (Drain)
            dF_2_minus = self.Ec * (1.0 - 2.0 * (n - (self.Cg * Vg + self.C1 * Vs + self.C2 * Vd) / self.e)) + self.e * Vd
            gamma_2_minus[idx] = self._rate(dF_2_minus, self.R2)

        # Розв'язок стаціонарного рівняння балансу
        P = np.zeros(num_states)
        P[n_max] = 1.0  # початкове значення для n=0

        # Прямий хід для n > 0
        for i in range(n_max, num_states - 1):
            W_plus = gamma_1_plus[i] + gamma_2_plus[i]
            W_minus = gamma_1_minus[i + 1] + gamma_2_minus[i + 1]
            if W_minus > 0:
                P[i + 1] = P[i] * (W_plus / W_minus)

        # Зворотний хід для n < 0
        for i in range(n_max, 0, -1):
            W_minus = gamma_1_minus[i] + gamma_2_minus[i]
            W_plus = gamma_1_plus[i - 1] + gamma_2_plus[i - 1]
            if W_plus > 0:
                P[i - 1] = P[i] * (W_minus / W_plus)

        # Нормування ймовірностей
        sum_P = np.sum(P)
        if sum_P > 0:
            P /= sum_P

        # Обчислення результуючого струму
        I_ds = self.e * np.sum(P * (gamma_1_plus - gamma_1_minus))
        return I_ds

    def simulate_coulomb_diamonds(self, Vg_vec, Vds_vec):
        """Генерація 2D матриці струму для графіку ромбів Кулона."""
        I_matrix = np.zeros((len(Vds_vec), len(Vg_vec)))
        for i, Vds in enumerate(Vds_vec):
            for j, Vg in enumerate(Vg_vec):
                I_matrix[i, j] = self.calculate_current(Vds, Vg)
        return I_matrix

if __name__ == "__main__":
    sim = SETSimulator(Temp=0.1)
    Vg_vec = np.linspace(-0.1, 0.1, 100)
    Vds_vec = np.linspace(-0.05, 0.05, 100)
    I_map = sim.simulate_coulomb_diamonds(Vg_vec, Vds_vec)
    print(f"Розраховано карту {I_map.shape}, макс струм: {np.max(np.abs(I_map))*1e9:.3f} нА")
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define E_CHARGE 1.602176634e-19
#define KB_CONST 1.380649e-23

typedef struct {
    double C1, C2, Cg, C_total;
    double R1, R2;
    double Temp, Ec;
} SETParams;

static double tunnel_rate(double delta_F, double R_tunnel, double Temp) {
    if (fabs(delta_F) < 1e-30) {
        return (KB_CONST * Temp) / (E_CHARGE * E_CHARGE * R_tunnel);
    }
    double arg = delta_F / (KB_CONST * Temp);
    if (arg > 100.0) return 0.0;
    if (arg < -100.0) return -delta_F / (E_CHARGE * E_CHARGE * R_tunnel);
    return delta_F / (E_CHARGE * E_CHARGE * R_tunnel * (1.0 - exp(-arg)));
}

double calculate_set_current(const SETParams *sp, double Vds, double Vg, int n_max) {
    int num_states = 2 * n_max + 1;
    double *P = (double*)malloc(sizeof(double) * num_states);
    double *g1_plus = (double*)malloc(sizeof(double) * num_states);
    double *g1_minus = (double*)malloc(sizeof(double) * num_states);
    double *g2_plus = (double*)malloc(sizeof(double) * num_states);
    double *g2_minus = (double*)malloc(sizeof(double) * num_states);

    double Vs = Vds / 2.0;
    double Vd = -Vds / 2.0;

    for (int i = 0; i < num_states; i++) {
        int n = i - n_max;
        double n_ind = (sp->Cg * Vg + sp->C1 * Vs + sp->C2 * Vd) / E_CHARGE;
        
        double dF1_p = sp->Ec * (1.0 + 2.0 * (n - n_ind)) - E_CHARGE * Vs;
        double dF1_m = sp->Ec * (1.0 - 2.0 * (n - n_ind)) + E_CHARGE * Vs;
        double dF2_p = sp->Ec * (1.0 + 2.0 * (n - n_ind)) - E_CHARGE * Vd;
        double dF2_m = sp->Ec * (1.0 - 2.0 * (n - n_ind)) + E_CHARGE * Vd;

        g1_plus[i]  = tunnel_rate(dF1_p, sp->R1, sp->Temp);
        g1_minus[i] = tunnel_rate(dF1_m, sp->R1, sp->Temp);
        g2_plus[i]  = tunnel_rate(dF2_p, sp->R2, sp->Temp);
        g2_minus[i] = tunnel_rate(dF2_m, sp->R2, sp->Temp);
        P[i] = 0.0;
    }

    P[n_max] = 1.0;
    for (int i = n_max; i < num_states - 1; i++) {
        double W_p = g1_plus[i] + g2_plus[i];
        double W_m = g1_minus[i + 1] + g2_minus[i + 1];
        if (W_m > 0.0) P[i + 1] = P[i] * (W_p / W_m);
    }
    for (int i = n_max; i > 0; i--) {
        double W_m = g1_minus[i] + g2_minus[i];
        double W_p = g1_plus[i - 1] + g2_plus[i - 1];
        if (W_p > 0.0) P[i - 1] = P[i] * (W_m / W_p);
    }

    double sum_P = 0.0;
    for (int i = 0; i < num_states; i++) sum_P += P[i];
    for (int i = 0; i < num_states; i++) P[i] /= sum_P;

    double I_ds = 0.0;
    for (int i = 0; i < num_states; i++) {
        I_ds += E_CHARGE * P[i] * (g1_plus[i] - g1_minus[i]);
    }

    free(P); free(g1_plus); free(g1_minus); free(g2_plus); free(g2_minus);
    return I_ds;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <algorithm>

class SingleElectronTransistor {
public:
    struct Configuration {
        double C1{1e-18};
        double C2{1e-18};
        double Cg{2e-18};
        double R1{100e3};
        double R2{100e3};
        double Temp{0.1};
    };

    explicit SingleElectronTransistor(Configuration config) 
        : cfg_(config), 
          c_total_(config.C1 + config.C2 + config.Cg),
          ec_((e_charge_ * e_charge_) / (2.0 * c_total_)) {}

    [[nodiscard]] double calculateCurrent(double Vds, double Vg, int n_max = 10) const {
        const int num_states = 2 * n_max + 1;
        std::vector<double> P(num_states, 0.0);
        std::vector<double> g1_plus(num_states), g1_minus(num_states);
        std::vector<double> g2_plus(num_states), g2_minus(num_states);

        const double Vs = Vds / 2.0;
        const double Vd = -Vds / 2.0;

        for (int i = 0; i < num_states; ++i) {
            const int n = i - n_max;
            const double n_ind = (cfg_.Cg * Vg + cfg_.C1 * Vs + cfg_.C2 * Vd) / e_charge_;
            
            const double dF1_p = ec_ * (1.0 + 2.0 * (n - n_ind)) - e_charge_ * Vs;
            const double dF1_m = ec_ * (1.0 - 2.0 * (n - n_ind)) + e_charge_ * Vs;
            const double dF2_p = ec_ * (1.0 + 2.0 * (n - n_ind)) - e_charge_ * Vd;
            const double dF2_m = ec_ * (1.0 - 2.0 * (n - n_ind)) + e_charge_ * Vd;

            g1_plus[i]  = computeRate(dF1_p, cfg_.R1);
            g1_minus[i] = computeRate(dF1_m, cfg_.R1);
            g2_plus[i]  = computeRate(dF2_p, cfg_.R2);
            g2_minus[i] = computeRate(dF2_m, cfg_.R2);
        }

        P[n_max] = 1.0;
        for (int i = n_max; i < num_states - 1; ++i) {
            const double W_p = g1_plus[i] + g2_plus[i];
            const double W_m = g1_minus[i + 1] + g2_minus[i + 1];
            if (W_m > 0.0) P[i + 1] = P[i] * (W_p / W_m);
        }
        for (int i = n_max; i > 0; --i) {
            const double W_m = g1_minus[i] + g2_minus[i];
            const double W_p = g1_plus[i - 1] + g2_plus[i - 1];
            if (W_p > 0.0) P[i - 1] = P[i] * (W_m / W_p);
        }

        double sum_P = 0.0;
        for (double val : P) sum_P += val;
        if (sum_P > 0.0) {
            for (double& val : P) val /= sum_P;
        }

        double I_ds = 0.0;
        for (int i = 0; i < num_states; ++i) {
            I_ds += e_charge_ * P[i] * (g1_plus[i] - g1_minus[i]);
        }
        return I_ds;
    }

private:
    static constexpr double e_charge_ = 1.602176634e-19;
    static constexpr double kb_const_ = 1.380649e-23;

    Configuration cfg_;
    double c_total_;
    double ec_;

    [[nodiscard]] double computeRate(double delta_F, double R_tunnel) const {
        if (std::abs(delta_F) < 1e-30) {
            return (kb_const_ * cfg_.Temp) / (e_charge_ * e_charge_ * R_tunnel);
        }
        const double arg = delta_F / (kb_const_ * cfg_.Temp);
        if (arg > 100.0) return 0.0;
        if (arg < -100.0) return -delta_F / (e_charge_ * e_charge_ * R_tunnel);
        return delta_F / (e_charge_ * e_charge_ * R_tunnel * (1.0 - std::exp(-arg)));
    }
};

int main() {
    SingleElectronTransistor::Configuration cfg;
    cfg.Temp = 0.05; // 50 мілікельвінів
    SingleElectronTransistor set_sim(cfg);

    double current = set_sim.calculateCurrent(0.01, 0.02);
    std::cout << "Розрахований струм SET: " << current * 1e9 << " нА\n";
    return 0;
}
```
:::

## 4. Фізичний аналіз результатів симуляції

Аналіз чисельно побудованої карти ромбів Кулона виявляє такі фундаментальні закономірності:

1. **Ефект температурного розмивання:** При підвищенні температури від `T = 0.1` К до `T = 4.2` К тунельний функціонал `Γ(ΔF)` перестає бути сходинковим. Експоненційний хвіст розподілу Фермі — Дірака викликає появу термічно активованого струму всередині ромбів. При `k_B · T ≥ E_C` ромби Кулона повністю розмиваються, і ВАХ транзистора стає класичною омічною прямою.
2. **Асиметрія тунельних опірностей (Кулонівські сходинки):** Якщо тунельні опори бар'єрів суттєво відрізняються (наприклад, `R₁ >> R₂`), електрон швидко тунелює крізь другий бар'єр, але надовго застрягає на першому. Це викликає виникнення **кулонівського сходинчастого транспорту** (*Coulomb Staircase*) на вольт-амперних характеристиках `I_ds(V_ds)`. На характеристиці з'являються чіткі плато струму, що відповідають формуванню цілих стаціонарних заповнень острівця.
3. **Визначення динамічного опору:** Диференціальна провідність `dI_ds / dV_ds` на вершинах ромбів сягає максимального значення `G_max ≈ 1 / (R₁ + R₂)`, що дає змогу виміряти параметри бар'єрів експериментального пристрою.
4. **Виділення паразитичних зв'язків:** Врахування асиметрії ємностей `C₁ ≠ C₂` у симуляторі призводить до зміщення та нахилу ромбів відносно горизонтальної осі `V_ds = 0`, що повністю відтворює реальні експериментальні карти стабільності, виміряні в розчинних кріостатах.
5. **Вплив затворної ємності на періодичність:** Зміна ємності затвора `C_g` у симуляторі дозволяє модифікувати геометричний період осциляцій `ΔV_g = e / C_g`. Це дає змогу оцінювати ефективність ємнісного зв'язку між контрольною лінією та квантовим острівцем при проектуванні реальних інтегральних наносхем.
6. **Алгоритмічна стійкість при наднизьких температурах:** При `T -> 0` тунельні швидкості переходів `Γ(ΔF)` для `ΔF > 0` прямують до нуля, а відношення `W⁺ / W⁻` стає невизначеним. Програми використовують адаптивний підібраний поріг зрізання для збереження числової стійкості без виклику винятків ділення на нуль, забезпечуючи точний розрахунок кулонівської щілини навіть у межі абсолютного нуля температур.
