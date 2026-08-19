# ⚙️ Практична генерація та детекція сигналу Break у коді

Цей практичний посібник розбирає повну реалізацію генерації та надійного розпізнавання сигналу Break у мікроконтролерних системах і Linux: від формування прецизійних інтервалів протоколу DMX512/LIN до апаратного обробника переривань UART із кільцевим буфером і прапорцями помилок кадрування.

---

### 1. Формування прецизійного Break для DMX512 та LIN

У протоколах керування сценічним світлом DMX512 (швидкість 250 кбод) та автомобільній шині LIN стандарт вимагає суворого дотримання часових параметрів сигналу Break та наступного розділювача (MAB / Delimiter).

Головна складність полягає в тому, що стандартний апаратний біт передавача `SBK` у багатьох мікроконтролерах формує розрив фіксованої довжини рівно в 10 або 11 бітів кадру. Для протоколу DMX512 цього замало: стандарт ANSI E1.11 вимагає, щоб мінімальна тривалість Break становила не менше 88 мікросекунд (що відповідає 22 бітовим інтервалам на швидкості 250 кбод). Типове рекомендоване значення становить 100–176 мкс.

Найбільш надійний та повторюваний інженерний метод — тимчасове перемикання піна TX з периферії UART у режим звичайного цифрового виходу (GPIO Output Push-Pull) з відліком мікросекундного таймера.

Цей процес складається з п'яти послідовних кроків:
1. **Перевірка завершення попереднього кадру**: Обов'язково зачекати встановлення прапорця `TC` (Transmission Complete) або `TXC` у статусному регістрі UART, щоб не обірвати передачу останнього байта попереднього пакета.
2. **Перехоплення керування виводом**: Перемкнути конфігурацію виводу мікроконтролера з альтернативної функції UART на вихід загального призначення GPIO та встановити низький рівень (0V) на 100 мкс (Break).
3. **Формування розділювача MAB**: Встановити високий рівень (3.3V/5V) на 12 мкс для формування обов'язкового розділювача Mark After Break (MAB).
4. **Повернення периферії**: Повернути керування піном апаратному блоку UART.
5. **Потокова передача слотів**: Надіслати стартовий код `0x00` та 512 байтів значень яскравості каналів через звичайний зсувний регістр UART.

Нижче наведено закінчену реалізацію модуля передавача DMX512 на мовах C та C++:

:::tabs
```c
/* dmx_transmitter.c - Генератор пакетів DMX512 з прецизійним Break */
#include <stdint.h>
#include <stdbool.h>

#define DMX_CHANNELS 512
#define DMX_BREAK_US 100    /* Стандарт ANSI E1.11: >= 88 мкс */
#define DMX_MAB_US   12     /* Mark After Break: >= 8 мкс */

/* Низькорівневі апаратні примітиви платформи */
extern void hw_delay_us(uint32_t us);
extern void uart_tx_pin_set_gpio_low(void);
extern void uart_tx_pin_set_gpio_high(void);
extern void uart_tx_pin_restore_peripheral(void);
extern void uart_send_byte_blocking(uint8_t byte);

typedef struct {
    uint8_t start_code;
    uint8_t channels[DMX_CHANNELS];
} dmx_packet_t;

void dmx_send_packet(const dmx_packet_t *packet) {
    /* Крок 1: Формування Break (утримання лінії в 0V) */
    uart_tx_pin_set_gpio_low();
    hw_delay_us(DMX_BREAK_US);

    /* Крок 2: Формування Mark After Break (повернення в 1) */
    uart_tx_pin_set_gpio_high();
    hw_delay_us(DMX_MAB_US);

    /* Крок 3: Повернення піна під контроль апаратного UART */
    uart_tx_pin_restore_peripheral();

    /* Крок 4: Передача стартового коду (0x00 для димерів) */
    uart_send_byte_blocking(packet->start_code);

    /* Крок 5: Послідовна відправка всіх 512 каналів даних */
    for (uint32_t i = 0; i < DMX_CHANNELS; ++i) {
        uart_send_byte_blocking(packet->channels[i]);
    }
}
```
```cpp
// dmx_transmitter.hpp / .cpp - Генератор пакетів DMX512 на C++20
#include <cstdint>
#include <array>
#include <span>

extern "C" {
    void hw_delay_us(uint32_t us);
    void uart_tx_pin_set_gpio_low();
    void uart_tx_pin_set_gpio_high();
    void uart_tx_pin_restore_peripheral();
    void uart_send_byte_blocking(uint8_t byte);
}

class DmxTransmitter {
public:
    static constexpr size_t ChannelCount = 512;
    static constexpr uint32_t BreakDurationUs = 100; // >= 88 мкс
    static constexpr uint32_t MabDurationUs = 12;    // >= 8 мкс

    struct Packet {
        uint8_t start_code{0x00};
        std::array<uint8_t, ChannelCount> channels{};
    };

    void send_packet(const Packet& packet) const {
        // 1. Апаратний перехід у стан Break через GPIO
        uart_tx_pin_set_gpio_low();
        hw_delay_us(BreakDurationUs);

        // 2. Інтервал Mark After Break
        uart_tx_pin_set_gpio_high();
        hw_delay_us(MabDurationUs);

        // 3. Відновлення периферії UART
        uart_tx_pin_restore_peripheral();

        // 4. Стартовий код
        uart_send_byte_blocking(packet.start_code);

        // 5. Послідовна передача слотів даних через безпечний span
        std::span<const uint8_t> slots{packet.channels};
        for (uint8_t val : slots) {
            uart_send_byte_blocking(val);
        }
    }
};
```
:::

