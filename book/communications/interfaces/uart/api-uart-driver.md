# 📋 Інтерфейс драйвера UART із перериваннями та буферизацією

Ця довідкова вставка визначає програмний контракт (API) та архітектуру низькорівневого драйвера периферійного модуля UART для мікроконтролерних систем. Драйвер забезпечує неблокувальну прийом-передачу даних у фоновому режимі з використанням переривань hardware та кільцевих буферів (*Ring Buffers*), а також обробляє апаратні прапорці помилок кадру, переповнення та парності.

Робота з послідовним портом через прямо опитування прапорців (*polling*) є прийнятною лише в найпростіших навчальних прикладах. У реальних системах опитування блокує процесор і призводить до втрати байтів при появі інших задач. Створення драйвера на базі переривань дозволяє обробляти вхідний та вихідний потоки у фоновому режимі, зводячи затримку реакції системи до часток мікросекунди.

Нижче наведено специфікацію регістрової карти, програмний інтерфейс функцій, аналіз синхронізації та повну реалізацію драйвера двома мовами (C та ідіоматичною C++).

---

### Регістрова карта та прапорці периферійного модуля

Драйвер взаємодіє з апаратним модулем UART через чотири основні групи регістрів:

1. **Регістри керування (Control Registers - CR1 / CR2 / CR3):**
   - `UE` (*USART Enable*) — вмикання живлення та тактування модуля.
   - `TE` (*Transmitter Enable*) — вмикання передавального тракту.
   - `RE` (*Receiver Enable*) — вмикання приймального тракту.
   - `RXNEIE` (*RX Not Empty Interrupt Enable*) — дозволяє апаратному модулю генерувати векторне переривання процесора при кожному прибутті нового байта.
   - `TXEIE` (*TX Empty Interrupt Enable*) — дозволяє переривання при звільненні буфера передавача TDR.
   - `TCIE` (*Transmission Complete Interrupt Enable*) — дозволяє переривання при повному виході стоп-біта із зсувного регістра TSR.
   - `RTSE` / `CTSE` — вмикання апаратного керування потоком (RTS/CTS).

2. **Регістр стану та прапорців (Status Register - SR / ISR):**
   - `RXNE` (*Read Data Register Not Empty*) — прапорець прибуття нового байта в приймальний буфер.
   - `TXE` (*Transmit Data Register Empty*) — прапорець готовності прийняти наступний байт у передавач.
   - `TC` (*Transmission Complete*) — прапорець завершення передачі останнього біта з зсувного регістра.
   - `OE` (*Overrun Error*) — прапорець втрати байта через нечитання RBR.
   - `FE` (*Framing Error*) — помилка старт/стоп бітів (шум або невірний baud).
   - `PE` (*Parity Error*) — незбіг контрольного біта парності.
   - `NE` (*Noise Error Flag*) — виявлення завад під час мажоритарної вибірки.

3. **Регістри даних (Data Registers - TDR / RDR або DR):**
   - Запис у `TDR` завантажує байт у передавальний буфер.
   - Читання з `RDR` вилучає байт із приймального буфера та автоматично скидає прапорець `RXNE`.

---

### Специфікація функцій драйвера (API Contract)

Повний контракт драйвера визначає такі обов'язкові операції:

```
Операція           │ Призначення                                │ Тип виконання
───────────────────┼────────────────────────────────────────────┼────────────────────────
uart_init()        │ Ініціалізація baud, формат кадру, IRQ      │ Блокувальний
uart_write_byte()  │ Помістити байт у TX-буфер та увімкнути IRQ │ Неблокувальний
uart_write_bytes() │ Помістити масив байтів у TX-буфер          │ Неблокувальний
uart_read_byte()   │ Зчитати один байт із RX-буфера             │ Неблокувальний
uart_bytes_available() │ Отримати кількість байтів у RX-буфері    │ Миттєвий (Atomic)
uart_flush_tx()    │ Чекати повного виходу даних із зсувного регістра │ Блокувальний (за вимогою)
uart_get_errors()  │ Отримати маску апаратних помилок (OE/FE/PE) │ Миттєвий
```

---

### Життєвий цикл та машини станів драйвера

