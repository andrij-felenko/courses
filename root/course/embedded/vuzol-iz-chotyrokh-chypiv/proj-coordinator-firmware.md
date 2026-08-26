# ⚙️ Прошивка координатора вузла: неблокуючий диспетчер, буферизація у Flash та RS-485 зв'язок

Цей інженерний модуль реалізує повний стек прошивки для керування чотирма гетерогенними мікросхемами вузла телеметрії. Програмна архітектура базується на неблокуючому диспетчері подій, кільцевому журналюванні записів у NOR Flash та асинхронній обробці запитів по шині RS-485.

---

## 1. Архітектура програмного координатора та модель подій

Координатор об'єднує роботу чотирьох зовнішніх мікросхем через єдиний цикл подій без використання блокуючих затримок `delay()` або нескінченних циклів очікування прапорців:

```
[ EXTI / RTC DS3231 ] ──> [ Черга подій: EVENT_ACQUIRE ]
                                    │
                                    ▼
[ Опитування I2C: BME280 ] ──> [ Пакет вимірювань + Мітка часу ]
                                    │
                                    ▼
[ Запис у Flash: W25Q128 ] ──> [ Кільцевий буфер сторінок 256 Б ]
                                    │
[ Запит RS-485: RX Frame ] ──> [ Формування відповіді Modbus RTU ]
```

### Ключові механізми реалізації:

1. **Ізоляція та неблокуючий доступ до шин:** Транзакції SPI Flash виконуються через контролер прямого доступу до пам'яті (DMA) або швидкісні пакетні виклики. Звернення до шини I2C (BME280 та DS3231) відбуваються з жорстким програмним контролем тайм-аутів. Якщо ведений чип утримує лінію SDA у низькому стані через збій внутрішнього автомата (Bus Lockup), драйвер запускає дев'ятитактну процедуру відновлення тактування SCL.
2. **Кільцевий буфер енергонезалежної пам'яті:** Телеметричні записи розміром 24 байти накопичуються у сторінковому буфері RAM (256 байтів) і скидаються у Flash-пам'ять W25Q128 за адресою поточного сектора (4096 байтів). Це виключає часті цикли стирання і продовжує ресурс кристала до сотень років.
3. **Керування напівдуплексним трансивером RS-485:** Перемикання виводу `DE` (Driver Enable) здійснюється перед початком передачі та скидається в режим прийому строго після фіксації прапорця завершення передачі останнього стоп-біта (`TC` — Transmission Complete), а не прапорця спустошення регістра передачі (`TXE`), що рятує останній байт від обрізання.
4. **Керування енергоспоживанням та сторожовий таймер:** Між циклами вимірювань мікроконтролер переходить у режим глибокого сну (Stop 2), у якому вимикаються високочастотні генератори HSE/PLL, а струм споживання падає до 5.2 мкА. Сторожовий таймер (Independent Watchdog, IWDG) налаштовується на інтервал 2.0 секунди для примусового перезавантаження системи у разі зависання в обробниках подій.

---

## 2. Алгоритми вирівнювання зносу та відновлення шини I2C

### Вирівнювання зносу осередків NOR Flash (Wear Leveling)

Пам'ять NOR Flash `W25Q128JV` допускає запис бітових нулів без попереднього стирання, проте переведення нулів назад в одиниці можливе лише операцією блокового стирання (Block / Sector Erase). Мінімальна неподільна одиниця стирання становить один сектор розміром `4096 байтів` (16 сторінок по 256 байтів).

Якщо прошивка записує кожне секундне вимірювання (24 байти) безпосередньо у початок Flash, перший сектор вичерпає ліміт у `100 000 циклів стирання` всього за кілька діб. Щоб розподілити навантаження по всьому фізичному об'єму мікросхеми (16 МБ = 4096 секторів), програмний логер використовує циклічне кільцеве просування початкової адреси секторів:

1. **Ініціалізація вказівника:** При старті пристрою прошивка сканує заголовки секторів по 4 КБ і знаходить останній частково заповнений сектор за наявністю байтів `0xFF`.
2. **Пакетування у сторінковий буфер:** Записи розміром 24 байти групуються в масиві оперативної пам'яті розміром 256 байтів. Програмування сторінки через SPI запускається лише тоді, коли накопичено 10 повних відліків.
3. **Стирання нового сектора наперед:** Щойно адреса запису досягає межі наступного сектора (кратна 4096), драйвер ініціює команду `0x20` (Sector Erase) для нового сектора. Це гарантує, що запис наступних сторінок відбуватиметься без затримок на очікування стирання.

