# ⚙️ Шаблони мережевих адаптерів для трьох архетипів зв'язку

Коли прошивка мікроконтролера починає надсилати байти в радіоефір, розробник часто припускається фатальної архітектурної помилки: вбудовує специфічні виклики радіомодема або мережевого стека безпосередньо в логіку збору даних і керування. У результаті логіка аварійного вимкнення реле змішується з очікуванням підтвердження Zigbee, код опитування датчика температури блокується на час пошуку стільникової вежі NB-IoT, а бортовий автопілот втрачає керування через затримку виклику передачі кадру телеметрії.

Щоб ізолювати прикладну логіку від фізичного середовища, застосовують архітектурний шаблон **порту й адаптера** (*Ports and Adapters / Hexagonal Architecture*). Прикладна система взаємодіє з єдиним абстрактним інтерфейсом мережевого адаптера, а три конкретні реалізації реалізують радикально відмінну поведінку, диктовану фізичними обмеженнями свого середовища:
1. **Адаптер розумного дому (*Home Node Adapter*)**: орієнтований на миттєву диспетчеризацію вхідних команд, швидке опитування локальних підписок і реакцію на зовнішні події із затримкою до 20 мс за постійної присутності в мережі;
2. **Адаптер автономного трекера (*Fleet Tracker Adapter*)**: реалізує суворий асинхронний автомат станів живлення, накопичення точок у енергонезалежному кільцевому буфері (Flash) та пакетне вивантаження (*Burst Transmission*) перед повним знеструмленням радіотракту;
3. **Адаптер двоточкового лінка (*P2P Machine-to-Station Link Adapter*)**: підтримує дворівневу пріоритетну чергу пакетів (високопріоритетне керування витісняє низькопріоритетну телеметрію), підрахунок втрат кадрів у реальному часі та апаратний сторожовий таймер втрати зв'язку (*Fail-Safe Watchdog*).

---

### 1. Уніфікований інтерфейс мережевого адаптера

Базовий контракт визначає життєвий цикл адаптера: ініціалізацію апаратних інтерфейсів, періодичне неблокуюче обслуговування автомата станів у головному циклі (*Poll / Tick*), надсилання корисного навантаження із зазначенням пріоритету та отримання вхідних повідомлень через механізм зворотного виклику (*Callback*).

Зверніть увагу на структуру `net_packet_t`: вона використовує статичний буфер фіксованого розміру (64 байти). У вбудованих системах реального часу динамічне виділення пам'яті через `malloc` усередині мережевого драйвера заборонено, оскільки фрагментація купи (*Heap Fragmentation*) неминуче призведе до зависання пристрою після кількох тижнів безперервної роботи.

:::tabs
```c
#ifndef NET_ADAPTER_H
#define NET_ADAPTER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    NET_PRIO_LOW = 0,     /* Фонова телеметрія, логи */
    NET_PRIO_NORMAL = 1,  /* Регулярні виміри, звіти */
    NET_PRIO_CRITICAL = 2 /* Команди керування, аварійні зупинки */
} net_priority_t;

typedef enum {
    NET_STATE_OFFLINE,
    NET_STATE_CONNECTING,
    NET_STATE_ONLINE,
    NET_STATE_SLEEPING,
    NET_STATE_ERROR
} net_state_t;

typedef struct {
    uint16_t msg_id;
    uint8_t  payload[64];
    uint8_t  len;
    net_priority_t priority;
} net_packet_t;

/* Інтерфейс зворотного виклику для вхідних даних */
typedef void (*net_rx_callback_t)(const net_packet_t *pkt, void *user_data);

typedef struct net_adapter {
    const struct net_adapter_api *api;
    void *driver_ctx;
    net_rx_callback_t rx_cb;
    void *user_data;
} net_adapter_t;

struct net_adapter_api {
    bool (*init)(net_adapter_t *self);
    void (*poll)(net_adapter_t *self, uint32_t now_ms);
    bool (*send)(net_adapter_t *self, const net_packet_t *pkt);
    net_state_t (*get_state)(const net_adapter_t *self);
};

#endif /* NET_ADAPTER_H */
```
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <functional>
#include <expected>

enum class NetPriority : uint8_t {
    Low = 0,
    Normal = 1,
    Critical = 2
};

enum class NetState : uint8_t {
    Offline,
    Connecting,
    Online,
    Sleeping,
    Error
};

enum class NetError : uint8_t {
    BufferFull,
    LinkDown,
    InvalidPayload,
    Timeout
};

