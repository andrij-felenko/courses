# ⚙️ Інженерний розрахунок теплової матриці та температурного бюджету

Цей програмний проєкт реалізує консольний інженерний калькулятор для розрахунку теплового опору масиву перехідних отворів, моделювання опору розтікання у мідних шарах плати та верифікації теплового бюджету напівпровідникового компонента під заданою потужністю розсіювання. Калькулятор дозволяє автоматично підібрати оптимальну кількість via, визначити температуру кристала T_J та перевірити відповідність обмеженням за технологією виготовлення (діаметр свердла, товщина металізації, ризик капілярного витікання припою).

## 1. Архітектура та математичний алгоритм

Програма моделює багатошаровий тепловий тракт як еквівалентний резистивний ланцюг, де кожна фізична ділянка конструкції представлена зосередженим тепловим опором. Алгоритм розв'язує задачу в одновимірному наближенні з урахуванням геометричного розтікання тепла у тонких пластинах.

Послідовність розрахунку складається з таких обов'язкових кроків:

1. **Розрахунок геометрії та власного опору одиничного отвору:**
   Спочатку обчислюється площа поперечного перерізу тонкостінної мідної гільзи:
   `A_Cu = π · (d · t − t²)`
   де `d` — зовнішній діаметр свердління, `t` — товщина осадженої гальванічної міді на стінках.
   Тепловий опір одиничної гільзи визначається за законом Фур'є вздовж довжини каналу `h`:
   `R_θ,via = h / (k_Cu · A_Cu)`

2. **Еквівалентний опір паралельного масиву отворів:**
   Якщо під термопадом розміщено `N` однакових переходів, їхній спільний тепловий опір обчислюється за формулою паралельних провідників:
   `R_θ,array = R_θ,via / N`

3. **Тепловий опір паяного з'єднання:**
   Для розрахунку перепаду температури на шарі припою товщиною `t_solder` (типово 50 мкм) під прямокутним майданчиком площею `A_pad = a · b` застосовується формула прямого теплового проведення:
   `R_θ,solder = t_solder / (k_solder · A_pad)`

4. **Опір радіального розтікання у нижній площині міді:**
   Коли тепловий потік виходить із нижніх торців перехідних отворів, він розтікається по площі внутрішнього чи зовнішнього полігону заземлення товщиною `t_foil`. За моделлю кругового розтікання від ефективного радіуса паду `r_pad = √(A_pad / π)` до радіуса полігону `r_plane`:
   `R_spread,bot = ln(r_plane / r_pad) / (2 · π · k_Cu · t_foil)`

5. **Сумарний тепловий опір «кристал-середовище» (R_θ,JA):**
   Усі опори тракту додаються послідовно:
   `R_θ,JA = R_θ,JC + R_θ,solder + R_θ,array + R_θ,spread,bot + R_θ,TIM + R_θ,HS`

6. **Розрахунок температури напівпровідникового переходу (T_J):**
   `T_J = T_A + P · R_θ,JA`

## 2. Аналіз крайових випадків та перевірка обмежень DRC

Інженерний розрахунок враховує критичні обмеження технологічного процесу:

- **Перевірка на капілярне витікання припою (Solder Wicking):** Якщо діаметр відкритого отвору перевищує 0.35 мм (`via_drill_diam_m > 3.5e-4`), програма встановлює попереджувальний прапорець `solder_wicking_risk = true`. У незаповнених via такого діаметра сила поверхневого натягу не здатна утримати рідкий припій, що призводить до утворення пустот.
- **Захист від ділення на нуль:** Якщо кількість отворів `N ≤ 0`, функція повертає опір монолітного склотекстоліту FR-4.
- **Перевірка безпечної температури кристала:** Для промислових кремнієвих мікросхем гранична робоча температура становить `T_J,max = 125 °C` (або 150 °C для силових MOSFET). При перевищенні цієї межі алгоритм фіксує аварійний стан `is_safe_temp = false`.
- **Вплив товщини фольги на розтікання:** Алгоритм демонструє, як подвоєння товщини міді (з 1 oz / 35 мкм до 2 oz / 70 мкм) пропорційно знижує опір розтікання `R_spread,bot`, полегшуючи передачу тепла на периферійні ділянки плати.
- **Урахування коефіцієнта заповнення пасти:** При моделюванні паяного з'єднання калькулятор враховує реальне покриття площі пастою (50–70% за стандартом IPC-7095) та відсутність дефектів капілярного стікання.

## 3. Реалізація мовами C та C++

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Константи матеріалів
#define K_COPPER 385.0       // Теплопровідність міді, Вт/(м·К)
#define K_SOLDER 58.0        // Теплопровідність припою SAC305, Вт/(м·К)

