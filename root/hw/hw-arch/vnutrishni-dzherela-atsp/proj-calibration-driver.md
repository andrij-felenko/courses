# ⚙️ Повний драйвер внутрішніх калібрувальних вимірювань АЦП

Промисловий драйвер для вимірювання внутрішніх джерел АЦП у вбудованих системах повинен одночасно вирішувати чотири ключові інженерні задачі:
1. **Керування енергоспоживанням (Power Gating):** вмикати буфер `VREFINT`, термодатчик та дільник `VBAT` лише на час короткої серії вимірювань, витримувати час стабілізації t_START ≥ 15 мкс, після чого повністю знеструмлювати їх для збереження ресурсу акумулятора.
2. **Апаратний час вибірки (Sample Time):** індивідуально конфігурувати тривалий час заряду вибіркового конденсатора (t_S ≥ 160.5 тактів АЦП) для високоомних внутрішніх ліній.
3. **Фільтрація шуму:** застосовувати апаратне оверсемплювання або програмний медіанний фільтр для відсікання імпульсних завад від роботи цифрового процесорного ядра та імпульсного DC-DC перетворювача.
4. **Захист від некоректних даних:** перевіряти цілісність заводських констант у пам'яті ROM і застосовувати безпечні табличні константи за замовчуванням при пошкодженні даних.

Нижче наведено повну модульну реалізацію виробничого драйвера мовами C та ідіоматичною C++20.

---

### Архітектура та життєвий цикл драйвера

Вимірювальний цикл організовано у вигляді скінченного автомата з послідовними фазами:
- **Фаза 1: Пробудження джерел.** Встановлення бітів `VREFEN`, `TSEN`, `VBATEN` у регістрі `ADC_CCR`.
- **Фаза 2: Пауза стабілізації.** Апаратний або таймерний інтервал очікування t_START (15–20 мкс) до повного встановлення напруг на виходах внутрішніх буферів.
- **Фаза 3: Пакетне перетворення.** Опитування регулярної послідовності каналів (`VREFINT`, `TEMPSENSOR`, `VBAT`, зовнішні аналогові канали) через прямий доступ до пам'яті (DMA).
- **Фаза 4: Математична обробка.** Фільтрація відліків та обчислення фізичних величин (мВ, 0.1 °C) у цілочисельному форматі.
- **Фаза 5: Знеструмлення.** Очищення бітів керування та перехід АЦП у режим сну.

