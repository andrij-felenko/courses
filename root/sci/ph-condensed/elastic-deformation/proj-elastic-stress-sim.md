# ⚙️ Чисельний розрахунок пружного стержня та деформаційного енергетичного балансу

Даний проект присвячено розробці розрахункового алгоритму та програмного комплексу для чисельного моделювання напружено-деформованого стану складеного ступенчатого стержня під комбінованим впливом механічного осьового навантаження та температурного розширення. Програма визначає механічне напруження `σ`, відносні механічну та температурну деформації `ε`, абсолютне поздовжнє подовження `ΔL`, поперечне звуження діаметра `Δd` внаслідок ефекту Пуассона, а також точний розподіл накопиченої потенціальної енергії пружності `U`.

### 1. Постановка фізичної задачі та чисельна модель

У багатьох інженерних конструкціях (турбінні вали, болтові з'єднання, стрижні мікромеханічних датчиків) елементи працюють в умовах складеного навантаження. Розглянемо стержень, що складається з `N` послідовних циліндричних сегментів із різних матеріалів.

Кожен сегмент `i` описується таким набором фізико-механічних та геометричних параметрів:
- Довжиною сегмента `L_i` (м);
- Початковим діаметром поперечного перерізу `d_i` (м);
- Модулем Юнга матеріалу `E_i` (Па);
- Коефіцієнтом Пуассона `ν_i` (безрозмірна величина);
- Коефіцієнтом лінійного температурного розширення `α_i` (1/К);
- Температурним відхиленням від початкового стану `ΔT_i` (К).

До кінців стержня прикладено осьову розтягувальну силу `F` (Н). Потрібно розрахувати повне подовження конструкції, зміну діаметрів та сумарний енергетичний баланс.

#### Математичний алгоритм покрокового розрахунку

Для кожного окремого сегмента `i` обчислення виконуються за такою послідовністю математичних формул:

1. **Площа поперечного перерізу `A_i`:**
   ```
   A_i = π · d_i² / 4
   ```
   Геометрична площа перерізу визначає розподіл нормального напруження.
2. **Нормальне механічне напруження `σ_i`:**
   ```
   σ_i = F / A_i
   ```
   Згідно з умовою рівноваги силового потоку, одна й та сама сила `F` передається уздовж усіх послідовно з'єднаних сегментів.
3. **Механічна пружна деформація `ε_mech_i` за законом Гука:**
   ```
   ε_mech_i = σ_i / E_i
   ```
4. **Температурна деформація `ε_therm_i`:**
   ```
   ε_therm_i = α_i · ΔT_i
   ```
   Якщо температура зростає (`ΔT > 0`), матеріал зазнає ізотропного подовження, яке додається до механічного видовження під дією зовнішньої сили.
5. **Повна поздовжня деформація `ε_total_i`:**
   ```
   ε_total_i = ε_mech_i + ε_therm_i
   ```
6. **Абсолютна зміна довжини сегмента `ΔL_i`:**
   ```
   ΔL_i = L_i · ε_total_i
   ```
7. **Абсолютна зміна діаметра `Δd_i` за рахунок ефекту Пуассона:**
   ```
   Δd_i = -ν_i · ε_mech_i · d_i
   ```
   Зверніть увагу: поперечне звуження викликається виключно механічною компонентою деформації `ε_mech_i`, оскільки ізотропне температурне розширення змінює розміри пропорційно в усіх напрямках без виникнення бічних орієнтаційних напружень Пуассона.
8. **Потенціальна енергія пружності `U_i`, накопичена у сегменті:**
   ```
   U_i = 1/2 · σ_i · ε_mech_i · V_i = (F² · L_i) / (2 · E_i · A_i)      [де V_i = A_i · L_i — об'єм]
   ```

Сумарне подовження всієї конструкції `ΔL_total` та загальна накопичена потенціальна енергія `U_total` визначаються як суми відповідних величин по всіх `N` сегментах:

```
ΔL_total = ∑_i ΔL_i,   U_total = ∑_i U_i
```

### 2. Крайові випадки та аналіз температурних напружень

Розглянута вище модель відноситься до **вільного розтягу**, коли стержень може вільно подовжуватися. Проте на практиці часто зустрічається крайовий випадок **жорстко затиснутого стержня**, коли обидва кінці нерухомо зафіксовані між жорсткими опорами (`ΔL_total = 0`).

У цьому випадку температурне нагрівання (`ΔT > 0`) не може викликати геометричного подовження. Замість цього у затиснутому стержні виникає реактивне стискальне напруження реакції опор `σ_therm`:

```
σ_therm = -E · α · ΔT
```

Якщо це реактивне стискальне напруження перевищить критичну межу Стійкості Ейлера, стержень зазнає раптового вигину (поздовжнього згину) або пластичної руйнації. Саме для запобігання цьому на залізничних коліях та трубопроводах залишають температурні компенсаційні зазори або застосовують П-подібні компенсатори.

### 3. Реалізація алгоритму трьома мовами (Python, C, C++)

Програма реалізована трьома мовами програмування (Python, C та C++) з дотриманням ідіоматичних стандартів кожної мови. Кожен приклад є повністю автономним, працездатним і розраховує навантаження складеного сталево-алюмінієвого стержня під дією розтягувальної сили `F = 50 кН`.

:::tabs
```py
import math

class Segment:
    def __init__(self, name, length, diameter, young_modulus, poisson_ratio, alpha=0.0, delta_t=0.0):
        self.name = name
        self.length = length             # L (м)
        self.diameter = diameter         # d (м)
        self.E = young_modulus           # E (Па)
        self.nu = poisson_ratio          # ν
        self.alpha = alpha               # α (1/K)
        self.delta_t = delta_t           # ΔT (K)

def calculate_rod_state(segments, force):
    results = []
    total_delta_l = 0.0
    total_energy = 0.0

    for seg in segments:
        area = math.pi * (seg.diameter ** 2) / 4.0
        stress = force / area
        strain_mech = stress / seg.E
        strain_therm = seg.alpha * seg.delta_t
        strain_total = strain_mech + strain_therm
        
        delta_l = seg.length * strain_total
        delta_d = -seg.nu * strain_mech * seg.diameter
        volume = area * seg.length
        energy = 0.5 * stress * strain_mech * volume

        total_delta_l += delta_l
        total_energy += energy

        results.append({
            "name": seg.name,
            "stress_MPa": stress / 1e6,
            "strain_mech_pct": strain_mech * 100.0,
            "delta_l_mm": delta_l * 1000.0,
            "delta_d_um": delta_d * 1e6,
            "energy_J": energy
        })

    return results, total_delta_l, total_energy

if __name__ == "__main__":
    # Двосегментний стержень (сталь + алюміній) під навантаженням 50 кН
    rod = [
        Segment("Сталевий сегмент", length=0.5, diameter=0.02, young_modulus=210e9, poisson_ratio=0.30),
        Segment("Алюмінієвий сегмент", length=0.3, diameter=0.025, young_modulus=70e9, poisson_ratio=0.33)
    ]
    axial_force = 50000.0  # 50 кН

    res, total_l, total_u = calculate_rod_state(rod, axial_force)

    print(f"=== Результати розрахунку (Сила = {axial_force/1000:.1f} кН) ===")
    for r in res:
        print(f"[{r['name']}]")
        print(f"  Напруження σ:       {r['stress_MPa']:.2f} МПа")
        print(f"  Пружна деформація: {r['strain_mech_pct']:.4f} %")
        print(f"  Подовження ΔL:      {r['delta_l_mm']:.4f} мм")
        print(f"  Зміна діаметра Δd: {r['delta_d_um']:.2f} мкм")
        print(f"  Енергія U:          {r['energy_J']:.4f} Дж")

    print(f"Загальне подовження стержня: {total_l*1000:.4f} мм")
    print(f"Повна потенціальна енергія:   {total_u:.4f} Дж")
```
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    const char* name;
    double length;          /* L (м) */
    double diameter;        /* d (м) */
    double young_modulus;   /* E (Па) */
    double poisson_ratio;   /* ν */
    double alpha;           /* α (1/K) */
    double delta_t;         /* ΔT (K) */
} Segment;

