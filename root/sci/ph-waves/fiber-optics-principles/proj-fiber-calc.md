# ⚙️ Обчислення параметрів волокна (NA, V-число, дисперсія, загасання траси)

Практичний розрахунок геометричних, модових та енергетичних параметрів оптичного волокна є необхідним етапом під час проектування волоконно-оптичних ліній зв'язку (ВОЛЗ) будь-якого рівня — від локальних підсистем дата-центрів до трансконтинентальних магістралей.

Утиліта, подана нижче мовами C та C++, автоматизує повний цикл інженерного аналізу оптичного волокна та розрахунку оптичного бюджету траси.

---

### Архітектура утиліти та математичні моделі

Програма обчислює шість фундаментальних фізичних параметрів для заданої структури волокна та довжини хвилі випромінювання:

1. **Числова апертура (`NA`)**: Обчислюється за базовою тригонометричною формулою `NA = √(n₁² − n₂²)`. Вона описує максимальний світлозбірний конус волокна.
2. **Апертурний кут падіння (`θ_a`)**: Кут у повітрі `θ_a = arcsin(NA / n₀)`, у межах якого світловий промінь, що падає на торець волокна, гарантовано зазнає повного внутрішнього відбиття на межі серцевини та оболонки.
3. **Параметр нормованої частоти (`V`)**: Обчислюється як `V = (2π · a / λ) · NA`. Безрозмірний параметр хвильового рівняння, який визначає модову місткість диелектричного хвилеводу.
4. **Оцінка одномодового режиму**: Якщо `V < 2.405`, волокно працює у строго одномодовому режимі (підтримується лише хвиля `HE₁₁`). Якщо `V ≥ 2.405`, волокно вважається багатомодовим.
5. **Кількість допустимих мод (`M`)**: Для одномодового волокна `M = 1`. Для багатомодового волокна зі ступінчастим профілем кількість мод оцінюється параболічним наближенням хвильових станів: `M ≈ round(V² / 2)`.
6. **Довжина хвилі відсічки (`λc`)**: Гранична довжина хвилі `λc = (2π · a · NA) / 2.405`, вище якої волокно гарантовано стає одномодовим.
7. **Бюджет оптичної потужності траси**: Сумарні втрати сигналу в лінії `A_total = (L · α) + (N_splice · α_splice) + (N_conn · α_conn)` та обчислення енергетичного запасу `Margin = (P_tx − P_rx) − A_total`. Якщо запас перевищує стандартний норматив у `3.0 дБ`, траса вважається придатною для експлуатації.

---

### Інженерні крайові випадки та обчислювальні нюанси

Під час розробки високоточних оптичних калькуляторів слід враховувати такі крайові випадки:
- **Умова фізичної коректності**: Показник заломлення серцевини `n₁` мусить бути строго більшим за показник оболонки `n₂`. Якщо `n₁ ≤ n₂`, виникає від'ємне значення під коренем, що відповідає відсутності хвилеводного ефекту (світло витікає у зовнішнє середовище).
- **Обмеження апертурного кута**: Якщо розрахована `NA > 1.0` (що трапляється в деяких пластикових волокнах із великою різницею показників), синус `sin θ_a` затискається до `1.0`, що відповідає максимальному теоретичному куту прийняття `90°`.
- **Точність плаваючої крапки**: Для одномодових волокон різниця показників `n₁ − n₂` є дуже малою (наприклад, `1.4677 − 1.4624 = 0.0053`). Щоб уникнути втрати точності під час віднімання близьких чисел, використовується математична тип високої точності `double`.

---

### Покроковий розбір виконання алгоритму

Обчислення виконуються послідовно в п'ять кроків:
1. **Перевірка вхідних параметрів**: Модуль перевіряє, щоб радіус серцевини `a` та довжина хвилі `λ` були строго додатними числами, а показник `n₁` перевищував `n₂`. При виявленні некоректних даних обчислення негайно зупиняються з поверненням помилки.
2. **Перетворення одиниць вимірювання**: Довжина хвилі переводиться з нанометрів у метри (`1 нм = 10⁻⁹ м`), а радіус серцевини подається в метрах.
3. **Обчислення модових параметрів**: За формулами хвилеводного аналізу визначається `V`-число та довжина хвилі відсічки `λc`.
4. **Обчислення лінійних втрат**: Лінійні втрати розраховуються як добуток довжини траси на кілометричний коефіцієнт згасання плюс сума втрат на роз'ємах та зварювальних стиках.
5. **Формування звітного висновку**: Порівняння оптичного запасу `Margin` із нормативом `3.0 дБ`.

