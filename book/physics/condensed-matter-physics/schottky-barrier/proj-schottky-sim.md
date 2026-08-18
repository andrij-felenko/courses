# ⚙️ Чисельне моделювання C-V та I-V характеристик бар'єра Шотткі

Цей практичний проєкт присвячено розробці алгоритмів чисельного моделювання вольт-амперних (I-V) та вольт-фарадних (C-V) характеристик контакту метал-напівпровідник, а також автоматизованій екстракції фізичних параметрів бар'єра Шотткі (висоти бар'єра `Φ_Bn`, фактора неідеальності `η`, послідовного опору `R_s` та концентрації донорів `N_d`) із виміряних експериментальних даних.

> 🔧 **Навіщо це.**
> У розробці напівпровідникових приладів та контролі якості металізації (силіцидоутворення) прямого вимірювання фізичної висоти бар'єра у вольтах не існує. Єдиним шляхом визначення якості контакту є вимірювання макроскопічних I-V та C-V характеристик діодної структури з подальшим чисельним розв'язанням оберненої фізичної задачі.

---

## 1. Математична модель реального діода та метод Чуна

Експериментальна вольт-амперна характеристика реального діода Шотткі відхиляється від ідеальної термоелектронної емісії через наявність послідовного опору об'єму напівпровідникової підкладки та анодного і катодного контактів `R_s`. Напруга `V_d`, яка безпосередньо припадає на виснажений шар бар'єра, менша за зовнішню прикладену напругу `V` на величину падіння напруги на послідовному опорі `I · R_s`:

```
V_d = V - I · R_s
```

Рівняння ВАХ реального контакту Шотткі приймає трансцендентну форму:

```
I = I_s · [exp(q · (V - I · R_s) / (η · k_B · T)) - 1]
```

де `I_s = A · A* · T² · exp(-q · Φ_Bn / (k_B · T))` — струм насичення, `A` — площа контакту, `A*` — ефективна стала Річардсона, `η` — фактор неідеальності.

При прямих напругах `V > 3 · k_B T / q` одиницею в дужках можна знехтувати, що дає спрощене співвідношення:

```
I ≈ I_s · exp(q · (V - I · R_s) / (η · k_B · T))
```

Продеференціюємо це рівняння за напругою або струмом. Визначимо допоміжну функцію Чуна `H(I)` та її диференціальну форму `d(V)/d(ln I)`:

```
d(V) / d(ln I) = (η · k_B · T / q) + I · R_s
```

Ця фундаментальна залежність утворює основу чисельного алгоритму екстракції:
1. За виміряним масивом `(V_i, I_i)` обчислюються числові похідні `dV / d(ln I)`.
2. На графіку залежності `dV / d(ln I)` від струму `I` обирається лінійний фрагмент у ділянці середньо-високих струмів.
3. Кутовий нахил лінійного апроксимаційного відрізка дорівнює послідовному опору `R_s` (в Омах).
4. Точка перетину прямої з віссю ординат `I = 0` визначає фактор неідеальності `η = (q / (k_B · T)) · Intercept`.

Для більш точного обчислення висоти бар'єра `Φ_Bn` С. К. Чунг запропонував другу функцію `H(I)`:

```
H(I) = V - (η · k_B · T / q) · ln(I / (A · A* · T²))
```

Підставляючи вираз для ВАХ у `H(I)`, отримуємо лінійне рівняння залежності `H(I)` від струму `I`:

```
H(I) = I · R_s + η · Φ_Bn
```

Будуючи графік `H(I)` від `I`, отримуємо другу пряму лінію. Кутовий нахил цього графіка дає незалежну оцінку послідовного опору `R_s`, а відрізок відсічки на осі ординат при `I = 0` прямо визначає добуток `η · Φ_Bn`. Поділивши отримане значення на раніше вилучений фактор неідеальності `η`, одержуємо точне значення висоти бар'єра Шотткі `Φ_Bn` (в електронвольтах).

---

## 2. Температурні вимірювання та побудова графіків Арреніуса

Для усунення похибок, пов'язаних із нестабільністю площі контакту `A` або невизначеністю ефективної сталої Річардсона `A*`, експериментальні ВАХ вимірюють при декількох температурах у діапазоні від 250 К до 400 К.

Згідно з виразом для струму насичення:

