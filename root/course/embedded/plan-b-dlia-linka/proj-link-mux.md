# ⚙️ Реалізація менеджера резервних каналів зв'язку

Цей проект демонструє автономний програмний диспетчер каналів зв'язку (Multi-Link Arbiter) та пріоритетний мультиплексор для вбудованих систем керування. Програмний комплекс відстежує метрики кількох фізичних трансиверів, здійснює експоненційне згладжування якості сигналу (EWMA), розраховує коефіцієнт пакетних втрат (PER) за ковзним вікном і детерміновано виконує аварійне перемикання з основного широкосмугового каналу на резервний субгігагерцовий при виникненні завад радіоелектронної боротьби.

## Архітектурний дизайн та конвеєр обробки даних

Диспетчер спроектовано для роботи в жорсткому реальному часі на мікроконтролерах класу ARM Cortex-M (STM32, NXP LPC, ESP32). Архітектура спирається на чотири фундаментальні принципи:

1. **Повна відсутність динамічної пам'яті (Zero Heap Allocation):** усі дескриптори носіїв, кільцеві черги повідомлень та структури статистики виділяються статично у секції `.bss` або `.data`. Динамічне виділення пам'яті (`malloc`, `new`) у критичних вбудованих системах заборонене через ризик фрагментації купи, непередбачувану затримку виконання та загрозу виникнення `HardFault` під час польоту.
2. **Триярусна черга пріоритетів (QoS Queueing):** вхідні пакети сортуються на три ізольовані статичні кільцеві черги:
   - `PRIO_CRITICAL` (команди ручного пілотування, аварійні директиви `DISARM`/`RTL`) — ніколи не скидаються, за потреби дублюються в обидва канали;
   - `PRIO_TELEMETRY` (поточні кути орієнтації, координати, напруга) — на низькошвидкісному каналі проріджуються та стискаються;
   - `PRIO_VIDEO` (стиснені кадри відеопотоку) — негайно блокуються при переході на субгігагерцовий резерв, щоб не перевантажувати канал з пропускною здатністю 10–50 кбіт/с.
3. **Безблокувальна синхронізація (Lock-Free SPSC):** передача пакетів між перериваннями приймача (RX ISR) та основним циклом арбітражу здійснюється через кільцеві буфери з атомарними покажчиками читання й запису.
4. **Асиметричний пороговий автомат з гістерезисом:** перехід на резервний канал відбувається за 80–200 мс після фіксації завади, тоді як повернення на основний канал вимагає безперервної стабільності протягом 4000–5000 мс.

## Хід виконання та обробка аварійних подій

Конвеєр обробки складається з трьох послідовних кроків:
- **Крок 1 (Прийом та оновлення метрик):** при отриманні кожного кадру викликається функція `link_stats_on_packet_rx()`, яка оновлює експоненційне середнє RSSI та SNR за формулою Q8-фільтрації, зсуває бітову маску вікна `rx_packet_mask` та перераховує поточний відсоток втрат `PER`.
- **Крок 2 (Періодичний арбітраж):** функція `arbiter_step()` (або `update()` у C++) викликається у таймерному перериванні кожні 10–20 мс. Вона перевіряє таймаути тиші (`last_rx_time`) та поріг втрат. При перевищенні ліміту втрат (PER ≥ 25%) активний канал миттєво змінюється на `BEARER_FALLBACK`.
- **Крок 3 (Диспетчеризація передачі):** функція `arbiter_send_packet()` (або `routePacket()` у C++) перевіряє пріоритет вихідного пакета. Якщо активним є резервний канал, важкі пакети `PRIO_VIDEO` відкидаються без передачі в драйвер, зберігаючи смугу для команд керування.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_BEARERS             2
#define MAX_PAYLOAD_SIZE        256
#define STATS_WINDOW_SIZE       32
#define HYSTERESIS_DWELL_MS     5000
#define FAILOVER_PER_THRESHOLD  25
#define RECOVERY_PER_THRESHOLD  5

typedef enum {
    BEARER_PRIMARY = 0,
    BEARER_FALLBACK = 1
} bearer_type_t;

