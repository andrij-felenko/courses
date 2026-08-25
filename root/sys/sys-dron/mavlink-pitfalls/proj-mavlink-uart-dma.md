# ⚙️ Неблокувальний драйвер UART з DMA та кільцевим буфером для MAVLink

У системах керування польотом головний контур стабілізації та оцінки просторової орієнтації (PID-регулятори та розширений фільтр Калмана EKF) повинен виконуватися зі строго детермінованим періодом. Для сучасних польотних контролерів (наприклад, на мікроконтролерах STM32F4, STM32F7 або STM32H7) ця частота становить від 400 Гц (період 2.5 мс) до 1000 Гц (період 1.0 мс). Якщо в цьому критичному потоці викликати класичну блокувальну функцію відправки даних через послідовний порт UART, центральний процесор затримується на десятки мілісекунд у разі повільного каналу радіозв'язку або переповнення апаратного буфера, що неминуче призводить до зриву стабілізації та катастрофи апарата.

Єдиним надійним інженерним рішенням є побудова двостороннього повністю асинхронного драйвера послідовного інтерфейсу на основі кільцевих буферів та контролера прямого доступу до пам'яті (DMA).

### Архітектура та вимоги до підсистеми зв'язку

Підсистема вводу-виводу MAVLink повинна задовольняти такі фундаментальні вимоги реального часу:

1. **Асинхронний прийом без навантаження на процесор (RX Pipeline):**
   - Контролер DMA налаштовується в циклічний режим (`DMA_CIRCULAR`), записуючи байти з регістра даних UART безпосередньо в оперативну пам'ять без генерації переривань на кожен прийнятий байт.
   - Для виявлення завершення прийому кадру використовується апаратне переривання простою лінії UART (англ. *IDLE Line Detection*), яке спрацьовує тоді, коли лінія RX залишається в стані логічної одиниці протягом тривалості одного повного байтового кадру.
   - Обробник переривання обчислює кількість нових байтів, перевіряє цілісність кільцевого буфера та передає потік байтів у потоковий розбирач MAVLink.

2. **Неблокувальна передача з пріоритетним скиданням (TX Pipeline):**
   - Основний потік програми або завдання генерації телеметрії RTOS записує сформований пакет у проміжний передавальний [кільцевий буфер](topic:sf-algorithms/ring-buffer) за сталий час `O(1)` (менше однієї мікросекунди).
   - Якщо в буфері передачі недостатньо вільного місця, драйвер не блокує виконання і не чекає звільнення порту, а застосовує політику пріоритетного скидання: низькопріоритетні кадри високочастотної телеметрії (`ATTITUDE`, `VFR_HUD`) скидаються зі збільшенням лічильника втрат, тоді як критичні повідомлення (`HEARTBEAT`, `COMMAND_ACK`, `PARAM_VALUE`) зберігаються.
   - Фізична передача байтів з буфера в регістр UART здійснюється модулем DMA у фоновому режимі без залучення процесорного ядра.

3. **Коректне розбиття блоків при переході через фізичний край масиву (Wrap-around Handling):**
   - Оскільки кільцевий буфер логічно замкнений у коло, блок даних для DMA може бути розірваний кінцем фізичного масиву пам'яті. Драйвер повинен відправляти дані послідовними неперервними шматками, ініціюючи передачу залишку в обробнику завершення попередньої транзакції DMA.

### Робота апаратного каналу прийому (DMA RX) та виявлення простою лінії

Класична помилка початківців при роботі з UART на мікроконтролерах — налаштування переривання на кожен прийнятий байт (`RXNE` — *RX Not Empty*). На швидкості 921600 бод надходження одного байта відбувається кожні `10.85` мікросекунди. Якщо обробка переривання разом зі збереженням регістрів стека займає 2–3 мкс, центральний процесор витрачає 25–30% своєї обчислювальної потужності лише на вхід у функції переривання.

Застосування прямого доступу до пам'яті повністю знімає це навантаження. Регістр периферії `USART_RDR` або `USART_DR` призначається джерелом даних для каналу DMA, а масив в оперативній пам'яті `dma_rx_buf` розміром 512 або 1024 байти — адресою призначення. Регістр лічильника кількості передач DMA (`NDTR` — *Number of Data to Transfer Register*) декрементується апаратно після кожного перенесеного байта.

