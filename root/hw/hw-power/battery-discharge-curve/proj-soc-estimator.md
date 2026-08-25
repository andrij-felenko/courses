# ⚙️ Алгоритм оцінки стану заряду (SoC) за кривою відкрите коло — напруга

Оцінка залишку енергії в акумуляторі (State of Charge, SoC) є однією з найбільш відповідальних задач систем управління батареями (Battery Management System, BMS). Працездатність сучасного електромобіля, безпілотного літального апарата чи автономної сонячної станції безпосередньо залежить від точності знання поточного резерву енергії. Однак виміряти SoC безпосередньо «в лоб» фізичним датчиком неможливо: не існує приладу, який міг би зануритися всередину закритих комірок та порахувати кількість іонів літію у кристалічній ґратці електродів.

Єдиними доступними фізичними величинами для мікроконтролера є виміряна напруга на клемах `V_cell`, струм розряду `I` та температура `T`. Напруга на клемах під навантаженням постійно викривляється омічним спадом `I · R_i` та поляризаційними перенапругами.

Найпростіший метод оцінки — прямого вимірювання напруги — дає катастрофічну похибку (до 40–50%) під час зміни навантаження, оскільки омічний спад миттєво зсуває розрядну криву вниз. Метод інтегрування струму (Coulomb Counting, або підрахунок кулонів) є високоточним на коротких інтервалах, але накопичує монотонну похибку інтегрування через шум АЦП, дрейф нуля струмового датчика та нелінійний кулонівський ККД.

Практичні промислові системи BMS застосовують двокомпонентний алгоритм: підрахунок кулонів здійснює безперервне динамічне відстеження в реальному часі, а нелінійна крива напруги розімкненого кола (Open Circuit Voltage, OCV) використовується для корекції накопленої похибки та періодичного прив'язування нульової точки у станах спокою.

---

### Фізико-математична база алгоритму

Загальний вираз для динамічного оновлення стану заряду `SoC(t)` під час розряду струмом `I(t)` описується фундаментальним інтегральним рівнянням:

```
SoC(t) = SoC(0) - (1 / Q_max) · ∫₀ᵗ η_coulomb(I, T) · I(τ) dτ
```

де:
- `SoC(0)` — початковий рівень заряду (від 0.0 до 1.0);
- `Q_max` — поточна максимальна ємність батареї з урахуванням старіння (А·год);
- `η_coulomb(I, T)` — кулонівський коефіцієнт корисної дії (зазвичай `0.99–1.00` при розрядженні);
- `I(τ)` — миттєве значення струму навантаження.

Для компенсації просідання напруги під навантаженням алгоритм постійно розраховує відновлений потенціал розімкненого кола `V_ocv_est`:

```
V_ocv_est = V_cell + I · R_i(T, SoC)
```

При малих струмах навантаження (коли елемент наближається до стану спокою) значення `V_ocv_est` прямує до істинного термодинамічного потенціалу. Алгоритм виконує кусково-лінійну інтерполяцію за таблицею `OCV(SoC)` та вираховує статичну оцінку `SoC_ocv`.

Фінальний рівень заряду оновлюється за допомогою комплементарного Альфа-фільтра (Alpha-Filter), який плавно притягує інтегральний кулонівський показник до табличного значення OCV:

```
SoC_final = (1 - α) · SoC_coulomb + α · SoC_ocv
```

Значення вагового коефіцієнта `α` адаптивно змінюється від `0.0` (під час інтенсивного руху чи розрядження великим струмом) до `0.05–0.10` (у стані спокою або при макроскопічній релаксації).

---

### Практична реалізація оцінювача SoC

Нижче наведено робочий код оцінювача SoC для вбудованих систем. Реалізація надається у двох ідіоматичних варіантах: чистою мовою C (для мікроконтролерів без підтримки стандартної бібліотеки C++) та мовою C++20 (із застосуванням `std::array`, `std::upper_bound` та типу `noexcept`).

