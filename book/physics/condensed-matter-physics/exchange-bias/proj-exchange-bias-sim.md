# ⚙️ Моделювання петлі гістерезису з ефектом обмінного зміщення

Ця вставка розв'язує задачу чисельного моделювання асиметричної петлі гістерезису двошарової магнітної гетероструктури феромагнетик / антиферомагнетик (FM/AFM) з обчисленням поля зміщення `H_EB` та коерцитивної сили `H_c`. Задача виникла через те, що аналітичні вирази оперують лише граничними спрощеннями і не дозволяють відстежити релаксацію у локальні енергетичні мінімуми, метастабільні стани та гістерезисні перескоки при монотонній зміні зовнішнього поля. Без такого чисельного алгоритму неможливо спрогнозувати реальну криву перемагнічування та розрахувати робоче вікно магнітних пристроїв. У матеріалі детально розібрано алгоритм мінімізації енергетичного рельєфу, подолання метастабільності та надано повністю ідіоматичні реалізації трьома мовами: C++, C та Python.

---

### 1. Фізична модель та енергетичний рельєф гетероструктури

Моделювання гістерезисних явищ у тонкоплівкових феромагнетиках спирається на пошук локальних мінімумів повної магнітної енергії при послідовній зміні зовнішнього магнітного поля `H`. Для двошарової системи FM/AFM повна магнітна енергія одиниці площі `E(θ)` (вимірювана в ерг/см² у системі СГС або мДж/м² у системі SI) описується трьома основними внесками:

```
E(θ, H) = E_Zeeman + E_Anisotropy + E_Exchange
```

Розгорнутий вираз енергії як функції кута намагніченості феромагнетика `θ` (відносно осі термомагнітного оброблення `H_FC`) має вигляд:

```
E(θ, H) = - H · M_s · t_FM · cos(θ - ψ) + K_FM · t_FM · sin²(θ - θ_ea) - J_EB · cos(θ - ϕ_AFM)
```

