# 📋 Регістри та системний API керування сигналом Break у UART

Цей довідник містить систематичний опис програмно-апаратних інтерфейсів для генерації, детекції та обробки сигналу Break у послідовних лініях зв'язку: системні виклики та прапорці POSIX `termios` в операційній системі Linux, функціонал Win32 Communications API, низькорівневі механізми ядра `serial_core` і Magic SysRq, а також карти регістрів і бітові поля мікроконтролерів 16550, STM32, ESP32, Nordic nRF52, NXP LPC, Microchip SAM, AVR та PIC.

---

### 1. Системний інтерфейс POSIX Termios у середовищі Linux та UNIX

В операційних системах сімейства POSIX керування послідовним терміналом здійснюється через структуру `struct termios` (заголовок `<termios.h>`) та низькорівневі керуючі виклики `ioctl` (заголовок `<sys/ioctl.h>`).

#### 1.1. Системні функції та запити ioctl для генерації розриву

Для переведення передавача у стан Break стандарт POSIX передбачає два основні механізми: високорівневу функцію `tcsendbreak()` та прямі запити драйверу термінала через виклик `ioctl()`.

:::tabs
```c
/* Системні виклики керування сигналом Break на мові C */
#include <termios.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* Відправка нормованого імпульсу Break */
int tcsendbreak(int fd, int duration);

/* Низькорівневе пряме увімкнення та вимкнення стану розриву */
int ioctl_set_break(int fd) {
    return ioctl(fd, TIOCSBRK);
}

int ioctl_clear_break(int fd) {
    return ioctl(fd, TIOCCBRK);
}
```
```cpp
// Системні виклики керування сигналом Break на мові C++20
#include <termios.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <system_error>

namespace serial_api {

inline void send_break(int fd, int duration = 0) {
    if (::tcsendbreak(fd, duration) != 0) {
        throw std::system_error(errno, std::generic_category(), "tcsendbreak failed");
    }
}

inline void set_break_state(int fd, bool active) {
    const unsigned long request = active ? TIOCSBRK : TIOCCBRK;
    if (::ioctl(fd, request) != 0) {
        throw std::system_error(errno, std::generic_category(), "ioctl break request failed");
    }
}

} // namespace serial_api
```
:::

Функція `tcsendbreak(fd, duration)` є найбільш переносним засобом. Коли параметр `duration` дорівнює `0`, функція генерує розрив лінії тривалістю від **0.25 до 0.5 секунди** (від 250 до 500 мілісекунд). Якщо значення `duration` більше нуля, у класичному стандарті POSIX.1 тривалість імпульсу визначалася множенням на фіксований часовий квант драйвера. Проте в багатьох версіях ядра Linux значення `duration > 0` розглядається як ідентичне нулю або інтерпретується залежно від конкретного апаратного драйвера мікросхеми.

Запит `ioctl(fd, TIOCSBRK)` перемикає лінію передавача TX у стан Space (логічний «0») і залишає її в цьому стані **нескінченно довго**, блокуючи звичайний вивід даних. Лінія залишається притиснутою до нуля доти, доки програма явно не виконає парний виклик `ioctl(fd, TIOCCBRK)`. Ця пара викликів незамінна, коли необхідно згенерувати імпульс нестандартної тривалості (наприклад, мікросекундний Break для протоколів DMX512 чи LIN) із використанням системних функцій точного сну `usleep()` чи `nanosleep()`.

#### 1.2. Конфігураційні прапорці поля `c_iflag` у структурі `termios`

Поведінка термінального драйвера при отриманні вхідного сигналу Break від підключеного пристрою налаштовується через поле вхідних прапорців `c_iflag` структури `struct termios`. Чотири прапорці визначають повний життєвий цикл вхідної події:

```
Порядок аналізу прапорців при отриманні Break у підсистемі termios:
                 ┌───────────────────────────┐
                 │  Отримано Break від UART  │
                 └─────────────┬─────────────┘
                               │
                      [IGNBRK == 1?]
                       /           \
                    ТАК             НІ
                    /                 \
        ┌─────────────────────┐   [BRKINT == 1?]
        │  Мовчки викинути    │    /          \
        │  (сигнал відкинуто) │  ТАК           НІ
        └─────────────────────┘  /               \
              ┌────────────────────────┐    [PARMRK == 1?]
              │ Очистити буфери черги  │     /          \
              │ + надіслати SIGINT     │   ТАК           НІ
              └────────────────────────┘   /               \
                    ┌─────────────────────────┐   ┌───────────────────────┐
                    │ Вставити в потік байти  │   │ Вставити в потік один │
                    │ \377 \0 \0 (3 байти)    │   │ нульовий байт \0      │
                    └─────────────────────────┘   └───────────────────────┘
```

1. **`IGNBRK` (Ignore Break)**:
   Значення `0x0001`. Якщо цей біт встановлено, підсистема TTY повністю ігнорує сигнал Break. Жодні дані не додаються у чергу прийому, жодні сповіщення не надсилаються програмам. Цей режим типово застосовується у фонових сервісах опитування давачів, де випадковий розрив кабелю не повинен переривати виконання процесу.

2. **`BRKINT` (Break Interrupt)**:
   Значення `0x0002`. Якщо `IGNBRK` вимкнено, а `BRKINT` увімкнено, сигнал Break призводить до негайного скидання вхідного та вихідного буферів порту (`tcflush`) та відправки сигналу `SIGINT` групі процесів переднього плану термінала. Це класична поведінка для інтерактивних оболонок командного рядка (Shell).

3. **`IGNPAR` (Ignore Framing and Parity Errors)**:
   Значення `0x0004`. Дозволяє ігнорувати поодинокі помилки кадрування та парності. Якщо `IGNBRK` вимкнено, а `IGNPAR` увімкнено при скинутому `BRKINT`, поодинокі спотворення стоп-бітів не генерують байтів помилок.

4. **`PARMRK` (Mark Parity and Break Errors)**:
   Значення `0x0008`. Якщо ввімкнено `PARMRK` (при `IGNBRK=0` та `BRKINT=0`), драйвер кодує сигнал Break спеціальною трьохбайтовою послідовністю символів `\377 \0 \0` (0xFF 0x00 0x00). Якщо у вхідному потоці зустрічається звичайний байт даних `\377`, драйвер дублює його як `\377 \377`, що усуває будь-яку неоднозначність під час розбору двійкового протоколу.

Таблиця станів вхідного потоку залежно від комбінації прапорців `c_iflag`:

| `IGNBRK` | `BRKINT` | `PARMRK` | Результат виклику `read()` при виявленні Break на лінії |
| :--- | :--- | :--- | :--- |
| `1` | будь-яке | будь-яке | **Подія ігнорується**: буфер читання порожній, сигнал відкинуто. |
| `0` | `1` | будь-яке | **Переривання процесу**: буфери скинуто, надсилається сигнал `SIGINT`. |
| `0` | `0` | `1` | **Екранований маркер**: у буфер читання надходить 3 байти: `0xFF, 0x00, 0x00`. |
| `0` | `0` | `0` | **Нульовий байт**: у буфер читання надходить 1 байт: `0x00`. |

---

### 2. Інтерфейс Windows Communications API (Win32)

В операційних системах сімейства Microsoft Windows послідовний порт відкривається як стандартний файловий дескриптор через функцію `CreateFileA("COM1", ...)`.

Для керування сигналом Break у Win32 API використовуються такі спеціалізовані системні функції:

:::tabs
```c
/* Керування послідовним портом через Win32 API на мові C */
#include <windows.h>

BOOL win32_send_break(HANDLE hSerial, DWORD duration_ms) {
    /* Перемикання лінії TX у стан Space (логічний нуль) */
    if (!SetCommBreak(hSerial)) return FALSE;
    Sleep(duration_ms);
    /* Повернення лінії TX у стан Mark (логічна одиниця) */
    return ClearCommBreak(hSerial);
}
```
```cpp
// Керування послідовним портом через Win32 API на мові C++
#include <windows.h>
#include <stdexcept>
#include <chrono>
#include <thread>

class Win32SerialBreak {
public:
    static void send_break(HANDLE handle, std::chrono::milliseconds duration) {
        if (!::SetCommBreak(handle)) {
            throw std::runtime_error("SetCommBreak failed");
        }
        std::this_thread::sleep_for(duration);
        if (!::ClearCommBreak(handle)) {
            throw std::runtime_error("ClearCommBreak failed");
        }
    }
};
```
:::