:::tabs
```c
/* soc_estimator.c — C-версія модуля оцінки стану заряду батареї */
#include <stdio.h>
#include <stdbool.h>

#define OCV_TABLE_SIZE 11

typedef struct {
    float soc_percent;     /* Точка SoC у відсотках (0.0 - 100.0) */
    float ocv_volts;       /* Напруга розімкненого кола в вольтах */
} OcvPoint;

/* Опорна крива OCV(SoC) для типового Li-ion елемента (3.7V nominal) */
static const OcvPoint ocv_lookup[OCV_TABLE_SIZE] = {
    {  0.0f, 3.00f},
    { 10.0f, 3.45f},
    { 20.0f, 3.68f},
    { 30.0f, 3.74f},
    { 40.0f, 3.77f},
    { 50.0f, 3.79f},
    { 60.0f, 3.83f},
    { 70.0f, 3.92f},
    { 80.0f, 4.02f},
    { 90.0f, 4.11f},
    {100.0f, 4.20f}
};

typedef struct {
    float nominal_capacity_ah;  /* Номінальна ємність батареї (А·год) */
    float internal_resistance;  /* Внутрішній опір R_i (Ом) */
    float v_cutoff;             /* Напруга відсічки (В) */
    float current_soc;          /* Поточний розрахований SoC (0.0 - 1.0) */
    float accumulated_mah;      /* Накопичений розряд в мА·год */
} BatteryEstimator;

void battery_estimator_init(BatteryEstimator *est, float capacity_ah, float r_internal_ohm, float v_cut) {
    est->nominal_capacity_ah = capacity_ah;
    est->internal_resistance = r_internal_ohm;
    est->v_cutoff = v_cut;
    est->current_soc = 1.0f; /* Початковий стан — 100% заряд */
    est->accumulated_mah = 0.0f;
}

/* Кусково-лінійна інтерполяція SoC за відновильним потенціалом OCV */
float ocv_to_soc(float ocv_volts) {
    if (ocv_volts <= ocv_lookup[0].ocv_volts) {
        return 0.0f;
    }
    if (ocv_volts >= ocv_lookup[OCV_TABLE_SIZE - 1].ocv_volts) {
        return 100.0f;
    }

    for (int i = 0; i < OCV_TABLE_SIZE - 1; i++) {
        if (ocv_volts >= ocv_lookup[i].ocv_volts && ocv_volts <= ocv_lookup[i + 1].ocv_volts) {
            float v_min = ocv_lookup[i].ocv_volts;
            float v_max = ocv_lookup[i + 1].ocv_volts;
            float soc_min = ocv_lookup[i].soc_percent;
            float soc_max = ocv_lookup[i + 1].soc_percent;

            float ratio = (ocv_volts - v_min) / (v_max - v_min);
            return soc_min + ratio * (soc_max - soc_min);
        }
    }
    return 0.0f;
}

/* Оновлення стану estimator на кожному такті вимірювання (dt в секундах) */
bool battery_estimator_update(BatteryEstimator *est, float v_cell, float current_amps, float dt_sec) {
    /* Перевірка критичної відсічки за напругою */
    if (v_cell <= est->v_cutoff) {
        est->current_soc = 0.0f;
        return false; /* Сигнал зупинити розряд */
    }

    /* Інтегрування струму (Coulomb Counting) */
    float delta_ah = (current_amps * dt_sec) / 3600.0f;
    est->accumulated_mah += delta_ah * 1000.0f;

    float soc_coulomb = est->current_soc - (delta_ah / est->nominal_capacity_ah);
    if (soc_coulomb < 0.0f) soc_coulomb = 0.0f;
    if (soc_coulomb > 1.0f) soc_coulomb = 1.0f;

    /* Якщо струм малий (|I| < 50 мА), корегуємо SoC за таблицею OCV */
    if (current_amps > -0.05f && current_amps < 0.05f) {
        float ocv_est = v_cell + current_amps * est->internal_resistance;
        float soc_ocv = ocv_to_soc(ocv_est) / 100.0f;

        /* Комплексне зважування (Alpha-filter): 95% Кулон + 5% OCV-корекція */
        est->current_soc = 0.95f * soc_coulomb + 0.05f * soc_ocv;
    } else {
        est->current_soc = soc_coulomb;
    }

    return true;
}
```
```cpp
// soc_estimator.hpp / .cpp — C++20 версія класу оцінки стану батареї
#include <iostream>
#include <vector>
#include <array>
#include <algorithm>
#include <cmath>
#include <optional>

namespace bms {

struct OcvPoint {
    float soc_percent;
    float ocv_volts;
};

class BatteryEstimator {
public:
    BatteryEstimator(float capacity_ah, float r_internal_ohm, float v_cutoff)
        : capacity_ah_(capacity_ah),
          r_internal_(r_internal_ohm),
          v_cutoff_(v_cutoff),
          current_soc_(1.0f),
          accumulated_mah_(0.0f) {}

    // Кусково-лінійна інтерполяція за кривою OCV
    [[nodiscard]] static float ocv_to_soc(float ocv_volts) noexcept {
        constexpr std::array<OcvPoint, 11> lookup = {{
            {  0.0f, 3.00f}, { 10.0f, 3.45f}, { 20.0f, 3.68f},
            { 30.0f, 3.74f}, { 40.0f, 3.77f}, { 50.0f, 3.83f},
            { 60.0f, 3.83f}, { 70.0f, 3.92f}, { 80.0f, 4.02f},
            { 90.0f, 4.11f}, {100.0f, 4.20f}
        }};

        if (ocv_volts <= lookup.front().ocv_volts) return 0.0f;
        if (ocv_volts >= lookup.back().ocv_volts) return 100.0f;

        auto it = std::upper_bound(lookup.begin(), lookup.end(), ocv_volts,
            [](float val, const OcvPoint& pt) { return val < pt.ocv_volts; });

        const auto& p2 = *it;
        const auto& p1 = *(it - 1);

        float ratio = (ocv_volts - p1.ocv_volts) / (p2.ocv_volts - p1.ocv_volts);
        return p1.soc_percent + ratio * (p2.soc_percent - p1.soc_percent);
    }

    // Оновлення стану алгоритму за такт вимірювання
    [[nodiscard]] bool update(float v_cell, float current_amps, float dt_sec) noexcept {
        if (v_cell <= v_cutoff_) {
            current_soc_ = 0.0f;
            return false; // Досягнуто граничну відсічку
        }

        float delta_ah = (current_amps * dt_sec) / 3600.0f;
        accumulated_mah_ += delta_ah * 1000.0f;

        float soc_coulomb = std::clamp(current_soc_ - (delta_ah / capacity_ah_), 0.0f, 1.0f);

        // Корекція за OCV при малому струмі розряду
        if (std::abs(current_amps) < 0.05f) {
            float ocv_est = v_cell + current_amps * r_internal_;
            float soc_ocv = ocv_to_soc(ocv_est) / 100.0f;
            current_soc_ = 0.95f * soc_coulomb + 0.05f * soc_ocv;
        } else {
            current_soc_ = soc_coulomb;
        }

        return true;
    }

    [[nodiscard]] float get_soc_percent() const noexcept { return current_soc_ * 100.0f; }
    [[nodiscard]] float get_consumed_mah() const noexcept { return accumulated_mah_; }

private:
    float capacity_ah_;
    float r_internal_;
    float v_cutoff_;
    float current_soc_;
    float accumulated_mah_;
};

} // namespace bms
```
:::