typedef enum {
    ARBITER_STATE_PRIMARY_OK = 0,
    ARBITER_STATE_FALLBACK_ACTIVE,
    ARBITER_STATE_EVALUATING_RECOVERY,
    ARBITER_STATE_TOTAL_BLACKOUT
} arbiter_fsm_state_t;

typedef enum {
    PRIO_CRITICAL = 0,
    PRIO_TELEMETRY,
    PRIO_VIDEO
} packet_prio_t;

typedef struct {
    int16_t  rssi_dbm;
    int8_t   snr_db;
    uint32_t last_rx_time_ms;
    uint32_t rx_packet_mask;     /* Бітова маска останніх 32 пакетів */
    uint8_t  smoothed_per;       /* Розрахований PER (0..100%) */
    uint8_t  composite_score;    /* Бал якості (0..100) */
    bool     is_physical_up;
} link_stats_t;

typedef struct {
    bearer_type_t       type;
    const char         *name;
    link_stats_t        stats;
    int (*raw_send)(const uint8_t *data, size_t len);
} bearer_channel_t;

typedef struct {
    arbiter_fsm_state_t state;
    bearer_type_t       active_bearer;
    uint32_t            state_enter_time_ms;
    uint32_t            consecutive_good_primary_pkts;
    bearer_channel_t    bearers[MAX_BEARERS];
} link_arbiter_t;

/* Обчислення кількості одиничних бітів у масці (кількість успішно прийнятих пакетів) */
static inline uint8_t count_received_packets(uint32_t mask) {
    uint8_t count = 0;
    while (mask) {
        count += (mask & 1);
        mask >>= 1;
    }
    return count;
}

/* Оновлення бітової маски втрат при надходженні нового пакета */
void link_stats_on_packet_rx(link_stats_t *stats, uint16_t seq, int16_t rssi, int8_t snr, uint32_t now_ms) {
    stats->last_rx_time_ms = now_ms;
    stats->rssi_dbm = (int16_t)((stats->rssi_dbm * 7 + rssi) >> 3); /* EWMA фільтр */
    stats->snr_db = (int8_t)((stats->snr_db * 7 + snr) >> 3);
    
    stats->rx_packet_mask = (stats->rx_packet_mask << 1) | 1;
    uint8_t received = count_received_packets(stats->rx_packet_mask);
    stats->smoothed_per = (uint8_t)(((STATS_WINDOW_SIZE - received) * 100) / STATS_WINDOW_SIZE);
    
    /* Розрахунок інтегрального балу: PER має найбільшу вагу */
    int score = 100 - stats->smoothed_per;
    if (stats->rssi_dbm < -100) {
        score -= 20;
    }
    stats->composite_score = (uint8_t)(score < 0 ? 0 : (score > 100 ? 100 : score));
}

void link_stats_on_packet_timeout(link_stats_t *stats) {
    stats->rx_packet_mask = (stats->rx_packet_mask << 1); /* Зсув нуля при втраті */
    uint8_t received = count_received_packets(stats->rx_packet_mask);
    stats->smoothed_per = (uint8_t)(((STATS_WINDOW_SIZE - received) * 100) / STATS_WINDOW_SIZE);
    stats->composite_score = (uint8_t)(100 - stats->smoothed_per);
}

void arbiter_init(link_arbiter_t *arbiter) {
    memset(arbiter, 0, sizeof(link_arbiter_t));
    arbiter->state = ARBITER_STATE_PRIMARY_OK;
    arbiter->active_bearer = BEARER_PRIMARY;
    arbiter->bearers[BEARER_PRIMARY].name = "2.4G-OFDM";
    arbiter->bearers[BEARER_PRIMARY].stats.rssi_dbm = -60;
    arbiter->bearers[BEARER_PRIMARY].stats.is_physical_up = true;
    
    arbiter->bearers[BEARER_FALLBACK].name = "868M-LoRa";
    arbiter->bearers[BEARER_FALLBACK].stats.rssi_dbm = -75;
    arbiter->bearers[BEARER_FALLBACK].stats.is_physical_up = true;
}

