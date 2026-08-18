# ⚙️ Симуляція доменних структур

Ця вставка містить детальний фізичний опис та чисельну реалізацію алгоритму Монте-Карло за методом Метрополіса для 2D-сітки магнітних спінів. Модель демонструє спонтанний фазовий перехід другого роду, виникнення критичного упорядкування та формування макроскопічних магнітних доменів і доменних стінок у результаті змагання між термодинамічним хаосом, обмінною взаємодією та кристалічною анізотропією.

## Фізичні основи двовимірної моделі решітки

Для опису мікроскопічної поведінки феромагнітних матеріалів на атомному рівні застосовують гратчасті моделі. У найпростішій двовимірній моделі Ізинга-Гейзенберга кристал подається у вигляді регулярної квадратної сітки розміром `N × N` вузлів. У кожному вузлі `(i, j)` знаходиться магнітний момент (дипольний спін) `S[i, j]`.

У класичному наближенні з сильною кристалічною анізотропією вздовж вісі легкого намагнічування спін може приймати лише два дискретних значення орієнтації: `S[i, j] = +1` (спрямований вгору) або `S[i, j] = -1` (спрямований вниз).

Загальна потенціальна енергія цієї системи (гамільтоніан `E`) визначається трьома основними фізичними внесками:

```
E = -J · ∑_<i,j; k,l> S[i,j] · S[k,l] - K · ∑_[i,j] (S[i,j])² - μ₀ · H_ext · ∑_[i,j] S[i,j]
```

Розберемо кожен доданок цього рівняння:

1. **Доданок обмінної взаємодії (`-J · ∑ S[i,j] · S[k,l]`):**
   Підсумовування проводиться лише за всіма парами найближчих сусідніх вузлів `<i,j; k,l>` на 2D-решітці. Константа `J > 0` являє собою інтеграл обмінного зв'язку. Якщо два сусідні спіни мають однакову орієнтацію (`+1` і `+1` або `-1` і `-1`), їхній добуток дорівнює `+1`, що зменшує енергію системи на `-J`. Якщо спіни орієнтовані антипаралельно (`+1` і `-1`), добуток дорівнює `-1`, що збільшує енергію на `+J`. Таким чином, обмінна взаємодія підтримує паралельне впорядкування і прагне перетворити всю решітку на єдиний монодомен.

2. **Доданок одноосьової анізотропії (`-K · ∑ (S[i,j])²`):**
   Константа `K` фіксує енергетичну перевагу орієнтації спінів вздовж обраної кристалографічної осі. У двокомпонентній модельній решітці Ізинга дискретні значення спінів уже обмежені легкою віссю, тому ця енергія створює додатковий потенціальний бар'єр для повороту моментів у проміжні напрямки.

3. **Доданок зовнішнього магнітного поля (`-μ₀ · H_ext · ∑ S[i,j]`):**
   Описує зеєманівську взаємодію кожного спіна із зовнішнім магнітним полем `H_ext`. Поле змушує спіни повертатися вздовж напрямку `H_ext`. При `H_ext > 0` енергетично вигіднішим стає стан `S[i,j] = +1`.

## Метод Монте-Карло та термодинамічний алгоритм Метрополіса

При будь-якій температурі, вищій за абсолютний нуль (`T > 0`), на впорядковану дію обмінного поля накладається хаотичний тепловий рух (флуктуації). Тепловий рух прагне дезорієнтувати спіни і зруйнувати магнітний порядок.

Згідно з законами статистичної фізики, ймовірність перебування системи в стані з енергією `E` при температурі `T` визначається розподілом Канонічного ансамблю Ґіббса:

```
P(E) = (1 / Z) · exp(-E / (k_B · T))   [розподіл Ґіббса для термодинамічної системи]
```

де `k_B` — константа Больцмана, а `Z` — статистична сума за всіма можливими станами.

Для чисельного моделювання такої системи алгоритм прямого обчислення статистичної суми неможливий, оскільки кількість можливих конфігурацій сітки `50 × 50` становить `2²⁵⁰⁰ ≈ 10⁷⁵²`. Для розв'язання цієї задачі у 1953 році Ніколас Метрополіс (Nicholas Metropolis) запропонував **метод марковських ланцюгів Монте-Карло з найважливішою вибіркою** (марковська динаміка з умовою детального балансу).

Покрокова логіка алгоритму Метрополіса реалізується наступним чином:

1. **Вибір елемента:** На кожній ітерації випадковим чином обирається один вузол решітки `(r, c)`.
2. **Обчислення енергії оточення:** Обчислюється сума чотирьох найближчих сусідніх спінів (із застосуванням періодичних граничних умов, тобто тороїдальної топології для виключення крайових ефектів):
   `S_sum = S[r-1, c] + S[r+1, c] + S[r, c-1] + S[r, c+1]`
3. **Обчислення зміни енергії `ΔE`:** Розраховується гіпотетична зміна енергії всієї решітки, яка виникла б у разі перевороту обраного спіна `S[r, c] → -S[r, c]`:
   `ΔE = E_new - E_old = 2 · S[r, c] · (J · S_sum + μ₀ · H_ext)`
4. **Прийняття стану за умовою Метрополіса:**
   - Якщо `ΔE ≤ 0`, переворот спіна зменшує або не змінює енергію системи. Зміна **приймається безумовно**, і новий стан фіксується у сітці.
   - Якщо `ΔE > 0`, переворот вимагає додаткової енергії від теплового резервуара. Зміна приймається з **ймовірністю Больцмана**:
     `P_accept = exp(-ΔE / (k_B · T))`
     Для цього генерується випадкове число `rand ∈ [0.0, 1.0)`. Якщо `rand < P_accept`, переворот спіна виконується; у протилежному випадку спін зберігає свій початковий напрямок.

Один **крок Монте-Карло по решітці (Monte Carlo Step per Site, MCSS)** визначається як проведення `N × N` послідовних спроб перевороту спінів. Це відповідає статистичній середній імовірності того, що кожен спін решітки випробовується один раз.

## Фазовий перехід та теорія Ларса Онсагера

У 1944 році Ларс Онсагер (Lars Onsager) вивів точний аналітичний розв'язок для 2D-моделі Ізинга на квадратній решітці у відсутності зовнішнього поля (`H_ext = 0`). Він довів, що в такій системі існує чітка критична температура Кюрі `T_c`:

```
k_B · T_c = 2J / ln(1 + √2) ≈ 2.269 · J  [критична температура 2D-моделі Ізинга]
```

Фізичний зміст симуляції залежно від температури `T`:
- **При високій температурі (`T > T_c`):** Теплова енергія `k_B · T` суттєво перевищує обмінну енергію `J`. Хаотичні флуктуації руйнують будь-які кореляції. Решітка перебуває у парамагнітному стані, середня намагніченість `M = 0`, домени відсутні.
- **При низькій температурі (`T < T_c`):** Обмінна взаємодія перемагає тепловий шум. Сусідні спіни об'єднуються у великі однорідні кластери. Починають формуватися макроскопічні **магнітні домени**, розділені виразними доменними стінками.

Зростання середнього розміру доменів `L(t)` у часі релаксації описується масштабуванням Ліфшиця-Сльозова:

```
L(t) ∝ t^(1/2)                         [закон росту доменних кластерів Ліфшиця-Сльозова]
```

Рушійною силою цього процесу є зменшення сумарної кривини та протяжності доменних меж задля мінімізації повної поверхневої енергії стінок.

## Багатомовна реалізація симулятора

Нижче наведено повноцінні, незалежні та ідіоматичні реалізації симулятора формування доменів трьома мовами програмування: Python, C99 та C++17.

