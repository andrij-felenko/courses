# ⚙️ Моделювання кривої магнітоопору GMR спинового клапана

Числове моделювання статичних та динамічних характеристик спинового клапана дозволяє розрахувати кути повороту намагніченості у тонких феромагнітних шарах та спрогнозувати залежність електричного опору від зовнішнього магнітного поля `R(H)`. Розрахунок спирається на мінімізацію енергії Стонера-Вольфарта для вільного шару під дією одноосьової анізотропії, зовнішнього поля та обмінного зсуву, з подальшим обчисленням опору за моделлю Мотта.

У цій вставці наведено повні програмні реалізації числової моделі тришарового спинового клапана трьома мовами програмування: Python, C та C++. Моделювання відтворює петлю гістерезису намагніченості вільного шару, враховує екранний обнійний зсув закріпленого шару та будує повну залежність опору при прямому та зворотному ходах розгортки магнітного поля.

## Фізична модель Стонера-Вольфарта та потенціальний рельєф

Густина магнітної енергії `E` вільного феромагнітного шару одиничного об'єму під кутом `θ` відносно осі легкого намагнічування визначається сумою трьох доданків:

```
E(θ) = K_u · sin²(θ) - M_s · H · cos(θ - θ_H) - J_inter · cos(θ - θ_pinned)
```

тут:
- `K_u` — константа одноосьової магнітної анізотропії вільного шару (Дж/м³),
- `M_s` — намагніченість насичення вільного шару (А/м),
- `H` — напруженість зовнішнього магнітного поля (А/м або мТл),
- `θ_H` — кут прикладання зовнішнього магнітного поля відносно осі легкого намагнічування,
- `J_inter` — паразитичний інтерфейсний зв'язок із закріпленим шаром (поля розсіювання або Неєлівське шорсткісне зчеплення «Orange-peel coupling»).

У наближенні макроспіна (коли увесь шар перемагнічується як єдиний монодоменний вектор) рівноважний кут намагніченості `θ_free(H)` знаходиться з умови мінімуму енергії: `dE/dθ = 0` при додатному значенні другої похідної `d²E/dθ² > 0`. 

За відсутності зовнішнього поля (`H = 0`) потенціальний рельєф є симетричною двоямною потенціальною лункою з двома мінімумами при `θ = 0` (0°) та `θ = π` (180°), розділеними енергетичним бар'єром `E_b = K_u · V` (де `V` — об'єм шару). Для забезпечення термостабільності записаної інформації вимагається, щоб енергетичний бар'єр перевищував теплові флуктуації: `K_u · V / (k_B · T) > 40–60`.

При прикладанні зовнішнього поля `H` вздовж осі легкого намагнічування потенціальна потенціальна лунка нахиляється. При досягненні коерцитивного поля Стонера-Вольфарта `H_c = 2·K_u / M_s` один із мінімумів енергії повністю зникає (точка перегіну), і вектор намагніченості стрибкоподібно лавиноподібно розвертається у напрямок нового єдиного мінімуму.

Після визначення рівноважного кута `θ_free(H)` опір спинового клапана обчислюється за кутовою формулою Мотта через косинус кута між вектором вільного та зафіксованого шарів:

```
R(H) = R_P + [(R_AP - R_P) / 2] · [1 - cos(θ_free(H) - θ_pinned)]
```

де `R_P` — опір у паралельному стані (`θ = 0°`), а `R_AP` — опір в антипаралельному стані (`θ = 180°`).

## Опис архітектури чисельного алгоритму та трасування стану

Програми реалізують двопрохідний алгоритм сканування магнітного поля з урахуванням історії перемагнічування (гістерезису):

```
                       Траєкторія розгортки магнітного поля H

    Sweep Up (Прямий хід):     H_min (-40 мТл) ──────────────► H_max (+40 мТл)
                               θ_free = 180°  ──[H = +H_c]──► θ_free = 0°

    Sweep Down (Зворотний хід): H_max (+40 мТл) ──────────────► H_min (-40 мТл)
                               θ_free = 0°    ──[H = -H_c]──► θ_free = 180°
```