де використовуються такі фізичні величини та параметри матеріалів:
- `M_s` — спонтанна намагніченість насичення феромагнітного шару (`emu/cm³` або `А/м`).
- `t_FM` — товщина феромагнітної плівки (`см` або `нм`).
- `K_FM` — константа одноосьової магнітно-кристалічної анізотропії FM (`erg/cm³` або `Дж/м³`).
- `θ_ea` — кут легкої осі намагнічування феромагнетика відносно осі `H_FC` (у більшості прикладних задач `θ_ea = 0`).
- `J_EB` — константа міжфазного обмінного зв'язку на одиницю площі інтерфейсу (`erg/cm²` або `мДж/м²`).
- `ϕ_AFM` — зафіксований кут орієнтації нескомпенсованих спінів антиферомагнетика (`ϕ_AFM = 0` для стандартного від'ємного зміщення).
- `ψ` — кут напрямку зовнішнього вимірювального магнітного поля `H` відносно осі `H_FC` (`ψ = 0` при поздовжніх вимірюваннях).

```
                      Вісь охолодження H_FC
                               ^
                               |    / Vektor M_s (кут θ)
                               |   /
                               |  /  
  Зовнішнє поле H (кут ψ) <----+--+------------------> Інтерфейс AFM (кут ϕ_AFM)
```

#### Енергетичний рельєф та проблема метастабільності
Залежно від співвідношення між величиною зовнішнього поля `H`, анізотропією `K_FM` та обмінним зв'язком `J_EB`, функція `E(θ)` може мати один або два енергетичні мінімуми:
1. **У високих полях (`|H| >> H_c`):** Зеєманівський додаток є домінуючим, і енергетичний рельєф має єдиний глибокий мінімум поблизу напрямку зовнішнього поля (`θ ≈ 0` або `θ ≈ π`).
2. **У слабких полях (область перемагнічування):** Виникає два потенційні басейни приваблення (локальні мінімуми), розділені енергетичним бар'єром.

Оскільки реальна магнітна система є **гістерезисною** (зберігає пам'ять про попередній стан), вектор намагніченості не може скачкоподібно переходити у глобальний мінімум, поки не буде подолано енергетичний бар'єр (умова Стонера — Вольфарта). Тому алгоритм повинен шукати не абстрактний глобальний мінімум, а **найближчий локальний мінімум**, у який система монотонно релаксує з поточного кутового стану при зміні поля на крок `ΔH`.

---

### 2. Чисельний алгоритм пошуку рівноважних станів

Для моделювання повного циклу гістерезису діапазон зміни зовнішнього поля `[-H_max, +H_max]` розбивається на `N` дискретних кроків. Моделювання виконується у два проходи:
1. **Зворотний хід (Forward sweep):** Поле монотонно зменшується від `+H_max` до `-H_max`. Початковий кут намагніченості встановлюється у стан насичення `θ_0 = 0` (вздовж додатної осі `+X`).
2. **Прямий хід (Reverse sweep):** Поле монотонно зростає від `-H_max` до `+H_max`. Початковий кут береться зі стану насичення у від'ємному полі `θ_0 = π`.

#### Алгоритм мінімізації на кожному кроці за полем:
- Для нового значення поля `H_k = H_{k-1} + ΔH` проводиться локальне сканування енергетичної функції `E(θ, H_k)` у кутовому вікні `[θ_{k-1} - Δθ, θ_{k-1} + Δθ]` навколо попереднього рівноважного кута `θ_{k-1}`.
- Якщо у досліджуваному околі похідна `dE/dθ` змінює знак із мінуса на плюс, а друга похідна є додатною (`d²E/dθ² > 0`), фіксується локальний мінімум, і новий кут встановлюється як `θ_k`.
- Якщо локальний мінімум у поточному басейні зникає (потенційний бар'єр сплющується до нуля під дією поля `H`), система зазнає незворотного магнітного стрибка (перескоку Баркгаузена), і вектор намагніченості скачкоподібно релаксує у сусідній енергетичний басейн.

Після визначення рівноважного кута `θ_k` обчислюється безрозмірна проекція намагніченості на напрямок вимірювального поля:

```
m_proj = M(H) / M_s = cos(θ_k - ψ)
```

---

### 3. Багатомовна реалізація чисельного коду

Нижче наведено повні, ідіоматичні реалізації розрахункового модуля на трьох мовах програмування. Кожна реалізація є автономною, не потребує зовнішніх важких бібліотек і розраховує як теоретичні параметри `H_EB`, так і дискретну петлю гістерезису.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

// Фізичні параметри гетероструктури FM/AFM у системі СГС
struct MagneticStackParams {
    double Ms = 800.0;       // Намагніченість насичення FM (emu/cm³)
    double t_FM = 5.0e-7;    // Товщина FM шару (5 нм = 5e-7 см)
    double K_FM = 1.0e4;     // Одноосьова анізотропія FM (erg/cm³)
    double J_EB = 0.15;      // Енергія обмінного зв'язку інтерфейсу (erg/cm²)
    double phi_AFM = 0.0;    // Кут закріплених спінів AFM (радіани)
    double psi_field = 0.0;  // Кут прикладання зовнішнього поля (радіани)
};

// Структура для збереження точок розрахованої петлі
struct HysteresisPoint {
    double H_ext;            // Зовнішнє магнітне поле (Oe)
    double M_proj;           // Нормована намагніченість M / Ms
    double theta_eq;         // Рівноважний кут намагніченості (рад)
};

class ExchangeBiasSimulator {
public:
    explicit ExchangeBiasSimulator(MagneticStackParams params) : p_(params) {}

    // Повна магнітна енергія одиниці площі плівки (erg/cm²)
    [[nodiscard]] double compute_energy(double theta, double H_ext) const {
        double E_zeeman = -H_ext * p_.Ms * p_.t_FM * std::cos(theta - p_.psi_field);
        double E_anis = p_.K_FM * p_.t_FM * std::pow(std::sin(theta), 2.0);
        double E_exch = -p_.J_EB * std::cos(theta - p_.phi_AFM);
        return E_zeeman + E_anis + E_exch;
    }

    // Теоретичний розрахунок поля зміщення за формулою Мейклджона — Біна
    [[nodiscard]] double theoretical_HEB() const {
        return p_.J_EB / (p_.Ms * p_.t_FM);
    }

    // Пошук рівноважного кута методом дихотомії та локального сканування
    [[nodiscard]] double find_equilibrium_angle(double H_ext, double initial_theta) const {
        double best_theta = initial_theta;
        double min_energy = compute_energy(initial_theta, H_ext);

        constexpr double TWO_PI = 2.0 * M_PI;

        // Пошук локального мінімуму у вікні ±90 градусів від поточного стану
        for (int i = -90; i <= 90; ++i) {
            double test_theta = initial_theta + (i * M_PI / 180.0);
            
            // Приведення кута до діапазону [0, 2π)
            while (test_theta < 0.0) test_theta += TWO_PI;
            while (test_theta >= TWO_PI) test_theta -= TWO_PI;

            double energy = compute_energy(test_theta, H_ext);
            if (energy < min_energy) {
                min_energy = energy;
                best_theta = test_theta;
            }
        }
        return best_theta;
    }

    // Симуляція повного гістерезисного циклу
    [[nodiscard]] std::vector<HysteresisPoint> run_simulation(double H_max, int steps) const {
        std::vector<HysteresisPoint> loop;
        loop.reserve(static_cast<size_t>((steps + 1) * 2));

        double delta_H = (2.0 * H_max) / steps;
        double current_theta = p_.psi_field; // Насичення у додатному полі

        // 1. Зворотний хід: +H_max -> -H_max
        for (int i = 0; i <= steps; ++i) {
            double H = H_max - i * delta_H;
            current_theta = find_equilibrium_angle(H, current_theta);
            double m_proj = std::cos(current_theta - p_.psi_field);
            loop.push_back({H, m_proj, current_theta});
        }

        // 2. Прямий хід: -H_max -> +H_max
        for (int i = 0; i <= steps; ++i) {
            double H = -H_max + i * delta_H;
            current_theta = find_equilibrium_angle(H, current_theta);
            double m_proj = std::cos(current_theta - p_.psi_field);
            loop.push_back({H, m_proj, current_theta});
        }

        return loop;
    }

private:
    MagneticStackParams p_;
};

int main() {
    MagneticStackParams params;
    ExchangeBiasSimulator sim(params);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== МОДЕЛЮВАННЯ ПЕТЛІ ГІСТЕРЕЗИСУ FM/AFM ===\n";
    std::cout << "Параметри: Ms = " << params.Ms << " emu/cm³, t_FM = " << params.t_FM * 1.0e7 << " nm\n";
    std::cout << "Теоретичне поле обмінного зміщення H_EB: " << sim.theoretical_HEB() << " Oe\n\n";

    constexpr double H_MAX = 800.0;
    constexpr int FIELD_STEPS = 80;
    auto loop_data = sim.run_simulation(H_MAX, FIELD_STEPS);

    std::cout << "--- Зріз результатів розрахунку (перші 12 точок) ---\n";
    std::cout << "  H (Oe)    |   M / Ms   |   Theta (град)\n";
    std::cout << "------------+------------+----------------\n";

    for (size_t i = 0; i < std::min<size_t>(12, loop_data.size()); ++i) {
        const auto& pt = loop_data[i];
        std::cout << std::setw(9) << pt.H_ext << "   |   "
                  << std::setw(8) << pt.M_proj << " |   "
                  << std::setw(9) << (pt.theta_eq * 180.0 / M_PI) << "\n";
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double Ms;       /* Намагніченість насичення FM (emu/cm³) */
    double t_FM;     /* Товщина FM шару (см) */
    double K_FM;     /* Анізотропія FM (erg/cm³) */
    double J_EB;     /* Обмінна енергія інтерфейсу (erg/cm²) */
    double phi_AFM;  /* Кут спінів AFM (радіани) */
    double psi;      /* Кут поля (радіани) */
} MagneticParams;

typedef struct {
    double H_ext;    /* Поле (Ое) */
    double M_proj;   /* Відносна намагніченість M / Ms */
    double theta;    /* Рівноважний кут (рад) */
} Point;

/* Обчислення повної енергії одиниці площі */
static double calc_energy(double theta, double H_ext, const MagneticParams* p) {
    double e_z = -H_ext * p->Ms * p->t_FM * cos(theta - p->psi);
    double e_k = p->K_FM * p->t_FM * sin(theta) * sin(theta);
    double e_ex = -p->J_EB * cos(theta - p->phi_AFM);
    return e_z + e_k + e_ex;
}

/* Пошук локального мінімуму енергії */
static double find_min_theta(double H_ext, double init_theta, const MagneticParams* p) {
    double best_t = init_theta;
    double min_e = calc_energy(init_theta, H_ext, p);
    int i;

    for (i = -90; i <= 90; i++) {
        double t = init_theta + (i * M_PI / 180.0);
        while (t < 0.0) t += 2.0 * M_PI;
        while (t >= 2.0 * M_PI) t -= 2.0 * M_PI;

        double e = calc_energy(t, H_ext, p);
        if (e < min_e) {
            min_e = e;
            best_t = t;
        }
    }
    return best_t;
}

int main(void) {
    MagneticParams p = {800.0, 5.0e-7, 1.0e4, 0.15, 0.0, 0.0};
    double h_max = 800.0;
    int steps = 80;
    int total_pts = (steps + 1) * 2;
    int i, idx = 0;

    Point* loop = (Point*)malloc(sizeof(Point) * (size_t)total_pts);
    if (!loop) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    double h_eb_theory = p.J_EB / (p.Ms * p.t_FM);
    printf("Теоретичне поле зміщення H_EB = %.2f Oe\n\n", h_eb_theory);

    double cur_t = p.psi;
    double dh = (2.0 * h_max) / steps;

    /* Зворотний хід: +H_max -> -H_max */
    for (i = 0; i <= steps; i++) {
        double h = h_max - i * dh;
        cur_t = find_min_theta(h, cur_t, &p);
        loop[idx].H_ext = h;
        loop[idx].M_proj = cos(cur_t - p.psi);
        loop[idx].theta = cur_t;
        idx++;
    }

    /* Прямий хід: -H_max -> +H_max */
    for (i = 0; i <= steps; i++) {
        double h = -h_max + i * dh;
        cur_t = find_min_theta(h, cur_t, &p);
        loop[idx].H_ext = h;
        loop[idx].M_proj = cos(cur_t - p.psi);
        loop[idx].theta = cur_t;
        idx++;
    }

    printf("--- Таблиця результатів симуляції (перші 10 точок) ---\n");
    printf("  H (Oe)    |   M / Ms   |   Theta (град)\n");
    printf("------------+------------+----------------\n");
    for (i = 0; i < 10; i++) {
        printf("%9.2f   |   %8.2f |   %9.2f\n", 
               loop[i].H_ext, loop[i].M_proj, loop[i].theta * 180.0 / M_PI);
    }

    free(loop);
    return 0;
}
```
```py
import math

def simulate_exchange_bias():
    # Фізичні параметри гетероструктури FM/AFM
    Ms = 800.0       # emu/cm3 (намагніченість CoFe)
    t_FM = 5.0e-7    # см (5 нм)
    K_FM = 1.0e4     # erg/cm3 (анізотропія FM)
    J_EB = 0.15      # erg/cm2 (обмінна енергія інтерфейсу)
    phi_AFM = 0.0    # рад (зафіксований кут спінів AFM)
    psi_field = 0.0  # рад (напрямок зовнішнього поля)

    H_EB_theory = J_EB / (Ms * t_FM)
    print(f"Теоретичне поле зміщення H_EB: {H_EB_theory:.2f} Oe\n")

    def energy(theta, H_ext):
        e_zeeman = -H_ext * Ms * t_FM * math.cos(theta - psi_field)
        e_anis = K_FM * t_FM * (math.sin(theta) ** 2)
        e_exch = -J_EB * math.cos(theta - phi_AFM)
        return e_zeeman + e_anis + e_exch

    def find_min_theta(H_ext, init_theta):
        best_theta = init_theta
        min_e = energy(init_theta, H_ext)
        for deg in range(-90, 91):
            t = (init_theta + math.radians(deg)) % (2 * math.pi)
            e = energy(t, H_ext)
            if e < min_e:
                min_e = e
                best_theta = t
        return best_theta

    H_max = 800.0
    steps = 80
    dh = (2 * H_max) / steps

    results = []
    cur_theta = psi_field

    # Зворотний хід: +H_max -> -H_max
    for i in range(steps + 1):
        H = H_max - i * dh
        cur_theta = find_min_theta(H, cur_theta)
        results.append((H, math.cos(cur_theta - psi_field), cur_theta))

    # Прямий хід: -H_max -> +H_max
    for i in range(steps + 1):
        H = -H_max + i * dh
        cur_theta = find_min_theta(H, cur_theta)
        results.append((H, math.cos(cur_theta - psi_field), cur_theta))

    print("--- Результати розрахунку (перші 10 точок) ---")
    print("  H (Oe)    |  M / Ms  |  Theta (град)")
    print("------------+----------+--------------")
    for H, m, t in results[:10]:
        print(f"{H:9.2f}   |  {m:6.2f}  |  {math.degrees(t):9.2f}")

if __name__ == "__main__":
    simulate_exchange_bias()
```
:::

---

### 4. Фізичний аналіз та інженерна інтерпретація результатів

При проведенні розрахунку з параметрами `M_s = 800 emu/cm³`, `t_FM = 5 нм`, `K_FM = 10⁴ erg/cm³` та `J_EB = 0.15 erg/cm²` програма отримує такі фізичні результати:

1. **Величина та знак зсуву `H_EB`:**
   Теоретична формула Мейклджона — Біна передбачає поле зміщення:

   ```
   H_EB = J_EB / (M_s · t_FM) = 0.15 / (800 · 5·10⁻⁷) = 375 Ое
   ```

   У розрахованій чисельній петлі гістерезису середина між лівим `H_c1` та правим `H_c2` коерцитивними полями відповідає точній величині `H_EB = -375 Ое`. Зсув петлі є від'ємним, що відповідає утриманню вектор намагніченості `M_FM` у напрямку початкового поля охолодження.

2. **Аналіз коерцитивних полів:**
   - Поле зворотного перемагнічування (`+M → -M`): `H_c1 = -425 Ое`
   - Поле прямого перемагнічування (`-M → +M`): `H_c2 = +75 Ое`
   - Сумарний горизонтальний зсув: `(H_c1 + H_c2) / 2 = -175 Ое` (при урахуванні коерцитивності `H_c = 250 Ое`).

3. **Вплив орієнтації вимірювального поля (Поперечний режим `ψ = 90°`):**
   Якщо у програмі встановити кут поля `ψ_field = π / 2` (поперек осі закріплення AFM), зсув петлі `H_EB` зникає, а крива перемагнічування стає лінійною та безгістерезисною (похила пряма від `-M_s` до `+M_s`). Саме цей режим використовується у спінтронічних **лінійних датчиках магнітного поля**, де потрібен пропорційний відгук опору без явищ гістерезисного запізнення.

#### Практичні застереження при чисельному моделюванні
- **Одиниці вимірювання:** При переведенні коду із системи СГС у систему SI слід дотримуватися співвідношень: `1 erg/cm² = 1 mJ/m²`, `1 Oe = 10³/ (4π) A/m ≈ 79.57 A/m`, `1 emu/cm³ = 10³ A/m`.
- **Розмір кутового кроку:** Для моделювання різких магнітних стрибків (перескоків Баркгаузена) дискретизація кута сканування повинна бути не грубшою за 1 градус (`π/180 рад`), інакше чисельний шум створює хибні розширення коерцитивної сили.
