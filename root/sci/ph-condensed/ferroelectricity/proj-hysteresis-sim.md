# ⚙️ Чисельне моделювання сегнетоелектричного гістерезису та динаміки доменів

Динаміка електричної поляризації в сегнетоелектриках під дією змінного зовнішнього поля визначається не лише статичною розетою потенціалу Ландау, а й релаксаційними процесами переорієнтації доменів та руху доменних стінок. Для опису цієї часової затримки відгуку застосовують динамічне рівняння Ландау-Халатникова (Landau-Khalatnikov equation).

Цей документ містить повний розбір математичної моделі релаксації диполів, опис чисельного інтегрування диференціальних рівнянь методом Рунге-Кутти 4-го порядку (RK4), повнофункціональні реалізації мовами C, C++ та Python із розрахунком енергетичних втрат, а також аналіз фізичних обмежень та крайових випадків моделі.

## 1. Математична модель Ландау-Халатникова та безрозмірна форма

У феноменологічній теорії Ландау-Халатникова швидкість зміни поляризації `dP/dt` пропорційна термодинамічній силі, що повертає систему до мінімуму вільної енергії. З урахуванням зовнішнього електричного поля `E(t)` рівняння має вигляд:

```
γ · (dP / dt) = - (dF / dP)
= E(t) - α·P - β·P³
```
[де γ — коефіцієнт в'язкого тертя / релаксаційна стала доменних стінок, α = α_0·(T - T_0)]

Для забезпечення чисельної стійкості та уникнення помилок переповнення при роботі з плаваючою комою зручно перейти до безрозмірних змінних. Введемо характерний масштаб поляризації `P_0 = √(|α| / β)` та характерний масштаб часу `τ = γ / |α|`. Позначивши безрозмірну поляризацію `p = P / P_0`, безрозмірне поле `e = E / ( |α| · P_0 )` та безрозмірний час `t' = t / τ`, отримуємо зведене диференціальне рівняння:

```
dp / dt' = e(t') + p - p³     [для сегнетоелектричної фази T < T_0, де α < 0]
```

Це диференціальне рівняння нелінійного осцилятора із затуханням у двоямному потенціалі. За умови безрозмірного синусоїдального зовнішнього поля `e(t') = e_amp · sin(ω' · t')` чисельний інтеграл генерує закриту петлю гістерезису `p(e)`.

Якщо безрозмірна частота `ω'` надто висока (`ω' ≫ 1`), диполі не встигають переорієнтуватися, і петля розширюється зі збільшенням коерцитивного поля. Якщо ж частота прямує до нуля (`ω' ≪ 1`), розв'язок наближається до квазістатичної петлі гістерезису.

## 2. Аналіз крайових випадків та частотної залежності

Модель Ландау-Халатникова дозволяє дослідити три фізичні режими роботи сегнетоелектричного елемента:

1. **Квазістатичний режим (`f ≪ 1 / (2·π·τ)`)**:
   Частота поля значно менша за обернену релаксаційну сталу `τ = γ / |α|`. Поляризація встигає підлаштовуватися під миттєве значення поля `E(t)`. Коерцитивне поле прямо прямує до термодинамічної межі Ландау `E_c = (2 / (3·√3)) · |α| · √(|α| / β)`.
2. **Динамічний гістерезис (`f ≈ 1 / (2·π·τ)`)**:
   Період зовнішнього поля сумірний із часом переорієнтації доменів. Запізнення поляризації призводить до утворення відкритої петлі, площа якої росте з частотою. Саме у цьому режимі працюють комірки пам'яті FeRAM при високочастотному перемиканні.
3. **Високочастотний режим (`f ≫ 1 / (2·π·τ)`)**:
   Зовнішнє поле змінюється настільки швидко, що масивні іони не встигають зміщуватися зі своїх позицій. Амплітуда коливань поляризації `ΔP` падає до нуля, а петля гістерезису вироджується у тонку лінію (лінійний діелектричний відгук електронної поляризованості).

### Вплив внутрішнього поля зсуву (Internal Bias Field)

У реальних тонких плівках на межі з металевими електродами утворюються вбудовані електричні поля `E_bias` через різницю робіт виходу та наявність затиснутих зарядів на дефектах. Модель враховує цей ефект шляхом заміни `E(t) → E(t) + E_bias`:

```
γ · (dP / dt) = E(t) + E_bias - α·P - β·P³
```
Вбудоване поле `E_bias` викликає асиметричний зсув петлі гістерезису вздовж осі полів `E` (ефект імпринтингу або imprinting), що може призводити до втрати розрізнення логічних станів «0» та «1» у пам'яті FeRAM.

## 3. Чисельна реалізація алгоритму та обчислення втрат

Для інтегрування диференціального рівняння застосовується метод Рунге-Кутти 4-го порядку (RK4), який забезпечує високу точність та стійкість обчислень. Нижче наведено повнофункціональні реалізації алгоритму трьома мовами: C, C++ та Python, які розраховують не лише параметри `P(t)`, а й числово інтегрують площу петлі `W = ∮ E dP` за методом трапецій.

:::tabs
```c
#include <stdio.h>
#include <math.h>

#define PI 3.14159265358979323846

/* Структура параметрів сегнетоелектрика */
typedef struct {
    double alpha;    /* α0*(T - T0) < 0 */
    double beta;     /* β > 0 */
    double gamma;    /* релаксаційна стала γ */
    double e_amp;    /* амплітуда зовнішнього поля E0 */
    double freq;     /* частота поля f */
    double e_bias;   /* внутрішнє поле зсуву */
} FerroParams;

/* Похідна dP/dt = f(t, P) */
static double deriv_p(double t, double p, const FerroParams *params) {
    double e_field = params->e_amp * sin(2.0 * PI * params->freq * t) + params->e_bias;
    double df_dp = params->alpha * p + params->beta * p * p * p - e_field;
    return -df_dp / params->gamma;
}

/* Крок інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
static double step_rk4(double t, double p, double dt, const FerroParams *params) {
    double k1 = deriv_p(t, p, params);
    double k2 = deriv_p(t + 0.5 * dt, p + 0.5 * dt * k1, params);
    double k3 = deriv_p(t + 0.5 * dt, p + 0.5 * dt * k2, params);
    double k4 = deriv_p(t + dt, p + dt * k3, params);
    return p + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
}

int main(void) {
    FerroParams params = {
        .alpha = -1.0,
        .beta = 1.0,
        .gamma = 0.1,
        .e_amp = 1.5,
        .freq = 1.0,
        .e_bias = 0.0
    };

    double t = 0.0;
    double p = 0.1; /* початкова поляризація */
    double dt = 0.0005;
    int total_steps = 4000;
    double energy_loss = 0.0;
    double prev_e = 0.0;
    double prev_p = 0.1;

    printf("Time,E_field,Polarization\n");
    for (int i = 0; i < total_steps; i++) {
        double e_field = params.e_amp * sin(2.0 * PI * params.freq * t) + params.e_bias;
        
        /* Розрахунок втрат на останньому усталеному циклі за методом трапецій */
        if (i >= 2000) {
            printf("%.4f,%.4f,%.4f\n", t, e_field, p);
            double dp = p - prev_p;
            double avg_e = 0.5 * (e_field + prev_e);
            energy_loss += avg_e * dp;
        }
        
        prev_e = e_field;
        prev_p = p;
        p = step_rk4(t, p, dt, &params);
        t += dt;
    }

    fprintf(stderr, "Обчислена площа петлі (втрати W): %.4f у.о.\n", energy_loss);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <numeric>

struct FerroelectricMaterial {
    double alpha{-1.0}; // α < 0 у сегнетофазі
    double beta{1.0};   // β > 0
    double gamma{0.1};  // коефіцієнт релаксації
    double e_amplitude{1.5};
    double frequency{1.0};
    double e_bias{0.0};
};

struct DataPoint {
    double time;
    double e_field;
    double polarization;
};

class HysteresisSimulator {
public:
    explicit HysteresisSimulator(FerroelectricMaterial mat) : mat_(mat) {}

    [[nodiscard]] std::pair<std::vector<DataPoint>, double> simulate(double dt, std::size_t total_steps) const {
        std::vector<DataPoint> result;
        result.reserve(total_steps / 2);

        double t = 0.0;
        double p = 0.1;
        double energy_loss = 0.0;

        for (std::size_t i = 0; i < total_steps; ++i) {
            const double e_field = mat_.e_amplitude * std::sin(2.0 * std::numbers::pi * mat_.frequency * t) + mat_.e_bias;
            
            if (i >= total_steps / 2) {
                result.push_back({t, e_field, p});
                if (result.size() > 1) {
                    const auto& prev = result[result.size() - 2];
                    const double dp = p - prev.polarization;
                    const double avg_e = 0.5 * (e_field + prev.e_field);
                    energy_loss += avg_e * dp;
                }
            }

            p = step_rk4(t, p, dt);
            t += dt;
        }
        return {result, energy_loss};
    }

private:
    [[nodiscard]] double rk4_derivative(double t, double p) const {
        const double e_field = mat_.e_amplitude * std::sin(2.0 * std::numbers::pi * mat_.frequency * t) + mat_.e_bias;
        const double df_dp = mat_.alpha * p + mat_.beta * std::pow(p, 3) - e_field;
        return -df_dp / mat_.gamma;
    }

    [[nodiscard]] double step_rk4(double t, double p, double dt) const {
        const double k1 = rk4_derivative(t, p);
        const double k2 = rk4_derivative(t + 0.5 * dt, p + 0.5 * dt * k1);
        const double k3 = rk4_derivative(t + 0.5 * dt, p + 0.5 * dt * k2);
        const double k4 = rk4_derivative(t + dt, p + dt * k3);
        return p + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
    }

    FerroelectricMaterial mat_;
};

int main() {
    FerroelectricMaterial mat;
    HysteresisSimulator simulator(mat);
    const auto [data, loss] = simulator.simulate(0.0005, 4000);

    std::cout << "Отримано точок петлі: " << data.size() << "\n";
    std::cout << "Розрахована площа петлі (втрати W): " << loss << " Дж/м3\n";
    return 0;
}
```
```py
import math
from typing import List, Tuple

class FerroelectricSimulation:
    def __init__(self, alpha: float = -1.0, beta: float = 1.0, 
                 gamma: float = 0.1, e_amp: float = 1.5, 
                 freq: float = 1.0, e_bias: float = 0.0):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.e_amp = e_amp
        self.freq = freq
        self.e_bias = e_bias

    def derivative(self, t: float, p: float) -> float:
        e_field = self.e_amp * math.sin(2.0 * math.pi * self.freq * t) + self.e_bias
        df_dp = self.alpha * p + self.beta * (p ** 3) - e_field
        return -df_dp / self.gamma

    def step_rk4(self, t: float, p: float, dt: float) -> float:
        k1 = self.derivative(t, p)
        k2 = self.derivative(t + 0.5 * dt, p + 0.5 * dt * k1)
        k3 = self.derivative(t + 0.5 * dt, p + 0.5 * dt * k2)
        k4 = self.derivative(t + dt, p + dt * k3)
        return p + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    def run(self, dt: float = 0.0005, steps: int = 4000) -> Tuple[List[Tuple[float, float, float]], float]:
        t, p = 0.0, 0.1
        history = []
        energy_loss = 0.0
        prev_e, prev_p = 0.0, 0.1
        
        for i in range(steps):
            e_field = self.e_amp * math.sin(2.0 * math.pi * self.freq * t) + self.e_bias
            if i >= steps // 2:
                history.append((t, e_field, p))
                dp = p - prev_p
                avg_e = 0.5 * (e_field + prev_e)
                energy_loss += avg_e * dp
            prev_e, prev_p = e_field, p
            p = self.step_rk4(t, p, dt)
            t += dt
        return history, energy_loss

if __name__ == "__main__":
    sim = FerroelectricSimulation()
    results, loss = sim.run()
    print(f"Симуляція успішна: отримано {len(results)} точок.")
    print(f"Обчислено енергетичні втрати за цикл W = {loss:.4f} у.о.")
```
:::

## 4. Обробка результатів та розрахунок нелінійних параметрів

Згенеровані числові дані `(E[i], P[i])` дозволяють обчислити ключові практичні характеристики реальних сегнетоелектричних конденсаторів:

1. **Залишкова поляризація `P_r`**:
   Значення `P[i]` у точках, де зовнішнє поле звертається в нуль (`E[i] = 0`). Модуль залишкової поляризації визначає робочий заряд для зчитування біта у комірках пам'яті.
2. **Динамічне коерцитивне поле `E_c`**:
   Значення поля `E[i]` у точках перетину осі поляризації (`P[i] = 0`). Воно визначає порог напруги для перемикання стану доменів.
3. **Малосигнальна діелектрична проникність `ε_diff`**:
   Чисельна похідна `dP/dE` вздовж верхівок петлі насичення відповідає диференціальній діелектричній проникності `ε_diff = (1 / ε_0) · (dP / dE)`.

## 5. Порівняння чисельних моделей сегнетоелектриків

У сучасній фізиці твердого тіла та САПР розробки напівпровідникових мікросхем використовують три рівні моделювання:

1. **Однодоменна модель Ландау-Халатникова**:
   - *Переваги*: Надзвичайна обчислювальна швидкість, аналітична прозорість, можливість інтеграції в SPICE-симулятори схем.
   - *Недоліки*: Завищує коерцитивне поле `E_c` у 10–100 разів, оскільки не враховує зародження доменів.
2. **Феноменологічна модель Прайзаха (Preisach model)**:
   - *Переваги*: Описує полікристалічні кераміки PZT шляхом суперпозиції незалежних бістабільних гістерезисних операторів (гістеронів) із розподіленими значеннями `E_c` та `E_bias`. Точно відтворює часткові петлі гістерезису (minor loops).
   - *Недоліки*: Потребує великої кількості емпіричних підганяльних параметрів.
3. **Сіткова модель фазового поля (Phase-field modeling)**:
   - *Переваги*: Моделює 2D/3D просторово-часову еволюцію тисяч доменів і доменних стінок на основі системи рівнянь Ландау-Гінзбурга-Девоншира, розв'язаних у поєднанні з рівняннями пуассонівської електростатики та пружності.
   - *Недоліки*: Потребує потужних суперкомп'ютерних обчислень на сітках високої роздільності.
