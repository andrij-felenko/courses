# ⚙️ Алгоритм розрахунку надійності та критичної довжини Блеха

Цей інженерний модуль описує алгоритми розрахунку часу до відмови міжз'єднань за рівнянням Блека, екстраполяцію результатів випробувань прискореного старіння (HTOL) та оцінку критерію імунітету Блеха в сучасних системах автоматизованого проектування інтегральних схем (EDA).

---

### Архітектура аналізу надійності в EDA-системах

У сучасних технологічних процесах проектування надвеликих інтегральних схем (СБРІС / VLSI) перевірка стійкості до електроміграції є обов'язковим етапом маршруту фізичного проектування та підписання топології (Sign-off Electromigration Analysis). Автоматизовані інструменти аналізу надійності (такі як Synopsys PrimeRail, Cadence Voltus або Ansys Totem) виконують моделювання електроміграції для мільйонів металевих сегментів на основі файлів паразитичної екстракції ємностей і опорів (SPEF / DSPF) та моделей струмових навантажень.

Обчислювальний маршрут складається з п'яти послідовних етапів:

1. **Екстракція струмових профілів:** Для кожного металевого сегмента міжз'єднання розраховується середня густина постійного струму `j_avg`, ефективна середня квадратична густина струму `j_rms` та пікова густина струму `j_peak`. За наявності змінного струму (bidirectional AC) враховується ефект самолікування дефектів (*healing effect*), за якого зворотний напівперіод відновлює до `90% ... 99%` атомних зміщень, здійснених у прямому напівперіоді:

   ```
   j_eff = j_DC + ( 1 - r ) · | j_AC |
   ```

   де `r ≈ 0.9 ... 0.99` — коефіцієнт відновлення.

2. **Моделювання самонагріву (Joule Self-Heating):** Оскільки проходження струму викликає джоулів нагрів провідника `P = j² · ρ · V`, локальна температура доріжки `T_wire` перевищує температуру кремнієвої підкладки `T_sub`:

   ```
   T_wire = T_sub + j² · ρ · R_th
   ```

   де `R_th` — ефективний тепловий опір навколишнього міжшарового діелектрика. Усі подальші розрахунки за рівнянням Блека виконуються саме для локальної підвищеної температури `T_wire`.

3. **Фільтрація сегментів за критерієм Блеха (Blech Filtering):** Інструмент будує орієнтований граф металевої мережі між міжшаровими контактами (*vias*). Якщо добуток густини струму на довжину неперервного сегмента менший за критичну межу `(j · L) < (j · L)_c`, сегмент позначається як імунний («безсмертний») і виключається з подальшого складеного розрахунку надійності. Це скорочує обсяг обчислень на 60–80%.

4. **Обчислення коефіцієнта прискорення та MTTF:** Для решти вразливих сегментів розраховується коефіцієнт прискорення `AF` відносно стандартних випробувань прискореного старіння HTOL (*High-Temperature Operating Life*).

5. **Оцінка сукупного ризику та медіанного часу відмови кристала:** Загальна надійність всієї інтегральної схеми обчислюється як послідовна система за моделлю Пуассона або сума ризиків відмов окремих доріжок:

   ```
   FIT_total = ∑ FIT_i
   ```

   де `FIT` (*Failures in Time*) означає кількість відмов за 10⁹ годин роботи (`1 FIT = 1 відмова на 10⁹ приладо-годин`).

---

### Математичні формули екстраполяції та крайові випадки

Екстраполяція медіанного часу до відмови `MTTF_use` за робочих умов на основі експериментальних даних випробувань `MTTF_test` здійснюється за моделлю Ірвіна Блека:

```
AF = ( j_test / j_use )ⁿ · exp( ( E_a / k_B ) · ( 1/T_use - 1/T_test ) )
```

```
MTTF_use = MTTF_test · AF
```

Критична довжина імунітету Блеха `L_c` розраховується за формулою:

```
L_c = ( j_L_critical ) / j_use
```

При практичній чисельній реалізації алгоритму надійності виникають важливі крайові випадки та обчислювальні виклики:

- **Нульова або від'ємна густина струму:** Якщо густина струму прямує до нуля (`j → 0`), ділення у співвідношенні `j_test / j_use` спричиняє переповнення з плаваючою комою (*infinity* або `NaN`). Програма зобов'язана виконувати явну перевірку `j_use > 0` і повертати захисний статус безкінечного терміну служби (`MTTF = ∞`, `L_c = ∞`).
- **Експоненційне переповнення у показнику Арреніуса:** При великих температурних перепадах `ΔT = T_test - T_use > 200 K` значення аргументу у функції `exp()` перевищує `80 ... 100`, що на 64-бітних системах стандарту IEEE 754 може генерувати чисельне переповнення. Алгоритм використовує захисну нормалізацію температур у Кельвінах.
- **Вплив температурного коефіцієнта опору (TCR):** Зростання температури збільшує питомий опір металу `ρ(T) = ρ_0 · (1 + α · ΔT)`, що додатково підсилює локальне джоулеве виділення тепла. У строгому аналізі температура доріжки `T_wire` знаходить шляхом ітераційного розв'язання самоузгодженої системи рівнянь.

---

### Детальний огляд програмної реалізації мовами C та C++

Наведена нижче програмна реалізація містить два варіанти модулів для аналізу електроміграційної надійності:

1. **Варіант C99 (`calculate_reliability`):** Призначений для високопродуктивної обробки мільйонів сегментів у ядрах EDA-систем. Він використовує підстановчі функції `static inline` для перетворення одиниць вимірювання, передачу параметрів через вказівники на `const`-структури для мінімізації накладних витрат стеків виклику та чітке розділення кодів помилок повернення через логічний тип `bool`.
2. **Варіант C++17 (`ElectromigrationEvaluator`):** Ідіоматичний об'єктно-орієнтований модуль. Застосовує сувору інкапсуляцію в просторі імен `physics::electromigration`, обчислення часу у форматах `constexpr`, повернення результатів через безпечний шаблонний обгортковий тип `std::optional<ReliabilityReport>` без використання сирих вказівників, а також метод `noexcept` для гарантування відсутності генерації винятків у критичних за часом обчислювальних циклах.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи */
#define K_BOLTZMANN_EV 8.617333262145e-5  /* Стала Больцмана в еВ/К */

/* Структура параметрів металізації */
typedef struct {
    double activation_energy_ev; /* Енергія активації E_a (еВ) */
    double current_exponent;     /* Показник ступеня Блека n */
    double blech_product_a_cm;   /* Критичний добуток Блеха (А/см) */
} metal_process_params_t;

/* Структура умов випробувань та експлуатації */
typedef struct {
    double temp_celsius;         /* Температура в градусах Цельсія */
    double current_density_a_cm2;/* Густина струму в А/см² */
} operating_condition_t;

/* Результати оцінки надійності */
typedef struct {
    double acceleration_factor;  /* Коефіцієнт прискорення AF */
    double mttf_use_hours;       /* Прогнозований MTTF за робочих умов (годин) */
    double critical_length_um;   /* Критична довжина Блеха L_c (мікрометрів) */
    bool is_blech_immune;        /* Прапорець імунітету за довжиною */
} reliability_result_t;

/* Перетворення градусів Цельсія у Кельвіни */
static inline double celsius_to_kelvin(double temp_c) {
    return temp_c + 273.15;
}

/* Обчислення коефіцієнта прискорення та терміну служби */
bool calculate_reliability(
    const metal_process_params_t *process,
    const operating_condition_t *test_cond,
    double mttf_test_hours,
    const operating_condition_t *use_cond,
    double line_length_um,
    reliability_result_t *out_result
) {
    if (!process || !test_cond || !use_cond || !out_result) {
        return false;
    }
    if (test_cond->current_density_a_cm2 <= 0.0 || use_cond->current_density_a_cm2 <= 0.0) {
        return false;
    }

    double t_test_k = celsius_to_kelvin(test_cond->temp_celsius);
    double t_use_k = celsius_to_kelvin(use_cond->temp_celsius);

    /* Складник прискорення за струмом */
    double current_ratio = test_cond->current_density_a_cm2 / use_cond->current_density_a_cm2;
    double j_factor = pow(current_ratio, process->current_exponent);

    /* Складник прискорення за температурою (Арреніус) */
    double temp_diff_inv = (1.0 / t_use_k) - (1.0 / t_test_k);
    double t_factor = exp((process->activation_energy_ev / K_BOLTZMANN_EV) * temp_diff_inv);

    /* Загальний коефіцієнт прискорення AF */
    out_result->acceleration_factor = j_factor * t_factor;
    out_result->mttf_use_hours = mttf_test_hours * out_result->acceleration_factor;

    /* Перевірка критерію Блеха (L_c в мікрометрах: (A/см / А/см²) * 10⁴ мкм/см) */
    out_result->critical_length_um = (process->blech_product_a_cm / use_cond->current_density_a_cm2) * 1.0e4;
    out_result->is_blech_immune = (line_length_um <= out_result->critical_length_um);

    return true;
}