struct NetPacket {
    uint16_t msg_id{0};
    std::array<uint8_t, 64> payload{};
    uint8_t len{0};
    NetPriority priority{NetPriority::Normal};

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return std::span<const uint8_t>(payload.data(), len);
    }
};

class INetAdapter {
public:
    using RxCallback = std::function<void(const NetPacket&)>;

    virtual ~INetAdapter() = default;
    [[nodiscard]] virtual bool init() noexcept = 0;
    virtual void poll(uint32_t now_ms) noexcept = 0;
    [[nodiscard]] virtual std::expected<void, NetError> send(const NetPacket& pkt) noexcept = 0;
    [[nodiscard]] virtual NetState state() const noexcept = 0;
    virtual void set_rx_callback(RxCallback cb) noexcept = 0;
};
```
:::

---

### 2. Реалізація 1: Адаптер розумного дому (Smart Home Node)

У домашній локальній мережі головна задача адаптера — забезпечити миттєву реакцію на зовнішні запити. Адаптер перебуває в стані активного прийому або швидкого опитування радіоканалу (*Radio Polling* із періодом 250 мс для сплячих кінцевих пристроїв Zigbee/Thread). Отримавши команду зміни стану (наприклад, увімкнення реле освітлення), він негайно викликає зареєстрований зворотний виклик і надсилає локальне підтвердження (*ACK*).

Паралельно адаптер генерує періодичний контрольний кадр (*Heartbeat*) до локального концентратора кожні 30 секунд. Це дозволяє хабу своєчасно виявити фізичне знеструмлення вузла або пошкодження лінії живлення.

:::tabs
```c
#include <string.h>

#define HOME_RX_QUEUE_SIZE 8

typedef struct {
    net_state_t state;
    uint32_t last_heartbeat_ms;
    uint16_t ack_sequence;
} home_adapter_ctx_t;

static bool home_init(net_adapter_t *self) {
    home_adapter_ctx_t *ctx = (home_adapter_ctx_t *)self->driver_ctx;
    ctx->state = NET_STATE_ONLINE;
    ctx->last_heartbeat_ms = 0;
    ctx->ack_sequence = 0;
    return true;
}

static void home_poll(net_adapter_t *self, uint32_t now_ms) {
    home_adapter_ctx_t *ctx = (home_adapter_ctx_t *)self->driver_ctx;
    
    /* Періодичний локальний Heartbeat до хаба кожні 30 секунд */
    if (now_ms - ctx->last_heartbeat_ms >= 30000) {
        ctx->last_heartbeat_ms = now_ms;
        net_packet_t hb = {
            .msg_id = 0x0001, /* ID: Node Heartbeat */
            .payload = { 0x01 }, /* Статус OK */
            .len = 1,
            .priority = NET_PRIO_LOW
        };
        self->api->send(self, &hb);
    }
}

static bool home_send(net_adapter_t *self, const net_packet_t *pkt) {
    /* Пряма відправка кадру через локальний 802.15.4 / Wi-Fi трансивер */
    (void)self;
    (void)pkt;
    return true;
}

static net_state_t home_get_state(const net_adapter_t *self) {
    const home_adapter_ctx_t *ctx = (const home_adapter_ctx_t *)self->driver_ctx;
    return ctx->state;
}

static const struct net_adapter_api HOME_API = {
    .init = home_init,
    .poll = home_poll,
    .send = home_send,
    .get_state = home_get_state
};
```
```cpp
class HomeNodeAdapter final : public INetAdapter {
public:
    HomeNodeAdapter() = default;

    bool init() noexcept override {
        state_ = NetState::Online;
        last_heartbeat_ms_ = 0;
        return true;
    }

    void poll(uint32_t now_ms) noexcept override {
        if (now_ms - last_heartbeat_ms_ >= 30'000) {
            last_heartbeat_ms_ = now_ms;
            NetPacket hb{};
            hb.msg_id = 0x0001; // ID: Node Heartbeat
            hb.payload[0] = 0x01; // Status OK
            hb.len = 1;
            hb.priority = NetPriority::Low;
            (void)send(hb);
        }
    }

    std::expected<void, NetError> send(const NetPacket& pkt) noexcept override {
        if (state_ != NetState::Online) {
            return std::unexpected(NetError::LinkDown);
        }
        // Пряма відправка кадру через локальний радіотрансивер
        return {};
    }

    NetState state() const noexcept override {
        return state_;
    }

    void set_rx_callback(RxCallback cb) noexcept override {
        rx_callback_ = std::move(cb);
    }

