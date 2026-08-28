# ⚙️ Інженерний калькулятор падіння напруги в джгуті та зміщення потенціалу землі

Розробка бортового кабельного джгута вимагає суворого узгодження перерізів провідників (калібру AWG), довжин ліній, робочих температур та струмових навантажень. Помилка у виборі діаметра силового або сигнального проводу призводить не лише до неприпустимого падіння напруги на навантаженні, але й до небезпечного зміщення опорного потенціалу сигнальної землі, що руйнує логічні рівні цифрових шин і викликає збої авіоніки.

> 🔧 **Навіщо це.** Реальний мідний провідник має кінцевий питомий опір і нагрівається під час протікання струму за законом Джоуля — Ленца. Якщо відеопередавач VTX потужністю 1 Вт (струм споживання 2.0–2.5 А при напрузі 5 В) підключений через тонкий дріт AWG 28 завдовжки 40 см, опір петлі живлення становить понад 0.17 Ом. Це спричиняє падіння напруги на 0.43 В (понад 8.5% від номіналу) та піднімає потенціал «мінусового» контакту VTX відносно польотного контролера на 215 мВ. Для цифрової логіки 3.3V такий зсув з'їдає більше половини запасу завадостійкості шин UART/I2C, спричиняючи циклічні помилки передачі телеметрії, спотворення OSD та випадкові зависання мікроконтролера при перегазовках.

---

### Фізична модель провідника та температурна залежність

Калібр проводу за стандартом American Wire Gauge (AWG) визначає діаметр струмопровідної жили за логарифмічною прогресією. Базовий діаметр `d_n` для номера калібру `n` (від AWG 0000 до AWG 36) описується геометричним співвідношенням, де AWG 36 має діаметр 0.005 дюйма (0.127 мм), а AWG 0 — діаметр 0.3249 дюйма (8.251 мм):

```
d_n = 0.127 · 92^((36 − n) / 39)      [діаметр жили в міліметрах за стандартом AWG]
```

Площа поперечного перерізу струмопровідної жили `S` визначається через радіус:

```
S = π · (d_n / 2)²      [площа перерізу провідника]
```

Питомий електричний опір відпаленої міді високої чистоти при температурі `T₀ = 20°C` становить `ρ₂₀ = 1.724 · 10⁻⁸ Ом·м`. Під час роботи безпілотника всередині фюзеляжу або захисного кожуха температура кабельного пучка підвищується до `T = 45...70°C` через тепловиділення регуляторів ESC, відеопередавача та сонячний нагрів. Питомий опір міді зростає лінійно відповідно до температурного коефіцієнта опору `α = 0.00393 К⁻¹`:

```
ρ(T) = ρ₂₀ · (1 + α · (T − 20))      [температурна корекція питомого опору міді]
```

Опір прямого провідника довжиною `L` становить:

```
R_single = ρ(T) · L / S      [опір одного проводу в джгуті]
```

---

### Розрахунок втрат напруги та зміщення нуля землі

Повний опір замкненого кола живлення `R_loop` включає опір прямого проводу (шини живлення `+VCC`) та зворотного проводу (`GND`):

```
R_loop = 2 · R_single      [повний опір петлі живлення]
```

При протіканні постійного або середньоквадратичного струму навантаження `I_load` сумарне падіння напруги `ΔV_total` та розсіювана теплова потужність `P_loss` становлять:

```
ΔV_total = I_load · R_loop      [падіння напруги на навантаженні]
P_loss = I_load² · R_loop       [теплові втрати в проводах джгута]
```

Якщо зворотний провід `GND` використовується одночасно як силове повернення струму навантаження та як опорний нуль для сигнальних ліній, на зворотному проводі виникає падіння потенціалу `ΔV_gnd`:

```
ΔV_gnd = I_load · R_single      [зміщення нульового потенціалу сигнальної землі]
```

Для логічних інтерфейсів з рівнем живлення 3.3V (LVCMOS / LVTTL) граничні рівні напруги складають:
- Максимальна напруга логічного нуля на вході приймача: `V_IL_max = 0.8 В`.
- Максимальна вихідна напруга нуля передавача: `V_OL_max = 0.4 В`.

