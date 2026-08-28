# ⚙️ Комплекс стрес-тестування інтермітуючих несправностей

Цей інженерний модуль являє собою комплексне програмно-апаратне рішення для локалізації інтермітуючих несправностей, мікротріщин паяних з'єднань BGA, прихованої деградації керамічних конденсаторів та граничних порушень часових інтервалів (*PVT Corner Violations*), які не фіксуються стандартними функціональними тестами й призводять до помилкової класифікації гарантійних повернень як NFF (*No Fault Found*).

Звичайні тести самодіагностики (*POST, Power-On Self-Test*) та стандартні утиліти перевірки пам'яті проєктуються для виявлення грубих перманентних дефектів (статичного обриву лінії, повного пробою комірки чи зависання контролера). Вони виконують поодинокі, рівномірно розподілені в часі транзакції читання та запису. За таких умов локальні блокувальні конденсатори встигають повністю відновити свій заряд, температура кристала залишається стабільною, а паразитні електромагнітні наводки між сусідніми провідниками друкованої плати не перевищують порогу логічного шуму. На відміну від них, комплекс стрес-тестування `nff_stress_suite` штучно створює екстремальні градієнти струму `dI/dt`, генерує максимальний просторовий та часовий шум на шинах даних, змушує ядро процесора працювати на межі споживання енергії та реєструє найменші транзиторні відхилення параметрів із субмікросекундною точністю.

## Фізико-алгоритмічний базис провокації інтермітуючих збоїв

Щоб прихований інтермітуючий дефект проявив себе у вигляді детектовного апаратного або програмного збою, тестовий алгоритм повинен одночасно впливати на чотири фізичні механізми напівпровідникового вузла:

1. **Ємнісний перехресний зв'язок (Crosstalk) та взаємна індуктивність провідників:** Під час одночасного перемикання групи паралельних сигнальних ліній шини виникає наведена напруга завади на сусідніх лініях:

```
V_noise = M · (dI_aggressor / dt) + L_ground · (dI_total / dt)    [шум наведеної завади на шині]
```
де `M` — взаємна індуктивність між сусідніми провідниками, `L_ground` — паразитна індуктивність виводів заземлення та опорних полігонів друкованої плати. Якщо паяне з'єднання BGA має підвищений перехідний опір або мікротріщину, наведена завада спотворює логічний рівень сигналу, викликаючи бітовий фліп.

2. **Динамічне просідання шин живлення ядра (Power Rail Sag):** Синхронне перемикання десятків тисяч логічних вентилів комбінаційної логіки ядра викликає різкий стрибок споживання струму з крутизною фронту `dI/dt > 10 А/мкс`. Якщо керамічні конденсатори декаплінгу втратили ємність через механічне розтріскування, напруга живлення `V_core` короткочасно просідає нижче робочого порогу, спричиняючи збій конвеєра або спрацьовування супервізора BOR.

3. **Теплове навантаження кремнієвого кристала:** Безперервні векторні та матричні обчислення в блоках FPU/SIMD розігрівають локальні ділянки кристала швидше, ніж тепло поширюється через кремнієву підкладку на радіатор. Виникають локальні внутрішньокристалічні термомеханічні градієнти, що підсилюють зсувні напруження на виводах BGA.

4. **Граничні затримки часу встановлення та утримання (Setup / Hold Times):** Спеціальні послідовності звернень до пам'яті через контролер прямого доступу (DMA) тестують шину на максимальній частоті тактування, виявляючи зсуви фази та затримки поширення сигналів при зміні температури навколишнього середовища.

## Математичні моделі покриття несправностей пам'яті

Ефективність виявлення інтермітуючих дефектів безпосередньо залежить від математичної структури тестових послідовностей. Комплекс `nff_stress_suite` поєднує алгоритми з різним рівнем обчислювальної складності для повного охоплення спектра напівпровідникових аномалій:

```
+───────────────────────────────────────────────────────────────────────────+
| ПОРІВНЯЛЬНА ХАРАКТЕРИСТИКА АЛГОРИТМІВ СТРЕС-ТЕСТУВАННЯ ПАМ'ЯТІ             |
|                                                                           |
|  Алгоритм        | Складність | Цільові типи дефектів                     |
| ─────────────────┼────────────┼────────────────────────────────────────── |
|  Checkerboard    |    4N      | Міжкомірковий витік, граничний Crosstalk   |
|  Walking Ones/0s |  2·32·N    | Обрив BGA, замикання шини (Bridge Fault)  |
|  Bus Inversion   |    2N      | Максимальний сплеск dI/dt, Ground Bounce  |
|  PRBS-31         |    2N      | Стохастичний резонанс живлення, джиттер   |
|  March C-        |   10N      | SAF, TF, CF (Coupling), Address Decoder   |
|  GALPAT          |   4N²      | Повний мікроємнісний аналіз (глибинний)   |
+───────────────────────────────────────────────────────────────────────────+
```

### Класифікація виявлених дефектів за стандартом IEEE 1500

Комплекс класифікує знайдені збої за такими фундаментальними категоріями:
- **SAF (Stuck-At Fault):** Комірка пам'яті або лінія шини постійно утримує стан логічної одиниці чи нуля незалежно від операцій запису.
- **TF (Transition Fault):** Комірка успішно зберігає поточний стан, але не здатна змінити його за один такт (завалений фронт імпульсу через деградацію підтягуючого резистора або ємнісне перевантаження).
- **CFin (Inversion Coupling Fault):** Запис логічного перепаду (0 → 1 або 1 → 0) в комірку-агресор викликає інверсію біта в сусідній комірці-жертві.
- **CFid (Idempotent Coupling Fault):** Перехід у комірці-агресорі примусово встановлює фіксований стан (0 або 1) у комірці-жертві незалежно від її попереднього вмісту.
- **ADF (Address Decoder Fault):** Помилка дешифратора адреси, коли звернення за адресою `A` активує одночасно дві фізичні комірки `A` та `B`, або коли за адресою `A` не вибирається жодна комірка.