    void on_raw_frame_received(const NetPacket& pkt) noexcept {
        if (rx_callback_) {
            rx_callback_(pkt);
        }
    }

private:
    NetState state_{NetState::Offline};
    uint32_t last_heartbeat_ms_{0};
    RxCallback rx_callback_{};
};
```
:::

---

### 3. Реалізація 2: Адаптер автономного трекера (Fleet Tracker)

У польовому трекері радіомодем LTE-M/NB-IoT під час передачі споживає 250–400 мА. Якщо мережа відсутня, адаптер накопичує точки у статичному кільцевому буфері Flash-пам'яті. Робота модема реалізована як суворий асинхронний автомат станів (*FSM*), що виключає блокування мікроконтролера функціями затримки:
1. `TRACKER_ST_SLEEPING`: модем повністю знеструмлений через силовий ключ (P-MOSFET), струм споживання менше 2.5 мкА;
2. `TRACKER_ST_MODEM_POWERUP`: подача живлення на силову шину модема та імпульс на лінію PWRKEY тривалістю 500 мс;
3. `TRACKER_ST_REGISTERING`: неблокуюче очікування реєстрації в мережі оператора (пошук соти з тайм-аутом);
4. `TRACKER_ST_TRANSMITTING_BATCH`: вивантаження накопичених записів єдиним пакетом через швидкий CoAP/UDP запит;
5. `TRACKER_ST_MODEM_SHUTDOWN`: коректне відключення живлення та повернення в мікроамперний сон.

:::tabs
```c
#define TRACKER_FLASH_BUFFER_SIZE 32

typedef struct {
    uint32_t timestamp;
    int32_t  lat_e7;
    int32_t  lon_e7;
    uint8_t  battery_pct;
} tracker_record_t;

typedef enum {
    TRACKER_ST_SLEEPING,
    TRACKER_ST_MODEM_POWERUP,
    TRACKER_ST_REGISTERING,
    TRACKER_ST_TRANSMITTING_BATCH,
    TRACKER_ST_MODEM_SHUTDOWN
} tracker_fsm_state_t;

typedef struct {
    net_state_t state;
    tracker_fsm_state_t fsm;
    tracker_record_t flash_ring[TRACKER_FLASH_BUFFER_SIZE];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
    uint32_t session_timer_ms;
} tracker_adapter_ctx_t;

static bool tracker_init(net_adapter_t *self) {
    tracker_adapter_ctx_t *ctx = (tracker_adapter_ctx_t *)self->driver_ctx;
    ctx->state = NET_STATE_SLEEPING;
    ctx->fsm = TRACKER_ST_SLEEPING;
    ctx->head = 0;
    ctx->tail = 0;
    ctx->count = 0;
    ctx->session_timer_ms = 0;
    return true;
}

static bool tracker_buffer_point(tracker_adapter_ctx_t *ctx, const tracker_record_t *rec) {
    if (ctx->count >= TRACKER_FLASH_BUFFER_SIZE) {
        /* Перезапис найстарішої точки, якщо буфер переповнений */
        ctx->tail = (ctx->tail + 1) % TRACKER_FLASH_BUFFER_SIZE;
        ctx->count--;
    }
    ctx->flash_ring[ctx->head] = *rec;
    ctx->head = (ctx->head + 1) % TRACKER_FLASH_BUFFER_SIZE;
    ctx->count++;
    return true;
}

static void tracker_poll(net_adapter_t *self, uint32_t now_ms) {
    tracker_adapter_ctx_t *ctx = (tracker_adapter_ctx_t *)self->driver_ctx;

    switch (ctx->fsm) {
    case TRACKER_ST_SLEEPING:
        /* Прокидаємося, якщо накопичилося >5 точок або минула година */
        if (ctx->count >= 5 || (now_ms - ctx->session_timer_ms >= 3600000 && ctx->count > 0)) {
            ctx->fsm = TRACKER_ST_MODEM_POWERUP;
            ctx->session_timer_ms = now_ms;
            ctx->state = NET_STATE_CONNECTING;
        }
        break;

    case TRACKER_ST_MODEM_POWERUP:
        /* Симуляція подачі живлення на модем (PWRKEY затримка 500 мс) */
        if (now_ms - ctx->session_timer_ms >= 500) {
            ctx->fsm = TRACKER_ST_REGISTERING;
            ctx->session_timer_ms = now_ms;
        }
        break;

    case TRACKER_ST_REGISTERING:
        /* Симуляція реєстрації в мережі NB-IoT (до 4 секунд) */
        if (now_ms - ctx->session_timer_ms >= 4000) {
            ctx->fsm = TRACKER_ST_TRANSMITTING_BATCH;
            ctx->state = NET_STATE_ONLINE;
        }
        break;

    case TRACKER_ST_TRANSMITTING_BATCH:
        /* Вивантажуємо всі накопичені пакети одним з'єднанням */
        while (ctx->count > 0) {
            /* Передача точки ctx->flash_ring[ctx->tail] */
            ctx->tail = (ctx->tail + 1) % TRACKER_FLASH_BUFFER_SIZE;
            ctx->count--;
        }
        ctx->fsm = TRACKER_ST_MODEM_SHUTDOWN;
        ctx->session_timer_ms = now_ms;
        break;

    case TRACKER_ST_MODEM_SHUTDOWN:
        /* Вимикаємо живлення модема для нульового витоку струму */
        ctx->state = NET_STATE_SLEEPING;
        ctx->fsm = TRACKER_ST_SLEEPING;
        break;
    }
}