```
I_s = A · A* · T² · exp(-q · Φ_Bn / (k_B · T))
```

Поділивши `I_s` на `T²` та логарифмуючи обидві частини рівняння, отримуємо залежність Арреніуса:

```
ln(I_s / T²) = ln(A · A*) - (q · Φ_Bn / k_B) · (1 / T)
```

Будуючи чисельний графік `ln(I_s / T²)` залежно від оберненої температури `1 / T`, отримуємо пряму лінію:
* Нахил прямої `S_arr = -q · Φ_Bn / k_B` прямо визначає висоту бар'єра Шотткі `Φ_Bn`, незалежно від площі діода.
* Відрізок перетину з віссю `1/T = 0` визначає логарифм добутку `ln(A · A*)`, що дозволяє чисельно виміряти ефективну сталу Річардсона `A*` для даного напівпровідникового матеріалу.

---

## 3. Аналіз C-V характеристик та профілювання легування

Вольт-фарадна характеристика описує зміну бар'єрної ємності виснаженого шару `C` при зміні зворотної напруги зміщення `V_R = -V`. У графічних координатах `1 / C²` від `V_R` залежність утворює пряму лінію:

```
1 / C² = (2 / (q · ε_s · N_d · A²)) · (V_bi - k_B · T / q + V_R)
```

де `ε_s` — діелектрична проникність напівпровідника.

Чисельний модуль виконує лінійну регресію масиву `(V_R, 1/C²)` методом найменших квадратів, визначаючи нахил `S = d(1/C²) / dV_R` та відрізок відсічки `Y_int`:

* **Концентрація донорів**: `N_d = 2 / (q · ε_s · A² · S)`.
* **Вбудований потенціал**: `V_bi = (Y_int / S) + k_B · T / q`.

Якщо легування епітаксійного шару не є однорідним по глибині (наприклад, після іонної імплантації або дифузії), чисельний модуль обчислює локальний профіль розродження донорів `N_d(W)` за локальною похідною у кожній точці виміряної кривої:

```
N_d(W) = - (2 / (q · ε_s · A²)) / (d(1 / C²) / dV_R)
```

Глибина виснаженого шару `W`, яка відповідає даній зворотній напрузі `V_R`, обчислюється безпосередньо з виміряного значення ємності `C`:

```
W(V_R) = ε_s · A / C(V_R)
```

Таким чином, скануючи зворотну напругу `V_R` від 0 до напруги пробою, чисельний алгоритм будує повний глибинний профіль легування напівпровідникової структури `N_d(W)`.

---

## 4. Чисельні алгоритми розв'язання рівнянь та дифметод

При чисельному розв'язанні трансцендентного рівняння ВАХ методом Ньютона-Рафсона функція помилки `f(I)` та її похідна `f'(I)` задаються співвідношеннями:

```
f(I) = I - I_s · [exp(q · (V - I · R_s) / (η · k_B · T)) - 1]
f'(I) = 1 + I_s · (q · R_s / (η · k_B · T)) · exp(q · (V - I · R_s) / (η · k_B · T))
```

Ітераційне уточнення струму здійснюється за формулою:

```
I_{k+1} = I_k - f(I_k) / f'(I_k)
```

Завдяки додатній похідній `f'(I) > 0` та строгому монотонному зростанню функції `f(I)` метод Ньютона-Рафсона збігається квадратично (за 4–6 ітерацій), якщо початкове наближення обрано у фізично допустимій області `I_0 > 0`.

---

## 5. Програмна реалізація модулів розрахунку

Нижче наведено робочі реалізації алгоритму екстракції параметрів та симуляції характеристик трьома мовами: Python, C та C++.

