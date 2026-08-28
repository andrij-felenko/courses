# ⚙️ Бітовий пакувальник кадру здоров'я та адаптивний планувальник

Ця вставка містить робочу реалізацію ультракомпактного пакувальника мета-телеметрії здоров'я пристрою, алгоритм десеріалізації для серверного боку та логіку адаптивного планувача діагностики для енергоефективних вбудованих систем. Код оптимізовано для нульового використання динамічної пам'яті (нуль викликів `malloc` або оператора `new`) та детермінованого часу виконання.

## 1. Специфікація 8-байтового діагностичного кадру

Кадр пакує повний діагностичний зріз стану пристрою у фіксовані 8 байтів:

```text
Байт 0: [Reset Cause: 3b] [LowBatt: 1b] [RadioRetry: 1b] [FlashErr: 1b] [SensErr: 1b] [Tamper: 1b]
Байт 1: V_batt (напруга під навантаженням: 2000..4550 мВ з кроком 10 мВ, uint8_t)
Байт 2: ΔV_sag (просадка напруги під час TX: 0..510 мВ з кроком 2 мВ, uint8_t)
Байт 3: [RSSI mapped: 6b (-120..-57 dBm)] [Retries: 2b (0..3+)]
Байт 4: Min Free Heap Watermark (0..65280 байтів у квантах по 256 байтів, uint8_t)
Байт 5: MCU Temperature (-40..+87 °C зі зміщенням +40, uint8_t)
Байт 6-7: Uptime Delta (години безперервної роботи, uint16_t Little-Endian)
```

## 2. Обґрунтування вибору форматів та зміщень

Кожне поле діагностичного кадру оптимізовано під фізичний діапазон і роздільну здатність давачів:

1. **Причина перезавантаження (`Reset Cause`)**: кодується 3 бітами ($2^3 = 8$ можливих значень). Цього достатньо для розділення всіх стандартних апаратних джерел скидання сучасних мікроконтролерів Cortex-M: Power-On Reset, Watchdog Timeout, Brown-Out Reset, Software Reset, HardFault Lockup та Pin Reset.
2. **Напруга батареї (`V_batt`)**: збереження значень від 2000 до 4550 мВ із дискретом 10 мВ охоплює 256 станів. Замість 16-бітного поля ми використовуємо рівно 1 байт без втрати практичної цінності для моніторингу залишку ємності.
3. **Просадка напруги (`ΔV_sag`)**: різниця між напругою холостого ходу та напругою під час активного випромінювання сигналу передавачем (0..510 мВ) масштабується з кроком 2 мВ у 8-бітне число. Це дозволяє серверній аналітиці обчислювати еквівалентний внутрішній опір джерела живлення: `R_int = ΔV_sag / I_tx`.
4. **Якість зв'язку (`RSSI` та `Retries`)**: 6 бітів для RSSI охоплюють діапазон від −120 до −57 дБм із кроком 1 дБм, а 2 біти кодують кількість повторних спроб передачі попереднього кадру (0, 1, 2 або 3+).
5. **Мінімальний залишок купи (`Min Free Heap`)**: квантування по 256 байтів дозволяє умістити діапазон від 0 до 65 280 байтів у 1 байт. Для моніторингу повільних витоків пам'яті гранулярність 256 байтів є цілком достатньою.
6. **Температура чипа (`MCU Temperature`)**: зсув на +40 °C переводить промисловий діапазон −40..+87 °C у беззнаковий діапазон 0..127, що займає 1 байт без використання від'ємних чисел зі знаком.
7. **Час роботи (`Uptime Delta`)**: 16-бітне беззнакове число годин покриває понад 7.4 року безперервної роботи приладу без переповнення лічильника.

## 3. Реалізація пакувальника, розпакувальника та планувальника

Код структуровано у вигляді двох взаємозамінних вкладок: чистий C99 для платформ без підтримки C++ (Bare-Metal Cortex-M0/M3) та ідіоматичний C++20 із суворою типізацією, `std::span` та `std::array`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Причини останнього апаратного або програмного скидання */
typedef enum {
    RESET_CAUSE_POR        = 0, /* Power-On Reset */
    RESET_CAUSE_WDT        = 1, /* Watchdog Timer Timeout */
    RESET_CAUSE_BOR        = 2, /* Brown-Out Reset (провал живлення) */
    RESET_CAUSE_SOFT       = 3, /* Програмне скидання (NVIC_SystemReset) */
    RESET_CAUSE_HARDFAULT  = 4, /* Помилка виконання HardFault / Lockup */
    RESET_CAUSE_PIN        = 5  /* Зовнішній пін NRST */
} reset_cause_t;