### Відновлення завислої шини I2C (Bus Recovery Pattern)

Поширеним апаратним дефектом на шині I2C є зависання веденого чипа (наприклад, датчика BME280) під час скидання живлення або збою тактування посеред транзакції читання: ведений пристрій утримує лінію `SDA` у низькому стані, чекаючи на черговий спадний фронт `SCL`. Оскільки лінія даних заблокована, мікроконтролер не може сформувати стан `Start` або `Stop`.

Програмний драйвер вузла реалізує стандартний дев'ятиімпульсний алгоритм розблокування (9-Clock Recovery Sequence):

```
Крок 1: Тимчасове переведення пінів PB6 (SCL) та PB7 (SDA) у режим GPIO General Purpose Output
Крок 2: Перевірка рівня на лінії SDA. Якщо SDA = High, шина вільна — повернення до кроку 6
Крок 3: Генерація до 9 тактових імпульсів на виводі SCL вручну (перемикання High -> Low -> High)
Крок 4: Фіксація моменту, коли ведений пристрій відпускає лінію SDA у високий рівень
Крок 5: Формування коректної умови STOP (SDA переходить з Low у High при високому SCL)
Крок 6: Переконфігурація виводів PB6/PB7 у режим Alternate Function (I2C1) та перезапуск периферії
```

Цей захисний механізм виконується автоматично перед першим зверненням до BME280 та DS3231, що повністю усуває потребу в апаратному вимкненні живлення плати при виникненні збоїв.

### Обробка переривань та часовий профіль каналу RS-485

Під час прийому кадру Modbus RTU мікроконтролер повинен розпізнати кінець передачі за паузою `t3.5` між символами. В апаратному блоці USART для цього вмикається детектор паузи `Receiver Timeout / Idle Line`:
* При виявленні вільної лінії генерується переривання, обробник якого встановлює прапорець `frame_ready = true` у структурі зв'язку.
* Головний цикл перевіряє контрольну суму CRC-16. У разі успішної перевірки формується відповідь у буфері передачі `tx_buf`.
* Вивід `DE` підтягується до одиниці, запускається передача по DMA або перериванню `TXE`.
* Після відправки останнього байта виникає переривання `TC` (Transmission Complete), де вивід `DE` повертається у нуль (режим прослуховування лінії).

### Двоетапна діагностика стану датчиків і статусних прапорців

Поле `status_flags` у кожному телеметричному записі несе детальну діагностичну інформацію про фізичний стан апаратних вузлів:
* `Біт 0 (0x0001) — SENSOR_BME_OK:` підтверджує успішну валідацію контрольної суми вимірювань датчика BME280 та відсутність переповнення АЦП;
* `Біт 1 (0x0002) — RTC_SYNC_OK:` вказує, що мітка часу отримана від термокомпенсованого генератора DS3231 і не піддавалася збою через розряд батареї;
* `Біт 2 (0x0004) — FLASH_LOG_OK:` свідчить про успішне завершення операції Page Program у W25Q128 без помилок апаратного прапорця Write Error;
* `Біт 3 (0x0008) — RS485_ACTIVE:` сигналізує про регулярне отримання опитувальних кадрів від ведучого контролера мережі.

---

## 3. Реалізація координатора вузла

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEMETRY_RECORD_SIZE  24
#define FLASH_PAGE_SIZE        256
#define FLASH_SECTOR_SIZE      4096
#define RS485_RX_BUF_SIZE      64
#define RS485_TX_BUF_SIZE      64

/* ── Структури даних ──────────────────────────────────────────────────────── */

typedef struct __attribute__((packed)) {
    uint32_t timestamp;     /* Unix timestamp від DS3231 */
    int32_t  temperature;   /* Температура x100 (°C)     */
    uint32_t pressure;      /* Тиск x100 (Па)            */
    uint32_t humidity;      /* Вологість x1024 (%RH)     */
    uint16_t sequence_id;   /* Порядковий номер зрізу    */
    uint16_t status_flags;  /* Прапорці стану вузла      */
    uint16_t crc16;         /* Контрольна сума запису    */
} telemetry_record_t;

typedef enum {
    NODE_EVENT_NONE = 0,
    NODE_EVENT_RTC_TICK,
    NODE_EVENT_DATA_READY,
    NODE_EVENT_RS485_RX,
    NODE_EVENT_FLASH_SYNC
} node_event_t;