Програмний драйвер UART працює як скінченний автомат із трьома основними фазами життєвого циклу:

1. **Фаза ініціалізації (`UNINITIALIZED -> IDLE`):**
   - Подача тактування на периферійне ядро в блоці RCC.
   - Конфігурація виводів `GPIO` у режим альтернативної функції (*Alternate Function*).
   - Обчислення та запис значення дільника `BRR`.
   - Скидання індексів кільцевих буферів `head` та `tail` у нуль.
   - Налаштування пріоритету векторного переривання у контролері NVIC.
   - Вмикання бітів `UE`, `TE`, `RE` та дозволу переривання `RXNEIE`.

2. **Фаза передачі даних (`IDLE -> TRANSMITTING -> IDLE`):**
   - Головна програма викликає `uart_send_byte()`, який кладе байт у кільцевий буфер `tx_ring` і піднімає біт дозволу переривання `TXEIE`.
   - Щойно передавач стає вільним, апаратна частина викликує ISR.
   - Обробник переривання витягує байт із `tx_ring` і записує його в `TDR`.
   - Коли буфер `tx_ring` спорожніє, ISR автоматично вимикає біт `TXEIE`, повертаючи драйвер у стан `IDLE`.

3. **Фаза приймання даних (`BACKGROUND ISR`):**
   - При появі старт-біта на ліній RX апаратна частина збирає байт у зсувному регістрі RSR.
   - При виникненні прапорця `RXNE` негайно генерується переривання ISR.
   - ISR зчитує байт із `RDR` і записує його в буфер `rx_ring`, оновлюючи індекс `head`.
   - Якщо буфер `rx_ring` досяг порогу заповнення, драйвер піднімає апаратний сигнал `RTS`, сповіщаючи передавача про необхідність паузи.

---

### Архітектура кільцевих буферів та атомність

Для узгодження асинхронних швидкостей надходження даних від обробника переривань (ISR) та головного циклу програми драйвер використовує **кільцеві буфери** (*Ring Buffers*).

Кожен буфер містить масив фіксованого розміру `N` (типово 64 або 128 байтів, що є ступенем двійки) та два вказівники/індекси:
- `head` — індекс місця, куди буде записано наступний байт.
- `tail` — індекс місця, звідки буде зчитано наступний байт.

```
Схема кільцевого буфера RX:

    Індекси:   0     1     2     3     4     5     6     7
            ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
            │ 'H' │ 'e' │ 'l' │ 'l' │ 'o' │     │     │     │
            └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
               ▲                         ▲
               │                         │
             tail (звідси читає CPU)   head (сюди пише ISR)
```

**Правила некопліктної синхронізації без блокування переривань:**
1. **Буфер прийому (RX):** Обробник переривань (ISR) модифікує **тільки** індекс `head`. Головна програма модифікує **тільки** індекс `tail`.
2. **Буфер передачі (TX):** Головна програма модифікує **тільки** індекс `head`. Обробник переривань (ISR) модифікує **тільки** індекс `tail`.

Завдяки такій роздільності індексів драйвер не вимагає критичних секцій із вимкненням переривань при читанні чи запису поодиноких байтів, якщо читання індексів є атомарною 16-бітовою або 32-бітовою операцією.

#### Бар'єри пам'яті та компіляторна оптимізація
При роботі з ядрами ARM Cortex-M3/M4/M7 компілятор C/C++ або конвеєр процесора з позачерговим виконанням (*Out-of-Order Execution*) може переупорядкувати записи у пам'ять. Наприклад, індекс `head` може оновитися до того, як байт реально записався в масив `buffer`.

Щоб запобігти цьому, застосовують ключове слово `volatile` для індексів та бар'єри пам'яті:
- Вказівники індексів оголошуються як `volatile uint16_t head;`.
- У відповідальних точках перед оновленням `head` додають компіляторний або апаратний бар'єр пам'яті `__DMB()` (*Data Memory Barrier*).