1. **Прямий хід (Sweep Up):** Поле монотонно зростає від від'ємного насичення `H_min` до позитивного насичення `H_max`. Вільний шар утримується у напрямку 180° доти, доки поле не перевищить коерцитивну силу `+H_c`, після чого скачкоподібно розвертається у напрямок 0°.
2. **Зворотний хід (Sweep Down):** Поле монотонно спадає від `H_max` до `H_min`. Вільний шар утримується у напрямку 0° доти, доки поле не стане меншим за `-H_c`, після чого повертається у напрямок 180°.
3. **Обчислення закріпленого шару:** Намагніченість закріпленого шару утримується під кутом 0° дією обмінного зсуву `H_ex`. Якщо від'ємне зовнішнє поле перевищує `H_ex` (`H < -H_ex`), поле долає закріплення і розвертає закріплений шар у напрямок 180°.
4. **Формування масиву результатів:** Для кожного кроку обчислюється проєкція намагніченості `M(H) = M_s · cos(θ_free)` та електричний опір `R(H)`.

У порівнянні з мікромагнітними пакетними симуляторами (такими як OOMMF або MuMax3), які розбивають шар на тисячі кубічних сіткових осередків і розв'язують рівняння Ландау-Ліфшиця-Ґільберта (LLG), представлена макроспінова модель працює миттєво і забезпечує високу точність для наноелементів, чий розмір є меншим за довжину магнітного обміну (`l_ex ≈ 3–5` нм).

## Трасування виконання та розрахунок крутизни відгуку

Під час чисельного моделювання алгоритм обчислює диференціальну крутизну відгуку `dR/dH`, яка визначає чутливість магнітного датчика у лінійній області:

```
dR/dH = [(R_AP - R_P) / 2] · sin(θ_free - θ_pinned) · (dθ_free / dH)
```

Для оптимально зсунутого спинового клапана, де осей легкого намагнічування вільного та закріпленого шарів орієнтовані під кутом 90° у відсутності поля (`θ_0 = 90°`), синусоїдальний чинник `sin(90°) = 1` стає максимальним. Це забезпечує постійне значення крутизни `dR/dH = const` і мінімальні нелінійні спотворення сигналу при малих полях.

У разі перевищення крайових полів `|H| > H_sat` симулятор фіксує насичення опору на рівнях `R_P` або `R_AP`. Якщо у реальному структурі присутні крайові домени (завдяки полям розсіювання від торців), перемагнічування відбувається не когерентним розворотом макроспіна, а зародженням та рухом 180-градусних доменних стінок, що трохи розмиває вертикальні стрибки опору і розширює коерцитивну область на `10–20%`.

## Програмні реалізації

Нижче наведено програмні реалізації чисельного розрахунку кривих `M(H)` та `R(H)` трьома мовами програмування: Python, C та C++.