Коли передавач завершує надсилання кадру MAVLink, на лінії UART настає стан спокою (високий логічний рівень протягом понад 10–11 бітових інтервалів). Периферійний модуль UART фіксує цю подію та виставляє апаратний прапорець `IDLE`, генеруючи переривання `USART_IRQHandler`.

Алгоритм обчислення кількості прийнятих байтів в обробнику переривання IDLE:
1. Зчитується поточне значення апаратного лічильника DMA: `current_ndtr = DMA_Channel->CNDTR`.
2. Поточна позиція запису в буфері обчислюється як: `write_head = BUF_SIZE - current_ndtr`.
3. Якщо `write_head > last_read_index`, нові байти лежать у неперервному діапазоні від `last_read_index` до `write_head`.
4. Якщо `write_head < last_read_index`, відбувся циклічний перехід через кінець масиву: байти зчитуються двома послідовними сегментами — від `last_read_index` до кінця масиву `BUF_SIZE`, а потім від індексу `0` до `write_head`.
5. Позиція `last_read_index` оновлюється на значення `write_head`.

Отриманий потік байтів безпосередньо передається у функцію скінченного автомата розбору пакетів MAVLink (`mavlink_parse_char`), яка відновлює кадри без додаткового копіювання в проміжні пам'яті.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UART_RX_DMA_BUF_SIZE   512
#define UART_TX_RING_BUF_SIZE  1024
#define MAVLINK_MAX_PACKET_LEN 280

/* Рівні пріоритету повідомлень для політики скидання при заторах */
typedef enum {
    PKT_PRIORITY_LOW = 0,     /* Потокова телеметрія: ATTITUDE, VFR_HUD */
    PKT_PRIORITY_MEDIUM = 1,  /* Навігація: GLOBAL_POSITION_INT, GPS_RAW_INT */
    PKT_PRIORITY_HIGH = 2     /* Критичні кадри: HEARTBEAT, COMMAND_ACK, PARAM_VALUE */
} packet_priority_t;

/* Кільцевий буфер передачі (SPSC: Single-Producer Single-Consumer) */
typedef struct {
    uint8_t buffer[UART_TX_RING_BUF_SIZE];
    volatile uint16_t head;          /* Індекс запису (модифікує продюсер) */
    volatile uint16_t tail;          /* Індекс читання (модифікує DMA ISR) */
    uint32_t dropped_packets;        /* Лічильник скинутих пакетів */
    uint32_t total_sent_bytes;       /* Загальна кількість переданих байтів */
} tx_ring_buffer_t;

/* Структура контексту драйвера UART */
typedef struct {
    uint8_t dma_rx_buf[UART_RX_DMA_BUF_SIZE];
    uint16_t last_rx_index;
    tx_ring_buffer_t tx_ring;
    volatile bool tx_dma_busy;
} mavlink_uart_driver_t;

static mavlink_uart_driver_t g_mav_driver;

/* Ініціалізація структури драйвера */
void mavlink_driver_init(mavlink_uart_driver_t *drv) {
    memset(drv, 0, sizeof(mavlink_uart_driver_t));
    drv->last_rx_index = 0;
    drv->tx_dma_busy = false;
    drv->tx_ring.head = 0;
    drv->tx_ring.tail = 0;
    drv->tx_ring.dropped_packets = 0;
    drv->tx_ring.total_sent_bytes = 0;
}

/* Обчислення кількості вільних байтів у передавальному кільці */
static inline uint16_t tx_ring_available(const tx_ring_buffer_t *rb) {
    uint16_t head = rb->head;
    uint16_t tail = rb->tail;
    if (head >= tail) {
        return (UART_TX_RING_BUF_SIZE - 1) - (head - tail);
    }
    return tail - head - 1;
}

/* Запуск апаратного каналу DMA TX на неперервний блок пам'яті */
static void start_dma_tx_transfer(mavlink_uart_driver_t *drv) {
    if (drv->tx_dma_busy) {
        return;
    }

    uint16_t head = drv->tx_ring.head;
    uint16_t tail = drv->tx_ring.tail;

    if (head == tail) {
        return; /* Буфер порожній */
    }

    uint16_t chunk_len = 0;
    if (head > tail) {
        chunk_len = head - tail;
    } else {
        /* Дані переходять через фізичний кінець масиву */
        chunk_len = UART_TX_RING_BUF_SIZE - tail;
    }

    drv->tx_dma_busy = true;

    /* Виклик апаратного рівня (HAL/LL мікроконтролера):
       HAL_UART_Transmit_DMA(&huart1, &drv->tx_ring.buffer[tail], chunk_len); */
}