:::tabs
```py
import random
import math

class MagneticDomainSimulator2D:
    """Чисельний симулятор магнітних доменів на 2D-сітці за методом Метрополіса."""
    
    def __init__(self, grid_size=50, J_exchange=1.0, temperature=1.5):
        self.size = grid_size
        self.J = J_exchange
        self.temp = temperature
        # Ініціалізація повністю хаотичного стану (+1 або -1 з ймовірністю 50%)
        self.grid = [
            [1 if random.random() > 0.5 else -1 for _ in range(self.size)]
            for _ in range(self.size)
        ]

    def _get_neighbors_sum(self, r, c):
        """Сума орієнтацій 4 найближчих сусідів із періодичними граничними умовами."""
        top = self.grid[(r - 1) % self.size][c]
        bottom = self.grid[(r + 1) % self.size][c]
        left = self.grid[r][(c - 1) % self.size]
        right = self.grid[r][(c + 1) % self.size]
        return top + bottom + left + right

    def monte_carlo_step(self, external_h=0.0):
        """Один повний крок Метрополіса (N*N випробувань перевороту)."""
        total_sites = self.size * self.size
        for _ in range(total_sites):
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            spin = self.grid[r][c]
            
            neighbors_sum = self._get_neighbors_sum(r, c)
            # ΔE = 2 * S * (J * S_neighbors + H_ext)
            delta_energy = 2.0 * spin * (self.J * neighbors_sum + external_h)
            
            # Умова прийняття нового стану за Метрополісом
            if delta_energy <= 0.0 or random.random() < math.exp(-delta_energy / self.temp):
                self.grid[r][c] = -spin

    def get_magnetization(self):
        """Обчислення середньої питомої намагніченості M ∈ [-1.0, +1.0]."""
        total_spin = sum(sum(row) for row in self.grid)
        return total_spin / (self.size * self.size)

    def render_ascii_map(self):
        """Візуалізація доменної карти у текстовому консольному форматі."""
        print("=== КАРТА МАГНІТНИХ ДОМЕНІВ (# : +1, . : -1) ===")
        for row in self.grid:
            line = "".join("#" if s > 0 else "." for s in row)
            print(line)

if __name__ == "__main__":
    # Запуск симуляції на сітці 40x40 при T = 1.3 (нижче T_c ≈ 2.27)
    sim = MagneticDomainSimulator2D(grid_size=40, J_exchange=1.0, temperature=1.3)
    print(f"Початкова намагніченість M_0 = {sim.get_magnetization():.3f}")
    
    # Проведення 120 кроків Монте-Карло для релаксації до доменної структури
    for step in range(120):
        sim.monte_carlo_step(external_h=0.0)
    
    print(f"Кінцева намагніченість після релаксації M = {sim.get_magnetization():.3f}")
    sim.render_ascii_map()
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define GRID_SIZE 40

typedef struct {
    int grid[GRID_SIZE][GRID_SIZE];
    double J_exchange;
    double temperature;
} DomainSimulatorC;

void domain_sim_init(DomainSimulatorC *sim, double J_exchange, double temperature) {
    sim->J_exchange = J_exchange;
    sim->temperature = temperature;
    for (int r = 0; r < GRID_SIZE; r++) {
        for (int c = 0; c < GRID_SIZE; c++) {
            sim->grid[r][c] = ((double)rand() / RAND_MAX > 0.5) ? 1 : -1;
        }
    }
}

void domain_sim_step(DomainSimulatorC *sim, double external_h) {
    int n = GRID_SIZE;
    int total_trials = n * n;

    for (int k = 0; k < total_trials; k++) {
        int r = rand() % n;
        int c = rand() % n;
        int spin = sim->grid[r][c];

        int top = sim->grid[(r - 1 + n) % n][c];
        int bottom = sim->grid[(r + 1) % n][c];
        int left = sim->grid[r][(c - 1 + n) % n];
        int right = sim->grid[r][(c + 1) % n];
        int neighbors_sum = top + bottom + left + right;

        double delta_e = 2.0 * spin * (sim->J_exchange * neighbors_sum + external_h);

        if (delta_e <= 0.0 || ((double)rand() / RAND_MAX) < exp(-delta_e / sim->temperature)) {
            sim->grid[r][c] = -spin;
        }
    }
}

double domain_sim_magnetization(const DomainSimulatorC *sim) {
    int sum = 0;
    for (int r = 0; r < GRID_SIZE; r++) {
        for (int c = 0; c < GRID_SIZE; c++) {
            sum += sim->grid[r][c];
        }
    }
    return (double)sum / (GRID_SIZE * GRID_SIZE);
}

void domain_sim_print(const DomainSimulatorC *sim) {
    printf("=== C DOMAIN MAP ===\n");
    for (int r = 0; r < GRID_SIZE; r++) {
        for (int c = 0; c < GRID_SIZE; c++) {
            putchar(sim->grid[r][c] > 0 ? '#' : '.');
        }
        putchar('\n');
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    DomainSimulatorC sim;
    domain_sim_init(&sim, 1.0, 1.3);

    printf("C Simulator: M_init = %.3f\n", domain_sim_magnetization(&sim));

    for (int step = 0; step < 120; step++) {
        domain_sim_step(&sim, 0.0);
    }

    printf("C Simulator: M_final = %.3f\n", domain_sim_magnetization(&sim));
    domain_sim_print(&sim);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <string>
#include <memory>

class MagneticDomainSimulatorCPP {
private:
    std::size_t size_;
    double J_exchange_;
    double temperature_;
    std::vector<int> grid_;
    std::mt19937 rng_;

    [[nodiscard]] inline std::size_t idx(std::size_t r, std::size_t c) const noexcept {
        return r * size_ + c;
    }

public:
    MagneticDomainSimulatorCPP(std::size_t size, double J_exchange, double temperature)
        : size_(size), J_exchange_(J_exchange), temperature_(temperature),
          grid_(size * size), rng_(std::random_device{}()) 
    {
        std::uniform_int_distribution<int> dist(0, 1);
        for (auto& spin : grid_) {
            spin = dist(rng_) ? 1 : -1;
        }
    }

    void monte_carlo_step(double external_h = 0.0) {
        std::uniform_int_distribution<std::size_t> pos_dist(0, size_ - 1);
        std::uniform_real_distribution<double> prob_dist(0.0, 1.0);

        const std::size_t total_trials = size_ * size_;
        for (std::size_t k = 0; k < total_trials; ++k) {
            const std::size_t r = pos_dist(rng_);
            const std::size_t c = pos_dist(rng_);
            const int spin = grid_[idx(r, c)];

            const std::size_t top_r = (r == 0) ? (size_ - 1) : (r - 1);
            const std::size_t bot_r = (r == size_ - 1) ? 0 : (r + 1);
            const std::size_t left_c = (c == 0) ? (size_ - 1) : (c - 1);
            const std::size_t right_c = (c == size_ - 1) ? 0 : (c + 1);

            const int neighbors_sum = grid_[idx(top_r, c)] + grid_[idx(bot_r, c)] +
                                      grid_[idx(r, left_c)] + grid_[idx(r, right_c)];

            const double delta_energy = 2.0 * spin * (J_exchange_ * neighbors_sum + external_h);

            if (delta_energy <= 0.0 || prob_dist(rng_) < std::exp(-delta_energy / temperature_)) {
                grid_[idx(r, c)] = -spin;
            }
        }
    }

    [[nodiscard]] double magnetization() const noexcept {
        long long total_sum = 0;
        for (int spin : grid_) {
            total_sum += spin;
        }
        return static_cast<double>(total_sum) / static_cast<double>(grid_.size());
    }

    void render_ascii_map() const {
        std::cout << "=== C++ DOMAIN MAP ===\n";
        for (std::size_t r = 0; r < size_; ++r) {
            std::string line;
            line.reserve(size_);
            for (std::size_t c = 0; c < size_; ++c) {
                line.push_back(grid_[idx(r, c)] > 0 ? '#' : '.');
            }
            std::cout << line << '\n';
        }
    }
};

int main() {
    MagneticDomainSimulatorCPP sim(40, 1.0, 1.3);
    std::cout << "C++ Simulator M_init: " << sim.magnetization() << '\n';

    for (int step = 0; step < 120; ++step) {
        sim.monte_carlo_step(0.0);
    }

    std::cout << "C++ Simulator M_final: " << sim.magnetization() << '\n';
    sim.render_ascii_map();
    return 0;
}
```
:::

## Фізичний аналіз результатів симуляції та часової еволюції

При створенні початкового стану програма генерує хаотичний розподіл спінів (еквівалент температури `T → ∞`), де середня намагніченість близька до нуля `M ≈ 0`.

У міру виконання кроків Метрополіса при температурі `T = 1.3 < T_c` спостерігається чітка термодинамічна еволюція:
1. **Перші 10-20 кроків:** Дрібні одиночні спінові флуктуації зникають. Виникають локальні зародки впорядкованих областей розміром у кілька атомних осередків.
2. **Від 20 до 80 кроків:** Зародки зливаються у виразні великі смуги та плями — **магнітні домени**. Сусідні домени розділяються гладкими межами (доменними стінками).
3. **Понад 100 кроків:** Система досягає квазірівноважного стану. Доменна структура стабілізується; надалі відбувається лише повільний процес зменшення кривини доменних меж для мінімізації повної поверхневой енергії стінок.

Якщо задати додатне зовнішнє поле `external_h > 0`, домени з орієнтацією `#` починають розширюватися, поглинаючи домени `.`, що точно відтворює фізичний процес зворотного зсуву доменних стінок у зовнішньому полі.
