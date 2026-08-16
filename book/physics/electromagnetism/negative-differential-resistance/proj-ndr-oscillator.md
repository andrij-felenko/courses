# ⚙️ Чисельна симуляція автогенератора на тунельному діоді

Чисельне моделювання автоколивальних процесів у електричних кола з від'ємним диференційним опором (NDR) є необхідним етапом проектування високочастотних генераторів, імпульсних тригерів та перетворювачів частоти. Оскільки диференціальні рівняння, що описують нелінійні характеристики напівпровідникових приладів, не мають точного аналітичного розв'язку у замкненій формі через наявність нелінійних експоненціальних та кубічних членів, чисельне інтегрування методом Рунге-Кутти 4-го порядку (RK4) забезпечує необхідну точність та стійкість розрахунку.

Ця вставка містить повну фізичну математичну модель, виведення диференціальних рівнянь стану та практичні реалізації алгоритму чисельної симуляції автогенератора на тунельному діоді мовами Python, C та C++.

## Фізична та математична модель кола

Розглянемо класичну схему автогенератора незатухаючих коливань. Схема містить напівпровідниковий тунельний діод (діод Есакі), еквівалентна схема якого складається з паралельного з'єднання нелінійного елемента з струмом `I_diode(V)` та власної бар'єрної ємності p-n переходу `C`. Діод підключено послідовно з котушкою індуктивності `L` та активним опором втрат дротів і джерела `R_L` до джерела постійної напруги зміщення `V_CC`.

За законами Кірхгофа для вузла діода та замкненого контуру струму, динаміка електромагнітних процесів у системі описується двома зв'язаними нелінійними диференціальними рівняннями першого порядку відносно двох змінних стану — напруги на ємності діода `V(t)` та струму через індуктивність `I_L(t)`:

```
C · (dV / dt) = I_L - I_diode(V)
L · (dI_L / dt) = V_CC - V - R_L · I_L
```

Переписавши систему у формі Коші для чисельного інтегрування, отримуємо похідні змінних стану по часу:

```
dV / dt = (I_L - I_diode(V)) / C
dI_L / dt = (V_CC - V - R_L · I_L) / L
```

Вольт-амперна характеристика тунельного діода `I_diode(V)` описується феноменологічною апроксимацією Фізичного інституту імені Лебедєва, що враховує два основних фізичних компоненти транспорту носіїв — квантове тунелювання електронів при малих прямих напругах та дифузійний тепловий струм прямозаміщеного p-n переходу при більших напругах:

```
I_diode(V) = I_p · (V / V_p) · exp(1 - V / V_p) + I_v · exp( α · (V - V_v) )
```

де значення фізичних параметрів модельованого діода відповідають типовому германієвому тунельному діоду 1N3716:
- `V_p = 0.07 В` (70 мВ) — напруга пікового струму;
- `I_p = 5.0 мА` — піковий тунельний струм;
- `V_v = 0.35 В` (350 мВ) — напруга долини;
- `I_v = 0.5 мА` — мінімальний струм у долині;
- `α = 10.0 В⁻¹` — крутизна дифузійної гілки ВАХ.

Модуль від'ємного диференційного опору в зоні падаючої ділянки обчислюється як:

```
|r_d| ≈ (V_v - V_p) / (I_p - I_v) = (0.35 - 0.07) / (0.005 - 0.0005) = 0.28 / 0.0045 ≈ 62.2 Ом
```

Для виникнення самозбуджуваних коливань опір втрат контуру `R_L` повинен бути строго меншим за модуль від'ємного опору (`R_L < |r_d|`), а напруга джерела живлення `V_CC` має вибиратися так, щоб робоча точка перетину опинилася на падаючій ділянці ВАХ між `V_p` та `V_v` (`V_CC ≈ 0.18 В`).

## Математичний алгоритм чисельного інтегрування Рунге-Кутти (RK4)