---

### 2. Апаратна детекція Break на стороні приймача (ISR)

На стороні приймача (мікроконтролера STM32, ESP32 або AVR) сигнал Break проявляється як **помилка кадрування (Framing Error / FE)**, що обов'язково супроводжується нульовим значенням у зсувному регістрі даних (`0x00`).

Якщо обробник переривань не вміє розрізняти помилку кадрування від валідного нуля даних, лічильник прийнятих байтів зміщується, і всі наступні канали починають керувати чужими освітлювальними приладами на сцені.

Логіка кінцевого автомата обробника переривань (ISR):
1. **Зчитування статусу**: Перевірити біт помилки кадрування `FE` у статусному регістрі периферії (`USART_SR` або `USART_ISR`).
2. **Зчитування байта даних**: Обов'язково прочитати байт із регістра даних `USART_RDR` або `DR`, щоб скинути апаратні прапорці переривання.
3. **Класифікація події**:
   - Якщо `FE == 1` і `байт == 0x00` → зафіксовано **початок нового кадру (Break Condition)**. Лічильник каналів скидається в 0, а автомат переходить у стан очікування стартового коду (`DMX_STATE_WAIT_START_CODE`).
   - Якщо `FE == 0` → байт є валідними даними, які записуються в буфер каналів за поточним індексом.
4. **Завершення кадру**: Коли лічильник досягає 512 байтів, виставляється атомарний прапорець готовності `frame_ready`, а автомат повертається в очікування наступного розриву лінії.

Нижче наведено закінчену реалізацію приймального автомата на мовах C та C++:

:::tabs
```c
/* uart_break_receiver.c - Обробник переривань UART із детекцією Break */
#include <stdint.h>
#include <stdbool.h>

#define RX_BUFFER_SIZE 512

typedef enum {
    DMX_STATE_WAIT_BREAK = 0,
    DMX_STATE_WAIT_START_CODE,
    DMX_STATE_RECEIVE_DATA
} dmx_rx_state_t;

typedef struct {
    volatile dmx_rx_state_t state;
    volatile uint16_t channel_index;
    volatile bool frame_ready;
    uint8_t buffer[RX_BUFFER_SIZE];
} dmx_receiver_t;

static dmx_receiver_t g_dmx_rx;

/* Функція, що викликається з вектора переривання USART_IRQHandler */
void USART_Receive_ISR_Handler(uint32_t status_reg, uint8_t data_reg) {
    bool framing_error = (status_reg & (1u << 1)) != 0; /* Біт FE у USART_SR/ISR */

    if (framing_error) {
        if (data_reg == 0x00) {
            /* Зафіксовано валідний сигнал Break! */
            g_dmx_rx.state = DMX_STATE_WAIT_START_CODE;
            g_dmx_rx.channel_index = 0;
        }
        return;
    }

    switch (g_dmx_rx.state) {
        case DMX_STATE_WAIT_START_CODE:
            if (data_reg == 0x00) {
                /* Валідний стартовий код для каналів діммера */
                g_dmx_rx.state = DMX_STATE_RECEIVE_DATA;
                g_dmx_rx.channel_index = 0;
            } else {
                /* Чужий стартовий код (наприклад RDM або текст) -> ігноруємо */
                g_dmx_rx.state = DMX_STATE_WAIT_BREAK;
            }
            break;

        case DMX_STATE_RECEIVE_DATA:
            if (g_dmx_rx.channel_index < RX_BUFFER_SIZE) {
                g_dmx_rx.buffer[g_dmx_rx.channel_index++] = data_reg;
                if (g_dmx_rx.channel_index == RX_BUFFER_SIZE) {
                    g_dmx_rx.frame_ready = true;
                    g_dmx_rx.state = DMX_STATE_WAIT_BREAK;
                }
            }
            break;

        case DMX_STATE_WAIT_BREAK:
        default:
            /* Очікуємо наступного розриву лінії, ігноруючи решту байтів */
            break;
    }
}
```
```cpp
// uart_break_receiver.hpp - Безпечний C++ автомат детекції Break
#include <cstdint>
#include <array>
#include <atomic>

class DmxReceiver {
public:
    static constexpr size_t BufferSize = 512;

    enum class State : uint8_t {
        WaitBreak,
        WaitStartCode,
        ReceiveData
    };

    void handle_uart_irq(uint32_t status_reg, uint8_t data_reg) noexcept {
        const bool framing_error = (status_reg & (1u << 1)) != 0;

        if (framing_error) {
            if (data_reg == 0x00) {
                // Виявлено Break: синхронізація початку пакета
                state_ = State::WaitStartCode;
                channel_idx_ = 0;
            }
            return;
        }

        switch (state_) {
            case State::WaitStartCode:
                if (data_reg == 0x00) {
                    state_ = State::ReceiveData;
                    channel_idx_ = 0;
                } else {
                    state_ = State::WaitBreak;
                }
                break;

            case State::ReceiveData:
                if (channel_idx_ < BufferSize) {
                    buffer_[channel_idx_++] = data_reg;
                    if (channel_idx_ == BufferSize) {
                        frame_ready_.store(true, std::memory_order_release);
                        state_ = State::WaitBreak;
                    }
                }
                break;

            case State::WaitBreak:
            default:
                break;
        }
    }

    [[nodiscard]] bool is_frame_ready() const noexcept {
        return frame_ready_.load(std::memory_order_acquire);
    }

    void clear_frame_ready() noexcept {
        frame_ready_.store(false, std::memory_order_release);
    }

    [[nodiscard]] const std::array<uint8_t, BufferSize>& data() const noexcept {
        return buffer_;
    }

private:
    State state_{State::WaitBreak};
    size_t channel_idx_{0};
    std::atomic<bool> frame_ready_{false};
    std::array<uint8_t, BufferSize> buffer_{};
};
```
:::

---

### 3. Робота з сигналом Break у системному програмуванні POSIX (Linux)

В операційній системі Linux взаємодія з послідовним портом зазвичай відбувається через символьний файл пристрою (наприклад, `/dev/ttyUSB0` або `/dev/ttyS0`).

Коли програма повинна перехоплювати сигнали Break від віддаленого мікроконтролера, звичайний виклик `read()` не може відрізнити справжній байт `0x00` від сигналу Break, якщо не налаштувати режим маркування помилок.

Для цього використовується прапорець **`PARMRK`** у комбінації зі скинутими прапорцями `IGNBRK` та `BRKINT`. У цьому режимі термінальний драйвер ядра автоматично замінює кожну вхідну подію Break трьохбайтовою послідовністю:
```
0xFF, 0x00, 0x00
```
Якщо ж у потік даних надходить звичайний валідний байт `0xFF`, драйвер ядра дублює його як `0xFF 0xFF`. Завдяки цьому прикладний парсер отримує однозначний потік, у якому маркер розриву лінії ніколи не перетинається зі звичайними двійковими даними.

Нижче наведено закінчену консольну програму на мовах C та C++, яка відкриває послідовний порт, надсилає тестовий сигнал Break віддаленому пристрою та розбирає вхідний потік байтів на наявність маркерів розриву:

:::tabs
```c
/* posix_break_demo.c - Керування та виявлення Break у Linux */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <errno.h>

int open_and_configure_port(const char *device) {
    int fd = open(device, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        perror("open failed");
        return -1;
    }

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        perror("tcgetattr failed");
        close(fd);
        return -1;
    }

    /* Налаштування швидкості 115200 8N1 у сирому (raw) режимі */
    cfsetospeed(&tty, B115200);
    cfsetispeed(&tty, B115200);

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~(PARENB | PARODD | CSTOPB | CRTSCTS);

    /* 
     * Вхідні прапорці:
     * - Вимикаємо IGNBRK (щоб НЕ викидати Break)
     * - Вимикаємо BRKINT (щоб НЕ генерувати SIGINT)
     * - Вмикаємо PARMRK (щоб закодувати Break як \377 \0 \0)
     */
    tty.c_iflag &= ~(IGNBRK | BRKINT | IGNPAR | INLCR | ICRNL | IXON | IXOFF);
    tty.c_iflag |= PARMRK;
    tty.c_lflag = 0; /* Raw режим без канонічної обробки */
    tty.c_oflag = 0;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        perror("tcsetattr failed");
        close(fd);
        return -1;
    }

    return fd;
}

int main(int argc, char *argv[]) {
    const char *port_name = (argc > 1) ? argv[1] : "/dev/ttyUSB0";
    int fd = open_and_configure_port(port_name);
    if (fd < 0) return EXIT_FAILURE;

    printf("Порт %s відкрито. Відправляємо довгий Break (250 мс)...\n", port_name);

    /* 1. Відправка апаратного розриву лінії */
    if (tcsendbreak(fd, 0) != 0) {
        perror("tcsendbreak failed");
    } else {
        printf("Сигнал Break успішно надіслано в лінію.\n");
    }

    printf("Слухаємо лінію... (Очікування маркера Break: 0xFF 0x00 0x00)\n");
    uint8_t buf[256];
    for (int iter = 0; iter < 100; ++iter) {
        ssize_t n = read(fd, buf, sizeof(buf));
        if (n > 0) {
            for (ssize_t i = 0; i < n; ++i) {
                /* Перевірка трьохбайтової екранованої послідовності PARMRK */
                if (i + 2 < n && buf[i] == 0xFF && buf[i + 1] == 0x00 && buf[i + 2] == 0x00) {
                    printf(">>> [ВИЯВЛЕНО BREAK CONDITION НА ЛІНІЇ RX!]\n");
                    i += 2;
                } else {
                    printf("Байт даних: 0x%02X\n", buf[i]);
                }
            }
        }
        usleep(50000); /* 50 мс */
    }

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
// posix_break_demo.cpp - ООП-обгортка послідовного порту з підтримкою Break на C++
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <span>
#include <chrono>
#include <thread>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>

class SerialPort {
public:
    explicit SerialPort(const std::string& dev, speed_t baud = B115200) {
        fd_ = ::open(dev.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити послідовний порт: " + dev);
        }

        struct termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка tcgetattr");
        }

        ::cfsetospeed(&tty, baud);
        ::cfsetispeed(&tty, baud);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
        tty.c_cflag |= (CLOCAL | CREAD);
        tty.c_cflag &= ~(PARENB | PARODD | CSTOPB | CRTSCTS);

        // Налаштування прапорців: виловлювати Break через префікс PARMRK
        tty.c_iflag &= ~(IGNBRK | BRKINT | IGNPAR | INLCR | ICRNL | IXON | IXOFF);
        tty.c_iflag |= PARMRK;
        tty.c_lflag = 0;
        tty.c_oflag = 0;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка tcsetattr");
        }
    }

    ~SerialPort() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання (RAII-ресурс)
    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;

    // Дозвіл переміщення
    SerialPort(SerialPort&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
    SerialPort& operator=(SerialPort&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    void send_break() const {
        if (::tcsendbreak(fd_, 0) != 0) {
            throw std::runtime_error("Помилка tcsendbreak");
        }
    }

    [[nodiscard]] std::vector<uint8_t> read_bytes(size_t max_count = 256) const {
        std::vector<uint8_t> buffer(max_count);
        const ssize_t n = ::read(fd_, buffer.data(), max_count);
        if (n <= 0) {
            return {};
        }
        buffer.resize(static_cast<size_t>(n));
        return buffer;
    }

private:
    int fd_{-1};
};

int main(int argc, char* argv[]) {
    try {
        const std::string port = (argc > 1) ? argv[1] : "/dev/ttyUSB0";
        SerialPort serial{port};

        std::cout << "Порт " << port << " відкрито. Надсилаємо сигнал Break...\n";
        serial.send_break();
        std::cout << "Break надіслано. Очікуємо відповіді...\n";

        for (int i = 0; i < 50; ++i) {
            auto data = serial.read_bytes();
            if (!data.empty()) {
                std::span<const uint8_t> s{data};
                for (size_t idx = 0; idx < s.size(); ++idx) {
                    if (idx + 2 < s.size() && s[idx] == 0xFF && s[idx + 1] == 0x00 && s[idx + 2] == 0x00) {
                        std::cout << ">>> [ВИЯВЛЕНО BREAK CONDITION НА ЛІНІЇ RX!]\n";
                        idx += 2;
                    } else {
                        std::cout << "Дані: 0x" << std::hex << static_cast<int>(s[idx]) << std::dec << "\n";
                    }
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

---

### 4. Робота з DMA-буферизацією при отриманні Break

При використанні прямого доступу до пам'яті (DMA) для високошвидкісного прийому пакетів UART (наприклад, у мікроконтролерах STM32 з циклічним буфером `DMA Circular Mode`) сигнал Break потребує особливої уваги.

Коли на лінію надходить сигнал Break, контролер DMA продовжує автоматично записувати нульовий байт помилки кадрування у поточну позицію кільцевого буфера RAM, не знаючи про порушення протоколу. Якщо вчасно не перехопити цю подію, вказівник DMA зміститься, і наступний валідний кадр запишеться не з нульового індексу, а в довільне місце буфера.

Правильний алгоритм поєднання DMA та переривання Break:
1. Налаштувати переривання UART за подією помилки кадрування `USART_IT_ERR` або детектора LIN Break `USART_IT_LBD`.
2. В обробнику переривання негайно зупинити потік DMA (`HAL_UART_DMAStop` або скидання біта `DMA_SxCR_EN`).
3. Очистити лічильник залишку передачі DMA (`DMA_CNDTR` або `NDTR`) та встановити початкову адресу буфера.
4. Перезапустити прийом DMA для запису наступних 512 байтів нового пакета з нульового індексу пам'яті.

---

### 5. Програмне детектування Break таймером (Input Capture)

Якщо застосовуваний мікроконтролер не має виділеного апаратного прапорця Break або якщо лінія зв'язку підключена до виводу без вбудованого апаратного блоку UART (програмний емулятор Software UART / Bit-banging), розпізнавання Break реалізують за допомогою апаратного таймера в режимі захоплення входу (Input Capture):
1. Пін RX підключається до каналу захоплення таймера, налаштованого на фіксацію як спадного фронту (початок імпульсу), так і наростаючого фронту (кінець імпульсу).
2. За спадним фронтом лічильник таймера скидається в 0.
3. За наростаючим фронтом обробник переривання зчитує виміряну тривалість низького рівня `Δt`.
4. Якщо виміряний інтервал `Δt` перевищує тривалість повного кадру `10 × Tbit` (наприклад, `> 88 мкс` для DMX512 або `> 650 мкс` для LIN на швидкості 19200 бод), стан класифікується як валідний Break, і викликається функція скидання протокольного парсера.

---

### 6. Пастки програмування та надійність коду

Під час практичної розробки драйверів та обробників сигналу Break слід враховувати такі критичні фактори:
1. **Апаратна затримка перемикання GPIO/UART**: При перемиканні виводу мікроконтролера між периферією UART та режимом GPIO необхідно обов'язково переконатися, що регістр зсуву передавача порожній (прапорець `TC` або `TXC` дорівнює 1). Якщо перемкнути пін у нуль, поки попередній байт ще передається, останній символ буде спотворено.
2. **Вимоги до пам'яті в багатопотоковому коді**: У C++ обробниках прапорці готовності пакетів (`frame_ready_`) мусять використовувати атомарні операції з семантикою `std::memory_order_release` та `std::memory_order_acquire`, щоб гарантувати коректну видимість буфера даних між контекстом переривання та основним потоком програми.
3. **Обробка помилок при роботі з USB-UART перетворювачами**: Мікросхеми USB-UART (такі як FTDI FT232R, Silicon Labs CP2102, WCH CH340) емулюють сигнал Break через керуючі пакети USB Control Endpoint. Виклик `tcsendbreak()` або `ioctl(TIOCSBRK)` спричиняє затримку передачі через шину USB (від 1 до 2 мілісекунд), що слід враховувати в чутливих до часу протоколах.
4. **Захист від хибного детектування при підключенні кабелю на гарячу**: У момент встромляння кабелю в роз'єм механічний брязкіт контактів може згенерувати випадковий імпульс низького рівня довжиною 10–50 мікросекунд. Програмний автомат повинен ігнорувати такі поодинокі помилки кадрування, якщо вони не підтверджені нульовим байтом даних `0x00` або правильним стартовим кодом протоколу.