static bool tracker_send(net_adapter_t *self, const net_packet_t *pkt) {
    tracker_adapter_ctx_t *ctx = (tracker_adapter_ctx_t *)self->driver_ctx;
    if (pkt->len >= sizeof(tracker_record_t)) {
        tracker_record_t rec;
        memcpy(&rec, pkt->payload, sizeof(tracker_record_t));
        return tracker_buffer_point(ctx, &rec);
    }
    return false;
}

static net_state_t tracker_get_state(const net_adapter_t *self) {
    const tracker_adapter_ctx_t *ctx = (const tracker_adapter_ctx_t *)self->driver_ctx;
    return ctx->state;
}
```
```cpp
struct TrackerRecord {
    uint32_t timestamp{0};
    int32_t  lat_e7{0};
    int32_t  lon_e7{0};
    uint8_t  battery_pct{0};
};

class FleetTrackerAdapter final : public INetAdapter {
public:
    static constexpr size_t BufferCapacity = 32;

    FleetTrackerAdapter() = default;

    bool init() noexcept override {
        state_ = NetState::Sleeping;
        fsm_ = FsmState::Sleeping;
        head_ = 0;
        tail_ = 0;
        count_ = 0;
        timer_ms_ = 0;
        return true;
    }

    void poll(uint32_t now_ms) noexcept override {
        switch (fsm_) {
        case FsmState::Sleeping:
            if (count_ >= 5 || (now_ms - timer_ms_ >= 3'600'000 && count_ > 0)) {
                fsm_ = FsmState::PowerUpModem;
                timer_ms_ = now_ms;
                state_ = NetState::Connecting;
            }
            break;

        case FsmState::PowerUpModem:
            if (now_ms - timer_ms_ >= 500) {
                fsm_ = FsmState::Registering;
                timer_ms_ = now_ms;
            }
            break;

        case FsmState::Registering:
            if (now_ms - timer_ms_ >= 4'000) {
                fsm_ = FsmState::TransmittingBatch;
                state_ = NetState::Online;
            }
            break;

        case FsmState::TransmittingBatch:
            // Пакетне вивантаження точок через CoAP/UDP
            count_ = 0;
            tail_ = head_;
            fsm_ = FsmState::ShutdownModem;
            timer_ms_ = now_ms;
            break;

        case FsmState::ShutdownModem:
            state_ = NetState::Sleeping;
            fsm_ = FsmState::Sleeping;
            break;
        }
    }

    std::expected<void, NetError> send(const NetPacket& pkt) noexcept override {
        if (pkt.len < sizeof(TrackerRecord)) {
            return std::unexpected(NetError::InvalidPayload);
        }
        TrackerRecord rec;
        std::memcpy(&rec, pkt.payload.data(), sizeof(TrackerRecord));

        if (count_ >= BufferCapacity) {
            tail_ = (tail_ + 1) % BufferCapacity;
            count_--;
        }
        buffer_[head_] = rec;
        head_ = (head_ + 1) % BufferCapacity;
        count_++;
        return {};
    }

    NetState state() const noexcept override {
        return state_;
    }

    void set_rx_callback(RxCallback cb) noexcept override {
        rx_callback_ = std::move(cb);
    }

private:
    enum class FsmState {
        Sleeping,
        PowerUpModem,
        Registering,
        TransmittingBatch,
        ShutdownModem
    };