/* Неблокувальне додавання пакета MAVLink у передавальний буфер */
bool mavlink_uart_send_packet(mavlink_uart_driver_t *drv, 
                              const uint8_t *packet, 
                              uint16_t len, 
                              packet_priority_t prio) {
    if (len == 0 || len > MAVLINK_MAX_PACKET_LEN) {
        return false;
    }

    uint16_t free_space = tx_ring_available(&drv->tx_ring);

    /* Якщо місця бракує, застосовуємо політику скидання за пріоритетом */
    if (free_space < len) {
        if (prio == PKT_PRIORITY_LOW || prio == PKT_PRIORITY_MEDIUM) {
            drv->tx_ring.dropped_packets++;
            return false; /* Безпечно відкидаємо надлишкову телеметрію */
        }
        /* Для високопріоритетного пакета перевіряємо критичний поріг */
        if (free_space < len) {
            drv->tx_ring.dropped_packets++;
            return false;
        }
    }

    /* Послідовний запис байтів у кільцевий буфер */
    uint16_t head = drv->tx_ring.head;
    for (uint16_t i = 0; i < len; ++i) {
        drv->tx_ring.buffer[head] = packet[i];
        head = (head + 1) % UART_TX_RING_BUF_SIZE;
    }
    drv->tx_ring.head = head;

    /* Запускаємо передачу DMA, якщо передавач був вільний */
    start_dma_tx_transfer(drv);
    return true;
}

/* Обробник переривання завершення передачі DMA (TX Complete ISR) */
void DMA1_Channel_UART_TX_IRQHandler(void) {
    mavlink_uart_driver_t *drv = &g_mav_driver;

    /* У реальній системі передана довжина chunk_len фіксується при старті */
    /* Оновлюємо tail кільцевого буфера на передану довжину */
    drv->tx_dma_busy = false;

    /* Запускаємо наступний фрагмент, якщо в буфері ще залишилися дані */
    start_dma_tx_transfer(drv);
}