---

### Методологія розрахунку запасу потужності та штрафу за дисперсію

Під час реального проектування ВОЛЗ інженери враховують не лише статичні згасання в склі та стиках, але й додаткові динамічні фактори:
- **Штраф за дисперсію (*Dispersion Penalty*)**: Розмиття імпульсу за рахунок хроматичної дисперсії призводить до того, що фотодетектор сприймає розширений фронт хвилі, що еквівалентно додатковим втратам потужності на `1.0–2.0 дБ`.
- **Деградація оптичного передавача**: З часом випромінювальна потужність лазерного діода спадає через старіння гетероструктури (зазвичай закладається деградаційний штраф `1.0–1.5 дБ`).
- **Температурний запас**: Зміна температури від `-40°C` до `+60°C` викликає мікродеформації полімерного покриття кабелю, що збільшує згасання на `0.02–0.05 дБ/км`.
- **Запас на ремонтні зварювання**: Упродовж 25 років експлуатації підземний кабель може зазнавати випадкових обривів під час земляних робіт. На кожну ділянку траси довжиною 10 км закладається запас на 2–3 ремонтні муфти.

Саме тому в інженерній утиліті поріг надійного оптичного запасу прийнятий рівним `Margin ≥ 3.0 дБ`.

---

### Інструкції з компіляції та запуску

Програму можна скомпілювати будь-яким сучасним компілятором C або C++:

- **Компіляція версії C (GCC / Clang)**:
  `gcc -O2 -std=c99 proj-fiber-calc.c -o fiber_calc -lm`
- **Компіляція версії C++ (GCC / Clang)**:
  `g++ -O2 -std=c++20 proj-fiber-calc.cpp -o fiber_calc_cpp`
- **Компіляція в MSVC (Windows Command Prompt)**:
  `cl /EHsc /std:c++20 proj-fiber-calc.cpp`

---

### Реалізація утиліти мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_VAL 3.14159265358979323846

/* Структура параметрів оптичного волокна */
typedef struct {
    double n1;           /* Показник заломлення серцевини */
    double n2;           /* Показник заломлення оболонки */
    double core_radius;  /* Радіус серцевини (в метрах) */
    double alpha_dB_km;  /* Коефіцієнт згасання (дБ/км) */
} FiberParams;

/* Структура результатів розрахунку */
typedef struct {
    double na;                  /* Числова апертура NA */
    double acceptance_angle_deg;/* Апертурний кут вводу в повітрі (градуси) */
    double v_number;            /* Нормована частота V */
    bool is_single_mode;        /* Прапорець одномодового режиму */
    unsigned long mode_count;   /* Оцінка кількості мод M */
    double cutoff_wavelength_nm;/* Довжина хвилі відсічки (нм) */
} FiberAnalysis;

/* Структура бюджету потужності траси */
typedef struct {
    double length_km;       /* Довжина лінійного кабелю (км) */
    int splice_count;       /* Кількість зварних зрощувань */
    double splice_loss_dB;  /* Втрати на одне зварювання (дБ) */
    int connector_count;    /* Кількість роз'ємів */
    double conn_loss_dB;    /* Втрати на один роз'єм (дБ) */
    double tx_power_dBm;    /* Потужність передавача (дБм) */
    double rx_sens_dBm;     /* Чутливість приймача (дБм) */
} LinkBudgetInput;

typedef struct {
    double total_attenuation_dB; /* Загальні втрати траси (дБ) */
    double power_margin_dB;      /* Оптичний запас потужності (дБ) */
    bool is_link_viable;         /* Прапорець працездатності лінії */
} LinkBudgetResult;

/* Обчислення оптичних характеристик волокна */
bool analyze_fiber(const FiberParams *fiber, double wavelength_nm, FiberAnalysis *out) {
    if (!fiber || !out || fiber->n1 <= fiber->n2 || fiber->core_radius <= 0.0 || wavelength_nm <= 0.0) {
        return false;
    }

    double n1_sq = fiber->n1 * fiber->n1;
    double n2_sq = fiber->n2 * fiber->n2;
    out->na = sqrt(n1_sq - n2_sq);

    double sin_theta_a = out->na / 1.0; /* для повітря n0 = 1.0 */
    if (sin_theta_a > 1.0) sin_theta_a = 1.0;
    out->acceptance_angle_deg = asin(sin_theta_a) * (180.0 / M_PI_VAL);

    double wavelength_m = wavelength_nm * 1e-9;
    out->v_number = (2.0 * M_PI_VAL * fiber->core_radius / wavelength_m) * out->na;
    out->is_single_mode = (out->v_number < 2.405);

    if (out->is_single_mode) {
        out->mode_count = 1;
    } else {
        out->mode_count = (unsigned long)round((out->v_number * out->v_number) / 2.0);
    }

    out->cutoff_wavelength_nm = ((2.0 * M_PI_VAL * fiber->core_radius * out->na) / 2.405) * 1e9;
    return true;
}