    NetState state_{NetState::Sleeping};
    FsmState fsm_{FsmState::Sleeping};
    std::array<TrackerRecord, BufferCapacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
    uint32_t timer_ms_{0};
    RxCallback rx_callback_{};
};
```
:::

---

### 4. Реалізація 3: Адаптер двоточкового лінка (P2P Machine-to-Station)

Для каналу «апарат-станція» неприпустимі блокуючі виклики та непередбачувані затримки буферизації. Адаптер реалізує прямий потік пакетів із суворою пріоритезацією: критичні команди керування передаються негайно, витісняючи фонову телеметрію.

Одночасно працює апаратний таймер втрати зв'язку: якщо протягом 1500 мс від станції не надійшло жодного пакету підтвердження чи команди, адаптер переводить статус у `NET_STATE_ERROR`, викликаючи аварійний протокол борту (*Fail-Safe / Return to Home*). Адаптер також аналізує монотонно зростаючі порядкові номери пакетів (*Sequence Numbers*) для безперервної оцінки відсотка втрачених кадрів в умовах радіозавад.

:::tabs
```c
#define P2P_FAILSAFE_TIMEOUT_MS 1500

typedef struct {
    net_state_t state;
    uint32_t last_rx_timestamp_ms;
    uint16_t tx_sequence;
    uint16_t rx_sequence;
    uint32_t packets_lost;
    bool failsafe_triggered;
} p2p_adapter_ctx_t;

static bool p2p_init(net_adapter_t *self) {
    p2p_adapter_ctx_t *ctx = (p2p_adapter_ctx_t *)self->driver_ctx;
    ctx->state = NET_STATE_CONNECTING;
    ctx->last_rx_timestamp_ms = 0;
    ctx->tx_sequence = 0;
    ctx->rx_sequence = 0;
    ctx->packets_lost = 0;
    ctx->failsafe_triggered = false;
    return true;
}

static void p2p_poll(net_adapter_t *self, uint32_t now_ms) {
    p2p_adapter_ctx_t *ctx = (p2p_adapter_ctx_t *)self->driver_ctx;

    /* Контроль тайм-ауту зв'язку */
    if (ctx->state == NET_STATE_ONLINE) {
        if (now_ms - ctx->last_rx_timestamp_ms >= P2P_FAILSAFE_TIMEOUT_MS) {
            ctx->state = NET_STATE_ERROR;
            ctx->failsafe_triggered = true;
            /* Повідомлення автопілоту: перехід у режим аварійного повернення */
        }
    }
}

static bool p2p_send(net_adapter_t *self, const net_packet_t *pkt) {
    p2p_adapter_ctx_t *ctx = (p2p_adapter_ctx_t *)self->driver_ctx;
    ctx->tx_sequence++;

    /* У P2P критичні пакети (керування) витісняють чергу телеметрії */
    if (pkt->priority == NET_PRIO_CRITICAL) {
        /* Негайна передача в RF-трансивер через SPI/UART без буферизації */
        return true;
    }
    
    /* Звичайна телеметрія відправляється, якщо радіоканал не зайнятий */
    return true;
}

static void p2p_on_frame_rx(net_adapter_t *self, const uint8_t *data, uint8_t len, uint16_t seq, uint32_t now_ms) {
    p2p_adapter_ctx_t *ctx = (p2p_adapter_ctx_t *)self->driver_ctx;
    
    /* Скидання таймера Fail-Safe */
    ctx->last_rx_timestamp_ms = now_ms;
    ctx->state = NET_STATE_ONLINE;
    ctx->failsafe_triggered = false;

    /* Підрахунок втрачених кадрів за послідовністю sequence number */
    if (seq > ctx->rx_sequence + 1) {
        ctx->packets_lost += (seq - ctx->rx_sequence - 1);
    }
    ctx->rx_sequence = seq;

    if (self->rx_cb) {
        net_packet_t pkt;
        pkt.msg_id = (data[0] << 8) | data[1];
        pkt.len = len > 64 ? 64 : len;
        memcpy(pkt.payload, data, pkt.len);
        pkt.priority = NET_PRIO_CRITICAL;
        self->rx_cb(&pkt, self->user_data);
    }
}
```
```cpp
class P2PLinkAdapter final : public INetAdapter {
public:
    static constexpr uint32_t FailSafeTimeoutMs = 1500;

    P2PLinkAdapter() = default;

    bool init() noexcept override {
        state_ = NetState::Connecting;
        last_rx_timestamp_ms_ = 0;
        tx_sequence_ = 0;
        rx_sequence_ = 0;
        packets_lost_ = 0;
        failsafe_triggered_ = false;
        return true;
    }