Для виявлення вхідного Break у Windows застосовується маска подій `SetCommMask(hSerial, EV_BREAK | EV_RXCHAR)` у поєднанні з асинхронним викликом `WaitCommEvent()`. Коли віддалений пристрій генерує Break, операційна система виставляє прапорець `EV_BREAK`, що дозволяє потоку обробки негайно зафіксувати подію без постійного опитування портів.

---

### 3. Рівень ядра Linux: serial_core та Magic SysRq

У підсистемі ядра `drivers/tty/serial/serial_core.c` обробка сигналу Break відбувається в контексті обробника переривання апаратного порту.

:::tabs
```c
/* Фрагмент інтерфейсу ядра serial_core (drivers/tty/serial/serial_core.c) */
#include <linux/serial_core.h>
#include <linux/tty.h>
#include <linux/sysrq.h>

/* Обробник Break у контексті переривання драйвера порту */
void kernel_uart_handle_break(struct uart_port *port) {
    if (uart_handle_break(port))
        return;

    /* Вставка TTY_BREAK у буфер термінала */
    tty_insert_flip_char(&port->state->port, 0, TTY_BREAK);
}
```
```cpp
// Концептуальна модель поведінки ядра serial_core на C++
#include <cstdint>
#include <chrono>

struct UartPort {
    bool is_console{true};
    bool sysrq_enabled{true};
    std::chrono::steady_clock::time_point sysrq_timeout{};
    bool in_sysrq_mode{false};
};

class SerialCoreHandler {
public:
    static bool handle_break(UartPort& port) noexcept {
        if (port.is_console && port.sysrq_enabled) {
            // Активація 5-секундного вікна очікування клавіші SysRq
            port.in_sysrq_mode = true;
            port.sysrq_timeout = std::chrono::steady_clock::now() + std::chrono::seconds(5);
            return true; // Перехоплено підсистемою SysRq
        }
        return false; // Передати далі в термінальний буфер
    }
};
```
:::

Функція `uart_handle_break()` перевіряє, чи скомпільовано ядро з підтримкою магічних комбінацій `CONFIG_MAGIC_SYSRQ`. Якщо поточний порт зареєстровано як системну консоль (`port->cons`), ядро активує таймер очікування магічної команди (типово 5 секунд). Усі наступні байти перевіряються таблицею обробників `sysrq_key_table`:
- `b` — викликає `emergency_restart()` (негайний апаратний перезапуск);
- `s` — викликає `emergency_sync()` (скидання дискових буферів);
- `u` — викликає `emergency_remount()` (перемонтування файлових систем у read-only);
- `t` — викликає `show_state()` (друк стеків усіх активних потоків ядра);
- `w` — викликає `show_unhandled()` (друк заблокованих задач у стані D).

---

### 4. Регістри промислового контролера 16550 / 8250 UART

Контролер 16550, створений компанією National Semiconductor, став промисловим стандартом де-факто для персональних комп'ютерів, промислових контролерів та систем на кристалі (SoC).

```
Карта регістрів 16550 UART (базові зміщення):
+0: RBR (Rx Buffer) / THR (Tx Holding)
+1: IER (Interrupt Enable Register)
+2: IIR (Interrupt Identification) / FCR (FIFO Control)
+3: LCR (Line Control Register)       <--- Керування передачею Break (Bit 6)
+4: MCR (Modem Control Register)
+5: LSR (Line Status Register)        <--- Фіксація Break Interrupt (Bit 4) та FE (Bit 3)
+6: MSR (Modem Status Register)
+7: SCR (Scratchpad Register)
```

#### Регістр керування лінією: Line Control Register (LCR, зміщення +3)