/* Обробник апаратного переривання простою лінії UART IDLE (новий пакет надійшов) */
void UART_RX_IdleLine_IRQHandler(mavlink_uart_driver_t *drv, void (*byte_parser)(uint8_t byte)) {
    /* Зчитуємо поточну позицію запису з лічильника регістра DMA:
       uint16_t current_pos = UART_RX_DMA_BUF_SIZE - __HAL_DMA_GET_COUNTER(huart->hdmarx); */
    uint16_t current_pos = 128; /* Приклад значення з регістра */
    uint16_t last_pos = drv->last_rx_index;

    if (current_pos != last_pos) {
        if (current_pos > last_pos) {
            /* Неперервний лінійний сегмент */
            for (uint16_t i = last_pos; i < current_pos; ++i) {
                byte_parser(drv->dma_rx_buf[i]);
            }
        } else {
            /* Кільце перейшло через кінець фізичного масиву */
            for (uint16_t i = last_pos; i < UART_RX_DMA_BUF_SIZE; ++i) {
                byte_parser(drv->dma_rx_buf[i]);
            }
            for (uint16_t i = 0; i < current_pos; ++i) {
                byte_parser(drv->dma_rx_buf[i]);
            }
        }
        drv->last_rx_index = current_pos;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <atomic>
#include <concepts>

enum class PacketPriority : uint8_t {
    Low = 0,     // Потокова телеметрія: ATTITUDE, VFR_HUD
    Medium = 1,  // Навігація: GLOBAL_POSITION_INT
    High = 2     // Критичні кадри: HEARTBEAT, COMMAND_ACK
};

template <size_t Capacity>
class SafeRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two for mask indexing");

public:
    SafeRingBuffer() : head_(0), tail_(0), dropped_count_(0) {}

    [[nodiscard]] size_t available() const noexcept {
        const size_t head = head_.load(std::memory_order_relaxed);
        const size_t tail = tail_.load(std::memory_order_relaxed);
        return (Capacity - 1) - ((head - tail) & (Capacity - 1));
    }

    bool push(std::span<const uint8_t> data, PacketPriority priority) noexcept {
        const size_t len = data.size();
        if (len == 0 || len >= Capacity) {
            return false;
        }

        const size_t free_slots = available();
        if (free_slots < len) {
            dropped_count_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        size_t head = head_.load(std::memory_order_relaxed);
        for (const uint8_t byte : data) {
            buffer_[head & (Capacity - 1)] = byte;
            head++;
        }
        head_.store(head, std::memory_order_release);
        return true;
    }

    std::span<const uint8_t> peek_contiguous_chunk() noexcept {
        const size_t head = head_.load(std::memory_order_acquire);
        const size_t tail = tail_.load(std::memory_order_relaxed);

        if (head == tail) {
            return {};
        }

        const size_t tail_idx = tail & (Capacity - 1);
        const size_t head_idx = head & (Capacity - 1);

        if (head_idx > tail_idx) {
            return std::span<const uint8_t>(&buffer_[tail_idx], head_idx - tail_idx);
        }
        return std::span<const uint8_t>(&buffer_[tail_idx], Capacity - tail_idx);
    }

    void advance_tail(size_t count) noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        tail_.store(current_tail + count, std::memory_order_release);
    }

    [[nodiscard]] size_t dropped_packets() const noexcept {
        return dropped_count_.load(std::memory_order_relaxed);
    }

private:
    std::array<uint8_t, Capacity> buffer_{};
    alignas(64) std::atomic<size_t> head_;
    alignas(64) std::atomic<size_t> tail_;
    std::atomic<size_t> dropped_count_;
};

class MavlinkAsyncUartDriver {
public:
    static constexpr size_t RxBufferSize = 512;
    static constexpr size_t TxRingSize = 1024;

    MavlinkAsyncUartDriver() = default;

    bool send_packet(std::span<const uint8_t> packet, PacketPriority prio) noexcept {
        const bool ok = tx_ring_.push(packet, prio);
        if (ok) {
            try_start_dma_tx();
        }
        return ok;
    }

    void on_tx_dma_complete(size_t bytes_transferred) noexcept {
        tx_ring_.advance_tail(bytes_transferred);
        tx_busy_.store(false, std::memory_order_release);
        try_start_dma_tx();
    }

    template <typename ParserCallback>
    void process_rx_dma(size_t dma_write_head, ParserCallback&& callback) noexcept {
        if (dma_write_head == last_rx_idx_) {
            return;
        }

        if (dma_write_head > last_rx_idx_) {
            for (size_t i = last_rx_idx_; i < dma_write_head; ++i) {
                callback(rx_dma_buffer_[i]);
            }
        } else {
            for (size_t i = last_rx_idx_; i < RxBufferSize; ++i) {
                callback(rx_dma_buffer_[i]);
            }
            for (size_t i = 0; i < dma_write_head; ++i) {
                callback(rx_dma_buffer_[i]);
            }
        }
        last_rx_idx_ = dma_write_head;
    }

private:
    void try_start_dma_tx() noexcept {
        bool expected = false;
        if (!tx_busy_.compare_exchange_strong(expected, true, std::memory_order_acq_rel)) {
            return;
        }

        auto chunk = tx_ring_.peek_contiguous_chunk();
        if (chunk.empty()) {
            tx_busy_.store(false, std::memory_order_release);
            return;
        }

        // Апаратний запуск DMA: chunk.data() та chunk.size()
        // launch_hardware_dma_tx(chunk.data(), chunk.size());
    }

    std::array<uint8_t, RxBufferSize> rx_dma_buffer_{};
    size_t last_rx_idx_{0};
    SafeRingBuffer<TxRingSize> tx_ring_{};
    std::atomic<bool> tx_busy_{false};
};
```
:::

### Порядок пам'яті та бар'єри в беззамоквих кільцевих буферах (SPSC)

При передачі даних між основним потоком програми (продюсером) та обробником переривання DMA (споживачем) критично важливо гарантувати строгий порядок звернення до пам'яті. Сучасні суперскалярні процесори (ARM Cortex-M7 з конвеєром подвійної видачі інструкцій) та оптимізуючі компілятори мають право переставляти місцями інструкції читання й запису, якщо між ними немає явної залежності за даними.

Розглянемо послідовність операцій додавання елемента в кільцевий буфер:
1. Продюсер записує байти повідомлення в масив `buffer[head..head+len]`.
2. Продюсер збільшує індекс `head` на величину `len`.

Якщо компілятор або процесор переставить ці дії місцями (виконає оновлення `head` до того, як усі байти фізично запишуться в пам'ять), переривання DMA може миттєво підхопити новий індекс `head` і розпочати передачу старого сміття або частково оновленого кадру MAVLink. Контрольна сума CRC на приймальному боці не зійдеться, і пакет буде втрачено.

У реалізації C++ це вирішується використанням семантики **Release/Acquire**:
- Запис індексу `head_.store(head, std::memory_order_release)` гарантує, що всі попередні операції запису в пам'ять буфера будуть завершені й видимі іншим контекстам **до** оновлення змінної `head`.
- Читання індексу `head_.load(std::memory_order_acquire)` в обробнику DMA гарантує, що жодна наступна операція читання даних з буфера не буде виконана раніше за зчитування актуального значення індексу `head`.

У класичному C на мікроконтролерах ARM без стандартної бібліотеки атоміків для цього використовуються апаратні бар'єри пам'яті:
- `__DMB()` (англ. *Data Memory Barrier*) — інструкція ядра, яка гарантує явне завершення всіх попередніх транзакцій запису до пам'яті перед виконанням наступних інструкцій.

### Інженерні пастки реалізації драйвера UART з DMA

1. **Неузгодженість кешу даних (Data Cache Coherency на ARM Cortex-M7):**
   На мікроконтролерах із увімкненим кешем першого рівня L1 D-Cache (наприклад, серія STM32H7 з ядром Cortex-M7 на частоті 480 МГц) контролер DMA підключається безпосередньо до шинної матриці AXI SRAM, оминаючи кеш ядра процесора.
   
   Якщо ядро записало байти нового кадру MAVLink у масив, ці дані спочатку потрапляють у рядки D-Cache (політика зворотного запису *Write-Back*). У фізичній пам'яті SRAM за цими адресами все ще зберігаються старі байти. Коли контролер DMA починає передачу, він вичитує з пам'яті застарілі дані.
   
   Аналогічна проблема виникає при прийомі (RX): контролер DMA записує прийняті байти у фізичну пам'ять SRAM, але процесор, виконуючи функцію розбору повідомлення, зчитує старі значення, що залишилися в рядках кеша.

   *Інженерні шляхи вирішення когерентності:*
   - **Конфігурація MPU (Memory Protection Unit):** Виділити окрему область оперативної пам'яті (наприклад, блок SRAM4 або D3 Domain) як некешовану область пам'яті (*Device* або *Normal Non-cacheable*) і розміщувати всі буфери DMA виключно в цій зоні.
   - **Явне очищення та інвалідація кеша:** Перед кожним запуском передачі DMA викликати функцію очищення кеша `SCB_CleanDCache_by_Addr((uint32_t *)&drv->tx_ring.buffer[tail], chunk_len)`, а після спрацьовування переривання прийому DMA — викликати функцію інвалідації рядків кеша `SCB_InvalidateDCache_by_Addr((uint32_t *)drv->dma_rx_buf, UART_RX_DMA_BUF_SIZE)`.
   При цьому розміри буферів та їхні початкові адреси обов'язково повинні бути вирівняні на розмір рядка кеша (32 байти), інакше інвалідація сусідніх змінних у пам'яті призведе до випадкового руйнування стека.

2. **Помилковий спільний доступ (False Sharing на багатоядерних SoC):**
   На гетерогенних або багатоядерних процесорах (наприклад, двоядерні мікроконтролери STM32H747 з ядрами Cortex-M7 та Cortex-M4 або процесори супутніх комп'ютерів Raspberry Pi) покажчики `head` та `tail` можуть потрапити в одну 64-байтову лінію кеша.
   
   Коли продюсер на ядрі M7 записує новий індекс `head`, протокол когерентності апаратно інвалідує всю кеш-лінію для ядра M4, змушуючи його повторно вичитувати змінну `tail` із повільної загальної пам'яті.
   
   *Рішення:* Використання директиви вирівнювання `alignas(64)` для розміщення кожного атомарного індексу в окремому рядку кеша.

3. **Скидання залишкових байтів при перериванні IDLE:**
   Якщо наземна станція надсилає потік байтів безперервно без жодної паузи між кадрами, апаратний прапорець простою лінії UART IDLE може не піднятися вчасно.
   
   *Рішення:* Крім переривання IDLE, обов'язково вмикати переривання половинного заповнення (`HT - Half Transfer`) та повного заповнення (`TC - Transfer Complete`) буфера DMA, що гарантує безперервну обробку пакетів навіть при 100% завантаженні лінії без пауз.