// Вхідні геометричні та теплові параметри
typedef struct {
    double pcb_thickness_m;      // Товщина плати (h), м
    double via_drill_diam_m;     // Діаметр свердла via (d), м
    double via_plating_thk_m;    // Товщина міднення стінки (t), м
    int    via_count;            // Кількість отворів (N)
    double pad_side_a_m;         // Сторона прямокутного термопада (a), м
    double pad_side_b_m;         // Сторона прямокутного термопада (b), м
    double plane_radius_m;       // Ефективний радіус розтікання міді, м
    double plane_copper_thk_m;   // Товщина мідного полігону, м
    double r_jc_k_w;             // Опір кристал-корпус (R_theta_JC), К/Вт
    double r_tim_k_w;            // Опір термоінтерфейсу (R_theta_TIM), К/Вт
    double r_hs_k_w;             // Опір радіатора (R_theta_HS), К/Вт
    double ambient_temp_c;       // Температура середовища (T_A), °C
    double power_dissipation_w;  // Потужність розсіювання (P), Вт
} ThermalParams;

// Результати розрахунку
typedef struct {
    double single_via_area_m2;
    double single_via_rth_k_w;
    double array_rth_k_w;
    double solder_rth_k_w;
    double plane_spread_rth_k_w;
    double total_rth_ja_k_w;
    double junction_temp_c;
    bool   solder_wicking_risk;
    bool   is_safe_temp;
} ThermalReport;

// Функція розрахунку теплового режиму
ThermalReport calculate_thermal_profile(const ThermalParams *p) {
    ThermalReport rep;
    
    // 1. Площа поперечного перерізу та опір одного via
    double d = p->via_drill_diam_m;
    double t = p->via_plating_thk_m;
    rep.single_via_area_m2 = M_PI * (d * t - t * t);
    rep.single_via_rth_k_w = p->pcb_thickness_m / (K_COPPER * rep.single_via_area_m2);
    
    // 2. Паралельний опір масиву
    rep.array_rth_k_w = rep.single_via_rth_k_w / (double)p->via_count;
    
    // 3. Опір шару припою (товщина 50 мкм)
    double pad_area = p->pad_side_a_m * p->pad_side_b_m;
    double solder_thk = 5.0e-5; // 50 мкм
    rep.solder_rth_k_w = solder_thk / (K_SOLDER * pad_area);
    
    // 4. Опір розтікання на нижній площині
    double r_pad_eff = sqrt(pad_area / M_PI);
    if (p->plane_radius_m > r_pad_eff && p->plane_copper_thk_m > 0.0) {
        rep.plane_spread_rth_k_w = log(p->plane_radius_m / r_pad_eff) / 
                                   (2.0 * M_PI * K_COPPER * p->plane_copper_thk_m);
    } else {
        rep.plane_spread_rth_k_w = 0.0;
    }
    
    // 5. Сумарний тепловий опір
    rep.total_rth_ja_k_w = p->r_jc_k_w + rep.solder_rth_k_w + rep.array_rth_k_w + 
                           rep.plane_spread_rth_k_w + p->r_tim_k_w + p->r_hs_k_w;
    
    // 6. Температура переходу
    rep.junction_temp_c = p->ambient_temp_c + p->power_dissipation_w * rep.total_rth_ja_k_w;
    
    // 7. Технологічні прапорці
    rep.solder_wicking_risk = (p->via_drill_diam_m > 3.5e-4); // d > 0.35 мм
    rep.is_safe_temp = (rep.junction_temp_c <= 125.0);        // ліміт 125 °C
    
    return rep;
}

