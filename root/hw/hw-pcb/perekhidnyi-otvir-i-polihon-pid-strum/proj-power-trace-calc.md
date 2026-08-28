# ⚙️ Інженерний калькулятор силової міді та перехідних отворів

Проєктування силових шин живлення, полігонів та перехідних отворів вимагає точного розрахунку трьох взаємопов'язаних величин: мінімальної ширини мідної доріжки за стандартом IPC-2152 для заданого струму та перегріву, необхідної кількості паралельних перехідних отворів (via array) та сумарного падіння напруги з урахуванням теплового зростання опору міді.

Ручний розрахунок за номограмами стандартів забирає багато часу й часто призводить до грубих помилок при переведенні імперських одиниць (mils, oz/ft²) у метричні (мм, мкм). Наведений нижче програмний модуль реалізує повний математичний апарат IPC-2152, температурну корекцію питомого опору та розрахунок матриці перехідних отворів.

## 1. Алгоритм розрахунку силової шини

Програма послідовно виконує такі інженерні обчислення:

1. **Розрахунок площі поперечного перерізу міді за IPC-2152:**
   Емпірична степенева залежність стандарту зв'язує струм `I` (А), допустимий перегрів `ΔT` (°C) та площу перерізу `A` (mils²):
   ```
   I = k · ΔT^0.44 · A^0.725
   ```
   Звідси розрахункова площа перерізу провідника:
   ```
   A = (I / (k · ΔT^0.44))^(1 / 0.725)
   ```
   де коефіцієнт `k = 0.048` для відкритих зовнішніх шарів (Top / Bottom) та `k = 0.024` для ізольованих внутрішніх шарів (Inner).

2. **Визначення геометричної ширини провідника:**
   Отримана площа `A` у квадратних мілах переводиться у квадратні міліметри (`A_mm2 = A_mils2 / 1550`). Потім ширина доріжки обчислюється діленням площі на номінальну товщину мідної фольги: `W = A_mm2 / t_foil`, де `t_foil = 0.0175 мм` (0.5 oz), `0.035 мм` (1 oz) або `0.070 мм` (2 oz).

3. **Температурна корекція провідності:**
   Усталена температура провідника під струмом становить `T_op = T_amb + ΔT`. Опір міді перераховується з урахуванням температурного коефіцієнта `α = 0.00393 1/°C`:
   ```
   ρ(T_op) = ρ₂₀ · (1 + α · (T_op - 20°C))
   ```

4. **Розрахунок матриці перехідних отворів (Stitching Vias):**
   За геометрією свердла `d_drill` та товщиною стінки осадженої міді `t_wall` обчислюється площа мідного кільця гільзи `A_via = π · t_wall · (d_drill - t_wall)`. Визначається опір одного via, а кількість отворів у матриці вибирається так, щоб струм через кожен отвір не перевищував безпечну межу (типово 1.5–2.0 А на один отвір діаметром 0.3 мм).

5. **Інтегральний аналіз втрат:**
   Обчислюється сумарне падіння напруги `ΔU_total = ΔU_trace + ΔU_vias` та загальна теплова потужність втрат `P_loss = I · ΔU_total`.

## 2. Реалізація калькулятора на C та C++

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Базові константи міді та діелектрика */
#define COPPER_RHO_20C_OHM_MM   1.72e-5  /* Питомий опір міді при 20 °C (Ом·мм) */
#define COPPER_TCR_PER_C        0.00393  /* Температурний коефіцієнт опору (1/°C) */
#define MILS_PER_MM             39.3701  /* Коефіцієнт переведення мм у mils */

/* Товщина мідної фольги у міліметрах за вагою в унціях (oz) */
#define FOIL_THICKNESS_0_5_OZ   0.0175   /* 0.5 oz ≈ 17.5 мкм */
#define FOIL_THICKNESS_1_0_OZ   0.0350   /* 1.0 oz ≈ 35.0 мкм */
#define FOIL_THICKNESS_2_0_OZ   0.0700   /* 2.0 oz ≈ 70.0 мкм */

typedef enum {
    LAYER_EXTERNAL = 0,  /* Зовнішній шар (Top / Bottom) */
    LAYER_INTERNAL = 1   /* Внутрішній шар (Inner 1 / Inner 2) */
} pcb_layer_type_t;