Статичний запас завадостійкості за рівнем логічного нуля становить `V_noise_margin = V_IL_max − V_OL_max = 0.4 В` (400 мВ). Якщо зміщення потенціалу землі `ΔV_gnd` перевищує 200 мВ, динамічний запас стійкості до високочастотних комутаційних шумів падає нижче допустимого порогу, що гарантовано викликає помилки зчитування байтів на шинах UART та хибні спрацьовування умов Start/Stop на шині I2C.

---

### Авіаційні коефіцієнти зниження навантаження та матеріали ізоляції

В авіаційних стандартах проектування кабельних мереж (таких як SAE AS50881 та MIL-W-5088L) струмові навантаження для окремих проводів не застосовуються безпосередньо до проводів у складі щільного пучка. Коли `N` струмопровідних жил упаковані всередину захисного обплетення «зміїна шкіра» або термозбіжної трубки, погіршуються умови конвективного тепловідведення в навколишнє повітря.

Для врахування групового нагріву застосовується емпіричний коефіцієнт зниження струму `k_bundle`:

```
k_bundle ≈ 1 / √N      [коефіцієнт зниження допустимого струму для пучка]
```

Для пучка з `N = 9` навантажених провідників допустимий тривалий струм кожного проводу зменшується в `√9 = 3 рази`. Якщо для одиночного силіконового проводу AWG 22 у вільному повітрі допустимий струм становить 5.0 А, то всередині щільного магістрального джгута його безпечне навантаження обмежується значенням `5.0 / 3 ≈ 1.67 А`.

Крім того, необхідно враховувати перехідний опір роз'ємів (англ. *contact resistance*). Компактні мікророз'єми типу JST-SH (крок 1.0 мм) або Molex PicoBlade (крок 1.25 мм), що повсюдно використовуються в польотних контролерах, мають номінальний опір пари контактів `R_contact ≈ 20...30 мОм`. Під дією тривалих вібрацій та окислення цей опір може зростати до 50–100 мОм на кожне з'єднання. При струмі 1.5 А падіння напруги на одному піні роз'єму становить додаткові `1.5 · 0.050 = 75 мВ`, що додається до втрат у самому кабелі.

При виборі типу проводу враховують властивості ізоляції:
- **Силіконова ізоляція (High-Strand Silicone).** Робоча температура від −60°C до +200°C, надзвичайно гнучка, але має збільшений зовнішній діаметр та низьку стійкість до механічного прорізання гострими кромками. Оптимальна для рухомих з'єднань і підвісів.
- **Фторопластова ізоляція ETFE / PTFE (Tefzel, MIL-W-22759).** Робоча температура до +150...+260°C, тонкостінна, надтверда та стійка до стирання. Зменшує вагу та діаметр джгута на 35–45% порівняно з силіконом, що робить її стандартом для магістральних трас у крилах та фюзеляжах БПЛА.

---

### Програмна реалізація аналізатора ліній

Наведена нижче модульна бібліотека реалізує повний аналітичний розрахунок параметрів лінії живлення, перевіряє допустиму густину струму `J = I / S` (яка не повинна перевищувати `10...15 А/мм²` для відкритої проводки та `5...8 А/мм²` для щільних закритих джгутів) та формує діагностичний звіт безпеки.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Базові фізичні константи міді */
#define COPPER_RHO_20C   1.724e-8  /* Питомий опір міді при 20°C, Ом·м */
#define COPPER_TEMP_COEF 0.00393   /* Температурний коефіцієнт опору, 1/°C */

typedef enum {
    AWG_10 = 10,
    AWG_12 = 12,
    AWG_14 = 14,
    AWG_16 = 16,
    AWG_18 = 18,
    AWG_20 = 20,
    AWG_22 = 22,
    AWG_24 = 24,
    AWG_26 = 26,
    AWG_28 = 28,
    AWG_30 = 30
} awg_gauge_t;

typedef struct {
    awg_gauge_t gauge;
    double length_m;        /* Довжина кабельної траси в один бік, метри */
    double current_amps;    /* Струм навантаження лінії, Ампери */
    double operating_temp_c;/* Очікувана температура джгута, °C */
    bool shared_ground;     /* Чи використовується зворотний провід як спільна земля */
    double bus_voltage_v;   /* Номінальна напруга живлення шини, Вольти */
} harness_spec_t;

