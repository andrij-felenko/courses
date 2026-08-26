# 📋 Інтерфейс диспетчера багатоканального зв'язку

Цей інтерфейс визначає апаратно-незалежний програмний контракт для диспетчера каналів зв'язку (Link Arbiter) та мультиплексора резервних радіотрактів (Multi-Bearer Redundancy Manager). Контракт ізолює високорівневу логіку автопілота, системи прийняття рішень або наземної станції керування від деталей конкретних радіомодулів (Wi-Fi, SDR OFDM, LoRa, FSK, Cellular) через уніфіковані таблиці операцій, кільцеві черги пріоритетів та структури метрик фізичного рівня.

## Архітектурні вимоги та модель пам'яті

Інтерфейс спроектовано під жорсткі вимоги вбудованих систем реального часу (RTOS, bare-metal):
1. **Детермінована пам'ять без динамічного виділення:** жодна функція API не викликає `malloc()` чи `free()`. Усі контексти, дескриптори каналів та буфери черг виділяються статично під час компіляції або передаються викликачем при ініціалізації.
2. **Асинхронність та потокобезпечність:** функції відправки та опитування (`send`, `poll_rx`) є неблокуючими. Обробка переривань від трансиверів (GPIO IRQ, DMA completion) ізольована у драйвері носія і взаємодіє з арбітром через кільцеві буфери без блокування (lock-free SPSC ring buffers).
3. **Апаратна незалежність:** перемикання частотних сіток, потужності випромінювання та апаратних ключів комутації антен виконується через стандартизовані покажчики на функції.

## Переліки та коди станів

### Ідентифікатори фізичних носіїв (Bearer ID)

Перелік `bearer_id_t` визначає тип фізичного радіоканалу в системі. Кожен носій має власні частотні, енергетичні та регуляторні характеристики:

:::tabs
```c
typedef enum {
    BEARER_ID_PRIMARY   = 0,  /* Високошвидкісний канал (2.4 ГГц Wi-Fi / 5.8 ГГц OFDM) */
    BEARER_ID_FALLBACK  = 1,  /* Резервний далекобійний канал (Sub-GHz LoRa / FSK) */
    BEARER_ID_RELAY     = 2,  /* Естафетний ретранслятор (Mesh вузол) */
    BEARER_ID_MAX       = 3
} bearer_id_t;
```
```cpp
#include <cstdint>

namespace link_api {

enum class BearerId : uint8_t {
    Primary  = 0,  // Високошвидкісний канал (2.4 ГГц Wi-Fi / 5.8 ГГц OFDM)
    Fallback = 1,  // Резервний далекобійний канал (Sub-GHz LoRa / FSK)
    Relay    = 2,  // Естафетний ретранслятор (Mesh вузол)
    Count    = 3
};

} // namespace link_api
```
:::

- `BEARER_ID_PRIMARY`: високошвидкісний широкосмуговий канал (ширина смуги 10–20 МГц, бітрейт 5–50 Мбіт/с, затримка < 25 мс). Використовується для передачі стисненого цифрового відеопотоку високої чіткості (H.264/H.265) та повної телеметрії MAVLink.
- `BEARER_ID_FALLBACK`: вузькосмуговий субгігагерцовий канал (ширина смуги 62.5–250 кГц, бітрейт 1.2–50 кбіт/с, чутливість до −138 дБм). Використовується для гарантованої доставки критичних команд та стисненого навігаційного статусу під час придушення основного діапазону.
- `BEARER_ID_RELAY`: проміжний радіопроліт через мобільний ретранслятор або сусідній вузол самоорганізованої mesh-мережі.

### Стани автомата арбітра (Arbiter State)

Перелік `arbiter_state_t` описує життєвий цикл вибору активного каналу та режимів деградації:

:::tabs
```c
typedef enum {
    ARBITER_STATE_PRIMARY_ACTIVE    = 0, /* Основний канал справний, повний потік */
    ARBITER_STATE_PRIMARY_DEGRADED  = 1, /* Початок завад/втрат: стиснення телеметрії */
    ARBITER_STATE_SWITCHING         = 2, /* Процес перемикання та РЧ-комутації */
    ARBITER_STATE_FALLBACK_ACTIVE   = 3, /* Робота на резервному каналі */
    ARBITER_STATE_RECOVERY_EVAL     = 4, /* Перевірка стабільності перед поверненням */
    ARBITER_STATE_EMERGENCY_AUTONOMY= 5  /* Всі канали заглушено: активація Failsafe */
} arbiter_state_t;
```
```cpp
namespace link_api {

enum class ArbiterState : uint8_t {
    PrimaryActive     = 0, // Основний канал справний, повний потік
    PrimaryDegraded   = 1, // Початок завад/втрат: стиснення телеметрії
    Switching         = 2, // Процес перемикання та РЧ-комутації
    FallbackActive    = 3, // Робота на резервному каналі
    RecoveryEval      = 4, // Перевірка стабільності перед поверненням
    EmergencyAutonomy = 5  // Всі канали заглушено: активація Failsafe
};

} // namespace link_api
```
:::

- `ARBITER_STATE_PRIMARY_ACTIVE`: лінк функціонує в штатному режимі. Усі три рівні пріоритетів QoS обслуговуються без обмежень.
- `ARBITER_STATE_PRIMARY_DEGRADED`: виявлено погіршення метрик основного каналу (втрати PER 5–25%, падіння SNR). Відеокодек переводиться на мінімальний профіль бітрейту, а для телеметрії вмикається упереджувальне кодування з виправленням помилок (FEC).
- `ARBITER_STATE_SWITCHING`: короткочасний стан (тривалістю від 2 мкс до 10 мс), під час якого здійснюється зміна логічного рівня на GPIO керування РЧ-комутатором антен (RF SPDT Switch) та надсилання службового кадру підтвердження зміни маршруту.
- `ARBITER_STATE_FALLBACK_ACTIVE`: передача переведена на вузькосмуговий трансивер. Відеопотік повністю блокується на вході диспетчера, а телеметрія пакується у бінарний компактний формат.
- `ARBITER_STATE_RECOVERY_EVAL`: основний канал відновив прийом тестових пакетів. Арбітр утримує активним резервний канал до завершення таймера гістерезису тривалістю 4–6 секунд.
- `ARBITER_STATE_EMERGENCY_AUTONOMY`: розрив усіх радіотрактів тривалістю понад встановлений таймаут (типово 3.0 секунди). Викликається аварійний обробник Failsafe.

### Пріоритети обслуговування трафіку (QoS Tiers)

Корисне навантаження розділяється на три взаємовиключні рівні пріоритету:

:::tabs
```c
typedef enum {
    QOS_PRIO_CRITICAL_CMD = 0, /* Команди керування, аварійні переривання */
    QOS_PRIO_TELEMETRY    = 1, /* Основні навігаційні пакети (MAVLink attitude/GPS) */
    QOS_PRIO_BULK_VIDEO   = 2  /* Відеопотік, сенсорні логи (скидаються першими) */
} qos_priority_t;
```
```cpp
namespace link_api {

enum class QosPriority : uint8_t {
    CriticalCommand = 0, // Команди керування, аварійні переривання
    Telemetry       = 1, // Основні навігаційні пакети (MAVLink attitude/GPS)
    BulkVideo       = 2  // Відеопотік, сенсорні логи (скидаються першими)
};

} // namespace link_api
```
:::

При перевантаженні радіоканалу або переході на низькошвидкісний носій черга `QOS_PRIO_BULK_VIDEO` негайно очищується, запобігаючи блокуванню життєво важливих команд `QOS_PRIO_CRITICAL_CMD` у кільцевому буфері.

## Структури даних та метрики каналу

### Метрики фізичного рівня

Структура `bearer_metrics_t` акумулює статистичні та миттєві параметри якості радіоприйому:

:::tabs
```c
typedef struct {
    int16_t  rssi_dbm;         /* Згладжена потужність сигналу (дБм) */
    int8_t   snr_db;           /* Відношення сигнал/шум (дБ) */
    uint8_t  per_percent;      /* Коефіцієнт пакетних втрат (0..100%) */
    uint16_t rtt_ms;           /* Кругова затримка (Round-Trip Time, мс) */
    uint32_t throughput_bps;   /* Поточна пропускна здатність (біт/с) */
    uint32_t last_rx_mono_ms;  /* Монотонний час останнього успішного прийому (мс) */
    uint8_t  composite_score;  /* Інтегральний бал якості (0..100) */
    bool     is_link_alive;    /* Прапорець фізичної доступності трансивера */
} bearer_metrics_t;
```
```cpp
#include <chrono>

namespace link_api {

struct BearerMetrics {
    int16_t  rssiDbm{-120};
    int8_t   snrDb{-20};
    uint8_t  perPercent{100};
    uint16_t rttMs{0};
    uint32_t throughputBps{0};
    std::chrono::milliseconds lastRxMono{0};
    uint8_t  compositeScore{0};
    bool     isLinkAlive{false};
};

} // namespace link_api
```
:::

- `rssi_dbm`: згладжений рівень прийнятого сигналу (Received Signal Strength Indicator), виміряний вхідним підсилювачем у дБм (наприклад, −65 дБм).
- `snr_db`: відношення потужності корисного сигналу до шуму в каналі demodulator SNR (від −20 дБ для LoRa до +30 дБ для чистого Wi-Fi).
- `per_percent`: відсоток втрачених пакетів у межах останнього ковзного вікна розміром 32 кадри.
- `composite_score`: інтегральна оцінка лінка від 0 (повний розрив) до 100 (ідеальний канал), яка використовується алгоритмом арбітражу для прийняття рішень.

### Заголовок мультиплексованого кадру

Кожен пакет, що передається через диспетчер, упаковується в уніфікований бінарний заголовок розміром 8 байтів:

:::tabs
```c
typedef struct {
    uint8_t  version;          /* Версія заголовка протоколу (0x01) */
    uint8_t  bearer_id;        /* Ідентифікатор фізичного каналу відправника */
    uint8_t  qos_prio;         /* Пріоритет корисного навантаження (qos_priority_t) */
    uint8_t  flags;            /* Прапорці кадру: [0]=ACK_REQ, [1]=RELAYED, [2]=COMPRESSED */
    uint16_t sequence_num;     /* Наскрізний монотонний номер пакета */
    uint16_t payload_len;      /* Довжина корисних даних у байтах (0..1024) */
} __attribute__((packed)) mux_frame_header_t;
```
```cpp
#include <cstdint>

namespace link_api {

#pragma pack(push, 1)
struct MuxFrameHeader {
    uint8_t     version{1};
    BearerId    bearerId{BearerId::Primary};
    QosPriority qosPrio{QosPriority::CriticalCommand};
    uint8_t     flags{0};
    uint16_t    sequenceNum{0};
    uint16_t    payloadLen{0};
};
#pragma pack(pop)

} // namespace link_api
```
:::

Бітові прапорці поля `flags`:
- `0x01` (`MUX_FLAG_ACK_REQ`): запит негайного підтвердження доставки від приймача;
- `0x02` (`MUX_FLAG_RELAYED`): кадр пройшов через проміжний вузол-ретранслятор;
- `0x04` (`MUX_FLAG_COMPRESSED`): корисне навантаження стиснене алгоритмом LZ4 або упаковане у дельта-формат;
- `0x08` (`MUX_FLAG_HEARTBEAT`): службовий кадр перевірки цілісності резервного каналу.

## Таблиця операцій фізичного каналу (Bearer Driver Interface)

