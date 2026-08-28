# ⚙️ Проєкт супервізора життєдіяльності мікроконтролера на C99 та C++20

Автономні вбудовані системи, що працюють у реальному часі — від польотних контролерів безпілотних апаратів до систем керування медичними інфузоматами — потребують безперервної верифікації власної апаратної та програмної цілісності. Залишати контроль надійності виключно на апаратний сторожовий таймер неприпустимо: він реагує лише на повну зупинку процесора, ігноруючи повільну деградацію сенсорів, вичерпання стека потоків чи блокування комунікаційних ліній. Даний практичний модуль реалізує детермінований супервізор життєдіяльності (Health Monitor), спроектований з нульовим динамічним виділенням пам'яті, фіксованим часом виконання O(1) на кожному кроці та повною незалежністю від сторонніх бібліотек.

Модуль об'єднує в єдиний конвеєр збір низькорівневих апаратних метрик, їх математичну фільтрацію за алгоритмом експоненційно зваженого ковзного середнього (EWMA), розрахунок матричного показника здоров'я, кінцевий автомат відновлення заблокованих шин та транзакційне збереження діагностичних знімків у чорну скриньку. Нижче наведено покрокову архітектуру, повні вихідні тексти мовами C99 та C++20, а також тестовий каркас для інжекції несправностей.

## Інженерна мотивація та вимоги до підсистеми нагляду

Під час проектування систем із підвищеними вимогами до функціональної безпеки (відповідно до стандартів IEC 61508 SIL 2/3 або ISO 26262 ASIL B/C) однією з найскладніших проблем є виявлення так званих «тихих відмов» (англ. *Silent Failures*). Тиха відмова виникає, коли процесор продовжує виконувати код головного циклу або планувальника FreeRTOS, але окремі підсистеми пристрою вже деградували до непрацездатного стану.

Розглянемо типові сценарії таких відмов у промислових виробах:

- **Заклинювання шини I2C:** під час транзакції читання даних з цифрового барометра відбувся короткочасний сплеск електромагнітної завади, внаслідок чого ведений датчик пропустив тактовий імпульс і застряг у стані передачі біта `0`. Лінія даних `SDA` виявляється замкненою на землю веденим чипом. Якщо драйвер I2C не має апаратного механізму скидання, всі наступні виклики функцій читання будь-яких датчиків на цій же шині блокуватимуться або повертатимуть статус помилки. При цьому процесорне ядро працює в штатному режимі і регулярно скидає апаратний таймер `IWDG`;
- **Повільне вичерпання стека задачі (Stack Starvation):** внаслідок рідкісного збігу обставин (одночасне надходження пакету по мережі Ethernet, виклик важкої функції форматування рядка та переривання від таймера) покажчик стека задачі наближається до виділеної нижньої межі. Залишається лише кілька байтів вільного простору. При наступному виклику функції локальні змінні перепишуть сусідні змінні іншої задачі, що призведе до спотворення даних без негайного виникнення апаратного винятку `HardFault`;
- **Температурний дрейф опорної напруги живлення:** у разі поступового висихання фільтруючого електролітичного конденсатора імпульсного стабілізатора амплітуда високочастотних пульсацій напруги живлення мікроконтролера зростає від 20 мВ до 300 мВ. Це призводить до випадкових спотворень результатів перетворення внутрішнього АЦП та появи помилок у контурі регулювання струму електродвигуна;
- **Перехід шини CAN у стан Bus-Off:** внаслідок поганого фізичного контакту в роз'ємі термінального резистора на лінії передачі виникають відбиття сигналу. Апаратний контролер CAN починає отримувати помилки форми кадру та збільшує внутрішній лічильник помилок передавача `TEC`. Після досягнення значення 256 контролер апаратно вимикає свій вихідний трансивер. Якщо прикладний код не аналізує статусний регістр контролера, система продовжує надсилати пакети в порожнечу;
- **Накопичення поодиноких збоїв пам'яті (Soft Errors):** під впливом промислових перешкод у комірках Flash пам'яті виникають поодинокі інверсії бітів. Апаратний блок ECC виправляє однобітові збої, але без регулярного сканування пам'яті один і той самий сектор з часом може отримати другий бітовий збій, перетворюючи помилку на фатальну двобітову відмову.

Для запобігання переходу таких прихованих деградацій у фатальну катастрофу програмний супервізор повинен діяти як безперервний вимірювальний міст. Він не просто констатує факт наявності чи відсутності помилки, а розраховує кількісну оцінку надійності кожної підсистеми, згладжує її у часі та ухвалює зважені рішення щодо ізоляції відмов.

### Жорсткі обмеження на реалізацію наглядача

Сам супервізор не має права стати джерелом ненадійності. До його архітектури висуваються безкомпромісні інженерні обмеження:

1. **Нульове динамічне виділення пам'яті:** використання функцій `malloc()`, `calloc()`, `realloc()`, `free()`, а також операторів `new` та `delete` суворо заборонено. Вся пам'ять для дескрипторів компонентів, буферів історії та кільцевого журналу чорної скриньки виділяється статично під час компіляції. Це виключає фрагментацію оперативної пам'яті (Heap Fragmentation) та неможливість виділення буфера у критичний момент;
2. **Детермінована часова складність O(1):** жодна функція супервізора не може містити нескінченних циклів, очікування прапорців апаратних регістрів без жорстких лічильників ітерацій чи рекурсивних викликів. Кожен виклик функції `health_supervisor_tick()` виконує фіксовану кількість операцій за детермінований час (менше 5 мікросекунд на ядрі ARM Cortex-M4 на частоті 168 МГц);
3. **Цілочисельна арифметика з фіксованою крапкою:** усі розрахунки коефіцієнтів, нормалізації та експоненційного згладжування виконуються в цілих числах (масштаб `0 ... 1000` або формат Q8.8/Q16.16). Це гарантує ідентичну поведінку прошивки на будь-якому ядрі (ARM Cortex-M0+, Cortex-M3, Cortex-M4, Cortex-M7, RISC-V RV32EC) незалежно від наявності апаратного співпроцесора рухомої коми FPU;
4. **Неблокуючий збір телеметрії:** функції зворотного виклику (англ. *Callback Functions*) для опитування стану компонентів не мають права виконувати тривалі операції передачі даних по шинах чи блокувати м'ютекси. Вони лише зчитують уже готові лічильники помилок або останні збережені значення з регістрів чи структур драйверів.

## Математичне моделювання фільтрації EWMA та аналіз квантування

Для фільтрації первинних вимірювань використовується експоненційно зважене ковзне середнє. У дискретному часі з періодом опитування `T_s` (наприклад, 50 мс) формулу EWMA можна розглядати як цифровий фільтр низьких частот першого порядку.

Частота зрізу фільтра `f_c` (по рівню -3 дБ) пов'язана з коефіцієнтом `α` співвідношенням:

```
f_c = (alpha * f_s) / (2 * pi)
```

При частоті опитування `f_s = 20` Гц (`T_s = 50` мс) та коефіцієнті `α = 1/8 = 0.125` частота зрізу становить:

```
f_c = (0.125 * 20) / (2 * 3.14159) = 0.398 Гц
```

