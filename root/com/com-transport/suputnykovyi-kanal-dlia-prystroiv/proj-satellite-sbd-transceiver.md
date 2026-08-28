# ⚙️ Драйвер супутникового трансивера Iridium SBD на C та C++

Реалізація надійного драйвера для автономного супутникового трансивера Iridium 9603 вимагає врахування переривчастого зв'язку (Intermittent Connectivity), тривалих затримок відповіді модема під час виходу в ефір (до 20–60 секунд) та асинхронного парсингу двійкових кадрових структур із контрольною сумою.

## 1. Задача та інженерна архітектура драйвера

Супутниковий трансивер — це пристрій із високою вартістю помилки: кожна невдала спроба виходу в ефір через закритий горизонт марно витрачає обмежений запас енергії літієвої батареї, а некоректно запакований зайвий байт збільшує вартість супутникового білінгу.

Драйвер вирішує п'ять критичних задач:
1. **Керування живленням та захист від падіння напруги (Brownout Protection):** Драйвер вмикає живлення трансивера через пін `ON_OFF`, вичікує інтервал заряду буферного суперконденсатора через обмежувач струму (2000 мс) та лише після цього ініціалізує лінію зв'язку UART.
2. **Пакування телеметрії та контроль цілісності:** Стиснення телеметричних параметрів (координати, заряд, температура) у компактний двійковий буфер та обрахунок 16-бітної арифметичної контрольної суми кадру `AT+SBDWB`.
3. **Асинхронний контроль готовності радіоканалу:** Опитування якості сигналу `AT+CSQ` перед виходом в ефір для запобігання запуску енерговитратної сесії `AT+SBDIX` при нульовому рівні сигналу.
4. **Обробка ефірної сесії та тайм-аутів:** Виконання сесії `AT+SBDIX` із підтримкою тривалого тайм-ауту (до 60 секунд), обробка статусних кодів шлюзу Iridium та автоматичне викачування вхідної черги MT (якщо `MT queued > 0`).
5. **Політика адаптивного бекофу (Adaptive Exponential Backoff):** У разі відсутності супутника над горизонтом драйвер переводить систему в глибокий сон із поступово зростаючим інтервалом паузи та випадковим часовим джитером.

## 2. Апаратне сполучення та часові діаграми живлення

Перед початком передачі даних мікроконтролер повинен дотримуватися суворої послідовності керування живильними та сигнальними лініями:

```
VCC_BAT (3.6V) ───[ Обмежувач струму 150 мА ]───► VBOOST (Суперконденсатор 0.22Ф)
                                                          │
ON_OFF Pin     ───[ LOW = Вимкнено / HIGH = 3.3V ]───────► 9603N Power Rail
                                                          │
                   ├──── 2000 мс (зарядка C_super) ───────┤
                                                          ▼
UART TX/RX     ──────────────────────────────────────────► AT-команди синхронізації
```

Під час фази випромінювання імпульсний струм досягає 2 А, тому напруга на шині `VBOOST` контролюється через вбудований АЦП мікроконтролера. Якщо перед стартом `AT+SBDIX` напруга на суперконденсаторі нижча за 3.2 В, драйвер відкладає вихід в ефір ще на 500 мс для дозаряджання.

## 3. Реалізація драйвера на C та C++

Нижче наведено повну реалізацію драйвера на мові C (підходить для вбудованих систем на FreeRTOS, Zephyr або bare-metal) та ідіоматичну об'єктно-орієнтовану реалізацію на C++20 із застосуванням `std::span`, `std::expected` та типів безпечного парсингу чисел.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define IRIDIUM_MAX_MO_LEN       340
#define IRIDIUM_MAX_MT_LEN       270
#define IRIDIUM_UART_TIMEOUT_MS  60000

typedef enum {
    IRIDIUM_OK = 0,
    IRIDIUM_ERR_TIMEOUT,
    IRIDIUM_ERR_CHECKSUM,
    IRIDIUM_ERR_NO_NETWORK,
    IRIDIUM_ERR_BUFFER_OVERFLOW,
    IRIDIUM_ERR_PROTOCOL
} iridium_err_t;

typedef struct {
    uint16_t mo_status;
    uint16_t momsn;
    uint16_t mt_status;
    uint16_t mtmsn;
    uint16_t mt_len;
    uint16_t mt_queued;
} sbdix_response_t;