## Архітектура та алгоритмічні патерни навантаження

Комплекс складається з чотирьох функціональних підсистем, що взаємодіють у реальному часі:

```
+───────────────────────────────────────────────────────────────────────────+
| СТРУКТУРА СТРЕС-ДІАГНОСТИЧНОГО КОМПЛЕКСУ NFF STRESS SUITE                 |
|                                                                           |
|  1. Генератор стресових патернів пам'яті (Pattern Engine):                |
|     - Walking Ones / Zeros ──> Виявлення обривів адресних ліній BGA       |
|     - Checkerboard / Inverted ──> Максимізація наводок (Crosstalk)        |
|     - PRBS-31 / Random Burst ──> Генерація імпульсних просідань живлення  |
|                                                                           |
|  2. Обчислювальне стрес-ядро (ALU & Cache Saturator):                     |
|     - Безперервні векторні та матричні обчислення (FPU/SIMD)              |
|     - Примусове скидання та інвалідація ліній кешу (D-Cache thrashing)    |
|                                                                           |
|  3. Монітор транзиторних збоїв (Glitch & Anomaly Detector):               |
|     - Безперервний підрахунок бітових інверсій та CRC-помилок             |
|     - Фіксація латентності відповідей периферії (Timeout watchdog)        |
|                                                                           |
|  4. Генератор діагностичного звіту RMA (Report Builder):                  |
|     - Локалізація дефектної бітової лінії або адресного діапазону         |
|     - Формування класифікаційного вердикту для сервісного інженера        |
+───────────────────────────────────────────────────────────────────────────+
```

### Багатопотокова модель паралельного стрес-навантаження

Для систем на базі багатоядерних SoC або мікроконтролерів із контролерами прямого доступу (DMA) стрес-комплекс реалізує асинхронну модель навантаження:
1. **Потік 1 (Core Memory Engine):** Виконує послідовну генерацію та верифікацію математичних патернів у тестовому буфері пам'яті.
2. **Потік 2 (FPU / ALU Burner):** Завантажує математичний співпроцесор безперервним розрахунком матричних перетворень та CORDIC-алгоритмів, підтримуючи локальну температуру кристала на піковому рівні.
3. **Потік 3 (DMA Bus Saturator):** Запускає фонову циклічну пересилку псевдовипадкових пакетів між портами SPI, QSPI та внутрішньою пам'яттю, створюючи арбітражні конфлікти на матриці шин (*AHB/AXI Bus Matrix Crossbar*).
4. **Потік 4 (High-Frequency Interrupt Injector):** Апаратний таймер генерує періодичні переривання з частотою до 100 кГц. Це тестує механізм збереження та відновлення контексту процесора (*Stack Push/Pop operations*) під час навантаження шин.

## Налаштування апаратної підсистеми пам'яті: кешування та MPU

Під час проведення стрес-тестування на сучасних високоефективних мікроконтролерах (ARM Cortex-M7, Cortex-R, Cortex-A) критично важливо правильно налаштувати модуль захисту пам'яті (*MPU, Memory Protection Unit*) та контролер кешу (*D-Cache*):

1. **Небезпека кешування даних:** Якщо тестовий буфер пам'яті позначено атрибутом `Cacheable (Write-Back / Write-Through)`, операції запису та читання будуть обслуговуватися внутрішнім швидкісним кешем першого рівня (L1). Зовнішня шина даних та фізичні виводи BGA залишаться ненавантаженими, а дефектні паяні з'єднання не будуть протестовані.
2. **Конфігурація MPU:** Тестовий регіон пам'яті повинен бути явно сконфігурований як `Non-Cacheable (Normal memory)` або `Device / Strongly-Ordered`.
3. **Бар'єри пам'яті:** Між фазами запису та верифікації обов'язково викликаються інструкції бар'єрів пам'яті:
   - `__DMB()` (*Data Memory Barrier*) — гарантує завершення всіх попередніх транзакцій запису до початку наступної операції.
   - `__DSB()` (*Data Synchronization Barrier*) — призупиняє виконання конвеєра до завершення всіх шинних операцій.
   - `__ISB()` (*Instruction Synchronization Barrier*) — очищає конвеєр інструкцій процесора.

## Реалізація стрес-комплексу на C99 та C++20

Нижче наведено повний вихідний код комплексу стрес-тестування. Код спроєктований як для роботи на вбудованих bare-metal мікроконтролерах, так і під керуванням RTOS або вбудованого Linux у складі автоматизованих діагностичних стендів.