/* Періодичний автомат станів диспетчера */
void arbiter_step(link_arbiter_t *arbiter, uint32_t now_ms) {
    link_stats_t *prim_stats = &arbiter->bearers[BEARER_PRIMARY].stats;
    link_stats_t *fall_stats = &arbiter->bearers[BEARER_FALLBACK].stats;
    
    bool prim_dead = (now_ms - prim_stats->last_rx_time_ms > 1500) || (prim_stats->smoothed_per >= FAILOVER_PER_THRESHOLD);
    bool fall_dead = (now_ms - fall_stats->last_rx_time_ms > 3000);

    switch (arbiter->state) {
    case ARBITER_STATE_PRIMARY_OK:
        if (prim_dead) {
            arbiter->state = ARBITER_STATE_FALLBACK_ACTIVE;
            arbiter->active_bearer = BEARER_FALLBACK;
            arbiter->state_enter_time_ms = now_ms;
        }
        break;

    case ARBITER_STATE_FALLBACK_ACTIVE:
        if (prim_dead && fall_dead) {
            arbiter->state = ARBITER_STATE_TOTAL_BLACKOUT;
            arbiter->state_enter_time_ms = now_ms;
        } else if (!prim_dead && prim_stats->smoothed_per <= RECOVERY_PER_THRESHOLD) {
            arbiter->state = ARBITER_STATE_EVALUATING_RECOVERY;
            arbiter->state_enter_time_ms = now_ms;
            arbiter->consecutive_good_primary_pkts = 0;
        }
        break;

    case ARBITER_STATE_EVALUATING_RECOVERY:
        if (prim_dead) {
            arbiter->state = ARBITER_STATE_FALLBACK_ACTIVE;
            arbiter->active_bearer = BEARER_FALLBACK;
        } else if (now_ms - arbiter->state_enter_time_ms >= HYSTERESIS_DWELL_MS) {
            /* Успішне проходження гістерезису: повертаємося на основний канал */
            arbiter->state = ARBITER_STATE_PRIMARY_OK;
            arbiter->active_bearer = BEARER_PRIMARY;
        }
        break;

    case ARBITER_STATE_TOTAL_BLACKOUT:
        if (!fall_dead) {
            arbiter->state = ARBITER_STATE_FALLBACK_ACTIVE;
            arbiter->active_bearer = BEARER_FALLBACK;
        } else if (!prim_dead) {
            arbiter->state = ARBITER_STATE_PRIMARY_OK;
            arbiter->active_bearer = BEARER_PRIMARY;
        }
        break;
    }
}