#### Політика обробки переповнення буфера
Якщо головна програма тривалий час не зчитує дані з `rx_ring`, індекс `head` доганяє `tail`. У цьому разі драйвер може застосовувати одну з двох стратегій:
- **Discard New (Відкидати нові):** Якщо буфер повний, нові прибулі байти відкидаються, а лічильник `buffer_overflow_count` збільшується. Це запобігає спотворенню вже накопичених даних.
- **Overwrite Oldest (Перезаписувати найстаріші):** Індекс `tail` примусово зсувається вперед, звільняючи місце для нового байта. Це корисно для телеметрії, де найновіші дані важливіші за застарілі.

---

### Стратегії підключення контролера DMA (Direct Memory Access)

У високопродуктивних застосунках (наприклад, прийомі аудіопотоку або супутникових даних GNSS на швидкості 921600 біт/с) використання переривань на кожен байт генерує до 92 000 переривань на секунду. Це відбирає до 15-20% обчислювальної потужності ЦП лише на пролог і епілог обробника переривань.

Для розвантаження процесора застосовують **підключення контролера DMA**:

1. **Circular DMA RX з підтримкою переривання лінії в спокої (IDLE Line Interrupt):**
   - Контролер DMA налаштовується в циклічний режим (*Circular Mode*), заповнюючи буфер у пам'яті RAM повністю без участі процесора.
   - Модуль UART налаштовують на генерування переривання `IDLEIE` (*IDLE Line Detected Interrupt*).
   - Коли передавальна сторона завершує надсилання пачки даних і лінія RX повертається в спокій (1) на тривалість більше одного кадру, UART піднімає прапорець `IDLE`.
   - Обробник переривання `IDLE_ISR` зчитує лічильник залишку DMA (`NDTR`), обчислює кількість реально прийнятих байтів і сповіщає задачу верхнього рівня про прибуття нового кадру.

2. **Double-Buffered DMA TX:**
   - Для передачі масивів даних драйвер використовує два покажчики на RAM-буфери (`Ping-Pong Buffers`).
   - Поки DMA виштовхує перший буфер у лінію `TX`, процесор готує дані у другому буфері. При закінченні передачі DMA викликує переривання `TC` (*Transfer Complete*) і перемикається на другий буфер без паузи в лінії.

---

### Обробка апаратних помилок та відновлення каналу

Під час роботи послідовного порту в реальних умовах можуть виникати апаратні збої:
- **Переповнення (Overrun Error):** Якщо RX FIFO заповнений, а новий байт надходить із лінії, модуль виставляє прапорець `OE`. Більшість апаратних модулів UART припиняють прийом нових байтів доти, доки програма явним чином не скине прапорець `OE` (шляхом послідовного читання регістрів `SR` та `DR` або записом у регістр `ICR`).
- **Помилка кадру (Framing Error):** Виникає при розриві лінії або хибній швидкості baud. Драйвер повинен прочитати спотворений байт із `DR`, щоб очистити апаратний буфер, але відкинути його й не поміщати в кільцевий буфер `rx_ring`.
- **Помилка парності (Parity Error):** Виникає під час виявлення поодинокої збійної бітової позиції у кадрі. Драйвер фіксує лічильник `parity_errors`, але може передавати байт вищому рівню (наприклад, для інспекції).

---

### Інтеграція з операційними системами реального часу (RTOS)

У середовищі операційних систем реального часу (FreeRTOS, Zephyr, RT-Thread) драйвер UART виступає джерелом подій для задач вищого рівня:

1. **Сповіщення задач із ISR (`Task Notifications`):** При прибутті термінального символу (наприклад, `\n` або `\r`) обробник переривання викликує `vTaskNotifyGiveFromISR()`, пробуджуючи задачу обробки команд без затримок.
2. **Передача через семафори та черги:** Запис у буфер `tx_ring` блокує викликаючий потік через бінарний семафор `xSemaphoreTake()`, якщо буфер передачі повний, і розблоковує його, коли ISR виштовхне половину байтів у лінію.

---

### Показники продуктивності та накладних витрат

Нижче наведено порівняльний аналіз трьох основних підходів до написання драйвера UART з погляду навантаження на процесор та затримок:

```
Режим роботи драйвера │ Завантаження ЦП (на 115200) │ Максимальна затримка │ Складність коду
──────────────────────┼─────────────────────────────┼──────────────────────┼─────────────────
Пряме опитування (Poll)│ 100% (Блокуючий цикл)       │ 0 мкс (миттєве)      │ Мінімальна
Переривання + RingBuf │ 2% .. 5% (За байт ISR)      │ < 5 мкс (контекст)   │ Середня
DMA Circular Stream   │ < 0.1% (За блок даних)      │ 0 мкс (hardware RAM) │ Висока
```