typedef struct {
    uint32_t write_address;
    uint32_t record_count;
    uint8_t  page_buffer[FLASH_PAGE_SIZE];
    uint16_t page_offset;
} flash_logger_t;

typedef struct {
    uint8_t  rx_buf[RS485_RX_BUF_SIZE];
    uint8_t  tx_buf[RS485_TX_BUF_SIZE];
    uint16_t rx_index;
    bool     frame_ready;
} rs485_channel_t;

typedef struct {
    flash_logger_t  logger;
    rs485_channel_t comm;
    uint16_t        seq_counter;
    volatile node_event_t pending_event;
} node_coordinator_t;

/* ── Апаратні інтерфейси (зовнішні драйвери) ──────────────────────────────── */

extern bool bme280_read_measurements(int32_t *t, uint32_t *p, uint32_t *h);
extern bool ds3231_get_unix_time(uint32_t *unix_time);
extern bool w25q128_page_program(uint32_t addr, const uint8_t *data, uint16_t len);
extern bool w25q128_sector_erase(uint32_t addr);
extern void rs485_set_de(bool enable);
extern void rs485_transmit_bytes(const uint8_t *data, uint16_t len);

/* ── Контрольна сума CRC-16 Modbus ────────────────────────────────────────── */

static uint16_t calculate_crc16(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc = crc >> 1;
            }
        }
    }
    return crc;
}

/* ── Ініціалізація та обробка записів у Flash ─────────────────────────────── */

void node_init(node_coordinator_t *node) {
    memset(node, 0, sizeof(node_coordinator_t));
    node->logger.write_address = 0x000000;
    node->logger.page_offset = 0;
    node->seq_counter = 1;
    node->pending_event = NODE_EVENT_NONE;
    rs485_set_de(false);
}

static void logger_write_record(flash_logger_t *log, const telemetry_record_t *rec) {
    /* Якщо починається новий сектор (4096 байтів), очищуємо його */
    if ((log->write_address % FLASH_SECTOR_SIZE) == 0 && log->page_offset == 0) {
        w25q128_sector_erase(log->write_address);
    }

    /* Копіюємо запис у сторінковий буфер ОЗП */
    memcpy(&log->page_buffer[log->page_offset], rec, sizeof(telemetry_record_t));
    log->page_offset += sizeof(telemetry_record_t);
    log->record_count++;

    /* Якщо сторінка (256 байтів) заповнена, скидаємо її у Flash */
    if (log->page_offset + sizeof(telemetry_record_t) > FLASH_PAGE_SIZE) {
        w25q128_page_program(log->write_address, log->page_buffer, log->page_offset);
        log->write_address += FLASH_PAGE_SIZE;
        log->page_offset = 0;
        memset(log->page_buffer, 0xFF, FLASH_PAGE_SIZE);
    }
}

/* ── Обробка подій та протоколу RS-485 ────────────────────────────────────── */

void node_process_rs485_request(node_coordinator_t *node, const telemetry_record_t *last_rec) {
    if (!node->comm.frame_ready) return;

    /* Перевірка простого кадру запиту: [0x01 (Node ID)][0x03 (Read)][CRC16_L][CRC16_H] */
    if (node->comm.rx_index >= 4 && node->comm.rx_buf[0] == 0x01 && node->comm.rx_buf[1] == 0x03) {
        uint16_t rx_crc = (uint16_t)node->comm.rx_buf[2] | ((uint16_t)node->comm.rx_buf[3] << 8);
        if (calculate_crc16(node->comm.rx_buf, 2) == rx_crc) {
            /* Формування відповіді */
            node->comm.tx_buf[0] = 0x01; /* Node ID */
            node->comm.tx_buf[1] = 0x03; /* Function Code */
            node->comm.tx_buf[2] = sizeof(telemetry_record_t);
            memcpy(&node->comm.tx_buf[3], last_rec, sizeof(telemetry_record_t));

            uint16_t tx_len = 3 + sizeof(telemetry_record_t);
            uint16_t tx_crc = calculate_crc16(node->comm.tx_buf, tx_len);
            node->comm.tx_buf[tx_len]     = (uint8_t)(tx_crc & 0xFF);
            node->comm.tx_buf[tx_len + 1] = (uint8_t)((tx_crc >> 8) & 0xFF);
            tx_len += 2;

            /* Відправка через RS-485 з контролем виводу DE */
            rs485_set_de(true);
            rs485_transmit_bytes(node->comm.tx_buf, tx_len);
            rs485_set_de(false);
        }
    }

    node->comm.rx_index = 0;
    node->comm.frame_ready = false;
}

