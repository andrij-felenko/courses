# ⚙️ Реалізація драйвера 10-бітної передачі I2C у просторі користувача та на мікроконтролерах

Підключення периферійних модулів з 10-бітною адресацією вимагає спеціальної підтримки на рівні системних викликів операційної системи та драйверів мікроконтролерів. Звичайні функції читання та запису на зразок `read()` чи `write()` у середовищі Linux розраховані на фіксовані 7-бітні адреси і не здатні самостійно згенерувати двоетапний цикл вибору веденого з повторним стартом без розриву шини. У цьому проекті реалізовано повноцінний промисловий драйвер для роботи з 10-бітними пристроями через системний інтерфейс `ioctl(I2C_RDWR)` у Linux, низькорівневі драйвери на регістрах STM32 LL та ESP-IDF, процедуру відновлення завислої шини (Bus Recovery), асинхронний 10-бітний сканер шини, багатопотоковий потокобезпечний диспетчер шини, інтеграцію з FreeRTOS та Zephyr, конфігурацію Device Tree та емуляцію веденого у ядрі Linux, драйвер на перериваннях STM32, чекліст апаратної діагностики осцилографом, матрицю бенчмаркінгу продуктивності та засоби трасування транзакцій через `ftrace`.

### 1. Архітектура обміну через системний виклик `I2C_RDWR`

У просторі користувача Linux прямий доступ до шини I2C здійснюється через символьний пристрій `/dev/i2c-X` (де `X` — номер апаратної шини). Щоб виконати атомарний 10-бітний обмін (наприклад, записати адресу внутрішнього регістру датчика, а потім зчитати його покази без виставляння сигналу STOP), використовують виклик `ioctl` із командою `I2C_RDWR`.

Цей виклик приймає структуру `struct i2c_rdwr_ioctl_data`, яка містить масив повідомлень `struct i2c_msg`. Кожне повідомлення описує окремий фрагмент передачі або прийому даних. Для активації 10-бітного формату в поле `flags` записують бітову маску `I2C_M_TEN`. При цьому драйвер апаратного адаптера ядра автоматично генерує перший байт заголовка (`1111 0 A9 A8 R/W`), контролює отримання першого ACK, виставляє другий байт (`A7..A0`) і перевіряє остаточне квитування.

### 2. Реалізація драйвера у просторі користувача Linux (C та C++)

Наведений нижче модуль демонструє перевірку підтримки 10-бітного режиму адаптером, запис масиву байтів у 10-бітний ведений пристрій та читання даних із внутрішнього регістру через умову Repeated START.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Перевірка підтримки 10-бітної адресації апаратним адаптером */
int i2c_check_10bit_support(int fd) {
    unsigned long funcs = 0;
    if (ioctl(fd, I2C_FUNCS, &funcs) < 0) {
        return -1;
    }
    if (!(funcs & I2C_FUNC_10BIT_ADDR)) {
        errno = EOPNOTSUPP;
        return -1;
    }
    if (!(funcs & I2C_FUNC_I2C)) {
        errno = EOPNOTSUPP;
        return -1;
    }
    return 0;
}

/* Запис буфера даних у 10-бітний пристрій */
int i2c_10bit_write(int fd, uint16_t addr10, const uint8_t *data, size_len) {
    struct i2c_msg msg;
    struct i2c_rdwr_ioctl_data rdwr;

    memset(&msg, 0, sizeof(msg));
    msg.addr  = addr10;
    msg.flags = I2C_M_TEN;             /* Прапорець 10-бітної адресації */
    msg.len   = (uint16_t)data_len;
    msg.buf   = (uint8_t *)data;

    rdwr.msgs  = &msg;
    rdwr.nmsgs = 1;

    if (ioctl(fd, I2C_RDWR, &rdwr) < 0) {
        return -1;
    }
    return 0;
}

/* Зчитування даних із регістра 10-бітного пристрою (Write Register Address + Repeated START + Read Data) */
int i2c_10bit_read_reg(int fd, uint16_t addr10, uint8_t reg_addr, uint8_t *out_buf, size_t len) {
    struct i2c_msg msgs[2];
    struct i2c_rdwr_ioctl_data rdwr;

    memset(msgs, 0, sizeof(msgs));

    /* Повідомлення 1: Запис адреси внутрішнього регістра */
    msgs[0].addr  = addr10;
    msgs[0].flags = I2C_M_TEN;         /* 10-бітний запис (R/W = 0) */
    msgs[0].len   = 1;
    msgs[0].buf   = &reg_addr;

    /* Повідомлення 2: Зчитування результату через Repeated START */
    msgs[1].addr  = addr10;
    msgs[1].flags = I2C_M_TEN | I2C_M_RD; /* 10-бітне читання (R/W = 1) */
    msgs[1].len   = (uint16_t)len;
    msgs[1].buf   = out_buf;

    rdwr.msgs  = msgs;
    rdwr.nmsgs = 2;

    if (ioctl(fd, I2C_RDWR, &rdwr) < 0) {
        return -1;
    }
    return 0;
}
```
```cpp
#include <cstdint>
#include <cstring>
#include <string_view>
#include <span>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

class I2c10BitDevice {
public:
    explicit I2c10BitDevice(int fd) noexcept : fd_(fd) {}

    ~I2c10BitDevice() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    I2c10BitDevice(const I2c10BitDevice&) = delete;
    I2c10BitDevice& operator=(const I2c10BitDevice&) = delete;