typedef struct {
    double current_amps;         /* Робочий постійний струм (А) */
    double temp_rise_c;          /* Допустимий перегрів Delta_T (°C) */
    double ambient_temp_c;       /* Температура довкілля (°C) */
    double copper_oz;            /* Вага міді (0.5, 1.0, 2.0 oz) */
    pcb_layer_type_t layer;      /* Тип шару */
    double trace_length_mm;      /* Довжина провідника (мм) */
} pcb_trace_params_t;

typedef struct {
    double drill_diam_mm;        /* Діаметр свердла via (мм) */
    double plating_thickness_mm; /* Товщина стінки металізації (мм, типово 0.025) */
    double board_thickness_mm;   /* Повна товщина плати (мм, типово 1.6) */
    double max_current_per_via;  /* Допустимий струм на 1 via (А, типово 1.5–2.0) */
} pcb_via_params_t;

typedef struct {
    double required_width_mm;    /* Розрахункова ширина доріжки (мм) */
    double required_width_mils;  /* Розрахункова ширина доріжки (mils) */
    double trace_resistance_ohm; /* Опір доріжки при робочій температурі (Ом) */
    double voltage_drop_trace_v; /* Падіння напруги на доріжці (В) */
    double power_loss_trace_w;   /* Втрати потужності на доріжці (Вт) */
    int    required_via_count;   /* Мінімальна кількість via у матриці */
    double via_array_res_ohm;    /* Сумарний опір матриці via (Ом) */
    double voltage_drop_vias_v;  /* Падіння напруги на матриці via (В) */
    double total_voltage_drop_v; /* Загальне падіння напруги (В) */
    double total_power_loss_w;   /* Загальні теплові втрати (Вт) */
} pcb_power_calc_result_t;

/* Розрахунок площі перерізу та ширини за формулами IPC-2152 */
bool calculate_pcb_power_rail(const pcb_trace_params_t* trace,
                              const pcb_via_params_t* via,
                              pcb_power_calc_result_t* result)
{
    if (!trace || !via || !result || trace->current_amps <= 0.0 || trace->temp_rise_c <= 0.0) {
        return false;
    }

    /* Коефіцієнти емпіричної моделі IPC-2152: I = k * (Delta_T)^b * (Area_mils2)^c */
    double k = (trace->layer == LAYER_EXTERNAL) ? 0.048 : 0.024;
    double b = 0.44;
    double c = 0.725;

    /* Площа поперечного перерізу в mils²: Area = (I / (k * Delta_T^b))^(1/c) */
    double area_mils2 = pow(trace->current_amps / (k * pow(trace->temp_rise_c, b)), 1.0 / c);
    double area_mm2 = area_mils2 / (MILS_PER_MM * MILS_PER_MM);

    /* Товщина міді у міліметрах */
    double thickness_mm = trace->copper_oz * FOIL_THICKNESS_1_0_OZ;
    result->required_width_mm = area_mm2 / thickness_mm;
    result->required_width_mils = result->required_width_mm * MILS_PER_MM;

    /* Робоча температура провідника */
    double operating_temp_c = trace->ambient_temp_c + trace->temp_rise_c;
    double temp_delta = operating_temp_c - 20.0;
    double rho_operating = COPPER_RHO_20C_OHM_MM * (1.0 + COPPER_TCR_PER_C * temp_delta);

    /* Електричний опір доріжки */
    result->trace_resistance_ohm = (rho_operating * trace->trace_length_mm) / area_mm2;
    result->voltage_drop_trace_v = trace->current_amps * result->trace_resistance_ohm;
    result->power_loss_trace_w = trace->current_amps * result->voltage_drop_trace_v;

    /* Розрахунок параметрів перехідного отвору */
    double d_drill = via->drill_diam_mm;
    double t_wall = via->plating_thickness_mm;
    double a_via_mm2 = 3.141592653589793 * t_wall * (d_drill - t_wall);

    /* Опір одиничного via при робочій температурі */
    double r_single_via = (rho_operating * via->board_thickness_mm) / a_via_mm2;

    /* Кількість via з урахуванням допустимого струму на один отвір */
    int n_vias = (int)ceil(trace->current_amps / via->max_current_per_via);
    if (n_vias < 1) n_vias = 1;
    result->required_via_count = n_vias;

    /* Паралельний опір матриці via */
    result->via_array_res_ohm = r_single_via / (double)n_vias;
    result->voltage_drop_vias_v = trace->current_amps * result->via_array_res_ohm;

    /* Загальні втрати на всій силовій ланці */
    result->total_voltage_drop_v = result->voltage_drop_trace_v + result->voltage_drop_vias_v;
    result->total_power_loss_w = result->power_loss_trace_w + (trace->current_amps * result->voltage_drop_vias_v);

    return true;
}