:::tabs
```py
import math
import numpy as np

class SchottkySimulator:
    """Модуль розрахунку та екстракції параметрів бар'єра Шотткі."""
    
    Q = 1.602176634e-19       # Заряд електрона (Кл)
    KB = 1.380649e-23         # Стала Больцмана (Дж/К)
    EPS0 = 8.8541878128e-14   # Діелектрична стала вакууму (Ф/см)

    def __init__(self, area_cm2=1.0e-3, rel_perm=11.7, richardson_a=112.0):
        self.area = area_cm2
        self.eps_s = rel_perm * self.EPS0
        self.a_star = richardson_a

    def generate_iv(self, phi_bn_ev=0.7, eta=1.05, rs_ohm=15.0, temp_k=300.0, v_max=0.6, steps=100):
        """Ґенерує вольт-амперну характеристику за моделлю термоелектронної емісії."""
        vt = (self.KB * temp_k) / self.Q
        is_sat = self.area * self.a_star * (temp_k ** 2) * math.exp(-phi_bn_ev / vt)
        
        voltages = np.linspace(0.0, v_max, steps)
        currents = np.zeros_like(voltages)
        
        for i, v in enumerate(voltages):
            # Чисельне розв'язання трансцендентного рівняння методом Ньютона-Рафсона
            curr = 1.0e-9
            for _ in range(20):
                v_diode = v - curr * rs_ohm
                f_val = curr - is_sat * (math.exp(v_diode / (eta * vt)) - 1.0)
                df_val = 1.0 + is_sat * (rs_ohm / (eta * vt)) * math.exp(v_diode / (eta * vt))
                step = f_val / df_val
                curr -= step
                if abs(step) < 1.0e-12:
                    break
            currents[i] = max(curr, 0.0)
            
        return voltages, currents

    def extract_cheung_params(self, voltages, currents, temp_k=300.0):
        """Екстрагує Rs та eta за допомогою функції Чуна dV/d(ln I)."""
        vt = (self.KB * temp_k) / self.Q
        ln_i = np.log(np.maximum(currents, 1.0e-12))
        
        # Обчислення чисельної похідної dV / d(ln I)
        dvdln_i = np.gradient(voltages, ln_i)
        
        # Вибір прямолінійної ділянки середня напруга
        mask = (voltages > 0.2) & (voltages < 0.5)
        if not np.any(mask):
            mask = np.ones_like(voltages, dtype=bool)
            
        rs_fit, eta_vt_fit = np.polyfit(currents[mask], dvdln_i[mask], 1)
        eta_fit = eta_vt_fit / vt
        
        return {"rs_ohm": rs_fit, "eta": eta_fit}

    def extract_cv_params(self, vr_array, c_array_pf, temp_k=300.0):
        """Екстрагує Nd та Vbi з вольт-фарадної характеристики (1/C² vs VR)."""
        vt = (self.KB * temp_k) / self.Q
        c_farad = np.array(c_array_pf) * 1.0e-12
        inv_c2 = 1.0 / (c_farad ** 2)
        
        # Лінійна регресія: inv_c2 = slope * VR + intercept
        slope, intercept = np.polyfit(vr_array, inv_c2, 1)
        
        # Nd = 2 / (q * eps_s * A² * slope)
        nd_cm3 = 2.0 / (self.Q * self.eps_s * (self.area ** 2) * slope)
        
        # Vbi = intercept / slope + Vt
        v_int = intercept / slope
        v_bi = v_int + vt
        
        return {"nd_cm3": nd_cm3, "v_bi_v": v_bi, "slope": slope}

# Демонстраційний запуск
if __name__ == "__main__":
    sim = SchottkySimulator(area_cm2=1.0e-3)
    v, i = sim.generate_iv(phi_bn_ev=0.72, eta=1.04, rs_ohm=10.0)
    print(f"Сгенеровано {len(v)} точок ВАХ. Струм при V=0.5В: {i[int(len(i)*0.83)]*1e3:.3f} мА")
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define Q_ELEM 1.602176634e-19
#define K_BOLTZ 1.380649e-23
#define EPS_0 8.8541878128e-14

typedef struct {
    double area_cm2;
    double rel_perm;
    double richardson_a;
} schottky_config_t;

typedef struct {
    double nd_cm3;
    double v_bi_v;
    double slope;
} cv_results_t;

/* Обчислення струму насичення Is */
double calc_saturation_current(const schottky_config_t* cfg, double phi_bn_ev, double temp_k) {
    double vt = (K_BOLTZ * temp_k) / Q_ELEM;
    return cfg->area_cm2 * cfg->richardson_a * (temp_k * temp_k) * exp(-phi_bn_ev / vt);
}

/* Симуляція ВАХ методом Ньютона-Рафсона */
int simulate_iv_curve(const schottky_config_t* cfg, double phi_bn_ev, double eta, 
                      double rs_ohm, double temp_k, double* v_out, double* i_out, int count) {
    if (!cfg || !v_out || !i_out || count <= 0) return -1;

    double vt = (K_BOLTZ * temp_k) / Q_ELEM;
    double is_sat = calc_saturation_current(cfg, phi_bn_ev, temp_k);
    double v_step = 0.6 / (count - 1);

    for (int idx = 0; idx < count; ++idx) {
        double v_ext = idx * v_step;
        double curr = 1.0e-9;

        for (int iter = 0; iter < 30; ++iter) {
            double v_diode = v_ext - curr * rs_ohm;
            double exp_term = exp(v_diode / (eta * vt));
            double f_val = curr - is_sat * (exp_term - 1.0);
            double df_val = 1.0 + is_sat * (rs_ohm / (eta * vt)) * exp_term;
            double step = f_val / df_val;
            curr -= step;
            if (fabs(step) < 1.0e-12) break;
        }

        v_out[idx] = v_ext;
        i_out[idx] = (curr > 0.0) ? curr : 0.0;
    }
    return 0;
}

/* Обчислення C-V параметрів */
int extract_cv_parameters(const schottky_config_t* cfg, const double* vr, 
                          const double* c_pf, int count, double temp_k, cv_results_t* res) {
    if (!cfg || !vr || !c_pf || !res || count < 2) return -1;

    double sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_xx = 0.0;
    double eps_s = cfg->rel_perm * EPS_0;
    double vt = (K_BOLTZ * temp_k) / Q_ELEM;

    for (int i = 0; i < count; ++i) {
        double c_f = c_pf[i] * 1.0e-12;
        double y_val = 1.0 / (c_f * c_f);
        double x_val = vr[i];

        sum_x += x_val;
        sum_y += y_val;
        sum_xy += x_val * y_val;
        sum_xx += x_val * x_val;
    }

    double slope = (count * sum_xy - sum_x * sum_y) / (count * sum_xx - sum_x * sum_x);
    double intercept = (sum_y - slope * sum_x) / count;

    res->slope = slope;
    res->nd_cm3 = 2.0 / (Q_ELEM * eps_s * (cfg->area_cm2 * cfg->area_cm2) * slope);
    res->v_bi_v = (intercept / slope) + vt;

    return 0;
}

int main(void) {
    schottky_config_t cfg = { .area_cm2 = 1.0e-3, .rel_perm = 11.7, .richardson_a = 112.0 };
    double v[50], i[50];

    if (simulate_iv_curve(&cfg, 0.70, 1.05, 12.0, 300.0, v, i, 50) == 0) {
        printf("C симуляцію ВАХ успішно виконано. Точок: 50, I(max) = %.4f мА\n", i[49] * 1000.0);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <expected>
#include <numeric>
#include <span>

namespace physics::schottky {

constexpr double Q_ELEM = 1.602176634e-19;
constexpr double K_BOLTZ = 1.380649e-23;
constexpr double EPS_0 = 8.8541878128e-14;

struct DeviceConfig {
    double area_cm2 = 1.0e-3;
    double rel_perm = 11.7;
    double richardson_a = 112.0;
};

struct CvFitResult {
    double nd_cm3;
    double v_bi_v;
    double slope;
};

enum class SimError {
    InvalidData,
    ConvergenceFailed
};

class SchottkySolver {
public:
    explicit SchottkySolver(DeviceConfig config) : cfg_(config) {}

    [[nodiscard]] double saturation_current(double phi_bn_ev, double temp_k) const noexcept {
        const double vt = (K_BOLTZ * temp_k) / Q_ELEM;
        return cfg_.area_cm2 * cfg_.richardson_a * (temp_k * temp_k) * std::exp(-phi_bn_ev / vt);
    }

    [[nodiscard]] std::expected<std::pair<std::vector<double>, std::vector<double>>, SimError>
    simulate_iv(double phi_bn_ev, double eta, double rs_ohm, double temp_k, double v_max, std::size_t steps) const {
        if (steps < 2 || v_max <= 0.0) return std::unexpected(SimError::InvalidData);

        std::vector<double> voltages(steps);
        std::vector<double> currents(steps);

        const double vt = (K_BOLTZ * temp_k) / Q_ELEM;
        const double is_sat = saturation_current(phi_bn_ev, temp_k);
        const double v_step = v_max / static_cast<double>(steps - 1);

        for (std::size_t idx = 0; idx < steps; ++idx) {
            const double v_ext = static_cast<double>(idx) * v_step;
            double curr = 1.0e-9;

            bool converged = false;
            for (int iter = 0; iter < 35; ++iter) {
                const double v_diode = v_ext - curr * rs_ohm;
                const double exp_term = std::exp(v_diode / (eta * vt));
                const double f_val = curr - is_sat * (exp_term - 1.0);
                const double df_val = 1.0 + is_sat * (rs_ohm / (eta * vt)) * exp_term;
                const double step = f_val / df_val;
                curr -= step;
                if (std::abs(step) < 1.0e-12) {
                    converged = true;
                    break;
                }
            }
            if (!converged) return std::unexpected(SimError::ConvergenceFailed);

            voltages[idx] = v_ext;
            currents[idx] = std::max(curr, 0.0);
        }

        return std::make_pair(std::move(voltages), std::move(currents));
    }

    [[nodiscard]] std::expected<CvFitResult, SimError>
    extract_cv(std::span<const double> vr, std::span<const double> c_pf, double temp_k) const {
        if (vr.size() != c_pf.size() || vr.size() < 2) return std::unexpected(SimError::InvalidData);

        const std::size_t n = vr.size();
        double sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_xx = 0.0;

        for (std::size_t idx = 0; idx < n; ++idx) {
            const double c_farad = c_pf[idx] * 1.0e-12;
            const double y_val = 1.0 / (c_farad * c_farad);
            const double x_val = vr[idx];

            sum_x += x_val;
            sum_y += y_val;
            sum_xy += x_val * y_val;
            sum_xx += x_val * x_val;
        }

        const double count = static_cast<double>(n);
        const double slope = (count * sum_xy - sum_x * sum_y) / (count * sum_xx - sum_x * sum_x);
        const double intercept = (sum_y - slope * sum_x) / count;

        const double eps_s = cfg_.rel_perm * EPS_0;
        const double vt = (K_BOLTZ * temp_k) / Q_ELEM;

        CvFitResult res;
        res.slope = slope;
        res.nd_cm3 = 2.0 / (Q_ELEM * eps_s * (cfg_.area_cm2 * cfg_.area_cm2) * slope);
        res.v_bi_v = (intercept / slope) + vt;

        return res;
    }

private:
    DeviceConfig cfg_;
};

} // namespace physics::schottky

int main() {
    using namespace physics::schottky;
    SchottkySolver solver(DeviceConfig{.area_cm2 = 1.0e-3, .rel_perm = 11.7, .richardson_a = 112.0});

    auto res = solver.simulate_iv(0.70, 1.04, 15.0, 300.0, 0.6, 50);
    if (res) {
        const auto& [v, i] = *res;
        std::cout << "C++23 симуляцію пройдено. Точок: " << v.size() 
                  << ", Макс струм: " << i.back() * 1e3 << " мА\n";
    }
    return 0;
}
```
:::