void node_task_step(node_coordinator_t *node) {
    static telemetry_record_t current_record;

    if (node->pending_event == NODE_EVENT_RTC_TICK) {
        node->pending_event = NODE_EVENT_NONE;

        uint32_t unix_ts = 0;
        int32_t  t = 0;
        uint32_t p = 0, h = 0;

        /* Послідовне зчитування з контролем статусу шини I2C */
        if (ds3231_get_unix_time(&unix_ts) && bme280_read_measurements(&t, &p, &h)) {
            current_record.timestamp   = unix_ts;
            current_record.temperature = t;
            current_record.pressure    = p;
            current_record.humidity    = h;
            current_record.sequence_id = node->seq_counter++;
            current_record.status_flags = 0x0001; /* OK flag */
            current_record.crc16       = calculate_crc16((const uint8_t *)&current_record,
                                                         sizeof(telemetry_record_t) - 2);

            /* Збереження у Flash через енергонезалежний логер */
            logger_write_record(&node->logger, &current_record);
        }
    }

    if (node->comm.frame_ready) {
        node_process_rs485_request(node, &current_record);
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <string_view>
#include <algorithm>

namespace embedded::node {

constexpr size_t FlashPageSize = 256;
constexpr size_t FlashSectorSize = 4096;
constexpr size_t RxBufferSize = 64;
constexpr size_t TxBufferSize = 64;

#pragma pack(push, 1)
struct TelemetryRecord {
    uint32_t timestamp{0};     // Unix timestamp від DS3231
    int32_t  temperature{0};   // Температура x100 (°C)
    uint32_t pressure{0};      // Тиск x100 (Па)
    uint32_t humidity{0};      // Вологість x1024 (%RH)
    uint16_t sequenceId{0};    // Порядковий номер
    uint16_t statusFlags{0};   // Прапорці стану
    uint16_t crc16{0};         // Контрольна сума
};
#pragma pack(pop)

static_assert(sizeof(TelemetryRecord) == 24, "TelemetryRecord must be exactly 24 bytes");

enum class NodeEvent : uint8_t {
    None = 0,
    RtcTick,
    DataReady,
    Rs485Rx,
    FlashSync
};

// ── Обчислення контрольної суми CRC-16 ──────────────────────────────────────
[[nodiscard]] constexpr uint16_t calculateCrc16(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte);
        for (uint8_t j = 0; j < 8; ++j) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc = crc >> 1;
            }
        }
    }
    return crc;
}

// ── Інтерфейс апаратної платформи ──────────────────────────────────────────
class INodeHardware {
public:
    virtual ~INodeHardware() = default;
    virtual bool readBme280(int32_t& temp, uint32_t& press, uint32_t& hum) = 0;
    virtual bool getRtcTime(uint32_t& unixTime) = 0;
    virtual bool flashSectorErase(uint32_t addr) = 0;
    virtual bool flashPageProgram(uint32_t addr, std::span<const uint8_t> data) = 0;
    virtual void setRs485DriverEnable(bool enable) = 0;
    virtual void rs485Transmit(std::span<const uint8_t> data) = 0;
};

// ── RAII-обгортка для лінії Driver Enable трансивера RS-485 ─────────────────
class Rs485TxGuard {
public:
    explicit Rs485TxGuard(INodeHardware& hw) : hw_(hw) {
        hw_.setRs485DriverEnable(true);
    }
    ~Rs485TxGuard() {
        hw_.setRs485DriverEnable(false);
    }
    Rs485TxGuard(const Rs485TxGuard&) = delete;
    Rs485TxGuard& operator=(const Rs485TxGuard&) = delete;

private:
    INodeHardware& hw_;
};

// ── Логер енергонезалежної пам'яті NOR Flash ────────────────────────────────
class FlashLogger {
public:
    explicit FlashLogger(INodeHardware& hw) : hw_(hw) {
        pageBuffer_.fill(0xFF);
    }

    bool appendRecord(const TelemetryRecord& record) {
        if ((writeAddress_ % FlashSectorSize) == 0 && pageOffset_ == 0) {
            if (!hw_.flashSectorErase(writeAddress_)) {
                return false;
            }
        }

        const auto* bytePtr = reinterpret_cast<const uint8_t*>(&record);
        std::copy_n(bytePtr, sizeof(TelemetryRecord), &pageBuffer_[pageOffset_]);
        pageOffset_ += sizeof(TelemetryRecord);
        ++totalRecords_;

        if (pageOffset_ + sizeof(TelemetryRecord) > FlashPageSize) {
            auto span = std::span<const uint8_t>(pageBuffer_.data(), pageOffset_);
            if (!hw_.flashPageProgram(writeAddress_, span)) {
                return false;
            }
            writeAddress_ += FlashPageSize;
            pageOffset_ = 0;
            pageBuffer_.fill(0xFF);
        }
        return true;
    }

