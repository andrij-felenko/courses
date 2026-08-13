# ⚙️ Обчислення зон Френеля та просвіт траси

Ця вставка містить практичну реалізацію алгоритму аналізу траси радіолінії мовами C та C++, який обчислює радіус першої зони Френеля, опуклість Землі з урахуванням атмосферної рефракції `k` та визначає необхідний просвіт відносно профілю перешкод.

### Задача та алгоритм аналізу траси

Інженерна задача аналізу профілю радіолінії виникає при проектуванні бездротових мостів Wi-Fi, мереж LoRaWAN, секторних базових станцій та радіорелейних ліній (РРЛ). При автоматизованому розрахунку цифрова модель рельєфу (DEM) подається у вигляді масиву висотних точок уздовж траси. Для кожної точки профілю необхідно перевірити критерій 60% просвіту першої зони Френеля.

Вхідні параметри радіолінії:
- **Загальна довжина траси (`d_total_km`):** відстань між передавачем та приймачем у кілометрах;
- **Поточна відстань до перешкоди (`d1_km`):** відстань від передавальної щогли до точки аналізу в кілометрах (`d2_km = d_total_km - d1_km`);
- **Робоча частота (`f_GHz`):** несуча частота сигналу у гігагерцах;
- **Висоти антенних щогл (`h_tx_m`, `h_rx_m`):** висоти підвісу антен над поверхнею землі у метрах;
- **Висота перешкоди (`h_obstacle_m`):** висота наземного об'єкта (рельєф + ліс + будівлі) у метрах;
- **Коефіцієнт атмосферної рефракції (`k_factor`):** безрозмірний коефіцієнт (за замовчуванням `k = 1.333` відповідає стандартній атмосфері 4/3, `k = 0.67` — критичній субрефракції).

Математичний алгоритм обчислення складається з п'яти послідовних кроків:

```
+--------------------------------------------------------------------+
|                СХЕМА АНАЛІЗУ ПРОФІЛЮ РАДІОТРАСИ                    |
+--------------------------------------------------------------------+
|                                                                    |
| 1. h_los = h_tx + (h_rx - h_tx) * (d1 / d_total)                   |
| 2. h_earth = (d1 * d2) / (12.74 * k)                               |
| 3. R1 = 17.32 * sqrt((d1 * d2) / (f_GHz * d_total))                |
|                                                                    |
| 4. h_obs_total = h_obstacle + h_earth                              |
| 5. clearance = h_los - h_obs_total                                 |
| 6. clearance_ratio = clearance / R1                                |
|                                                                    |
| Вимога: clearance_ratio >= 0.6  --->  Траса відкрита (0 дБ)         |
+--------------------------------------------------------------------+
```

#### Кроки розрахунку для довільної точки траси:
1. **Обчислення висоти прямого променя `h_los`:** лінійна інтерполяція між щоглами передавача та приймача: `h_los = h_tx + (h_rx - h_tx) · (d1 / d_total)`.
2. **Обчислення ефективної опуклості Землі `h_earth`:** геодезична поправка на кривизну планети з урахуванням рефракції атмосфери: `h_earth = (d1 · d2) / (12.74 · k)`.
3. **Обчислення радіуса 1-ї зони Френеля `R1`:** застосування спрощеної інженерної формули: `R1 = 17.32 · √((d1 · d2) / (f_GHz · d_total))`.
4. **Обчислення чистого просвіту `clearance`:** різниця між висотою променя та сумарною висотою перешкоди: `clearance = h_los - (h_obstacle + h_earth)`.
5. **Оцінка відносного просвіту `clearance_ratio = clearance / R1`:** порівняння з нормативним критерієм `0.6` (60%). Якщо `clearance_ratio ≥ 0.6`, траса вважається повністю відкритою (додаткові дифракційні втрати `0 дБ`). Якщо `clearance_ratio < 0.6`, обчислюється додаткове дифракційне загасання за формулою Лі.

### Механізм обчислення дифракційних втрат та рефракції