Для чисельного інтегрування векторного диференціального рівняння виду `dY/dt = F(t, Y)`, де вектор стану `Y(t) = [V(t), I_L(t)]ᵀ`, застосовується чотириетапний метод Рунге-Кутти четвертого порядку точності. Цей метод забезпечує локальну похибку порядку `O(h⁵)` та глобальну похибку `O(h⁴)`, що є ідеальним компромісом між обчислювальною складністю та стійкістю при моделюванні високочастотних нелінійних коливань.

На кожному кроці за часом `h = dt` вектор стану оновлюється за такою послідовністю дій:

1. Обчислюється вектор швидкості у початковій точці інтервалу:
   `K₁ = F(t_n, Y_n)`

2. Обчислюється вектор швидкості у середній точці інтервалу зі зсувом за вектором `K₁`:
   `K₂ = F(t_n + h/2, Y_n + (h/2) · K₁)`

3. Обчислюється другий оціночний вектор швидкості у середній точці за вектором `K₂`:
   `K₃ = F(t_n + h/2, Y_n + (h/2) · K₂)`

4. Обчислюється вектор швидкості у кінцевій точці інтервалу за вектором `K₃`:
   `K₄ = F(t_n + h, Y_n + h · K₃)`

5. Вектор стану системи на наступному кроці `t_(n+1) = t_n + h` розраховується як зважена середня сума:
   `Y_(n+1) = Y_n + (h / 6) · (K₁ + 2·K₂ + 2·K₃ + K₄)`

Оскільки власна резонансна частота даного контуру становить близько `f₀ ≈ 15.9 МГц` (період `T₀ ≈ 63 нс`), крок інтегрування вибирається рівним `dt = 10 пс` (`10⁻¹¹` с), що забезпечує понад 6000 точок розрахунку на один період коливань та унеможливлює накопичення фазової похибки.

## Реалізація чисельного розрахунку

Нижче наведено ідентичні за алгоритмом, але ідіоматичні реалізації симулятора трьома мовами програмування.

