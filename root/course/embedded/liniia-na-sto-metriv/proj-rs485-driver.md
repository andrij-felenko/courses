# ⚙️ Напівдуплексний драйвер RS-485: апаратне та програмне керування шиною

Напівдуплексний обмін по шині RS-485 вимагає точного часового узгодження роботи трансивера. Оскільки лінії `A` та `B` використовуються почергово як для передавання, так і для приймання, помилка у керуванні виводом дозволу передавача (`DE` — *Driver Enable*) навіть на тривалість одного біта призводить до втрати даних або апаратної колізії на шині.

## Пастка прапорців TXE та TC у контролері UART

Найпоширеніша помилка розробників вбудованого ПЗ виникає через нерозуміння двоступеневої буферизації периферійного модуля UART:

```
[ Процесор / DMA ] ──► [ Регістр даних TDR ] ──► [ Зсувний регістр TSR ] ──► TX Pin
                             │                           │
                     Прапорець TXE / TXRDY        Прапорець TC / TXC
                    (Буфер готовий до нового)    (Байт фізично вийшов у дріт)
```

1. **Прапорець TXE (Transmit Data Register Empty):** встановлюється в `1`, щойно байт переписано з регістру даних `TDR` у внутрішній зсувний регістр передавача `TSR`. У цей момент буфер вільний для наступного байта, але попередній байт **ще передається в лінію**. Якщо скинути сигнал `DE = 0` за подією `TXE`, передавач вимкнеться посеред передавання стоп-біта (або навіть даних), обрізавши хвіст кадру.
2. **Прапорець TC (Transmission Complete):** встановлюється в `1` виключно тоді, коли зсувний регістр `TSR` повністю виштовхнув стоп-біт і лінія повернулася до стану спокою. Скидати `DE` у низький рівень дозволено **тільки після події TC**.

## Час розвороту шини та часові інтервали Modbus RTU

Після завершення передавання останнього біта кадру і вимкнення передавача (`DE = 0`) шині потрібен певний час (зазвичай 1–2 бітових інтервали) для повернення до стану спокою через розрядження паразитної ємності кабелю та згасання залишкових коливань. 

Відповідальний ведений вузол (slave) не повинен починати відповідь миттєво: йому слід витримати захисну паузу (turnaround delay) перед підняттям свого `DE = 1`, щоб уникнути електричного конфлікту з передавачем майстра, який щойно вимикався.

У промисловому стандарті Modbus RTU межі пакетів визначаються виключно часовими інтервалами тиші на шині (без спеціальних стартових чи стопових символів):
* **Інтервал T1.5 (міжсимвольний інтервал):** максимальна допустима пауза між двома послідовними байтами всередині одного кадру. Вона дорівнює 1.5 тривалості символу (16.5 бітових інтервалів для формату 11 біт на символ: 1 старт, 8 даних, 1 паритет, 1 стоп). Якщо пауза між байтами перевищує T1.5, приймач вважає кадр пошкодженим.
* **Інтервал T3.5 (інтервал кінця кадру):** пауза тиші на шині тривалістю не менше 3.5 символів (38.5 бітових інтервалів). Вона позначає завершення попереднього кадру та готовність лінії до нового повідомлення.

Для швидкостей понад 19200 біт/с стандарт фіксує абсолютні значення: `T1.5 = 750 мкс`, а `T3.5 = 1.75 мс`. Драйвер реалізує цей контроль за допомогою апаратного таймера зі скиданням за кожним отриманим байтом (Watchdog кадру).

## Робота з прямим доступом до пам'яті (DMA) та обробка апаратних помилок

При використанні DMA для передавання пакетів RS-485 типова помилка полягає у вимкненні `DE` за перериванням завершення потоку DMA (DMA Transfer Complete, `DMA_TCIF`).

DMA завершує свою роботу в момент, коли **останній байт із пам'яті завантажено в регістр `TDR`**. У цей час передавач UART ще навіть не почав виштовхувати його зсувним регістром. Коректний алгоритм роботи з DMA:

1. Увімкнути передавач (`DE = 1`).
2. Запустити передачу блоку через DMA у регістр даних UART.
3. За перериванням DMA `Transfer Complete` не чіпати пін `DE`, а лише увімкнути переривання UART `TC` (Transmission Complete).
4. У перериванні UART `TC` безпечно скинути `DE = 0` і перевести драйвер у режим очікування відповіді.

