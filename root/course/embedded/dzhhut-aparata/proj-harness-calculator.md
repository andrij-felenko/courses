# ⚙️ Калькулятор джгута: розрахунок падіння напруги, перекосу земель та делейтингу

Цей практичний проект надає консольну інженерну утиліту мовами C та C++, яка виконує комплексний розрахунок параметрів міжплатного кабельного джгута: опір жил з урахуванням робочої температури, сумарне падіння напруги в колі живлення, динамічний перекіс потенціалів землі (Ground Shift) відносно запасу завадостійкості логічних рівнів інтерфейсів (3.3 В / 5 В / 1.8 В), тепловий делейтинг у щільному пучку провідників та обмеження радіусів вигину.

---

### Математична модель та фізичні передумови

Проектування кабельного джгута у вбудованих апаратах вимагає одночасного врахування електричних, теплових та механічних обмежень. Ігнорування хоча б одного з цих факторів призводить до прихованих відмов у польових умовах: перегріву ізоляції під навантаженням, раптового перезапуску мікроконтролерів або руйнування інтерфейсів зв'язку через блукаючі струми.

#### 1. Опір провідника та температурний коефіцієнт

Питомий опір електротехнічної міді за стандартом IACS (*International Annealed Copper Standard*) при 20 °C становить `ρ_20 = 1.724·10⁻⁸ Ом·м`. Опір відрізка провідника довжиною `L` з площею поперечного перерізу `A` визначається формулою:

```
R_20 = ρ_20 · (L / A)
```

При роботі пристрою температура всередині корпусу зростає за рахунок розсіювання тепла процесором, силовими транзисторами та самими проводами. Опір металів зростає лінійно зі збільшенням температури через інтенсифікацію теплових коливань кристалічної ґратки:

```
R_T = R_20 · (1 + α · (T_ambient - 20))
```

де `α = 0.00393 K⁻¹` — температурний коефіцієнт опору для міді. Наприклад, при нагріванні джгута до 70 °C опір кожної жили зростає на 19.65%, що пропорційно збільшує падіння напруги під навантаженням.

#### 2. Падіння напруги та перехідний опір контактів

Повне коло живлення складається з прямого провідника `+V`, зворотного провідника `GND` та щонайменше двох роз'ємних контактних пар. Сумарне падіння напруги в петлі:

```
ΔV_loop = I_load · (R_wire_pos + R_wire_gnd) + 2 · I_load · R_contact
```