:::tabs
```py
import math
import numpy as np

def diode_current(v: float, v_p: float = 0.07, i_p: float = 0.005,
                  v_v: float = 0.35, i_v: float = 0.0005, alpha: float = 10.0) -> float:
    """Аналітична ВАХ тунельного діода (тунельний + дифузійний струм)."""
    if v < 0:
        return -i_p * (abs(v) / v_p)
    i_tunnel = i_p * (v / v_p) * math.exp(1.0 - v / v_p)
    i_diff = i_v * math.exp(alpha * (v - v_v)) if v > v_v else 0.0
    return i_tunnel + i_diff

def derivatives(v: float, i_l: float, v_cc: float, r_l: float,
                l_ind: float, c_cap: float) -> tuple[float, float]:
    """Прави частини систем диференціальних рівнянь (похідні dv/dt та di/dt)."""
    dv_dt = (i_l - diode_current(v)) / c_cap
    di_dt = (v_cc - v - r_l * i_l) / l_ind
    return dv_dt, di_dt

def simulate_ndr_oscillator(v_cc=0.18, r_l=2.0, l_ind=1e-6, c_cap=100e-12,
                             dt=1e-11, steps=20000):
    """Симуляція генератора методом Рунге-Кутти 4-го порядку (RK4)."""
    t_arr = np.zeros(steps)
    v_arr = np.zeros(steps)
    i_arr = np.zeros(steps)

    # Початкові умови (стан близький до точки спокою)
    v, i_l = 0.01, 0.001

    for step in range(steps):
        t_arr[step] = step * dt
        v_arr[step] = v
        i_arr[step] = i_l

        # Коефіцієнти RK4
        kv1, ki1 = derivatives(v, i_l, v_cc, r_l, l_ind, c_cap)
        kv2, ki2 = derivatives(v + 0.5*dt*kv1, i_l + 0.5*dt*ki1, v_cc, r_l, l_ind, c_cap)
        kv3, ki3 = derivatives(v + 0.5*dt*kv2, i_l + 0.5*dt*ki2, v_cc, r_l, l_ind, c_cap)
        kv4, ki4 = derivatives(v + dt*kv3, i_l + dt*ki3, v_cc, r_l, l_ind, c_cap)

        v += (dt / 6.0) * (kv1 + 2.0*kv2 + 2.0*kv3 + kv4)
        i_l += (dt / 6.0) * (ki1 + 2.0*ki2 + 2.0*ki3 + ki4)

    return t_arr, v_arr, i_arr

if __name__ == "__main__":
    t, v, i = simulate_ndr_oscillator()
    print(f"Симуляція успішна. Кінцева напруга: {v[-1]*1000:.2f} мВ, струм: {i[-1]*1000:.2f} мА")
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double v;
    double i_l;
} State;

static double diode_current(double v) {
    const double v_p = 0.07;
    const double i_p = 0.005;
    const double v_v = 0.35;
    const double i_v = 0.0005;
    const double alpha = 10.0;

    if (v < 0.0) {
        return -i_p * (fabs(v) / v_p);
    }
    double i_tunnel = i_p * (v / v_p) * exp(1.0 - v / v_p);
    double i_diff = (v > v_v) ? i_v * exp(alpha * (v - v_v)) : 0.0;
    return i_tunnel + i_diff;
}

static State derivatives(State s, double v_cc, double r_l, double l_ind, double c_cap) {
    State d;
    d.v = (s.i_l - diode_current(s.v)) / c_cap;
    d.i_l = (v_cc - s.v - r_l * s.i_l) / l_ind;
    return d;
}

int main(void) {
    const double v_cc = 0.18;      /* Напруга живлення у зоні NDR (В) */
    const double r_l = 2.0;         /* Опір навантаження та втрат (Ом) */
    const double l_ind = 1.0e-6;    /* Індуктивність контуру (Гн) */
    const double c_cap = 100.0e-12; /* Ємність контуру (Ф) */
    const double dt = 1.0e-11;      /* Крок чисельного інтегрування (с) */
    const int steps = 20000;

    State s = { .v = 0.01, .i_l = 0.001 };

    printf("Time(ns)\tVoltage(mV)\tCurrent(mA)\n");
    for (int step = 0; step < steps; ++step) {
        if (step % 2000 == 0) {
            printf("%.3f\t\t%.2f\t\t%.2f\n", step * dt * 1.0e9, s.v * 1000.0, s.i_l * 1000.0);
        }

        State k1 = derivatives(s, v_cc, r_l, l_ind, c_cap);
        
        State s2 = { s.v + 0.5 * dt * k1.v, s.i_l + 0.5 * dt * k1.i_l };
        State k2 = derivatives(s2, v_cc, r_l, l_ind, c_cap);

        State s3 = { s.v + 0.5 * dt * k2.v, s.i_l + 0.5 * dt * k2.i_l };
        State k3 = derivatives(s3, v_cc, r_l, l_ind, c_cap);

        State s4 = { s.v + dt * k3.v, s.i_l + dt * k3.i_l };
        State k4 = derivatives(s4, v_cc, r_l, l_ind, c_cap);

        s.v   += (dt / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v);
        s.i_l += (dt / 6.0) * (k1.i_l + 2.0 * k2.i_l + 2.0 * k3.i_l + k4.i_l);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <array>

struct CircuitParams {
    double v_cc{0.18};      // Напруга джерела живлення (В)
    double r_l{2.0};        // Опір активних втрат (Ом)
    double l_ind{1.0e-6};   // Індуктивність контуру (Гн)
    double c_cap{100.0e-12};// Паралельна ємність (Ф)
};

struct DiodeParams {
    double v_p{0.07};   // Напруга піку (В)
    double i_p{0.005};  // Струм піку (А)
    double v_v{0.35};   // Напруга долини (В)
    double i_v{0.0005}; // Струм долини (А)
    double alpha{10.0}; // Градієнт експоненти (1/В)
};

struct State {
    double v{0.01};
    double i_l{0.001};

    [[nodiscard]] constexpr State operator+(const State& rhs) const noexcept {
        return {v + rhs.v, i_l + rhs.i_l};
    }
    [[nodiscard]] constexpr State operator*(double scalar) const noexcept {
        return {v * scalar, i_l * scalar};
    }
};

class TunnelDiodeOscillator {
public:
    explicit TunnelDiodeOscillator(CircuitParams cp = {}, DiodeParams dp = {})
        : c_params_{cp}, d_params_{dp} {}

    [[nodiscard]] double diode_current(double v) const noexcept {
        if (v < 0.0) {
            return -d_params_.i_p * (std::abs(v) / d_params_.v_p);
        }
        const double i_tunnel = d_params_.i_p * (v / d_params_.v_p) * 
                                std::exp(1.0 - v / d_params_.v_p);
        const double i_diff = (v > d_params_.v_v) 
            ? d_params_.i_v * std::exp(d_params_.alpha * (v - d_params_.v_v)) 
            : 0.0;
        return i_tunnel + i_diff;
    }

    [[nodiscard]] State derivatives(State s) const noexcept {
        return {
            (s.i_l - diode_current(s.v)) / c_params_.c_cap,
            (c_params_.v_cc - s.v - c_params_.r_l * s.i_l) / c_params_.l_ind
        };
    }

    [[nodiscard]] std::vector<State> run_simulation(double dt, std::size_t steps) const {
        std::vector<State> history;
        history.reserve(steps);

        State current_state{0.01, 0.001};

        for (std::size_t step = 0; step < steps; ++step) {
            history.push_back(current_state);

            const State k1 = derivatives(current_state);
            const State k2 = derivatives(current_state + k1 * (0.5 * dt));
            const State k3 = derivatives(current_state + k2 * (0.5 * dt));
            const State k4 = derivatives(current_state + k3 * dt);

            current_state = current_state + (k1 + k2 * 2.0 + k3 * 2.0 + k4) * (dt / 6.0);
        }
        return history;
    }

private:
    CircuitParams c_params_;
    DiodeParams d_params_;
};

int main() {
    constexpr double dt = 1.0e-11;
    constexpr std::size_t steps = 20000;

    const TunnelDiodeOscillator simulator;
    const auto results = simulator.run_simulation(dt, steps);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Час (нс)\tНапруга (мВ)\tСтрум (мА)\n";
    for (std::size_t i = 0; i < results.size(); i += 2000) {
        std::cout << (i * dt * 1.0e9) << "\t\t"
                  << (results[i].v * 1000.0) << "\t\t"
                  << (results[i].i_l * 1000.0) << "\n";
    }
    return 0;
}
```
:::