Кожен драйвер радіомодуля (SX1262, ESP-NOW, Microhard, Wi-Fi raw frame injection) реєструється в системі за допомогою таблиці функцій `bearer_ops_t`:

:::tabs
```c
struct bearer_interface;

typedef struct {
    int  (*init)(struct bearer_interface *self);
    int  (*send)(struct bearer_interface *self, const uint8_t *data, size_t len, qos_priority_t prio);
    int  (*poll_rx)(struct bearer_interface *self, uint8_t *buf, size_t max_len, bearer_metrics_t *out_metrics);
    void (*get_metrics)(struct bearer_interface *self, bearer_metrics_t *out_metrics);
    void (*set_active)(struct bearer_interface *self, bool active);
    int  (*set_frequency_band)(struct bearer_interface *self, uint32_t freq_hz);
} bearer_ops_t;

typedef struct bearer_interface {
    bearer_id_t          id;
    const char          *name;
    const bearer_ops_t  *ops;
    void                *driver_priv;   /* Вказівник на апаратно-залежний контекст драйвера */
    bearer_metrics_t     metrics;
    uint32_t             tx_byte_count;
    uint32_t             rx_byte_count;
    uint32_t             tx_drop_count;
} bearer_interface_t;
```
```cpp
#include <span>
#include <string_view>
#include <expected>

namespace link_api {

enum class DriverError {
    HardwareFault,
    Busy,
    InvalidParameter,
    BufferOverflow
};

class IBearerDriver {
public:
    virtual ~IBearerDriver() = default;
    virtual std::expected<void, DriverError> init() noexcept = 0;
    virtual std::expected<size_t, DriverError> send(std::span<const uint8_t> data, QosPriority prio) noexcept = 0;
    virtual std::expected<size_t, DriverError> pollRx(std::span<uint8_t> buffer, BearerMetrics& outMetrics) noexcept = 0;
    virtual void setActive(bool active) noexcept = 0;
    virtual std::expected<void, DriverError> setFrequency(uint32_t freqHz) noexcept = 0;
};

struct BearerDescriptor {
    BearerId       id;
    std::string_view name;
    IBearerDriver *driver{nullptr};
    BearerMetrics  metrics{};
};

} // namespace link_api
```
:::

Вимоги до функцій таблиці `bearer_ops_t`:
- `init`: виконує базову конфігурацію регістрів чипа, налаштування потужності та калібрування PLL. Повертає 0 при успіху або негативний код помилки.
- `send`: передає сформований буфер у чергу передавача (TX FIFO). Функція не повинна блокувати процесор на час радіопередачі кадру в ефір.
- `poll_rx`: перевіряє наявність прийнятих даних у буфері RX, записує їх у `buf` та оновлює миттєві параметри RSSI/SNR. Якщо даних немає, негайно повертає 0.
- `set_active`: переводить трансивер у режим сну (Standby/Sleep) для економії живлення або відновлює активний прийом (RX Continuous).

## Конфігурація та налаштування арбітра

Параметри порогових значень та часових констант задаються у структурі `arbiter_config_t`:

:::tabs
```c
typedef struct {
    uint8_t  failover_per_thresh;   /* Поріг втрат для переходу на резерв (типово 25%) */
    int16_t  failover_rssi_thresh;  /* Поріг RSSI для переходу на резерв (типово -95 дБм) */
    uint8_t  loss_burst_limit;      /* Ліміт поспіль втрачених пакетів до аварійного скидання */
    
    uint8_t  recovery_per_thresh;   /* Поріг втрат для повернення на основний (типово 5%) */
    uint16_t recovery_dwell_ms;     /* Час стабільності перед поверненням (типово 4000-6000 мс) */
    uint16_t recovery_packet_streak;/* Кількість поспіль успішних пакетів для відновлення */
    
    uint16_t heartbeat_timeout_ms;  /* Таймаут повної тиші перед переходом в автономію (3000 мс) */
    bool     enable_rf_switch_gpio; /* Керувати апаратним RF Switch (SPDT) через GPIO */
    uint8_t  rf_switch_gpio_pin;    /* Номер GPIO для апаратного ключа */
} arbiter_config_t;
```
```cpp
namespace link_api {

struct ArbiterConfig {
    uint8_t  failoverPerThresh{25};
    int16_t  failoverRssiThresh{-95};
    uint8_t  lossBurstLimit{4};

    uint8_t  recoveryPerThresh{5};
    uint16_t recoveryDwellMs{5000};
    uint16_t recoveryPacketStreak{50};

    uint16_t heartbeatTimeoutMs{3000};
    bool     enableRfSwitchGpio{true};
    uint8_t  rfSwitchGpioPin{12};
};

} // namespace link_api
```
:::