---

## 6. Порівняльний аналіз чисельних методів та практичні нюанси

При практичній реалізації чисельної обробки вимірювальних даних необхідно враховувати фізичні та обчислювальні особливості:

1. **Метод Ньютона-Рафсона для трансцендентного рівняння ВАХ**:
   Через експоненційне зростання струму початкове наближення `I_0` має бути вибране достатньо малим (`10⁻⁹ А`). Якщо початкова точка занадто велика, перший крок метод Ньютона може загнати від'ємне значення аргументу експоненти в область машинної нескінченності або нульової похідної.
2. **Вплив геометричних країв та індуктивності виводів**:
   Вимірювання C-V характеристик на високих частотах (f > 1 МГц) мінімізує внесок глибоких пасток у забороненій зоні, що забезпечує точне визначення об'ємного легування `N_d`. Вимірювання вимагає попередньої калібровки забійної ємності корпусних виводів `C_pad` та індуктивності `L_lead`. Нехтування ємністю паду `C_pad` призводить до штучного заниження екстрагованої концентрації донорів `N_d`.
3. **Екстракція залежності `N_d(x)` у нерівномірно легованих структурах**:
   Чисельне диференціювання експериментального масиву `1 / C²` піддається сильному зашумленню. Для уникання осциляцій застосовують згладжувальні сплайни або фільтр Савицького-Голея перед вирахуванням похідної `d(1/C²)/dV_R`.
