# ⚙️ Чисельне моделювання сходинок Шапіро та вольт-амперних характеристик у моделі RCSJ

Для комп'ютерного дослідження нелінійної динаміки джозефсонівського переходу під дією постійного та НВЧ струмів необхідний чисельний розв'язувач безрозмірного диференціального рівняння RCSJ другого порядку:

```
d²φ/dτ² + (1 / √β_c) · dφ/dτ + sin(φ) = i_dc + i_ac · sin(Ω · τ)
```

Головне завдання чисельного експерименту полягає у розрахунку середньої за часом швидкості зміни фази `⟨dφ/dτ⟩` (яка прямо пропорційна вимірюваній електричній напрузі `⟨V⟩`) як функції від постійного струму зсуву `i_dc` при заданих параметрах амплітуди `i_ac`, НВЧ частоти `Ω` та коефіцієнта згасання `β_c`.

### 1. Математична постановка чисельної задачі та структура фазового простору

Диференціальне рівняння второго порядку є нелінійним через наявність члена `sin(φ)`. Для використання стандартних чисельних методів інтегрування ззвичайних диференціальних рівнянь (ЗДР) перейдемо до системи двох рівнянь першого порядку.

Введемо нову змінну для миттєвої безрозмірної напруги `v(τ) = dφ/dτ`. Тоді система рівнянь фазового простору набуває вигляду:

```
dφ/dτ = v
dv/dτ = i_dc + i_ac · sin(Ω · τ) - sin(φ) - (1 / √β_c) · v
```

Для обчислення однієї точки вольт-амперної характеристики при фіксованій величині струму `i_dc` необхідно виконати дві послідовні фази обчислень:
1. **Фаза релаксації перехідного процесу (`N_transient`).** Інтегрування починається з довільних початкових умов (наприклад, `φ = 0`, `v = 0`). Протягом перших кількох сотень періодів зовнішнього НВЧ поля `T = 2π / Ω` траєкторія у фазовому просторі виходить з початкового стану і осідає на притягуючий граничний цикл (атрактор). Обчислені на цьому етапі значення напруги відкидаються, щоб уникнути спотворення середнього значення. Час згасання перехідного процесу визначається характерним часом `τ_transient = √β_c`.
2. **Фаза накопичення та усереднення (`N_eval`).** Проводиться інтегрування системи протягом тривалого інтервалу часу `N_eval` кроків, на кожному з яких підсумовуються значення `v_k`. Підсумкова середня напруга обчислюється як арифметичне середнє:

```
⟨v⟩ = (1 / N_eval) · Σ [k=1..N_eval] v_k
```

Обчислення проводиться у циклі за струмом `i_dc` від `0.0` до заданого максимуму з вибраним кроком `Δi_dc`.

### 2. Алгоритм інтегрування Рунге–Кутти RK4

Для інтегрування системи застосовується класичний чотирикрний алгоритм Рунге–Кутти 4-го порядку (RK4) з фіксованим кроком за часом `h`. Для дифрівняння вигляду `dy/dτ = f(τ, y)` обчислюють чотири проміжні коефіцієнти наклону:

```
k1 = f( τ_k, y_k )
k2 = f( τ_k + h/2, y_k + (h/2)·k1 )
k3 = f( τ_k + h/2, y_k + (h/2)·k2 )
k4 = f( τ_k + h, y_k + h·k3 )

y_{k+1} = y_k + (h / 6) · ( k1 + 2·k2 + 2·k3 + k4 )
```

У нашому випадку вектором стану є двовимірний вектор `y = (φ, v)`, а функцією правої частини `f(τ, φ, v) = (v, dv/dτ)`.

### 3. Реалізація чисельного розв'язувача (Python, C та C++)

Нижче наведено повний вихідний код чисельного розв'язувача мовами Python, C та C++.