/* Вхідна структура сирих метрик здоров'я */
typedef struct {
    reset_cause_t reset_cause;
    bool          low_batt_flag;
    bool          radio_retry_flag;
    bool          flash_error_flag;
    bool          sensor_error_flag;
    bool          tamper_flag;
    uint16_t      v_batt_mv;        /* Напруга під навантаженням, мВ */
    uint16_t      v_sag_mv;         /* Просадка напруги (V_oc - V_load), мВ */
    int8_t        rssi_dbm;         /* Рівень сигналу, dBm (-120..-57) */
    uint8_t       tx_retries;       /* Кількість повторних відправок (0..3+) */
    uint32_t      min_free_heap;    /* Мінімальний залишок купи, байти */
    int8_t        mcu_temp_c;       /* Температура чипа, °C (-40..+87) */
    uint32_t      uptime_hours;     /* Час роботи, години */
} health_metrics_t;

/* Режими роботи діагностичного планувальника */
typedef enum {
    DIAG_MODE_PIGGYBACK_ONLY = 0, /* Звичайний режим: 1 статус-байт до даних */
    DIAG_MODE_FULL_HEARTBEAT = 1, /* Плановий повний кадр (раз на 6-24 год) */
    DIAG_MODE_BURST_ANOMALY  = 2  /* Аварійний сплеск при виявленні деградації */
} diag_schedule_mode_t;

/* Упаковка 8-байтового діагностичного кадру без побітових структур (безпечно до Endianness) */
void pack_health_frame(const health_metrics_t *in, uint8_t out[8]) {
    /* Байт 0: Прапорці та причина перезавантаження */
    uint8_t b0 = ((uint8_t)(in->reset_cause & 0x07) << 5);
    if (in->low_batt_flag)     b0 |= (1U << 4);
    if (in->radio_retry_flag)  b0 |= (1U << 3);
    if (in->flash_error_flag)  b0 |= (1U << 2);
    if (in->sensor_error_flag) b0 |= (1U << 1);
    if (in->tamper_flag)       b0 |= (1U << 0);
    out[0] = b0;

    /* Байт 1: Напруга батареї (2000..4550 мВ -> 0..255, крок 10 мВ) */
    uint16_t v = in->v_batt_mv;
    if (v < 2000) v = 2000;
    if (v > 4550) v = 4550;
    out[1] = (uint8_t)((v - 2000) / 10);

    /* Байт 2: Просадка напруги (0..510 мВ -> 0..255, крок 2 мВ) */
    uint16_t sag = in->v_sag_mv;
    if (sag > 510) sag = 510;
    out[2] = (uint8_t)(sag / 2);

    /* Байт 3: RSSI (-120..-57 -> 0..63) [6 бітів] + Retries (0..3) [2 біти] */
    int8_t r = in->rssi_dbm;
    if (r < -120) r = -120;
    if (r > -57)  r = -57;
    uint8_t rssi_encoded = (uint8_t)(r + 120); /* 0..63 */
    uint8_t retries = in->tx_retries > 3 ? 3 : in->tx_retries;
    out[3] = (uint8_t)((rssi_encoded << 2) | (retries & 0x03));

    /* Байт 4: Мінімум вільної купи (0..65280 байтів, квант 256 байтів) */
    uint32_t heap_q = in->min_free_heap / 256;
    out[4] = (uint8_t)(heap_q > 255 ? 255 : heap_q);

    /* Байт 5: Температура MCU (-40..+87 °C, зміщення +40 -> 0..127) */
    int8_t temp = in->mcu_temp_c;
    if (temp < -40) temp = -40;
    if (temp > 87)  temp = 87;
    out[5] = (uint8_t)(temp + 40);

    /* Байт 6-7: Аптайм у годинах (uint16_t Little-Endian) */
    uint16_t up = (uint16_t)(in->uptime_hours > 65535 ? 65535 : in->uptime_hours);
    out[6] = (uint8_t)(up & 0xFF);
    out[7] = (uint8_t)((up >> 8) & 0xFF);
}