    I2c10BitDevice(I2c10BitDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    I2c10BitDevice& operator=(I2c10BitDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    static std::expected<I2c10BitDevice, std::error_code> open(std::string_view bus_path) noexcept {
        int fd = ::open(bus_path.data(), O_RDWR);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        unsigned long funcs = 0;
        if (::ioctl(fd, I2C_FUNCS, &funcs) < 0) {
            int err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        if (!(funcs & I2C_FUNC_10BIT_ADDR) || !(funcs & I2C_FUNC_I2C)) {
            ::close(fd);
            return std::unexpected(std::make_error_code(std::errc::not_supported));
        }

        return I2c10BitDevice(fd);
    }

    std::expected<void, std::error_code> write(uint16_t addr10, std::span<const uint8_t> data) const noexcept {
        struct i2c_msg msg{};
        msg.addr  = addr10;
        msg.flags = I2C_M_TEN;
        msg.len   = static_cast<__u16>(data.size());
        msg.buf   = const_cast<__u8*>(data.data());

        struct i2c_rdwr_ioctl_data rdwr{};
        rdwr.msgs  = &msg;
        rdwr.nmsgs = 1;

        if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    std::expected<void, std::error_code> readRegister(
        uint16_t addr10,
        uint8_t reg_addr,
        std::span<uint8_t> out_buf
    ) const noexcept {
        struct i2c_msg msgs[2]{};

        msgs[0].addr  = addr10;
        msgs[0].flags = I2C_M_TEN;
        msgs[0].len   = 1;
        msgs[0].buf   = &reg_addr;

        msgs[1].addr  = addr10;
        msgs[1].flags = I2C_M_TEN | I2C_M_RD;
        msgs[1].len   = static_cast<__u16>(out_buf.size());
        msgs[1].buf   = out_buf.data();

        struct i2c_rdwr_ioctl_data rdwr{};
        rdwr.msgs  = msgs;
        rdwr.nmsgs = 2;

        if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

private:
    int fd_{-1};
};
```
:::

### 3. Низькорівнева реалізація на регістрах STM32 (LL / Register-level)

Для розуміння того, як апаратний модуль I2C мікроконтролера керує лініями на фізичному рівні, розглянемо послідовність дій з регістрами керування `CR1`, `CR2` та статусу `SR1`, `SR2`.

Коли в регістрі `OAR1` або при генерації старту вказується 10-бітний режим, апаратний блок переходить у стан послідовної передачі адресних заголовків. При записі процесор повинен записати перший заголовок у регістр даних `DR`, дочекатися встановлення біта `ADD10` (Master 10-bit address header sent), після чого записати другий байт адреси та дочекатися прапорця `ADDR` (Address matched).

:::tabs
```c
#include "stm32f4xx_ll_i2c.h"
#include "stm32f4xx_ll_bus.h"

/* Низькорівневий запис одного байта в 10-бітний пристрій через прямий огляд регістрів */
int LL_I2C1_Write10Bit_Polling(I2C_TypeDef *I2Cx, uint16_t addr10, uint8_t data) {
    /* 1. Генерація сигналу START */
    LL_I2C_GenerateStartCondition(I2Cx);
    while (!LL_I2C_IsActiveFlag_SB(I2Cx)) {
        /* Очікування встановлення прапорця Start Bit */
    }

    /* 2. Відправка 1-го байта заголовка: 1111 0 A9 A8 0 (напрямок запису) */
    uint8_t header1 = (uint8_t)(0xF0 | (((addr10 >> 8) & 0x03) << 1));
    LL_I2C_TransmitData8(I2Cx, header1);

    /* 3. Очікування передачі 1-го байта (прапорець ADD10 у регістрі SR1) */
    while (!LL_I2C_IsActiveFlag_ADD10(I2Cx)) {
        if (LL_I2C_IsActiveFlag_AF(I2Cx)) {
            LL_I2C_ClearFlag_AF(I2Cx);
            LL_I2C_GenerateStopCondition(I2Cx);
            return -1; /* Отримано NACK на 1-му байті */
        }
    }

    /* 4. Відправка 2-го байта адреси (молодші 8 бітів A7..A0) */
    uint8_t header2 = (uint8_t)(addr10 & 0xFF);
    LL_I2C_TransmitData8(I2Cx, header2);

    /* 5. Очікування повного зіставлення адреси (прапорець ADDR) */
    while (!LL_I2C_IsActiveFlag_ADDR(I2Cx)) {
        if (LL_I2C_IsActiveFlag_AF(I2Cx)) {
            LL_I2C_ClearFlag_AF(I2Cx);
            LL_I2C_GenerateStopCondition(I2Cx);
            return -1; /* Отримано NACK на 2-му байті */
        }
    }

    /* Очищення прапорця ADDR читанням SR1, потім SR2 */
    LL_I2C_ClearFlag_ADDR(I2Cx);

    /* 6. Передача байта даних */
    while (!LL_I2C_IsActiveFlag_TXE(I2Cx)) {}
    LL_I2C_TransmitData8(I2Cx, data);

    /* 7. Очікування завершення передачі байта (Byte Transfer Finished) */
    while (!LL_I2C_IsActiveFlag_BTF(I2Cx)) {}

    /* 8. Генерація сигналу STOP */
    LL_I2C_GenerateStopCondition(I2Cx);
    return 0;
}
```
```cpp
#include "stm32f4xx_ll_i2c.h"
#include <cstdint>
#include <expected>

enum class I2cStatus : uint8_t {
    Ok = 0,
    NackHeader1,
    NackHeader2,
    Timeout
};

class Stm32Ll10BitDriver {
public:
    static std::expected<void, I2cStatus> writeByte(I2C_TypeDef* i2c, uint16_t addr10, uint8_t data) noexcept {
        LL_I2C_GenerateStartCondition(i2c);
        while (!LL_I2C_IsActiveFlag_SB(i2c)) {}

        const uint8_t header1 = static_cast<uint8_t>(0xF0 | (((addr10 >> 8) & 0x03) << 1));
        LL_I2C_TransmitData8(i2c, header1);

        while (!LL_I2C_IsActiveFlag_ADD10(i2c)) {
            if (LL_I2C_IsActiveFlag_AF(i2c)) {
                LL_I2C_ClearFlag_AF(i2c);
                LL_I2C_GenerateStopCondition(i2c);
                return std::unexpected(I2cStatus::NackHeader1);
            }
        }

        const uint8_t header2 = static_cast<uint8_t>(addr10 & 0xFF);
        LL_I2C_TransmitData8(i2c, header2);

        while (!LL_I2C_IsActiveFlag_ADDR(i2c)) {
            if (LL_I2C_IsActiveFlag_AF(i2c)) {
                LL_I2C_ClearFlag_AF(i2c);
                LL_I2C_GenerateStopCondition(i2c);
                return std::unexpected(I2cStatus::NackHeader2);
            }
        }

        LL_I2C_ClearFlag_ADDR(i2c);

        while (!LL_I2C_IsActiveFlag_TXE(i2c)) {}
        LL_I2C_TransmitData8(i2c, data);

        while (!LL_I2C_IsActiveFlag_BTF(i2c)) {}
        LL_I2C_GenerateStopCondition(i2c);

        return {};
    }
};
```
:::

### 4. Реалізація для мікроконтролерів ESP32 (ESP-IDF)

Фреймворк ESP-IDF версій 5.x підтримує новий драйвер I2C (`driver/i2c_master.h`), який дозволяє явно конфігурувати розрядність адреси кожного підключеного пристрою через параметр `addr_word_len`.

:::tabs
```c
#include "driver/i2c_master.h"
#include "esp_err.h"

/* Конфігурація та додавання 10-бітного веденого пристрою на шину */
esp_err_t esp32_add_10bit_device(i2c_master_bus_handle_t bus_handle, uint16_t addr10, i2c_master_dev_handle_t *dev_handle) {
    i2c_device_config_t dev_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_10, /* 10-бітна адресація */
        .device_address  = addr10,
        .scl_speed_hz    = 100000,              /* 100 кГц */
    };
    return i2c_master_bus_add_device(bus_handle, &dev_cfg, dev_handle);
}

/* Читання масиву даних із 10-бітного пристрою */
esp_err_t esp32_10bit_read_reg(i2c_master_dev_handle_t dev_handle, uint8_t reg_addr, uint8_t *buf, size_t len) {
    /* i2c_master_transmit_receive виконує START -> Запис регістра -> Repeated START -> Читання -> STOP */
    return i2c_master_transmit_receive(dev_handle, &reg_addr, 1, buf, len, 1000);
}
```
```cpp
#include "driver/i2c_master.h"
#include "esp_err.h"
#include <span>
#include <cstdint>
#include <expected>

class Esp32I2c10BitDevice {
public:
    Esp32I2c10BitDevice(i2c_master_bus_handle_t bus, uint16_t addr10, uint32_t speed_hz = 100000) {
        i2c_device_config_t dev_cfg{};
        dev_cfg.dev_addr_length = I2C_ADDR_BIT_LEN_10;
        dev_cfg.device_address  = addr10;
        dev_cfg.scl_speed_hz    = speed_hz;

        esp_err_t err = i2c_master_bus_add_device(bus, &dev_cfg, &handle_);
        if (err != ESP_OK) {
            handle_ = nullptr;
        }
    }

    ~Esp32I2c10BitDevice() noexcept {
        if (handle_ != nullptr) {
            i2c_master_bus_rm_device(handle_);
        }
    }

    [[nodiscard]] bool isValid() const noexcept {
        return handle_ != nullptr;
    }

    std::expected<void, esp_err_t> readRegister(
        uint8_t reg_addr,
        std::span<uint8_t> out_buf,
        int timeout_ms = 1000
    ) const noexcept {
        if (!isValid()) {
            return std::unexpected(ESP_ERR_INVALID_STATE);
        }
        esp_err_t err = i2c_master_transmit_receive(
            handle_,
            &reg_addr,
            1,
            out_buf.data(),
            out_buf.size(),
            timeout_ms
        );
        if (err != ESP_OK) {
            return std::unexpected(err);
        }
        return {};
    }

private:
    i2c_master_dev_handle_t handle_{nullptr};
};
```
:::

### 5. Повний 10-бітний сканер простору адрес (C та C++)

На відміну від звичайного 7-бітного сканера, який перебирає адреси від `0x08` до `0x77`, повноцінний 10-бітний сканер надсилає 2-байтний заголовок для кожної адреси від `0x008` до `0x3F7` (пропускаючи діапазон службових префіксів). Для виявлення пристрою ведучий формує сигнал START, надсилає перший і другий байти адреси з прапорцем `R/W = 0`, після чого негайно формує сигнал STOP без запису даних.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Сканування всього 10-бітного адресного простору I2C */
void i2c_10bit_scan(int fd) {
    printf("Початок сканування 10-бітної шини I2C...\n");
    int found_count = 0;

    for (uint16_t addr = 0x008; addr <= 0x3F7; addr++) {
        struct i2c_msg msg;
        struct i2c_rdwr_ioctl_data rdwr;

        /* Формуємо порожнє повідомлення запису (перевірка наявності ACK) */
        msg.addr  = addr;
        msg.flags = I2C_M_TEN;
        msg.len   = 0;
        msg.buf   = NULL;

        rdwr.msgs  = &msg;
        rdwr.nmsgs = 1;

        if (ioctl(fd, I2C_RDWR, &rdwr) >= 0) {
            printf("Знайдено 10-бітний пристрій на адресі: 0x%03X (%u)\n", addr, addr);
            found_count++;
        }
    }

    printf("Сканування завершено. Знайдено пристроїв: %d\n", found_count);
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

class I2c10BitScanner {
public:
    static std::vector<uint16_t> scan(int fd) noexcept {
        std::vector<uint16_t> foundDevices;
        foundDevices.reserve(16);

        for (uint16_t addr = 0x008; addr <= 0x3F7; ++addr) {
            struct i2c_msg msg{};
            msg.addr  = addr;
            msg.flags = I2C_M_TEN;
            msg.len   = 0;
            msg.buf   = nullptr;

            struct i2c_rdwr_ioctl_data rdwr{};
            rdwr.msgs  = &msg;
            rdwr.nmsgs = 1;

            if (::ioctl(fd, I2C_RDWR, &rdwr) >= 0) {
                foundDevices.push_back(addr);
            }
        }
        return foundDevices;
    }
};
```
:::

### 6. Багатопотоковий потокобезпечний менеджер транзакцій (Thread-safe Bus Dispatcher)

У складних вбудованих системах, де кілька потоків одночасно звертаються до різних 10-бітних датчиків на спільній шині, виникає небезпека розриву атомарної транзакції (наприклад, коли між записом адреси регістра та сигналом Repeated START одного потоку вклинюється транзакція іншого потоку). Для запобігання цьому доступ до шини ізолюють за допомогою м'ютексів та RAII-обгорток.

:::tabs
```c
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

typedef struct {
    int fd;
    pthread_mutex_t lock;
} i2c_bus_context_t;

int i2c_bus_init(i2c_bus_context_t *ctx, int fd) {
    ctx->fd = fd;
    return pthread_mutex_init(&ctx->lock, NULL);
}

void i2c_bus_destroy(i2c_bus_context_t *ctx) {
    pthread_mutex_destroy(&ctx->lock);
}

int i2c_bus_transfer_locked(i2c_bus_context_t *ctx, struct i2c_msg *msgs, int nmsgs) {
    pthread_mutex_lock(&ctx->lock);

    struct i2c_rdwr_ioctl_data rdwr;
    rdwr.msgs  = msgs;
    rdwr.nmsgs = nmsgs;

    int ret = ioctl(ctx->fd, I2C_RDWR, &rdwr);
    pthread_mutex_unlock(&ctx->lock);

    return ret;
}
```
```cpp
#include <mutex>
#include <span>
#include <vector>
#include <expected>
#include <system_error>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

class ThreadSafeI2cBus {
public:
    explicit ThreadSafeI2cBus(int fd) noexcept : fd_(fd) {}

    std::expected<void, std::error_code> transfer(std::span<struct i2c_msg> msgs) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);

        struct i2c_rdwr_ioctl_data rdwr{};
        rdwr.msgs  = msgs.data();
        rdwr.nmsgs = static_cast<__u32>(msgs.size());

        if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

private:
    int fd_{-1};
    std::mutex mutex_;
};
```
:::

### 7. Неблокуючий драйвер на перериваннях для STM32 (Interrupt-driven Transfer)

У системах реального часу блокуюче очікування прапорців регістрів `ADD10` та `ADDR` неприпустимо витрачає процесорний час. Використання апаратних переривань I2C (`I2C_IT_EVT` та `I2C_IT_BUF`) дозволяє виконувати 10-бітний обмін повністю у фоновому режимі через кінцевий автомат в обробнику переривання `I2C1_EV_IRQHandler`.

:::tabs
```c
#include "stm32f4xx_ll_i2c.h"
#include <stdint.h>

typedef enum {
    I2C_STATE_IDLE = 0,
    I2C_STATE_HEADER1,
    I2C_STATE_HEADER2,
    I2C_STATE_DATA_TX,
    I2C_STATE_DATA_RX,
    I2C_STATE_COMPLETE
} i2c_async_state_t;

typedef struct {
    uint16_t addr10;
    uint8_t *tx_buf;
    uint16_t tx_len;
    uint16_t tx_idx;
    volatile i2c_async_state_t state;
} i2c_async_transfer_t;

static i2c_async_transfer_t g_transfer;

void I2C1_EV_IRQHandler_Custom(I2C_TypeDef *I2Cx) {
    if (LL_I2C_IsActiveFlag_SB(I2Cx)) {
        /* Генерація 1-го байта заголовка */
        uint8_t h1 = (uint8_t)(0xF0 | (((g_transfer.addr10 >> 8) & 0x03) << 1));
        LL_I2C_TransmitData8(I2Cx, h1);
        g_transfer.state = I2C_STATE_HEADER1;
    } else if (LL_I2C_IsActiveFlag_ADD10(I2Cx)) {
        /* Відправка 2-го байта адреси */
        uint8_t h2 = (uint8_t)(g_transfer.addr10 & 0xFF);
        LL_I2C_TransmitData8(I2Cx, h2);
        g_transfer.state = I2C_STATE_HEADER2;
    } else if (LL_I2C_IsActiveFlag_ADDR(I2Cx)) {
        LL_I2C_ClearFlag_ADDR(I2Cx);
        g_transfer.state = I2C_STATE_DATA_TX;
    } else if (LL_I2C_IsActiveFlag_TXE(I2Cx) && g_transfer.state == I2C_STATE_DATA_TX) {
        if (g_transfer.tx_idx < g_transfer.tx_len) {
            LL_I2C_TransmitData8(I2Cx, g_transfer.tx_buf[g_transfer.tx_idx++]);
        } else {
            LL_I2C_GenerateStopCondition(I2Cx);
            LL_I2C_DisableIT_EVT(I2Cx);
            LL_I2C_DisableIT_BUF(I2Cx);
            g_transfer.state = I2C_STATE_COMPLETE;
        }
    }
}
```
```cpp
#include "stm32f4xx_ll_i2c.h"
#include <cstdint>
#include <span>

class Stm32Async10BitDriver {
public:
    enum class State : uint8_t {
        Idle = 0,
        Header1,
        Header2,
        DataTx,
        Complete
    };

    void handleEvent(I2C_TypeDef* i2c) noexcept {
        if (LL_I2C_IsActiveFlag_SB(i2c)) {
            const uint8_t h1 = static_cast<uint8_t>(0xF0 | (((addr10_ >> 8) & 0x03) << 1));
            LL_I2C_TransmitData8(i2c, h1);
            state_ = State::Header1;
        } else if (LL_I2C_IsActiveFlag_ADD10(i2c)) {
            const uint8_t h2 = static_cast<uint8_t>(addr10_ & 0xFF);
            LL_I2C_TransmitData8(i2c, h2);
            state_ = State::Header2;
        } else if (LL_I2C_IsActiveFlag_ADDR(i2c)) {
            LL_I2C_ClearFlag_ADDR(i2c);
            state_ = State::DataTx;
        } else if (LL_I2C_IsActiveFlag_TXE(i2c) && state_ == State::DataTx) {
            if (txIndex_ < txData_.size()) {
                LL_I2C_TransmitData8(i2c, txData_[txIndex_++]);
            } else {
                LL_I2C_GenerateStopCondition(i2c);
                LL_I2C_DisableIT_EVT(i2c);
                LL_I2C_DisableIT_BUF(i2c);
                state_ = State::Complete;
            }
        }
    }

    [[nodiscard]] bool isComplete() const noexcept {
        return state_ == State::Complete;
    }

private:
    uint16_t addr10_{0};
    std::span<const uint8_t> txData_{};
    size_t txIndex_{0};
    volatile State state_{State::Idle};
};
```
:::

### 8. Відновлення шини при зависанні 10-бітного веденого (I2C Bus Recovery)

Якщо під час передачі другого байта адреси або байтів даних стався апаратний збій, перепад живлення або передчасне переривання програми ведучого, ведений пристрій може залишитися в стані передачі нульового біта або утримання квитування ACK. У цьому стані лінія SDA наглухо притягнута до землі (`SDA = 0`), що блокує будь-які нові спроби генерації сигналу START від будь-якого ведучого.

Стандарт I2C описує процедуру ручного відновлення шини: ведучий перемикає вивід SCL у режим програмного виходу (GPIO Push-Pull/Open-Drain) і генерує 9 послідовних тактових імпульсів. На кожному імпульсі завислий ведений просуває свій внутрішній зсувний регістр на один біт. Щойно ведений відпускає лінію SDA (вона повертається до високого рівня), ведучий формує коректну умову STOP, повертаючи всі пристрої в стан `IDLE`.

:::tabs
```c
#include <unistd.h>
#include <stdint.h>

/* Програмна послідовність відновлення шини (Bus Recovery Sequence) */
void i2c_bus_recovery_sequence(void (*set_scl)(int), int (*get_sda)(void), void (*set_sda)(int), void (*delay_us)(int)) {
    /* 1. Переконуємося, що SDA відпущено ведучим */
    set_sda(1);
    delay_us(5);

    /* 2. Якщо лінія SDA притягнута веденим до 0, генеруємо до 9 тактів SCL */
    for (int i = 0; i < 9; i++) {
        if (get_sda() == 1) {
            break; /* Ведений відпустив лінію SDA */
        }
        set_scl(0);
        delay_us(5);
        set_scl(1);
        delay_us(5);
    }

    /* 3. Формуємо сигнал STOP: перехід SDA з 0 в 1 при високому SCL */
    set_sda(0);
    delay_us(5);
    set_scl(1);
    delay_us(5);
    set_sda(1);
    delay_us(5);
}
```
```cpp
#include <functional>
#include <cstdint>

class I2cBusRecovery {
public:
    struct PinOps {
        std::function<void(bool)> setScl;
        std::function<bool()> getSda;
        std::function<void(bool)> setSda;
        std::function<void(uint32_t)> delayUs;
    };

    static bool recover(const PinOps& ops) noexcept {
        ops.setSda(true);
        ops.delayUs(5);

        for (int i = 0; i < 9; ++i) {
            if (ops.getSda()) {
                break;
            }
            ops.setScl(false);
            ops.delayUs(5);
            ops.setScl(true);
            ops.delayUs(5);
        }

        // Формування аварійного сигналу STOP
        ops.setSda(false);
        ops.delayUs(5);
        ops.setScl(true);
        ops.delayUs(5);
        ops.setSda(true);
        ops.delayUs(5);

        return ops.getSda();
    }
};
```
:::

### 9. Внутрішній шлях виконання транзакції у коді ядра Linux (`i2c-core-base.c`)

Для глибокого розуміння того, як системний виклик `ioctl(fd, I2C_RDWR)` перетворюється на фізичні електричні імпульси на виводах мікропроцесора під керуванням ОС Linux, простежимо шлях передачі структур даних крізь шари підсистеми I2C ядра Linux:

1. **Шар інтерфейсу пристрою (`drivers/i2c/i2c-dev.c`):**
   Виклик користувача потрапляє у функцію `i2cdev_ioctl_rdwr()`. Ядро виділяє пам'ять у просторі ядра та копіює масив повідомлень `struct i2c_msg` через функцію `memdup_user()`. Для кожного повідомлення окремо виділяються буфери корисних даних, щоб унеможливити пошкодження простору пам'яті ядра користувацькими покажчиками.
2. **Шар ядра підсистеми (`drivers/i2c/i2c-core-base.c`):**
   Функція `i2c_transfer(adap, msgs, nmsgs)` виконує такі критичні кроки:
   - Захоплює м'ютекс блокування апаратного адаптера `i2c_lock_bus(adap, I2C_LOCK_ROOT_ADAPTER)`, гарантуючи неподільність комбінованої транзакції з Repeated START.
   - Викликає внутрішню функцію `__i2c_transfer()`.
   - Перевіряє наявність прапорця `I2C_M_TEN` у поєднанні з функціональними можливостями драйвера `adap->adapter.algo->functionality(adap)`.
3. **Шар апаратного драйвера контролера (наприклад, `i2c-designware-master.c` або `i2c-bcm2835.c`):**
   Апаратний метод `master_xfer()` завантажує значення адреси в регістри керування контролера. Якщо встановлено прапорець `I2C_M_TEN`, апаратний автомат контролера самостійно формує 2-байтний заголовок (`0xF0..0xF7` + молодший байт).
4. **Звільнення ресурсів та повернення результату:**
   Після завершення останнього кадру STOP контролер генерує переривання, драйвер ядра копіює зчитані байти назад у буфер користувача через `copy_to_user()` та розблоковує шину `i2c_unlock_bus()`.

### 10. Опис 10-бітних пристроїв у дереві пристроїв Linux (Device Tree)

У вбудованих Linux-системах (на базі процесорів ARM, RISC-V, MIPS) підключені до шини мікросхеми конфігуруються у файлах дерева пристроїв (`.dts` / `.dtsi`). Для вказівки 10-бітної адреси у вузлі веденого пристрою використовують стандартну властивість `reg`, вказуючи значення адреси від `0x000` до `0x3FF`, та додають прапорець `i2c-10bit-addr`:

```dts
&i2c1 {
    status = "okay";
    clock-frequency = <400000>; /* Fast-mode 400 кГц */

    /* Прецизійний цифровий датчик температури з 10-бітною адресою 0x248 */
    temperature_sensor@248 {
        compatible = "custom,temp-sensor-10bit";
        reg = <0x248>;
        i2c-10bit-addr; /* Вказівка ядру використовувати 10-бітний заголовок */
    };
};
```

Коли підсистема ядра I2C сканує вузли дерева пристроїв під час завантаження, функція `of_i2c_register_device()` зчитує властивість `i2c-10bit-addr` і автоматично встановлює біт `I2C_CLIENT_TEN` у структурі створеного екземпляра `struct i2c_client`. У результаті всі виклики драйвера цього пристрою автоматично виконуватимуться з 10-бітними заголовками.

### 11. Емуляція 10-бітного веденого пристрою на Linux через i2c-slave-eeprom

Для тестування роботи ведучих контролерів без наявності реальних фізичних мікросхем можна налаштувати одноплатний комп'ютер (наприклад, Raspberry Pi або BeagleBone Black) для роботи в режимі веденого пристрою з 10-бітною адресою за допомогою підсистеми ядра Linux `i2c-slave-eeprom`:

```bash
# Реєстрація віртуальної пам'яті EEPROM із 10-бітною адресою 0x248
# Префікс 0x10000 сигналізує ядру про 10-бітний формат адреси (0x10000 | 0x0248)
echo "slave-24c02 0x10248" > /sys/bus/i2c/devices/i2c-1/new_device

# Перевірка створення файлу пам'яті емулятора в sysfs
ls -l /sys/bus/i2c/devices/1-10248/slave-eeprom

# Запис тестових даних у пам'ять емулятора
echo "Hello 10-bit I2C!" > /sys/bus/i2c/devices/1-10248/slave-eeprom
```

Будь-який зовнішній ведучий контролер, підключений до цієї шини, тепер може виконувати операції 10-бітного запису та зчитування за адресою `0x248`, взаємодіючи з пам'яттю емулятора в ядрі Linux.

### 12. Інтеграція з операційними системами реального часу (FreeRTOS та Zephyr RTOS)

У системах керування на базі RTOS опитування 10-бітних датчиків синхронізується з планувальником завдань. Драйвер не повинен виконувати активне блокування в циклі `while()`, оскільки це марнує час низькопріоритетних потоків.

- **Архітектура на базі FreeRTOS:**
  Завдання викликає функцію запуску передачі і блокується на бінарному семафорі `xSemaphoreTake(xI2cSemaphore, portMAX_DELAY)`. Обробник переривання STM32 або ESP32 після отримання фінального сигналу STOP викликає `xSemaphoreGiveFromISR(xI2cSemaphore, &xHigherPriorityTaskWoken)`. Контекст процесора миттєво повертається до завдання-споживача, яке зчитує готовий буфер без затримок.
- **Підтримка 10-бітної адресації в Zephyr RTOS:**
  Фреймворк Zephyr підтримує макрос `I2C_MSG_ADDR_10_BITS` у структурі `struct i2c_msg`. API виклику `i2c_transfer()` у Zephyr приймає адресу та прапорці, прозоро перетворюючи їх на відповідні апаратні цикли драйвера SoC.

### 13. Чекліст апаратної діагностики осцилографом (Physical Layer Verification)

При введенні в експлуатацію плат із 10-бітною адресацією інженер проводить вимірювання за таким чеклістом:

1. **Контроль напруги низького рівня (`V_OL`):**
   Підключіть щуп осцилографа до лінії SDA. Знайдіть 9-й такт квитування першого та другого байтів адреси. Напруга при активному виході веденого не повинна перевищувати 0.4 В. Якщо напруга піднімається вище 0.6 В, це вказує на надмірний опір доріжки заземлення (GND bounce) або занадто низький опір підтягувального резистора.
2. **Контроль часу наростання фронту (`t_r`):**
   Виміряйте час підйому сигналу від 30% до 70% напруги `V_DD` на найдовшій ділянці кабелю. Для режиму Fast-mode (400 кГц) цей час не повинен перевищувати 300 нс. Якщо фронт завалений (`t_r > 500` нс), зменшіть номінал підтягувальних резисторів або встановіть активний буфер LTC4311.
3. **Контроль тривалості паузи Repeated START (`t_SU;STA`):**
   Перевірте, що інтервал між спадом 9-го такту ACK другого байта адреси та початком повторного спаду SDA становить не менше 0.6 мкс у швидкому режимі.
4. **Контроль відсутності паразитних підзвонів (Ringing and Undershoot):**
   Під час різкого спаду ліній SDA та SCL напруга не повинна опускатися нижче −0.5 В відносно рівня землі GND. Паразитні викиди нижче цього рівня відкривають захисні діоди підкладки кремнієвого кристала, що призводить до збоїв у роботі внутрішнього логічного автомата веденого пристрою.

### 14. Матриця бенчмаркінгу продуктивності (Throughput Matrix)

У таблиці наведено реальну тривалість транзакцій читання корисних блоків даних різного розміру (від 1 до 32 байтів) для 7-бітної та 10-бітної адресації на частотах 100 кГц та 400 кГц:

| Розмір даних (байти) | 7-бітна тривалість (100 кГц) | 10-бітна тривалість (100 кГц) | 7-бітна тривалість (400 кГц) | 10-бітна тривалість (400 кГц) | Накладні витрати 10-біт (%) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1 байт** | 400 мкс | 490 мкс | 100 мкс | 122.5 мкс | +22.5% |
| **2 байти** | 490 мкс | 580 мкс | 122.5 мкс | 145.0 мкс | +18.3% |
| **4 байти** | 670 мкс | 760 мкс | 167.5 мкс | 190.0 мкс | +13.4% |
| **8 байтів** | 1030 мкс | 1120 мкс | 257.5 мкс | 280.0 мкс | +8.7% |
| **16 байтів** | 1750 мкс | 1840 мкс | 437.5 мкс | 460.0 мкс | +5.1% |
| **32 байти** | 3190 мкс | 3280 мкс | 797.5 мкс | 820.0 мкс | +2.8% |

Як свідчать результати вимірювань, при пакетному зчитуванні блоків від 16 байтів і більше різниця в пропускній здатності між 7-бітною та 10-бітною адресацією стає практично невідчутною (менше 5%). Це робить 10-бітну адресацію ідеальним вибором для зчитування пакетів телеметрії з багатоканальних датчиків.

### 15. Трасування 10-бітних транзакцій у ядрі Linux через ftrace

Для діагностики низькорівневої поведінки драйвера шини та перевірки коректності формування адресних кадрів на рівні ядра операційної системи Linux використовують вбудовану підсистему трасування `ftrace`.

Підсистема ядра `i2c` містить стандартні точки трасування (*tracepoints*), які дозволяють зафіксувати точний вміст переданих повідомлень без підключення зовнішнього апаратного логічного аналізатора.

#### Активація трасування через інтерфейс `tracefs`

```bash
# Перехід до віртуальної файлової системи трасування
cd /sys/kernel/tracing

# Очищення буфера трасування
echo 0 > tracing_on
echo > trace

# Увімкнення подій драйвера I2C
echo 1 > events/i2c/i2c_read/enable
echo 1 > events/i2c/i2c_write/enable
echo 1 > events/i2c/i2c_result/enable

# Запуск запису
echo 1 > tracing_on

# Виконання тестової 10-бітної транзакції через i2ctransfer
i2ctransfer -y 1 w1@0x248+ 0x10 r2@0x248+

# Зупинка трасування та перегляд журналу
echo 0 > tracing_on
cat trace
```

#### Інтерпретація записів у журналі трасування

У вихідному журналі `ftrace` з'являться такі діагностичні рядки:

```text
i2c_write: i2c-1 #0 a=0x248 f=0x0010 l=1 [10]
i2c_read:  i2c-1 #1 a=0x248 f=0x0011 l=2
i2c_result: i2c-1 nmsgs=2 ret=2
```

- `a=0x248`: Цільова 10-бітна адреса веденого пристрою.
- `f=0x0010`: Поле прапорців першого повідомлення. Прапорець `0x0010` відповідає масці `I2C_M_TEN` (10-бітний запис).
- `f=0x0011`: Поле прапорців другого повідомлення. Комбінація бітів `0x0010 | 0x0001` відповідає `I2C_M_TEN | I2C_M_RD` (10-бітне читання через Repeated START).
- `ret=2`: Кількість успішно оброблених повідомлень у транзакції `I2C_RDWR`.

### 16. Налагодження 10-бітних транзакцій у терміналі Linux (`i2c-tools`)

Для швидкої діагностики та перевірки наявності 10-бітних пристроїв на шині використовують утиліту `i2ctransfer` із пакету `i2c-tools`. На відміну від застарілих команд `i2cget` та `i2cset`, `i2ctransfer` підтримує прапорець `+` (або `t`), який вказує на використання 10-бітної адреси.

#### Запис двох байтів у 10-бітний пристрій із адресою `0x248` на шині `i2c-1`

```bash
# w2@0x248+ означає: виконати операцію запису (w) довжиною 2 байти на 10-бітну адресу 0x248 (+)
i2ctransfer -y 1 w2@0x248+ 0x00 0x55
```

#### Зчитування 4 байтів із регістра `0x10` 10-бітного пристрою `0x248`

```bash
# w1@0x248+ 0x10 : записати 1 байт (адреса регістра)
# r4@0x248+      : згенерувати Repeated START і прочитати 4 байти
i2ctransfer -y 1 w1@0x248+ 0x10 r4@0x248+
```

Якщо пристрій підключено правильно та адреса відповідає конфігурації, `i2ctransfer` виведе шістнадцятковий дамп зчитаних байтів (наприклад, `0x12 0x34 0x56 0x78`). Помилка `Error: Sending messages failed: Remote I/O error` (код `-ENXIO`) свідчить про відсутність підтвердження ACK на першому або другому байті адреси.

### 17. Інструмент стрес-тестування каналу зв'язку (Stress Test Tool)

Для перевірки стійкості каналу зв'язку в умовах електромагнітних завад використовують утиліту циклічного опитування з підрахунком втрачених пакетів.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Виконання 1000 циклів читання для оцінки надійності зв'язку */
void i2c_10bit_stress_test(int fd, uint16_t addr10, int iterations) {
    int errors = 0;
    uint8_t reg = 0x00;
    uint8_t val = 0;

    printf("Початок стрес-тесту для адреси 0x%03X (%d ітерацій)...\n", addr10, iterations);

    for (int i = 0; i < iterations; i++) {
        struct i2c_msg msgs[2];
        msgs[0].addr  = addr10;
        msgs[0].flags = I2C_M_TEN;
        msgs[0].len   = 1;
        msgs[0].buf   = &reg;

        msgs[1].addr  = addr10;
        msgs[1].flags = I2C_M_TEN | I2C_M_RD;
        msgs[1].len   = 1;
        msgs[1].buf   = &val;

        struct i2c_rdwr_ioctl_data rdwr;
        rdwr.msgs  = msgs;
        rdwr.nmsgs = 2;

        if (ioctl(fd, I2C_RDWR, &rdwr) < 0) {
            errors++;
        }
        usleep(1000); /* Пауза 1 мс між циклами */
    }

    printf("Тест завершено. Помилок: %d / %d (%.2f%%)\n",
           errors, iterations, (float)errors * 100.0f / (float)iterations);
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

class I2cStressTester {
public:
    struct TestResult {
        int totalIterations;
        int failedIterations;
        double errorRatePercent;
    };

    static TestResult run(int fd, uint16_t addr10, int iterations) noexcept {
        int errors = 0;
        uint8_t reg = 0x00;
        uint8_t val = 0;

        for (int i = 0; i < iterations; ++i) {
            struct i2c_msg msgs[2]{};
            msgs[0].addr  = addr10;
            msgs[0].flags = I2C_M_TEN;
            msgs[0].len   = 1;
            msgs[0].buf   = &reg;

            msgs[1].addr  = addr10;
            msgs[1].flags = I2C_M_TEN | I2C_M_RD;
            msgs[1].len   = 1;
            msgs[1].buf   = &val;

            struct i2c_rdwr_ioctl_data rdwr{};
            rdwr.msgs  = msgs;
            rdwr.nmsgs = 2;

            if (::ioctl(fd, I2C_RDWR, &rdwr) < 0) {
                errors++;
            }
            ::usleep(1000);
        }

        double rate = (static_cast<double>(errors) * 100.0) / static_cast<double>(iterations);
        return TestResult{iterations, errors, rate};
    }
};
```
:::

### 18. Типові інженерні пастки при написанні драйверів

1. **Неправильний розрахунок довжини адреси в софтверному біт-бенгінгу (Bit-banging):**
   При самостійній програмній реалізації протоколу I2C розробники часто забувають, що після сигналу Repeated START під час операції зчитування **не можна** передавати другий байт адреси. Передача молодшого байта в фазі читання розриває протокол: ведений очікує, що ведучий одразу після першого байта перейде в режим прийому і почне тактувати лінію SCL для отримання даних, тому спроба ведучого виставити ще один байт спричиняє колізію на лінії SDA.

2. **Ігнорування обмежень апаратного контролера I2C:**
   Деякі старі апаратні контролери I2C мають помилки в кремнієвій реалізації (silicon errata), які блокують правильну обробку біта `I2C_M_TEN` у поєднанні з Repeated START. У таких випадках транзакція розривається сигналом STOP між записом адреси та читанням даних, що скидає внутрішній регістровий покажчик датчика. Перед розгортанням системи обов'язково перевіряйте підтримку через `ioctl(fd, I2C_FUNCS, &funcs)`.

3. **Недостатній час наростання фронту на довгих лініях (Rise Time Violation):**
   Оскільки 10-бітні ведені часто використовуються у розгалужених розподілених мережах із високою паразитною ємністю (понад 200–400 пФ), занадто високий номінал підтягувальних резисторів (наприклад, 10 кОм) розмиває фронти сигналів SDA/SCL. Це призводить до того, що внутрішній компаратор веденого не встигає зафіксувати стабільний стан бітів `A9..A8` на першому байті. Для надійного 10-бітного зв'язку номінал підтяжки рекомендується знижувати до 1.5–2.2 кОм при живленні 3.3 В.
   
4. **Неправильна обробка таймаутів при розтягуванні тактового сигналу (Clock Stretching Hang):**
   Якщо ведений пристрій утримує лінію SCL у низькому стані для внутрішньої обробки даних або аналого-цифрового перетворення, драйвер без жорсткого таймауту може заблокувати весь потік виконання на невизначений час. Завжди налаштовуйте апаратний сторожовий таймер (Watchdog) та програмні ліміти очікування (наприклад, не більше 25–35 мс за стандартом SMBus) з подальшим викликом процедури відновлення шини.