int main(void)
{
    pcb_trace_params_t trace = {
        .current_amps = 15.0,
        .temp_rise_c = 20.0,
        .ambient_temp_c = 25.0,
        .copper_oz = 1.0,
        .layer = LAYER_EXTERNAL,
        .trace_length_mm = 60.0
    };

    pcb_via_params_t via = {
        .drill_diam_mm = 0.3,
        .plating_thickness_mm = 0.025,
        .board_thickness_mm = 1.6,
        .max_current_per_via = 1.8
    };

    pcb_power_calc_result_t res;
    if (calculate_pcb_power_rail(&trace, &via, &res)) {
        printf("=== Результати розрахунку силової шини PCB ===\n");
        printf("Струм: %.1f А, Допустимий перегрів: %.1f °C (T_max = %.1f °C)\n",
               trace.current_amps, trace.temp_rise_c, trace.ambient_temp_c + trace.temp_rise_c);
        printf("Необхідна ширина доріжки: %.2f мм (%.1f mils)\n",
               res.required_width_mm, res.required_width_mils);
        printf("Опір доріжки (L = %.0f мм): %.3f мОм\n",
               trace.trace_length_mm, res.trace_resistance_ohm * 1000.0);
        printf("Падіння напруги на доріжці: %.2f мВ, втрати: %.3f Вт\n",
               res.voltage_drop_trace_v * 1000.0, res.power_loss_trace_w);
        printf("Матриця Stitching Vias: %d шт (R_array = %.3f мОм)\n",
               res.required_via_count, res.via_array_res_ohm * 1000.0);
        printf("Сумарне падіння напруги: %.2f мВ\n", res.total_voltage_drop_v * 1000.0);
        printf("Сумарна розсіювана потужність: %.3f Вт\n", res.total_power_loss_w);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <format>

namespace pcb::power {

// Базові фізичні константи
inline constexpr double copper_rho_20c_ohm_mm = 1.72e-5; // Ом·мм при 20 °C
inline constexpr double copper_tcr_per_c       = 0.00393; // 1/°C
inline constexpr double mils_per_mm            = 39.37007874;

enum class LayerType {
    External, // Зовнішній шар
    Internal  // Внутрішній шар
};

enum class CalcError {
    InvalidCurrent,
    InvalidTemperatureRise,
    InvalidGeometry
};

struct TraceParams {
    double current_a{1.0};
    double temp_rise_c{20.0};
    double ambient_temp_c{25.0};
    double copper_oz{1.0};       // 1 oz = 0.035 мм
    LayerType layer{LayerType::External};
    double length_mm{10.0};
};

struct ViaParams {
    double drill_diam_mm{0.3};
    double plating_thickness_mm{0.025};
    double board_thickness_mm{1.6};
    double max_current_per_via_a{1.8};
};

struct PowerRailAnalysis {
    double required_width_mm{};
    double required_width_mils{};
    double trace_resistance_ohm{};
    double voltage_drop_trace_v{};
    double power_loss_trace_w{};
    int    required_via_count{};
    double via_array_res_ohm{};
    double voltage_drop_vias_v{};
    double total_voltage_drop_v{};
    double total_power_loss_w{};
};

[[nodiscard]] constexpr auto calculate_power_rail(
    const TraceParams& trace,
    const ViaParams& via
) noexcept -> std::expected<PowerRailAnalysis, CalcError>
{
    if (trace.current_a <= 0.0) {
        return std::unexpected(CalcError::InvalidCurrent);
    }
    if (trace.temp_rise_c <= 0.0) {
        return std::unexpected(CalcError::InvalidTemperatureRise);
    }
    if (via.drill_diam_mm <= via.plating_thickness_mm * 2.0) {
        return std::unexpected(CalcError::InvalidGeometry);
    }

    // Коефіцієнти емпіричної моделі IPC-2152
    const double k = (trace.layer == LayerType::External) ? 0.048 : 0.024;
    constexpr double b = 0.44;
    constexpr double c = 0.725;

    // Площа перерізу за IPC-2152
    const double area_mils2 = std::pow(trace.current_a / (k * std::pow(trace.temp_rise_c, b)), 1.0 / c);
    const double area_mm2 = area_mils2 / (mils_per_mm * mils_per_mm);

    const double foil_thickness_mm = trace.copper_oz * 0.035;
    const double width_mm = area_mm2 / foil_thickness_mm;

    // Температурна корекція провідності міді
    const double operating_temp_c = trace.ambient_temp_c + trace.temp_rise_c;
    const double rho_operating = copper_rho_20c_ohm_mm * (1.0 + copper_tcr_per_c * (operating_temp_c - 20.0));

    // Опір та втрати на доріжці
    const double r_trace = (rho_operating * trace.length_mm) / area_mm2;
    const double v_drop_trace = trace.current_a * r_trace;
    const double p_loss_trace = trace.current_a * v_drop_trace;

    // Геометрія та опір перехідного отвору
    const double a_via_mm2 = std::numbers::pi * via.plating_thickness_mm * (via.drill_diam_mm - via.plating_thickness_mm);
    const double r_single_via = (rho_operating * via.board_thickness_mm) / a_via_mm2;

    const int n_vias = std::max(1, static_cast<int>(std::ceil(trace.current_a / via.max_current_per_via_a)));
    const double r_via_array = r_single_via / static_cast<double>(n_vias);
    const double v_drop_vias = trace.current_a * r_via_array;

    return PowerRailAnalysis{
        .required_width_mm = width_mm,
        .required_width_mils = width_mm * mils_per_mm,
        .trace_resistance_ohm = r_trace,
        .voltage_drop_trace_v = v_drop_trace,
        .power_loss_trace_w = p_loss_trace,
        .required_via_count = n_vias,
        .via_array_res_ohm = r_via_array,
        .voltage_drop_vias_v = v_drop_vias,
        .total_voltage_drop_v = v_drop_trace + v_drop_vias,
        .total_power_loss_w = p_loss_trace + (trace.current_a * v_drop_vias)
    };
}

} // namespace pcb::power

int main()
{
    using namespace pcb::power;

    const TraceParams trace_cfg{
        .current_a = 15.0,
        .temp_rise_c = 20.0,
        .ambient_temp_c = 25.0,
        .copper_oz = 1.0,
        .layer = LayerType::External,
        .length_mm = 60.0
    };

    const ViaParams via_cfg{
        .drill_diam_mm = 0.3,
        .plating_thickness_mm = 0.025,
        .board_thickness_mm = 1.6,
        .max_current_per_via_a = 1.8
    };

    const auto result = calculate_power_rail(trace_cfg, via_cfg);

    if (result) {
        const auto& r = *result;
        std::cout << "=== Результати розрахунку силової шини PCB (C++20) ===\n";
        std::cout << std::format("Струм: {:.1f} А, Перегрів: {:.1f} °C (T_max = {:.1f} °C)\n",
                                 trace_cfg.current_a, trace_cfg.temp_rise_c,
                                 trace_cfg.ambient_temp_c + trace_cfg.temp_rise_c);
        std::cout << std::format("Необхідна ширина доріжки: {:.2f} мм ({:.1f} mils)\n",
                                 r.required_width_mm, r.required_width_mils);
        std::cout << std::format("Опір доріжки (L = {:.0f} мм): {:.3f} мОм\n",
                                 trace_cfg.length_mm, r.trace_resistance_ohm * 1000.0);
        std::cout << std::format("Падіння напруги на доріжці: {:.2f} мВ, втрати: {:.3f} Вт\n",
                                 r.voltage_drop_trace_v * 1000.0, r.power_loss_trace_w);
        std::cout << std::format("Матриця Stitching Vias: {} шт (R_array = {:.3f} мОм)\n",
                                 r.required_via_count, r.via_array_res_ohm * 1000.0);
        std::cout << std::format("Сумарне падіння напруги: {:.2f} мВ\n",
                                 r.total_voltage_drop_v * 1000.0);
        std::cout << std::format("Сумарна розсіювана потужність: {:.3f} Вт\n",
                                 r.total_power_loss_w);
    } else {
        std::cerr << "Помилка розрахунку параметрів силової шини!\n";
    }

    return 0;
}
```
:::

## 3. Інженерний аналіз крайових випадків та практичні пастки

Під час практичного використання калькулятора слід враховувати кілька технологічних та фізичних обмежень реального виробництва плат:

1. **Імпульсні режими та адіабатичний нагрів:**
   Стандарт IPC-2152 та наведений калькулятор розраховують **усталений тепловий режим** (постійний постійний струм або діюче RMS-значення змінного струму тривалістю понад кілька секунд). Якщо лінія проводить короткі поодинокі імпульси великого струму (наприклад, пусковий струм мотора 80 А тривалістю 10 мс чи імпульс розряду конденсатора), тепло не встигає вийти за межі міді у склотекстоліт. У такому режимі нагрів є чисто **адіабатичним**:
   ```
   ΔT ≈ (I² · t) / (C_v · A² · t_foil²)
   ```
   де `C_v ≈ 3.45 Дж/(см³·°C)` — об'ємна теплоємність міді. У короткоімпульсному режимі вирішальним параметром є сумарна інтегральна теплова енергія Джоуля `I²·t`, а не тривала конвективна тепловіддача.

2. **Гальванічний допуск товщини міді (Plating Tolerance):**
   При замовленні плати з фольгою 1 oz реальна товщина зовнішнього шару після травлення й нарощування становить близько 45–55 мкм, а внутрішнього — 30–35 мкм. Калькулятор свідомо використовує номінальну базову товщину (35 мкм), що дає природний коефіцієнт інженерного запасу близько 1.25–1.30.

3. **Корекція на суцільні площини (Thermal Planes):**
   Якщо внутрішній силовий шар лежить на відстані 0.1 мм від суцільного внутрішнього шару GND, реальний перегрів буде нижчим за розрахунковий на 40–50%. Це дозволяє в щільних багатошарових дизайнах використовувати коефіцієнт `k = 0.035–0.040` замість песимістичного `0.024`.

4. **Правило запасу перехідних отворів (N - 1):**
   У силових модулях живлення ніколи не залишайте розрахункову кількість via рівною строго `I_total / I_via_rated`. Завжди додавайте як мінімум один отвір у запас: якщо у процесі свердління або гальваніки один отвір матиме тонку стінку чи дефект адгезії, інші отвори матриці спокійно візьмуть струмовий надлишок на себе без аварійного перегріву.

5. **Практична верифікація: тепловізор та чотириточкове вимірювання:**
   Після виготовлення дослідного зразка силової плати інженерний розрахунок обов'язково перевіряють двома інструментальними методами:
   - **Чотирипровідне вимірювання Кельвіна (Kelvin 4-Wire Sensing):** Дозволяє виміряти реальний опір ділянки силової шини або матриці via з роздільною здатністю до десятих часток міліома, виключивши опір вимірювальних щупів і контактних переходів.
   - **Інфрачервона термографія (тепловізор):** Під час роботи плати під номінальним струмом тепловізор показує реальну карту розподілу температур. Локальні гарячі плями свідчать про наявність зон стягування струму (current crowding), недостатню кількість перехідних отворів або надмірне звуження міді термобар'єрами.

## 4. Порівняння результатів IPC-2152 та застарілого IPC-2221

Порівняння розрахунків за IPC-2152 та застарілим стандартом IPC-2221 виявляє суттєві розбіжності:
- **Зовнішні шари:** Старий стандарт IPC-2221 через спрощену теплову модель давав дещо завищену ширину для струмів до 5 А, але недооцінював нагрів при великих струмах (понад 15–20 А) через нехтування ростом опору міді від нагрівання. IPC-2152 дає більш збалансований переріз, що економить до 15–20% площі плати.
- **Внутрішні шари:** За IPC-2221 внутрішні доріжки вимагали рівно подвійної ширини порівняно із зовнішніми, незалежно від наявності суцільних шарів заземлення. У сучасних 4- та 6-шарових платах із тонкими діелектриками препрегів IPC-2152 дозволяє зменшити ширину внутрішніх шин майже на 30–40% за умови їхнього розміщення поруч із площинами заземлення, які працюють як високоефективні теплові розподільники.