    void poll(uint32_t now_ms) noexcept override {
        if (state_ == NetState::Online) {
            if (now_ms - last_rx_timestamp_ms_ >= FailSafeTimeoutMs) {
                state_ = NetState::Error;
                failsafe_triggered_ = true;
                // Сповіщення підсистеми польотного контролера
            }
        }
    }

    std::expected<void, NetError> send(const NetPacket& pkt) noexcept override {
        tx_sequence_++;
        // Пряме відправлення кадру через радіотрансивер
        return {};
    }

    void on_raw_frame_received(std::span<const uint8_t> frame, uint16_t seq, uint32_t now_ms) noexcept {
        last_rx_timestamp_ms_ = now_ms;
        state_ = NetState::Online;
        failsafe_triggered_ = false;

        if (seq > rx_sequence_ + 1) {
            packets_lost_ += (seq - rx_sequence_ - 1);
        }
        rx_sequence_ = seq;

        if (rx_callback_ && frame.size() >= 2) {
            NetPacket pkt{};
            pkt.msg_id = static_cast<uint16_t>((frame[0] << 8) | frame[1]);
            pkt.len = static_cast<uint8_t>(std::min(frame.size(), size_t{64}));
            std::copy_n(frame.data(), pkt.len, pkt.payload.begin());
            pkt.priority = NetPriority::Critical;
            rx_callback_(pkt);
        }
    }

    [[nodiscard]] NetState state() const noexcept override {
        return state_;
    }

    [[nodiscard]] bool is_failsafe_active() const noexcept {
        return failsafe_triggered_;
    }

    [[nodiscard]] uint32_t lost_packets_count() const noexcept {
        return packets_lost_;
    }

    void set_rx_callback(RxCallback cb) noexcept override {
        rx_callback_ = std::move(cb);
    }

private:
    NetState state_{NetState::Offline};
    uint32_t last_rx_timestamp_ms_{0};
    uint16_t tx_sequence_{0};
    uint16_t rx_sequence_{0};
    uint32_t packets_lost_{0};
    bool failsafe_triggered_{false};
    RxCallback rx_callback_{};
};
```
:::

---

### Пастки проектування та розбір відмов

1. **Блокування обчислювального циклу (*Blocking I/O Trap*)**:
   Адаптер трекера ніколи не повинен виконувати очікування відповіді AT-команд модема через функцію `delay()` або блокуючий цикл. Якщо модем шукає оператора 30 секунд, блокуючий виклик заморозить опитування аварійних давачів та скидання апаратного сторожового таймера (*Watchdog Timer*), що призведе до циклічного перезавантаження плати. Функція `poll()` зобов'язана повертати керування за частки мікросекунди на кожній ітерації.

2. **Зношування Flash-пам'яті в трекерах (*Flash Wear Leveling*)**:
   Якщо енергонезалежний кільцевий буфер точок записується за кожною подією в один і той самий сектор SPI Flash-пам'яті, сектор вийде з ладу після 100 000 циклів запису (менше 6 місяців при щохвилинному записі). Необхідно або кешувати записи в енергонезалежній пам'яті з необмеженим ресурсом (FRAM або RTC Backup RAM), або застосовувати циклічний алгоритм вирівнювання зносу секторів.

3. **Стрибки струму при вмиканні модема (*Inrush Current & Voltage Sag*)**:
   Під час виходу стільникового модема в ефір імпульсне споживання струму може сягати 2 Ампер протягом 500 мікросекунд. Якщо внутрішній опір батареї або індуктивність доріжок живлення перевищують допустимі межі, напруга на шині живлення мікроконтролера просяде нижче порогу скидання за низькою напругою (*Brown-Out Reset, BOR*). Це викликає раптове перезавантаження процесора в момент відкриття радіопередавача. Рішення вимагає встановлення танталових конденсаторів великої ємності (470–1000 мкФ з низьким ESR) безпосередньо біля виводів живлення модема.

4. **Хибне спрацьовування Fail-Safe у P2P**:
   Якщо тайм-аут втрати зв'язку встановлено занадто малим (наприклад, 100 мс), короткочасна завада від пролітаючого об'єкта або плановий стрибок частоти в алгоритмі FHSS викличе аварійне повернення борту посеред виконання швидкісного маневру. Безпечний тайм-аут має становити не менше 3–5 періодів відправки контрольного кадру (*Heartbeat*), а перехід до аварійних режимів повинен відбуватися ступенево через фазу м'якої стабілізації.