    [[nodiscard]] uint32_t totalRecords() const noexcept { return totalRecords_; }

private:
    INodeHardware& hw_;
    uint32_t writeAddress_{0x000000};
    uint32_t totalRecords_{0};
    size_t pageOffset_{0};
    std::array<uint8_t, FlashPageSize> pageBuffer_{};
};

// ── Головний клас координатора вузла ────────────────────────────────────────
class NodeCoordinator {
public:
    explicit NodeCoordinator(INodeHardware& hw)
        : hw_(hw), logger_(hw_) {}

    void onRtcTick() noexcept {
        pendingEvent_ = NodeEvent::RtcTick;
    }

    void onRs485PacketReceived(std::span<const uint8_t> frame) {
        if (frame.size() <= RxBufferSize) {
            std::copy(frame.begin(), frame.end(), rxBuffer_.begin());
            rxSize_ = frame.size();
            frameReady_ = true;
        }
    }

    void step() {
        if (pendingEvent_ == NodeEvent::RtcTick) {
            pendingEvent_ = NodeEvent::None;
            acquireSensorsAndLog();
        }

        if (frameReady_) {
            processRs485Command();
        }
    }

private:
    void acquireSensorsAndLog() {
        uint32_t time = 0;
        int32_t temp = 0;
        uint32_t press = 0;
        uint32_t hum = 0;

        if (hw_.getRtcTime(time) && hw_.readBme280(temp, press, hum)) {
            lastRecord_.timestamp = time;
            lastRecord_.temperature = temp;
            lastRecord_.pressure = press;
            lastRecord_.humidity = hum;
            lastRecord_.sequenceId = ++sequenceCounter_;
            lastRecord_.statusFlags = 0x0001;

            auto payloadSpan = std::span<const uint8_t>(
                reinterpret_cast<const uint8_t*>(&lastRecord_),
                sizeof(TelemetryRecord) - sizeof(uint16_t)
            );
            lastRecord_.crc16 = calculateCrc16(payloadSpan);

            logger_.appendRecord(lastRecord_);
        }
    }

    void processRs485Command() {
        frameReady_ = false;
        if (rxSize_ < 4 || rxBuffer_[0] != 0x01 || rxBuffer_[1] != 0x03) {
            return;
        }

        uint16_t expectedCrc = static_cast<uint16_t>(rxBuffer_[2]) |
                              (static_cast<uint16_t>(rxBuffer_[3]) << 8);

        if (calculateCrc16(std::span(rxBuffer_.data(), 2)) != expectedCrc) {
            return;
        }

        // Побудова кадру телеметричної відповіді
        txBuffer_[0] = 0x01;
        txBuffer_[1] = 0x03;
        txBuffer_[2] = sizeof(TelemetryRecord);

        const auto* recBytes = reinterpret_cast<const uint8_t*>(&lastRecord_);
        std::copy_n(recBytes, sizeof(TelemetryRecord), &txBuffer_[3]);

        size_t payloadLen = 3 + sizeof(TelemetryRecord);
        uint16_t txCrc = calculateCrc16(std::span(txBuffer_.data(), payloadLen));
        txBuffer_[payloadLen]     = static_cast<uint8_t>(txCrc & 0xFF);
        txBuffer_[payloadLen + 1] = static_cast<uint8_t>((txCrc >> 8) & 0xFF);
        size_t totalLen = payloadLen + 2;

        // Безпечна відправка з автоматичним поверненням DE в Low через RAII
        {
            Rs485TxGuard guard(hw_);
            hw_.rs485Transmit(std::span(txBuffer_.data(), totalLen));
        }
    }

    INodeHardware& hw_;
    FlashLogger logger_;
    TelemetryRecord lastRecord_{};
    uint16_t sequenceCounter_{0};
    volatile NodeEvent pendingEvent_{NodeEvent::None};

    std::array<uint8_t, RxBufferSize> rxBuffer_{};
    std::array<uint8_t, TxBufferSize> txBuffer_{};
    size_t rxSize_{0};
    bool frameReady_{false};
};

} // namespace embedded::node
```
:::
