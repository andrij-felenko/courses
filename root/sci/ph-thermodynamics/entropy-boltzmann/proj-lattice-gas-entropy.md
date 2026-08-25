# ⚙️ Моделювання розширення ґратчастого газу та підрахунок мікростанів

У цій проектній вставці розроблено комп'ютерну модель незворотного статистичного розширення газу у двовимірній ґратці (модель ґратчастого газу). Програма моделює процес розширення газу при відчиненні розділювальної перегородки, підраховує кількість доступних мікростанів `W(t)` на кожному часовому кроці за допомогою логарифму гамма-функції та відстежує часову еволюцію конфігураційної ентропії Больцмана `S(t) / k_B` від початкового нерівноважного стану до стану термодинамічної рівноваги.

---

## 1. Постановка задачі та фізична модель

Розглянемо двовимірну прямокутну ґратку розміром `Lx × Ly` дискретних вузлів. Початково ґратка розділена вертикальною перегородкою посередині (при координаті `x = Lx / 2`) на дві рівні комірки з однаковими об'ємами `V_1 = V_2 = (Lx / 2) · Ly`.

У початковий момент часу `t = 0`:
1. Усі `N` одинакових газових частинок розташовані випадковим чином виключно у лівій половині ґратки (`x ∈ [0, Lx / 2 - 1]`).
2. Частинки вважаються взаємно непроникними та невзаємодіючими на відстані (модель ідеального ґратчастого газу). У кожному вузлі ґратки може перебувати довільна кількість частинок.
3. Оскільки всі `N` частинок локалізовані у лівій половині об'ємом `V_1`, початкова кількість доступних просторових конфігурацій дорівнює `W(0) = (V_1)^N`. При виборі комбінаторного розподілу частинок між лівою та правою половинами маємо `N_L = N` та `N_R = 0`, що відповідає `W_conf = N! / (N! · 0!) = 1` та нульовій конфігураційній ентропії `S(0) = 0`.

У момент часу `t = 1` перегородку прибирають. На кожному часовому кроці `Δt` кожна частинка виконує випадкове блукання в один із чотирьох сусідніх вузлів ґратки (праворуч, ліворуч, вгору або вниз) з однаковою ймовірністю `1 / 4`. Межі ґратки є відбиваючими: якщо спроба зсуву виводить частинку за межі прямокутника `[0, Lx - 1] × [0, Ly - 1]`, частинка залишається у поточному вузлі.

На кожному кроці симуляції програма вимірює число частинок у ліві половині `N_L(t)` та у правій половині `N_R(t) = N - N_L(t)`.

Число мікростанів `W(t)` для макростану з макроскопічним розподілом `(N_L, N_R)` задається біноміальним коефіцієнтом:

```
W(t) = N! / (N_L(t)! · N_R(t)!)
```

Безрозмірна ентропія Больцмана `S / k_B` обчислюється через логарифм `ln W(t)`:

```
S(t) / k_B = ln W(t) = ln N! - ln(N_L!) - ln(N_R!)
```

---

## 2. Усунення числового переповнення через `lgamma`

Пряме обчислення факторіалів `N!` за допомогою циклу чи рекурсії швидко призводить до числового переповнення. У стандартній арифметиці з плаваючою комою подвійної точності (IEEE 754 `double`) максимальне представлюване число становить близько `1.79 · 10³⁰⁸`. Зважаючи на це, вже при `N = 171` значення факторіала `171!` перевищує цей поріг і повертає `infinity` (нескінченність), що унеможливлює подальші розрахунки.

Для розв'язання цієї проблеми в обчислювальній статистичній фізиці використовують математичну гамма-функцію Ейлера `Γ(x)`. Для натуральних чисел виконується тотожність:

```
Γ(K + 1) = K!
```

Логарифмуючи обидві частини, отримуємо вираз для логарифма факторіала через логарифм гамма-функції:

```
ln K! = ln Γ(K + 1) = lgamma(K + 1)
```

Стандартні математичні бібліотеки мов C та C++ (заголовочні файли `<math.h>` та `<cmath>`) містять високоточну функцію `lgamma(x)`, яка обчислює значення `ln Γ(x)` напряму через асимптотичні розклади без проміжного обчислення самого факторіала `K!`. Це дозволяє обчислювати ентропію Больцмана для систем із мільйонами частинок без втрати точності та без ризику чисельного переповнення.