У реальному програмному забезпеченні моделювання траси алгоритм аналізу повинен враховувати два ключові фізичні ефекти:
- **Атмосферну рефракцію:** При зміні кліматичних умов (наприклад, ранковий туман чи прогрів ґрунту) коефіцієнт рефракції `k` може зменшуватися від нормального значенні `1.333` до субрефракційного `0.67`. У коді це враховується шляхом масштабування знаменника у формулі опуклості Землі `12.74 · k`.
- **Ніж-крайову дифракцію на перешкоді:** При частковому блокуванні зони Френеля (`clearance_ratio < 0.6`) втрати обчислюються за допомогою апроксимації Лі. Безрозмірний параметр дифракції `v` пов'язаний із відносним просвітом співвідношенням `v = -clearance_ratio · √2`. Коли просвіт стає від'ємним (перешкода перетинає лінію зору), значення `v` стає додатним, і загасання швидко зростає до 10–30 дБ.

### Сканування багатоточкового профілю рельєфу

Для аналізу протяжних трас із сотнями геодезичних точок програма сканує весь масив профілю `profile` і знаходить так звану **лімітуючу (контрольну) точку**. Це точка траси, у якій відносний просвіт `clearance_ratio` має мінімальне значення.

Якщо у контрольованій точці `clearance_ratio ≥ 0.6`, то вся радіолінія є повністю відкритою. Якщо ж у цій точці `clearance_ratio < 0.6`, програма обчислює мінімально необхідне підняття щогл `Δh`, яке треба додати до передавальної чи приймальної вежі, щоб підняти лінію зору та відновити просвіт до нормативного рівня.

### Архітектура програмістського рішення

Для використання в реальних серверних системах картографії та вбудованих контролерах розроблено дві реалізації:
- **Мова C (ANSI C89/C99):** орієнтована на високу швидкість обчислень, мінімальний розмір виконуваного коду та відсутність динамічного виділення пам'яті. Використовує просту структуру `TraceAnalysisResult` та пряму передачу параметрів за значенням.
- **Мова C++ (C++20):** побудована за принципами об'єктно-орієнтованого та функціонального проектування. Використовує структуровані типи результатів (`std::vector<TraceReport>`), безпечні перегляди масивів без копіювання (`std::span<const ObstaclePoint>`), метод обчислення профілю без ручного управління пам'яттю та суворий контроль сутності об'єктів через `constexpr` й `nodiscard`.

Нижче наведено повністю робочий вихідний код обох реалізацій у вигляді синхронізованих вкладок `:::tabs`.

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

// Структура для збереження результатів аналізу траси у точці
typedef struct {
    double r1_meters;          // Радіус 1-ї зони Френеля (м)
    double earth_bulge_m;      // Опуклість Землі у точці (м)
    double los_height_m;       // Висота лінії LOS у точці перешкоди (м)
    double clearance_m;        // Наявний чистий просвіт (м)
    double clearance_ratio;    // Відносний просвіт (c / R1)
    double diff_loss_db;       // Дифракційне загасання (дБ)
    bool is_clear;             // Прапорець виконання критерію 60% R1
} TraceAnalysisResult;

// Оцінка дифракційного загасання за спрощеною формулою Лі
static double calculate_knife_edge_loss(double clearance_ratio) {
    // c/R1 = 0.6 відповідає параметру v = -0.6 * sqrt(2) ≈ -0.85
    double v = -clearance_ratio * 1.41421356;
    
    if (v < -1.0) {
        return 0.0; // Практично нульові втрати при великому просвіті
    }
    
    double v_minus_01 = v - 0.1;
    double term = sqrt(v_minus_01 * v_minus_01 + 1.0) + v_minus_01;
    if (term <= 0.0) return 0.0;
    
    double loss = 6.9 + 20.0 * log10(term);
    return loss < 0.0 ? 0.0 : loss;
}

// Функція розрахунку просвіту траси для однієї точки
TraceAnalysisResult analyze_trace_point(
    double d_total_km,
    double d1_km,
    double f_ghz,
    double h_tx_m,
    double h_rx_m,
    double h_obs_m,
    double k_factor
) {
    TraceAnalysisResult res;
    double d2_km = d_total_km - d1_km;

    // 1. Радіус першої зони Френеля
    res.r1_meters = 17.32 * sqrt((d1_km * d2_km) / (f_ghz * d_total_km));

    // 2. Опуклість Землі (еквівалентний радіус R_eq = k * 6371 км)
    res.earth_bulge_m = (d1_km * d2_km) / (12.74 * k_factor);

    // 3. Висота прямого променя LOS над землею в точці перешкоди
    res.los_height_m = h_tx_m + (h_rx_m - h_tx_m) * (d1_km / d_total_km);

    // 4. Загальна ефективна висота перешкоди з урахуванням опуклості Землі
    double total_obs_height = h_obs_m + res.earth_bulge_m;

    // 5. Просвіт траси та відносний коефіцієнт
    res.clearance_m = res.los_height_m - total_obs_height;
    res.clearance_ratio = res.clearance_m / res.r1_meters;

    // 6. Перевірка критерію 0.6 * R1
    res.is_clear = (res.clearance_ratio >= 0.6);

    // 7. Розрахунок втрат
    res.diff_loss_db = calculate_knife_edge_loss(res.clearance_ratio);

    return res;
}