/* Обчислення бюджету оптичного сигналу */
bool calculate_link_budget(const FiberParams *fiber, const LinkBudgetInput *link, LinkBudgetResult *out) {
    if (!fiber || !link || !out || link->length_km < 0.0) {
        return false;
    }

    double fiber_loss = link->length_km * fiber->alpha_dB_km;
    double splices_loss = link->splice_count * link->splice_loss_dB;
    double conns_loss = link->connector_count * link->conn_loss_dB;

    out->total_attenuation_dB = fiber_loss + splices_loss + conns_loss;
    double available_power = link->tx_power_dBm - link->rx_sens_dBm;
    out->power_margin_dB = available_power - out->total_attenuation_dB;
    out->is_link_viable = (out->power_margin_dB >= 3.0); /* вимога запасу мінімум 3 дБ */

    return true;
}

int main(void) {
    /* Приклад: Одномодове волокно SMF-28 (1310 нм) */
    FiberParams smf = {
        .n1 = 1.4677,
        .n2 = 1.4624,
        .core_radius = 4.1e-6, /* 8.2 мкм діаметр */
        .alpha_dB_km = 0.35
    };

    FiberAnalysis analysis;
    if (analyze_fiber(&smf, 1310.0, &analysis)) {
        printf("--- Аналіз волокна SMF-28 (1310 нм) ---\n");
        printf("Числова апертура (NA): %.4f\n", analysis.na);
        printf("Апертурний кут вводу:  %.2f deg\n", analysis.acceptance_angle_deg);
        printf("Параметр V:           %.3f (%s)\n", analysis.v_number,
               analysis.is_single_mode ? "Одномодове" : "Багатомодове");
        printf("Довжина хвилі відсічки: %.1f nm\n\n", analysis.cutoff_wavelength_nm);
    }

    LinkBudgetInput link = {
        .length_km = 40.0,
        .splice_count = 8,
        .splice_loss_dB = 0.05,
        .connector_count = 4,
        .conn_loss_dB = 0.30,
        .tx_power_dBm = 0.0,    /* 1 мВт */
        .rx_sens_dBm = -30.0   /* 1 мкВт */
    };

    LinkBudgetResult budget;
    if (calculate_link_budget(&smf, &link, &budget)) {
        printf("--- Бюджет оптичної траси (40 км) ---\n");
        printf("Загальні втрати траси:   %.2f dB\n", budget.total_attenuation_dB);
        printf("Запас потужності:        %.2f dB\n", budget.power_margin_dB);
        printf("Статус траси:            %s\n", budget.is_link_viable ? "ПРОЙШЛА (OK)" : "НЕВДАЧА (Втрати перевищують норматив)");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <optional>
#include <string_view>

struct FiberParams {
    double n1{1.4677};          // Показник заломлення серцевини
    double n2{1.4624};          // Показник заломлення оболонки
    double core_radius_m{4.1e-6};// Радіус серцевини (м)
    double alpha_dB_km{0.35};   // Коефіцієнт згасання (дБ/км)
};

struct FiberAnalysis {
    double na;                  // Числова апертура NA
    double acceptance_angle_deg;// Кут вводу в повітрі
    double v_number;            // Нормована частота V
    bool is_single_mode;        // Прапорець одномодового режиму
    std::size_t mode_count;     // Оцінка кількості мод
    double cutoff_wavelength_nm;// Довжина хвилі відсічки
};

struct LinkBudgetInput {
    double length_km{10.0};
    int splice_count{2};
    double splice_loss_dB{0.05};
    int connector_count{2};
    double conn_loss_dB{0.30};
    double tx_power_dBm{0.0};
    double rx_sens_dBm{-30.0};
};

struct LinkBudgetResult {
    double total_attenuation_dB;
    double power_margin_dB;
    bool is_link_viable;
};

class FiberCalculator {
public:
    static std::optional<FiberAnalysis> analyze(const FiberParams& fiber, double wavelength_nm) noexcept {
        if (fiber.n1 <= fiber.n2 || fiber.core_radius_m <= 0.0 || wavelength_nm <= 0.0) {
            return std::nullopt;
        }

        const double na = std::sqrt(fiber.n1 * fiber.n1 - fiber.n2 * fiber.n2);
        const double sin_theta = std::min(1.0, na);
        const double acceptance_angle = std::asin(sin_theta) * (180.0 / std::numbers::pi);

        const double wavelength_m = wavelength_nm * 1e-9;
        const double v_num = (2.0 * std::numbers::pi * fiber.core_radius_m / wavelength_m) * na;
        const bool single_mode = (v_num < 2.405);

        const std::size_t modes = single_mode ? 1 : static_cast<std::size_t>(std::round((v_num * v_num) / 2.0));
        const double cutoff_nm = ((2.0 * std::numbers::pi * fiber.core_radius_m * na) / 2.405) * 1e9;

        return FiberAnalysis{
            .na = na,
            .acceptance_angle_deg = acceptance_angle,
            .v_number = v_num,
            .is_single_mode = single_mode,
            .mode_count = modes,
            .cutoff_wavelength_nm = cutoff_nm
        };
    }

    static std::optional<LinkBudgetResult> calculateLink(const FiberParams& fiber, const LinkBudgetInput& link) noexcept {
        if (link.length_km < 0.0) return std::nullopt;

        const double fiber_loss = link.length_km * fiber.alpha_dB_km;
        const double splices_loss = link.splice_count * link.splice_loss_dB;
        const double conns_loss = link.connector_count * link.conn_loss_dB;

        const double total_loss = fiber_loss + splices_loss + conns_loss;
        const double available_power = link.tx_power_dBm - link.rx_sens_dBm;
        const double margin = available_power - total_loss;

        return LinkBudgetResult{
            .total_attenuation_dB = total_loss,
            .power_margin_dB = margin,
            .is_link_viable = (margin >= 3.0)
        };
    }
};

int main() {
    constexpr FiberParams smf28{
        .n1 = 1.4677,
        .n2 = 1.4624,
        .core_radius_m = 4.1e-6,
        .alpha_dB_km = 0.35
    };

    if (auto res = FiberCalculator::analyze(smf28, 1310.0)) {
        std::cout << "--- Аналіз волокна SMF-28 (C++) ---\n"
                  << "Числова апертура (NA): " << res->na << "\n"
                  << "Апертурний кут:        " << res->acceptance_angle_deg << " deg\n"
                  << "Параметр V:           " << res->v_number 
                  << (res->is_single_mode ? " (Одномодове)" : " (Багатомодове)") << "\n"
                  << "Відсічка λc:          " << res->cutoff_wavelength_nm << " nm\n\n";
    }

    constexpr LinkBudgetInput link{
        .length_km = 40.0,
        .splice_count = 8,
        .splice_loss_dB = 0.05,
        .connector_count = 4,
        .conn_loss_dB = 0.30,
        .tx_power_dBm = 0.0,
        .rx_sens_dBm = -30.0
    };

    if (auto budget = FiberCalculator::calculateLink(smf28, link)) {
        std::cout << "--- Бюджет оптичної траси (C++) ---\n"
                  << "Загальні втрати: " << budget->total_attenuation_dB << " dB\n"
                  << "Запас потужності: " << budget->power_margin_dB << " dB\n"
                  << "Статус лінії:     " << (budget->is_link_viable ? "ПРОЙШЛА (OK)" : "НЕВДАЧА") << "\n";
    }

    return 0;
}
```
:::

---

### Аналіз ідіоматичних відмінностей між C та C++

Реалізація інженерної утиліти на двох мовах ілюструє концептуальну різницю у підходах до проектиування програмного забезпечення:

1. **Безпека обробки помилок**: У версії на мові C функція повертає прапорець `bool` і заповнює результат через вказівники на вихідні структури. У версії на C++ використовується сучасний шаблон `std::optional<T>`, що виключає ризик роботи з необов'язковими або некоректно ініціалізованими даними.
2. **Константні обчислення під час компіляції (`constexpr`)**: У C++ параметри волокна та параметри траси оголошені як `constexpr`. Це дозволяє компілятору виконувати частину геометричних та оптичних розрахунків безпосередньо на етапі компіляції програми, зменшуючи навантаження у рантаймі.
3. **Стандартні математичні константи**: У C використовуються власні макроси на кшталт `M_PI_VAL`, тоді як C++20 надає стандартні типубезпечні константи з модуля `<numbers>` (`std::numbers::pi`).