---

## 3. Граничні умови та порівняння з безперервним фазовим простором

У даній комп'ютерній моделі використовується дискретна просторова ґратка, де мікростан системи задається вектором координат всіх частинок `{(x_1, y_1), (x_2, y_2), ..., (x_N, y_N)}`. У класичному суцільному фазовому просторі координати частинок змінюються неперервно, тому фазовий об'єм описується інтегралом `∫ d³N q d³N p`.

Щоб перейти від неперервного фазового простору до дискретного підрахунку мікростанів `W`, фазовий простір розбивається на елементарні комірки об'ємом `h^(3N)`, де `h` — стала Планка. У нашій ґратчастій моделі роль такої елементарної комірки відіграє один вузол ґратки.

Граничні умови відбивання на стінках прямокутника забезпечують збереження повної кількості частинок `N`. Якщо змінити граничні умови на періодичні (топологія тора), характер дифузійного розширення зберігається, але виключається крайовий ефект підвищеної густини частинок біля твердих стінок.

---

## 4. Реалізація мовами C та C++ (`:::tabs`)

Нижче наведено ідіоматичні реалізації симулятора двовимірного ґратчастого газу мовами C та C++.

У реалізації мовою C використовується ручне управління динамічною пам'яттю (`malloc`/`free`), структура `Particle` та генератор псевдовипадкових чисел `rand()`.

У реалізації мовою C++ застосовано сучасні стандарти: автоматичне управління ресурсами RAII, контейнери `std::vector`, розумні вказівники `std::unique_ptr`, генератор `std::mt19937` з заголовка `<random>` для забезпечення високої якості псевдовипадкової послідовності та атрибути `[[nodiscard]]`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

typedef struct {
    int x;
    int y;
} Particle;

typedef struct {
    int lx;
    int ly;
    int num_particles;
    Particle *particles;
} LatticeGas;

/* Створення та ініціалізація газу у лівій половині ґратки */
LatticeGas* lattice_gas_create(int lx, int ly, int n) {
    LatticeGas *gas = (LatticeGas*)malloc(sizeof(LatticeGas));
    if (!gas) return NULL;

    gas->lx = lx;
    gas->ly = ly;
    gas->num_particles = n;
    gas->particles = (Particle*)malloc(sizeof(Particle) * n);
    if (!gas->particles) {
        free(gas);
        return NULL;
    }

    /* Розміщення частинок у лівій половині: x in [0, lx/2 - 1] */
    int half_x = lx / 2;
    for (int i = 0; i < n; ++i) {
        gas->particles[i].x = rand() % half_x;
        gas->particles[i].y = rand() % ly;
    }

    return gas;
}

void lattice_gas_free(LatticeGas *gas) {
    if (gas) {
        free(gas->particles);
        free(gas);
    }
}

/* Крок симуляції: випадкове блукання кожної частинки */
void lattice_gas_step(LatticeGas *gas) {
    for (int i = 0; i < gas->num_particles; ++i) {
        int dir = rand() % 4;
        int nx = gas->particles[i].x;
        int ny = gas->particles[i].y;

        if (dir == 0) nx++;      /* праворуч */
        else if (dir == 1) nx--; /* ліворуч */
        else if (dir == 2) ny++; /* вгору */
        else if (dir == 3) ny--; /* вниз */

        /* Відбиваючі межі ґратки */
        if (nx >= 0 && nx < gas->lx) gas->particles[i].x = nx;
        if (ny >= 0 && ny < gas->ly) gas->particles[i].y = ny;
    }
}

/* Підрахунок частинок у ліві половині */
int lattice_gas_count_left(const LatticeGas *gas) {
    int count = 0;
    int half_x = gas->lx / 2;
    for (int i = 0; i < gas->num_particles; ++i) {
        if (gas->particles[i].x < half_x) {
            count++;
        }
    }
    return count;
}

/* Точне обчислення S / k_B = ln W через lgamma */
double calculate_entropy(int n, int n_left) {
    int n_right = n - n_left;
    double log_n_fact = lgamma(n + 1.0);
    double log_nl_fact = lgamma(n_left + 1.0);
    double log_nr_fact = lgamma(n_right + 1.0);

    return log_n_fact - log_nl_fact - log_nr_fact;
}