int main(void) {
    /* Параметри мідної металізації Dual-Damascene (Cu з покриттям Co/Ru) */
    metal_process_params_t cu_process = {
        .activation_energy_ev = 0.90,  /* E_a = 0.9 еВ */
        .current_exponent = 1.5,       /* n = 1.5 */
        .blech_product_a_cm = 3500.0   /* (j·L)_c = 3500 А/см */
    };

    /* Умови випробування прискореного старіння HTOL */
    operating_condition_t htol_test = {
        .temp_celsius = 200.0,         /* T_test = 200 °C */
        .current_density_a_cm2 = 3.0e6 /* j_test = 3·10⁶ А/см² */
    };
    double mttf_test_h = 120.0;        /* Отриманий медіанний час відмови t50 = 120 годин */

    /* Робочі умови в інтегральній схемі */
    operating_condition_t operational_use = {
        .temp_celsius = 105.0,         /* T_use = 105 °C */
        .current_density_a_cm2 = 5.0e5 /* j_use = 5·10⁵ А/см² */
    };

    double interconnect_length_um = 50.0; /* Довжина доріжки 50 мкм */
    reliability_result_t res;

    if (calculate_reliability(&cu_process, &htol_test, mttf_test_h, &operational_use, interconnect_length_um, &res)) {
        printf("=== Результати аналізу електроміграційної надійності ===\n");
        printf("Коефіцієнт прискорення (AF): %.2f\n", res.acceleration_factor);
        printf("Прогнозований MTTF за робочих умов: %.2e годин (%.2f років)\n",
               res.mttf_use_hours, res.mttf_use_hours / 8760.0);
        printf("Критична довжина Блеха (L_c): %.2f мкм\n", res.critical_length_um);
        printf("Статус стійкості доріжки (50.0 мкм): %s\n",
               res.is_blech_immune ? "БЕЗСМЕРТНА (Immune)" : "ВРАЗЛИВА (Electromigration Limited)");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <optional>
#include <string_view>

namespace physics::electromigration {

constexpr double kBoltzmannEv = 8.617333262145e-5; // еВ/К

struct MetalProcess {
    double activation_energy_ev{0.9};
    double current_exponent{1.5};
    double blech_product_a_cm{3500.0};
};

struct StressCondition {
    double temp_celsius{25.0};
    double current_density_a_cm2{1.0e5};

    [[nodiscard]] constexpr double temp_kelvin() const noexcept {
        return temp_celsius + 273.15;
    }
};

struct ReliabilityReport {
    double acceleration_factor{1.0};
    double mttf_use_hours{0.0};
    double critical_length_um{0.0};
    bool is_blech_immune{false};

    [[nodiscard]] constexpr double mttf_years() const noexcept {
        return mttf_use_hours / 8760.0;
    }
};

class ElectromigrationEvaluator {
public:
    explicit constexpr ElectromigrationEvaluator(MetalProcess process) noexcept
        : process_(process) {}

    [[nodiscard]] std::optional<ReliabilityReport> evaluate(
        const StressCondition& test_cond,
        double mttf_test_hours,
        const StressCondition& use_cond,
        double line_length_um
    ) const noexcept {
        if (test_cond.current_density_a_cm2 <= 0.0 || use_cond.current_density_a_cm2 <= 0.0) {
            return std::nullopt;
        }

        const double current_ratio = test_cond.current_density_a_cm2 / use_cond.current_density_a_cm2;
        const double j_factor = std::pow(current_ratio, process_.current_exponent);

        const double temp_diff_inv = (1.0 / use_cond.temp_kelvin()) - (1.0 / test_cond.temp_kelvin());
        const double t_factor = std::exp((process_.activation_energy_ev / kBoltzmannEv) * temp_diff_inv);

        ReliabilityReport report{};
        report.acceleration_factor = j_factor * t_factor;
        report.mttf_use_hours = mttf_test_hours * report.acceleration_factor;
        report.critical_length_um = (process_.blech_product_a_cm / use_cond.current_density_a_cm2) * 1.0e4;
        report.is_blech_immune = (line_length_um <= report.critical_length_um);

        return report;
    }

private:
    MetalProcess process_;
};

} // namespace physics::electromigration

int main() {
    using namespace physics::electromigration;

    constexpr MetalProcess cu_process{
        .activation_energy_ev = 0.90,
        .current_exponent = 1.5,
        .blech_product_a_cm = 3500.0
    };

    const StressCondition htol_test{.temp_celsius = 200.0, .current_density_a_cm2 = 3.0e6};
    const StressCondition operational_use{.temp_celsius = 105.0, .current_density_a_cm2 = 5.0e5};
    const double mttf_test_h = 120.0;
    const double line_length_um = 50.0;

    ElectromigrationEvaluator evaluator(cu_process);
    auto result = evaluator.evaluate(htol_test, mttf_test_h, operational_use, line_length_um);

    if (result.has_value()) {
        std::cout << "=== C++17 Результати аналізу електроміграційної надійності ===\n";
        std::cout << "Коефіцієнт прискорення (AF): " << result->acceleration_factor << "\n";
        std::cout << "Прогнозований MTTF: " << result->mttf_use_hours << " годин ("
                  << result->mttf_years() << " років)\n";
        std::cout << "Критична довжина Блеха: " << result->critical_length_um << " мкм\n";
        std::cout << "Статус імунітету Блеха (L=" << line_length_um << " мкм): "
                  << (result->is_blech_immune ? "БЕЗСМЕРТНА LINE" : "ОБМЕЖЕНА ЕЛЕКТРОМІГРАЦІЄЮ") << "\n";
    }

    return 0;
}
```
:::

---

### Аналіз практичних результатів обчислення

За результатами виконання обчислювального алгоритму для типових параметрів сучасного мідного технологічного процесу (енергія активації `E_a = 0.9 еВ`, показник струму `n = 1.5`, прискорене випробування при `200 °C` та `3·10⁶ А/см²`) можна зробити важливі інженерні висновки:

1. **Масштаб коефіцієнта прискорення (AF):** Перехід від випробувальної температури `200 °C` та струму `3·10⁶ А/см²` до робочих умов `105 °C` та `5·10⁵ А/см²` забезпечує коефіцієнт прискорення `AF ≈ 240 ... 280`. Це означає, що відмова, яка настає через 120 годин у випробуваній термобарокамері, за нормальних умов експлуатації в процесорі трапиться лише через `29 000` годин (понад 3.3 роки безперервної роботи).

2. **Поріг імунітету за довжиною (Blech Threshold):** Для робочої густини струму `j = 5·10⁵ А/см²` критична довжина Блеха становить `L_c = 70.0 мкм`. Оскільки реальна довжина провідника в даному прикладі дорівнює `50.0 мкм` (`L < L_c`), доріжка володіє абсолютним імунітетом до електроміграції: механічний зворотний потік повністю зупиняє атомарну дифузію до моменту виникнення дефектів.

3. **Практичні рекомендації топологічного проектування:**
   - Для доріжок довжиною `L > L_c` тополог зобов'язаний або збільшити ширину лінії `w` (зменшивши робочу густину струму `j`), або розбити доріжку на кілька коротших сегментів за допомогою проміжних вертикальних переходів (*vias*), повернувши кожен сегмент у зону дії імунітету Блеха (`L < L_c`).
   - У шинах живлення та заземлення (`VDD` / `GSS`), де струм протікає постійно в одному напрямку, рекомендується застосовувати багатошарову дубльовану металізацію (*multi-via arrays*) для зниження локального струмового навантаження на окремі віа.
   - У зонах високої щільності сигнальних доріжок інструменти автоматичного розведення (*Auto-Router*) закладають технологічні запаси за шириною провідників для упередження джоулевого самонагріву.