де `R_contact` — перехідний опір пари штир-гніздо (зазвичай 5–15 мОм для нових роз'ємів Molex Micro-Fit або JST XH, але цей опір може зростати до 50–100 мОм при окисненні або послабленні пружини гнізда).

#### 3. Перекіс потенціалу землі (Ground Shift) та запас завадостійкості

Коли віддалений модуль споживає струм `I_load`, зворотний струм повертається на головну плату крізь опір земляної жили та земляного контакту роз'єму. Це створює зміщення локального потенціалу землі віддаленого вузла:

```
V_gnd_local = I_load · (R_wire_gnd + R_contact)
```

Сигнал передавача `Tx` віддаленої плати формується відносно `V_gnd_local`. Якщо драйвер видає логічний нуль напругою `V_OL`, приймач головної плати бачить абсолютний потенціал:

```
V_in_actual = V_OL + V_gnd_local
```

Для надійної роботи цифрового інтерфейсу напруга `V_in_actual` повинна залишатися нижче максимального порога розпізнавання логічного нуля приймача `V_IL_max` із запасом завадостійкості (*Noise Margin*):

```
Margin_noise = V_IL_max - V_in_actual
```

Якщо `Margin_noise < 0.15 В`, будь-яка високочастотна завада або комутаційний сплеск призведе до хибного зчитування одиниці замість нуля, викликаючи збій кадрування UART або втрату біта ACK на шині I2C.

#### 4. Тепловий делейтинг у щільному пучку проводів

Коли кілька навантажених струмом провідників зібрані в щільний джгут під захисним рукавом або гофрою, внутрішні жили позбавлені прямого конвективного охолодження повітрям. Їхнє тепло накопичується всередині пучка, підвищуючи локальну температуру ізоляції.

Згідно з військовим стандартом проектування бортових кабельних мереж MIL-W-5088L (SAE AS50881), допустимий струм кожного провідника у пучку зменшується на поправочний коефіцієнт делейтингу `K_bundle`:

```
K_bundle = 1.0 / sqrt(N_loaded)    (при N_loaded ≥ 3, з нижнім порогом 0.40)
```

Для одиночного проводу `K = 1.0`; для пари проводів `K = 0.88`; для джгута з 9 навантажених жил `K = 1 / sqrt(9) = 0.33` (обмежується безпечним мінімумом 0.40). Це означає, що дріт, який на відкритому повітрі несе 5 А, у складі джгута безпечно навантажувати лише струмом до 2 А.

#### 5. Механічні обмеження: мінімальний радіус вигину

При згинанні джгута на зовнішній стороні вигину виникають розтягуючі напруження, а на внутрішній — стискаючі. Щоб уникнути пластичної деформації мідних жил, перетирання ізоляції та розриву ниток екрана, радіус вигину нормується відносно зовнішнього діаметра джгута `D`:

```
R_bend_static = 6 · D     (для нерухомого монтажу всередині шасі)
R_bend_dynamic = 12 · D   (для рухомих шарнірів, маніпуляторів, підвісів)
```

---

### Програмна реалізація інженерного калькулятора

Нижче наведено вихідний код утиліти двома мовами: чистому стандартному C (C99) та сучасному ідіоматичному C++ (C++20/C++23) з використанням `std::expected`, просторів імен та строгої типізації.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define COPPER_RHO_20 1.724e-8  /* Питомий опір міді за 20 °C, Ом * м */
#define COPPER_ALPHA  0.00393   /* Температурний коефіцієнт опору, 1 / K */

typedef struct {
    double awg;
    double cross_section_mm2;
    double length_m;
    double current_a;
    double ambient_temp_c;
    double contact_resistance_mohm;
    int    loaded_wires_count;
    double logic_v_il_max;      /* Максимальний поріг логічного нуля приймача (V) */
    double logic_v_ol_max;      /* Максимальний вихідний нуль передавача (V) */
    double harness_outer_dia_mm;
} HarnessSpec;

typedef struct {
    double wire_resistance_ohm;
    double total_loop_drop_v;
    double ground_shift_v;
    double actual_v_il_at_receiver;
    double noise_margin_v;
    bool   logic_level_safe;
    double bundle_derating_factor;
    double min_bend_radius_static_mm;
    double min_bend_radius_dynamic_mm;
} HarnessResult;

bool calculate_harness(const HarnessSpec *spec, HarnessResult *res) {
    if (!spec || !res || spec->cross_section_mm2 <= 0.0 || spec->length_m <= 0.0) {
        return false;
    }

    double area_m2 = spec->cross_section_mm2 * 1e-6;
    double r_20 = (COPPER_RHO_20 * spec->length_m) / area_m2;
    double delta_t = spec->ambient_temp_c - 20.0;
    double r_wire = r_20 * (1.0 + COPPER_ALPHA * delta_t);
    double r_contact = (spec->contact_resistance_mohm * 1e-3);

    res->wire_resistance_ohm = r_wire;

    /* Повне падіння: 2 жили (плюс і земля) + 2 контакти роз'ємів */
    res->total_loop_drop_v = spec->current_a * (2.0 * r_wire + 2.0 * r_contact);

    /* Зсув землі на віддаленому вузлі: падіння на зворотній жилі та контакті */
    res->ground_shift_v = spec->current_a * (r_wire + r_contact);

    /* Рівень нуля на вході головного приймача */
    res->actual_v_il_at_receiver = spec->logic_v_ol_max + res->ground_shift_v;
    res->noise_margin_v = spec->logic_v_il_max - res->actual_v_il_at_receiver;
    res->logic_level_safe = (res->noise_margin_v >= 0.15); /* Запас не менше 150 мВ */

    /* Делейтинг у пучку за MIL-W-5088L */
    if (spec->loaded_wires_count <= 1) {
        res->bundle_derating_factor = 1.0;
    } else if (spec->loaded_wires_count == 2) {
        res->bundle_derating_factor = 0.88;
    } else {
        double k = 1.0 / sqrt((double)spec->loaded_wires_count);
        res->bundle_derating_factor = (k < 0.40) ? 0.40 : k;
    }

    /* Радіуси вигину */
    res->min_bend_radius_static_mm = 6.0 * spec->harness_outer_dia_mm;
    res->min_bend_radius_dynamic_mm = 12.0 * spec->harness_outer_dia_mm;

    return true;
}

int main(void) {
    HarnessSpec spec = {
        .awg = 24.0,
        .cross_section_mm2 = 0.205,      /* 24 AWG */
        .length_m = 1.8,                 /* 1.8 метра */
        .current_a = 1.5,                /* 1.5 А піковий струм вузла */
        .ambient_temp_c = 50.0,          /* Температура всередині корпусу */
        .contact_resistance_mohm = 15.0, /* 2 контакти Micro-Fit */
        .loaded_wires_count = 6,         /* 6 навантажених жил у пучку */
        .logic_v_il_max = 0.80,          /* Поріг логічного нуля 3.3V CMOS */
        .logic_v_ol_max = 0.20,          /* Вихідний нуль передавача */
        .harness_outer_dia_mm = 7.5      /* Зовнішній діаметр джгута */
    };

    HarnessResult res;
    if (!calculate_harness(&spec, &res)) {
        fprintf(stderr, "Помилка вхідних параметрів джгута.\n");
        return EXIT_FAILURE;
    }

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ КАБЕЛЬНОГО ДЖГУТА (C) ===\n");
    printf("Опір однієї жили за %0.1f °C:   %0.4f Ом\n", spec.ambient_temp_c, res.wire_resistance_ohm);
    printf("Сумарне падіння в петлі (±V):   %0.3f В\n", res.total_loop_drop_v);
    printf("Перекіс потенціалу землі (GND):  %0.3f В\n", res.ground_shift_v);
    printf("Рівень логічного нуля на вході: %0.3f В (поріг: %0.2f В)\n",
           res.actual_v_il_at_receiver, spec.logic_v_il_max);
    printf("Запас завадостійкості:           %0.3f В [%s]\n",
           res.noise_margin_v, res.logic_level_safe ? "БЕЗПЕЧНО" : "НЕБЕЗПЕЧНИЙ ЗБІЙ");
    printf("Коефіцієнт струму в пучку (K):   %0.2f (струм зменшити до %0.1f%%)\n",
           res.bundle_derating_factor, res.bundle_derating_factor * 100.0);
    printf("Мін. радіус вигину (статика):    %0.1f мм\n", res.min_bend_radius_static_mm);
    printf("Мін. радіус вигину (динаміка):   %0.1f мм\n", res.min_bend_radius_dynamic_mm);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <expected>
#include <string_view>

namespace harness {

constexpr double CopperRho20 = 1.724e-8; // Питомий опір міді за 20 °C, Ом * м
constexpr double CopperAlpha = 0.00393;  // Температурний коефіцієнт, 1 / K

enum class CalcError {
    InvalidCrossSection,
    InvalidLength,
    InvalidCurrent
};

struct Spec {
    double awg{24.0};
    double crossSectionMm2{0.205};     // 24 AWG
    double lengthM{1.8};               // 1.8 м
    double currentA{1.5};              // 1.5 А
    double ambientTempC{50.0};         // 50 °C
    double contactResistanceMohm{15.0};// 15 мОм
    int    loadedWiresCount{6};
    double logicVIlMax{0.80};          // 3.3V CMOS V_IL max
    double logicVOlMax{0.20};          // 3.3V CMOS V_OL max
    double outerDiameterMm{7.5};
};

struct Result {
    double wireResistanceOhm{0.0};
    double totalLoopDropV{0.0};
    double groundShiftV{0.0};
    double actualVIlAtReceiver{0.0};
    double noiseMarginV{0.0};
    bool   isLogicSafe{false};
    double bundleDeratingFactor{1.0};
    double minBendRadiusStaticMm{0.0};
    double minBendRadiusDynamicMm{0.0};
};

[[nodiscard]] constexpr std::expected<Result, CalcError> evaluate(const Spec& spec) noexcept {
    if (spec.crossSectionMm2 <= 0.0) {
        return std::unexpected(CalcError::InvalidCrossSection);
    }
    if (spec.lengthM <= 0.0) {
        return std::unexpected(CalcError::InvalidLength);
    }
    if (spec.currentA < 0.0) {
        return std::unexpected(CalcError::InvalidCurrent);
    }

    const double areaM2 = spec.crossSectionMm2 * 1e-6;
    const double r20 = (CopperRho20 * spec.lengthM) / areaM2;
    const double deltaT = spec.ambientTempC - 20.0;
    const double rWire = r20 * (1.0 + CopperAlpha * deltaT);
    const double rContact = spec.contactResistanceMohm * 1e-3;

    Result res{};
    res.wireResistanceOhm = rWire;
    res.totalLoopDropV = spec.currentA * (2.0 * rWire + 2.0 * rContact);
    res.groundShiftV = spec.currentA * (rWire + rContact);

    res.actualVIlAtReceiver = spec.logicVOlMax + res.groundShiftV;
    res.noiseMarginV = spec.logicVIlMax - res.actualVIlAtReceiver;
    res.isLogicSafe = (res.noiseMarginV >= 0.15); // Мінімальний запас 150 мВ

    if (spec.loadedWiresCount <= 1) {
        res.bundleDeratingFactor = 1.0;
    } else if (spec.loadedWiresCount == 2) {
        res.bundleDeratingFactor = 0.88;
    } else {
        const double k = 1.0 / std::sqrt(static_cast<double>(spec.loadedWiresCount));
        res.bundleDeratingFactor = (k < 0.40) ? 0.40 : k;
    }

    res.minBendRadiusStaticMm = 6.0 * spec.outerDiameterMm;
    res.minBendRadiusDynamicMm = 12.0 * spec.outerDiameterMm;

    return res;
}

} // namespace harness

int main() {
    constexpr harness::Spec spec{};
    const auto outcome = harness::evaluate(spec);

    if (!outcome) {
        std::cerr << "Помилка розрахунку джгута: некоректні геометричні параметри.\n";
        return 1;
    }

    const auto& res = *outcome;

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== РЕЗУЛЬТАТИ РОЗРАХУНКУ КАБЕЛЬНОГО ДЖГУТА (C++) ===\n";
    std::cout << "Опір жили за " << spec.ambientTempC << " °C:       " << res.wireResistanceOhm << " Ом\n";
    std::cout << "Сумарне падіння в петлі (±V):   " << res.totalLoopDropV << " В\n";
    std::cout << "Перекіс потенціалу землі (GND):  " << res.groundShiftV << " В\n";
    std::cout << "Рівень нуля на вході приймача:  " << res.actualVIlAtReceiver
              << " В (поріг: " << spec.logicVIlMax << " В)\n";
    std::cout << "Запас завадостійкості:           " << res.noiseMarginV
              << " В [" << (res.isLogicSafe ? "БЕЗПЕЧНО" : "НЕБЕЗПЕЧНИЙ ЗБІЙ") << "]\n";
    std::cout << "Делейтинг пучка провідників:     " << res.bundleDeratingFactor
              << " (струм знизити до " << (res.bundleDeratingFactor * 100.0) << "%)\n";
    std::cout << "Мін. радіус вигину (статика):    " << res.minBendRadiusStaticMm << " мм\n";
    std::cout << "Мін. радіус вигину (динаміка):   " << res.minBendRadiusDynamicMm << " мм\n";

    return 0;
}
```
:::

---

### Детальний аналіз результатів розрахунку

У наведеному типовому інженерному прикладі розглядається живлення плати модуля зв'язку струмом 1.5 А через кабель завдовжки 1.8 м на базі дротів 24 AWG (переріз 0.205 мм²):

1. **Ефект нагрівання міді:** За кімнатної температури опір однієї жили становив 0.151 Ом. При нагріванні всередині корпусу до 50 °C опір зріс до 0.169 Ом.
2. **Падіння напруги в силовій петлі:** Повний опір двох жил (плюс і земля) разом із перехідними контактами роз'ємів досяг `2 · 0.169 + 0.030 = 0.368 Ом`. Сумарне падіння напруги на навантаженні склало **0.552 В**. При живленні шиною 3.3 В до модуля доходить лише 2.748 В, що нижче порога стабільної роботи більшості мікросхем флеш-пам'яті та радіомодулів.
3. **Руйнування порогів інтерфейсу UART:** Перекіс землі на зворотній жилі становить `0.276 В`. Вхідний сигнал нуля, сформований передавачем (`0.20 В`), потрапляє на головний мікроконтролер із потенціалом `0.476 В`. Хоча він формально нижчий за поріг 0.80 В, запас завадостійкості зменшився з нормативних 600 мВ до 324 мВ. При роботі поруч сильних джерел електромагнітних завад (ШІМ моторів) такий сигнал буде періодично збоїти.
4. **Висновки для оптимізації проекту:**
   - Необхідно збільшити калібр силових жил до 20 AWG (0.518 мм²) або 18 AWG (0.823 мм²), щоб зменшити петльовий опір у 2.5–4 рази.
   - Відокремити сигнальну землю датчиків від силового повернення струму (зіркова топологія).
   - При монтажі джгута діаметром 7.5 мм забезпечити радіус повороту в корпусі не менше 45 мм у статиці та 90 мм на рухомих підвісах.