:::tabs
```c
/* nff_stress_suite.h - C99 інтерфейс комплексу стрес-тестування NFF */
#ifndef NFF_STRESS_SUITE_H
#define NFF_STRESS_SUITE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define NFF_TEST_BUFFER_SIZE      (16U * 1024U) /* 16 КБ тестового буфера */
#define NFF_MAX_ERROR_LOG_ENTRIES 32U

/* Типи тестових стрес-патернів */
typedef enum {
    PATTERN_CHECKERBOARD = 0,
    PATTERN_WALKING_ONES,
    PATTERN_WALKING_ZEROS,
    PATTERN_BUS_INVERSION,
    PATTERN_PRBS31_RANDOM,
    PATTERN_COUNT
} stress_pattern_type_t;

/* Запис журналу знайденої інтермітуючої помилки */
typedef struct {
    uint32_t timestamp_ms;       /* Час виявлення збою */
    uint32_t memory_offset;      /* Зсув у тестовому буфері */
    uint32_t expected_val;       /* Очікуване значення */
    uint32_t actual_val;         /* Фактично прочитане значення */
    uint32_t xor_diff;           /* Маска спотворених бітів (Actual ^ Expected) */
    uint8_t  pattern_type;       /* Тип патерну, на якому виник збій */
    uint8_t  reserved[3];
} error_log_entry_t;

/* Підсумкова статистика стрес-сесії */
typedef struct {
    uint64_t total_cycles;       /* Загальна кількість виконаних проходів */
    uint64_t total_words_tested; /* Перевірено 32-бітних слів */
    uint32_t error_count;        /* Кількість зафіксованих бітових збоїв */
    uint32_t stuck_at_ones;      /* Помилки типу "залипання в 1" */
    uint32_t stuck_at_zeros;     /* Помилки типу "залипання в 0" */
    uint32_t bridge_faults;      /* Підозра на замикання сусідніх ліній */
    uint32_t duration_ms;        /* Тривалість тесту в мілісекундах */
    uint8_t  is_aborted;         /* Прапорець переривання через критичний збій */
    uint8_t  reserved[3];
} stress_stats_t;

/* Структура контексту стрес-двигуна */
typedef struct {
    uint32_t buffer[NFF_TEST_BUFFER_SIZE / sizeof(uint32_t)];
    error_log_entry_t error_log[NFF_MAX_ERROR_LOG_ENTRIES];
    stress_stats_t stats;
    uint32_t prbs_state;
    uint32_t start_time_ms;
} stress_suite_context_t;

/* Публічний API */
void nff_suite_init(stress_suite_context_t *ctx);
bool nff_suite_run_cycle(stress_suite_context_t *ctx, uint32_t current_time_ms);
void nff_suite_generate_report(const stress_suite_context_t *ctx, char *out_buffer, size_t max_len);
uint32_t nff_suite_get_error_count(const stress_suite_context_t *ctx);

#endif /* NFF_STRESS_SUITE_H */
```
```cpp
/* nff_stress_suite.hpp - C++20 об'єктно-орієнтований стрес-комплекс */
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <string_view>
#include <expected>
#include <algorithm>
#include <numeric>
#include <bit>

namespace notary::stress {

enum class PatternType : uint8_t {
    Checkerboard = 0,
    WalkingOnes,
    WalkingZeros,
    BusInversion,
    Prbs31Random,
    Count
};

struct ErrorLogEntry {
    uint32_t timestamp_ms{0};
    uint32_t memory_offset{0};
    uint32_t expected_val{0};
    uint32_t actual_val{0};
    uint32_t xor_diff{0};
    PatternType pattern{PatternType::Checkerboard};

    [[nodiscard]] constexpr uint32_t flipped_bits_count() const noexcept {
        return static_cast<uint32_t>(std::popcount(xor_diff));
    }
};

struct StressStats {
    uint64_t total_cycles{0};
    uint64_t total_words_tested{0};
    uint32_t error_count{0};
    uint32_t stuck_at_ones{0};
    uint32_t stuck_at_zeros{0};
    uint32_t bridge_faults{0};
    uint32_t duration_ms{0};
    bool is_aborted{false};
};

enum class SuiteError {
    BufferTooSmall,
    ExecutionTimeout,
    CriticalMemoryFailure
};

template <size_t BufferSizeBytes = 16 * 1024, size_t MaxLogs = 32>
class StressSuite {
public:
    static constexpr size_t WordCount = BufferSizeBytes / sizeof(uint32_t);

    constexpr StressSuite() noexcept {
        reset();
    }

    void reset() noexcept {
        std::fill(buffer_.begin(), buffer_.end(), 0U);
        stats_ = {};
        log_count_ = 0;
        prbs_state_ = 0x55AA55AAU;
    }

    bool run_iteration(uint32_t current_time_ms) noexcept;
    
    [[nodiscard]] const StressStats& get_stats() const noexcept { return stats_; }
    [[nodiscard]] std::span<const ErrorLogEntry> get_logs() const noexcept {
        return std::span<const ErrorLogEntry>(error_logs_.data(), log_count_);
    }

    void print_summary_report(std::span<char> out_report) const noexcept;

private:
    void execute_pattern_test(PatternType type, uint32_t current_time_ms) noexcept;
    void log_fault(uint32_t offset, uint32_t expected, uint32_t actual,
                   PatternType pattern, uint32_t time_ms) noexcept;
    uint32_t next_prbs31() noexcept;

    std::array<uint32_t, WordCount> buffer_{};
    std::array<ErrorLogEntry, MaxLogs> error_logs_{};
    size_t log_count_{0};
    StressStats stats_{};
    uint32_t prbs_state_{0x55AA55AAU};
};

} // namespace notary::stress
```
:::

Нижче наведено реалізацію генерації патернів, стрес-алгоритмів та звітності:

:::tabs
```c
/* nff_stress_suite.c - C99 реалізація логіки виявлення дефектів */
#include "nff_stress_suite.h"
#include <string.h>
#include <stdio.h>

/* Лінійний конгруентний генератор / PRBS-31 */
static uint32_t prbs31_step(uint32_t *state) {
    uint32_t b31 = (*state >> 30) & 1U;
    uint32_t b28 = (*state >> 27) & 1U;
    uint32_t new_bit = b31 ^ b28;
    *state = ((*state << 1U) | new_bit) & 0x7FFFFFFFU;
    return *state;
}

void nff_suite_init(stress_suite_context_t *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(stress_suite_context_t));
    ctx->prbs_state = 0x5A5A5A5AU;
}

static void log_error(stress_suite_context_t *ctx, uint32_t offset, uint32_t expected,
                      uint32_t actual, stress_pattern_type_t pattern, uint32_t time_ms) {
    ctx->stats.error_count++;

    uint32_t diff = expected ^ actual;
    if ((actual & diff) == diff) {
        ctx->stats.stuck_at_ones++;
    } else if ((~actual & diff) == diff) {
        ctx->stats.stuck_at_zeros++;
    } else {
        ctx->stats.bridge_faults++;
    }

    if (ctx->stats.error_count <= NFF_MAX_ERROR_LOG_ENTRIES) {
        size_t idx = ctx->stats.error_count - 1U;
        ctx->error_log[idx].timestamp_ms = time_ms;
        ctx->error_log[idx].memory_offset = offset;
        ctx->error_log[idx].expected_val = expected;
        ctx->error_log[idx].actual_val = actual;
        ctx->error_log[idx].xor_diff = diff;
        ctx->error_log[idx].pattern_type = (uint8_t)pattern;
    }
}

static void run_checkerboard(stress_suite_context_t *ctx, uint32_t time_ms) {
    const size_t word_count = NFF_TEST_BUFFER_SIZE / sizeof(uint32_t);
    const uint32_t p1 = 0x55555555U;
    const uint32_t p2 = 0xAAAAAAAAU;

    /* Фаза 1: Прямий запис */
    for (size_t i = 0; i < word_count; ++i) {
        ctx->buffer[i] = (i & 1U) ? p1 : p2;
    }
    /* Фаза 2: Верифікація */
    for (size_t i = 0; i < word_count; ++i) {
        uint32_t expected = (i & 1U) ? p1 : p2;
        uint32_t actual = ctx->buffer[i];
        if (actual != expected) {
            log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), expected, actual, PATTERN_CHECKERBOARD, time_ms);
        }
    }
    /* Фаза 3: Інверсний запис */
    for (size_t i = 0; i < word_count; ++i) {
        ctx->buffer[i] = (i & 1U) ? p2 : p1;
    }
    /* Фаза 4: Інверсна верифікація */
    for (size_t i = 0; i < word_count; ++i) {
        uint32_t expected = (i & 1U) ? p2 : p1;
        uint32_t actual = ctx->buffer[i];
        if (actual != expected) {
            log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), expected, actual, PATTERN_CHECKERBOARD, time_ms);
        }
    }
    ctx->stats.total_words_tested += (word_count * 2U);
}

static void run_walking_bits(stress_suite_context_t *ctx, bool zeros, uint32_t time_ms) {
    const size_t word_count = NFF_TEST_BUFFER_SIZE / sizeof(uint32_t);
    stress_pattern_type_t p_type = zeros ? PATTERN_WALKING_ZEROS : PATTERN_WALKING_ONES;

    for (uint8_t bit = 0; bit < 32; ++bit) {
        uint32_t val = zeros ? ~(1U << bit) : (1U << bit);
        for (size_t i = 0; i < word_count; ++i) {
            ctx->buffer[i] = val;
        }
        for (size_t i = 0; i < word_count; ++i) {
            uint32_t actual = ctx->buffer[i];
            if (actual != val) {
                log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), val, actual, p_type, time_ms);
            }
        }
    }
    ctx->stats.total_words_tested += (word_count * 32U);
}

static void run_bus_inversion(stress_suite_context_t *ctx, uint32_t time_ms) {
    const size_t word_count = NFF_TEST_BUFFER_SIZE / sizeof(uint32_t);
    for (size_t i = 0; i < word_count; ++i) {
        ctx->buffer[i] = (i & 1U) ? 0x00000000U : 0xFFFFFFFFU;
    }
    for (size_t i = 0; i < word_count; ++i) {
        uint32_t expected = (i & 1U) ? 0x00000000U : 0xFFFFFFFFU;
        uint32_t actual = ctx->buffer[i];
        if (actual != expected) {
            log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), expected, actual, PATTERN_BUS_INVERSION, time_ms);
        }
    }
    ctx->stats.total_words_tested += word_count;
}

static void run_prbs_stress(stress_suite_context_t *ctx, uint32_t time_ms) {
    const size_t word_count = NFF_TEST_BUFFER_SIZE / sizeof(uint32_t);
    uint32_t seed = ctx->prbs_state;

    for (size_t i = 0; i < word_count; ++i) {
        ctx->buffer[i] = prbs31_step(&seed);
    }
    seed = ctx->prbs_state;
    for (size_t i = 0; i < word_count; ++i) {
        uint32_t expected = prbs31_step(&seed);
        uint32_t actual = ctx->buffer[i];
        if (actual != expected) {
            log_error(ctx, (uint32_t)(i * sizeof(uint32_t)), expected, actual, PATTERN_PRBS31_RANDOM, time_ms);
        }
    }
    ctx->prbs_state = seed;
    ctx->stats.total_words_tested += word_count;
}

bool nff_suite_run_cycle(stress_suite_context_t *ctx, uint32_t current_time_ms) {
    if (!ctx) return false;

    if (ctx->stats.total_cycles == 0) {
        ctx->start_time_ms = current_time_ms;
    }

    run_checkerboard(ctx, current_time_ms);
    run_walking_bits(ctx, false, current_time_ms);
    run_walking_bits(ctx, true, current_time_ms);
    run_bus_inversion(ctx, current_time_ms);
    run_prbs_stress(ctx, current_time_ms);

    ctx->stats.total_cycles++;
    ctx->stats.duration_ms = current_time_ms - ctx->start_time_ms;

    return (ctx->stats.error_count == 0);
}

uint32_t nff_suite_get_error_count(const stress_suite_context_t *ctx) {
    return ctx ? ctx->stats.error_count : 0U;
}

void nff_suite_generate_report(const stress_suite_context_t *ctx, char *out_buffer, size_t max_len) {
    if (!ctx || !out_buffer || max_len == 0) return;

    snprintf(out_buffer, max_len,
             "--- NFF STRESS TEST SUITE REPORT ---\n"
             "Total Cycles: %llu\n"
             "Words Tested: %llu\n"
             "Duration:     %u ms\n"
             "Total Errors: %u\n"
             "  Stuck-At-1: %u\n"
             "  Stuck-At-0: %u\n"
             "  Bridge/Noise: %u\n"
             "VERDICT:      %s\n",
             (unsigned long long)ctx->stats.total_cycles,
             (unsigned long long)ctx->stats.total_words_tested,
             ctx->stats.duration_ms,
             ctx->stats.error_count,
             ctx->stats.stuck_at_ones,
             ctx->stats.stuck_at_zeros,
             ctx->stats.bridge_faults,
             (ctx->stats.error_count == 0) ? "PASS (No Intermittent Faults Detected)" : "FAIL (Hardware Anomaly Captured)");
}
```
```cpp
/* nff_stress_suite.cpp - C++20 реалізація шаблонних методів стрес-комплексу */
#include "nff_stress_suite.hpp"
#include <cstdio>

namespace notary::stress {

template <size_t BufferSizeBytes, size_t MaxLogs>
uint32_t StressSuite<BufferSizeBytes, MaxLogs>::next_prbs31() noexcept {
    uint32_t b31 = (prbs_state_ >> 30) & 1U;
    uint32_t b28 = (prbs_state_ >> 27) & 1U;
    uint32_t new_bit = b31 ^ b28;
    prbs_state_ = ((prbs_state_ << 1U) | new_bit) & 0x7FFFFFFFU;
    return prbs_state_;
}

template <size_t BufferSizeBytes, size_t MaxLogs>
void StressSuite<BufferSizeBytes, MaxLogs>::log_fault(uint32_t offset, uint32_t expected,
                                                     uint32_t actual, PatternType pattern,
                                                     uint32_t time_ms) noexcept {
    stats_.error_count++;
    uint32_t diff = expected ^ actual;

    if ((actual & diff) == diff) {
        stats_.stuck_at_ones++;
    } else if ((~actual & diff) == diff) {
        stats_.stuck_at_zeros++;
    } else {
        stats_.bridge_faults++;
    }

    if (log_count_ < MaxLogs) {
        error_logs_[log_count_++] = ErrorLogEntry{
            .timestamp_ms = time_ms,
            .memory_offset = offset,
            .expected_val = expected,
            .actual_val = actual,
            .xor_diff = diff,
            .pattern = pattern
        };
    }
}

template <size_t BufferSizeBytes, size_t MaxLogs>
void StressSuite<BufferSizeBytes, MaxLogs>::execute_pattern_test(PatternType type, uint32_t current_time_ms) noexcept {
    switch (type) {
    case PatternType::Checkerboard: {
        constexpr uint32_t p1 = 0x55555555U;
        constexpr uint32_t p2 = 0xAAAAAAAAU;
        for (size_t i = 0; i < WordCount; ++i) {
            buffer_[i] = (i & 1U) ? p1 : p2;
        }
        for (size_t i = 0; i < WordCount; ++i) {
            uint32_t expected = (i & 1U) ? p1 : p2;
            if (buffer_[i] != expected) {
                log_fault(static_cast<uint32_t>(i * 4), expected, buffer_[i], type, current_time_ms);
            }
        }
        stats_.total_words_tested += WordCount;
        break;
    }
    case PatternType::WalkingOnes:
    case PatternType::WalkingZeros: {
        const bool is_zero = (type == PatternType::WalkingZeros);
        for (uint8_t bit = 0; bit < 32; ++bit) {
            const uint32_t val = is_zero ? ~(1U << bit) : (1U << bit);
            std::fill(buffer_.begin(), buffer_.end(), val);
            for (size_t i = 0; i < WordCount; ++i) {
                if (buffer_[i] != val) {
                    log_fault(static_cast<uint32_t>(i * 4), val, buffer_[i], type, current_time_ms);
                }
            }
        }
        stats_.total_words_tested += (WordCount * 32);
        break;
    }
    case PatternType::BusInversion: {
        for (size_t i = 0; i < WordCount; ++i) {
            buffer_[i] = (i & 1U) ? 0x00000000U : 0xFFFFFFFFU;
        }
        for (size_t i = 0; i < WordCount; ++i) {
            uint32_t expected = (i & 1U) ? 0x00000000U : 0xFFFFFFFFU;
            if (buffer_[i] != expected) {
                log_fault(static_cast<uint32_t>(i * 4), expected, buffer_[i], type, current_time_ms);
            }
        }
        stats_.total_words_tested += WordCount;
        break;
    }
    case PatternType::Prbs31Random: {
        uint32_t seed = prbs_state_;
        for (size_t i = 0; i < WordCount; ++i) {
            buffer_[i] = next_prbs31();
        }
        prbs_state_ = seed;
        for (size_t i = 0; i < WordCount; ++i) {
            uint32_t expected = next_prbs31();
            if (buffer_[i] != expected) {
                log_fault(static_cast<uint32_t>(i * 4), expected, buffer_[i], type, current_time_ms);
            }
        }
        stats_.total_words_tested += WordCount;
        break;
    }
    default:
        break;
    }
}

template <size_t BufferSizeBytes, size_t MaxLogs>
bool StressSuite<BufferSizeBytes, MaxLogs>::run_iteration(uint32_t current_time_ms) noexcept {
    execute_pattern_test(PatternType::Checkerboard, current_time_ms);
    execute_pattern_test(PatternType::WalkingOnes, current_time_ms);
    execute_pattern_test(PatternType::WalkingZeros, current_time_ms);
    execute_pattern_test(PatternType::BusInversion, current_time_ms);
    execute_pattern_test(PatternType::Prbs31Random, current_time_ms);

    stats_.total_cycles++;
    return (stats_.error_count == 0);
}

template <size_t BufferSizeBytes, size_t MaxLogs>
void StressSuite<BufferSizeBytes, MaxLogs>::print_summary_report(std::span<char> out_report) const noexcept {
    if (out_report.empty()) return;

    std::snprintf(out_report.data(), out_report.size(),
                  "=== C++20 NFF DIAGNOSTIC REPORT ===\n"
                  "Cycles Completed: %zu\n"
                  "Words Tested:     %zu\n"
                  "Errors Detected:  %u\n"
                  "Stuck at 1 / 0:   %u / %u\n"
                  "Bridge Faults:    %u\n"
                  "Result:           %s\n",
                  stats_.total_cycles,
                  stats_.total_words_tested,
                  stats_.error_count,
                  stats_.stuck_at_ones,
                  stats_.stuck_at_zeros,
                  stats_.bridge_faults,
                  (stats_.error_count == 0) ? "PASS" : "HARDWARE FAULT DETECTED");
}

/* Явна інстанціація типового розміру 16 КБ */
template class StressSuite<16 * 1024, 32>;

} // namespace notary::stress
```
:::