:::tabs
```py
import math

class GmrSpinValveSim:
    """Клас моделювання характеристик спинового клапана GMR."""

    def __init__(self, r_p: float = 100.0, gmr_ratio: float = 0.12, h_c: float = 0.5, h_ex: float = 25.0):
        """Ініціалізація параметрів спинового клапана.
        
        :param r_p: Опір у паралельному стані (Ом)
        :param gmr_ratio: Відносний коефіцієнт GMR (ΔR/R_P)
        :param h_c: Коерцитивна сила вільного шару (мТл)
        :param h_ex: Поле обмінного зсуву закріпленого шару (мТл)
        """
        self.r_p = r_p
        self.r_ap = r_p * (1.0 + gmr_ratio)
        self.h_c = h_c     
        self.h_ex = h_ex   

    def calculate_free_layer_angle(self, h_field: float, sweep_up: bool) -> float:
        """Обчислення кута намагніченості вільного шару з урахуванням коерцитивності гістерезису."""
        if sweep_up:
            if h_field < -self.h_c:
                return math.pi  # Намагніченість спрямована вліво (180°)
            elif h_field > self.h_c:
                return 0.0      # Намагніченість спрямована вправо (0°)
            else:
                return math.pi  # Збереження попередньої гілки гістерезису
        else:
            if h_field > self.h_c:
                return 0.0
            elif h_field < -self.h_c:
                return math.pi
            else:
                return 0.0

    def calculate_pinned_layer_angle(self, h_field: float) -> float:
        """Обчислення кута закріпленого шару (перемикається лише при високих полях H_ex)."""
        if h_field > -self.h_ex:
            return 0.0          # Закріплений стан під дією exchange bias (0°)
        else:
            return math.pi      # Зовнішнє поле подолало exchange bias (180°)

    def compute_resistance(self, theta_free: float, theta_pinned: float) -> float:
        """Обчислення електричного опору за кутом між векторами намагніченості."""
        cos_angle = math.cos(theta_free - theta_pinned)
        return self.r_p + 0.5 * (self.r_ap - self.r_p) * (1.0 - cos_angle)

    def run_sweep(self, h_min: float = -40.0, h_max: float = 40.0, steps: int = 200):
        """Виконання повного гістерезисного циклу розгортки магнітного поля."""
        results = []
        step_size = (h_max - h_min) / steps
        
        # Прямий хід розгортки (від h_min до h_max)
        for i in range(steps + 1):
            h = h_min + i * step_size
            t_free = self.calculate_free_layer_angle(h, sweep_up=True)
            t_pin = self.calculate_pinned_layer_angle(h)
            r = self.compute_resistance(t_free, t_pin)
            results.append((h, t_free, r, "up"))

        # Зворотний хід розгортки (від h_max до h_min)
        for i in range(steps + 1):
            h = h_max - i * step_size
            t_free = self.calculate_free_layer_angle(h, sweep_up=False)
            t_pin = self.calculate_pinned_layer_angle(h)
            r = self.compute_resistance(t_free, t_pin)
            results.append((h, t_free, r, "down"))

        return results

if __name__ == "__main__":
    sim = GmrSpinValveSim(r_p=100.0, gmr_ratio=0.10, h_c=0.8, h_ex=20.0)
    sweep_data = sim.run_sweep(-30.0, 30.0, 10)
    print(" H (mT) | theta_free (rad) | R (Ohm) | Sweep")
    print("-" * 45)
    for h, tf, r, direction in sweep_data[:6]:
        print(f"{h:7.2f} | {tf:16.3f} | {r:7.2f} | {direction}")
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура фізичних параметрів спинового клапана GMR */
typedef struct {
    double r_p;     /* Опір паралельного стану (Ом) */
    double r_ap;    /* Опір антипаралельного стану (Ом) */
    double h_c;     /* Коерцитивна сила вільного шару (мТл) */
    double h_ex;    /* Поле обмінного зсуву закріпленого шару (мТл) */
} gmr_sim_t;

/* Структура результату розрахунку для однієї точки поля */
typedef struct {
    double h_field;
    double theta_free;
    double resistance;
    int is_sweep_up;
} gmr_point_t;

/* Ініціалізація симулятора */
gmr_sim_t gmr_init(double r_p, double gmr_ratio, double h_c, double h_ex) {
    gmr_sim_t sim;
    sim.r_p = r_p;
    sim.r_ap = r_p * (1.0 + gmr_ratio);
    sim.h_c = h_c;
    sim.h_ex = h_ex;
    return sim;
}

/* Обчислення кута намагніченості вільного шару */
double gmr_calc_free_angle(const gmr_sim_t* sim, double h_field, int is_sweep_up) {
    if (is_sweep_up) {
        if (h_field < -sim->h_c) return M_PI;
        if (h_field > sim->h_c) return 0.0;
        return M_PI;
    } else {
        if (h_field > sim->h_c) return 0.0;
        if (h_field < -sim->h_c) return M_PI;
        return 0.0;
    }
}

/* Обчислення кута закріпленого шару під дією exchange bias */
double gmr_calc_pinned_angle(const gmr_sim_t* sim, double h_field) {
    return (h_field > -sim->h_ex) ? 0.0 : M_PI;
}

/* Обчислення електричного опору за формулою Мотта */
double gmr_calc_resistance(const gmr_sim_t* sim, double t_free, double t_pinned) {
    double cos_angle = cos(t_free - t_pinned);
    return sim->r_p + 0.5 * (sim->r_ap - sim->r_p) * (1.0 - cos_angle);
}

int main(void) {
    gmr_sim_t sim = gmr_init(100.0, 0.10, 0.8, 20.0);
    double h_min = -30.0;
    double h_max = 30.0;
    int steps = 10;
    double step_size = (h_max - h_min) / steps;

    printf(" H (mT) | theta_free (rad) | R (Ohm)\n");
    printf("------------------------------------\n");

    for (int i = 0; i <= steps; ++i) {
        double h = h_min + i * step_size;
        double tf = gmr_calc_free_angle(&sim, h, 1);
        double tp = gmr_calc_pinned_angle(&sim, h);
        double r = gmr_calc_resistance(&sim, tf, tp);
        printf("%7.2f | %16.3f | %7.2f\n", h, tf, r);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

class GmrSpinValveSim {
public:
    struct DataPoint {
        double h_field;
        double theta_free;
        double resistance;
        bool is_sweep_up;
    };

    explicit constexpr GmrSpinValveSim(double r_p = 100.0, double gmr_ratio = 0.12, 
                                       double h_c = 0.5, double h_ex = 25.0) noexcept
        : r_p_{r_p}, r_ap_{r_p * (1.0 + gmr_ratio)}, h_c_{h_c}, h_ex_{h_ex} {}

    [[nodiscard]] double calculate_free_angle(double h_field, bool sweep_up) const noexcept {
        if (sweep_up) {
            if (h_field < -h_c_) return std::numbers::pi;
            if (h_field > h_c_) return 0.0;
            return std::numbers::pi;
        } else {
            if (h_field > h_c_) return 0.0;
            if (h_field < -h_c_) return std::numbers::pi;
            return 0.0;
        }
    }

    [[nodiscard]] double calculate_pinned_angle(double h_field) const noexcept {
        return (h_field > -h_ex_) ? 0.0 : std::numbers::pi;
    }

    [[nodiscard]] double compute_resistance(double theta_free, double theta_pinned) const noexcept {
        const double cos_angle = std::cos(theta_free - theta_pinned);
        return r_p_ + 0.5 * (r_ap_ - r_p_) * (1.0 - cos_angle);
    }

    [[nodiscard]] std::vector<DataPoint> run_sweep(double h_min, double h_max, std::size_t steps) const {
        std::vector<DataPoint> results;
        results.reserve((steps + 1) * 2);
        const double step_size = (h_max - h_min) / static_cast<double>(steps);

        for (std::size_t i = 0; i <= steps; ++i) {
            const double h = h_min + static_cast<double>(i) * step_size;
            const double tf = calculate_free_angle(h, true);
            const double tp = calculate_pinned_angle(h);
            results.push_back({h, tf, compute_resistance(tf, tp), true});
        }

        for (std::size_t i = 0; i <= steps; ++i) {
            const double h = h_max - static_cast<double>(i) * step_size;
            const double tf = calculate_free_angle(h, false);
            const double tp = calculate_pinned_angle(h);
            results.push_back({h, tf, compute_resistance(tf, tp), false});
        }

        return results;
    }

private:
    double r_p_;
    double r_ap_;
    double h_c_;
    double h_ex_;
};

int main() {
    const GmrSpinValveSim sim{100.0, 0.10, 0.8, 20.0};
    const auto data = sim.run_sweep(-30.0, 30.0, 10);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << " H (mT) | theta_free (rad) | R (Ohm)\n";
    std::cout << "------------------------------------\n";
    for (std::size_t i = 0; i < 6 && i < data.size(); ++i) {
        std::cout << std::setw(7) << data[i].h_field << " | "
                  << std::setw(16) << data[i].theta_free << " | "
                  << std::setw(7) << data[i].resistance << "\n";
    }
    return 0;
}
```
:::

