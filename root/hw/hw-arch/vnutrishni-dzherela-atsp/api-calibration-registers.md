# 📋 Регістри, адреси пам'яті та часові параметри калібрування АЦП

Для точного розрахунку напруги живлення, температури кристала та стану батареї мікроконтролер використовує апаратні константи, прошиті виробником у захищену системну пам'ять (System Memory / Flash ROM), а також спеціальні біти керування вбудованими джерелами.

Нижче наведено структурований інженерний довідник адрес системної пам'яті, конфігураційних регістрів периферійного блоку АЦП, часових обмежень вибірки та структур даних для системного програмування.

---

### Організація системної пам'яті та адресні карти заводських коефіцієнтів

Виробники напівпровідникових мікросхем проводять фінішне випробування кожного кристала на автоматизованому тестовому обладнанні (ATE — Automated Test Equipment). Під час цього тесту кристал поміщають у термокамеру з фіксованою температурою, подають на виводи живлення стабілізовану напругу лабораторного класу та зчитують вихідні коди АЦП для всіх внутрішніх джерел.

Отримані калібрувальні відліки записуються в спеціальний інформаційний блок Flash-пам'яті (Information Block / System Memory). Ця область фізично відділена від основної пам'яті програм користувача, захищена від випадкового стирання апаратними бітами блокування і мапується в адресний простір мікроконтролера як область, доступна тільки для читання.

У таблиці наведено апаратні адреси комірок пам'яті, де зберігаються калібрувальні константи для поширених мікроконтролерів архітектури ARM Cortex-M:

| Архітектура / Родина MCU | Параметр у ROM | Базова адреса у пам'яті | Розрядність та умови заводського калібрування |
|---|---|---|---|
| **STM32G0 / G4 / L4 / WB / WL** | `VREFINT_CAL` | `0x1FFF75AA` | 16 біт (12-бітне значення): VDDA = 3.0 В ± 10 мВ, T = 30 °C ± 5 °C |
| | `TS_CAL1` | `0x1FFF75A8` | 16 біт (12-бітне значення): T = 30 °C ± 5 °C, VDDA = 3.0 В |
| | `TS_CAL2` | `0x1FFF75CA` | 16 біт (12-бітне значення): T = 130 °C (чи 110 °C), VDDA = 3.0 В |
| **STM32F0 / F3 / L0** | `VREFINT_CAL` | `0x1FFFF7BA` | 16 біт: еталонний код при VDDA = 3.3 В (або 3.0 В залежно від суфікса) |
| | `TS_CAL1` | `0x1FFFF7B8` | 16 біт: відлік термодатчика при T = 30 °C, VDDA = 3.3 В |
| | `TS_CAL2` | `0x1FFFF7C2` | 16 біт: відлік термодатчика при T = 110 °C, VDDA = 3.3 В |
| **STM32H7 / H7A3 / H7B3** | `VREFINT_CAL` | `0x1FF1E860` | 16 біт (16-бітний або 12-бітний режим): VDDA = 3.3 В |
| | `TS_CAL1` | `0x1FF1E820` | 16 біт: відлік термодатчика при T = 30 °C, VDDA = 3.3 В |
| | `TS_CAL2` | `0x1FF1E840` | 16 біт: відлік термодатчика при T = 110 °C, VDDA = 3.3 В |
| **STM32U5 (Low Power Ultra)** | `VREFINT_CAL` | `0x0BFA07A0` | 16 біт (14-бітний режим АЦП): VDDA = 3.0 В, T = 30 °C |
| | `TS_CAL1` | `0x0BFA0710` | 16 біт: код датчика при T = 30 °C |
| | `TS_CAL2` | `0x0BFA0742` | 16 біт: код датчика при T = 130 °C |
| **STM32F405..417 / F429** | `TS_CAL` (відсутній) | *Не калібровано* | Використовуються табличні дані даташита: V_25 = 0.76 В, Slope = 2.5 мВ/°C |

Зверніть увагу, що у родинах без індивідуального фабричного калібрування (наприклад, ранні серії STM32F405/407) у системній пам'яті відсутні записані відліки для температурного датчика. У таких системах прошивка змушена спиратися на усереднені табличні параметри з офіційного даташита, що збільшує абсолютну похибку визначення температури до кількох градусів, проте відносна динаміка нагріву залишається придатною для моніторингу перевантаження.

---

### Регістри спільного керування АЦП (ADC_CCR / ADC_Common)

Вбудовані аналогові блоки за замовчуванням знеструмлені для мінімізації фонового споживання енергії в режимах низького споживання (Sleep, Stop, Standby). Перед запуском перетворення системна програма повинна встановити відповідні біти у регістрі спільного керування АЦП (`ADC_CCR` або `ADC_Common->CCR`).

