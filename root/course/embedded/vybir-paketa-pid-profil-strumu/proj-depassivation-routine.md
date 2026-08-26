# ⚙️ Алгоритм адаптивної депасивації та оцінки внутрішнього опору

Цей проєкт наводить повну інженерну реалізацію вбудованого модуля керування живленням для систем на базі первинних літій-тіонілхлоридних (Li-SOCl₂) елементів, що виконує планову адаптивну депасивацію та вимірювання динамічного внутрішнього опору джерела перед активацією енергоємного радіотракту.

У тривалих автономних системах (наприклад, лічильниках газу, тепла чи води з міжповірочним інтервалом 10–15 років) пристрій 99.9% часу перебуває у стані глибокого сну зі споживанням 2–5 мкА. За таких умов на поверхні металевого літієвого анода формується щільна ізоляційна плівка хлориду літію (LiCl). Якщо після місяців або років спокою мікроконтролер безпосередньо увімкне радіопередавач LoRaWAN або NB-IoT (зі струмом 100–300 мА), напруга батареї миттєво впаде нижче 2.0 В через перехідний мінімум напруги (TMV), що призведе до апаратного скидання (Brownout Reset, BOR).

### Схемотехніка вузла депасивації

Для безпечного руйнування плівки LiCl на друкованій платі реалізується кероване баластне навантаження:

```
          VCC_BAT (3.6 В)
             │
             ├───[ Резистор R_load (100 Ом, 0.25 Вт) ]
             │                     │
             │                   Drain
             │             GPIO ── Gate  [ N-MOSFET logic-level, Vgs_th < 1.2 В ]
             │                   Source
             │                     │
            GND                   GND
```

1. **Вибір польового транзистора (MOSFET):** Необхідно обирати N-канальний транзистор із логічним рівнем відкривання (Logic-Level Gate), у якого порогова напруга відкривання затвора V_gs_th не перевищує 1.0–1.2 В при кімнатній температурі, а опір відкритого каналу R_ds_on становить менше 50 мОм. Це гарантує повне відкривання ключа від виводу GPIO мікроконтролера навіть при падінні внутрішньої напруги живлення до 2.2–2.5 В.
2. **Вибір баластного резистора:** Номінал обирається в діапазоні 68–150 Ом (для типорозмірів AA / C / D). При напрузі 3.6 В і номіналі 100 Ом тестовий струм становить близько 36 мА. Цього струму достатньо для створення високої локальної напруженості електричного поля в мікропорах LiCl, але він не викликає перевантаження свіжої комірки. Потужність розсіювання на резисторі складає P = V^2 / R = (3.6)^2 / 100 = 0.13 Вт, тому використовують резистори типорозміру 0805 або 1206 із номінальною потужністю 0.25 Вт.

### Поетапний алгоритм адаптивного контролю

Процедура підготовки джерела живлення складається з чотирьох послідовних кроків:

1. **Вимірювання напруги холостого ходу (OCV):** Мікроконтролер вимикає баластний MOSFET, очікує 5 мс для завершення перехідних процесів на вхідних ємностях і зчитує напругу V_ocv за допомогою вбудованого АЦП із каліброваним внутрішнім джерелом опорної напруги (VREF). Якщо V_ocv < 3.0 В, батарея вважається виснаженою.
2. **Тестовий імпульс та розрахунок R_int:** Транзистор вмикається на 15 мс. АЦП виконує серію вибірок напруги під навантаженням V_load. Внутрішній опір комірки обчислюється за формулою:
   ```
   R_int = (V_ocv - V_load) / I_load    [за законом Ома для повного кола]
   ```
   де струм навантаження I_load = V_load / R_load.
3. **Циклічна депасивація:** Якщо напруга під баластом опускається нижче безпечного порогу (наприклад, 3.0 В), алгоритм формує серію імпульсів струму тривалістю 50 мс із паузами релаксації по 25 мс. Паузи критично необхідні для вирівнювання концентрації іонів в електроліті та відведення тепла. Серія триває доти, доки напруга під навантаженням не перевищить 3.0 В або до вичерпання ліміту спроб (наприклад, 10 циклів).
4. **Прийняття рішення щодо старту радіомодуля:** Якщо після депасивації внутрішній опір знизився до норми (R_int < 10–15 Ом), прошивка дає дозвіл на увімкнення радіомодуля. Якщо напруга залишається низькою, сеанс передачі скасовується, а подія деградації джерела записується в енергонезалежну пам'ять (Flash/EEPROM).