Рекомендовані значення конфігурації:
- `failover_per_thresh`: 25% (перемикання при втраті кожного четвертого кадру);
- `loss_burst_limit`: 4 пакети (при частоті 50 Гц це забезпечує реакцію на РЕБ за 80 мс);
- `recovery_dwell_ms`: 5000 мс (захисний бар'єр проти короткочасних пауз у глушінні);
- `heartbeat_timeout_ms`: 3000 мс (час до запуску аварійного набору висоти Failsafe).

## Сигнатури функцій API

:::tabs
```c
/* Ініціалізація внутрішніх структур арбітра та черг пріоритетів */
int arbiter_init(const arbiter_config_t *config);

/* Реєстрація фізичного носія у пулі доступних інтерфейсів */
int arbiter_register_bearer(bearer_interface_t *bearer);

/* Маршрутизація та відправка пакета з урахуванням поточного активного каналу та QoS */
int arbiter_transmit(const uint8_t *payload, size_t len, qos_priority_t prio);

/* Регулярний крок автомата станів: перевірка таймаутів, оновлення PER та гістерезису */
void arbiter_tick(uint32_t current_mono_ms);

/* Отримання поточної діагностики стану диспетчера */
arbiter_state_t arbiter_get_state(void);
bearer_id_t     arbiter_get_active_bearer(void);

/* Реєстрація функції зворотного виклику при зміні активного носія */
typedef void (*on_bearer_switched_cb_t)(bearer_id_t prev_bearer, bearer_id_t new_bearer, arbiter_state_t state);
void arbiter_set_switch_callback(on_bearer_switched_cb_t cb);

/* Реєстрація функції зворотного виклику при переході в аварійну автономію (Failsafe) */
typedef void (*on_emergency_autonomy_cb_t)(uint32_t silent_duration_ms);
void arbiter_set_autonomy_callback(on_emergency_autonomy_cb_t cb);
```
```cpp
#include <functional>

namespace link_api {

using SwitchCallback   = std::function<void(BearerId prevBearer, BearerId newBearer, ArbiterState state)>;
using AutonomyCallback = std::function<void(std::chrono::milliseconds silentDuration)>;

class ILinkArbiterManager {
public:
    virtual ~ILinkArbiterManager() = default;
    virtual std::expected<void, DriverError> initialize(const ArbiterConfig& config) noexcept = 0;
    virtual std::expected<void, DriverError> registerBearer(const BearerDescriptor& bearer) noexcept = 0;
    virtual std::expected<size_t, DriverError> transmit(std::span<const uint8_t> payload, QosPriority prio) noexcept = 0;
    virtual void tick(std::chrono::milliseconds now) noexcept = 0;
    virtual ArbiterState currentState() const noexcept = 0;
    virtual BearerId activeBearerId() const noexcept = 0;
    virtual void setSwitchCallback(SwitchCallback cb) noexcept = 0;
    virtual void setAutonomyCallback(AutonomyCallback cb) noexcept = 0;
};

} // namespace link_api
```
:::

Усі функції повертають `0` у разі успішного виконання або від'ємний код помилки (`-EINVAL` — некоректні параметри, `-ENOMEM` — переповнення черги, `-EBUSY` — трансивер зайнятий відправкою).
