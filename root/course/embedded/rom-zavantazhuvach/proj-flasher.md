# ⚙️ Реалізація хост-прошивальника для UART

Під час серійного виробництва або польового оновлення мікроконтролера часто виникає потреба прошити чистий чип без використання важких графічних утиліт на зразок STM32CubeProgrammer чи сторонніх пропрієтарних бібліотек. Для цього на стороні керуючого комп'ютера або хост-процесора (наприклад, одноплатника Raspberry Pi на базі Linux чи іншого мікроконтролера-майстра) реалізують компактний клієнт протоколу ROM-завантажувача.

Нижче наведено повноцінний інженерний розбір та робочу реалізацію хост-прошивальника двома мовами: класичною C для вбудованих систем із мінімальними ресурсами та сучасною C++ із застосуванням ідіом RAII, типізованих помилок `std::expected` та безпечних зрізів пам'яті `std::span`.

---

## Архітектура та послідовність прошивки

Процес програмування чипа через послідовний порт USART вимагає суворого дотримання часових інтервалів та складається з шести послідовних етапів:

1. **Апаратний вхід у завантажувач:** Встановлення рівня `BOOT0 = 1`, притискання лінії скидання `NRST` до землі на 50–100 мс і наступне її відпускання. Завдяки цьому ядро стартує з системної пам'яті System Memory ROM.
2. **Синхронізація (Autobauding):** Очищення вхідних буферів порту та передача єдиного байта `0x7F` на швидкості 115200 бод у форматі 8E1 (8 бітів даних, Even Parity, 1 стоп-біт). Завантажувач вимірює тривалість стартового імпульсу і повертає квитанцію `0x79 (ACK)`.
3. **Ідентифікація кристала:** Виклик команди `0x02 (Get ID)` для вичитування 16-бітного ідентифікатора продукту (Product ID, PID) та звірки його із заголовком бінарного файлу прошивки.
4. **Перевірка та зняття захисту (RDP):** Виклик команди `0x01 (Get Version & Read Protection Status)`. Якщо мікроконтролер перебуває у стані захисту RDP Level 1, операції читання та запису блокуватимуться помилкою `NACK`. У такому разі прошивальник надсилає команду `0x92 (Readout Unprotect)`, яка ініціює апаратне масове стирання та повертає чип до відкритого стану RDP Level 0.
5. **Масове або секторне стирання Flash:** Надсилання розширеної команди стирання `0x44 (Extended Erase)` зі спеціальним 16-бітним кодом `0xFFFF` (Mass Erase) та контрольною сумою `0x00`. Хост зобов'язаний виставити збільшений таймаут очікування `ACK` (до 25–30 секунд), оскільки високовольтне стирання всієї кремнієвої матриці Flash триває відчутний час.
6. **Посторінковий запис даних:** Вхідний двійковий образ ділиться на послідовні блоки розміром не більше 256 байтів (`N <= 255`). Для кожного блоку передається команда `0x31 (Write Memory)`, 4-байтова адреса з контрольною сумою XOR, кількість байтів `N`, тіло даних та кінцева контрольна сума XOR.
7. **Верифікація та запуск:** Опціональне вичитування записаних областей пам'яті командою `0x11 (Read Memory)` для побайтового порівняння з оригінальним образом, після чого викликається команда `0x21 (Go)` на базову адресу `0x08000000` для передачі керування прошивці.

---

## Налаштування низькорівневого термінала POSIX (termios)

Робота з послідовним портом у середовищі POSIX вимагає переводу термінала в повністю «сирий» (raw) не канонічний режим. За замовчуванням драйвер операційної системи намагається інтерпретувати спеціальні символи (наприклад, переведення рядка, символи зупинки Ctrl+C/Ctrl+D), що миттєво спотворює двійковий потік прошивки.

Критичні прапорці конфігурації структури `termios`:
- `CS8 | PARENB | ~PARODD`: Вмикає 8 бітів даних із контролем парності Even. Це необхідно, оскільки апаратний UART мікроконтролера під час процедури Autobauding очікує 9-бітний кадр (8 бітів даних + 1 біт парності).
- `~CSTOPB`: Встановлює рівно 1 стоп-біт.
- `CLOCAL | CREAD`: Дозволяє прийом даних та ігнорує лінії керування модемом.
- `~IXON & ~IXOFF & ~IXANY`: Повністю вимикає програмне керування потоком за допомогою символів XON/XOFF (`0x11` та `0x13`). Якщо цей прапорець не зняти, байт прошивки з кодом `0x13` призупинить передачу порту на рівні ядра ОС.
- `c_cc[VMIN] = 0` та `c_cc[VTIME] = 10`: Встановлює неблокуючий посимвольний таймаут тривалістю 1.0 секунда. Якщо завантажувач не відповідає, системний виклик `read()` завершується без вічного зависання процесу.