## Інтеграція стрес-комплексу в автоматизований стенд HASS

Для досягнення максимальної достовірності результатів комплекс `nff_stress_suite` повинен запускатися не ізольовано, а як центральне ядро автоматизованої випробувальної станції. Процес інтеграції передбачає три рівні координації:

```
+───────────────────────────────────────────────────────────────────────────+
| ІНТЕГРАЦІЙНИЙ КОНТУР АВТОМАТИЗОВАНОГО ДІАГНОСТИЧНОГО СТЕНДА RMA           |
|                                                                           |
|  1. Керування кліматичною камерою (SCPI / MODBUS через RS-485):           |
|     - Синхронізація термопрофілю (-40 °C <──> +85 °C, градієнт 30 °C/хв)  |
|     - Подача рідкого азоту LN2 для швидкого охолодження                   |
|                                                                           |
|  2. Керування цифровим лабораторним джерелом живлення:                    |
|     - Ступінчастий марджинінг V_core: 3.3 В -> 2.97 В -> 3.63 В          |
|     - Генерація імпульсних провалів тривалістю 50 мкс                     |
|                                                                           |
|  3. Центральний сервер збору діагностичних логів (Ethernet / SWD):        |
|     - Потокове зчитування звітів nff_suite_generate_report()              |
|     - Співставлення часу помилки з показами термопари та напруги живлення |
+───────────────────────────────────────────────────────────────────────────+
```