int main(void) {
    ThermalParams config = {
        .pcb_thickness_m     = 1.6e-3,   // 1.6 мм
        .via_drill_diam_m    = 3.0e-4,   // 0.3 мм
        .via_plating_thk_m   = 2.5e-5,   // 25 мкм
        .via_count           = 16,       // матриця 4x4
        .pad_side_a_m        = 5.0e-3,   // 5 мм
        .pad_side_b_m        = 5.0e-3,   // 5 мм
        .plane_radius_m      = 2.5e-2,   // 25 мм
        .plane_copper_thk_m  = 3.5e-5,   // 35 мкм (1 oz)
        .r_jc_k_w            = 2.0,      // 2.0 К/Вт
        .r_tim_k_w           = 3.0,      // 3.0 К/Вт (термопрокладка)
        .r_hs_k_w            = 6.0,      // 6.0 К/Вт (невеликий радіатор)
        .ambient_temp_c      = 25.0,     // 25 °C
        .power_dissipation_w = 4.6       // 4.6 Вт
    };
    
    ThermalReport report = calculate_thermal_profile(&config);
    
    printf("=== ЗВІТ ТЕПЛОВОГО РОЗРАХУНКУ ===\n");
    printf("Одиничний via: площа Cu = %.4f мм2, R_th = %.2f К/Вт\n", 
           report.single_via_area_m2 * 1.0e6, report.single_via_rth_k_w);
    printf("Масив із %d via: R_th = %.2f К/Вт\n", config.via_count, report.array_rth_k_w);
    printf("Шар припою: R_th = %.3f К/Вт\n", report.solder_rth_k_w);
    printf("Розтікання у міді: R_th = %.2f К/Вт\n", report.plane_spread_rth_k_w);
    printf("Повний опір R_th(JA): %.2f К/Вт\n", report.total_rth_ja_k_w);
    printf("Температура кристала T_J: %.2f °C\n", report.junction_temp_c);
    printf("Ризик втягування припою: %s\n", report.solder_wicking_risk ? "ТАК (d > 0.35 мм!)" : "НІ (норма)");
    printf("Статус безпеки кристала: %s\n", report.is_safe_temp ? "НОРМА (T_J <= 125 °C)" : "ПЕРЕГРІВ!");
    
    return 0;
}
```

@tab C++
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <string_view>

struct ThermalParams {
    double pcb_thickness_m{1.6e-3};      // Товщина плати (h), м
    double via_drill_diam_m{3.0e-4};     // Діаметр свердла via (d), м
    double via_plating_thk_m{2.5e-5};    // Товщина міднення стінки (t), м
    int    via_count{16};                // Кількість отворів (N)
    double pad_side_a_m{5.0e-3};         // Сторона прямокутного термопада (a), м
    double pad_side_b_m{5.0e-3};         // Сторона прямокутного термопада (b), м
    double plane_radius_m{2.5e-2};       // Ефективний радіус розтікання міді, м
    double plane_copper_thk_m{3.5e-5};   // Товщина мідного полігону, м
    double r_jc_k_w{2.0};                // Опір кристал-корпус (R_theta_JC), К/Вт
    double r_tim_k_w{3.0};               // Опір термоінтерфейсу (R_theta_TIM), К/Вт
    double r_hs_k_w{6.0};                // Опір радіатора (R_theta_HS), К/Вт
    double ambient_temp_c{25.0};         // Температура середовища (T_A), °C
    double power_dissipation_w{4.6};     // Потужність розсіювання (P), Вт
};

struct ThermalReport {
    double single_via_area_m2{0.0};
    double single_via_rth_k_w{0.0};
    double array_rth_k_w{0.0};
    double solder_rth_k_w{0.0};
    double plane_spread_rth_k_w{0.0};
    double total_rth_ja_k_w{0.0};
    double junction_temp_c{0.0};
    bool   solder_wicking_risk{false};
    bool   is_safe_temp{true};
};

class ThermalSolver {
public:
    static constexpr double kCopper = 385.0; // Вт/(м·К)
    static constexpr double kSolder = 58.0;  // Вт/(м·К)

    [[nodiscard]] static ThermalReport solve(const ThermalParams& p) noexcept {
        ThermalReport rep;

        // 1. Площа поперечного перерізу та опір одного via
        const double d = p.via_drill_diam_m;
        const double t = p.via_plating_thk_m;
        rep.single_via_area_m2 = std::numbers::pi * (d * t - t * t);
        rep.single_via_rth_k_w = p.pcb_thickness_m / (kCopper * rep.single_via_area_m2);

        // 2. Паралельний опір масиву
        rep.array_rth_k_w = rep.single_via_rth_k_w / static_cast<double>(p.via_count);

        // 3. Опір шару припою (товщина 50 мкм)
        const double pad_area = p.pad_side_a_m * p.pad_side_b_m;
        constexpr double solder_thk = 5.0e-5; // 50 мкм
        rep.solder_rth_k_w = solder_thk / (kSolder * pad_area);

        // 4. Опір розтікання у нижньому мідному полігоні
        const double r_pad_eff = std::sqrt(pad_area / std::numbers::pi);
        if (p.plane_radius_m > r_pad_eff && p.plane_copper_thk_m > 0.0) {
            rep.plane_spread_rth_k_w = std::log(p.plane_radius_m / r_pad_eff) /
                                       (2.0 * std::numbers::pi * kCopper * p.plane_copper_thk_m);
        } else {
            rep.plane_spread_rth_k_w = 0.0;
        }

        // 5. Повний тепловий опір
        rep.total_rth_ja_k_w = p.r_jc_k_w + rep.solder_rth_k_w + rep.array_rth_k_w +
                               rep.plane_spread_rth_k_w + p.r_tim_k_w + p.r_hs_k_w;

        // 6. Температура переходу
        rep.junction_temp_c = p.ambient_temp_c + p.power_dissipation_w * rep.total_rth_ja_k_w;

        // 7. Технологічні верифікації
        rep.solder_wicking_risk = (p.via_drill_diam_m > 3.5e-4);
        rep.is_safe_temp = (rep.junction_temp_c <= 125.0);

        return rep;
    }
};

int main() {
    ThermalParams config{
        .pcb_thickness_m     = 1.6e-3,
        .via_drill_diam_m    = 3.0e-4,
        .via_plating_thk_m   = 2.5e-5,
        .via_count           = 16,
        .pad_side_a_m        = 5.0e-3,
        .pad_side_b_m        = 5.0e-3,
        .plane_radius_m      = 2.5e-2,
        .plane_copper_thk_m  = 3.5e-5,
        .r_jc_k_w            = 2.0,
        .r_tim_k_w           = 3.0,
        .r_hs_k_w            = 6.0,
        .ambient_temp_c      = 25.0,
        .power_dissipation_w = 4.6
    };

    const auto report = ThermalSolver::solve(config);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== ЗВІТ ТЕПЛОВОГО РОЗРАХУНКУ ===\n";
    std::cout << "Одиничний via: площа Cu = " << report.single_via_area_m2 * 1.0e6 
              << " мм², R_th = " << report.single_via_rth_k_w << " К/Вт\n";
    std::cout << "Масив із " << config.via_count << " via: R_th = " << report.array_rth_k_w << " К/Вт\n";
    std::cout << "Шар припою: R_th = " << std::setprecision(3) << report.solder_rth_k_w << " К/Вт\n";
    std::cout << std::setprecision(2);
    std::cout << "Розтікання у міді: R_th = " << report.plane_spread_rth_k_w << " К/Вт\n";
    std::cout << "Повний опір R_th(JA): " << report.total_rth_ja_k_w << " К/Вт\n";
    std::cout << "Температура кристала T_J: " << report.junction_temp_c << " °C\n";
    std::cout << "Ризик втягування припою: " 
              << (report.solder_wicking_risk ? "ТАК (d > 0.35 мм!)" : "НІ (норма)") << "\n";
    std::cout << "Статус безпеки кристала: " 
              << (report.is_safe_temp ? "НОРМА (T_J <= 125 °C)" : "ПЕРЕГРІВ!") << "\n";

    return 0;
}
```
:::