---

## Апаратне автоскидання через DTR/RTS

Щоб оператору не доводилося переставляти джампери чи вручну натискати кнопки на платі, на перехідниках USB-UART (наприклад, CP2102, FT232R або CH340) застосовують схему автоскидання на двох біполярних NPN-транзисторах:

```
DTR (ПК) ───[ 10k ]───► База Q1 ──── Колектор Q1 ───► NRST (Мікроконтролер)
RTS (ПК) ───[ 10k ]───► База Q2 ──── Колектор Q2 ───► BOOT0 (Мікроконтролер)
Емітер Q1 з'єднано з лінією RTS; Емітер Q2 з'єднано з лінією DTR.
```

- Коли керуюча програма виставляє `DTR = 0` та `RTS = 1`, відкривається транзистор Q2, підтягуючи пін `BOOT0` до високого рівня живлення `VCC`.
- Одночасне перемикання `DTR = 1` та `RTS = 0` відкриває транзистор Q1, притискаючи пін `NRST` до землі (GND) та генеруючи імпульс апаратного скидання.
- Повернення обох ліній у стан `DTR = 0, RTS = 0` відпускає скидання при збереженому заряді на фільтруючому конденсаторі піна `BOOT0`, завдяки чому кристал надійно стартує в режимі System Memory Bootloader.

---

## Простеження обміну байтами на шині (Трасування)

Під час запису блока розміром 256 байтів на адресу `0x08000000` на лініях TX та RX відбувається такий фізичний діалог:

```
1. Хост (TX) -> [ 0x31 ] [ 0xCE ]              (Команда запису та інверсія)
   Чип  (RX) <- [ 0x79 ]                       (ACK від чипа)

2. Хост (TX) -> [ 0x08 ] [ 0x00 ] [ 0x00 ] [ 0x00 ] [ 0x08 ]
   (Адреса 0x08000000 та XOR контрольна сума: 0x08 ^ 0x00 ^ 0x00 ^ 0x00 = 0x08)
   Чип  (RX) <- [ 0x79 ]                       (ACK: адреса валідна)

3. Хост (TX) -> [ 0xFF ] [ D0 ] [ D1 ] ... [ D255 ] [ XOR_SUM ]
   (Кількість 256 байтів позначається N = 255 (0xFF);
    XOR_SUM = 0xFF ^ D0 ^ D1 ^ ... ^ D255)
   Чип  (RX) <- [ 0x79 ]                       (ACK: дані успішно зашито у Flash)
```

---

## Робочий код прошивальника

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>

#define ACK_BYTE   0x79
#define NACK_BYTE  0x1F

#define CMD_GET_ID 0x02
#define CMD_ERASE  0x44
#define CMD_WRITE  0x31
#define CMD_GO     0x21

// Налаштування послідовного порту: 115200 бод, 8E1 (парний контроль)
static int serial_open(const char *port_name)
{
    int fd = open(port_name, O_RDWR | O_NOCTTY | O_SYNC);
    if (fd < 0) return -1;

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        close(fd);
        return -1;
    }

    cfsetospeed(&tty, B115200);
    cfsetispeed(&tty, B115200);

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8; // 8 біт даних
    tty.c_cflag |= PARENB;                      // Увімкнути контроль парності
    tty.c_cflag &= ~PARODD;                     // Even parity (парний)
    tty.c_cflag &= ~CSTOPB;                     // 1 стоп-біт
    tty.c_cflag &= ~CRTSCTS;                    // Без апаратного керування лініями
    tty.c_cflag |= (CLOCAL | CREAD);            // Локальне підключення та прийом

    tty.c_iflag &= ~(IXON | IXOFF | IXANY);     // Без програмного XON/XOFF
    tty.c_lflag = 0;                            // Сирий (raw) не канонічний режим
    tty.c_oflag = 0;

    tty.c_cc[VMIN]  = 0;
    tty.c_cc[VTIME] = 10;                       // Посимвольний таймаут 1.0 с

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        close(fd);
        return -1;
    }
    return fd;
}

// Очікування квитанції ACK (0x79)
static bool wait_ack(int fd, int timeout_seconds)
{
    uint8_t rx_byte = 0;
    int max_attempts = timeout_seconds * 10;
    for (int i = 0; i < max_attempts; ++i) {
        if (read(fd, &rx_byte, 1) == 1) {
            if (rx_byte == ACK_BYTE) return true;
            if (rx_byte == NACK_BYTE) return false;
        }
        usleep(100000); // Інтервал опитування 100 мс
    }
    return false;
}