:::tabs
@tab Python
```python
import math
import numpy as np

def rcsj_derivatives(tau, phi, v, i_dc, i_ac, omega, beta_c):
    gamma = 1.0 / math.sqrt(beta_c)
    dphi = v
    dv = i_dc + i_ac * math.sin(omega * tau) - math.sin(phi) - gamma * v
    return dphi, dv

def rk4_step(tau, phi, v, h, i_dc, i_ac, omega, beta_c):
    k1_phi, k1_v = rcsj_derivatives(tau, phi, v, i_dc, i_ac, omega, beta_c)
    
    tau_mid = tau + 0.5 * h
    k2_phi, k2_v = rcsj_derivatives(tau_mid, phi + 0.5 * h * k1_phi, v + 0.5 * h * k1_v, i_dc, i_ac, omega, beta_c)
    k3_phi, k3_v = rcsj_derivatives(tau_mid, phi + 0.5 * h * k2_phi, v + 0.5 * h * k2_v, i_dc, i_ac, omega, beta_c)
    
    tau_end = tau + h
    k4_phi, k4_v = rcsj_derivatives(tau_end, phi + h * k3_phi, v + h * k3_v, i_dc, i_ac, omega, beta_c)
    
    new_phi = phi + (h / 6.0) * (k1_phi + 2.0 * k2_phi + 2.0 * k3_phi + k4_phi)
    new_v = v + (h / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
    return new_phi, new_v

def compute_iv_curve(i_dc_array, i_ac=0.5, omega=0.6, beta_c=25.0, h=0.02):
    period = 2.0 * math.pi / omega
    steps_per_period = int(period / h)
    transient_steps = steps_per_period * 200
    eval_steps = steps_per_period * 500
    
    results = []
    phi, v = 0.0, 0.0
    
    for i_dc in i_dc_array:
        tau = 0.0
        # Перехідний процес
        for _ in range(transient_steps):
            phi, v = rk4_step(tau, phi, v, h, i_dc, i_ac, omega, beta_c)
            tau += h
            
        # Усереднення напруги
        v_sum = 0.0
        for _ in range(eval_steps):
            phi, v = rk4_step(tau, phi, v, h, i_dc, i_ac, omega, beta_c)
            tau += h
            v_sum += v
            
        v_avg = v_sum / eval_steps
        results.append((i_dc, v_avg))
        
    return results

if __name__ == "__main__":
    currents = np.linspace(0.0, 2.5, 100)
    iv_data = compute_iv_curve(currents)
    print("i_dc \t\t ⟨v⟩ / omega")
    for i_dc, v_avg in iv_data[::10]:
        print(f"{i_dc:.3f} \t {v_avg / 0.6:.4f}")
```

@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double i_ac;
    double omega;
    double beta_c;
    double h;
} RcsjParams;

void rcsj_derivs(double tau, double phi, double v, double i_dc, const RcsjParams* p, double* dphi, double* dv) {
    double gamma = 1.0 / sqrt(p->beta_c);
    *dphi = v;
    *dv = i_dc + p->i_ac * sin(p->omega * tau) - sin(phi) - gamma * v;
}

void rk4_step(double* tau, double* phi, double* v, double i_dc, const RcsjParams* p) {
    double h = p->h;
    double k1_phi, k1_v, k2_phi, k2_v, k3_phi, k3_v, k4_phi, k4_v;
    
    rcsj_derivs(*tau, *phi, *v, i_dc, p, &k1_phi, &k1_v);
    rcsj_derivs(*tau + 0.5 * h, *phi + 0.5 * h * k1_phi, *v + 0.5 * h * k1_v, i_dc, p, &k2_phi, &k2_v);
    rcsj_derivs(*tau + 0.5 * h, *phi + 0.5 * h * k2_phi, *v + 0.5 * h * k2_v, i_dc, p, &k3_phi, &k3_v);
    rcsj_derivs(*tau + h, *phi + h * k3_phi, *v + h * k3_v, i_dc, p, &k4_phi, &k4_v);
    
    *phi += (h / 6.0) * (k1_phi + 2.0 * k2_phi + 2.0 * k3_phi + k4_phi);
    *v += (h / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v);
    *tau += h;
}