typedef struct {
    double wire_area_mm2;       /* Площа поперечного перерізу, мм² */
    double single_wire_res_ohm; /* Опір одного провідника при робочій температурі, Ом */
    double loop_res_ohm;        /* Повний опір петлі живлення (+ та -), Ом */
    double total_voltage_drop_v;/* Сумарне падіння напруги на споживачі, В */
    double voltage_drop_percent;/* Падіння напруги у відсотках від номіналу шини */
    double ground_shift_v;      /* Зміщення потенціалу землі на боці приймача, В */
    double thermal_loss_w;      /* Потужність теплових втрат у джгуті, Вт */
    bool current_density_ok;    /* Перевірка допустимої густини струму (< 15 А/мм²) */
    bool logic_margin_ok;       /* Перевірка запасу завадостійкості (< 0.2 В для 3.3V) */
} harness_result_t;

/* Обчислення площі перерізу мідної жили за стандартом AWG */
static double calculate_awg_area(awg_gauge_t gauge) {
    /* Діаметр за формулою AWG: d_n = 0.127 мм · 92^((36-n)/39) */
    double diameter_mm = 0.127 * pow(92.0, (36.0 - (double)gauge) / 39.0);
    double radius_mm = diameter_mm / 2.0;
    return 3.141592653589793 * radius_mm * radius_mm;
}

bool evaluate_harness_link(const harness_spec_t *spec, harness_result_t *res) {
    if (!spec || !res || spec->length_m <= 0.0 || spec->current_amps < 0.0) {
        return false;
    }

    res->wire_area_mm2 = calculate_awg_area(spec->gauge);
    double area_m2 = res->wire_area_mm2 * 1.0e-6;

    /* Розрахунок питомого опору з урахуванням температури: ρ(T) = ρ₂₀ · (1 + α · (T - 20)) */
    double delta_t = spec->operating_temp_c - 20.0;
    double rho_t = COPPER_RHO_20C * (1.0 + COPPER_TEMP_COEF * delta_t);

    /* Опір одного провідника: R = ρ · L / S */
    res->single_wire_res_ohm = rho_t * spec->length_m / area_m2;
    res->loop_res_ohm = 2.0 * res->single_wire_res_ohm;

    /* Падіння напруги та втрати */
    res->total_voltage_drop_v = spec->current_amps * res->loop_res_ohm;
    res->voltage_drop_percent = (spec->bus_voltage_v > 0.0)
        ? (res->total_voltage_drop_v / spec->bus_voltage_v) * 100.0
        : 0.0;

    /* Зміщення потенціалу землі на кінці лінії: ΔV_gnd = I_return · R_single */
    res->ground_shift_v = spec->current_amps * res->single_wire_res_ohm;
    res->thermal_loss_w = spec->current_amps * spec->current_amps * res->loop_res_ohm;

    /* Інженерні критерії: густина струму J ≤ 15 А/мм² для відкритого джгута */
    double current_density = spec->current_amps / res->wire_area_mm2;
    res->current_density_ok = (current_density <= 15.0);

    /* Запас завадостійкості: для 3.3V CMOS зсув землі понад 200 мВ неприпустимий */
    res->logic_margin_ok = (!spec->shared_ground) || (res->ground_shift_v < 0.200);

    return true;
}

void print_harness_report(const harness_spec_t *spec, const harness_result_t *res) {
    printf("=== ЗВІТ РОЗРАХУНКУ БОРТОВОЇ ЛІНІЇ (AWG %d, L=%.2f м, I=%.2f А) ===\n",
           spec->gauge, spec->length_m, spec->current_amps);
    printf("Переріз провідника:      %.4f мм²\n", res->wire_area_mm2);
    printf("Опір петлі (+ / -):      %.4f Ом\n", res->loop_res_ohm);
    printf("Падіння напруги на лінії: %.3f В (%.2f %% від %.1f В)\n",
           res->total_voltage_drop_v, res->voltage_drop_percent, spec->bus_voltage_v);
    printf("Зміщення потенціалу GND: %.3f В (%.1f мВ)\n",
           res->ground_shift_v, res->ground_shift_v * 1000.0);
    printf("Теплове розсіювання:     %.3f Вт\n", res->thermal_loss_w);
    printf("Статус густини струму:   %s\n", res->current_density_ok ? "НОРМА" : "ПЕРЕГРІВ (>15 А/мм²)");
    printf("Статус земляного зсуву:  %s\n", res->logic_margin_ok ? "БЕЗПЕЧНО" : "КРИТИЧНИЙ ЗСУВ ЗЕМЛІ!");
}
```
```cpp
#include <iostream>
#include <format>
#include <numbers>
#include <cmath>
#include <expected>
#include <string_view>