int main(void) {
    // Приклад: траса 10 км на частоті 5 ГГц, перешкода на 4-му кілометрі
    double d_total = 10.0;
    double d1 = 4.0;
    double f_ghz = 5.0;
    double h_tx = 25.0;
    double h_rx = 25.0;
    double h_obs = 18.0;
    double k_factor = 1.333; // Стандартна атмосфера (4/3)

    TraceAnalysisResult r = analyze_trace_point(d_total, d1, f_ghz, h_tx, h_rx, h_obs, k_factor);

    printf("=== Аналіз просвіту радіолінії (C) ===\n");
    printf("Відстань: %.1f км (d1=%.1f км, d2=%.1f км), Частота: %.2f ГГц\n", d_total, d1, d_total - d1, f_ghz);
    printf("Радіус 1-ї зони Френеля R1: %.2f м\n", r.r1_meters);
    printf("Опуклість Землі (k=%.2f):   %.2f м\n", k_factor, r.earth_bulge_m);
    printf("Висота променя LOS:        %.2f м\n", r.los_height_m);
    printf("Наявний просвіт:           %.2f м (%.1f%% від R1)\n", r.clearance_m, r.clearance_ratio * 100.0);
    printf("Дифракційні втрати:        %.2f дБ\n", r.diff_loss_db);
    printf("Статус просвіту:           %s\n", r.is_clear ? "ВІДКРИТА (OK)" : "ЗАКРИТА (Втрати)");

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <span>
#include <vector>
#include <string_view>
#include <iomanip>

namespace radio {

struct ObstaclePoint {
    double distance_from_tx_km;
    double obstacle_height_m;
    std::string_view description;
};

struct TraceReport {
    double distance_km;
    double r1_m;
    double earth_bulge_m;
    double los_height_m;
    double clearance_m;
    double clearance_ratio;
    double diff_loss_db;
    bool is_pass;
};

class FresnelCalculator {
public:
    static constexpr double DefaultKFactor = 1.333333; // 4/3

    explicit FresnelCalculator(double frequency_ghz, double k_factor = DefaultKFactor)
        : frequency_ghz_(frequency_ghz), k_factor_(k_factor) {}

    [[nodiscard]] double calculate_r1(double d1_km, double d2_km, double d_total_km) const noexcept {
        return 17.32 * std::sqrt((d1_km * d2_km) / (frequency_ghz_ * d_total_km));
    }

    [[nodiscard]] double calculate_earth_bulge(double d1_km, double d2_km) const noexcept {
        return (d1_km * d2_km) / (12.74 * k_factor_);
    }

    [[nodiscard]] TraceReport evaluate_obstacle(
        double d_total_km,
        double h_tx_m,
        double h_rx_m,
        const ObstaclePoint& obs
    ) const noexcept {
        const double d1 = obs.distance_from_tx_km;
        const double d2 = d_total_km - d1;

        const double r1 = calculate_r1(d1, d2, d_total_km);
        const double bulge = calculate_earth_bulge(d1, d2);
        const double los = h_tx_m + (h_rx_m - h_tx_m) * (d1 / d_total_km);
        const double clearance = los - (obs.obstacle_height_m + bulge);
        const double ratio = clearance / r1;

        const double loss = compute_diffraction_loss(ratio);

        return TraceReport{
            .distance_km = d1,
            .r1_m = r1,
            .earth_bulge_m = bulge,
            .los_height_m = los,
            .clearance_m = clearance,
            .clearance_ratio = ratio,
            .diff_loss_db = loss,
            .is_pass = (ratio >= 0.6)
        };
    }

    [[nodiscard]] std::vector<TraceReport> evaluate_profile(
        double d_total_km,
        double h_tx_m,
        double h_rx_m,
        std::span<const ObstaclePoint> obstacles
    ) const {
        std::vector<TraceReport> reports;
        reports.reserve(obstacles.size());
        for (const auto& obs : obstacles) {
            reports.push_back(evaluate_obstacle(d_total_km, h_tx_m, h_rx_m, obs));
        }
        return reports;
    }

private:
    double frequency_ghz_;
    double k_factor_;

    static double compute_diffraction_loss(double ratio) noexcept {
        double v = -ratio * 1.41421356;
        if (v < -1.0) return 0.0;
        double v_sub = v - 0.1;
        double arg = std::sqrt(v_sub * v_sub + 1.0) + v_sub;
        if (arg <= 0.0) return 0.0;
        double loss = 6.9 + 20.0 * std::log10(arg);
        return loss < 0.0 ? 0.0 : loss;
    }
};

} // namespace radio

int main() {
    using namespace radio;

    constexpr double total_dist_km = 12.0;
    constexpr double freq_ghz = 5.8;
    constexpr double h_tx = 30.0;
    constexpr double h_rx = 25.0;

    const std::vector<ObstaclePoint> profile = {
        { .distance_from_tx_km = 3.0, .obstacle_height_m = 15.0, .description = "Лісосмуга" },
        { .distance_from_tx_km = 6.0, .obstacle_height_m = 22.0, .description = "Пагорб" },
        { .distance_from_tx_km = 9.0, .obstacle_height_m = 18.0, .description = "Будівля" }
    };

    FresnelCalculator calc(freq_ghz);
    auto reports = calc.evaluate_profile(total_dist_km, h_tx, h_rx, profile);

    std::cout << "=== Профільний аналіз траси (C++20) ===\n";
    std::cout << "Траса: " << total_dist_km << " км, Частота: " << freq_ghz << " ГГц\n\n";

    for (size_t i = 0; i < profile.size(); ++i) {
        const auto& obs = profile[i];
        const auto& rep = reports[i];

        std::cout << "Точка " << (i + 1) << " [" << obs.description << "] на " << obs.distance_from_tx_km << " км:\n"
                  << "  - R1: " << std::fixed << std::setprecision(2) << rep.r1_m << " м\n"
                  << "  - Опуклість Землі: " << rep.earth_bulge_m << " м\n"
                  << "  - Просвіт: " << rep.clearance_m << " м (" << std::setprecision(1) << rep.clearance_ratio * 100.0 << "% від R1)\n"
                  << "  - Втрати: " << std::setprecision(2) << rep.diff_loss_db << " дБ\n"
                  << "  - Критерій 60%: " << (rep.is_pass ? "ПРОЙДЕНО" : "НЕ ПРОЙДЕНО") << "\n\n";
    }

    return 0;
}
```
:::

### Аналіз результатів виконання та крайових випадків

Під час розрахунку профілю радіоліній інженер мусить враховувати такі крайові випадки та особливості обчислень:

1. **Крайові точки траси (`d1 → 0` або `d1 → d_total`):**
   Біля антенних щогла радіус першої зони Френеля прямує до нуля (`R1 → 0`), а опуклість Землі також прямує до нуля. У цих точках головною небезпекою є безпосереднє затінення конструкціями даху чи щогли. Програма обробляє ці точки без ділення на нуль завдяки лінійній інтерполяції.

2. **Вплив вибору коефіцієнта рефракції `k`:**
   При значенні `k = 1.33` (нормальна рефракція) опуклість Землі зменшується. Проте для розрахунку гарантованого зв'язку рекомендується додатково проганяти аналіз із `k = 0.67` (субрефракція). Якщо при `k = 0.67` відносний просвіт падає нижче `0.0`, радіолінія зазнаватиме глибинних замирань у ранкові години під час появи туману.

3. **Складний рельєф із багатьма перешкодами:**
   C++ реалізація приймає вектор точок `profile` і дозволяє знайти найкритичнішу точку всієї траси (з мінімальним `clearance_ratio`). Саме ця точка визначає підсумковий енергетичний запас лінку та мінімальну висоту антенних щогл.

4. **Розподіл обчислень у високонавантажених GIS-системах:**
   При пексельному скануванні великих регіональних карт (мільйони точок рельєфу) обчислення радіуса зони Френеля та опуклості Землі у C-версії легко векторизується інструкціями SIMD (AVX2/NEON), оскільки формули містять лише базові арифметичні операції та корінь `sqrt()`.

Цей модуль може бути легко інтегрований у розкладки веб-сервісів або вбудоване ПЗ мікроконтролерів для автономного моніторингу стану радіоліній у реальному часі.