### Синхронізація марджинінгу напруги та термоциклів

Під час виконання тесту хост-комп'ютер керує лабораторним джерелом живлення за протоколом SCPI, подаючи команди зміни напруги у моменти зміни тестових патернів:

```
:VOLT 2.97          [встановлення нижньої межі Slow Corner V_nom - 10%]
:OUTP ON
*TRG                [запуск циклу nff_suite_run_cycle]
```

Якщо під час просідання напруги до 2.97 В за температури +85 °C у звіті фіксуються помилки на патернах `PATTERN_CHECKERBOARD`, а при 3.30 В за тієї ж температури помилки зникають, це вказує на дефіцит часового запасу *Setup Time* або деградацію вихідного каскаду LDO-стабілізатора.

## Діагностична карта аналізу помилок для сервісного інженера

Аналіз бітових масок, збережених у масиві `error_log`, дає змогу однозначно локалізувати фізичну природу дефекту:

1. **Ізольований бітовий збій (Single Bit Flip, `popcount(xor_diff) == 1`):**
   - Якщо помилка виникає на всіх патернах на одній і тій самій фізичній адресі — це локальна деградація комірки пам'яті (витік заряду через дефект оксиду затвора).
   - Якщо помилка блукає по різних адресах, але завжди вражає одну й ту саму лінію даних (наприклад, біт 14 — маска `0x00004000`) під час вібрації або нагрівання — це мікротріщина паяної кульки BGA або відрив контактного майданчика (*Pad Cratering*) для лінії D14.

2. **Груповий збій шини (Multiple Bit Corruption, `popcount(xor_diff) > 4`):**
   - Виникає виключно під час тесту `PATTERN_BUS_INVERSION` або `PATTERN_PRBS31_RANDOM`. Свідчить про імпульсне падіння напруги живлення ядра через втрату ємності керамічними конденсаторами MLCC або високий динамічний імпеданс провідників живлення плати.

3. **Помилка мостового замикання (Bridge Fault, `stuck_at_ones / stuck_at_zeros == 0`):**
   - Зчитане значення містить комбінацію сусідніх розрядів (наприклад, біт 3 приймає значення біта 4). Свідчить про наявність струмопровідного залишку флюсу, утворення дендритів під BGA-корпусом або коротке замикання між сусідніми мікродоріжками плати при тепловому розширенні.

## Алгоритми виявлення інтермітуючих просідань живлення через аналоговий компаратор MCU

Окремим критичним класом інтермітуючих несправностей є мікросекундні та субмікросекундні транзиторні просідання напруги живлення (*Power Supply Glitches / Brownout Drops*), спричинені деградацією керамічних конденсаторів знеструмлення (MLCC), розтріскуванням контактних майданчиків ліній `V_dd` або стрибками споживання струму під час одночасного перемикання вихідних буферів шини (*Simultaneous Switching Noise, SSN*).

Стандартні вбудовані супервізори живлення мікроконтролера (*Brownout Reset, BOR* або *Power Voltage Detector, PVD*) мають вбудовану затримку фільтрації завад тривалістю 1–10 мкс або призводять до негайного апаратного перезавантаження чипа з повною втратою діагностичного контексту процесора. Для фіксації ультракоротких імпульсних провалів тривалістю від 20 нс до 500 нс комплекс стрес-тестування задіює вбудований швидкодіючий аналоговий компаратор (*High-Speed Analog Comparator, ACMP*) у комбінації з апаратним таймером захоплення та системою асинхронних подій.