namespace avionics::wiring {

enum class AwgGauge : int {
    Awg10 = 10, Awg12 = 12, Awg14 = 14, Awg16 = 16,
    Awg18 = 18, Awg20 = 20, Awg22 = 22, Awg24 = 24,
    Awg26 = 26, Awg28 = 28, Awg30 = 30
};

struct HarnessSpec {
    AwgGauge gauge{AwgGauge::Awg22};
    double length_m{0.30};
    double current_amps{2.5};
    double operating_temp_c{45.0};
    bool shared_ground{true};
    double bus_voltage_v{5.0};
};

struct HarnessAnalysis {
    double wire_area_mm2{0.0};
    double loop_res_ohm{0.0};
    double single_res_ohm{0.0};
    double total_voltage_drop_v{0.0};
    double voltage_drop_pct{0.0};
    double ground_shift_v{0.0};
    double thermal_power_w{0.0};
    bool is_thermal_safe{false};
    bool is_ground_shift_safe{false};
};

enum class AnalysisError {
    InvalidLength,
    InvalidCurrent,
    ZeroVoltage
};

class HarnessCalculator {
public:
    static constexpr double CopperRho20C = 1.724e-8;   // Ом·м
    static constexpr double TempCoeff = 0.00393;        // 1/°C
    static constexpr double MaxCurrentDensity = 15.0;   // А/мм²
    static constexpr double MaxGndShiftVoltage = 0.200; // 200 мВ для 3.3V логіки

    [[nodiscard]] static constexpr double calculate_cross_section(AwgGauge gauge) noexcept {
        const double n = static_cast<double>(gauge);
        const double diameter_mm = 0.127 * std::pow(92.0, (36.0 - n) / 39.0);
        const double radius_mm = diameter_mm / 2.0;
        return std::numbers::pi * radius_mm * radius_mm;
    }

    [[nodiscard]] static std::expected<HarnessAnalysis, AnalysisError>
    analyze(const HarnessSpec& spec) noexcept {
        if (spec.length_m <= 0.0) {
            return std::unexpected(AnalysisError::InvalidLength);
        }
        if (spec.current_amps < 0.0) {
            return std::unexpected(AnalysisError::InvalidCurrent);
        }

        HarnessAnalysis result{};
        result.wire_area_mm2 = calculate_cross_section(spec.gauge);
        const double area_m2 = result.wire_area_mm2 * 1.0e-6;

        const double delta_t = spec.operating_temp_c - 20.0;
        const double rho_t = CopperRho20C * (1.0 + TempCoeff * delta_t);

        result.single_res_ohm = rho_t * spec.length_m / area_m2;
        result.loop_res_ohm = 2.0 * result.single_res_ohm;

        result.total_voltage_drop_v = spec.current_amps * result.loop_res_ohm;
        result.voltage_drop_pct = (spec.bus_voltage_v > 0.0)
            ? (result.total_voltage_drop_v / spec.bus_voltage_v) * 100.0
            : 0.0;

        result.ground_shift_v = spec.current_amps * result.single_res_ohm;
        result.thermal_power_w = spec.current_amps * spec.current_amps * result.loop_res_ohm;

        const double density = spec.current_amps / result.wire_area_mm2;
        result.is_thermal_safe = (density <= MaxCurrentDensity);
        result.is_ground_shift_safe = (!spec.shared_ground) || (result.ground_shift_v < MaxGndShiftVoltage);

        return result;
    }
};

} // namespace avionics::wiring
```
:::
