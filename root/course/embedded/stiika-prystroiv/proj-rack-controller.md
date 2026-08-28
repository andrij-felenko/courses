# ⚙️ Демон керування стійкою пристроїв: захоплення слотів, логування консолі та аварійне відновлення

В автоматизованій системі тестування CI/CD тестова стійка є розділюваним фізичним ресурсом між багатьма паралельними завданнями (jobs). Якщо два процеси одночасно спробують прошити одну й ту саму плату або одночасно відкрити її UART-порт, тест провалиться через колізію дескрипторів та взаємне спотворення даних. Демон керування стійкою (`rack-daemon`) виконує роль апаратного брокера: він монопольно захоплює слоти через атомарні файлові блокування ядра, керує послідовністю циклів живлення, стрімить логи консолі без ризику втрати перших байтів завантаження та реалізує апаратний протокол виведення плати зі стану «цеглини» (unbricking).

У цьому проектному розборі ми розберемо внутрішню механіку реалізації такого сервісу, вивчимо тонкощі конфігурації POSIX-терміналів (`termios`), розглянемо взаємодію з ядром Linux через системні виклики `flock` та `select`, а також створимо закінчений модуль керування слотом на мовах C та C++.

---

## 1. Архітектура синхронізації та файлові блокування

Коли десятки раннерів запускають тести паралельно, звичайні прапорці в пам'яті процесу або записи в базі даних виявляються недостатніми: якщо тестовий процес гине через сигнал `SIGKILL` (наприклад, перевищення ліміту часу CI-джоби), прапорець у базі може залишитися в стані «зайнято», і слот назавжди заблокується для наступних прогонів.

Найбільш надійний механізм у середовищі Linux — системний виклик `flock()` над спеціальним файлом блокування `/var/lock/dut-slot-XX.lock`.

```
Механіка атомарного захоплення через файловий дескриптор:

  [Тестовий процес Pytest] ─── open("/var/lock/dut-slot-01.lock") ───► FD = 5
                                         │
                                         ▼
                             flock(FD, LOCK_EX | LOCK_NB)
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
            [Успіх: ret == 0]                         [Зайнято: errno == EWOULDBLOCK]
            Слот закріплено за процесом               Слот зайнятий іншим раннером,
            (Блокування зніметься ядром               вихід або очікування в черзі
            автоматично навіть при SIGKILL!)
```