У мікроконтролерах із кількома перетворювачами (наприклад ADC1, ADC2, ADC3) регістр спільного керування є єдиним для пари або трійки блоків. При цьому внутрішні аналогові джерела зазвичай фізично підведені лише до комутатора першого перетворювача (ADC1) або третього (ADC3). Спроба опитати канал VREFINT через вторинний перетворювач ADC2 призведе до зчитування плаваючого потенціалу незадіяного входу.

Нижче наведено бітові маски та базові структури для роботи з регістром керування:

:::tabs
=== "C"
```c
#include <stdint.h>

/* Бітові маски та зміщення регістра ADC_CCR (STM32 ADC Common Control Register) */
#define ADC_CCR_VREFEN_Pos      (22U)
#define ADC_CCR_VREFEN_Msk      (0x1UL << ADC_CCR_VREFEN_Pos)
#define ADC_CCR_VREFEN          ADC_CCR_VREFEN_Msk      /* Дозвіл буфера VREFINT */

#define ADC_CCR_TSEN_Pos        (23U)
#define ADC_CCR_TSEN_Msk        (0x1UL << ADC_CCR_TSEN_Pos)
#define ADC_CCR_TSEN            ADC_CCR_TSEN_Msk        /* Дозвіл датчика температури */

#define ADC_CCR_VBATEN_Pos      (24U)
#define ADC_CCR_VBATEN_Msk      (0x1UL << ADC_CCR_VBATEN_Pos)
#define ADC_CCR_VBATEN          ADC_CCR_VBATEN_Msk      /* Дозвіл внутрішнього дільника VBAT */

#define ADC_CCR_PRESC_Pos       (18U)
#define ADC_CCR_PRESC_Msk       (0xFUL << ADC_CCR_PRESC_Pos) /* Дільник тактування АЦП */
```
=== "C++"
```cpp
#include <cstdint>

namespace McuAdc::Registers {

struct AdcCommonControl {
    static constexpr uint32_t vref_enable_pos   = 22U;
    static constexpr uint32_t vref_enable_mask  = (1UL << vref_enable_pos);

    static constexpr uint32_t temp_enable_pos   = 23U;
    static constexpr uint32_t temp_enable_mask  = (1UL << temp_enable_pos);

    static constexpr uint32_t vbat_enable_pos   = 24U;
    static constexpr uint32_t vbat_enable_mask  = (1UL << vbat_enable_pos);

    static constexpr uint32_t prescaler_pos     = 18U;
    static constexpr uint32_t prescaler_mask    = (0xFUL << prescaler_pos);
};

} // namespace McuAdc::Registers
```
:::

#### Детальний аналіз функціональних бітів:

1. **`VREFEN` (Internal Voltage Reference Enable):**
   - Біт керує подачею живлення на буферний операційний підсилювач кремнієвого джерела опорної напруги.
   - Коли біт скинуто в `0`, вихідний каскад переходить у стан високого імпедансу, вимикаючи струм споживання опорного вузла (економія близько 12–15 мкА).
   - Коли біт встановлено в `1`, джерело VREFINT запускається та підключається до вхідного каналу мультиплексора (у більшості серій це канал `ADC_IN17` або `ADC_IN0`).

2. **`TSEN` (Temperature Sensor Enable):**
   - Біт вмикає живлення генератора стабільного мікроструму для внутрішнього p-n переходу кремнієвого термодіода.
   - У стані `0` термосенсор знеструмлений і не споживає енергії.
   - У стані `1` датчик починає формувати вихідну напругу з температурним схилом близько 2.5 мВ/°C, підключену до внутрішнього каналу мультиплексора (зазвичай `ADC_IN16` або `ADC_IN18`).

3. **`VBATEN` (VBAT Divider Enable):**
   - Біт керує затвором аналогового польового транзистора, що вмикає внутрішній прецизійний резистивний дільник між зовнішнім виводом живлення батареї VBAT та землею.
   - У стані `0` ключ розімкнений, струм витоку з резервної батарейки дорівнює нулю (менше 1 нА).
   - У стані `1` ключ замкнений, напруга ділиться на коефіцієнт K_div і передається на ядро перетворювача.

---

### Часові параметри та вимоги до вибірки (Sample Timing Parameters)

Внутрішні аналогові джерела суттєво відрізняються від зовнішніх низькоомних сигналів величиною вихідного імпедансу. Якщо зовнішній операційний підсилювач має вихідний опір у кілька ом, то внутрішній термодіод та дільник батареї мають еквівалентний опір від 15 до 100 кОм.