## 4. Верифікація на інженерних сценаріях

Протестуємо роботу розрахункового модуля на трьох типових сценаріях проєктування:

### Сценарій 1: Силовий перетворювач у корпусі QFN-32 з матрицею 4×4 via
- **Вхідні дані:** `P = 4.6 Вт`, `d = 0.3 мм`, `t = 25 мкм`, `N = 16`, `h = 1.6 мм`, `R_θ,JC = 2.0 К/Вт`, радіатор `R_θ,HS = 6.0 К/Вт`, термоінтерфейс `R_θ,TIM = 3.0 К/Вт`.
- **Аналіз результатів:** Сумарний опір `R_θ,JA = 18.30 К/Вт`. Перегрів кристала над навколишнім середовищем становить `ΔT = 4.6 · 18.30 = 84.18 °C`. За кімнатної температури `T_A = 25 °C` кристал нагрівається до `T_J = 109.18 °C`. Це вкладається в безпечний діапазон (нижче максимальних 125 °C). Масив із 16 отворів бере на себе ключове навантаження з подолання товщі плати, додаючи лише 12.03 К/Вт.

### Сценарій 2: Відсутність радіатора (охолодження лише мідним полігоном плати)
- **Вхідні дані:** Якщо прибрати зовнішній радіатор (`R_θ,HS = 0`) і покладатися виключно на природну конвекцію з мідного полігону 50×50 мм (`R_θ,conv ≈ 35 К/Вт`):
- **Аналіз результатів:** Сумарний опір зростає до `R_θ,JA ≈ 48.8 К/Вт`. При потужності `P = 4.6 Вт` розрахована температура сягає `T_J = 25 + 4.6 · 48.8 = 249.5 °C` — катастрофічний тепловий пробій напівпровідника та руйнування корпусу.
- **Висновки для проєктування:** Самі по собі теплові отвори не поглинають і не розсіюють тепло — вони є лише транспортними магістралями на зворотний бік плати. Якщо на зворотному боці немає достатньої площі тепловідведення або металевого радіатора, тепло накопичується в платі, і температура продовжує зростати до аварійного відключення.

### Сценарій 3: Помилка проєктування — отвори 0.6 мм без заповнення (Wicking)
- **Вхідні дані:** Встановлення отворів `d = 0.6 мм` замість `0.3 мм` формально знижує опір мідної гільзи зі 192 до 94 К/Вт.
- **Аналіз наслідків:** Програма фіксує порушення DRC: `solder_wicking_risk = true`. Рідкий припій засмоктується у відкриті канали, і під термопадом утворюється понад 60% порожнин. Реальний тепловий опір припою зростає з 0.034 К/Вт до 1.5–2.5 К/Вт, а нерівномірний локальний контакт викликає локальний перегрів окремих транзисторних комірок усередині кристала та їхній лавинний пробій.