Під час приймання драйвер повинен постійно перевіряти біти статусного регістру UART на наявність апаратних помилок:
* **Overrun Error (ORE):** процесор не встиг вичитати попередній байт до приходу нового (вимагає очищення буфера та скидання прапорця читанням регістрів `SR` та `DR`);
* **Framing Error (FE):** на місці стоп-біта виявлено нульовий рівень (ознака колізії або невідповідності швидкості Baud Rate);
* **Noise Error (NE):** внутрішній цифровий фільтр UART зафіксував шум або дрібний викид під час вибірки біта.

## Виявлення колізій через локальне відлуння (Echo Verification)

Якщо вивід дозволу приймача `/RE` жорстко підтягнутий до землі (`/RE = 0`), приймальний каскад трансивера залишається активним навіть під час роботи власного передавача (`DE = 1`). Усі байти, що виходять у лінію `TX`, одночасно повертаються на вхід `RX` мікроконтролера як локальне відлуння.

Порівнюючи кожен відправлений байт із прийнятим ехо-байтом, прошивка отримує миттєвий апаратний контроль лінії:
1. **Колізія (два майстри передають одночасно):** якщо власний передавач виставляє логічну `1`, а інший вузол у той самий момент видає логічний `0`, напруга на шині просідає, і на вході `RX` зчитується `0` замість `1`. Драйвер миттєво фіксує колізію, скидає `DE = 0` і скасовує передачу.
2. **Коротке замикання або обрив лінії:** невідповідність відлуння свідчить про фізичну несправність кабельної траси.

## Реалізація драйвера на C та C++

Нижче наведено модульний драйвер напівдуплексного порту RS-485 із кільцевим буфером, асинхронним обробником переривань та конечним автоматом керування кадрами.