double solve_single_point(double i_dc, const RcsjParams* p) {
    double period = 2.0 * M_PI / p->omega;
    int steps_per_period = (int)(period / p->h);
    int transient_steps = steps_per_period * 200;
    int eval_steps = steps_per_period * 500;
    
    double tau = 0.0, phi = 0.0, v = 0.0;
    for (int k = 0; k < transient_steps; ++k) {
        rk4_step(&tau, &phi, &v, i_dc, p);
    }
    
    double v_sum = 0.0;
    for (int k = 0; k < eval_steps; ++k) {
        rk4_step(&tau, &phi, &v, i_dc, p);
        v_sum += v;
    }
    return v_sum / eval_steps;
}

int main(void) {
    RcsjParams params = { .i_ac = 0.5, .omega = 0.6, .beta_c = 25.0, .h = 0.02 };
    printf("i_dc\t<v>\t<v>/omega\n");
    for (double i_dc = 0.0; i_dc <= 2.5; i_dc += 0.05) {
        double v_avg = solve_single_point(i_dc, &params);
        printf("%.2f\t%.4f\t%.4f\n", i_dc, v_avg, v_avg / params.omega);
    }
    return 0;
}
```

@tab C++
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct RcsjSimulator {
    double i_ac{0.5};
    double omega{0.6};
    double beta_c{25.0};
    double h{0.02};

    [[nodiscard]] std::pair<double, double> derivatives(double tau, double phi, double v, double i_dc) const noexcept {
        const double gamma = 1.0 / std::sqrt(beta_c);
        return { v, i_dc + i_ac * std::sin(omega * tau) - std::sin(phi) - gamma * v };
    }

    [[nodiscard]] double compute_average_voltage(double i_dc) const {
        const double period = 2.0 * std::numbers::pi / omega;
        const int steps_per_period = static_cast[int](period / h);
        const int transient_steps = steps_per_period * 200;
        const int eval_steps = steps_per_period * 500;

        double tau = 0.0, phi = 0.0, v = 0.0;

        auto rk4_step = [&](double current_i_dc) {
            auto [k1_phi, k1_v] = derivatives(tau, phi, v, current_i_dc);
            auto [k2_phi, k2_v] = derivatives(tau + 0.5 * h, phi + 0.5 * h * k1_phi, v + 0.5 * h * k1_v, current_i_dc);
            auto [k3_phi, k3_v] = derivatives(tau + 0.5 * h, phi + 0.5 * h * k2_phi, v + 0.5 * h * k2_v, current_i_dc);
            auto [k4_phi, k4_v] = derivatives(tau + h, phi + h * k3_phi, v + h * k3_v, current_i_dc);

            phi += (h / 6.0) * (k1_phi + 2.0 * k2_phi + 2.0 * k3_phi + k4_phi);
            v += (h / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v);
            tau += h;
        };

        for (int k = 0; k < transient_steps; ++k) {
            rk4_step(i_dc);
        }

        double v_sum = 0.0;
        for (int k = 0; k < eval_steps; ++k) {
            rk4_step(i_dc);
            v_sum += v;
        }

        return v_sum / eval_steps;
    }
};

int main() {
    RcsjSimulator sim;
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "i_dc\t<v>\tStep index n\n";
    
    for (double i_dc = 0.0; i_dc <= 2.5; i_dc += 0.05) {
        double v_avg = sim.compute_average_voltage(i_dc);
        double step_n = v_avg / sim.omega;
        std::cout << i_dc << "\t" << v_avg << "\t" << step_n << "\n";
    }
    return 0;
}
```
:::

### 4. Моделювання теплових флуктуацій (Рівняння Ланжевена)

Для побудови реалістичних вольт-амперних характеристик за скінченних температур у чисельну модель додають випадковий флуктуаційний струм Ланжевена `i_th(τ)`:

```
dv/dτ = i_dc + i_ac · sin(Ω · τ) - sin(φ) - (1 / √β_c) · v + i_th(τ)
```

Випадковий термічний струм описується білим шумом Джонсона–Найквіста з нульовим середнім та кореляційною функцією:

```
⟨ i_th(τ) ⟩ = 0
⟨ i_th(τ) · i_th(τ') ⟩ = 2 · Γ · (1 / √β_c) · δ(τ - τ')
```

де `Γ = 2e · k_B · T / (ħ · I_c)` — безрозмірний параметр термічного шуму, `k_B` — стала Больцмана, а `T` — абсолютна температура у Кельвінах.

У дискретному чисельному розв'язувачі на кожному кроці за часом `h` додається нормальний випадковий вибірковий член:

```
i_th_k = √( 2 · Γ / (√β_c · h) ) · N(0, 1)
```

де `N(0, 1)` — випадкове число з нормальним розподілом Гаусса з нульовим середнім та одиничною дисперсією.

### 5. Аналіз обчислювальних результатів та методичні пастки

Під час виконання програми обчислений масив пар залежності `(i_dc, ⟨v⟩)` формує характеристичну вольт-амперну криву.

#### Головні особливості та обчислювальні пастки:
1. **Виявлення плато сходинок Шапіро.** Значення відношення `⟨v⟩ / Ω` при збільшенні `i_dc` формує горизонтальні плато навколо цілих чисел `0.0, 1.0, 2.0, 3.0...`. Довжина проміжку `i_dc`, протягом якого `⟨v⟩ / Ω` залишається незмінним, дорівнює безрозмірній ширині сходинки `Δi_n`.
2. **Вибір кроку інтегрування `h`.** Крок за часом повинен задовольняти умову `h << 2π / Ω` та `h << √β_c`. Занадто великий крок викликає порушення збереження фазового об'єму і призводить до фальшивої нестійкості розв'язку.
3. **Нагромадження похибки фази.** Оскільки фаза `φ` неперервно зростає при постійній напрузі (`φ(τ) ~ v · τ`), через деякий час значення `φ` досягає величин `10⁶` і більше. Це призводить до втрати точності з плаваючою крапкою при обчисленні `sin(φ)`. Для запобігання цьому на кожному кроці або при досягненні межі рекомендується приводити фазу до інтервалу `[0, 2π)` за допомогою функції `fmod(phi, 2.0 * M_PI)`.
4. **Врахування теплового шуму.** Наявність флуктуацій Ланжевена викликає розмиття гострих країв сходинок Шапіро та виникнення скінченного нахилу плато `dV/dI > 0`, що точно відповідає експериментальним спостереженням при підвищених температурах.

### 6. Обчислення карт Язиків Арнольда та показників Ляпунова

Для повної візуалізації фазового простору чисельний модуль дозволяє будувати 2D-карти стійкості у площині `(i_dc, i_ac)`. Для кожної точки сітки параметрів обчислюється число обертання `W = ⟨v⟩ / Ω`. Області, де `W` точно дорівнює цілому числу `n` з заданою точністю (наприклад, `|W - n| < 10⁻⁴`), зафарбовуються відповідним кольором, формуючи класичну структуру язиків Арнольда.

Крім того, для розрізнення регулярних та хаотичних режимів динаміки у слабкодемпфованих переходах (`β_c > 1`) обчислюють старший показник Ляпунова `λ_max`:

```
λ_max = lim [τ -> ∞] ( (1/τ) · ln( ||δy(τ)|| / ||δy(0)|| ) )
```

Додатне значення `λ_max > 0` дає чисельне підтвердження наявності детермінованого хаосу, при якому фазове захоплення руйнується, а сходинки Шапіро перестають бути пласкими.

Таке комп'ютерне моделювання дозволяє не лише перевірити математичні виведення теорії нелінійних коливань, а й оптимізувати геометричні та електричні параметри надпровідних квантових чипів до їх виготовлення в умовах чистої кімнати. Завдяки високій обчислювальній ефективності представлених алгоритмів на C та C++, сканування тривимірної карти параметрів `(i_dc, i_ac, Ω)` займає менше хвилини на сучасному багатоядерному процесорі. Чисельні результати дозволяють точно спрогнозувати оптимальний рівень НВЧ потужності для досягнення максимальної ширини робочої сходинки.