/* Розпаковка 8-байтового кадру на боці сервера */
void unpack_health_frame(const uint8_t in[8], health_metrics_t *out) {
    /* Байт 0 */
    out->reset_cause       = (reset_cause_t)((in[0] >> 5) & 0x07);
    out->low_batt_flag     = (in[0] & (1U << 4)) != 0;
    out->radio_retry_flag  = (in[0] & (1U << 3)) != 0;
    out->flash_error_flag  = (in[0] & (1U << 2)) != 0;
    out->sensor_error_flag = (in[0] & (1U << 1)) != 0;
    out->tamper_flag       = (in[0] & (1U << 0)) != 0;

    /* Байт 1 */
    out->v_batt_mv = (uint16_t)(in[1] * 10 + 2000);

    /* Байт 2 */
    out->v_sag_mv = (uint16_t)(in[2] * 2);

    /* Байт 3 */
    out->rssi_dbm   = (int8_t)((in[3] >> 2) - 120);
    out->tx_retries = in[3] & 0x03;

    /* Байт 4 */
    out->min_free_heap = (uint32_t)(in[4] * 256);

    /* Байт 5 */
    out->mcu_temp_c = (int8_t)(in[5] - 40);

    /* Байт 6-7 */
    out->uptime_hours = (uint32_t)(in[6] | (in[7] << 8));
}

/* Генерація 1 статус-байта для регулярного підсаджування (Piggybacking) */
uint8_t generate_piggyback_status(const health_metrics_t *in) {
    uint8_t status = 0;
    if (in->low_batt_flag || in->v_batt_mv < 3000) status |= (1U << 7);
    if (in->v_sag_mv > 350)                        status |= (1U << 6);
    if (in->radio_retry_flag || in->tx_retries > 2) status |= (1U << 5);
    if (in->flash_error_flag)                      status |= (1U << 4);
    if (in->sensor_error_flag)                     status |= (1U << 3);
    if (in->min_free_heap < 1024)                  status |= (1U << 2);
    return status;
}