Регістр LCR відповідає за конфігурацію формату кадру та примусове керування станом лінії передачі:
- **Bit 6 (SBRK — Set Break)**: Запис `1` у цей біт примусово переводить вихід TX у стан Space (логічний нуль), блокуючи роботу зсувного регістра передавача. Вміст FIFO при цьому не знищується, але передача зупиняється. Запис `0` знімає стан розриву та відновлює штатні передачі.
- **Bit 7 (DLAB)**: Доступ до дільника швидкості генератора.
- **Bits 5..3 (Parity Select)**: Налаштування парності (Even, Odd, Stick Parity).
- **Bit 2 (Stop Bits)**: Кількість стоп-бітів (0 = 1 стоп-біт, 1 = 1.5 або 2 стоп-біти).
- **Bits 1..0 (WLS[1:0])**: Довжина слова даних (5, 6, 7 або 8 бітів).

#### Регістр стану лінії: Line Status Register (LSR, зміщення +5)

Регістр LSR містить прапорці помилок поточного прийнятого символу:
- **Bit 4 (BI — Break Interrupt)**: Встановлюється в `1`, коли лінія RX перебуває у стані Space довше, ніж триває повний кадр (старт-біт + біти даних + біт парності + стоп-біт). Прапорець автоматично скидається в `0` після читання регістра LSR процесором.
- **Bit 3 (FE — Framing Error)**: Встановлюється в `1`, якщо на позиції стоп-біта виявлено нульовий рівень замість одиниці.
- **Bit 2 (PE — Parity Error)**: Помилка перевірки парності.
- **Bit 1 (OE — Overrun Error)**: Переповнення буфера прийому.
- **Bit 0 (DR — Data Ready)**: Наявність хоча б одного байта у буфері прийому.

---

### 5. Периферія USART мікроконтролерів STM32

У мікроконтролерах STM32 (родини F0, F1, F4, F7, G0, G4, L4, H7) модуль USART містить розвинену апаратну логіку для формування та розпізнавання розривів лінії.

```
Архітектура обробки Break у STM32 USART:
Лінія TX:
  CR1.SBK (F1/F4) або RQR.SBKRQ (G4/H7) -> [Генератор Break] -> 10/11 бітів 0V -> Стоп-біт

Лінія RX:
  Вхідний сигнал -> [Детектор довжини 10/11 біт] -> CR2.LBDL
                                                  -> ISR.LBDF (прапорець переривання)
                                                  -> ISR.FE   (помилка кадрування)
```

#### Бібліотечні функції STM32 HAL та LL

Для роботи з сигналом Break у середовищі STM32 HAL передбачено спеціальні функції:
- `HAL_LIN_SendBreak(UART_HandleTypeDef *huart)`: генерує кадровий розрив тривалістю 10 або 11 бітів.
- `LL_USART_RequestBreakSending(USART_TypeDef *USARTx)`: низькорівневий запис у біт `SBKRQ` для негайної відправки Break.
- `LL_USART_IsActiveFlag_LBD(USART_TypeDef *USARTx)`: перевірка прапорця детектора розриву шини LIN.
- `LL_USART_ClearFlag_LBD(USART_TypeDef *USARTx)`: очищення прапорця переривання LIN Break.

---

### 6. Контролер UART в архітектурі Espressif ESP32

Мікроконтролери ESP32, ESP32-S3 та ESP32-C3 містять незалежні апаратні лічильники тривалості низького рівня на шині UART.

| Назва регістра ESP32 | Поле бітів | Функціональне призначення |
| :--- | :--- | :--- |
| **`UART_CONF0_REG`** | `UART_TXD_BRK` (Bit 8) | Примусове перемикання лінії TX у нульовий рівень Space. Працює як статичний перемикач: `1` — активний розрив, `0` — відновлення передавача. |
| **`UART_INT_ENA_REG`** | `UART_BRK_DET_INT_ENA` (Bit 7) | Біт дозволу апаратного переривання за подією виявлення сигналу Break. |
| **`UART_INT_RAW_REG`** | `UART_BRK_DET_INT_RAW` (Bit 7) | Необроблений статус детектора Break (встановлюється, коли RX утримується в нулі довше тривалості кадру). |
| **`UART_INT_CLR_REG`** | `UART_BRK_DET_INT_CLR` (Bit 7) | Запис одиниці очищає прапорець переривання Break. |
| **`UART_AUTOBAUD_REG`**| `UART_GLITCH_FILT` (Bits 11..0)| Цифровий фільтр шумів, що запобігає хибному спрацьовуванню детектора Break від коротких завад. |