// Крок 1: Синхронізація бітрейту через надсилання 0x7F
bool bootloader_sync(int fd)
{
    uint8_t sync_byte = 0x7F;
    tcflush(fd, TCIOFLUSH); // Очищення залишків у буфері після скидання
    if (write(fd, &sync_byte, 1) != 1) return false;
    return wait_ack(fd, 2);
}

// Крок 2: Отримання Product ID (PID)
bool bootloader_get_pid(int fd, uint16_t *out_pid)
{
    uint8_t cmd[2] = {CMD_GET_ID, (uint8_t)(~CMD_GET_ID)};
    if (write(fd, cmd, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    uint8_t len = 0;
    if (read(fd, &len, 1) != 1 || len != 1) return false; // Очікуємо 2 байти PID (N = 1)

    uint8_t pid_bytes[2];
    if (read(fd, pid_bytes, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    *out_pid = ((uint16_t)pid_bytes[0] << 8) | pid_bytes[1];
    return true;
}

// Крок 3: Глобальне стирання всієї Flash-пам'яті (Mass Erase)
bool bootloader_mass_erase(int fd)
{
    uint8_t cmd[2] = {CMD_ERASE, (uint8_t)(~CMD_ERASE)};
    if (write(fd, cmd, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    // Спеціальний код 0xFFFF та його XOR чексума 0x00
    uint8_t erase_params[3] = {0xFF, 0xFF, 0x00};
    if (write(fd, erase_params, 3) != 3) return false;

    // Масове стирання може тривати до 20-25 секунд на великих кристалах
    return wait_ack(fd, 25);
}

// Крок 4: Запис одного блоку пам'яті (до 256 байтів)
bool bootloader_write_block(int fd, uint32_t address, const uint8_t *data, size_t length)
{
    if (length == 0 || length > 256) return false;

    // 1. Надсилання команди Write
    uint8_t cmd[2] = {CMD_WRITE, (uint8_t)(~CMD_WRITE)};
    if (write(fd, cmd, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    // 2. Надсилання 4-байтової адреси та її XOR чексуми
    uint8_t addr_buf[5];
    addr_buf[0] = (address >> 24) & 0xFF;
    addr_buf[1] = (address >> 16) & 0xFF;
    addr_buf[2] = (address >> 8) & 0xFF;
    addr_buf[3] = address & 0xFF;
    addr_buf[4] = addr_buf[0] ^ addr_buf[1] ^ addr_buf[2] ^ addr_buf[3];

    if (write(fd, addr_buf, 5) != 5) return false;
    if (!wait_ack(fd, 1)) return false;

    // 3. Надсилання кількості байтів N (len-1), корисних даних та XOR чексуми
    uint8_t payload[258];
    uint8_t n = (uint8_t)(length - 1);
    payload[0] = n;
    uint8_t checksum = n;

    for (size_t i = 0; i < length; ++i) {
        payload[1 + i] = data[i];
        checksum ^= data[i];
    }
    payload[1 + length] = checksum;

    if (write(fd, payload, length + 2) != (ssize_t)(length + 2)) return false;
    return wait_ack(fd, 2);
}

// Крок 5: Передача керування завантаженій програмі (Go)
bool bootloader_go(int fd, uint32_t address)
{
    uint8_t cmd[2] = {CMD_GO, (uint8_t)(~CMD_GO)};
    if (write(fd, cmd, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    uint8_t addr_buf[5];
    addr_buf[0] = (address >> 24) & 0xFF;
    addr_buf[1] = (address >> 16) & 0xFF;
    addr_buf[2] = (address >> 8) & 0xFF;
    addr_buf[3] = address & 0xFF;
    addr_buf[4] = addr_buf[0] ^ addr_buf[1] ^ addr_buf[2] ^ addr_buf[3];

    if (write(fd, addr_buf, 5) != 5) return false;
    return wait_ack(fd, 1);
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <chrono>
#include <thread>
#include <expected>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>

enum class BootloaderError {
    PortOpenFailed,
    ConfigurationFailed,
    SyncFailed,
    AckTimeout,
    NackReceived,
    WriteFailed,
    InvalidParameter
};

class SerialPort {
public:
    explicit SerialPort(const std::string& port_name) {
        fd_ = open(port_name.c_str(), O_RDWR | O_NOCTTY | O_SYNC);
        if (fd_ < 0) return;

        struct termios tty{};
        if (tcgetattr(fd_, &tty) != 0) {
            closePort();
            return;
        }

        cfsetospeed(&tty, B115200);
        cfsetispeed(&tty, B115200);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8; // 8 бітів даних
        tty.c_cflag |= PARENB;                      // Контроль парності
        tty.c_cflag &= ~PARODD;                     // Even
        tty.c_cflag &= ~CSTOPB;                     // 1 стоп-біт
        tty.c_cflag &= ~CRTSCTS;
        tty.c_cflag |= (CLOCAL | CREAD);

        tty.c_iflag &= ~(IXON | IXOFF | IXANY);
        tty.c_lflag = 0;
        tty.c_oflag = 0;
        tty.c_cc[VMIN]  = 0;
        tty.c_cc[VTIME] = 10;                       // Таймаут 1.0 с

        if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
            closePort();
        }
    }

    ~SerialPort() {
        closePort();
    }

    // Заборона копіювання для суворого контролю дескриптора (RAII)
    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;

    SerialPort(SerialPort&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    [[nodiscard]] bool isOpen() const noexcept { return fd_ >= 0; }

    bool writeBytes(std::span<const uint8_t> data) const {
        if (!isOpen()) return false;
        return write(fd_, data.data(), data.size()) == static_cast<ssize_t>(data.size());
    }

    bool readBytes(std::span<uint8_t> buffer) const {
        if (!isOpen()) return false;
        size_t total = 0;
        while (total < buffer.size()) {
            ssize_t res = read(fd_, buffer.data() + total, buffer.size() - total);
            if (res <= 0) return false;
            total += static_cast<size_t>(res);
        }
        return true;
    }

    void flush() const {
        if (isOpen()) tcflush(fd_, TCIOFLUSH);
    }

private:
    int fd_{-1};

    void closePort() noexcept {
        if (fd_ >= 0) {
            close(fd_);
            fd_ = -1;
        }
    }
};

class Stm32Flasher {
public:
    static constexpr uint8_t ACK_BYTE   = 0x79;
    static constexpr uint8_t NACK_BYTE  = 0x1F;
    static constexpr uint8_t CMD_GET_ID = 0x02;
    static constexpr uint8_t CMD_ERASE  = 0x44;
    static constexpr uint8_t CMD_WRITE  = 0x31;
    static constexpr uint8_t CMD_GO     = 0x21;

    explicit Stm32Flasher(SerialPort& port) : port_(port) {}

    std::expected<void, BootloaderError> sync() {
        port_.flush();
        const uint8_t sync_byte = 0x7F;
        if (!port_.writeBytes(std::span{&sync_byte, 1})) {
            return std::unexpected(BootloaderError::WriteFailed);
        }
        return waitAck(std::chrono::seconds(2));
    }

    std::expected<uint16_t, BootloaderError> getChipId() {
        const uint8_t cmd[2] = {CMD_GET_ID, static_cast<uint8_t>(~CMD_GET_ID)};
        if (!port_.writeBytes(cmd)) return std::unexpected(BootloaderError::WriteFailed);
        
        auto ack_res = waitAck(std::chrono::seconds(1));
        if (!ack_res) return std::unexpected(ack_res.error());

        uint8_t len = 0;
        if (!port_.readBytes(std::span{&len, 1}) || len != 1) {
            return std::unexpected(BootloaderError::InvalidParameter);
        }

        uint8_t pid_buf[2]{};
        if (!port_.readBytes(pid_buf)) return std::unexpected(BootloaderError::SyncFailed);
        
        auto ack_end = waitAck(std::chrono::seconds(1));
        if (!ack_end) return std::unexpected(ack_end.error());

        return (static_cast<uint16_t>(pid_buf[0]) << 8) | pid_buf[1];
    }

    std::expected<void, BootloaderError> massErase() {
        const uint8_t cmd[2] = {CMD_ERASE, static_cast<uint8_t>(~CMD_ERASE)};
        if (!port_.writeBytes(cmd)) return std::unexpected(BootloaderError::WriteFailed);
        
        auto ack_res = waitAck(std::chrono::seconds(1));
        if (!ack_res) return ack_res;

        // Код глобального стирання 0xFFFF та XOR сума 0x00
        const uint8_t params[3] = {0xFF, 0xFF, 0x00};
        if (!port_.writeBytes(params)) return std::unexpected(BootloaderError::WriteFailed);

        // Повне стирання матриці Flash вимагає тривалого таймауту
        return waitAck(std::chrono::seconds(30));
    }

    std::expected<void, BootloaderError> writeBlock(uint32_t address, std::span<const uint8_t> data) {
        if (data.empty() || data.size() > 256) {
            return std::unexpected(BootloaderError::InvalidParameter);
        }

        const uint8_t cmd[2] = {CMD_WRITE, static_cast<uint8_t>(~CMD_WRITE)};
        if (!port_.writeBytes(cmd)) return std::unexpected(BootloaderError::WriteFailed);
        
        auto ack_res = waitAck(std::chrono::seconds(1));
        if (!ack_res) return ack_res;

        const uint8_t addr_buf[5] = {
            static_cast<uint8_t>((address >> 24) & 0xFF),
            static_cast<uint8_t>((address >> 16) & 0xFF),
            static_cast<uint8_t>((address >> 8) & 0xFF),
            static_cast<uint8_t>(address & 0xFF),
            static_cast<uint8_t>(((address >> 24) ^ (address >> 16) ^ (address >> 8) ^ address) & 0xFF)
        };

        if (!port_.writeBytes(addr_buf)) return std::unexpected(BootloaderError::WriteFailed);
        auto ack_addr = waitAck(std::chrono::seconds(1));
        if (!ack_addr) return ack_addr;

        std::vector<uint8_t> packet;
        packet.reserve(data.size() + 2);
        
        const auto n = static_cast<uint8_t>(data.size() - 1);
        packet.push_back(n);
        uint8_t checksum = n;

        for (uint8_t byte : data) {
            packet.push_back(byte);
            checksum ^= byte;
        }
        packet.push_back(checksum);

        if (!port_.writeBytes(packet)) return std::unexpected(BootloaderError::WriteFailed);
        return waitAck(std::chrono::seconds(2));
    }

    std::expected<void, BootloaderError> jumpToApp(uint32_t address) {
        const uint8_t cmd[2] = {CMD_GO, static_cast<uint8_t>(~CMD_GO)};
        if (!port_.writeBytes(cmd)) return std::unexpected(BootloaderError::WriteFailed);
        
        auto ack_res = waitAck(std::chrono::seconds(1));
        if (!ack_res) return ack_res;

        const uint8_t addr_buf[5] = {
            static_cast<uint8_t>((address >> 24) & 0xFF),
            static_cast<uint8_t>((address >> 16) & 0xFF),
            static_cast<uint8_t>((address >> 8) & 0xFF),
            static_cast<uint8_t>(address & 0xFF),
            static_cast<uint8_t>(((address >> 24) ^ (address >> 16) ^ (address >> 8) ^ address) & 0xFF)
        };

        if (!port_.writeBytes(addr_buf)) return std::unexpected(BootloaderError::WriteFailed);
        return waitAck(std::chrono::seconds(1));
    }

private:
    SerialPort& port_;

    std::expected<void, BootloaderError> waitAck(std::chrono::milliseconds timeout) {
        const auto start = std::chrono::steady_clock::now();
        while (std::chrono::steady_clock::now() - start < timeout) {
            uint8_t byte = 0;
            if (port_.readBytes(std::span{&byte, 1})) {
                if (byte == ACK_BYTE) return {};
                if (byte == NACK_BYTE) return std::unexpected(BootloaderError::NackReceived);
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        return std::unexpected(BootloaderError::AckTimeout);
    }
};
```
:::

---

## Підводні камені та діагностика збоїв

1. **Дерево затримок USB-драйвера:** Під час використання віртуальних COM-портів USB (CDC/ACM) виклики керування лініями DTR/RTS проходять через буферизацію операційної системи. Якщо надіслати байт синхронізації `0x7F` занадто швидко після підняття лінії `NRST`, завантажувач ще не встигне завершити ініціалізацію внутрішнього тактового генератора HSI. Слід завжди вставляти паузу щонайменше 50–100 мс після скидання.
2. **Вирівнювання розміру останнього пакета:** Якщо розмір бінарного файлу не кратний 256 байтам, фінальний блок передається зі зменшеною довжиною `N = rem - 1`. На чипах з апаратною підтримкою ECC у Flash (STM32G0, STM32G4, STM32L4) адреса та довжина запису мають бути строго вирівняні за межею подвійного слова (8 байтів), тому хвіст останнього блока слід доповнювати байтами `0xFF`.
3. **Паразитичні перешкоди на лініях зв'язку:** Під час апаратного скидання ніжки мікроконтролера тимчасово переходять у високоімпедансний стан (Hi-Z). Без зовнішніх резисторів підтяжки до живлення лінія RX може зафіксувати помилковий спад напруги як стартовий біт, спотворивши автопідлаштування бітрейту. Очищення буфера порту функцією `tcflush()` перед початком синхронізації усуває цю проблему.
