# ⚙️ Програмна валідація часових параметрів цифрової шини

Під час розробки високошвидкісних цифрових пристроїв інженери стикаються із завданням верифікації часових параметрів для різних кутів технологічного процесу та умов середовища (англ. *PVT corners: Process, Voltage, Temperature*). Розрахунки вручну в електронних таблицях часто призводять до помилок копіювання параметрів, не враховують комбінацію найшвидшого кута (*Fast-Fast / Low-Temp*, де виникають збої утримання) та найповільнішого кута (*Slow-Slow / High-Temp*, де збоїть встановлення).

Нижче наведено модульний інструмент валідації часового балансу цифрових синхронних інтерфейсів (SPI, QSPI, паралельні шини пам'яті). Програма виконує перевірку запасу встановлення (*setup slack*), запасу утримання (*hold slack*), розраховує час польоту сигналу по провіднику друкованої плати та визначає абсолютну граничну тактову частоту шини.

## 1. Архітектура та математична модель валідатора

Програмний модуль базується на класичній моделі синхронного тракту передачі даних із спільним джерелом тактування (*Common Clock Architecture*). У цій системі тактовий генератор подає сигнал одночасно на передавач (Tx) та приймач (Rx).

Математична модель враховує такі фізичні процеси:
- **Затримка вихідного каскаду передавача:** Моделюється парою значень `t_co_min` (найшвидший відгук у куті Fast-Fast за температури -40 °C та підвищеної напруги) та `t_co_max` (найповільніший відгук у куті Slow-Slow за температури +85 °C / +125 °C та зниженої напруги).
- **Час поширення хвилі по друкованій платі (`t_flight`):** Для мікросмужкової лінії (*microstrip*) на зовнішньому шарі текстоліту FR-4 ефективна діелектрична проникність становить `ε_eff ≈ 3.1...3.4`, що дає питому затримку поширення близько `6.0–6.5 пс/мм`. Для внутрішніх смужкових ліній (*stripline*) діелектрична проникність вища (`ε_r ≈ 4.2`), а затримка зростає до `7.0–7.5 пс/мм`.
- **Вимоги вхідного тригера приймача:** Параметри `t_setup` (мінімальний час попередньої стабільності даних) та `t_hold` (мінімальний час збереження даних після тактового стробу).
- **Похибки тактового дерева:** Перекіс такту `t_skew` (різниця довжин тактових трас до передавача і приймача) та випадковий фазовий джиттер `t_jitter` тактового генератора.

## 2. Програмна реалізація мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Паспортні часові параметри вихідного каскаду передавача (нс) */
typedef struct {
    double t_co_min_ns;  /* Найшвидший відгук (Fast corner / Low Temp) */
    double t_co_max_ns;  /* Найповільніший відгук (Slow corner / High Temp) */
} TransmitterTiming;

/* Паспортні вимоги вхідного тригера приймача (нс) */
typedef struct {
    double t_setup_ns;   /* Мінімально необхідний час встановлення */
    double t_hold_ns;    /* Мінімально необхідний час утримання */
} ReceiverTiming;

/* Фізичні параметри друкованої плати та джерела тактування */
typedef struct {
    double trace_length_mm;  /* Довжина провідника на платі (мм) */
    double ps_per_mm;        /* Питома затримка (FR-4 microstrip: ~6.5 пс/мм) */
    double clock_freq_mhz;   /* Робоча тактова частота (МГц) */
    double clock_skew_ns;    /* Перекіс тактових ліній між чіпами */
    double clock_jitter_ns;  /* Фазове тремтіння тактового сигналу */
} InterconnectParams;

/* Результати розрахунку часового бюджету */
typedef struct {
    double t_flight_ns;       /* Час поширення хвилі по трасі PCB */
    double setup_slack_ns;    /* Запас за часом встановлення */
    double hold_slack_ns;     /* Запас за часом утримання */
    double max_safe_freq_mhz; /* Максимальна розрахункова частота */
    bool setup_passed;        /* Чи виконується вимога встановлення */
    bool hold_passed;         /* Чи виконується вимога утримання */
} TimingResult;

/* Функція обчислення часового бюджету синхронної шини */
TimingResult validate_bus_timing(
    const TransmitterTiming *tx,
    const ReceiverTiming *rx,
    const InterconnectParams *bus
) {
    TimingResult res;
    double t_period_ns = 1000.0 / bus->clock_freq_mhz;
    
    /* 1. Розрахунок часу польоту сигналу: t_flight = length · delay_per_mm */
    res.t_flight_ns = (bus->trace_length_mm * bus->ps_per_mm) / 1000.0;
    
    /* 2. Запас за встановленням:
       Slack = T_clk - (t_co_max + t_flight + t_setup + t_skew + t_jitter) */
    double total_setup_path = tx->t_co_max_ns + res.t_flight_ns + rx->t_setup_ns 
                            + bus->clock_skew_ns + bus->clock_jitter_ns;
    res.setup_slack_ns = t_period_ns - total_setup_path;
    res.setup_passed = (res.setup_slack_ns >= 0.0);
    
    /* 3. Запас за утриманням:
       Slack = (t_co_min + t_flight) - (t_hold + t_skew) */
    double min_data_arrival = tx->t_co_min_ns + res.t_flight_ns;
    double hold_required = rx->t_hold_ns + bus->clock_skew_ns;
    res.hold_slack_ns = min_data_arrival - hold_required;
    res.hold_passed = (res.hold_slack_ns >= 0.0);
    
    /* 4. Теоретична максимальна частота, обмежена встановленням */
    if (total_setup_path > 0.0) {
        res.max_safe_freq_mhz = 1000.0 / total_setup_path;
    } else {
        res.max_safe_freq_mhz = 0.0;
    }
    
    return res;
}

int main(void) {
    /* Тестовий випадок: SPI NOR Flash W25Q128JV та мікроконтролер STM32H7 */
    TransmitterTiming flash_tx = {
        .t_co_min_ns = 1.5,
        .t_co_max_ns = 7.0
    };
    
    ReceiverTiming mcu_rx = {
        .t_setup_ns = 3.5,
        .t_hold_ns = 1.0
    };
    
    InterconnectParams pcb = {
        .trace_length_mm = 80.0,
        .ps_per_mm = 6.5,
        .clock_freq_mhz = 60.0,
        .clock_skew_ns = 0.4,
        .clock_jitter_ns = 0.3
    };
    
    TimingResult r = validate_bus_timing(&flash_tx, &mcu_rx, &pcb);
    
    printf("=== ВАЛІДАЦІЯ ЧАСОВОГО БЮДЖЕТУ ШИНИ (C) ===\n");
    printf("Затримка траси плати:       %.3f нс\n", r.t_flight_ns);
    printf("Запас Setup (встановлення): %.3f нс [%s]\n", 
           r.setup_slack_ns, r.setup_passed ? "PASS" : "FAIL");
    printf("Запас Hold (утримання):     %.3f нс [%s]\n", 
           r.hold_slack_ns, r.hold_passed ? "PASS" : "FAIL");
    printf("Максимальна частота шини:   %.2f МГц\n", r.max_safe_freq_mhz);
    
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <format>
#include <expected>
#include <array>

namespace timing {

struct TransmitterSpec {
    double t_co_min_ns;  // Fast-corner output delay
    double t_co_max_ns;  // Slow-corner output delay
};

struct ReceiverSpec {
    double t_setup_ns;   // Required input setup time
    double t_hold_ns;    // Required input hold time
};

struct InterconnectSpec {
    double trace_length_mm{50.0};
    double ps_per_mm{6.5};       // FR-4 microstrip delay: ~6.5 ps/mm
    double clock_freq_mhz{50.0};
    double clock_skew_ns{0.3};
    double clock_jitter_ns{0.2};
};

struct ValidationReport {
    double flight_time_ns;
    double setup_slack_ns;
    double hold_slack_ns;
    double max_safe_freq_mhz;
    bool setup_ok;
    bool hold_ok;
};

enum class TimingError {
    InvalidFrequency,
    NegativeDelayParameter
};

class BusTimingValidator {
public:
    [[nodiscard]] static constexpr std::expected<ValidationReport, TimingError> validate(
        const TransmitterSpec& tx,
        const ReceiverSpec& rx,
        const InterconnectSpec& bus
    ) noexcept {
        if (bus.clock_freq_mhz <= 0.0) {
            return std::unexpected(TimingError::InvalidFrequency);
        }
        if (tx.t_co_min_ns < 0.0 || tx.t_co_max_ns < 0.0 || 
            rx.t_setup_ns < 0.0 || rx.t_hold_ns < 0.0) {
            return std::unexpected(TimingError::NegativeDelayParameter);
        }

        const double t_period_ns = 1000.0 / bus.clock_freq_mhz;
        const double t_flight_ns = (bus.trace_length_mm * bus.ps_per_mm) / 1000.0;

        // Бюджет встановлення (Setup Budget)
        const double total_setup_path = tx.t_co_max_ns + t_flight_ns + rx.t_setup_ns 
                                      + bus.clock_skew_ns + bus.clock_jitter_ns;
        const double setup_slack = t_period_ns - total_setup_path;

        // Бюджет утримання (Hold Budget)
        const double min_arrival = tx.t_co_min_ns + t_flight_ns;
        const double hold_required = rx.t_hold_ns + bus.clock_skew_ns;
        const double hold_slack = min_arrival - hold_required;

        const double max_freq = (total_setup_path > 0.0) ? (1000.0 / total_setup_path) : 0.0;

        return ValidationReport{
            .flight_time_ns = t_flight_ns,
            .setup_slack_ns = setup_slack,
            .hold_slack_ns = hold_slack,
            .max_safe_freq_mhz = max_freq,
            .setup_ok = (setup_slack >= 0.0),
            .hold_ok = (hold_slack >= 0.0)
        };
    }
};

} // namespace timing

int main() {
    using namespace timing;

    constexpr TransmitterSpec flash_tx{
        .t_co_min_ns = 1.5,
        .t_co_max_ns = 7.0
    };

    constexpr ReceiverSpec mcu_rx{
        .t_setup_ns = 3.5,
        .t_hold_ns = 1.0
    };

    constexpr InterconnectSpec pcb{
        .trace_length_mm = 80.0,
        .ps_per_mm = 6.5,
        .clock_freq_mhz = 60.0,
        .clock_skew_ns = 0.4,
        .clock_jitter_ns = 0.3
    };

    const auto result = BusTimingValidator::validate(flash_tx, mcu_rx, pcb);

    if (!result) {
        std::cerr << "Помилка валідації параметрів шини!\n";
        return 1;
    }

    const auto& report = *result;
    std::cout << "=== ВАЛІДАЦІЯ ЧАСОВОГО БЮДЖЕТУ ШИНИ (C++20) ===\n";
    std::cout << std::format("Затримка траси плати:       {:.3f} нс\n", report.flight_time_ns);
    std::cout << std::format("Запас Setup (встановлення): {:.3f} нс [{}]\n", 
                             report.setup_slack_ns, report.setup_ok ? "PASS" : "FAIL");
    std::cout << std::format("Запас Hold (утримання):     {:.3f} нс [{}]\n", 
                             report.hold_slack_ns, report.hold_ok ? "PASS" : "FAIL");
    std::cout << std::format("Максимальна частота шини:   {:.2f} МГц\n", report.max_safe_freq_mhz);

    return 0;
}
```
:::

## 3. Інженерний аналіз та сценарії усунення збоїв

### Аналіз кутів середовища (Corner Analysis)
При розрахунку не можна використовувати типові значення з даташитів. Повноцінний інженерний аналіз вимагає перевірки двох діаметрально протилежних кутів:

1. **Найповільніший режим (Slow-Slow Corner):**
   Мінімальна напруга живлення (наприклад, 3.0 В замість 3.3 В) та максимальна температура (+85 °C або +125 °C). У цьому стані затримка `t_co_max` максимальна, а час польоту `t_flight` зростає через зниження крутизни фронтів. Це найкритичніша точка для перевірки **часу встановлення (Setup)**. Якщо за таких умов `setup_slack < 0`, дані надходять із запізненням.

2. **Найшвидший режим (Fast-Fast Corner):**
   Максимальна напруга живлення (3.6 В) та мінімальна робоча температура (-40 °C). Транзистори відкриваються надзвичайно швидко, затримка `t_co_min` падає до мінімуму. Це найнебезпечніша точка для виникнення **збоїв утримання (Hold Violation)**, оскільки новий стан даних може знищити попередній біт до завершення його фіксації.

### Що робити при виявленні негативного запасу встановлення (`setup_slack < 0`):
- **Знизити тактову частоту шини:** Найпростіший програмний спосіб. Збільшення періоду `T_clk` безпосередньо збільшує бюджет встановлення.
- **Увімкнути зсув фази вибірки такту:** Багато сучасних мікроконтролерів (STM32H7, NXP i.MX RT, ESP32-S3) мають вбудовані апаратні блоки фазового зсуву такту (блок затримки DLYB або налаштування вибірки по протилежному напівперіоду). Зсув тактового стробу на 2–4 нс вперед компенсує затримку пам'яті.
- **Зменшити ємнісне навантаження лінії:** Скоротити довжину провідників друкованої плати, зменшити кількість перехідних отворів (кожен отвір додає 0.5–1.0 пФ ємності), оптимізувати ширину траси під хвильовий опір 50 Ом.
- **Застосувати мікросхеми вищої градації швидкості (*speed grade*):** Наприклад, перейти з чіпів пам'яті з індексом 85 МГц на версії з індексом 133 МГц, у яких внутрішня затримка `t_co` скорочена з 9.5 нс до 6.0 нс.

### Що робити при виявленні порушення утримання (`hold_slack < 0`):
- **Увага: Зниження частоти не допоможе!** Порушення утримання залежить виключно від різниці затримок усередині одного тактового фронту і зберігається навіть на частоті 1 кГц.
- **Фізично подовжити трасу лінії даних на платі:** Прокласти меандр (*serpentine routing*) на лінії даних для штучного збільшення затримки `t_flight`.
- **Встановити послідовний демпферний резистор:** Резистор номіналом 22–47 Ом, встановлений безпосередньо біля виводу передавача, сповільнює крутизну наростання фронту, збільшуючи час наростання та затримку початку спаду сигналу.
- **Задіяти внутрішні налаштування затримки вхідних буферів:** В FPGA (Xilinx IODELAY, Intel I/O Elements) або мікроконтролерах можна програмно активувати додаткові лінії затримки на входах GPIO.

## 4. Інтеграція валідатора в конвеєр розробки (CI/CD)

У промисловому проєктуванні цей валідатор можна скомпілювати як консольну утиліту для автоматичної перевірки переліку елементів (BOM, Bill of Materials) перед запуском друкованих плат у виробництво.

Коли інженер змінює постачальника мікросхеми Flash-пам'яті або змінює топологію трасування шини в САПР (KiCad, Altium Designer), скрипт автоматично витягує оновлені довжини провідників із файлу плати, завантажує граничні часові параметри з бази компонентів і генерує звіт про стан часових запасів. Це унеможливлює передачу у виробництво плат із прихованими дефектами гонок або порушень часу встановлення.