В офіційній бібліотеці ESP-IDF для відправки Break застосовується функція `uart_write_bytes_with_break(uart_port_t uart_num, const void* src, size_t size, int brk_len)`, яка дозволяє передати масив даних із автоматичним додаванням імпульсу Break заданої кількості бітових інтервалів перед початком передачі.

---

### 7. Nordic Semiconductor nRF52 (UARTE з EasyDMA) та Microchip SAM

У бездротових чіпах Nordic nRF52832 та nRF52840 периферія UARTE з прямим доступом до пам'яті EasyDMA обробляє помилки кадрування та сигнали Break через регістри подій і помилок:
- **`TASKS_STARTRX`**: Запуск прийому даних EasyDMA у буфер RAM.
- **`EVENTS_ERROR`**: Подія, що генерує переривання процесора при виникненні будь-якої апаратної помилки на лінії.
- **`ERRORSRC` (Error Source Register)**:
  - **Bit 1 (FRAMING)**: Зафіксовано помилку стоп-біта (Framing Error).
  - **Bit 2 (BREAK)**: Лінія RX утримувалася в нулі довше тривалості одного повного кадру.
- **`TASKS_STOPRX`**: Зупинка прийому після фіксації сигналу Break для скидання вказівників буфера EasyDMA.

У мікроконтролерах родини Microchip SAM D21 / SAME54 периферійний модуль SERCOM (USART Mode) використовує регістр `CTRLB`:
- **`SERCOM_USART_CTRLB_CMD(1)`**: Команда виконання швидкого скидання стану приймача після виявлення прапорця `INTFLAG.ERROR` та читання нульового байта помилки.
- **`STATUS.FERR` (Frame Error)**: Прапорець статусу поточного байта в апаратному буфері.

---

### 8. USB-UART контролери FTDI та Silicon Labs: команди драйверів

У спеціалізованих мікросхемах мостів USB-UART пряме керування станом Break здійснюється через бібліотечні функції вендорних драйверів (FTDI D2XX та Silicon Labs CP210x VCP):

:::tabs
```c
/* Керування Break через бібліотеки FTDI D2XX та Silicon Labs VCP на мові C */
#include <ftd2xx.h>

/* FTDI D2XX API */
FT_STATUS ftdi_set_break_on(FT_HANDLE ftHandle) {
    return FT_SetBreakOn(ftHandle);
}

FT_STATUS ftdi_set_break_off(FT_HANDLE ftHandle) {
    return FT_SetBreakOff(ftHandle);
}
```
```cpp
// Керування Break через обгортку FTDI D2XX на C++
#include <ftd2xx.h>
#include <stdexcept>

class FtdiBreakGuard {
public:
    explicit FtdiBreakGuard(FT_HANDLE handle) : handle_{handle} {
        if (::FT_SetBreakOn(handle_) != FT_OK) {
            throw std::runtime_error("FT_SetBreakOn failed");
        }
    }

    ~FtdiBreakGuard() noexcept {
        ::FT_SetBreakOff(handle_);
    }

    FtdiBreakGuard(const FtdiBreakGuard&) = delete;
    FtdiBreakGuard& operator=(const FtdiBreakGuard&) = delete;

private:
    FT_HANDLE handle_;
};
```
:::

Бібліотека FTDI транслює виклик `FT_SetBreakOn()` у службовий USB-пакет `SIO_SET_BREAK_REQUEST` (значення запиту `0x05`), який внутрішній процесор чіпа FT232R обробляє як команду примусового замикання лінії TX на нульовий рівень Space.