typedef struct {
    double stress_MPa;
    double strain_mech_pct;
    double delta_l_mm;
    double delta_d_um;
    double energy_J;
} SegmentResult;

void calculate_segment(const Segment* seg, double force, SegmentResult* res) {
    double area = M_PI * seg->diameter * seg->diameter / 4.0;
    double stress = force / area;
    double strain_mech = stress / seg->young_modulus;
    double strain_therm = seg->alpha * seg->delta_t;
    double strain_total = strain_mech + strain_therm;

    double delta_l = seg->length * strain_total;
    double delta_d = -seg->poisson_ratio * strain_mech * seg->diameter;
    double volume = area * seg->length;
    double energy = 0.5 * stress * strain_mech * volume;

    res->stress_MPa = stress / 1e6;
    res->strain_mech_pct = strain_mech * 100.0;
    res->delta_l_mm = delta_l * 1000.0;
    res->delta_d_um = delta_d * 1e6;
    res->energy_J = energy;
}

int main(void) {
    Segment rod[] = {
        {"Сталевий сегмент", 0.5, 0.02, 210e9, 0.30, 0.0, 0.0},
        {"Алюмінієвий сегмент", 0.3, 0.025, 70e9, 0.33, 0.0, 0.0}
    };
    size_t count = sizeof(rod) / sizeof(rod[0]);
    double force = 50000.0; /* 50 кН */

    double total_delta_l_mm = 0.0;
    double total_energy_J = 0.0;

    printf("=== Результати розрахунку (C) ===\n");
    for (size_t i = 0; i < count; ++i) {
        SegmentResult res;
        calculate_segment(&rod[i], force, &res);

        printf("[%s]\n", rod[i].name);
        printf("  Напруження σ:       %.2f МПа\n", res.stress_MPa);
        printf("  Пружна деформація: %.4f %%\n", res.strain_mech_pct);
        printf("  Подовження ΔL:      %.4f мм\n", res.delta_l_mm);
        printf("  Зміна діаметра Δd: %.2f мкм\n", res.delta_d_um);
        printf("  Енергія U:          %.4f Дж\n", res.energy_J);

        total_delta_l_mm += res.delta_l_mm;
        total_energy_J += res.energy_J;
    }

    printf("Загальне подовження стержня: %.4f мм\n", total_delta_l_mm);
    printf("Повна потенціальна енергія:   %.4f Дж\n", total_energy_J);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>

struct Segment {
    std::string name;
    double length;          // L (м)
    double diameter;        // d (м)
    double young_modulus;   // E (Па)
    double poisson_ratio;   // ν
    double alpha{0.0};      // α (1/K)
    double delta_t{0.0};    // ΔT (K)
};

struct SegmentResult {
    std::string name;
    double stress_MPa;
    double strain_mech_pct;
    double delta_l_mm;
    double delta_d_um;
    double energy_J;
};

class RodSimulator {
public:
    explicit RodSimulator(double axial_force) : force_(axial_force) {}

    SegmentResult simulate_segment(const Segment& seg) const {
        const double area = M_PI * std::pow(seg.diameter, 2) / 4.0;
        const double stress = force_ / area;
        const double strain_mech = stress / seg.young_modulus;
        const double strain_therm = seg.alpha * seg.delta_t;
        const double strain_total = strain_mech + strain_therm;

        const double delta_l = seg.length * strain_total;
        const double delta_d = -seg.poisson_ratio * strain_mech * seg.diameter;
        const double volume = area * seg.length;
        const double energy = 0.5 * stress * strain_mech * volume;

        return SegmentResult{
            seg.name,
            stress / 1e6,
            strain_mech * 100.0,
            delta_l * 1000.0,
            delta_d * 1e6,
            energy
        };
    }

private:
    double force_;
};

int main() {
    const std::vector<Segment> rod = {
        {"Сталевий сегмент", 0.5, 0.02, 210e9, 0.30},
        {"Алюмінієвий сегмент", 0.3, 0.025, 70e9, 0.33}
    };
    const double force = 50000.0; // 50 кН

    RodSimulator sim(force);
    double total_delta_l_mm = 0.0;
    double total_energy_J = 0.0;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Результати розрахунку (C++) ===\n";

    for (const auto& seg : rod) {
        const auto res = sim.simulate_segment(seg);
        std::cout << "[" << res.name << "]\n";
        std::cout << "  Напруження σ:       " << res.stress_MPa << " МПа\n";
        std::cout << "  Пружна деформація: " << res.strain_mech_pct << " %\n";
        std::cout << "  Подовження ΔL:      " << res.delta_l_mm << " мм\n";
        std::cout << "  Зміна діаметра Δd: " << res.delta_d_um << " мкм\n";
        std::cout << "  Енергія U:          " << res.energy_J << " Дж\n\n";

        total_delta_l_mm += res.delta_l_mm;
        total_energy_J += res.energy_J;
    }

    std::cout << "Загальне подовження стержня: " << total_delta_l_mm << " мм\n";
    std::cout << "Повна потенціальна енергія:   " << total_energy_J << " Дж\n";

    return 0;
}
```
:::

### 4. Фізичний аналіз та інженерна інтерпретація результатів

Після запуску програмного коду на виконання розрахунковий модуль повертає такі числові значення:

```
=== Результати розрахунку (Сила = 50.0 кН) ===
[Сталевий сегмент]
  Напруження σ:       159.15 МПа
  Пружна деформація: 0.0758 %
  Подовження ΔL:      0.3789 мм
  Зміна діаметра Δd: -4.55 мкм
  Енергія U:          9.4735 Дж

[Алюмінієвий сегмент]
  Напруження σ:       101.86 МПа
  Пружна деформація: 0.1455 %
  Подовження ΔL:      0.4365 мм
  Зміна діаметра Δd: -12.01 мкм
  Енергія U:          10.9133 Дж

Загальне подовження стержня: 0.8155 мм
Повна потенціальна енергія:   20.3868 Дж
```

#### Ключові фізичні висновки з отриманих даних

1. **Концентрація напружень у тонших сегментах.** Сталевий сегмент діаметром 20 мм володіє меншою площею перерізу (`A = 3.14 см²`), ніж алюмінієвий діаметром 25 мм (`A = 4.91 см²`). Тому нормальне напруження у сталі виявилося вищим (`159.15 МПа` проти `101.86 МПа`), хоча сталь є значно жорсткішим матеріалом.
2. **Розподіл деформацій та модуль Юнга.** Внаслідок того, що модуль Юнга алюмінію (`70 ГПа`) у три рази менший за модуль Юнга сталі (`210 ГПа`), відносна деформація алюмінію виявилася майже вдвічі більшою (`0.1455%` проти `0.0758%`), незважаючи на менше напруження.
3. **Аналіз ефекту Пуассона.** Звуження діаметра алюмінієвого сегмента становить `-12.01 мкм`, що у 2.6 рази перевищує звуження сталевого сегмента (`-4.55 мкм`). Це випливає з поєднання вищої деформації та більшого коефіцієнта Пуассона алюмінію (`ν = 0.33` проти `0.30`).
4. **Енергетичний баланс.** Сумарна потенціальна енергія пружності `20.3868 Дж` дорівнює повній роботі зовнішньої сили `1/2 · F · ΔL_total = 1/2 · 50000 Н · 0.0008155 м = 20.387 Дж`. Це підтверджує строге виконання закону збереження енергії у розрахованій моделі.

### 5. Архітектурні особливості реалізацій C, C++ та Python

Кожна з трьох поданих у списку реалізацій ілюструє ідіоматичний підхід своєї мовної парадигми:

- **C-реалізація:** Використовує чисті структури `Segment` та `SegmentResult` і процедурну функцію `calculate_segment`. Виділення пам'яті відбувається статично на стеку, що забезпечує максимальну швидкість виконання без оверхеду динамічної пам'яті (ідеально для вбудованих мікроконтролерів та симуляцій реального часу).
- **C++ реалізація:** Використовує клас `RodSimulator` із константними методами обчислень, стандартний контейнер `std::vector` та ідіому RAII. Застосування `std::fixed` та `std::iomanip` гарантує безпечне й точно форматоване виведення дійсних чисел.
- **Python-реалізація:** Надає найкоротший та найбільш читабельний код для швидкого прототипування та наукових розрахунків із використанням списків та словників.