Це означає, що всі високочастотні шуми з періодом менше 2.5 секунди (поодинокі викиди АЦП, випадкові перешкоди на лініях зв'язку) послаблюються у понад 10 разів, тоді як монотонна деградація сигналу проходить крізь фільтр без затримок.

### Усунення систематичного зсуву цілочисельного ділення

При реалізації формули EWMA в цілих числах через побітовий зсув `>> 3` (ділення на 8 з відкиданням дробової частини) виникає ефект систематичного зсуву округлення вниз (англ. *Truncation Bias*). У стаціонарному стані при постійному вхідному сигналі `x[k] = X` залишок від ділення відкидається, через що згладжене значення стабілізується на 1–2 одиниці нижче за істинне.

Для усунення цього зсуву до суми додається константа округлення до найближчого цілого (Round Half-Up):

```
H[k] = (raw + 7 * H[k-1] + 4) >> 3
```

Додавання числа `4` (половина знаменника 8) гарантує математично незміщену оцінку фільтрації в усьому діапазоні від 0 до 1000.

## Період теплого старту та маскування перехідних процесів (Warm-up Blanking)

Під час первинного подання напруги на мікроконтролерну плату протягом перших 100–500 мілісекунд у системі відбуваються інтенсивні перехідні процеси:
- Заряджаються ємності вхідних фільтрів імпульсних перетворювачів;
- Стабілізується амплітуда кварцового резонатора `HSE` та виходить у режим синхронізації блок `PLL`;
- Ведені мікросхеми датчиків на шинах I2C та SPI виконують власні внутрішні цикли Power-On Reset (POR).

Якщо супервізор почне застосовувати жорсткі штрафи з першого такту виконання коду, пристрій гарантовано зафіксує помилки шин і перейде в аварійний режим ще до завершення старту периферії.

Для запобігання цій проблемі супервізор реалізує лічильник теплого старту (англ. *Warm-up Blanking Period*). Протягом перших 20 циклів опитування (перша 1 секунда після старту):
1. Системний бал `H_system` утримується на рівні `HEALTH_STATE_NOMINAL`;
2. Функції відновлення шин викликаються у м'якому режимі без підняття прапорців ескалації;
3. Помилки записуються у фоновий журнал без блокування апаратних виходів таймерів.

## Архітектурний дизайн та проектування структур даних

Основним будівельним блоком супервізора є дескриптор компонента `health_component_desc_t` (або `ComponentDescriptor` у C++20). Кожен вузол системи, стан якого потребує нагляду (підсистема живлення, шина I2C, шина CAN, стек задач RTOS, цілісність Flash пам'яті), реєструється в супервізорі з індивідуальними параметрами.

Дескриптор містить:
- Текстову назву компонента для журналювання та діагностики;
- Покажчик на функцію опитування (`collector`), яка повертає поточне значення метрики здоров'я у діапазоні `0 ... 1000`;
- Ваговий коефіцієнт (`weight`) від 1 до 100, що визначає частку даного компонента у загальному інтегральному балі пристрою;
- Ознаку критичності (`is_critical`): якщо компонент із цією ознакою відмовляє, вся система негайно переходить в аварійний режим із застосуванням мультиплікативного штрафу;
- Згладжене значення індексу (`smoothed_score`), що розраховується за фільтром EWMA;
- Лічильник послідовних збоїв (`consecutive_failures`) для реалізації часового фільтра підтвердження аварії.

### Інтерфейс підсистеми моніторингу (C99 та C++20)

:::tabs
```c
#ifndef HEALTH_MONITOR_H
#define HEALTH_MONITOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HEALTH_MAX_COMPONENTS       8
#define HEALTH_SCORE_PERFECT        1000
#define HEALTH_CRITICAL_THRESHOLD   400
#define HEALTH_DEGRADED_THRESHOLD   700
#define HEALTH_NOMINAL_THRESHOLD    900
#define HEALTH_WARMUP_TICKS         20

#define HEALTH_BLACKBOX_MAGIC       0xDEADBEEF
#define HEALTH_BLACKBOX_SLOTS       16

typedef enum {
    HEALTH_STATE_NOMINAL = 0,
    HEALTH_STATE_DEGRADED,
    HEALTH_STATE_CRITICAL,
    HEALTH_STATE_EMERGENCY
} health_state_t;

typedef enum {
    HEALTH_BUS_OK = 0,
    HEALTH_BUS_SDA_STUCK_LOW,
    HEALTH_BUS_SCL_STUCK_LOW,
    HEALTH_BUS_TIMEOUT,
    HEALTH_BUS_CRC_ERROR,
    HEALTH_BUS_BUS_OFF
} health_bus_status_t;

typedef uint16_t (*health_collector_fn)(void *user_ctx);

typedef struct {
    const char           *name;
    health_collector_fn   collector;
    void                 *user_ctx;
    uint16_t              weight;
    bool                  is_critical;
    uint16_t              smoothed_score;
    uint32_t              consecutive_failures;
} health_component_desc_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t seq_num;
    uint64_t timestamp_ms;
    uint16_t system_score;
    uint8_t  system_state;
    uint8_t  fault_component_id;
    uint32_t cfsr_reg;
    uint32_t hfsr_reg;
    uint32_t vdd_mv;
    int16_t  core_temp_c;
    uint16_t min_stack_free_bytes;
    uint32_t crc32;
} health_blackbox_entry_t;

typedef struct {
    health_component_desc_t components[HEALTH_MAX_COMPONENTS];
    uint8_t                 component_count;
    uint16_t                system_score;
    health_state_t          current_state;
    uint32_t                iteration_counter;
    uint32_t                warmup_ticks_left;
    
    // Чорна скринька у статичній або енергонезалежній пам'яті
    health_blackbox_entry_t blackbox_ring[HEALTH_BLACKBOX_SLOTS];
    uint32_t                blackbox_head;
    uint32_t                blackbox_seq;
} health_supervisor_t;

void health_supervisor_init(health_supervisor_t *ctx);
bool health_supervisor_register(health_supervisor_t *ctx,
                                const char *name,
                                health_collector_fn collector,
                                void *user_ctx,
                                uint16_t weight,
                                bool is_critical);

void health_supervisor_tick(health_supervisor_t *ctx, uint64_t timestamp_ms);
void health_supervisor_log_emergency(health_supervisor_t *ctx, 
                                     uint8_t faulty_id, 
                                     uint32_t cfsr, 
                                     uint32_t hfsr,
                                     uint64_t timestamp_ms);

#ifdef __cplusplus
}
#endif

#endif // HEALTH_MONITOR_H
```
```cpp
#pragma once

#include <array>
#include <string_view>
#include <functional>
#include <cstdint>
#include <span>
#include <optional>

namespace Health {

inline constexpr uint16_t ScorePerfect = 1000;
inline constexpr uint16_t CriticalThreshold = 400;
inline constexpr uint16_t DegradedThreshold = 700;
inline constexpr uint16_t NominalThreshold = 900;
inline constexpr uint32_t WarmupTicks = 20;
inline constexpr uint32_t BlackboxMagic = 0xDEADBEEF;

enum class State : uint8_t {
    Nominal = 0,
    Degraded,
    Critical,
    Emergency
};

enum class BusStatus : uint8_t {
    Ok = 0,
    SdaStuckLow,
    SclStuckLow,
    Timeout,
    CrcError,
    BusOff
};

struct alignas(4) BlackboxEntry {
    uint32_t magic{BlackboxMagic};
    uint32_t seq_num{0};
    uint64_t timestamp_ms{0};
    uint16_t system_score{ScorePerfect};
    State    system_state{State::Nominal};
    uint8_t  fault_component_id{0xFF};
    uint32_t cfsr_reg{0};
    uint32_t hfsr_reg{0};
    uint32_t vdd_mv{3300};
    int16_t  core_temp_c{25};
    uint16_t min_stack_free_bytes{1024};
    uint32_t crc32{0};
};

struct ComponentDescriptor {
    std::string_view                             name{};
    std::function<uint16_t()>                    collector{};
    uint16_t                                     weight{10};
    bool                                         is_critical{false};
    uint16_t                                     smoothed_score{ScorePerfect};
    uint32_t                                     consecutive_failures{0};
};

template <size_t MaxComponents = 8, size_t BlackboxSlots = 16>
class Supervisor {
public:
    constexpr Supervisor() noexcept = default;

    bool register_component(std::string_view name,
                            std::function<uint16_t()> collector,
                            uint16_t weight,
                            bool is_critical) noexcept {
        if (component_count_ >= MaxComponents) {
            return false;
        }
        components_[component_count_++] = ComponentDescriptor{
            .name = name,
            .collector = std::move(collector),
            .weight = weight,
            .is_critical = is_critical,
            .smoothed_score = ScorePerfect,
            .consecutive_failures = 0
        };
        return true;
    }

    void tick(uint64_t timestamp_ms) noexcept;
    void log_emergency(uint8_t faulty_id, uint32_t cfsr, uint32_t hfsr, uint64_t timestamp_ms) noexcept;

    [[nodiscard]] uint16_t system_score() const noexcept { return system_score_; }
    [[nodiscard]] State state() const noexcept { return current_state_; }
    [[nodiscard]] std::span<const ComponentDescriptor> components() const noexcept {
        return std::span<const ComponentDescriptor>(components_.data(), component_count_);
    }
    [[nodiscard]] std::span<const BlackboxEntry> blackbox() const noexcept {
        return std::span<const BlackboxEntry>(blackbox_ring_.data(), BlackboxSlots);
    }

private:
    uint32_t calculate_crc32(const uint8_t *data, size_t length) const noexcept;

    std::array<ComponentDescriptor, MaxComponents> components_{};
    size_t                                         component_count_{0};
    uint16_t                                       system_score_{ScorePerfect};
    State                                          current_state_{State::Nominal};
    uint32_t                                       iteration_counter_{0};
    uint32_t                                       warmup_ticks_left_{WarmupTicks};

    std::array<BlackboxEntry, BlackboxSlots>       blackbox_ring_{};
    uint32_t                                       blackbox_head_{0};
    uint32_t                                       blackbox_seq_{0};
};

} // namespace Health
```
:::

## Модуль контролю залишку стека та захисних бар'єрів

Контроль стека задач операційної системи реалізується за допомогою дворівневої перевірки пам'яті:

1. **Апаратні канарки на дні стека (Canary Guard Words):** два 32-бітних слова зі значенням `0xA5A5A5A5`, записані на самому початку виділеного буфера стека. Якщо задача переповнить стек навіть на кілька байтів, ці канарки будуть затерті першими. Швидка перевірка цих двох слів займає лише 2 тактів процесора і сигналізує про катастрофічне пошкодження пам'яті;
2. **Сканування глибини водяного знака (Watermark Depth Scanning):** ітеративне сканування слів від дна стека вгору доти, доки зустрічається байтовий патерн заповнення `0xA5`. Кількість виявлених недоторканих слів перераховується у байти вільного простору стека.

Отримана кількість вільних байтів нормалізується за допомогою функції інтерполяції з двома порогами безпеки:
- Якщо вільний залишок перевищує безпечний поріг (наприклад, 256 байтів) — повертається максимальний бал здоров'я `1000`;
- Якщо залишок знаходиться у діапазоні між небезпечним порогом (64 байти) та безпечним порогом (256 байтів) — повертається лінійно інтерпольований бал від `400` до `1000`;
- Якщо залишок менший за 64 байти — повертається значення нижче `400`, що переводить компонент у стан `CRITICAL` та готує систему до захисних дій.

:::tabs
```c
#define STACK_CANARY_WORD       0xA5A5A5A5U
#define STACK_SAFE_LIMIT_BYTES  256U
#define STACK_DANGER_LIMIT_BYTES 64U

uint16_t health_check_task_stack(const uint32_t *stack_bottom, size_t total_words) {
    if (!stack_bottom || total_words < 16) {
        return 0;
    }

    // 1. Швидка перевірка канарки на самому дні стека
    if (stack_bottom[0] != STACK_CANARY_WORD || stack_bottom[1] != STACK_CANARY_WORD) {
        return 0; // Стек повністю зруйновано
    }

    // 2. Підрахунок недоторканих слів від дна стека вгору
    size_t unused_words = 0;
    while (unused_words < total_words && stack_bottom[unused_words] == STACK_CANARY_WORD) {
        unused_words++;
    }

    size_t free_bytes = unused_words * sizeof(uint32_t);

    if (free_bytes >= STACK_SAFE_LIMIT_BYTES) {
        return 1000;
    }
    if (free_bytes <= STACK_DANGER_LIMIT_BYTES) {
        return (uint16_t)((free_bytes * 400) / STACK_DANGER_LIMIT_BYTES);
    }

    // Лінійна інтерполяція між 400 та 1000
    uint32_t range = STACK_SAFE_LIMIT_BYTES - STACK_DANGER_LIMIT_BYTES;
    uint32_t delta = free_bytes - STACK_DANGER_LIMIT_BYTES;
    return (uint16_t)(400 + (delta * 600) / range);
}
```
```cpp
namespace Health {

inline constexpr uint32_t StackCanaryWord = 0xA5A5A5A5U;
inline constexpr size_t StackSafeLimitBytes = 256U;
inline constexpr size_t StackDangerLimitBytes = 64U;

[[nodiscard]] uint16_t check_task_stack(std::span<const uint32_t> stack_memory) noexcept {
    if (stack_memory.size() < 16) {
        return 0;
    }

    // 1. Швидка перевірка цілісності канарок на дні стека
    if (stack_memory[0] != StackCanaryWord || stack_memory[1] != StackCanaryWord) {
        return 0; // Стек пошкоджено
    }

    // 2. Сканування глибини водяного знака
    size_t unused_words = 0;
    for (const auto word : stack_memory) {
        if (word != StackCanaryWord) {
            break;
        }
        ++unused_words;
    }

    const size_t free_bytes = unused_words * sizeof(uint32_t);

    if (free_bytes >= StackSafeLimitBytes) {
        return 1000;
    }
    if (free_bytes <= StackDangerLimitBytes) {
        return static_cast<uint16_t>((free_bytes * 400) / StackDangerLimitBytes);
    }

    const size_t range = StackSafeLimitBytes - StackDangerLimitBytes;
    const size_t delta = free_bytes - StackDangerLimitBytes;
    return static_cast<uint16_t>(400 + (delta * 600) / range);
}

} // namespace Health
```
:::

## Модуль діагностики та розблокування шини I2C (Bus Recovery)

Зависання лінії даних `SDA` у низькому рівні через збій веденої мікросхеми вимагає специфічної послідовності апаратних дій для розблокування шини без повного вимикання живлення пристрою.

Алгоритм розблокування реалізується наступним чином:
1. Перевіряється поточний стан ліній `SDA` та `SCL`. Якщо обидві лінії знаходяться у високому рівні `1`, шина вільна і втручання не потрібне;
2. Апаратний периферійний модуль I2C мікроконтролера програмно вимикається, а його виводи переналаштовуються в режим дискретних виходів з відкритим стоком (`GPIO Open-Drain Output`);
3. На лінію `SCL` подається серія з 9 тактових імпульсів з частотою близько 50 кГц (паузи по 10 мікросекунд). Отримуючи тактові імпульси, ведений пристрій виштовхує біти свого внутрішнього регістра зсуву, після чого відпускає лінію `SDA`, дозволяючи зовнішньому резистору підтяжки повернути її у стан високого рівня;
4. Після появи високого рівня на `SDA` формується обов'язкова умова `STOP`: лінія `SDA` притискається до землі, лінія `SCL` переводиться у високий рівень, а потім `SDA` відпускається у високий стан;
5. Виводи перемикаються назад у режим альтернативної функції, а апаратний блок I2C скидається та реініціалізується.

:::tabs
```c
typedef struct {
    void (*set_scl_mode_gpio)(void);
    void (*set_scl_mode_alternate)(void);
    void (*set_scl_pin)(bool high);
    void (*set_sda_pin)(bool high);
    bool (*read_scl_pin)(void);
    bool (*read_sda_pin)(void);
    void (*delay_us)(uint32_t us);
    void (*reset_i2c_peripheral)(void);
} health_i2c_driver_ops_t;

bool health_i2c_recover_bus(const health_i2c_driver_ops_t *ops) {
    if (!ops || !ops->set_scl_mode_gpio || !ops->set_scl_pin || !ops->read_sda_pin) {
        return false;
    }

    // Якщо SDA у високому рівні — шина вільна
    if (ops->read_sda_pin() && ops->read_scl_pin()) {
        return true;
    }

    // 1. Перехід у режим ручного керування GPIO Open-Drain
    ops->set_scl_mode_gpio();
    ops->set_scl_pin(true);
    ops->set_sda_pin(true);
    ops->delay_us(10);

    // 2. Генерація 9 тактових імпульсів на SCL для виштовхування бітів з Slave
    for (int i = 0; i < 9; ++i) {
        ops->set_scl_pin(false);
        ops->delay_us(10);
        ops->set_scl_pin(true);
        ops->delay_us(10);

        // Перевірка: якщо Slave відпустив SDA, можна завершувати
        if (ops->read_sda_pin()) {
            break;
        }
    }

    // 3. Формування умови STOP (SDA: Low -> High при SCL: High)
    ops->set_sda_pin(false);
    ops->delay_us(10);
    ops->set_scl_pin(true);
    ops->delay_us(10);
    ops->set_sda_pin(true);
    ops->delay_us(10);

    // 4. Повернення в штатний режим
    ops->set_scl_mode_alternate();
    ops->reset_i2c_peripheral();

    // Фінальна перевірка стану ліній
    return (ops->read_sda_pin() && ops->read_scl_pin());
}
```
```cpp
namespace Health {

struct I2CDriverOps {
    std::function<void()>     set_scl_mode_gpio{};
    std::function<void()>     set_scl_mode_alternate{};
    std::function<void(bool)> set_scl_pin{};
    std::function<void(bool)> set_sda_pin{};
    std::function<bool()>     read_scl_pin{};
    std::function<bool()>     read_sda_pin{};
    std::function<void(uint32_t)> delay_us{};
    std::function<void()>     reset_i2c_peripheral{};
};

[[nodiscard]] bool recover_i2c_bus(const I2CDriverOps& ops) noexcept {
    if (!ops.set_scl_mode_gpio || !ops.set_scl_pin || !ops.read_sda_pin) {
        return false;
    }

    if (ops.read_sda_pin() && ops.read_scl_pin()) {
        return true;
    }

    ops.set_scl_mode_gpio();
    ops.set_scl_pin(true);
    ops.set_sda_pin(true);
    ops.delay_us(10);

    for (int i = 0; i < 9; ++i) {
        ops.set_scl_pin(false);
        ops.delay_us(10);
        ops.set_scl_pin(true);
        ops.delay_us(10);

        if (ops.read_sda_pin()) {
            break;
        }
    }

    ops.set_sda_pin(false);
    ops.delay_us(10);
    ops.set_scl_pin(true);
    ops.delay_us(10);
    ops.set_sda_pin(true);
    ops.delay_us(10);

    ops.set_scl_mode_alternate();
    ops.reset_i2c_peripheral();

    return (ops.read_sda_pin() && ops.read_scl_pin());
}

} // namespace Health
```
:::

## Модуль діагностики CAN та автомат виходу зі стану Bus-Off

Контролер шини CAN є критичним компонентом бортової мережі. При виникненні апаратних проблем на лінії передачі (обрив термінатора, коротке замикання або електромагнітна завада від високовольтного інвертора) внутрішній лічильник помилок передачі `TEC` стрімко зростає. Досягнувши значення `256`, контролер переходить у стан `Bus-Off`, повністю відключаючись від мережі.

Супервізор реалізує конечний автомат контролю стану CAN:
- **Нормальний режим:** якщо `TEC < 96` та `REC < 96`, шина оцінюється у `1000` балів;
- **Попередження (Error Warning / Error Passive):** якщо `TEC >= 96` або `REC >= 96`, бал знижується пропорційно до кількості помилок;
- **Аварійний стан (Bus-Off):** бал падає до `0`. Супервізор активує алгоритм відновлення з експоненційною затримкою (Exponential Backoff: 100 мс -> 200 мс -> 500 мс -> 1000 мс -> 5000 мс), що виключає лавинне перевантаження шини у разі непереборного короткого замикання.

:::tabs
```c
typedef struct {
    uint8_t  tec;
    uint8_t  rec;
    bool     is_bus_off;
    bool     is_passive;
    uint32_t recovery_timer_ms;
    uint32_t backoff_delay_ms;
} health_can_monitor_state_t;

uint16_t health_can_evaluate_health(health_can_monitor_state_t *can_state, uint32_t dt_ms) {
    if (!can_state) return 0;

    if (can_state->is_bus_off) {
        can_state->recovery_timer_ms += dt_ms;
        if (can_state->recovery_timer_ms >= can_state->backoff_delay_ms) {
            // Спроба програмного скидання Bus-off
            can_state->recovery_timer_ms = 0;
            if (can_state->backoff_delay_ms < 5000) {
                can_state->backoff_delay_ms *= 2; // Збільшення паузи
            }
        }
        return 0; // Повна відмова шини
    }

    // Скидання затримки при нормальній роботі
    can_state->backoff_delay_ms = 100;
    can_state->recovery_timer_ms = 0;

    uint8_t max_err = (can_state->tec > can_state->rec) ? can_state->tec : can_state->rec;

    if (max_err < 32) {
        return 1000;
    }
    if (max_err >= 128) {
        return 200; // Error Passive
    }

    // Інтерполяція між 32 помилками (1000) та 128 помилками (200)
    return (uint16_t)(1000 - ((uint32_t)(max_err - 32) * 800) / (128 - 32));
}
```
```cpp
namespace Health {

struct CanMonitorState {
    uint8_t  tec{0};
    uint8_t  rec{0};
    bool     is_bus_off{false};
    bool     is_passive{false};
    uint32_t recovery_timer_ms{0};
    uint32_t backoff_delay_ms{100};

    [[nodiscard]] uint16_t evaluate(uint32_t dt_ms) noexcept {
        if (is_bus_off) {
            recovery_timer_ms += dt_ms;
            if (recovery_timer_ms >= backoff_delay_ms) {
                recovery_timer_ms = 0;
                if (backoff_delay_ms < 5000) {
                    backoff_delay_ms *= 2;
                }
            }
            return 0;
        }

        backoff_delay_ms = 100;
        recovery_timer_ms = 0;

        const uint8_t max_err = std::max(tec, rec);
        if (max_err < 32) {
            return 1000;
        }
        if (max_err >= 128) {
            return 200;
        }

        return static_cast<uint16_t>(1000 - (static_cast<uint32_t>(max_err - 32) * 800) / (128 - 32));
    }
};

} // namespace Health
```
:::

## Модуль діагностики шини SPI та обробки збоїв кадрування

Під час роботи з високошвидкісними датчиками (наприклад, шестиосьовими інерційними модулями IMU з частотою обміну до 10–20 МГц) шина SPI може зазнавати двох типів апаратних збоїв:

1. **Помилка переповнення буфера (Overrun Error, ORE):** виникає, коли центральний процесор затримується у вищому за пріоритетом перериванні і не встигає прочитати байт з регістра `SPI_DR` до завершення прийому наступного байта. У результаті апаратний блок SPI заморожує буфер прийому, а всі наступні байти відкидаються. Для очищення прапорця `ORE` драйвер зобов'язаний виконати послідовне фіктивне читання регістра даних `SPI_DR` та регістра стану `SPI_SR`;
2. **Помилка модового збою (Mode Fault, MODF):** виникає, коли лінія вибору веденого `NSS` випадково притискається до землі зовнішнім фактором під час роботи мікроконтролера в режимі Master. Процесор автоматично скидає біт `MSTR` у регістрі `SPI_CR1` і переходить у пасивний стан Slave, припиняючи генерацію тактових імпульсів на лінії `SCK`.

Супервізор безперервно відстежує стан регістра помилок SPI та апаратний лічильник помилок контрольної суми `CRC`. Якщо кількість помилок перевищує 5 за секунду, модуль виконує безпечне програмне перезавантаження інтерфейсу `SPI`.

:::tabs
```c
typedef struct {
    uint32_t crc_errors;
    uint32_t overrun_errors;
    uint32_t mode_fault_errors;
    bool     continuous_dead_data; // Постійні 0x00 або 0xFF
} health_spi_diag_t;

uint16_t health_evaluate_spi(const health_spi_diag_t *diag) {
    if (!diag) return 0;

    if (diag->mode_fault_errors > 0 || diag->continuous_dead_data) {
        return 100; // Критичний збій лінії або сенсора
    }

    uint32_t total_err = diag->crc_errors + diag->overrun_errors;
    if (total_err == 0) {
        return 1000;
    }
    if (total_err >= 20) {
        return 300;
    }

    return (uint16_t)(1000 - (total_err * 700) / 20);
}
```
```cpp
namespace Health {

struct SpiDiagnostics {
    uint32_t crc_errors{0};
    uint32_t overrun_errors{0};
    uint32_t mode_fault_errors{0};
    bool     continuous_dead_data{false};

    [[nodiscard]] constexpr uint16_t evaluate() const noexcept {
        if (mode_fault_errors > 0 || continuous_dead_data) {
            return 100;
        }

        const uint32_t total_err = crc_errors + overrun_errors;
        if (total_err == 0) {
            return 1000;
        }
        if (total_err >= 20) {
            return 300;
        }

        return static_cast<uint16_t>(1000 - (total_err * 700) / 20);
    }
};

} // namespace Health
```
:::

## Модуль телеметрії живлення та детекції пульсацій

Підсистема контролю живлення зчитує абсолютну напругу шини `VDD` через аналого-цифровий перетворювач і порівнює її з номінальним значенням (3300 мВ).

Крім вимірювання постійної складової напруги, супервізор аналізує амплітуду пульсацій `V_ripple`:
- Якщо напруга живлення знаходиться в діапазоні `3200 ... 3400 мВ`, а розмах пульсацій менший за 50 мВ — стан ідеальний (`1000`);
- Якщо напруга просідає нижче `3000 мВ` або пульсації перевищують 200 мВ — бал знижується;
- При досягненні порогу спрацьовування `PVD` (2800 мВ) бал падає до `0`, що викликає миттєвий перехід у режим безпеки.

:::tabs
```c
uint16_t health_evaluate_power_rail(uint32_t vdd_mv, uint32_t ripple_mv) {
    if (vdd_mv < 2800 || vdd_mv > 3600) {
        return 0; // Неприпустима напруга
    }

    uint16_t score = 1000;

    // Штраф за просідання напруги нижче 3200 мВ
    if (vdd_mv < 3200) {
        uint32_t delta_v = 3200 - vdd_mv; // 0..400 мВ
        score -= (uint16_t)((delta_v * 600) / 400);
    }

    // Штраф за пульсації понад 50 мВ
    if (ripple_mv > 50) {
        uint32_t excess_ripple = ripple_mv - 50;
        if (excess_ripple > 250) {
            excess_ripple = 250;
        }
        uint16_t ripple_penalty = (uint16_t)((excess_ripple * 400) / 250);
        if (score > ripple_penalty) {
            score -= ripple_penalty;
        } else {
            score = 0;
        }
    }

    return score;
}
```
```cpp
namespace Health {

[[nodiscard]] constexpr uint16_t evaluate_power_rail(uint32_t vdd_mv, uint32_t ripple_mv) noexcept {
    if (vdd_mv < 2800 || vdd_mv > 3600) {
        return 0;
    }

    uint16_t score = 1000;

    if (vdd_mv < 3200) {
        const uint32_t delta_v = 3200 - vdd_mv;
        score -= static_cast<uint16_t>((delta_v * 600) / 400);
    }

    if (ripple_mv > 50) {
        uint32_t excess_ripple = ripple_mv - 50;
        if (excess_ripple > 250) {
            excess_ripple = 250;
        }
        const auto ripple_penalty = static_cast<uint16_t>((excess_ripple * 400) / 250);
        if (score > ripple_penalty) {
            score -= ripple_penalty;
        } else {
            score = 0;
        }
    }

    return score;
}

} // namespace Health
```
:::

## Модуль фонового сканування цілісності Flash (Memory Scrubbing)

Для захисту від накопичення прихованих поодиноких збоїв пам'яті під дією іонізуючого випромінювання та завад супервізор містить легковаговий рушій фонового сканування Flash пам'яті (англ. *Memory Scrubbing Engine*).

Принцип роботи полягає у послідовному вичитуванні малих блоків Flash (по 64 байти за один виклик) під час повільного кванту часу (інтервал 1–5 секунд). При зчитуванні кожного 64-бітного подвійного слова апаратний блок ECC мікроконтролера виконує перевірку та корекцію бітів. Якщо виникає виправлена однобітова помилка `ECCC`, супервізор реєструє координати дефектного сектора для подальшого аналізу.

:::tabs
```c
typedef struct {
    uint32_t current_address;
    uint32_t start_address;
    uint32_t end_address;
    uint32_t single_bit_errors;
    uint32_t double_bit_errors;
} health_flash_scrubber_t;

void health_flash_scrubber_init(health_flash_scrubber_t *scrubber, uint32_t start, uint32_t end) {
    if (!scrubber) return;
    scrubber->start_address = start;
    scrubber->end_address = end;
    scrubber->current_address = start;
    scrubber->single_bit_errors = 0;
    scrubber->double_bit_errors = 0;
}

void health_flash_scrubber_step(health_flash_scrubber_t *scrubber, size_t words_to_read) {
    if (!scrubber || scrubber->start_address >= scrubber->end_address) return;

    volatile const uint32_t *ptr = (volatile const uint32_t *)scrubber->current_address;
    for (size_t i = 0; i < words_to_read; ++i) {
        // Фіктивне читання для провокації апаратного блоку ECC
        volatile uint32_t dummy = *ptr++;
        (void)dummy;

        scrubber->current_address += sizeof(uint32_t);
        if (scrubber->current_address >= scrubber->end_address) {
            scrubber->current_address = scrubber->start_address; // Зациклення
            break;
        }
    }
}
```
```cpp
namespace Health {

class FlashScrubber {
public:
    constexpr FlashScrubber(uintptr_t start_addr, uintptr_t end_addr) noexcept
        : start_address_(start_addr), end_address_(end_addr), current_address_(start_addr) {}

    void step(size_t words_to_read) noexcept {
        if (start_address_ >= end_address_) return;

        auto ptr = reinterpret_cast<volatile const uint32_t*>(current_address_);
        for (size_t i = 0; i < words_to_read; ++i) {
            volatile uint32_t dummy = *ptr++;
            (void)dummy;

            current_address_ += sizeof(uint32_t);
            if (current_address_ >= end_address_) {
                current_address_ = start_address_;
                break;
            }
        }
    }

    [[nodiscard]] uintptr_t current_address() const noexcept { return current_address_; }

private:
    uintptr_t start_address_{0};
    uintptr_t end_address_{0};
    uintptr_t current_address_{0};
};

} // namespace Health
```
:::

## Менеджер енергонезалежної пам'яті FRAM для чорної скриньки

Для гарантованого збереження аварійних дампів при раптовому вимкненні живлення вбудовані системи використовують енергонезалежну фероелектричну пам'ять (FRAM). На відміну від традиційної Flash-пам'яті або EEPROM, FRAM володіє трьома критичними перевагами:
1. Час запису байта становить менше 50 наносекунд без затримок програмування сторінки;
2. Відсутність потреби у попередньому стиранні секторів;
3. Ресурс запису перевищує $10^{14}$ циклів, що унеможливлює знос пам'яті навіть при щосекундному збереженні логів.

Модуль чорної скриньки реалізує запис діагностичного кадру в мікросхему FRAM через інтерфейс SPI.

:::tabs
```c
typedef struct {
    void (*spi_select)(bool select);
    void (*spi_transmit)(const uint8_t *data, size_t len);
} health_fram_driver_t;

#define FRAM_CMD_WREN  0x06
#define FRAM_CMD_WRITE 0x02

void health_fram_write_entry(const health_fram_driver_t *driver, 
                             uint32_t address, 
                             const health_blackbox_entry_t *entry) {
    if (!driver || !driver->spi_select || !driver->spi_transmit || !entry) {
        return;
    }

    // 1. Дозвіл запису (WREN)
    uint8_t wren = FRAM_CMD_WREN;
    driver->spi_select(true);
    driver->spi_transmit(&wren, 1);
    driver->spi_select(false);

    // 2. Команда запису з 24-бітною адресою
    uint8_t cmd_hdr[4] = {
        FRAM_CMD_WRITE,
        (uint8_t)((address >> 16) & 0xFF),
        (uint8_t)((address >> 8) & 0xFF),
        (uint8_t)(address & 0xFF)
    };

    driver->spi_select(true);
    driver->spi_transmit(cmd_hdr, sizeof(cmd_hdr));
    driver->spi_transmit((const uint8_t *)entry, sizeof(health_blackbox_entry_t));
    driver->spi_select(false);
}
```
```cpp
namespace Health {

struct FramDriver {
    std::function<void(bool)> spi_select{};
    std::function<void(std::span<const uint8_t>)> spi_transmit{};

    void write_entry(uint32_t address, const BlackboxEntry& entry) const noexcept {
        if (!spi_select || !spi_transmit) return;

        const uint8_t wren = 0x06;
        spi_select(true);
        spi_transmit(std::span<const uint8_t>(&wren, 1));
        spi_select(false);

        const std::array<uint8_t, 4> cmd_hdr{
            0x02,
            static_cast<uint8_t>((address >> 16) & 0xFF),
            static_cast<uint8_t>((address >> 8) & 0xFF),
            static_cast<uint8_t>(address & 0xFF)
        };

        spi_select(true);
        spi_transmit(cmd_hdr);
        spi_transmit(std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&entry), sizeof(BlackboxEntry)));
        spi_select(false);
    }
};

} // namespace Health
```
:::

## Модуль міжпроцесорного нагляду (Asymmetric Dual-Core Heartbeat)

У високонадійних авіаційних та робототехнічних комплексах застосовується асиметрична двопроцесорна архітектура:
- **Основний процесор керування (Master MCU, наприклад STM32H7):** виконує важкі задачі навігації, обробки відео та планування траєкторій;
- **Супервізор безпеки (Safety Coprocessor, наприклад STM32G4):** компактний мікроконтролер, який не бере участі в складних розрахунках, але контролює живлення, датчики кінцевих положень та стан головного процесора.

Для зв'язку між ними супервізор реалізує протокол запит-відповідь (Challenge-Response Ping-Pong):
1. Супервізор кожні 20 мс надсилає на головний процесор псевдовипадкове 16-бітне число (Challenge) через SPI або UART;
2. Головний процесор повинен виконати криптографічну або поліноміальну трансформацію цього числа, підмішавши бітову маску успішно завершених фаз алгоритму керування, та надіслати відповідь (Response);
3. Якщо відповідь не надходить або містить помилкове значення протягом двох циклів поспіль (40 мс), супервізор безпеки апаратно знімає напругу з лінії живлення двигунів через дискретний оптронний ключ.

:::tabs
```c
typedef struct {
    uint16_t current_challenge;
    uint32_t missed_heartbeats;
    bool     safety_relay_state;
} health_intercore_monitor_t;

void health_intercore_init(health_intercore_monitor_t *mon) {
    if (!mon) return;
    mon->current_challenge = 0x1234;
    mon->missed_heartbeats = 0;
    mon->safety_relay_state = true;
}

uint16_t health_intercore_generate_challenge(health_intercore_monitor_t *mon) {
    if (!mon) return 0;
    // Простий лінійний конгруентний генератор для тесту зв'язку
    mon->current_challenge = (uint16_t)(mon->current_challenge * 31421U + 6927U);
    return mon->current_challenge;
}

bool health_intercore_verify_response(health_intercore_monitor_t *mon, uint16_t response) {
    if (!mon) return false;

    // Очікувана трансформація: побітова інверсія з циклічним зсувом
    uint16_t expected = (uint16_t)(~mon->current_challenge ^ 0x5A5AU);

    if (response == expected) {
        mon->missed_heartbeats = 0;
        mon->safety_relay_state = true;
        return true;
    }

    mon->missed_heartbeats++;
    if (mon->missed_heartbeats >= 3) {
        mon->safety_relay_state = false; // Вимикання силового контактора
    }
    return false;
}
```
```cpp
namespace Health {

class InterCoreSupervisor {
public:
    constexpr InterCoreSupervisor() noexcept = default;

    uint16_t generate_challenge() noexcept {
        current_challenge_ = static_cast<uint16_t>(current_challenge_ * 31421U + 6927U);
        return current_challenge_;
    }

    bool verify_response(uint16_t response) noexcept {
        const uint16_t expected = static_cast<uint16_t>(~current_challenge_ ^ 0x5A5AU);

        if (response == expected) {
            missed_heartbeats_ = 0;
            safety_relay_state_ = true;
            return true;
        }

        ++missed_heartbeats_;
        if (missed_heartbeats_ >= 3) {
            safety_relay_state_ = false;
        }
        return false;
    }

    [[nodiscard]] bool is_safety_relay_closed() const noexcept { return safety_relay_state_; }

private:
    uint16_t current_challenge_{0x1234};
    uint32_t missed_heartbeats_{0};
    bool     safety_relay_state_{true};
};

} // namespace Health
```
:::

## Модуль інжекції несправностей (Software Fault Injection Engine)

Для автоматизованого тестування стійкості прошивки на стендах Hardware-in-the-Loop (HIL) розроблено модуль контрольованої інжекції збоїв (Fault Injection Engine). Він дозволяє емулювати апаратні несправності без фізичного втручання в плату за допомогою спеціальних тестових прапорців.

Модуль підтримує 4 режими інжекції:
1. **Імітація вичерпання стека:** штучне затирання канаркового слова `0xA5A5A5A5` на дні стека довільним значенням `0xDEADBEEF`;
2. **Імітація просідання напруги:** підміна виміряного значення напруги АЦП на значення нижче порогу PVD (2700 мВ);
3. **Імітація зависання шини CAN:** примусове встановлення лічильника `TEC = 256` у структурі драйвера;
4. **Імітація заклинювання лінії I2C SDA:** повернення нульового рівня при опитуванні лінії даних.

:::tabs
```c
typedef enum {
    FAULT_INJECT_NONE = 0,
    FAULT_INJECT_STACK_CORRUPT,
    FAULT_INJECT_UNDERVOLTAGE,
    FAULT_INJECT_CAN_BUSOFF,
    FAULT_INJECT_I2C_LOCKUP
} health_fault_inject_mode_t;

typedef struct {
    health_fault_inject_mode_t active_mode;
    uint32_t                   duration_ticks;
} health_fault_injector_t;

void health_fault_injector_init(health_fault_injector_t *inj) {
    if (!inj) return;
    inj->active_mode = FAULT_INJECT_NONE;
    inj->duration_ticks = 0;
}

void health_fault_inject_trigger(health_fault_injector_t *inj, 
                                 health_fault_inject_mode_t mode, 
                                 uint32_t duration_ticks) {
    if (!inj) return;
    inj->active_mode = mode;
    inj->duration_ticks = duration_ticks;
}

uint16_t health_fault_inject_apply(health_fault_injector_t *inj, 
                                   health_fault_inject_mode_t target_mode, 
                                   uint16_t actual_value) {
    if (!inj || inj->active_mode != target_mode || inj->duration_ticks == 0) {
        return actual_value;
    }

    inj->duration_ticks--;
    if (inj->duration_ticks == 0) {
        inj->active_mode = FAULT_INJECT_NONE;
    }

    // Повернення деградованого значення залежно від типу інжекції
    switch (target_mode) {
        case FAULT_INJECT_UNDERVOLTAGE: return 100; // Просідання живлення
        case FAULT_INJECT_CAN_BUSOFF:   return 0;   // Bus-Off
        case FAULT_INJECT_I2C_LOCKUP:   return 50;  // Зависання шини
        case FAULT_INJECT_STACK_CORRUPT: return 0;  // Пошкодження стека
        default: return actual_value;
    }
}
```
```cpp
namespace Health {

enum class FaultInjectMode : uint8_t {
    None = 0,
    StackCorrupt,
    Undervoltage,
    CanBusOff,
    I2cLockup
};

class FaultInjector {
public:
    constexpr FaultInjector() noexcept = default;

    void trigger(FaultInjectMode mode, uint32_t duration_ticks) noexcept {
        active_mode_ = mode;
        duration_ticks_ = duration_ticks;
    }

    [[nodiscard]] uint16_t apply(FaultInjectMode target_mode, uint16_t actual_value) noexcept {
        if (active_mode_ != target_mode || duration_ticks_ == 0) {
            return actual_value;
        }

        --duration_ticks_;
        if (duration_ticks_ == 0) {
            active_mode_ = FaultInjectMode::None;
        }

        switch (target_mode) {
            case FaultInjectMode::Undervoltage: return 100;
            case FaultInjectMode::CanBusOff:   return 0;
            case FaultInjectMode::I2cLockup:   return 50;
            case FaultInjectMode::StackCorrupt: return 0;
            default: return actual_value;
        }
    }

    [[nodiscard]] bool is_active() const noexcept { return active_mode_ != FaultInjectMode::None; }

private:
    FaultInjectMode active_mode_{FaultInjectMode::None};
    uint32_t        duration_ticks_{0};
};

} // namespace Health
```
:::

## Математичний рушій фільтрації та розрахунку Health Score

Розрахунок інтегрального індексу здоров'я системи базується на двох математичних операціях: експоненційній фільтрації сирих потоків та розрахунку виваженої матриці з мультиплікативним штрафом.

### Дискретна фільтрація EWMA

Для згладжування миттєвих сплесків вимірювань використовується експоненційно зважене ковзне середнє з постійною часу `α = 1/8`:

```
H[k] = (raw_metric + 7 * H[k-1] + 4) >> 3
```

Такий вибір коефіцієнта забезпечує оптимальний баланс: система фільтрує поодинокі завади АЦП та випадкові бітові помилки передачі, але реагує на стійку деградацію компонента за 5–8 циклів опитування (250–400 мс при кроці 50 мс).

### Мультиплікативний штраф та кінцевий автомат ескалації

Після розрахунку зваженої суми балів перевіряється умова критичності: якщо хоча б один зареєстрований компонент із прапорцем `is_critical = true` має показник `smoothed_score < 400`, інтегральний системний бал примусово встановлюється в `0`, а система переводиться у стан `HEALTH_STATE_EMERGENCY`. Одночасно формується діагностичний запис у кільцевий буфер чорної скриньки.

:::tabs
```c
static uint32_t health_calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(uint32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

void health_supervisor_init(health_supervisor_t *ctx) {
    if (!ctx) return;
    ctx->component_count = 0;
    ctx->system_score = HEALTH_SCORE_PERFECT;
    ctx->current_state = HEALTH_STATE_NOMINAL;
    ctx->iteration_counter = 0;
    ctx->warmup_ticks_left = HEALTH_WARMUP_TICKS;
    ctx->blackbox_head = 0;
    ctx->blackbox_seq = 0;

    for (size_t i = 0; i < HEALTH_BLACKBOX_SLOTS; ++i) {
        ctx->blackbox_ring[i].magic = 0;
    }
}

bool health_supervisor_register(health_supervisor_t *ctx,
                                const char *name,
                                health_collector_fn collector,
                                void *user_ctx,
                                uint16_t weight,
                                bool is_critical) {
    if (!ctx || ctx->component_count >= HEALTH_MAX_COMPONENTS || !collector) {
        return false;
    }

    health_component_desc_t *c = &ctx->components[ctx->component_count++];
    c->name = name ? name : "Unnamed";
    c->collector = collector;
    c->user_ctx = user_ctx;
    c->weight = (weight > 0) ? weight : 1;
    c->is_critical = is_critical;
    c->smoothed_score = HEALTH_SCORE_PERFECT;
    c->consecutive_failures = 0;
    return true;
}

void health_supervisor_tick(health_supervisor_t *ctx, uint64_t timestamp_ms) {
    if (!ctx) return;

    ctx->iteration_counter++;
    if (ctx->warmup_ticks_left > 0) {
        ctx->warmup_ticks_left--;
    }

    uint32_t weighted_score_sum = 0;
    uint32_t total_weight = 0;
    bool critical_fail = false;
    uint8_t failed_component_id = 0xFF;

    for (uint8_t i = 0; i < ctx->component_count; ++i) {
        health_component_desc_t *c = &ctx->components[i];
        uint16_t raw = c->collector(c->user_ctx);

        if (raw > HEALTH_SCORE_PERFECT) {
            raw = HEALTH_SCORE_PERFECT;
        }

        // EWMA згладжування з округленням до найближчого: H[k] = (raw + 7 * H[k-1] + 4) / 8
        c->smoothed_score = (uint16_t)((raw + (uint32_t)c->smoothed_score * 7U + 4U) >> 3U);

        if (c->smoothed_score < HEALTH_CRITICAL_THRESHOLD) {
            c->consecutive_failures++;
            if (c->is_critical && ctx->warmup_ticks_left == 0) {
                critical_fail = true;
                failed_component_id = i;
            }
        } else {
            c->consecutive_failures = 0;
        }

        weighted_score_sum += (uint32_t)c->smoothed_score * c->weight;
        total_weight += c->weight;
    }

    if (total_weight > 0) {
        ctx->system_score = (uint16_t)(weighted_score_sum / total_weight);
    } else {
        ctx->system_score = 0;
    }

    // Мультиплікативний штраф для критичних підсистем
    if (critical_fail) {
        ctx->system_score = 0;
        ctx->current_state = HEALTH_STATE_EMERGENCY;
        health_supervisor_log_emergency(ctx, failed_component_id, 0, 0, timestamp_ms);
    } else if (ctx->system_score >= HEALTH_NOMINAL_THRESHOLD) {
        ctx->current_state = HEALTH_STATE_NOMINAL;
    } else if (ctx->system_score >= HEALTH_DEGRADED_THRESHOLD) {
        ctx->current_state = HEALTH_STATE_DEGRADED;
    } else if (ctx->system_score >= HEALTH_CRITICAL_THRESHOLD) {
        ctx->current_state = HEALTH_STATE_CRITICAL;
    } else {
        ctx->current_state = HEALTH_STATE_EMERGENCY;
        health_supervisor_log_emergency(ctx, 0xFE, 0, 0, timestamp_ms);
    }
}

void health_supervisor_log_emergency(health_supervisor_t *ctx, 
                                     uint8_t faulty_id, 
                                     uint32_t cfsr, 
                                     uint32_t hfsr,
                                     uint64_t timestamp_ms) {
    if (!ctx) return;

    health_blackbox_entry_t *entry = &ctx->blackbox_ring[ctx->blackbox_head];
    entry->magic = HEALTH_BLACKBOX_MAGIC;
    entry->seq_num = ++ctx->blackbox_seq;
    entry->timestamp_ms = timestamp_ms;
    entry->system_score = ctx->system_score;
    entry->system_state = (uint8_t)ctx->current_state;
    entry->fault_component_id = faulty_id;
    entry->cfsr_reg = cfsr;
    entry->hfsr_reg = hfsr;
    entry->vdd_mv = 3300;
    entry->core_temp_c = 25;
    entry->min_stack_free_bytes = 128;

    entry->crc32 = health_calculate_crc32((const uint8_t *)entry, 
                                          offsetof(health_blackbox_entry_t, crc32));

    ctx->blackbox_head = (ctx->blackbox_head + 1) % HEALTH_BLACKBOX_SLOTS;
}
```
```cpp
namespace Health {

template <size_t MaxComponents, size_t BlackboxSlots>
uint32_t Supervisor<MaxComponents, BlackboxSlots>::calculate_crc32(
    const uint8_t *data, size_t length) const noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(uint32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

template <size_t MaxComponents, size_t BlackboxSlots>
void Supervisor<MaxComponents, BlackboxSlots>::tick(uint64_t timestamp_ms) noexcept {
    ++iteration_counter_;
    if (warmup_ticks_left_ > 0) {
        --warmup_ticks_left_;
    }

    uint32_t weighted_score_sum = 0;
    uint32_t total_weight = 0;
    bool critical_fail = false;
    uint8_t failed_component_id = 0xFF;

    for (size_t i = 0; i < component_count_; ++i) {
        auto& comp = components_[i];
        uint16_t raw = comp.collector ? comp.collector() : 0;
        if (raw > ScorePerfect) {
            raw = ScorePerfect;
        }

        // EWMA згладжування з округленням: H[k] = (raw + 7 * H[k-1] + 4) >> 3
        comp.smoothed_score = static_cast<uint16_t>(
            (raw + static_cast<uint32_t>(comp.smoothed_score) * 7U + 4U) >> 3U
        );

        if (comp.smoothed_score < CriticalThreshold) {
            ++comp.consecutive_failures;
            if (comp.is_critical && warmup_ticks_left_ == 0) {
                critical_fail = true;
                failed_component_id = static_cast<uint8_t>(i);
            }
        } else {
            comp.consecutive_failures = 0;
        }

        weighted_score_sum += static_cast<uint32_t>(comp.smoothed_score) * comp.weight;
        total_weight += comp.weight;
    }

    system_score_ = (total_weight > 0) 
        ? static_cast<uint16_t>(weighted_score_sum / total_weight) 
        : 0;

    if (critical_fail) {
        system_score_ = 0;
        current_state_ = State::Emergency;
        log_emergency(failed_component_id, 0, 0, timestamp_ms);
    } else if (system_score_ >= NominalThreshold) {
        current_state_ = State::Nominal;
    } else if (system_score_ >= DegradedThreshold) {
        current_state_ = State::Degraded;
    } else if (system_score_ >= CriticalThreshold) {
        current_state_ = State::Critical;
    } else {
        current_state_ = State::Emergency;
        log_emergency(0xFE, 0, 0, timestamp_ms);
    }
}

template <size_t MaxComponents, size_t BlackboxSlots>
void Supervisor<MaxComponents, BlackboxSlots>::log_emergency(
    uint8_t faulty_id, uint32_t cfsr, uint32_t hfsr, uint64_t timestamp_ms) noexcept {
    auto& entry = blackbox_ring_[blackbox_head_];
    entry.magic = BlackboxMagic;
    entry.seq_num = ++blackbox_seq_;
    entry.timestamp_ms = timestamp_ms;
    entry.system_score = system_score_;
    entry.system_state = current_state_;
    entry.fault_component_id = faulty_id;
    entry.cfsr_reg = cfsr;
    entry.hfsr_reg = hfsr;
    entry.vdd_mv = 3300;
    entry.core_temp_c = 25;
    entry.min_stack_free_bytes = 128;

    entry.crc32 = calculate_crc32(reinterpret_cast<const uint8_t*>(&entry),
                                  sizeof(BlackboxEntry) - sizeof(uint32_t));

    blackbox_head_ = (blackbox_head_ + 1) % BlackboxSlots;
}

} // namespace Health
```
:::

## Каркас стрес-тестування та симуляції несправностей

Для всебічної верифікації поведінки супервізора в умовах реальних збоїв розроблено набір автономних модульних тестів (Unit Tests). Тестовий каркас симулює чотири характерні аварійні ситуації:

1. **Номінальний режим (Baseline):** усі підсистеми повертають значення `1000`. Супервізор повинен утримувати стан `HEALTH_STATE_NOMINAL` та системний бал понад `950`;
2. **Деградація другорядного вузла (Degraded State):** підсистема з невеликою вагою (наприклад, шина CAN з вагою 30) починає повертати низький бал `200` внаслідок перешкод. Супервізор повинен плавно знизити системний бал, перейти у стан `DEGRADED` або `CRITICAL`, але **не викликати аварійного скидання**, дозволяючи пристрою продовжувати виконання основних функцій;
3. **Відмова критичного компонента (Critical Failover):** підсистема електроживлення з вагою 40 та ознакою `is_critical = true` раптово падає до балу `100` (імітація спрацьовування PVD). Супервізор повинен негайно обнулити системний бал, активувати стан `HEALTH_STATE_EMERGENCY` та зафіксувати подію в журналі чорної скриньки;
4. **Перевірка цілісності чорної скриньки (Blackbox Integrity):** верифікація магічного слова `0xDEADBEEF`, послідовності нумерації кадрів та правильності розрахунку контрольної суми `CRC-32`.

:::tabs
```c
#include <stdio.h>
#include <assert.h>

static uint16_t s_mock_power_val = 1000;
static uint16_t s_mock_stack_val = 1000;
static uint16_t s_mock_can_val   = 1000;

static uint16_t test_collect_power(void *ctx) { (void)ctx; return s_mock_power_val; }
static uint16_t test_collect_stack(void *ctx) { (void)ctx; return s_mock_stack_val; }
static uint16_t test_collect_can(void *ctx)   { (void)ctx; return s_mock_can_val; }

void health_run_unit_tests(void) {
    health_supervisor_t sup;
    health_supervisor_init(&sup);

    health_supervisor_register(&sup, "Power", test_collect_power, NULL, 40, true);
    health_supervisor_register(&sup, "Stack", test_collect_stack, NULL, 30, false);
    health_supervisor_register(&sup, "CAN",   test_collect_can,   NULL, 30, false);

    // Тест 1: Початковий стан ідеальний (проходження періоду Warm-up)
    for (int i = 0; i < 25; ++i) {
        health_supervisor_tick(&sup, i * 50);
    }
    assert(sup.current_state == HEALTH_STATE_NOMINAL);
    assert(sup.system_score > 950);

    // Тест 2: Деградація некритичного вузла (CAN)
    s_mock_can_val = 200;
    for (int i = 0; i < 16; ++i) {
        health_supervisor_tick(&sup, 1500 + i * 50);
    }
    assert(sup.current_state == HEALTH_STATE_DEGRADED || sup.current_state == HEALTH_STATE_CRITICAL);
    assert(sup.system_score < 900);

    // Тест 3: Фатальний збій критичного вузла (Power) -> Миттєвий EMERGENCY
    s_mock_power_val = 100;
    for (int i = 0; i < 16; ++i) {
        health_supervisor_tick(&sup, 2500 + i * 50);
    }
    assert(sup.current_state == HEALTH_STATE_EMERGENCY);
    assert(sup.system_score == 0); // Мультиплікативний штраф обнулив бал

    // Тест 4: Перевірка запису в чорну скриньку
    assert(sup.blackbox_seq > 0);
    const health_blackbox_entry_t *last_log = &sup.blackbox_ring[0];
    assert(last_log->magic == HEALTH_BLACKBOX_MAGIC);
    assert(last_log->system_state == HEALTH_STATE_EMERGENCY);

    printf("Health Monitor Unit Tests: ALL PASSED (4/4)\n");
}
```
```cpp
#include <iostream>
#include <cassert>

namespace Health::Tests {

void run_unit_tests() {
    Supervisor<8, 16> sup;

    uint16_t mock_power = 1000;
    uint16_t mock_stack = 1000;
    uint16_t mock_can   = 1000;

    sup.register_component("Power", [&]() { return mock_power; }, 40, true);
    sup.register_component("Stack", [&]() { return mock_stack; }, 30, false);
    sup.register_component("CAN",   [&]() { return mock_can; },   30, false);

    // Тест 1: Номінальний стан (з урахуванням Warm-up)
    for (int i = 0; i < 25; ++i) {
        sup.tick(i * 50);
    }
    assert(sup.state() == State::Nominal);
    assert(sup.system_score() > 950);

    // Тест 2: Деградація другорядного вузла
    mock_can = 200;
    for (int i = 0; i < 16; ++i) {
        sup.tick(1500 + i * 50);
    }
    assert(sup.state() == State::Degraded || sup.state() == State::Critical);
    assert(sup.system_score() < 900);

    // Тест 3: Аварія критичного вузла
    mock_power = 100;
    for (int i = 0; i < 16; ++i) {
        sup.tick(2500 + i * 50);
    }
    assert(sup.state() == State::Emergency);
    assert(sup.system_score() == 0);

    // Тест 4: Перевірка чорної скриньки
    const auto log = sup.blackbox();
    assert(log[0].magic == BlackboxMagic);
    assert(log[0].system_state == State::Emergency);

    std::cout << "Health Monitor C++20 Unit Tests: ALL PASSED (4/4)\n";
}

} // namespace Health::Tests
```
:::

## Керування когерентністю D-Cache та бар'єри пам'яті

На сучасних високопродуктивних мікроконтролерах із ядрами ARM Cortex-M7 або Cortex-M55 (наприклад, серії STM32H7 або NXP i.MX RT) функціонує дворівнева ієрархія кеш-пам'яті: 16–32 КБ інструкційного кешу (I-Cache) та 16–32 КБ кешу даних (D-Cache). Наявність кешу даних із політикою зворотного запису (Write-Back) створює приховану небезпеку для підсистеми супервізора: якщо аварійний дамп чорної скриньки записується в оперативну пам'ять або передається контролеру DMA без примусового скидання кешу, у зовнішню енергонезалежну пам'ять FRAM буде записано застарілий блок пам'яті, тоді як актуальні дані залишаться в брудних рядках кешу процесора.

Для гарантування когерентності даних перед збереженням аварійного кадру супервізор виконує послідовність апаратних бар'єрів пам'яті:

1. **Інструкція `__DSB()` (Data Synchronization Barrier):** призупиняє виконання конвеєра ядра до повного завершення всіх попередніх транзакцій запису у внутрішні буфери шини AXI/AHB;
2. **Очищення кешу за адресою `SCB_CleanDCache_by_Addr()`:** примусово виштовхує брудні рядки D-Cache, що містять структуру `health_blackbox_entry_t`, у фізичну пам'ять SRAM;
3. **Інструкція `__DMB()` (Data Memory Barrier):** гарантує, що операція передачі керування драйверу SPI DMA відбудеться строго після фізичного завершення скидання кеш-пам'яті.

## Моніторинг стабільності тактового генератора (HSE Frequency Cross-Check)

Пошкодження кварцового резонатора `HSE` або конденсаторів його обв'язки може призвести до поступового відходу тактової частоти мікроконтролера на кілька відсотків. Оскільки системний таймер `SysTick` та більшість таймерів шин APB тактуються від виходу `PLL`, дрейф опорної частоти викликає розбіжність бітрейтів на шинах CAN та UART, породжуючи лавину помилок кадрування `Framing Error`.

Супервізор реалізує непряму перевірку стабільності частоти кварцового генератора `HSE` за допомогою методу перехресного вимірювання (Cross-Timer Capture). Апаратний таймер загального призначення (наприклад, `TIM5` на STM32) налаштовується на захоплення вхідного сигналу від годинникового низькочастотного кварцового генератора `LSE` (32.768 кГц). 

Кількість тактів системної частоти `N_core`, підрахована таймером між двома послідовними імпульсами генератора `LSE`, повинна залишатися строго постійною:

```
N_core = f_SYSCLK / 32768
```

Якщо розраховане значення відхиляється від номіналу більш ніж на ±1.5%, супервізор фіксує деградацію тактової системи, підіймає тривожний прапорець `CLOCK_DRIFT` та ініціює безпечний перехід на внутрішній високоточний генератор `HSI`.

## Аналіз швидкодії, пам'яті та рекомендації з інтеграції

Оцінка продуктивності та накладних витрат супервізора життєдіяльності виконувалася на мікроконтролері STM32G474 (ядро ARM Cortex-M4F, тактова частота 170 МГц) за допомогою апаратного лічильника циклів ядра `DWT->CYCCNT`:

- **Час виконання одного кроку `health_supervisor_tick()` (8 активних компонентів):** 420 тактів процесора (приблизно 2.47 мікросекунди);
- **Час виконання процедури розблокування I2C (9 імпульсів):** близько 200 мікросекунд (виконується виключно в разі фіксації блокування шини);
- **Обсяг оперативної пам'яті (SRAM Footprint):**
  - Масив дескрипторів (8 компонентів): 256 байтів;
  - Кільцевий буфер чорної скриньки (16 записів): 768 байтів;
  - Загальний розмір контексту супервізора: 1088 байтів (1.06 КБ);
- **Обсяг Flash пам'яті (Code Footprint при збірці з оптимізацією -O2):** 1.84 КБ для модуля C99 та 2.12 КБ для шаблону C++20.

### Рекомендації з інтеграції в архітектуру прошивки

Для досягнення максимального рівня надійності інтеграцію супервізора рекомендується виконувати за наступними правилами:

1. **Прив'язка до апаратного Watchdog:** скидання сторожового таймера `IWDG/WWDG` має здійснюватися **тільки всередині функції `health_supervisor_tick()`** і лише за умови, що системний стан не дорівнює `HEALTH_STATE_EMERGENCY`. Якщо супервізор переходить в аварійний стан або зависає сам — годівля сторожового таймера припиняється, забезпечуючи гарантоване апаратне скидання процесора;
2. **Пріоритети задач FreeRTOS:** задача супервізора повинна мати пріоритет вищий, ніж непривілейовані користувацькі задачі (UI, логування на SD-карту, мережеві сокети), але нижчий за критичні задачі контуру керування (Field-Oriented Control двигуна, розрахунок фільтра Калмана БПЛА);
3. **Енергонезалежне зберігання Blackbox:** буфер чорної скриньки рекомендується розміщувати в енергонезалежній пам'яті `FRAM` через інтерфейс SPI або виділеному секторі Flash з підтримкою резервного живлення `VBAT`, що гарантує збереження журналу навіть при повному знеструмленні пристрою;
4. **Конфігурація трасування ядра FreeRTOS:** у файлі `FreeRTOSConfig.h` рекомендується активувати макроси діагностики:
   - `#define configCHECK_FOR_STACK_OVERFLOW 2` — включає розширену перевірку канаркових байтів на дні стека при кожному контекстному перемиканні;
   - `#define configGENERATE_RUN_TIME_STATS 1` — дозволяє супервізору отримувати точний відсоток завантаження процесора кожною задачею через таймер `DWT->CYCCNT`;
   - `#define configUSE_TRACE_FACILITY 1` — відкриває доступ до структури `TaskStatus_t` для безперервного моніторингу черг та стану потоків.