Якщо час вибірки t_S (Sample Time) налаштовано занадто коротким, внутрішній вибірковий конденсатор АЦП C_S (ємністю близько 5–8 пФ) не встигає зарядитися до повної амплітуди вхідного сигналу за час замикання аналогового ключа. Це призводить до систематичного заниження виміряного коду та появи перехресних завад від попереднього вимірюваного каналу.

У таблиці наведено мінімальні та рекомендовані часові інтервали для коректного оцифрування внутрішніх ліній:

| Параметр | Символ | Типове значення | Мінімальний допустимий час | Рекомендована кількість тактів АЦП |
|---|---|---|---|---|
| Час стабілізації опори після увімкнення `VREFEN` | t_START_VREF | 10 мкс | 12 мкс | Програмна затримка перед запуском перетворення |
| Час стабілізації термодатчика після увімкнення `TSEN` | t_START_TS | 15 мкс | 20 мкс | Програмна затримка перед запуском перетворення |
| Час вибірки каналу VREFINT (R_out ≈ 15 кОм) | t_S_VREF | 4.0 мкс | 4.0 мкс | ≥ 160.5 тактів при F_ADC = 32 МГц |
| Час вибірки каналу термодатчика (R_out ≈ 100 кОм) | t_S_TEMP | 5.0 мкс | 5.0 мкс | ≥ 247.5 тактів при F_ADC = 32 МГц |
| Час вибірки каналу VBAT (R_out ≈ 50 кОм) | t_S_VBAT | 12.0 мкс | 12.0 мкс | ≥ 390.5–640.5 тактів при F_ADC = 32 МГц |

Розрахунок кількості тактів для регістра вибірки `ADC_SMPR` виконується за формулою:

```text
Кількість_тактів = t_S_min * F_ADC
```

Наприклад, при тактовій частоті АЦП F_ADC = 32 МГц період одного такту становить 31.25 нс. Для забезпечення мінімального часу вибірки термодатчика 5.0 мкс необхідно встановити не менше ніж `5000 нс / 31.25 нс = 160 тактів`. Оптимальним вибором у регістрі `ADC_SMPR` буде найближче більше значення — 247.5 або 640.5 тактів перетворення.

---

### Дільники каналу батареї за родинами мікроконтролерів

Коефіцієнт поділу K_div обирається виробником апаратно так, щоб максимальна напруга батареї не перевищувала мінімально можливе значення VDDA за будь-яких умов експлуатації:

:::tabs
=== "C"
```c
/* Коефіцієнти внутрішнього дільника VBAT для різних архітектур */
#if defined(STM32F4) || defined(STM32F2)
    #define MCU_VBAT_DIVIDER_RATIO      (2U)  /* Дільник 1/2: V_ADC = VBAT / 2 */
#elif defined(STM32G0) || defined(STM32G4) || defined(STM32L4) || defined(STM32WB)
    #define MCU_VBAT_DIVIDER_RATIO      (3U)  /* Дільник 1/3: V_ADC = VBAT / 3 */
#elif defined(STM32H7) || defined(STM32H5) || defined(STM32U5)
    #define MCU_VBAT_DIVIDER_RATIO      (4U)  /* Дільник 1/4: V_ADC = VBAT / 4 */
#else
    #define MCU_VBAT_DIVIDER_RATIO      (3U)  /* За замовчуванням для сучасних MCU */
#endif
```
=== "C++"
```cpp
#include <cstdint>

namespace McuAdc {

enum class McuFamily {
    Stm32F4,
    Stm32G4,
    Stm32H7,
    Stm32U5
};

template <McuFamily Family>
struct FamilyTraits;

template <>
struct FamilyTraits<McuFamily::Stm32F4> {
    static constexpr uint8_t vbat_divider = 2U;
    static constexpr uint16_t cal_vref_mv = 3300U;
};

template <>
struct FamilyTraits<McuFamily::Stm32G4> {
    static constexpr uint8_t vbat_divider = 3U;
    static constexpr uint16_t cal_vref_mv = 3000U;
};

template <>
struct FamilyTraits<McuFamily::Stm32H7> {
    static constexpr uint8_t vbat_divider = 4U;
    static constexpr uint16_t cal_vref_mv = 3300U;
};

} // namespace McuAdc
```
:::

---

### Структури даних конфігурації та безпечного доступу до ROM

Системний код повинен перевіряти цілісність заводських констант перед їх використанням. Якщо мікроконтролер перепрошивався неофіційним програматором або зазнав апаратного збою флеш-пам'яті, комірки ROM можуть містити нульові значення або значення `0xFFFF`. Пряме ділення на такий коефіцієнт призведе до ділення на нуль або спотворення всіх аналогових вимірювань у системі.

Нижче наведено модуль безпечного читання калібрувальних даних із верифікацією діапазонів:

:::tabs
=== "C"
```c
#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Апаратні адреси заводських калібрувальних значень для STM32G4
 */
#define STM32G4_VREFINT_CAL_ADDR   ((const volatile uint16_t*)0x1FFF75AAUL)
#define STM32G4_TS_CAL1_ADDR       ((const volatile uint16_t*)0x1FFF75A8UL)
#define STM32G4_TS_CAL2_ADDR       ((const volatile uint16_t*)0x1FFF75CAUL)

/**
 * @brief Структура параметрів калібрування АЦП
 */
typedef struct {
    uint16_t vrefint_cal;    /* Значення VREFINT_CAL при напрузі калібрування */
    uint16_t ts_cal1;        /* Значення TS_CAL1 при температурі T1 (30 °C) */
    uint16_t ts_cal2;        /* Значення TS_CAL2 при температурі T2 (110 або 130 °C) */
    uint16_t cal_vref_mv;    /* Еталонна напруга калібрування (типово 3000 мВ) */
    int16_t  ts_cal1_temp;   /* Температура калібрування точки 1 (°C) */
    int16_t  ts_cal2_temp;   /* Температура калібрування точки 2 (°C) */
    uint8_t  vbat_div;       /* Коефіцієнт дільника напруги батареї VBAT */
    bool     valid;          /* Прапорець достовірності даних у пам'яті */
} McuAdcCalibrationData;

static inline McuAdcCalibrationData mcu_adc_read_factory_cal(void) {
    McuAdcCalibrationData cal;
    cal.vrefint_cal  = *STM32G4_VREFINT_CAL_ADDR;
    cal.ts_cal1      = *STM32G4_TS_CAL1_ADDR;
    cal.ts_cal2      = *STM32G4_TS_CAL2_ADDR;
    cal.cal_vref_mv  = 3000U;
    cal.ts_cal1_temp = 30;
    cal.ts_cal2_temp = 130;
    cal.vbat_div     = 3U;

    // Перевірка цілісності: діапазон валідних значень для 12-бітного АЦП
    if ((cal.vrefint_cal > 1000 && cal.vrefint_cal < 2500) &&
        (cal.ts_cal1 > 500 && cal.ts_cal1 < 3000) &&
        (cal.ts_cal2 > cal.ts_cal1 && cal.ts_cal2 < 4095)) {
        cal.valid = true;
    } else {
        // Fallback константи при пошкодженій або незаписаній Flash
        cal.vrefint_cal = 1650;
        cal.ts_cal1     = 1035;
        cal.ts_cal2     = 1380;
        cal.valid       = false;
    }

    return cal;
}
```
=== "C++"
```cpp
#include <cstdint>
#include <span>
#include <optional>

namespace McuAdc {

/**
 * @brief Структура заводського калібрування з типізованими параметрами
 */
struct FactoryCalibration {
    uint16_t vrefint_cal{1650};
    uint16_t ts_cal1{1035};
    uint16_t ts_cal2{1380};
    uint16_t cal_vref_mv{3000};
    int16_t  ts_cal1_temp_c{30};
    int16_t  ts_cal2_temp_c{130};
    uint8_t  vbat_multiplier{3};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (vrefint_cal > 1000 && vrefint_cal < 2500) &&
               (ts_cal1 > 500 && ts_cal1 < 3000) &&
               (ts_cal2 > ts_cal1 && ts_cal2 < 4095);
    }
};

/**
 * @brief Безпечне читання заводських констант для сімейства STM32G4
 */
[[nodiscard]] inline FactoryCalibration read_hardware_calibration() noexcept {
    constexpr uintptr_t addr_vrefint = 0x1FFF75AAUL;
    constexpr uintptr_t addr_ts_cal1 = 0x1FFF75A8UL;
    constexpr uintptr_t addr_ts_cal2 = 0x1FFF75CAUL;

    FactoryCalibration cal;
    cal.vrefint_cal     = *reinterpret_cast<const volatile uint16_t*>(addr_vrefint);
    cal.ts_cal1         = *reinterpret_cast<const volatile uint16_t*>(addr_ts_cal1);
    cal.ts_cal2         = *reinterpret_cast<const volatile uint16_t*>(addr_ts_cal2);
    cal.cal_vref_mv     = 3000;
    cal.ts_cal1_temp_c  = 30;
    cal.ts_cal2_temp_c  = 130;
    cal.vbat_multiplier = 3;

    if (!cal.is_valid()) {
        // Fallback константи при пошкодженій системній пам'яті
        cal.vrefint_cal = 1650;
        cal.ts_cal1     = 1035;
        cal.ts_cal2     = 1380;
    }

    return cal;
}

} // namespace McuAdc
```
:::