---

### Перевірка працездатності та аналіз інженерних крайніх випадків

Розглянемо ключові практичні пастки, які виникають при впровадженні цього алгоритму у реальні промислові вироби.

#### 1. Ефект гістерезису розрядно-зарядних кривих
Опорна крива `OCV(SoC)` під час розрядження та під час заряджання **не збігається повністю**. Через термодинамічний гістерезис фазових переходів у матеріалі електрода (наприклад, у графіті або LiFePO₄) напруга розімкненого кола після розряду на `2–5 мВ` нижча за напругу після заряду при тому самому фактичному рівні SoC. 

Якщо контролер використовує єдину усереднену таблицю OCV, похибка обчислення заряду в режимі спокою може досягати `4–6%`. У високоточних BMS зберігають дві окремі таблиці: `OCV_discharge(SoC)` та `OCV_charge(SoC)`, і вибір таблиці залежить від знаку струму перед переходом у стан спокою.

#### 2. Температурна залежність внутрішнього опору `R_i(T)`
При падінні температури від `+25 °C` до `-20 °C` опір `R_i` зростає у кілька разів. Якщо алгоритм використовує константне значення `R_i = 0.02 Ом`, обчислений потенціал `V_ocv_est = V_cell + I · R_i` під навантаженням на морозі виявиться значно заниженим. Алгоритм вирішить, що батарея повністю розряджена, хоча всередині елемента ще лишається понад 50% заряду. Для запобігання цьому внутрішній опір `R_i` у коді BMS табулюють залежно від температури `T`, яку зчитують із термистора NTC.

#### 3. Врахування старіння батареї (State of Health, SoH)
У міру циклування батареї її максимальна ємність `Q_max` зменшується (наприклад, від `3.0 А·год` до `2.4 А·год` при SoH = 80%), а опір `R_i` зростає на 40–80%. Якщо алгоритм не оновлює параметр `nominal_capacity_ah`, інтегрування струму Кулон-лічильником даватиме хибний відсоток залишку (наприклад, показуватиме 20% SoC тоді, коли акумулятор уже досяг фізичного коліна виснаження й відсічки `V_cut`). Тому промислові системи BMS постійно перераховують `Q_max` при кожному повному циклі розряду від 100% до 0%.

#### 4. Шум АЦП та дрейф нуля струмового шунта
Вимірювання струму через резистивний шунт за допомогою підсилювача й АЦП завжди має незначне зсунення нуля (Offset Error), наприклад `3–5 мА`. При тривалому простої пристрою протягом місяця цей дрейф дає хибне «накопичення» струму обсягом до `3.6 А·год`. Для блокування цього ефекту алгоритм BMS реалізує зону нечутливості (Deadband) навколо нуля: будь-який виміряний струм, менший за `10 мА`, примусово вважається нульовим.