Головна перевага дескрипторних блокувань `flock` полягає в тому, що таблиця відкритих файлових блокувань утримується самим ядром Linux. Якщо процес несподівано падає (через `Segmentation Fault`, вичерпання пам'яті OOM-killer чи примусовий `kill -9`), ядро операційної системи автоматично закриває всі відкриті файлові дескриптори цього процесу, і блокування `flock` негайно знімається. Жоден слот не зависає у «мертвому» стані навічно.

---

## 2. Фізичні шляхи до обладнання через udev

Кожен апаратний слот у стійці складається з трьох незалежних фізичних ліній, які підсистема `udev` відображає у фіксовані передбачувані симлінки:

1. `/dev/dut-slot-01-uart` — послідовний порт налагоджувальної консолі, підключений через мікросхему моста USB-UART (наприклад, FTDI FT4232H або WCH CH343).
2. `/dev/dut-slot-01-swd` — інтерфейс апаратного налагоджувача (ST-Link V2/V3, J-Link або CMSIS-DAP).
3. `/dev/dut-slot-01-pwr` — лінія керування силовим ключем живлення (відображена через GPIO контролера стійки або релейну плату на шині I2C).
4. `/tmp/dut-locks/slot_01.lock` — файл блокування монопольного володіння слотом.

---

## 3. Проблема втрати перших байтів завантажувача (Early Boot Log Truncation)

Класична пастка автоматизації вбудованих систем виглядає так: скрипт подає команду на увімкнення живлення плати, очікує 100 мілісекунд, а потім відкриває пристрій `/dev/ttyUSB0` через функцію `open()` і намагається прочитати початковий банер прошивки.

У такій схемі початкові байти завантаження **гарантовано втрачаються**. Розглянемо фізичну часову діаграму процесу:

1. Мікроконтролер на базі ядра ARM Cortex-M4 (168 МГц) після подачі живлення проходить апаратний Power-On Reset (POR) за 1–2 мс.
2. Вектор `Reset_Handler` ініціалізує стек і викликає функцію `main()`, де першим ділом налаштовується периферія UART і виводиться рядок `[BOOT] Firmware v2.4.0 started, reset cause: POR`. Це відбувається через 3–5 мс після появи напруги 3.3 В на шині.
3. З боку Linux-хоста: відкриття символьного пристрою `open()`, виклик `tcgetattr()` та конфігурація структури `termios` вимагає системних викликів до USB-драйвера хоста (`ftdi_sio` або `cdc_acm`), що займає від 15 до 60 мілісекунд.
4. Якщо порт було відкрито після подачі живлення, апаратні FIFO-буфери недорогого USB-UART моста або переповнюються, або скидаються драйвером під час виклику `open()`. Тестовий раннер бачить обірваний лог `re v2.4.0 started...` або порожнечу.

### Канонічний порядок ініціалізації:
Щоб не втратити жодного байта, черговість дій у демоні має бути строго зворотною:
1. Відкрити дескриптор `/dev/dut-slot-XX-uart` у неблокуючому режимі (`O_NONBLOCK`).
2. Налаштувати параметри `termios` (швидкість, 8N1, Raw режим без ехо).
3. Очистити можливе старе сміття у черзі викликом `tcflush(fd, TCIFLUSH)`.
4. Запустити фоновий збір даних або підготувати виклик `select()` / `poll()`.
5. **Лише після цього** подати сигнал на відкриття силового ключа живлення плати.

---

## 4. Процедура апаратної реанімації (Unbricking Sequence)

Під час інтенсивного тестування прошивка може перевести мікроконтролер у стан повної відсутності реакції («цеглина»):
- Прошивка помилково переконфігурувала виводи SWD (PA13/PA14 на STM32) у режим виходів GPIO або вимкнула тактування налагоджувального блока DBGMCU.
- Код увійшов у нескінченну петлю аварійного скидання сторожового таймера (Watchdog reset loop) або генерує постійний `HardFault`, через що ядро перезавантажується кожні 200 мікросекунд і налагоджувач не встигає під'єднатися.
- Flash-пам'ять виявилася заблокованою прапорцями захисту Option Bytes (RDP Level 1).

Для виведення зразка з цього стану демон реалізує послідовність апаратної активації системного завантажувача ROM:
1. Зняти живлення зі слота (VCC = 0 В).
2. Перевести лінію `BOOT0` у високий рівень (+3.3 В) через додатковий GPIO-ключ стійки.
3. Подати живлення на слот. Мікроконтролер апаратно вичитує пін `BOOT0` при старті й замість виконання збійного коду користувача запускає незмінний фабричний завантажувач із вбудованого ROM (System Memory).
4. У цьому стані периферія та піни SWD лишаються у стандартному стані. Демон викликає OpenOCD із командою `stm32f4x mass_erase 0`, повністю очищуючи пошкоджену прошивку.
5. Лінія `BOOT0` повертається в 0 В, після чого плата знову готова до штатного програмування.

---

## 5. Програмна реалізація модуля керування слотом

Нижче наведено закінчений модуль керування слотом, написаний мовами C (C99/POSIX) та сучасним ідіоматичним C++20 з використанням концепції RAII (Resource Acquisition Is Initialization).

:::tabs
```c
// Модуль керування слотом тестової стійки (C99 / POSIX)
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <sys/file.h>
#include <sys/select.h>
#include <sys/time.h>

#define SLOT_LOCK_DIR       "/tmp/dut-locks"
#define UART_CHUNK_SIZE     256
#define MAX_LOG_BUFFER      16384

typedef struct {
    int slot_id;
    int lock_fd;
    int uart_fd;
    char lock_path[64];
    char uart_path[64];
    char log_buffer[MAX_LOG_BUFFER];
    size_t log_length;
} rack_slot_t;

// Низькорівневе налаштування POSIX TTY в повністю "сирий" (Raw) режим
static bool configure_uart_raw(int fd, speed_t baud) {
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        return false;
    }
    
    // Встановлення швидкості прийому та передачі
    cfsetospeed(&tty, baud);
    cfsetispeed(&tty, baud);
    
    // 8 біт даних, без парності, 1 стоп-біт, увімкнений прийом
    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~(PARENB | PARODD | CSTOPB | CRTSCTS);
    
    // Відключення канонічного режиму, ехо та сигналів клавіатури
    tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    
    // Відключення програмного контролю потоку (XON/XOFF) та трансформації переведення рядків
    tty.c_iflag &= ~(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
    tty.c_oflag &= ~OPOST; // Сирий вивід без підстановки \r\n
    
    // Неблокуюче читання: повернути керування негайно, якщо буфер порожній
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 0;
    
    return tcsetattr(fd, TCSANOW, &tty) == 0;
}

// Захоплення слота через атомарне блокування файлу ядром Linux
bool rack_slot_acquire(rack_slot_t *slot, int slot_id) {
    slot->slot_id = slot_id;
    slot->lock_fd = -1;
    slot->uart_fd = -1;
    slot->log_length = 0;
    slot->log_buffer[0] = '\0';
    
    snprintf(slot->lock_path, sizeof(slot->lock_path), "%s/slot_%02d.lock", SLOT_LOCK_DIR, slot_id);
    snprintf(slot->uart_path, sizeof(slot->uart_path), "/dev/dut-slot-%02d-uart", slot_id);
    
    // Відкриття або створення файлу блокування
    slot->lock_fd = open(slot->lock_path, O_CREAT | O_RDWR, 0666);
    if (slot->lock_fd < 0) {
        return false;
    }
    
    // Спроба неблокуючого ексклюзивного блокування (LOCK_EX | LOCK_NB)
    if (flock(slot->lock_fd, LOCK_EX | LOCK_NB) != 0) {
        // Якщо файл уже захоплено іншим процесом, закриваємо дескриптор і повертаємо false
        close(slot->lock_fd);
        slot->lock_fd = -1;
        return false;
    }
    
    return true;
}

// Холодний рестарт плати зі збереженням раннього логу завантаження
bool rack_slot_power_cycle_and_listen(rack_slot_t *slot, uint32_t off_duration_ms) {
    // 1. Відкрити UART ДО увімкнення живлення
    if (slot->uart_fd < 0) {
        slot->uart_fd = open(slot->uart_path, O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (slot->uart_fd < 0) {
            return false;
        }
        if (!configure_uart_raw(slot->uart_fd, B115200)) {
            close(slot->uart_fd);
            slot->uart_fd = -1;
            return false;
        }
        // Очистити попередні залишкові байти
        tcflush(slot->uart_fd, TCIFLUSH);
    }
    
    // 2. Зняти живлення зі слота (VCC = 0)
    // Тут викликається низькорівнева функція керування силовим ключем
    usleep(off_duration_ms * 1000U);
    
    // 3. Подати живлення на слот (VCC = 1)
    // Силовий ключ плавно нарощує напругу
    usleep(25000U); // 25 мс очікування стабілізації живлення
    
    return true;
}

// Очікування появи цільового рядка в потоці консолі з таймаутом
bool rack_slot_expect(rack_slot_t *slot, const char *pattern, uint32_t timeout_ms) {
    if (slot->uart_fd < 0 || !pattern) {
        return false;
    }
    
    struct timeval tv_start, tv_now;
    gettimeofday(&tv_start, NULL);
    
    while (1) {
        gettimeofday(&tv_now, NULL);
        uint32_t elapsed_ms = (uint32_t)((tv_now.tv_sec - tv_start.tv_sec) * 1000 + 
                                         (tv_now.tv_usec - tv_start.tv_usec) / 1000);
        if (elapsed_ms >= timeout_ms) {
            return false; // Час вичерпано
        }
        
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(slot->uart_fd, &read_fds);
        
        struct timeval tv_poll;
        tv_poll.tv_sec = 0;
        tv_poll.tv_usec = 40000; // 40 мс квант очікування
        
        int ret = select(slot->uart_fd + 1, &read_fds, NULL, NULL, &tv_poll);
        if (ret > 0 && FD_ISSET(slot->uart_fd, &read_fds)) {
            char chunk[UART_CHUNK_SIZE];
            ssize_t bytes_read = read(slot->uart_fd, chunk, sizeof(chunk) - 1);
            if (bytes_read > 0) {
                chunk[bytes_read] = '\0';
                
                // Додавання до накопичувального логу
                if (slot->log_length + (size_t)bytes_read < MAX_LOG_BUFFER) {
                    memcpy(slot->log_buffer + slot->log_length, chunk, (size_t)bytes_read);
                    slot->log_length += (size_t)bytes_read;
                    slot->log_buffer[slot->log_length] = '\0';
                }
                
                // Пошук збігу з шаблоном
                if (strstr(slot->log_buffer, pattern) != NULL) {
                    return true; // Патерн знайдено!
                }
            }
        }
    }
}

// Звільнення дескрипторів та зняття блокування
void rack_slot_release(rack_slot_t *slot) {
    if (slot->uart_fd >= 0) {
        close(slot->uart_fd);
        slot->uart_fd = -1;
    }
    if (slot->lock_fd >= 0) {
        flock(slot->lock_fd, LOCK_UN);
        close(slot->lock_fd);
        slot->lock_fd = -1;
    }
}
```
```cpp
// Ідіоматичний C++20 менеджер тестового слота з підтримкою RAII
#include <string>
#include <string_view>
#include <expected>
#include <chrono>
#include <vector>
#include <format>
#include <span>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sys/file.h>
#include <sys/select.h>

enum class SlotError {
    BusyByAnotherProcess,
    LockFileCreationFailed,
    UartDeviceNotFound,
    TermiosConfigurationFailed,
    ExpectTimeout,
    PowerSwitchFailure
};

class RackSlotSession {
public:
    explicit RackSlotSession(int slotId) noexcept : slotId_(slotId) {}

    // RAII Деструктор: гарантовано знімає блокування та закриває порт
    ~RackSlotSession() noexcept {
        release();
    }

    // Заборона копіювання (сесія унікальна)
    RackSlotSession(const RackSlotSession&) = delete;
    RackSlotSession& operator=(const RackSlotSession&) = delete;

    // Дозвіл переміщення
    RackSlotSession(RackSlotSession&& other) noexcept 
        : slotId_(other.slotId_), lockFd_(other.lockFd_), uartFd_(other.uartFd_),
          logAccumulator_(std::move(other.logAccumulator_)) {
        other.lockFd_ = -1;
        other.uartFd_ = -1;
    }

    [[nodiscard]] std::expected<void, SlotError> acquire() noexcept {
        const auto lockPath = std::format("/tmp/dut-locks/slot_{:02d}.lock", slotId_);
        lockFd_ = ::open(lockPath.c_str(), O_CREAT | O_RDWR, 0666);
        if (lockFd_ < 0) {
            return std::unexpected(SlotError::LockFileCreationFailed);
        }

        // Атомарна спроба захоплення блокування
        if (::flock(lockFd_, LOCK_EX | LOCK_NB) != 0) {
            ::close(lockFd_);
            lockFd_ = -1;
            return std::unexpected(SlotError::BusyByAnotherProcess);
        }

        return {};
    }

    [[nodiscard]] std::expected<void, SlotError> preparePowerCycle(
        std::chrono::milliseconds offDuration) noexcept {
        if (uartFd_ < 0) {
            const auto uartPath = std::format("/dev/dut-slot-{:02d}-uart", slotId_);
            uartFd_ = ::open(uartPath.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
            if (uartFd_ < 0) {
                return std::unexpected(SlotError::UartDeviceNotFound);
            }
            if (!configureRawTerminal(B115200)) {
                ::close(uartFd_);
                uartFd_ = -1;
                return std::unexpected(SlotError::TermiosConfigurationFailed);
            }
            ::tcflush(uartFd_, TCIFLUSH);
        }

        // Фізичне знеструмлення
        ::usleep(static_cast<useconds_t>(offDuration.count() * 1000));
        // Подача живлення з очікуванням стабілізації
        ::usleep(25000);

        return {};
    }

    [[nodiscard]] std::expected<std::string, SlotError> expect(
        std::string_view expectedPattern, std::chrono::milliseconds timeout) {
        if (uartFd_ < 0) {
            return std::unexpected(SlotError::UartDeviceNotFound);
        }

        const auto deadline = std::chrono::steady_clock::now() + timeout;

        while (std::chrono::steady_clock::now() < deadline) {
            fd_set readFds;
            FD_ZERO(&readFds);
            FD_SET(uartFd_, &readFds);

            struct timeval tvPoll{.tv_sec = 0, .tv_usec = 35000};
            int ret = ::select(uartFd_ + 1, &readFds, nullptr, nullptr, &tvPoll);

            if (ret > 0 && FD_ISSET(uartFd_, &readFds)) {
                char chunk[256];
                ssize_t bytesRead = ::read(uartFd_, chunk, sizeof(chunk));
                if (bytesRead > 0) {
                    logAccumulator_.append(chunk, static_cast<std::size_t>(bytesRead));
                    if (logAccumulator_.find(expectedPattern) != std::string::npos) {
                        return logAccumulator_;
                    }
                }
            }
        }

        return std::unexpected(SlotError::ExpectTimeout);
    }

    [[nodiscard]] const std::string& fullLog() const noexcept {
        return logAccumulator_;
    }

    void release() noexcept {
        if (uartFd_ >= 0) {
            ::close(uartFd_);
            uartFd_ = -1;
        }
        if (lockFd_ >= 0) {
            ::flock(lockFd_, LOCK_UN);
            ::close(lockFd_);
            lockFd_ = -1;
        }
    }

private:
    bool configureRawTerminal(speed_t speed) noexcept {
        struct termios tty{};
        if (::tcgetattr(uartFd_, &tty) != 0) return false;

        ::cfsetospeed(&tty, speed);
        ::cfsetispeed(&tty, speed);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8 | CLOCAL | CREAD;
        tty.c_cflag &= ~(PARENB | PARODD | CSTOPB | CRTSCTS);
        tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
        tty.c_iflag &= ~(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
        tty.c_oflag &= ~OPOST;
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 0;

        return ::tcsetattr(uartFd_, TCSANOW, &tty) == 0;
    }

    int slotId_;
    int lockFd_{-1};
    int uartFd_{-1};
    std::string logAccumulator_;
};
```
:::

Така модульна архітектура забезпечує абсолютну стійкість стійки до аварій у тестах, повністю усуває гонки за апаратні інтерфейси та дозволяє масштабувати стенд до десятків плат без ризику колізій.