:::tabs
```c
/* rs485_driver.h / rs485_driver.c — Промисловий драйвер RS-485 на C */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RS485_BUF_SIZE 256

typedef enum {
    RS485_STATE_IDLE = 0,
    RS485_STATE_RECEIVING,
    RS485_STATE_TRANSMITTING,
    RS485_STATE_TX_COMPLETE
} rs485_state_t;

typedef struct {
    uint8_t tx_buf[RS485_BUF_SIZE];
    uint8_t rx_buf[RS485_BUF_SIZE];
    volatile size_t tx_head;
    volatile size_t tx_tail;
    volatile size_t rx_count;
    volatile rs485_state_t state;
    volatile bool frame_ready;
    void (*set_de_pin)(bool enable);
    void (*uart_write_byte)(uint8_t data);
    void (*enable_tc_interrupt)(bool enable);
} rs485_port_t;

void rs485_init(rs485_port_t *port,
                void (*set_de)(bool),
                void (*uart_putc)(uint8_t),
                void (*enable_tc_irq)(bool))
{
    port->tx_head = 0;
    port->tx_tail = 0;
    port->rx_count = 0;
    port->state = RS485_STATE_IDLE;
    port->frame_ready = false;
    port->set_de_pin = set_de;
    port->uart_write_byte = uart_putc;
    port->enable_tc_interrupt = enable_tc_irq;

    /* Початковий стан: приймання (DE = 0) */
    port->set_de_pin(false);
}

bool rs485_send_packet(rs485_port_t *port, const uint8_t *data, size_t len)
{
    if (len == 0 || len > RS485_BUF_SIZE || port->state == RS485_STATE_TRANSMITTING) {
        return false;
    }

    for (size_t i = 0; i < len; ++i) {
        port->tx_buf[i] = data[i];
    }
    port->tx_head = len;
    port->tx_tail = 0;
    port->state = RS485_STATE_TRANSMITTING;

    /* 1. Вмикаємо передавач (DE = 1) */
    port->set_de_pin(true);

    /* 2. Відправляємо перший байт у чергу UART */
    uint8_t first_byte = port->tx_buf[port->tx_tail++];
    port->uart_write_byte(first_byte);

    return true;
}

/* Обробник переривання: байт переписано в зсувний регістр (TXE) */
void rs485_isr_txe(rs485_port_t *port)
{
    if (port->state != RS485_STATE_TRANSMITTING) {
        return;
    }

    if (port->tx_tail < port->tx_head) {
        port->uart_write_byte(port->tx_buf[port->tx_tail++]);
    } else {
        /* Усі байти завантажені — вмикаємо очікування повного завершення (TC) */
        port->enable_tc_interrupt(true);
    }
}

/* Обробник переривання: останній біт повністю вийшов у лінію (TC) */
void rs485_isr_tc(rs485_port_t *port)
{
    if (port->state == RS485_STATE_TRANSMITTING) {
        port->enable_tc_interrupt(false);
        /* 3. Безпечно вимикаємо передавач: стоп-біт гарантовано в лінії */
        port->set_de_pin(false);
        port->state = RS485_STATE_IDLE;
    }
}

/* Обробник переривання: отримано байт (RXNE) */
void rs485_isr_rxne(rs485_port_t *port, uint8_t byte)
{
    if (port->state == RS485_STATE_TRANSMITTING) {
        return; /* Ігноруємо відлуння, якщо /RE з'єднано з DE */
    }

    if (port->rx_count < RS485_BUF_SIZE) {
        port->rx_buf[port->rx_count++] = byte;
        port->state = RS485_STATE_RECEIVING;
    }
}

/* Викликається за таймером паузи (3.5 символи для Modbus або міжсимвольний таймаут) */
void rs485_timer_idle_timeout(rs485_port_t *port)
{
    if (port->state == RS485_STATE_RECEIVING && port->rx_count > 0) {
        port->frame_ready = true;
        port->state = RS485_STATE_IDLE;
    }
}
```
```cpp
// RS485Driver.hpp — Ідіоматичний об'єктно-орієнтований драйвер RS-485 на C++20
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <concepts>

enum class DriverState : uint8_t {
    Idle,
    Receiving,
    Transmitting,
    FrameReady
};

template <typename HardwareInterface, size_t BufferCapacity = 256>
class RS485Port {
public:
    explicit RS485Port(HardwareInterface& hw) : hw_{hw} {
        hw_.set_driver_enable(false);
    }

    bool send(std::span<const uint8_t> data) {
        if (data.empty() || data.size() > BufferCapacity || state_ == DriverState::Transmitting) {
            return false;
        }

        for (size_t i = 0; i < data.size(); ++i) {
            tx_buffer_[i] = data[i];
        }
        tx_length_ = data.size();
        tx_index_ = 0;
        state_ = DriverState::Transmitting;

        // Вмикаємо DE перед передачею першого байта
        hw_.set_driver_enable(true);
        hw_.write_byte(tx_buffer_[tx_index_++]);
        return true;
    }

    void on_uart_txe_interrupt() {
        if (state_ != DriverState::Transmitting) return;

        if (tx_index_ < tx_length_) {
            hw_.write_byte(tx_buffer_[tx_index_++]);
        } else {
            hw_.enable_tc_interrupt(true);
        }
    }

    void on_uart_tc_interrupt() {
        if (state_ == DriverState::Transmitting) {
            hw_.enable_tc_interrupt(false);
            // Вимикаємо передавач строго після фізичного завершення стоп-біта
            hw_.set_driver_enable(false);
            state_ = DriverState::Idle;
        }
    }

    void on_uart_rxne_interrupt(uint8_t byte) {
        if (state_ == DriverState::Transmitting) return;

        if (rx_count_ < BufferCapacity) {
            rx_buffer_[rx_count_++] = byte;
            state_ = DriverState::Receiving;
        }
    }

    void on_bus_idle_timeout() {
        if (state_ == DriverState::Receiving && rx_count_ > 0) {
            state_ = DriverState::FrameReady;
        }
    }

    [[nodiscard]] std::optional<std::span<const uint8_t>> get_received_frame() {
        if (state_ != DriverState::FrameReady) {
            return std::nullopt;
        }
        return std::span<const uint8_t>{rx_buffer_.data(), rx_count_};
    }

    void release_rx_buffer() {
        rx_count_ = 0;
        state_ = DriverState::Idle;
    }

    [[nodiscard]] DriverState state() const noexcept { return state_; }

private:
    HardwareInterface& hw_;
    std::array<uint8_t, BufferCapacity> tx_buffer_{};
    std::array<uint8_t, BufferCapacity> rx_buffer_{};
    size_t tx_length_{0};
    size_t tx_index_{0};
    size_t rx_count_{0};
    DriverState state_{DriverState::Idle};
};
```
:::

## Апаратне автокерування виводом DE (Hardware Driver Enable)

Сучасні мікроконтролери (STM32 сімейств G0/G4/F7/H7, Microchip SAM, ESP32) містять апаратну підтримку RS-485 безпосередньо в кремнії модуля UART:
* Вивід `RTS` перемикається в режим `DE` конфігураційним бітом регістра керування (наприклад, `USART_CR3_DEM` в STM32).
* Апаратний таймер модуля затримує підняття `DE` перед початком старт-біта на час `DEAT` (*Driver Enable Assertion Time*) та затримує скидання `DE` після стоп-біта на час `DEDT` (*Driver Enable De-assertion Time*).

Використання апаратного `DE` повністю знімає процесорне навантаження з ядра МК і ліквідує джиттер перемикання лінії у високонавантажених системах.