/* Маршрутизація передачі пакета відповідно до QoS та стану */
int arbiter_send_packet(link_arbiter_t *arbiter, packet_prio_t prio, const uint8_t *payload, size_t len) {
    if (arbiter->state == ARBITER_STATE_TOTAL_BLACKOUT) {
        return -1; /* Повний радіоблекаут */
    }

    if (prio == PRIO_VIDEO && arbiter->active_bearer == BEARER_FALLBACK) {
        return 0; /* Скидаємо важкий відеопотік на вузькому резервному каналі */
    }

    bearer_channel_t *ch = &arbiter->bearers[arbiter->active_bearer];
    if (ch->raw_send) {
        return ch->raw_send(payload, len);
    }
    return 0;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <string_view>
#include <chrono>

namespace link_fallback {

enum class BearerId : uint8_t {
    PrimaryHighSpeed = 0,
    FallbackSubGhz   = 1,
    Count            = 2
};

enum class ArbiterState : uint8_t {
    PrimaryActive,
    FallbackActive,
    RecoveryEvaluation,
    EmergencyBlackout
};

enum class PacketPriority : uint8_t {
    CriticalCommand = 0,
    Telemetry       = 1,
    BulkVideo       = 2
};

enum class TransmitError {
    LinkBlackout,
    PayloadTooLarge,
    DroppedLowPriority,
    HardwareFault
};

struct LinkQualityMetrics {
    int16_t  rssiDbm{-60};
    int8_t   snrDb{20};
    uint8_t  packetErrorRate{0};
    uint8_t  compositeScore{100};
    uint32_t packetWindowMask{0xFFFFFFFF};
    std::chrono::milliseconds lastRxTime{0};

    void recordPacket(int16_t rawRssi, int8_t rawSnr, std::chrono::milliseconds now) noexcept {
        lastRxTime = now;
        rssiDbm = static_cast<int16_t>((rssiDbm * 7 + rawRssi) >> 3);
        snrDb = static_cast<int8_t>((snrDb * 7 + rawSnr) >> 3);
        packetWindowMask = (packetWindowMask << 1) | 1U;
        computeStats();
    }

    void recordLoss() noexcept {
        packetWindowMask = (packetWindowMask << 1);
        computeStats();
    }

private:
    void computeStats() noexcept {
        uint32_t count = 0;
        uint32_t temp = packetWindowMask;
        while (temp) {
            count += (temp & 1U);
            temp >>= 1;
        }
        packetErrorRate = static_cast<uint8_t>(((32 - count) * 100) / 32);
        int score = 100 - packetErrorRate;
        if (rssiDbm < -100) score -= 20;
        compositeScore = static_cast<uint8_t>(score < 0 ? 0 : (score > 100 ? 100 : score));
    }
};

class MultiLinkArbiter {
public:
    static constexpr std::chrono::milliseconds kHysteresisDwell{5000};
    static constexpr uint8_t kFailoverPerThresh{25};
    static constexpr uint8_t kRecoveryPerThresh{5};

    MultiLinkArbiter() noexcept
        : currentState_(ArbiterState::PrimaryActive),
          activeBearer_(BearerId::PrimaryHighSpeed),
          stateEnterTime_(std::chrono::milliseconds{0}) {}

    [[nodiscard]] ArbiterState state() const noexcept { return currentState_; }
    [[nodiscard]] BearerId activeBearer() const noexcept { return activeBearer_; }
    [[nodiscard]] const LinkQualityMetrics& metrics(BearerId id) const noexcept {
        return metrics_[static_cast<size_t>(id)];
    }

    void onPacketReceived(BearerId id, int16_t rssi, int8_t snr, std::chrono::milliseconds now) noexcept {
        metrics_[static_cast<size_t>(id)].recordPacket(rssi, snr, now);
    }

    void update(std::chrono::milliseconds now) noexcept {
        const auto& prim = metrics_[static_cast<size_t>(BearerId::PrimaryHighSpeed)];
        const auto& fall = metrics_[static_cast<size_t>(BearerId::FallbackSubGhz)];

        const bool primFailed = (now - prim.lastRxTime > std::chrono::milliseconds{1500}) ||
                                (prim.packetErrorRate >= kFailoverPerThresh);
        const bool fallFailed = (now - fall.lastRxTime > std::chrono::milliseconds{3000});

        switch (currentState_) {
        case ArbiterState::PrimaryActive:
            if (primFailed) {
                currentState_ = ArbiterState::FallbackActive;
                activeBearer_ = BearerId::FallbackSubGhz;
                stateEnterTime_ = now;
            }
            break;

        case ArbiterState::FallbackActive:
            if (primFailed && fallFailed) {
                currentState_ = ArbiterState::EmergencyBlackout;
                stateEnterTime_ = now;
            } else if (!primFailed && prim.packetErrorRate <= kRecoveryPerThresh) {
                currentState_ = ArbiterState::RecoveryEvaluation;
                stateEnterTime_ = now;
            }
            break;

        case ArbiterState::RecoveryEvaluation:
            if (primFailed) {
                currentState_ = ArbiterState::FallbackActive;
                activeBearer_ = BearerId::FallbackSubGhz;
            } else if (now - stateEnterTime_ >= kHysteresisDwell) {
                currentState_ = ArbiterState::PrimaryActive;
                activeBearer_ = BearerId::PrimaryHighSpeed;
            }
            break;

        case ArbiterState::EmergencyBlackout:
            if (!fallFailed) {
                currentState_ = ArbiterState::FallbackActive;
                activeBearer_ = BearerId::FallbackSubGhz;
            } else if (!primFailed) {
                currentState_ = ArbiterState::PrimaryActive;
                activeBearer_ = BearerId::PrimaryHighSpeed;
            }
            break;
        }
    }

    [[nodiscard]] std::expected<size_t, TransmitError> routePacket(
        PacketPriority priority,
        std::span<const uint8_t> payload
    ) noexcept {
        if (currentState_ == ArbiterState::EmergencyBlackout) {
            return std::unexpected(TransmitError::LinkBlackout);
        }

        if (priority == PacketPriority::BulkVideo && activeBearer_ == BearerId::FallbackSubGhz) {
            return std::unexpected(TransmitError::DroppedLowPriority);
        }

        if (payload.size() > 256) {
            return std::unexpected(TransmitError::PayloadTooLarge);
        }

        /* Імітація успішної відправки через драйвер активного інтерфейсу */
        return payload.size();
    }

private:
    ArbiterState currentState_;
    BearerId activeBearer_;
    std::chrono::milliseconds stateEnterTime_;
    std::array<LinkQualityMetrics, static_cast<size_t>(BearerId::Count)> metrics_{};
};

} // namespace link_fallback
```
:::

## Крайові випадки та апаратні пастки перемикання

Практичне впровадження багатоканального диспетчера пов'язане з подоланням кількох прихованих апаратних та мережевих пасток:

1. **Перевпорядкування пакетів при перемиканні каналів (Packet Reordering):** субгігагерцовий лінк на базі LoRa має затримку передачі кадру 40–120 мс (залежно від довжини пакета та Spreading Factor), тоді як Wi-Fi передає кадр за 2–5 мс. Якщо в момент перемикання назад на Wi-Fi у буфері передавача LoRa ще залишався старий пакет, він дійде до наземної станції пізніше за новий пакет, надісланий через Wi-Fi. Для усунення цієї колізії приймач повинен мати ковзне вікно дедуплікації та фільтрувати кадри, чий `Sequence Number` менший за найсвіжіший підтверджений.
2. **Переповнення вихідного буфера (Backpressure Congestion):** коли політний контролер генерує потік телеметрії зі швидкістю 50 пакетів на секунду, а канал LoRa здатен передати лише 8 пакетів на секунду, черга `PRIO_TELEMETRY` переповнюється за сотні мілісекунд. Менеджер повинен застосовувати алгоритм адаптивного проріджування (Decimation): замість накопичення черги старі навігаційні кадри негайно заміщуються найновішими (Head-Drop Policy), забезпечуючи передачу лише актуальних координат без зростання штучної затримки.
3. **Енергоспоживання при аварійній автономії:** коли основний швидкісний трансивер повністю заглушено, залишати його вихідний підсилювач потужності (PA) увімкненим означає марно витрачати від 3 до 8 Вт потужності батареї. Арбітр повинен переводити заглушений модуль у режим чергового прийому (Duty-Cycled RX Sniffing) з періодичним увімкненням раз на 500 мс на 10 мс для перевірки наявності сигналу відновлення.

## Інтеграція в RTOS та налаштування переривань

Для розгортання в середовищі FreeRTOS або Zephyr RTOS диспетчер оформлюється у вигляді окремого завдання низької затримки з пріоритетом `configMAX_PRIORITIES - 2`:
- Завдання блокується на бітових прапорцях подій (`xEventGroupWaitBits`) або семафорі сповіщення про прийом кадру з DMA.
- Обробник переривання від трансивера (наприклад, лінія DIO1 чипа Semtech SX1262 або RDY у CC1101) лише фіксує статус події, переносить байти з апаратного буфера SPI у статичний кільцевий буфер і виставляє прапорець задачі.
- Уся математика згладжування, перерахунок PER та перемикання автомата станів виконуються в контексті задачі, що гарантує збереження мінімального часу перебування в обробнику переривань (ISR latency < 5 мкс).