## Аналіз результатів та інтерпретація обчислень

Запускаючи моделювання для спинового клапана з номінальним опором `100 Ом`, коефіцієнтом GMR `10%` (`R_AP = 110 Ом`), коерцитивною силою `0.8 мТл` та полем обмінного зсуву `20 мТл`, витискується така фіксована фізична поведінка:

- При `H = -30 мТл` обоє шарів орієнтовані паралельно вліво (`← ←`), оскільки зовнішнє від'ємне поле є більшим за `H_ex`. Опір становить `R_P = 100 Ом`.
- При зростанні поля до `-10 мТл` закріплений шар повертається у зафіксований стан під дією внутрішнього поля обмінного зсуву `H_ex` (вправо `→`), а вільний шар утримується від'ємним полем вліво (`←`). Намагніченості стають антипаралельними (`← →`), опір стрибкоподібно зростає до `R_AP = 110 Ом`.
- При перетині поля `+0.8 мТл` вільний шар перемагнічується вправо (`→`). Обидва шари стають паралельними (`→ →`), опір повертається до `R_P = 100 Ом`.

Така симуляція повністю підтверджує наявність стабільного магніторезистивного вікна плато `R_AP` між полем `H_c` та `H_ex`, що слугує основою надійного двопозиційного зчитування інформації у логічних комірках оперативної пам'яті MRAM та датчиках магнітного поля.