У батарейних пристроях вимірювання зазвичай запускається періодично (наприклад, один раз на секунду або перед кожним сеансом радіозв'язку). Активна фаза драйвера триває менше 100 мкс, що знижує середній струм споживання аналогового тракту до часток мікроампера.

---

### Організація DMA-буфера та фільтрація шумів

При роботі в умовах сильних електромагнітних завад (наприклад, поруч із імпульсним стабілізатором напруги чи силовими транзисторами приводу) поодинокий відлік АЦП може містити випадковий імпульсний викид. Для усунення таких завад драйвер налаштовує перетворювач на циклічне зняття серії з 5 або 7 послідовних вибірок для кожного каналу за допомогою контролера прямого доступу до пам'яті (DMA).

Контролер DMA переносить результати перетворення безпосередньо в оперативну пам'ять без залучення процесорного ядра. Після завершення передачі блоку генерується переривання `DMA_TCIF` (Transfer Complete Interrupt Flag), яке пробуджує обробник математичного перерахунку.

Отриманий масив відліків обробляється нелінійним ранговим фільтром (медіаною). На відміну від простого середнього арифметичного, медіанний фільтр повністю відкидає поодинокі екстремальні сплески, не спотворюючи справжнього значення сигналу та не додаючи фазової затримки. Якщо потрібне додаткове згладжування білого шуму, після медіани застосовується експоненційне ковзне середнє (EMA — Exponential Moving Average):

```text
EMA[k] = α * Median_Sample + (1 - α) * EMA[k-1]
```

Для цілочисельної реалізації коефіцієнт згладжування обирається у вигляді ступеня двійки (наприклад, `α = 1/4`), що замінює множення швидким бітовим зсувом.

---

### Обробка крайових випадків та відмовостійкість

У критичних застосуваннях драйвер контролює фізичні межі відновлених параметрів:
1. **Контроль напруги VDDA:** Якщо розраховане значення VDDA падає нижче 2.0 В або перевищує 3.6 В, це сигналізує про критичну просадку батареї або пробій регулятора напруги. У такому разі формується прапорець апаратного попередження `HARDWARE_FAULT`.
2. **Контроль температури:** Якщо розрахована температура T_J перевищує +105 °C, система повинна знизити тактову частоту або вимкнути силові споживачі для запобігання тепловому пробою кристала.
3. **Захист від ділення на нуль:** Якщо відлік `Raw_VREFINT` повертає нуль через коротке замикання або збій аналогового мультиплексора, функція обчислення безпечно повертає нульові значення з ознакою `valid = false`.

---

### Реалізація драйвера на мовах C та C++

:::tabs
=== "C"
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Апаратні адреси системної Flash-пам'яті для родини STM32G4 / STM32L4 */
#define MCU_VREFINT_CAL_ADDR    ((const volatile uint16_t*)0x1FFF75AAUL)
#define MCU_TS_CAL1_ADDR        ((const volatile uint16_t*)0x1FFF75A8UL)
#define MCU_TS_CAL2_ADDR        ((const volatile uint16_t*)0x1FFF75CAUL)

#define MCU_CAL_VREF_MV         (3000U)  /* Напруга заводського стенду: 3.0 В */
#define MCU_TS_CAL1_TEMP_C      (30)     /* Температура точки 1: +30 °C */
#define MCU_TS_CAL2_TEMP_C      (130)    /* Температура точки 2: +130 °C */
#define MCU_VBAT_DIV_RATIO      (3U)     /* Апаратний дільник VBAT 1/3 */

/* Результати вимірювання внутрішніх джерел */
typedef struct {
    uint32_t vdda_mv;           /* Напруга живлення в мілівольтах */
    int32_t  temperature_degc;  /* Температура кристала в десятих частках °C (0.1 °C) */
    uint32_t vbat_mv;           /* Напруга батареї в мілівольтах */
    bool     valid;             /* Ознака валідності вимірювання */
} McuInternalMetrics;

/* Структура конфігурації та кешу калібрування */
typedef struct {
    uint16_t vrefint_cal;
    uint16_t ts_cal1;
    uint16_t ts_cal2;
    bool     cal_valid;
} McuAdcDriver;

/**
 * @brief Ініціалізація та читання заводських коефіцієнтів
 */
void mcu_adc_driver_init(McuAdcDriver *driver) {
    if (!driver) return;

    driver->vrefint_cal = *MCU_VREFINT_CAL_ADDR;
    driver->ts_cal1     = *MCU_TS_CAL1_ADDR;
    driver->ts_cal2     = *MCU_TS_CAL2_ADDR;

    /* Перевірка цілісності: чи значення не є затертими (0x0000 чи 0xFFFF) */
    if ((driver->vrefint_cal > 1000 && driver->vrefint_cal < 2500) &&
        (driver->ts_cal1 > 500 && driver->ts_cal1 < 3000) &&
        (driver->ts_cal2 > driver->ts_cal1 && driver->ts_cal2 < 4095)) {
        driver->cal_valid = true;
    } else {
        /* Запасні константи за даташитом при пошкодженні пам'яті */
        driver->vrefint_cal = 1650;  /* 1.212 В при 3.0 В на 12 бітах */
        driver->ts_cal1     = 1035;  /* Орієнтовний код для +30 °C */
        driver->ts_cal2     = 1380;  /* Орієнтовний код для +130 °C */
        driver->cal_valid   = false;
    }
}

/**
 * @brief Обчислення медіани з масиву 5 відліків для придушення викидів шуму
 */
static uint16_t filter_median5(uint16_t samples[5]) {
    uint16_t s[5];
    memcpy(s, samples, sizeof(s));
    for (int i = 0; i < 4; ++i) {
        for (int j = i + 1; j < 5; ++j) {
            if (s[i] > s[j]) {
                uint16_t tmp = s[i];
                s[i] = s[j];
                s[j] = tmp;
            }
        }
    }
    return s[2]; // Центральний елемент відсортованого масиву
}

/**
 * @brief Розрахунок фізичних параметрів за сирими відліками АЦП
 */
McuInternalMetrics mcu_adc_calculate_metrics(const McuAdcDriver *driver,
                                             uint16_t raw_vrefint,
                                             uint16_t raw_temp,
                                             uint16_t raw_vbat) {
    McuInternalMetrics m;
    m.valid = false;

    if (!driver || raw_vrefint == 0) {
        m.vdda_mv = 0;
        m.temperature_degc = 0;
        m.vbat_mv = 0;
        return m;
    }

    /* 1. Точне відновлення VDDA в мілівольтах */
    uint32_t vdda_calc = ((uint32_t)MCU_CAL_VREF_MV * driver->vrefint_cal + (raw_vrefint / 2U)) / raw_vrefint;
    m.vdda_mv = vdda_calc;

    /* 2. Нормалізація коду термодатчика до напруги 3.0 В */
    uint32_t ts_norm = ((uint32_t)raw_temp * driver->vrefint_cal + (raw_vrefint / 2U)) / raw_vrefint;

    /* 3. Лінійна інтерполяція температури кристала в десятих частках °C (0.1 °C) */
    int32_t delta_t_x10 = (MCU_TS_CAL2_TEMP_C - MCU_TS_CAL1_TEMP_C) * 10;
    int32_t cal_diff = (int32_t)driver->ts_cal2 - (int32_t)driver->ts_cal1;
    if (cal_diff != 0) {
        int32_t temp_x10 = ((int32_t)(ts_norm - driver->ts_cal1) * delta_t_x10 + (cal_diff / 2)) / cal_diff + 
                           (MCU_TS_CAL1_TEMP_C * 10);
        m.temperature_degc = temp_x10;
    } else {
        m.temperature_degc = 0;
    }

    /* 4. Розрахунок напруги батареї з урахуванням дільника 1/3 */
    uint32_t vbat_raw_mv = (vdda_calc * (uint32_t)raw_vbat + 2047U) / 4095U;
    m.vbat_mv = vbat_raw_mv * MCU_VBAT_DIV_RATIO;

    m.valid = true;
    return m;
}
```
=== "C++"
```cpp
#include <cstdint>
#include <span>
#include <array>
#include <algorithm>
#include <optional>

namespace McuAdc {

/**
 * @brief Структура фізичних результатів з типізованими одиницями
 */
struct InternalMetrics {
    uint32_t millivolts_vdda{0};
    int32_t  millidegrees_temperature{0}; // 1/1000 °C
    uint32_t millivolts_vbat{0};
};

/**
 * @brief Драйвер калібрування внутрішніх джерел АЦП на C++20
 */
class CalibrationDriver {
public:
    struct CalibrationRom {
        uint16_t vrefint_cal{0};
        uint16_t ts_cal1{0};
        uint16_t ts_cal2{0};
        uint16_t cal_vref_mv{3000};
        int16_t  ts_cal1_c{30};
        int16_t  ts_cal2_c{130};
        uint8_t  vbat_multiplier{3};
    };

    explicit CalibrationDriver(std::optional<CalibrationRom> custom_rom = std::nullopt) noexcept {
        if (custom_rom.has_value()) {
            rom_ = *custom_rom;
        } else {
            read_hardware_rom();
        }
    }

    /**
     * @brief Розрахунок метрик за сирими відліками
     */
    [[nodiscard]] std::optional<InternalMetrics> calculate(
        uint16_t raw_vrefint,
        uint16_t raw_temperature,
        uint16_t raw_vbat) const noexcept {
        
        if (raw_vrefint == 0 || rom_.vrefint_cal == 0) {
            return std::nullopt;
        }

        InternalMetrics result;

        // 1. Точна напруга VDDA в мВ (цілочисельне ділення з математичним округленням)
        const uint32_t vdda_mv = (static_cast<uint32_t>(rom_.cal_vref_mv) * rom_.vrefint_cal + 
                                  (raw_vrefint / 2U)) / raw_vrefint;
        result.millivolts_vdda = vdda_mv;

        // 2. Нормалізація відліку термодатчика до напруги 3000 мВ
        const uint32_t ts_norm = (static_cast<uint32_t>(raw_temperature) * rom_.vrefint_cal + 
                                  (raw_vrefint / 2U)) / raw_vrefint;

        // 3. Інтерполяція температури в міліградусах (0.001 °C)
        const int32_t delta_cal = static_cast<int32_t>(rom_.ts_cal2) - static_cast<int32_t>(rom_.ts_cal1);
        if (delta_cal > 0) {
            const int32_t delta_temp_mc = (rom_.ts_cal2_c - rom_.ts_cal1_c) * 1000;
            const int32_t temp_mc = (static_cast<int32_t>(ts_norm - rom_.ts_cal1) * delta_temp_mc + (delta_cal / 2)) / delta_cal +
                                    (rom_.ts_cal1_c * 1000);
            result.millidegrees_temperature = temp_mc;
        }

        // 4. Напруга батареї
        const uint32_t vbat_pin_mv = (vdda_mv * static_cast<uint32_t>(raw_vbat) + 2047U) / 4095U;
        result.millivolts_vbat = vbat_pin_mv * rom_.vbat_multiplier;

        return result;
    }

    /**
     * @brief Медіанний фільтр для масиву відліків
     */
    template <size_t N>
    [[nodiscard]] static uint16_t filter_median(std::array<uint16_t, N> samples) noexcept {
        static_assert(N % 2 == 1, "Кількість відліків має бути непарною");
        std::nth_element(samples.begin(), samples.begin() + N / 2, samples.end());
        return samples[N / 2];
    }

private:
    void read_hardware_rom() noexcept {
        constexpr uintptr_t addr_vrefint = 0x1FFF75AAUL;
        constexpr uintptr_t addr_ts_cal1 = 0x1FFF75A8UL;
        constexpr uintptr_t addr_ts_cal2 = 0x1FFF75CAUL;

        rom_.vrefint_cal     = *reinterpret_cast<const volatile uint16_t*>(addr_vrefint);
        rom_.ts_cal1         = *reinterpret_cast<const volatile uint16_t*>(addr_ts_cal1);
        rom_.ts_cal2         = *reinterpret_cast<const volatile uint16_t*>(addr_ts_cal2);
        rom_.cal_vref_mv     = 3000;
        rom_.ts_cal1_c       = 30;
        rom_.ts_cal2_c       = 130;
        rom_.vbat_multiplier = 3;

        // Fallback при некоректному ROM
        if (rom_.vrefint_cal < 1000 || rom_.vrefint_cal > 2500 || rom_.ts_cal2 <= rom_.ts_cal1) {
            rom_.vrefint_cal = 1650;
            rom_.ts_cal1     = 1035;
            rom_.ts_cal2     = 1380;
        }
    }

    CalibrationRom rom_{};
};

} // namespace McuAdc
```
:::

---

### Практичні особливості системної інтеграції

1. **Режим низького споживання:** Якщо мікроконтролер переходить у сон (Stop / Standby), біти `VREFEN` та `TSEN` необхідно обов'язково очищати перед переходом. Постійне живлення цих аналогових вузлів створює паразитичний витік струму 35–50 мкА, що скорочує термін автономної роботи пристрою від батарейки CR2032 з кількох років до лічених місяців.
2. **Час пробудження аналогових блоків:** Після виставлення біта `ADC_CCR_VREFEN = 1` обов'язково потрібна апаратна чи програмна пауза щонайменше 12–15 мкс перед подачею команди старту перетворення (`ADSTART = 1`). Якщо запустити АЦП раніше цього часу, напруга на виході внутрішнього буфера не встигне встановитися до номінального рівня, і розрахована напруга живлення буде суттєво заниженою.
3. **Послідовність перетворення каналів:** При скануванні кількох каналів поспіль рекомендовано спочатку опитувати зовнішні низькоомні джерела, а внутрішні джерела з високим опором (`VREFINT`, `TEMPSENSOR`, `VBAT`) — наприкінці послідовності з максимальним встановленим значенням часу вибірки `SMPR` (наприклад 640.5 тактів). Це повністю усуває ефект перерозподілу залишкового заряду між каналами мультиплексора.