int main(void) {
    srand((unsigned int)time(NULL));

    const int LX = 100;
    const int LY = 100;
    const int N = 1000;
    const int STEPS = 200;

    LatticeGas *gas = lattice_gas_create(LX, LY, N);
    if (!gas) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    printf("Крок\tN_L\tN_R\tS/k_B\t\tS_max/k_B\n");
    double s_max = N * log(2.0); /* Рівноважна ентропія для рівних частин */

    for (int step = 0; step <= STEPS; step += 10) {
        int n_left = lattice_gas_count_left(gas);
        int n_right = N - n_left;
        double s_boltzmann = calculate_entropy(N, n_left);

        printf("%d\t%d\t%d\t%.4f\t%.4f\n", step, n_left, n_right, s_boltzmann, s_max);

        for (int k = 0; k < 10; ++k) {
            lattice_gas_step(gas);
        }
    }

    lattice_gas_free(gas);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <memory>

struct Particle {
    int x;
    int y;
};

class LatticeGasSimulation {
public:
    LatticeGasSimulation(int lx, int ly, int num_particles)
        : lx_(lx), ly_(ly), num_particles_(num_particles),
          gen_(std::random_device{}()), dis_(0, 3) {
        
        particles_.reserve(num_particles);
        std::uniform_int_distribution<int> dis_x(0, lx / 2 - 1);
        std::uniform_int_distribution<int> dis_y(0, ly - 1);

        for (int i = 0; i < num_particles; ++i) {
            particles_.push_back({dis_x(gen_), dis_y(gen_)});
        }
    }

    void step() {
        for (auto& p : particles_) {
            int dir = dis_(gen_);
            int nx = p.x;
            int ny = p.y;

            switch (dir) {
                case 0: nx++; break; // праворуч
                case 1: nx--; break; // ліворуч
                case 2: ny++; break; // вгору
                case 3: ny--; break; // вниз
            }

            if (nx >= 0 && nx < lx_) p.x = nx;
            if (ny >= 0 && ny < ly_) p.y = ny;
        }
    }

    [[nodiscard]] int count_left() const noexcept {
        int count = 0;
        int half_x = lx_ / 2;
        for (const auto& p : particles_) {
            if (p.x < half_x) ++count;
        }
        return count;
    }

    [[nodiscard]] double calculate_entropy() const noexcept {
        int n_left = count_left();
        int n_right = num_particles_ - n_left;

        double log_n_fact = std::lgamma(num_particles_ + 1.0);
        double log_nl_fact = std::lgamma(n_left + 1.0);
        double log_nr_fact = std::lgamma(n_right + 1.0);

        return log_n_fact - log_nl_fact - log_nr_fact;
    }

    [[nodiscard]] int total_particles() const noexcept { return num_particles_; }

private:
    int lx_;
    int ly_;
    int num_particles_;
    std::vector<Particle> particles_;
    mutable std::mt19937 gen_;
    mutable std::uniform_int_distribution<int> dis_;
};

int main() {
    constexpr int LX = 100;
    constexpr int LY = 100;
    constexpr int N = 1000;
    constexpr int TOTAL_STEPS = 200;
    constexpr int INTERVAL = 10;

    auto sim = std::make_unique<LatticeGasSimulation>(LX, LY, N);

    std::cout << std::left 
              << std::setw(8) << "Крок" 
              << std::setw(8) << "N_L" 
              << std::setw(8) << "N_R" 
              << std::setw(14) << "S/k_B" 
              << std::setw(14) << "S_max/k_B" << "\n";
    std::cout << std::string(52, '-') << "\n";

    double s_max = N * std::log(2.0);

    for (int step = 0; step <= TOTAL_STEPS; step += INTERVAL) {
        int n_left = sim->count_left();
        int n_right = N - n_left;
        double s_boltzmann = sim->calculate_entropy();

        std::cout << std::left 
                  << std::setw(8) << step 
                  << std::setw(8) << n_left 
                  << std::setw(8) << n_right 
                  << std::setw(14) << std::fixed << std::setprecision(4) << s_boltzmann 
                  << std::setw(14) << std::fixed << std::setprecision(4) << s_max << "\n";

        for (int k = 0; k < INTERVAL; ++k) {
            sim->step();
        }
    }

    return 0;
}
```
:::

---

## 5. Скрипт аналізу на Python для чисельного розрахунку та візуалізації

Для проведення багаторазових Монте-Карло симуляцій та аналізу еволюції ентропії при різній кількості частинок надається скрипт мовою Python із використанням бібліотеки NumPy.

```python
import math
import random
import numpy as np

def simulate_lattice_gas(lx=100, ly=100, num_particles=2000, max_steps=500):
    # Початковий стан: усі частинки у лівій половині (x < lx // 2)
    particles = np.zeros((num_particles, 2), dtype=int)
    particles[:, 0] = np.random.randint(0, lx // 2, size=num_particles)
    particles[:, 1] = np.random.randint(0, ly, size=num_particles)

    history_steps = []
    history_nl = []
    history_entropy = []

    s_max = num_particles * math.log(2.0)

    for step in range(max_steps):
        # Підрахунок кількості частинок у лівій половині
        n_left = np.sum(particles[:, 0] < (lx // 2))
        n_right = num_particles - n_left

        # Обчислення S / k_B = ln(N!) - ln(N_L!) - ln(N_R!) через math.lgamma
        s_val = (math.lgamma(num_particles + 1) 
                 - math.lgamma(n_left + 1) 
                 - math.lgamma(n_right + 1))

        history_steps.append(step)
        history_nl.append(n_left)
        history_entropy.append(s_val)

        # Зсув частинок у 4 напрямках
        moves = np.random.choice([0, 1, 2, 3], size=num_particles)
        # 0: right, 1: left, 2: up, 3: down
        dx = np.where(moves == 0, 1, np.where(moves == 1, -1, 0))
        dy = np.where(moves == 2, 1, np.where(moves == 3, -1, 0))

        new_x = np.clip(particles[:, 0] + dx, 0, lx - 1)
        new_y = np.clip(particles[:, 1] + dy, 0, ly - 1)

        particles[:, 0] = new_x
        particles[:, 1] = new_y

    return history_steps, history_nl, history_entropy, s_max

if __name__ == '__main__':
    steps, nl, s_list, s_max = simulate_lattice_gas()
    print(f"Початкова ентропія S(0) / k_B = {s_list[0]:.2f}")
    print(f"Кінцева ентропія S(500) / k_B = {s_list[-1]:.2f}")
    print(f"Теоретичний максимум S_max / k_B = {s_max:.2f}")
```

---

## 6. Фізичний аналіз результатів та часові масштаби релаксації

Аналіз результатів симуляції розкриває ключові властивості статистичної незворотності:

1. **Монотонне зростання ентропії в середньому:** У початковому стані `t = 0` всі частинки зосереджені у ліві половині (`N_L = N`). Оскільки можливий лише один макроскопічний варіант розміщення частини по половинах, `W_conf = N! / (N! · 0!) = 1`, а конфігураційна ентропія дорівнює нулю `S_conf(0) = 0`.
2. **Наближення до рівноваги та час релаксації:** Після видалення перегородки частинки діфундують у праву половину. Кількість частинок `N_L(t)` експоненціально наближається до значення `N / 2` з характерним часом релаксації `τ ~ (Lx)² / D`, де `D` — коефіцієнт дифузії частинок на ґратці. Відповідно, ентропія монотонно зростає до свого теоретичного максимуму `S_max = N · k_B · ln 2`.
3. **Рівноважні флуктуації:** У стані рівноваги (`t >> τ`) значення `N_L` не залишається строго постійним, а зазнає неперервних флуктуацій навколо математичного сподівання `N / 2`. Середньоквадратичне відхилення становить `σ_N = √N / 2`. Для системи з `N = 1000` відносна флуктуація складає близько `3%`, тоді як для термодинамічної системи з `N = 10²³` частинок відносна флуктуація становить непомітні `10⁻¹¹ %`.

> 🔧 **Навіщо це.** Представлений алгоритм моделювання ґратчастого газу та розрахунку ентропії через логарифми гамма-функції `lgamma()` лежить в основі методів Монте-Карло у статистичній фізиці. Подібні симуляції використовуються при розрахунку термодинамічних фазових діаграм, моделюванні дифузії домішок у напівпровідникових кристалах та розрахунку вільної енергії адсорбції газів пористими матеріалами.