```
+───────────────────────────────────────────────────────────────────────────+
| СХЕМА АПАРАТНОГО ДЕТЕКТОРА ТРАНЗИТОРНИХ ПРОСІДАНЬ ЖИВЛЕННЯ (ACMP GLITCH)   |
|                                                                           |
|   V_core / V_dd ────┬───[ R1 ]───┐                                        |
|                     │            │ (INP)                                  |
|                    [C1]         ┌┴──────────┐                             |
|                     │           │  Швидкий  │ COMP_OUT                    |
|                    GND          │ компаратор├────────┬──> Timer Input Cap |
|                                 │ (t_p<30ns)│        │    (Замір тривалості)|
|   VREFINT ───> [ 8-bit DAC ]───>┤           │        └──> Event / EXTI ISR |
|                (Поріг: V_nom-8%)│ (INM)     │             (Атомарний лог) |
|                                 └───────────┘                             |
+───────────────────────────────────────────────────────────────────────────+
```

### Апаратна конфігурація аналогового тракту та порогів спрацьовування

1. **Конфігурація входів компаратора:** Неінвертуючий вхід (`INP`) комутується безпосередньо на тестовану лінію живлення ядра або внутрішній вивід моніторингу `V_cap`. Інвертуючий вхід (`INM`) підключається до внутрішнього джерела опорної напруги (*Bandgap Reference, VREFINT*) через вбудований програмований дільник напруги або допоміжний цифро-аналоговий перетворювач (DAC).
2. **Динамічне калібрування порогу:** Поріг спрацьовування встановлюється на рівні `V_th = V_nom - 0.08 · V_nom` (падіння на 8% від номінальної напруги). Під час кроків навмисного марджинінгу напруги стендом поріг динамічно масштабується програмним драйвером для збереження відносного запасу чутливості.
3. **Апаратний гістерезис:** Для виключення паразитних осциляцій виходу компаратора при повільних коливаннях напруги активується внутрішній гістерезис амплітудою 15–20 мВ.

### Алгоритм асинхронного захоплення та кореляційного аналізу

Робота детектора організована за такою неблокувальною схемою:

1. **Апаратне захоплення часових параметрів:** Вихід компаратора з'єднується з каналом захвату високоточного таймера (*Advanced Resolution Timer*). Спад напруги нижче порогу формує сигнал старту лічильника, а повернення напруги в робочу зону фіксує точну тривалість імпульсного просідання `T_drop` у наносекундах.
2. **Генерація переривання з найвищим пріоритетом:** Фронт спрацьовування компаратора ініціює асинхронне немасковане переривання (*NMI* або *High-Priority ISR*). Обробник за мінімальну кількість тактів зберігає у кільцевий буфер діагностичний зліпок стану: поточний час із точністю до мікросекунди, тривалість провалу, номер активного тестового патерну та адресу поточної операції читання/запису.
3. **Класифікація та кореляція зі збоями пам'яті:** Якщо під час виконання тесту `nff_suite_run_cycle` фіксується спотворення даних у пам'яті, алгоритм зіставляє часову мітку збою `t_fault` із журналом подій компаратора:
   - Якщо `|t_fault - t_drop| < 2 мкс`, збій однозначно класифікується як *Power Integrity Drop* (апаратна деградація кіл живлення, висихання ємностей фільтра або дефект стабілізатора).
   - Якщо збій пам'яті стався за стабільної напруги живлення (жодного спрацьовування компаратора за вікно ±100 мкс), дефект класифікується як структурна несправність комірки або порушення часових інтервалів шини (*Signal Integrity / Setup Violation*).

## Метрологічний контроль та апаратна валідація стенда

Перед запуском серійної діагностики RMA-партій сервісна лабораторія проводить процедуру валідації діагностичного стенда (*Proof of Screen / POSS*), щоб гарантувати, що стендове обладнання не генерує хибнопозитивних збоїв:

1. **Калібрування еталонним зразком (Golden Unit Testing):**
   - Спеціально підготовлений зразок виробу із завідомо бездоганними параметрами витримує 100 циклів тесту `nff_stress_suite` при екстремальних напругах (`V_nom ± 12%`) та температурах від -45 °C до +95 °C без жодного збою. Це підтверджує, що сам тестовий алгоритм не перевищує конструктивних меж міцності здорового виробу.
2. **Осцилографічний аналіз очної діаграми (Eye Diagram):**
   - До сигнальних ліній шини пам'яті підключають високошвидкісні активні пробники з вхідною ємністю `C_in < 0.5 пФ` та смугою пропускання не менше ніж 4 ГГц. Під час виконання тесту `PATTERN_PRBS31_RANDOM` фіксується розкриття очної діаграми (*Eye Opening*), джиттер фронтів (*Total Jitter*) та запас по амплітуді напруги (шумовий імунітет повинен складати не менше ніж 35% від логічного розмаху).
3. **Тепловізійний моніторинг (FLIR Thermal Imaging):**
   - Інфрачервона камера фіксує просторовий розподіл тепла по поверхні друкованої плати під час тестування. Будь-який локальний перегрів пасивного компонента (наприклад, розігрів блокувального конденсатора вище +65 °C через надмірний струм витоку) однозначно ідентифікує прихований внутрішній дефект ще до його повного електричного пробою.

## Регламент діагностичного просіювання на RMA-лінії

Повний технологічний процес діагностики повернення, запідозреного у статусі NFF, регламентується такою послідовністю операцій:

```
+───────────────────────────────────────────────────────────────────────────+
| РЕГЛАМЕНТНИЙ ПРОФІЛЬ СТРЕС-ПРОСІЮВАННЯ HASS ДЛЯ ВХІДНИХ ПОВЕРНЕНЬ         |
|                                                                           |
|  Етап 1: Термошок (-40 °C <──> +85 °C, швидкість 30 °C/хв, 4 цикли).     |
|          Паралельно виконується: nff_suite_run_cycle() при V_nom.         |
|                                                                           |
|  Етап 2: Широкосмугова вібрація (10–2000 Гц, 12 Grms, 10 хв по осі Z).   |
|          Паралельно виконується: nff_suite_run_cycle() при V_nom.         |
|                                                                           |
|  Етап 3: Комбінований стрес (Температура + Вібрація + Voltage Margin).   |
|          - V_core = 2.97 В (-10%) при T = +85 °C (Slow Corner).           |
|          - V_core = 3.63 В (+10%) при T = -40 °C (Fast Corner).           |
|          Повний прохід усіх патернів nff_stress_suite.                    |
|                                                                           |
|  Етап 4: Генерація фінального звіту та електронного сертифіката RMA.     |
+───────────────────────────────────────────────────────────────────────────+
```

Якщо за всі чотири етапи комплекс зафіксував нульову кількість помилок (`error_count == 0`), виріб отримує статус підтвердженої апаратної придатності, а інженерна служба ініціює аудит польових умов замовника (якість ліній живлення, заземлення та кабельних з'єднань).

### Інтеграція з граничним скануванням JTAG / IEEE 1149.1

У випадках, коли мікроконтролер зазнає повного апаратного зависання під час стресу й не здатний сформувати фінальний звіт через внутрішнє програмне забезпечення, діагностичний стенд перемикається на апаратне тестування через інтерфейс JTAG за стандартом IEEE 1149.1 (*Boundary Scan*) або IEEE 1149.6 (*Advanced I/O Testing for AC-Coupled Lines*). 

Контролер стенда завантажує інструкцію `EXTEST` у регістр інструкцій чипа, формуючи повільні тестові перепади рівнів на комірках граничного сканування під час механічного натискання на BGA-корпус спеціальним каліброваним пуансоном із зусиллям 5–15 Н. Якщо під час притиску контакт відновлюється, це слугує остаточним фізичним підтвердженням відриву паяної кульки або кратерування майданчика.

## Розбір реальних виробничих кейсів локалізації NFF

Нижче наведено три реальні інженерні сценарії з практики розслідування повернень високонадійного обладнання:

### Сценарій 1: Мікротріщина кульки BGA кутового виводу процесора

- **Симптом у клієнта:** Періодичне спонтанне зависання процесора після 2–3 годин безперервної роботи в закритій шафі автоматики.
- **Діагностика:** Під час розміщення блоку в термокамері за температури +70 °C та запуску тесту `Walking Ones` через 12 хвилин зафіксовано систематичну помилку за маскою `0x00000010` (лінія даних D4). При кімнатній температурі +20 °C помилка повністю зникає.
- **Фізичний аналіз:** Шліфування поперечного зрізу BGA-чипа під оптичним мікроскопом виявило втому паяного шва та горизонтальну тріщину на межі інтерметалічного шару `Ni3Sn4` кутового виводу B12.
- **Коригувальна дія (CAPA):** Впровадження обов'язкового заповнення компаундом *Underfill* під час поверхневого монтажу плати.

### Сценарій 2: Деградація блокувального конденсатора MLCC шини ядра

- **Симптом у клієнта:** Скидання процесора під час активації радіомодуля стільникового зв'язку 4G/LTE.
- **Діагностика:** Тести `Checkerboard` та `Walking Ones` проходять успішно. Проте запуск тесту `Bus Inversion` синхронно з імітацією передачі радіопакетів викликає множинні бітові збої та спрацьовування апаратного детектора PVD.
- **Фізичний аналіз:** Вимірювання імпедансу шини живлення виявило падіння ємності блокувального конденсатора з номінальних 10 мкФ до 0.15 мкФ через внутрішнє розтріскування кераміки при ручному монтажі роз'єму антени.
- **Коригувальна дія (CAPA):** Заміна одного конденсатора типорозміру 0805 на два паралельні конденсатори типорозміру 0402 з м'якими полімерними виводами (*Soft Termination*).

### Сценарій 3: Зрив часового запасу шини QSPI у Slow PVT Corner

- **Симптом у клієнта:** Спотворення конфігураційних файлів при запуску пристрою в літній період на відкритому повітрі.
- **Діагностика:** Зниження напруги живлення до 2.97 В (-10%) за температури +85 °C викликає збій на тесті `PRBS-31 Random`. Зчитування осцилограми виявило, що час встановлення сигналу *Setup Time* скоротився до 1.2 нс при паспортному мінімумі 2.0 нс.
- **Коригувальна дія (CAPA):** Програмна модифікація конфігурації регістрів контролера QSPI у прошивці: перемикання фази стробування даних на півперіоду тактової частоти раніше.

## Висновки та інтеграція в систему управління якістю

Використання комплексу `nff_stress_suite` докорінно змінює процес обробки повернень RMA. Замість суб'єктивного висновку оператора стенда виробник отримує формалізований масив телеметричних даних, який безпосередньо завантажується в систему управління якістю підприємства (*QMS*). 

Кожна зафіксована аномалія автоматично відкриває заявку на інженерне розслідування в системі відстеження дефектів. Це дозволяє вносити превентивні зміни у трасування друкованих плат, оптимізувати температурні профілі оплавлення припою та вдосконалювати схемотехніку кіл живлення задовго до того, як поодинокі польові відмови переростуть у масовий брак серійного продукту.