Для більшості задач керування та обміну даними між мікроконтролерами саме драйвер на базе переривань із кільцевим буфером забезпечує ідеальний баланс між простотою реалізації та низьким навантаженням на системні ресурси.

---

### Програмна реалізація драйвера

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define UART_RING_BUFFER_SIZE 128U

/* Структура кільцевого буфера */
typedef struct {
    uint8_t buffer[UART_RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} uart_ring_buffer_t;

/* Коди помилок драйвера */
typedef enum {
    UART_ERR_NONE = 0x00,
    UART_ERR_OVERRUN = 0x01,
    UART_ERR_FRAMING = 0x02,
    UART_ERR_PARITY = 0x04,
    UART_ERR_BUFFER_FULL = 0x08
} uart_error_flags_t;

/* Структура стану екземпляра UART */
typedef struct {
    void *hardware_base;                 /* Базова адреса регістрів */
    uart_ring_buffer_t rx_ring;          /* Буфер приймача */
    uart_ring_buffer_t tx_ring;          /* Буфер передавача */
    volatile uint32_t error_counters;    /* Лічильник помилок */
    bool hw_flow_control;                /* Прапор RTS/CTS */
} uart_driver_t;

/* API Функції */
void uart_driver_init(uart_driver_t *dev, void *hw_base, uint32_t baud_rate, bool use_flow_control);
bool uart_send_byte(uart_driver_t *dev, uint8_t byte);
size_t uart_send_buffer(uart_driver_t *dev, const uint8_t *data, size_t length);
bool uart_receive_byte(uart_driver_t *dev, uint8_t *out_byte);
size_t uart_rx_available(const uart_driver_t *dev);
void uart_isr_handler(uart_driver_t *dev);

/* Внутрішні допоміжні функції буфера */
static inline bool ring_push(uart_ring_buffer_t *ring, uint8_t byte) {
    uint16_t next_head = (ring->head + 1U) % UART_RING_BUFFER_SIZE;
    if (next_head == ring->tail) {
        return false; /* Буфер повний */
    }
    ring->buffer[ring->head] = byte;
    ring->head = next_head;
    return true;
}

static inline bool ring_pop(uart_ring_buffer_t *ring, uint8_t *out_byte) {
    if (ring->head == ring->tail) {
        return false; /* Буфер порожній */
    }
    *out_byte = ring->buffer[ring->tail];
    ring->tail = (ring->tail + 1U) % UART_RING_BUFFER_SIZE;
    return true;
}

/* Реалізація обробника переривань (ISR) */
void uart_isr_handler(uart_driver_t *dev) {
    /* Псевдокод доступу до регістрів конкретного HW */
    volatile uint32_t *sr = (volatile uint32_t *)(dev->hardware_base);
    volatile uint32_t *dr = (volatile uint32_t *)(dev->hardware_base + 0x04);
    volatile uint32_t *cr1 = (volatile uint32_t *)(dev->hardware_base + 0x0C);

    uint32_t status = *sr;

    /* 1. Обробка приймання RXNE */
    if ((status & (1U << 5U)) != 0U) { /* RXNE bit */
        uint8_t received_byte = (uint8_t)(*dr);
        if (!ring_push(&dev->rx_ring, received_byte)) {
            dev->error_counters |= UART_ERR_BUFFER_FULL;
        }
    }

    /* 2. Обробка помилок кадру/переповнення */
    if ((status & (1U << 3U)) != 0U) { dev->error_counters |= UART_ERR_OVERRUN; }
    if ((status & (1U << 1U)) != 0U) { dev->error_counters |= UART_ERR_FRAMING; }
    if ((status & (1U << 0U)) != 0U) { dev->error_counters |= UART_ERR_PARITY; }

    /* 3. Обробка передачі TXE */
    if ((status & (1U << 7U)) != 0U && (*cr1 & (1U << 7U)) != 0U) { /* TXEIE bit */
        uint8_t byte_to_send;
        if (ring_pop(&dev->tx_ring, &byte_to_send)) {
            *dr = byte_to_send;
        } else {
            /* Буфер передачі порожній — вимикаємо переривання TXEIE */
            *cr1 &= ~(1U << 7U);
        }
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

class UartPeripheral {
public:
    static constexpr size_t BufferSize = 128;

    enum class Error : uint8_t {
        BufferOverflow,
        HardwareOverrun,
        FramingError,
        ParityError,
        TxBufferFull
    };

    explicit UartPeripheral(uintptr_t base_address) noexcept
        : hw_base_(reinterpret_cast<volatile uint32_t*>(base_address)) {}

    ~UartPeripheral() noexcept = default;

    // Заборона копіювання (RAII керування апаратним ресурсом)
    UartPeripheral(const UartPeripheral&) = delete;
    UartPeripheral& operator=(const UartPeripheral&) = delete;
    UartPeripheral(UartPeripheral&&) noexcept = default;
    UartPeripheral& operator=(UartPeripheral&&) noexcept = default;

    void init(uint32_t baud_rate, bool enable_rts_cts) noexcept {
        // Конфігурація апаратного модуля
        hw_base_[3] = 0; // CR1 reset
        // Налаштування baud і прапорців...
        hw_base_[3] |= (1U << 13) | (1U << 2) | (1U << 3) | (1U << 5); // UE, RE, TE, RXNEIE
    }

    [[nodiscard]] std::expected<void, Error> send(uint8_t byte) noexcept {
        const size_t next_head = (tx_head_ + 1) % BufferSize;
        if (next_head == tx_tail_) {
            return std::unexpected(Error::TxBufferFull);
        }
        tx_buffer_[tx_head_] = byte;
        tx_head_ = next_head;

        // Увімкнути переривання TXEIE
        hw_base_[3] |= (1U << 7);
        return {};
    }

    [[nodiscard]] size_t send(std::span<const uint8_t> data) noexcept {
        size_t written = 0;
        for (uint8_t b : data) {
            if (!send(b).has_value()) {
                break;
            }
            ++written;
        }
        return written;
    }

    [[nodiscard]] std::expected<uint8_t, Error> receive() noexcept {
        if (rx_head_ == rx_tail_) {
            return std::unexpected(Error::BufferOverflow); // Або NoData
        }
        uint8_t byte = rx_buffer_[rx_tail_];
        rx_tail_ = (rx_tail_ + 1) % BufferSize;
        return byte;
    }

    [[nodiscard]] size_t available() const noexcept {
        if (rx_head_ >= rx_tail_) {
            return rx_head_ - rx_tail_;
        }
        return BufferSize - (rx_tail_ - rx_head_);
    }

    // Обробник переривання (викликується з векторного столу IRQ)
    void handle_interrupt() noexcept {
        const uint32_t sr = hw_base_[0]; // SR
        const uint32_t cr1 = hw_base_[3]; // CR1

        // Читання RXNE
        if (sr & (1U << 5)) {
            const uint8_t byte = static_cast<uint8_t>(hw_base_[1]); // DR
            const size_t next_head = (rx_head_ + 1) % BufferSize;
            if (next_head != rx_tail_) {
                rx_buffer_[rx_head_] = byte;
                rx_head_ = next_head;
            } else {
                last_error_ = Error::BufferOverflow;
            }
        }

        // Запис TXE
        if ((sr & (1U << 7)) && (cr1 & (1U << 7))) {
            if (tx_head_ != tx_tail_) {
                hw_base_[1] = tx_buffer_[tx_tail_];
                tx_tail_ = (tx_tail_ + 1) % BufferSize;
            } else {
                hw_base_[3] &= ~(1U << 7); // Вимкнути TXEIE
            }
        }
    }

private:
    volatile uint32_t* hw_base_;
    std::array<uint8_t, BufferSize> rx_buffer_{};
    std::array<uint8_t, BufferSize> tx_buffer_{};
    volatile size_t rx_head_{0};
    volatile size_t rx_tail_{0};
    volatile size_t tx_head_{0};
    volatile size_t tx_tail_{0};
    Error last_error_{Error::BufferOverflow};
};
```
:::