/* Інтерфейс апаратного рівня (HAL) */
typedef struct {
    void (*set_power_pin)(bool state);
    void (*delay_ms)(uint32_t ms);
    int (*uart_write)(const uint8_t *data, size_t len);
    int (*uart_read_line)(char *buf, size_t max_len, uint32_t timeout_ms);
    int (*uart_read_bytes)(uint8_t *buf, size_t len, uint32_t timeout_ms);
} iridium_hal_t;

typedef struct {
    const iridium_hal_t *hal;
    bool is_powered;
} iridium_driver_t;

/* 16-бітна сума байтів за специфікацією Iridium SBD */
static uint16_t compute_checksum(const uint8_t *data, size_t len) {
    uint16_t sum = 0;
    for (size_t i = 0; i < len; ++i) {
        sum = (uint16_t)(sum + data[i]);
    }
    return sum;
}

iridium_err_t iridium_init(iridium_driver_t *dev, const iridium_hal_t *hal) {
    if (!dev || !hal) return IRIDIUM_ERR_PROTOCOL;
    dev->hal = hal;
    dev->is_powered = false;
    return IRIDIUM_OK;
}

iridium_err_t iridium_power_on(iridium_driver_t *dev) {
    dev->hal->set_power_pin(true);
    /* Пауза для заряду суперконденсаторів та завантаження DSP модуля */
    dev->hal->delay_ms(2000);
    dev->is_powered = true;

    /* Синхронізація швидкості UART */
    char resp[32];
    dev->hal->uart_write((const uint8_t *)"AT\r", 3);
    if (dev->hal->uart_read_line(resp, sizeof(resp), 2000) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    return IRIDIUM_OK;
}

void iridium_power_off(iridium_driver_t *dev) {
    dev->hal->set_power_pin(false);
    dev->is_powered = false;
}

iridium_err_t iridium_get_signal_quality(iridium_driver_t *dev, uint8_t *csq_out) {
    char resp[32];
    dev->hal->uart_write((const uint8_t *)"AT+CSQ\r", 7);
    if (dev->hal->uart_read_line(resp, sizeof(resp), 3000) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }

    int csq = 0;
    if (sscanf(resp, "+CSQ:%d", &csq) == 1) {
        *csq_out = (uint8_t)csq;
        return IRIDIUM_OK;
    }
    return IRIDIUM_ERR_PROTOCOL;
}

iridium_err_t iridium_load_binary_payload(iridium_driver_t *dev, const uint8_t *payload, size_t len) {
    if (len == 0 || len > IRIDIUM_MAX_MO_LEN) {
        return IRIDIUM_ERR_BUFFER_OVERFLOW;
    }

    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+SBDWB=%zu\r", len);
    dev->hal->uart_write((const uint8_t *)cmd, strlen(cmd));

    char resp[16];
    if (dev->hal->uart_read_line(resp, sizeof(resp), 2000) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    if (strstr(resp, "READY") == NULL) {
        return IRIDIUM_ERR_PROTOCOL;
    }

    /* Відправка навантаження */
    dev->hal->uart_write(payload, len);

    /* Відправка 16-бітної чексуми Big-Endian */
    uint16_t checksum = compute_checksum(payload, len);
    uint8_t cs_bytes[2];
    cs_bytes[0] = (uint8_t)((checksum >> 8) & 0xFF);
    cs_bytes[1] = (uint8_t)(checksum & 0xFF);
    dev->hal->uart_write(cs_bytes, 2);

    /* Модем відповідає двійковим статусом '0' (OK) */
    if (dev->hal->uart_read_line(resp, sizeof(resp), 5000) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    if (resp[0] != '0') {
        return IRIDIUM_ERR_CHECKSUM;
    }
    return IRIDIUM_OK;
}

iridium_err_t iridium_send_sbd_session(iridium_driver_t *dev, sbdix_response_t *result) {
    dev->hal->uart_write((const uint8_t *)"AT+SBDIX\r", 9);

    char resp[96];
    /* Сесія з супутником може тривати до 60 секунд */
    if (dev->hal->uart_read_line(resp, sizeof(resp), IRIDIUM_UART_TIMEOUT_MS) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }

    int mo_st, momsn, mt_st, mtmsn, mt_len, mt_q;
    if (sscanf(resp, "+SBDIX: %d, %d, %d, %d, %d, %d",
               &mo_st, &momsn, &mt_st, &mtmsn, &mt_len, &mt_q) == 6) {
        result->mo_status = (uint16_t)mo_st;
        result->momsn = (uint16_t)momsn;
        result->mt_status = (uint16_t)mt_st;
        result->mtmsn = (uint16_t)mtmsn;
        result->mt_len = (uint16_t)mt_len;
        result->mt_queued = (uint16_t)mt_q;

        if (result->mo_status <= 4) {
            return IRIDIUM_OK;
        } else if (result->mo_status == 32) {
            return IRIDIUM_ERR_NO_NETWORK;
        }
        return IRIDIUM_ERR_PROTOCOL;
    }
    return IRIDIUM_ERR_PROTOCOL;
}

iridium_err_t iridium_read_binary_payload(iridium_driver_t *dev, uint8_t *buf, size_t *out_len, size_t max_len) {
    dev->hal->uart_write((const uint8_t *)"AT+SBDRB\r", 9);

    /* Зчитування 2 байтів довжини */
    uint8_t len_bytes[2];
    if (dev->hal->uart_read_bytes(len_bytes, 2, 3000) != 2) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    uint16_t payload_len = (uint16_t)((len_bytes[0] << 8) | len_bytes[1]);
    if (payload_len > max_len || payload_len > IRIDIUM_MAX_MT_LEN) {
        return IRIDIUM_ERR_BUFFER_OVERFLOW;
    }

    /* Зчитування самого навантаження */
    if (dev->hal->uart_read_bytes(buf, payload_len, 5000) != (int)payload_len) {
        return IRIDIUM_ERR_TIMEOUT;
    }

    /* Зчитування 2 байтів чексуми */
    uint8_t cs_bytes[2];
    if (dev->hal->uart_read_bytes(cs_bytes, 2, 2000) != 2) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    uint16_t received_cs = (uint16_t)((cs_bytes[0] << 8) | cs_bytes[1]);
    uint16_t computed_cs = compute_checksum(buf, payload_len);

    if (received_cs != computed_cs) {
        return IRIDIUM_ERR_CHECKSUM;
    }

    *out_len = payload_len;
    return IRIDIUM_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <expected>
#include <array>
#include <numeric>
#include <chrono>
#include <format>
#include <charconv>

enum class IridiumError {
    Timeout,
    ChecksumMismatch,
    NoNetworkSignal,
    BufferOverflow,
    ProtocolError
};

struct SbdixResponse {
    uint16_t moStatus{0};
    uint16_t momsn{0};
    uint16_t mtStatus{0};
    uint16_t mtmsn{0};
    uint16_t mtLength{0};
    uint16_t mtQueued{0};

    [[nodiscard]] constexpr bool isSuccess() const noexcept {
        return moStatus <= 4;
    }
};

class IridiumHal {
public:
    virtual ~IridiumHal() = default;
    virtual void setPower(bool enable) = 0;
    virtual void sleep(std::chrono::milliseconds ms) = 0;
    virtual bool write(std::span<const uint8_t> data) = 0;
    virtual std::size_t readLine(std::span<char> buffer, std::chrono::milliseconds timeout) = 0;
    virtual std::size_t readBytes(std::span<uint8_t> buffer, std::chrono::milliseconds timeout) = 0;
};

class IridiumTransceiver {
public:
    static constexpr std::size_t MaxMoLength = 340;
    static constexpr std::size_t MaxMtLength = 270;

    explicit IridiumTransceiver(IridiumHal& hal) noexcept : hal_(hal) {}

    std::expected<void, IridiumError> powerOn() {
        hal_.setPower(true);
        hal_.sleep(std::chrono::milliseconds{2000});

        const std::string_view syncCmd = "AT\r";
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(syncCmd.data()), syncCmd.size()});

        std::array<char, 32> lineBuf{};
        if (hal_.readLine(lineBuf, std::chrono::milliseconds{2000}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }
        return {};
    }

    void powerOff() noexcept {
        hal_.setPower(false);
    }

    std::expected<uint8_t, IridiumError> getSignalQuality() {
        const std::string_view cmd = "AT+CSQ\r";
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(cmd.data()), cmd.size()});

        std::array<char, 32> lineBuf{};
        if (hal_.readLine(lineBuf, std::chrono::milliseconds{3000}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }

        std::string_view resp(lineBuf.data());
        auto pos = resp.find("+CSQ:");
        if (pos != std::string_view::npos && pos + 5 < resp.size()) {
            uint8_t csq = 0;
            auto [ptr, ec] = std::from_chars(resp.data() + pos + 5, resp.data() + resp.size(), csq);
            if (ec == std::errc{}) {
                return csq;
            }
        }
        return std::unexpected(IridiumError::ProtocolError);
    }

    std::expected<void, IridiumError> loadBinary(std::span<const uint8_t> payload) {
        if (payload.empty() || payload.size() > MaxMoLength) {
            return std::unexpected(IridiumError::BufferOverflow);
        }

        const auto cmd = std::format("AT+SBDWB={}\r", payload.size());
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(cmd.data()), cmd.size()});

        std::array<char, 16> readyBuf{};
        if (hal_.readLine(readyBuf, std::chrono::milliseconds{2000}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }
        if (std::string_view(readyBuf.data()).find("READY") == std::string_view::npos) {
            return std::unexpected(IridiumError::ProtocolError);
        }

        /* Обчислення 16-бітної контрольної суми */
        uint16_t checksum = std::accumulate(payload.begin(), payload.end(), uint16_t{0});

        hal_.write(payload);
        const std::array<uint8_t, 2> csBytes{
            static_cast<uint8_t>((checksum >> 8) & 0xFF),
            static_cast<uint8_t>(checksum & 0xFF)
        };
        hal_.write(csBytes);

        std::array<char, 16> ackBuf{};
        if (hal_.readLine(ackBuf, std::chrono::milliseconds{5000}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }
        if (ackBuf[0] != '0') {
            return std::unexpected(IridiumError::ChecksumMismatch);
        }
        return {};
    }

    std::expected<SbdixResponse, IridiumError> executeSession() {
        const std::string_view cmd = "AT+SBDIX\r";
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(cmd.data()), cmd.size()});

        std::array<char, 128> respBuf{};
        if (hal_.readLine(respBuf, std::chrono::seconds{60}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }

        SbdixResponse res{};
        std::string_view resp(respBuf.data());
        auto pos = resp.find("+SBDIX:");
        if (pos == std::string_view::npos) {
            return std::unexpected(IridiumError::ProtocolError);
        }

        /* Розбір 6 числових параметрів через кому */
        const char* ptr = resp.data() + pos + 7;
        const char* end = resp.data() + resp.size();
        uint16_t* fields[] = {&res.moStatus, &res.momsn, &res.mtStatus, &res.mtmsn, &res.mtLength, &res.mtQueued};

        for (int i = 0; i < 6; ++i) {
            while (ptr < end && (*ptr == ' ' || *ptr == ',')) ++ptr;
            if (ptr >= end) return std::unexpected(IridiumError::ProtocolError);
            auto [next_ptr, ec] = std::from_chars(ptr, end, *fields[i]);
            if (ec != std::errc{}) return std::unexpected(IridiumError::ProtocolError);
            ptr = next_ptr;
        }

        if (res.isSuccess()) {
            return res;
        } else if (res.moStatus == 32) {
            return std::unexpected(IridiumError::NoNetworkSignal);
        }
        return std::unexpected(IridiumError::ProtocolError);
    }

    std::expected<std::size_t, IridiumError> readBinary(std::span<uint8_t> outputBuffer) {
        const std::string_view cmd = "AT+SBDRB\r";
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(cmd.data()), cmd.size()});

        std::array<uint8_t, 2> lenBytes{};
        if (hal_.readBytes(lenBytes, std::chrono::milliseconds{3000}) != 2) {
            return std::unexpected(IridiumError::Timeout);
        }

        const uint16_t payloadLen = static_cast<uint16_t>((lenBytes[0] << 8) | lenBytes[1]);
        if (payloadLen > outputBuffer.size() || payloadLen > MaxMtLength) {
            return std::unexpected(IridiumError::BufferOverflow);
        }

        if (hal_.readBytes(outputBuffer.subspan(0, payloadLen), std::chrono::milliseconds{5000}) != payloadLen) {
            return std::unexpected(IridiumError::Timeout);
        }

        std::array<uint8_t, 2> csBytes{};
        if (hal_.readBytes(csBytes, std::chrono::milliseconds{2000}) != 2) {
            return std::unexpected(IridiumError::Timeout);
        }

        const uint16_t receivedChecksum = static_cast<uint16_t>((csBytes[0] << 8) | csBytes[1]);
        const uint16_t computedChecksum = std::accumulate(outputBuffer.begin(), outputBuffer.begin() + payloadLen, uint16_t{0});

        if (receivedChecksum != computedChecksum) {
            return std::unexpected(IridiumError::ChecksumMismatch);
        }

        return payloadLen;
    }