/* Оцінка стану та вибір режиму планувальника */
diag_schedule_mode_t evaluate_diag_scheduler(const health_metrics_t *m, uint32_t cycles_since_full) {
    /* Тригери аварійного сплеску (Anomaly Burst) */
    if (m->v_sag_mv > 400 || m->v_batt_mv < 2900 || m->tx_retries >= 3 || m->min_free_heap < 512) {
        return DIAG_MODE_BURST_ANOMALY;
    }

    /* Плановий пульс кожні 36 циклів (раз на 6 годин при 10-хвилинному кроці) */
    if (cycles_since_full >= 36) {
        return DIAG_MODE_FULL_HEARTBEAT;
    }

    return DIAG_MODE_PIGGYBACK_ONLY;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

enum class ResetCause : uint8_t {
    Por        = 0,
    Wdt        = 1,
    Bor        = 2,
    Soft       = 3,
    HardFault  = 4,
    Pin        = 5
};

struct HealthMetrics {
    ResetCause reset_cause       {ResetCause::Por};
    bool       low_batt_flag     {false};
    bool       radio_retry_flag  {false};
    bool       flash_error_flag  {false};
    bool       sensor_error_flag {false};
    bool       tamper_flag       {false};
    uint16_t   v_batt_mv         {3300};
    uint16_t   v_sag_mv          {100};
    int8_t     rssi_dbm          {-85};
    uint8_t    tx_retries        {0};
    uint32_t   min_free_heap     {8192};
    int8_t     mcu_temp_c        {25};
    uint32_t   uptime_hours      {0};
};

enum class DiagScheduleMode : uint8_t {
    PiggybackOnly = 0,
    FullHeartbeat = 1,
    BurstAnomaly  = 2
};

class HealthTelemetryEncoder {
public:
    static constexpr size_t FrameSize = 8;

    static std::array<uint8_t, FrameSize> pack(const HealthMetrics& in) noexcept {
        std::array<uint8_t, FrameSize> out{};

        // Байт 0: Прапорці та причина перезавантаження
        uint8_t b0 = static_cast<uint8_t>(static_cast<uint8_t>(in.reset_cause) << 5);
        if (in.low_batt_flag)     b0 |= (1U << 4);
        if (in.radio_retry_flag)  b0 |= (1U << 3);
        if (in.flash_error_flag)  b0 |= (1U << 2);
        if (in.sensor_error_flag) b0 |= (1U << 1);
        if (in.tamper_flag)       b0 |= (1U << 0);
        out[0] = b0;

        // Байт 1: Напруга під навантаженням (2000..4550 мВ, крок 10 мВ)
        const uint16_t v = std::clamp<uint16_t>(in.v_batt_mv, 2000, 4550);
        out[1] = static_cast<uint8_t>((v - 2000) / 10);

        // Байт 2: Просадка напруги (0..510 мВ, крок 2 мВ)
        const uint16_t sag = std::clamp<uint16_t>(in.v_sag_mv, 0, 510);
        out[2] = static_cast<uint8_t>(sag / 2);

        // Байт 3: RSSI (-120..-57 dBm) + Retries (0..3)
        const int8_t r = std::clamp<int8_t>(in.rssi_dbm, -120, -57);
        const uint8_t rssi_encoded = static_cast<uint8_t>(r + 120);
        const uint8_t retries = std::min<uint8_t>(in.tx_retries, 3);
        out[3] = static_cast<uint8_t>((rssi_encoded << 2) | (retries & 0x03));

        // Байт 4: Мінімальний залишок купи (кванти 256 байтів)
        const uint32_t heap_q = in.min_free_heap / 256;
        out[4] = static_cast<uint8_t>(std::min<uint32_t>(heap_q, 255));

        // Байт 5: Температура MCU (-40..+87 °C зі зміщенням +40)
        const int8_t temp = std::clamp<int8_t>(in.mcu_temp_c, -40, 87);
        out[5] = static_cast<uint8_t>(temp + 40);

        // Байт 6-7: Аптайм у годинах (Little-Endian)
        const uint16_t up = static_cast<uint16_t>(std::min<uint32_t>(in.uptime_hours, 65535));
        out[6] = static_cast<uint8_t>(up & 0xFF);
        out[7] = static_cast<uint8_t>((up >> 8) & 0xFF);

        return out;
    }

    static HealthMetrics unpack(std::span<const uint8_t, FrameSize> in) noexcept {
        HealthMetrics out{};

        // Байт 0
        out.reset_cause       = static_cast<ResetCause>((in[0] >> 5) & 0x07);
        out.low_batt_flag     = (in[0] & (1U << 4)) != 0;
        out.radio_retry_flag  = (in[0] & (1U << 3)) != 0;
        out.flash_error_flag  = (in[0] & (1U << 2)) != 0;
        out.sensor_error_flag = (in[0] & (1U << 1)) != 0;
        out.tamper_flag       = (in[0] & (1U << 0)) != 0;

        // Байт 1
        out.v_batt_mv = static_cast<uint16_t>(in[1] * 10 + 2000);

        // Байт 2
        out.v_sag_mv = static_cast<uint16_t>(in[2] * 2);

        // Байт 3
        out.rssi_dbm   = static_cast<int8_t>((in[3] >> 2) - 120);
        out.tx_retries = in[3] & 0x03;

        // Байт 4
        out.min_free_heap = static_cast<uint32_t>(in[4] * 256);

        // Байт 5
        out.mcu_temp_c = static_cast<int8_t>(in[5] - 40);

        // Байт 6-7
        out.uptime_hours = static_cast<uint32_t>(in[6] | (in[7] << 8));

        return out;
    }

    static uint8_t generatePiggybackStatus(const HealthMetrics& in) noexcept {
        uint8_t status = 0;
        if (in.low_batt_flag || in.v_batt_mv < 3000)  status |= (1U << 7);
        if (in.v_sag_mv > 350)                         status |= (1U << 6);
        if (in.radio_retry_flag || in.tx_retries > 2)  status |= (1U << 5);
        if (in.flash_error_flag)                       status |= (1U << 4);
        if (in.sensor_error_flag)                      status |= (1U << 3);
        if (in.min_free_heap < 1024)                   status |= (1U << 2);
        return status;
    }

    static DiagScheduleMode evaluateScheduler(const HealthMetrics& m, uint32_t cycles_since_full) noexcept {
        if (m.v_sag_mv > 400 || m.v_batt_mv < 2900 || m.tx_retries >= 3 || m.min_free_heap < 512) {
            return DiagScheduleMode::BurstAnomaly;
        }
        if (cycles_since_full >= 36) {
            return DiagScheduleMode::FullHeartbeat;
        }
        return DiagScheduleMode::PiggybackOnly;
    }
};
```
:::

## 4. Інтеграція з операційною системою реального часу (RTOS)

Для безпечного збору діагностичних метрик у багатозадачному середовищі FreeRTOS або Zephyr рекомендується дотримуватися таких правил:

1. **Безпечне опитування пам'яті**: Замість сканування таблиць розподілу пам'яті під час кожної відправки, створіть фонову низькопріоритетну задачу моніторингу (System Health Task), яка опитує `uxTaskGetStackHighWaterMark()` раз на годину та зберігає мінімальні значення в атомарній структурі.
2. **Черга телеметрії без динамічного виділення пам'яті**: Кадри вимірювань сенсорів та діагностики передаються в задачу мережевого стека через статично виділену кільцеву чергу `xQueueCreateStatic()`. Це унеможливлює відмову через дефіцит купи під час підготовки аварійного повідомлення.
3. **Обробка падіння живлення (Brown-Out ISR)**: Переривання від детектора напруги PVD/BOR повинно мати найвищий пріоритет. У тілі обробника ISR встановлюється прапорець критичної аварії живлення, вимикається радіопередавач та ініціюється швидкий запис коду стану в бекап-регістри RTC (Backup SRAM), які живляться від залишкового заряду іоністора.

## 5. Тестування та валідація на хост-машині

Розробку та перевірку пакувальника можна повністю автоматизувати за допомогою модульних тестів (Unit Tests) на комп'ютері розробника (Linux/macOS/Windows) без використання фізичної плати.

Тестовий сценарій перевіряє такі граничні випадки:
- **Коректність відновлення діапазонів (Round-Trip Test)**: генерація випадкових або граничних значень `v_batt_mv = 2000`, `4550`, `3612`, їх упаковка через `pack()` та розпаковка через `unpack()`. Відхилення відновленого значення не повинно перевищувати крок квантування (±10 мВ).
- **Стійкість до переповнення та насичення (Clamping Test)**: передача значень поза допустимими межами (наприклад, `v_batt_mv = 5500 мВ` або `temp = -60 °C`). Функція повинна коректно насичувати вихідні байти без зрізання бітів сусідніх полів.
- **Декларативна перевірка статусних тригерів**: імітація просадки напруги понад 400 мВ повинна автоматично переводити планувальник у стан `DiagScheduleMode::BurstAnomaly`.

## 6. Практичні пастки та особливості реалізації

1. **Чому явні бітові зсуви надійніші за `struct bitfields`**: Стандарт C (ISO C99 §6.7.2.1) залишає порядок упакування бітових полів у слові на розсуд компілятора (Implementation-Defined). Один компілятор пакує поля від молодшого біта до старшого (LSB-first), інший — навпаки (MSB-first). Прямі операції зсуву `<<` та порозрядного `|` гарантують 100% сумісність кадру між будь-яким мікроконтролером і хмарним сервером незалежно від архітектури чи рівня оптимізації компілятора.
2. **Синхронізація вимірювання `V_sag`**: Вимірювання напруги під навантаженням вимагає зчитування АЦП рівно в момент, коли підсилювач потужності (PA) радіомодуля виходить на максимальну потужність передачі (наприклад, через DMA або таймерне переривання, прив'язане до піна PA_EN). Вимірювання до старту передачі дає холосту напругу, а під час передачі — просілу; різниця між ними `ΔV_sag` дозволяє обчислити внутрішній опір комірки: `R_int = ΔV_sag / I_tx`.
3. **Безпека RTOS-метрик**: Виклики збору метрик FreeRTOS (`uxTaskGetStackHighWaterMark`, `xPortGetMinimumEverFreeHeapSize`) не повинні виконуватися всередині критичних секцій з вимкненими перериваннями, оскільки прохід за вказівниками виділених блоків пам'яті може затримати обробку апаратних подій радіомодема.
4. **Вирівнювання та DMA-буфери**: При передачі кадру через SPI або UART у радіомодем переконайтеся, що масив `out[8]` розташований у пам'яті, доступній для контролера DMA (наприклад, у сегменті SRAM, а не у внутрішньому кеші чи стеку функції з коротким життєвим циклом).