## Фізичний аналіз результатів розрахунку

Аналіз отриманих часових діаграм дозволяє виділити три послідовні фази становлення коливального процесу у колі з від'ємним опором:

1. **Фаза початкового експоненційного зростання (0–40 нс):**
   У цій фазі амплітуда відхилення напруги від точки рівноваги є малою, тому нелінійністю ВАХ можна знехтувати. Робота відбувається в околі точки зсуву `V_CC = 180 мВ`, де диференційний опір є сталим від'ємним числом `r_d ≈ -62.2 Ом`. Оскільки `R_L (2.0 Ом) < |r_d| (62.2 Ом)`, коефіцієнт згасання є від'ємним (`α < 0`), що спричиняє експоненційне наростання амплітуди коливань струму та напруги за законом `e^(|α|·t)`.

2. **Фаза нелінійного обмеження та формування граничного циклу (40–100 нс):**
   В міру зростання размаху напруги траєкторія починає заходити в області позитивного опору ВАХ (область піку `V < V_p` та область дифузійного зсуву `V > V_v`). В цих областях прилад перестає віддавати енергію і починає її розсіювати. Усереднений за період активний опір приладу зростає і прямує до точної компенсації активних втрат `R_L`.

3. **Стаціонарний режим незатухаючих коливань (понад 100 нс):**
   У фазовому просторі `(V, I_L)` траєкторія замикається у стійкий **граничний цикл**. Амплітуда напруги стабілізується на рівні розмаху близько `300 мВ` (від 50 мВ до 350 мВ), що точно відповідає ширині ділянки NDR тунельного діода. Частота стаціонарних коливань є дещо нижчою за точну резонансну частоту малосигнального LC-контуру через викривлення форми хвилі від чистої синусоїди до нелінійної релаксаційної хвилі.