private:
    IridiumHal& hal_;
};
```
:::

## 4. Оптимізація двійкового корисного навантаження (Bit-Packing)

Оскільки тарифні плани Iridium SBD розраховуються за одиниці повідомлень фіксованого розміру (наприклад, базовий блок 50 байтів), передача телеметрії у текстовому форматі JSON чи NMEA є вкрай неекономічною. 

Застосування побітового пакування дозволяє зменшити розмір кадру GPS-телеметрії з `~120 байтів` (у форматі ASCII) до всього `11 байтів`:

```
+----------------+----------------+----------------+--------+---------+
| Широта (24 біт)| Довгота (24 біт)| Висота (16 біт)| Напруга| Сенсор  |
| 0.00002° крок  | 0.00002° крок  | метри (0..8000)| (8 біт)| (16 біт)|
+----------------+----------------+----------------+--------+---------+
```

:::tabs
```c
/* Приклад структури упакованого бінарного кадру (11 байтів) */
typedef struct __attribute__((packed)) {
    int32_t lat_scaled : 24;   /* (lat + 90.0) * 50000 (точність ~2 метри) */
    int32_t lon_scaled : 24;   /* (lon + 180.0) * 50000 */
    uint16_t altitude_m;       /* висота над рівнем моря в метрах */
    uint8_t  battery_mv_div20; /* напруга батареї: (V_mv - 2000) / 20 */
    int16_t  temperature_c_x10;/* температура сенсора в сотих градуса */
} compact_telemetry_t;
```
```cpp
#pragma pack(push, 1)
struct CompactTelemetry {
    int32_t latScaled : 24;    // (lat + 90.0) * 50000 (точність ~2 метри)
    int32_t lonScaled : 24;    // (lon + 180.0) * 50000
    uint16_t altitudeM;        // висота над рівнем моря в метрах
    uint8_t  batteryMvDiv20;   // напруга батареї: (V_mv - 2000) / 20
    int16_t  temperatureCx10;  // температура сенсора в сотих градуса
};
#pragma pack(pop)
```
:::

Така оптимізація дозволяє вмістити до трьох послідовних зрізів телеметрії в один мінімальний платіжний блок SBD, скорочуючи експлуатаційні витрати автономного комплексу в кілька разів.

## 5. Інтеграція в операційні системи реального часу (FreeRTOS / Zephyr)

Супутниковий трансивер блокує комунікаційний порт на тривалий час (команда `AT+SBDIX` виконується до 20–60 секунд). У багатозадачному середовищі RTOS це створює загрозу пропуску подій швидких інтерфейсів або зависання сторожового таймера (Watchdog).

Архітектурний патерн інтеграції:
1. **Окремий низькопріоритетний потік:** Драйвер модема ізолюється в окремому RTOS-завданні (Task), яке більшу частину часу перебуває у заблокованому стані на очікуванні черги повідомлень (`xQueueReceive`).
2. **Асинхронний збір подій UART:** Прийом байтів здійснюється через апаратне переривання або DMA-контролер із кільцевим буфером (Ring Buffer), що виключає втрату байтів навіть за високого завантаження процесора.
3. **Опитування сторожового таймера:** Під час тривалого очікування відповіді `AT+SBDIX` драйвер регулярно скидає Watchdog у проміжних циклах опитування статусу модема.

## 6. Інженерні пастки та захисне програмування

1. **Блокування планувальника довгими тайм-аутами:** Виклик `AT+SBDIX` не повинен блокувати інші критичні потоки мікроконтролера (наприклад, опитування сенсорів безпеки). Сесія з супутником вимагає передачі в окремому RTOS-завданні або з використанням неблокуючого автомата станів (FSM).
2. **Просадка напруги в момент виклику `AT+SBDIX`:** У момент запуску радіосесії підсилювач потужності споживає імпульси струму до 2 А. Якщо живлення просяде нижче 3.0 В, модем апаратно скинеться, розірвавши з'єднання UART. Спроба програмно відправити повторну команду без очікування перезапуску призведе до збою протоколу.
3. **Обробка вхідної черги:** Якщо поле `<MT queued>` у відповіді `+SBDIX` більше нуля, шлюз має додаткові дані для пристрою. Драйвер зобов'язаний виконати новий цикл `AT+SBDIX` (із порожнім вихідним буфером `AT+SBDD0`), доки черга не спорожніє.
4. **Сміття в буфері UART при старті передавача:** Потужне радіовипромінювання антени поблизу несиметричних сигнальних ліній UART на платах без суцільного екранування може викликати паразитні наводки та поодинокі помилкові байти (Frame Error). Драйвер повинен очищати приймальний FIFO-буфер UART перед кожною новою AT-командою.