:::tabs
```c
// depassivation_driver.c — Драйвер депасивації та контролю батареї (C99)
#include <stdint.h>
#include <stdbool.h>

#define DEPASS_RESISTOR_MOHM    100000UL  // Баластний резистор 100 Ом (100000 мОм)
#define DEPASS_PULSE_MS         50U       // Тривалість імпульсу депасивації (мс)
#define DEPASS_MAX_ATTEMPTS     10U       // Максимальна кількість спроб розминки
#define BATTERY_SAFE_MV         3000U     // Безпечний поріг для старту радіо (3.0 В)
#define BATTERY_CRITICAL_MV     2400U     // Критичний поріг просідання під тестом (2.4 В)

typedef enum {
    BATTERY_STATUS_READY = 0,
    BATTERY_STATUS_DEPASSIVATED,
    BATTERY_STATUS_LOW_BATTERY,
    BATTERY_STATUS_FAULT
} battery_status_t;

typedef struct {
    uint32_t (*read_voltage_mv)(void);
    void (*set_load_switch)(bool enable);
    void (*delay_ms)(uint32_t ms);
} battery_hal_t;

typedef struct {
    uint32_t v_ocv_mv;
    uint32_t v_load_mv;
    uint32_t r_int_mohm;
    uint8_t depass_cycles_done;
    battery_status_t status;
} battery_diag_t;

battery_status_t battery_prepare_for_tx(const battery_hal_t *hal, battery_diag_t *diag) {
    if (!hal || !hal->read_voltage_mv || !hal->set_load_switch || !hal->delay_ms || !diag) {
        return BATTERY_STATUS_FAULT;
    }

    diag->depass_cycles_done = 0;
    
    // 1. Вимірювання напруги холостого ходу (Open Circuit Voltage)
    hal->set_load_switch(false);
    hal->delay_ms(5);
    diag->v_ocv_mv = hal->read_voltage_mv();

    if (diag->v_ocv_mv < BATTERY_SAFE_MV) {
        diag->status = BATTERY_STATUS_LOW_BATTERY;
        return BATTERY_STATUS_LOW_BATTERY;
    }

    // 2. Тестовий імпульс навантаження та адаптивна депасивація
    for (uint8_t attempt = 0; attempt < DEPASS_MAX_ATTEMPTS; ++attempt) {
        hal->set_load_switch(true);
        hal->delay_ms(15); // Час на встановлення перехідного процесу
        diag->v_load_mv = hal->read_voltage_mv();
        
        // Якщо напруга під баластом вище безпечного порогу — депасивація завершена
        if (diag->v_load_mv >= BATTERY_SAFE_MV) {
            hal->set_load_switch(false);
            
            // Розрахунок R_int: R_int = (V_ocv - V_load) / (V_load / R_load)
            uint32_t delta_v = diag->v_ocv_mv - diag->v_load_mv;
            diag->r_int_mohm = (uint32_t)(((uint64_t)delta_v * DEPASS_RESISTOR_MOHM) / diag->v_load_mv);
            
            diag->status = (attempt == 0) ? BATTERY_STATUS_READY : BATTERY_STATUS_DEPASSIVATED;
            return diag->status;
        }

        // Продовжуємо імпульс депасивації під струмом
        hal->delay_ms(DEPASS_PULSE_MS);
        hal->set_load_switch(false);
        diag->depass_cycles_done++;
        
        // Пауза між імпульсами для дифузійного релаксування електроліту
        hal->delay_ms(25);
    }

    // Якщо після максимальної кількості спроб напруга не піднялась
    diag->status = (diag->v_load_mv < BATTERY_CRITICAL_MV) ? BATTERY_STATUS_LOW_BATTERY : BATTERY_STATUS_FAULT;
    return diag->status;
}
```
```cpp
// depassivation_driver.hpp — Ідіоматичний C++20 модуль контролю джерела живлення
#include <cstdint>
#include <concepts>
#include <chrono>
#include <expected>
#include <utility>

enum class BatteryError {
    HardwareFault,
    CriticalBrownoutRisk,
    EndOfLifeDepleted,
    PassivationUnresolved
};

struct BatteryMetrics {
    std::uint32_t open_circuit_mv{0};
    std::uint32_t loaded_voltage_mv{0};
    std::uint32_t internal_resistance_mohm{0};
    std::uint8_t depassivation_pulses{0};
};

template <typename PlatformHAL>
concept BatteryHALConcept = requires(PlatformHAL hal, bool enable, std::chrono::milliseconds ms) {
    { hal.read_voltage_mv() } -> std::same_as<std::uint32_t>;
    { hal.set_load_resistor(enable) } -> std::same_as<void>;
    { hal.sleep_for(ms) } -> std::same_as<void>;
};

template <BatteryHALConcept HAL>
class AdaptiveBatteryGuard {
public:
    static constexpr std::uint32_t LoadResistorMohm = 100'000;  // 100 Ом
    static constexpr std::uint32_t SafeTxVoltageMv = 3'000;     // 3.0 В
    static constexpr std::uint32_t CriticalVoltageMv = 2'400;   // 2.4 В
    static constexpr std::uint8_t MaxAttempts = 10;

    explicit constexpr AdaptiveBatteryGuard(HAL& hal) noexcept : hal_(hal) {}

    [[nodiscard]] std::expected<BatteryMetrics, BatteryError> prepare_for_transmission() noexcept {
        BatteryMetrics metrics{};
        
        // 1. Зчитування напруги холостого ходу
        hal_.set_load_resistor(false);
        hal_.sleep_for(std::chrono::milliseconds(5));
        metrics.open_circuit_mv = hal_.read_voltage_mv();

        if (metrics.open_circuit_mv < SafeTxVoltageMv) {
            return std::unexpected(BatteryError::EndOfLifeDepleted);
        }

        // 2. Цикл адаптивної депасивації
        for (std::uint8_t i = 0; i < MaxAttempts; ++i) {
            hal_.set_load_resistor(true);
            hal_.sleep_for(std::chrono::milliseconds(15));
            metrics.loaded_voltage_mv = hal_.read_voltage_mv();

            if (metrics.loaded_voltage_mv >= SafeTxVoltageMv) {
                hal_.set_load_resistor(false);
                metrics.depassivation_pulses = i;

                const std::uint64_t delta_v = metrics.open_circuit_mv - metrics.loaded_voltage_mv;
                metrics.internal_resistance_mohm = static_cast<std::uint32_t>(
                    (delta_v * LoadResistorMohm) / metrics.loaded_voltage_mv
                );
                return metrics;
            }

            // Додаткова витримка під струмом для розчинення LiCl
            hal_.sleep_for(std::chrono::milliseconds(50));
            hal_.set_load_resistor(false);
            hal_.sleep_for(std::chrono::milliseconds(25));
        }

        if (metrics.loaded_voltage_mv < CriticalVoltageMv) {
            return std::unexpected(BatteryError::CriticalBrownoutRisk);
        }
        return std::unexpected(BatteryError::PassivationUnresolved);
    }

private:
    HAL& hal_;
};
```
:::

### Обробка крайових випадків у польових умовах

У практичній експлуатації автономних датчиків можливі три специфічні сценарії:

1. **Виснаження ресурсу при високій OCV:** Літієві первинні елементи зберігають напругу холостого ходу 3.65 В навіть тоді, коли віддано 95% паспортної ємності. Звичайний замір напруги вольтметром або АЦП без навантаження не показує реального зносу. Тестовий імпульс струму дозволяє своєчасно виявити зростання R_int до сотень Ом і попередити сервер збору даних про необхідність планової заміни джерела живлення за 3–6 місяців до повної відмови.
2. **Низькотемпературна пасивація:** При температурах навколишнього середовища нижче -20 °C іонна провідність електроліту SOCl₂ падає у 3–5 разів. Якщо плівка LiCl вже утворилася, депасивація на морозі потребує більше часу. Алгоритм автоматично збільшує кількість імпульсів, уникаючи фатального збою модему.
3. **Енергетичний баланс депасивації:** Витрата енергії на один повний цикл депасивації становить:
   ```
   E_depass = V * I * t = 3.6 В * 0.036 А * 0.05 с = 0.00648 Дж = 0.0018 мВт·год
   ```
   Проведення такої процедури один раз на добу протягом 10 років забирає всього 6.57 мВт·год, що становить менше 0.07% від загальної ємності елемента типорозміру AA (2600 мА·год · 3.6 В = 9360 мВт·год). Ця мізерна плата енергією на 100% захищає пристрій від непередбачуваних відмов і циклічних перезавантажень.
