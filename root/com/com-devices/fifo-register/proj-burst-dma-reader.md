# ⚙️ Драйвер пакетного вичитування FIFO через SPI DMA

У системах автономної навігації, безпілотних літальних апаратах, трекерах рухів та портативній медичній телеметрії опитування інерційних вимірювальних модулів (IMU) на високих частотах дискретизації (від 1 кГц до 6.66 кГц) здатне повністю заблокувати обчислювальне ядро мікроконтролера, якщо вичитувати кожен вектор вимірів поодинці через блокуючі синхронні виклики шини. Організація буферизації через вбудований у сенсор апаратний буфер FIFO та вичитування накопичених блоків за допомогою контролера прямого доступу до пам'яті (DMA, *Direct Memory Access*) дозволяє центральному процесору залишатися в режимі сну понад 95–98% часу, прокидаючись лише для високорівневої математичної обробки сформованих пакетів.

Нижче наведено закінчену інженерну реалізацію асинхронного неблокуючого драйвера для 6-осьового MEMS-сенсора (на прикладі архітектури STMicroelectronics LSM6DSO / TDK InvenSense ICM-42688). Драйвер поєднує апаратне переривання вотермарка, високошвидкісний SPI DMA Burst, захист від розриву кадрової синхронізації та безблокувальний потокобезпечний кільцевий буфер для передачі вибірок у прикладні задачі.

---

### Системна архітектура та часова послідовність подій

Класична схема зчитування за готовністю даних (*Data Ready Interrupt*, DRDY) створює рівно 1000 переривань ядра щосекунди при частоті 1 кГц. Навіть на швидкому 32-бітному мікроконтролері з ядром ARM Cortex-M4/M7 на тактовій частоті 168 МГц вхід у переривання, збереження регістрів у стек, запуск транзакції шини [SPI](root:com-devices/spi-bus), очікування байтів та вихід із переривання займають близько 2–4 мкс на кожну ітерацію. Якщо ж шина працює на помірній швидкості або використовується [I2C](root:com-devices/i2c-bus), процесор витрачає на обслуговування датчика до чверті свого ресурсу.

Застосування буфера FIFO докорінно змінює часову діаграму:
1. **Фаза автономного накопичення:** Сенсор самостійно вимірює прискорення та кутові швидкості, пакуючи їх у внутрішню пам'ять SRAM. Мікроконтролер перебуває у стані глибокого сну (Stop / Deep Sleep), живлячи лише модуль зовнішніх переривань (EXTI) зі споживанням 2–15 мкА.
2. **Фаза спрацьовування вотермарка:** Коли кількість накопичених слотів досягає заданого порогу `WTM = 64` слоти (448 байтів при 7 байтах на слот), сенсор піднімає фізичну лінію переривання `INT1`.
3. **Фаза запуску DMA:** Сигнал `INT1` будить ядро мікроконтролера. Обробник переривання EXTI виконує мінімальну роботу: за кілька інструкцій активує передачу по шині SPI через контролер DMA, опускає лінію Chip Select (CS) і миттєво повертає ядро у стан сну.
4. **Фаза передачі даних:** Контролер DMA повністю автономно тактує шину SPI, перекачуючи 448 байтів прямо у виділений буфер оперативної пам'яті мікроконтролера без участі процесорного ядра.
5. **Фаза завершення та парсингу:** Після пересилання останнього байта контролер DMA генерує переривання завершення транзакції (*Transfer Complete Interrupt*). Ядро прокидається, піднімає лінію CS і викликає парсер, який розбирає теговані кадри та розкладає вектори прискорення й кутової швидкості у відповідні кільцеві черги.

```
┌─────────────────┐                  ┌──────────────────────────────────────────────┐
│  MEMS IMU Сенсор│                  │             Мікроконтролер (MCU)             │
│                 │   Лінія INT1     │                                              │
│ [ Апаратне FIFO ]├─────────────────►│ 1. Обробник переривання (ISR / EXTI)         │
│   (448 байтів)  │ (Watermark High) │    └─► Ініціалізує та запускає SPI DMA       │
│                 │                  │                                              │
│                 │    Шина SPI      │ 2. Апаратний контролер DMA                   │
│ [ Шинний Порт ] │◄═════════════════┤    └─► Пересилає 448 байтів без участі ядра  │
│  (FIFO_DATA_OUT)│ (DMA Burst Read) │                                              │
│                 │                  │ 3. Колбек завершення DMA (Transfer Complete) │
│                 │                  │    └─► Розбирає теги та наповнює чергу      │
└─────────────────┘                  └──────────────────────────────────────────────┘
```

---

### Програмна реалізація драйвера

Нижче наведено паралельні реалізації драйвера: на чистому C з ручним керуванням пам'яттю та на сучасному ідіоматичному C++20 з використанням типізованих контейнерів, представлень пам'яті `std::span` та безблокувальних атомарних черг.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FIFO_TAG_EMPTY         0x00
#define FIFO_TAG_GYRO          0x01
#define FIFO_TAG_ACCEL         0x02
#define FIFO_TAG_TIMESTAMP     0x04
#define FIFO_SLOT_SIZE         7
#define FIFO_WATERMARK_SLOTS   64
#define FIFO_DMA_BUFFER_SIZE   (FIFO_WATERMARK_SLOTS * FIFO_SLOT_SIZE + 1) // +1 байт адреси регістра

#define RING_BUFFER_CAPACITY   256

// Структура одного фізичного виміру сенсора
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
    uint32_t timestamp_us;
} ImuSample;

// Потокобезпечний кільцевий буфер для взаємодії переривання з фоновою задачею
typedef struct {
    ImuSample buffer[RING_BUFFER_CAPACITY];
    volatile uint16_t head;
    volatile uint16_t tail;
    volatile uint32_t dropped_samples;
} ImuRingBuffer;

static ImuRingBuffer g_accel_ring;
static ImuRingBuffer g_gyro_ring;

// Буфери DMA повинні мати жорстке 32-байтне вирівнювання для коректної інвалідації D-Cache
__attribute__((aligned(32))) static uint8_t g_spi_tx_buf[FIFO_DMA_BUFFER_SIZE];
__attribute__((aligned(32))) static uint8_t g_spi_rx_buf[FIFO_DMA_BUFFER_SIZE];
static volatile bool g_dma_in_progress = false;

// Апаратні виклики низького рівня (BSP)
extern void bsp_spi_select(void);
extern void bsp_spi_deselect(void);
extern void bsp_spi_transfer_dma(const uint8_t *tx, uint8_t *rx, uint16_t len);
extern void bsp_sensor_fifo_reset(void);
extern uint32_t bsp_get_system_micros(void);
extern void bsp_dcache_invalidate(void *addr, uint32_t size);

void imu_ring_init(ImuRingBuffer *rb) {
    rb->head = 0;
    rb->tail = 0;
    rb->dropped_samples = 0;
}

void imu_ring_push(ImuRingBuffer *rb, const ImuSample *sample) {
    uint16_t next_head = (rb->head + 1) % RING_BUFFER_CAPACITY;
    if (next_head != rb->tail) {
        rb->buffer[rb->head] = *sample;
        rb->head = next_head;
    } else {
        rb->dropped_samples++; // Переповнення кільцевого буфера застосунку
    }
}

bool imu_ring_pop(ImuRingBuffer *rb, ImuSample *out_sample) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *out_sample = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % RING_BUFFER_CAPACITY;
    return true;
}

// 1. Апаратний обробник зовнішнього переривання (EXTI) по лінії Watermark
void EXTI_Sensor_Watermark_ISR(void) {
    if (!g_dma_in_progress) {
        g_dma_in_progress = true;
        
        // Формування команди читання з автоінкрементом для вікна FIFO_DATA_OUT (0x78)
        // Для шини SPI біт 7 встановлюється в 1 (Read: 0x80 | 0x78 = 0xF8)
        g_spi_tx_buf[0] = 0x78 | 0x80;
        memset(&g_spi_tx_buf[1], 0x00, FIFO_DMA_BUFFER_SIZE - 1);
        
        bsp_spi_select();
        bsp_spi_transfer_dma(g_spi_tx_buf, g_spi_rx_buf, FIFO_DMA_BUFFER_SIZE);
    }
}

// 2. Колбек завершення пересилання DMA (викликається контролером DMA по перериванню)
void DMA_SPI_RxComplete_Callback(void) {
    bsp_spi_deselect();
    g_dma_in_progress = false;

    // Інвалідація кешу даних процесора перед читанням пам'яті, заповненої DMA
    bsp_dcache_invalidate(g_spi_rx_buf, FIFO_DMA_BUFFER_SIZE);

    // Перший байт RX є сміттям (фаза адреси), корисний потік починається з індексу 1
    const uint8_t *raw_stream = &g_spi_rx_buf[1];
    uint16_t total_bytes = FIFO_DMA_BUFFER_SIZE - 1;
    uint32_t now = bsp_get_system_micros();

    for (uint16_t i = 0; i + FIFO_SLOT_SIZE <= total_bytes; i += FIFO_SLOT_SIZE) {
        const uint8_t *slot = &raw_stream[i];
        uint8_t tag = (slot[0] >> 3) & 0x1F; // Виділення 5-бітного коду тегу

        ImuSample sample;
        // Збирання 16-бітних знакових слів із пари байтів (Little-Endian)
        sample.x = (int16_t)((uint16_t)slot[1] | ((uint16_t)slot[2] << 8));
        sample.y = (int16_t)((uint16_t)slot[3] | ((uint16_t)slot[4] << 8));
        sample.z = (int16_t)((uint16_t)slot[5] | ((uint16_t)slot[6] << 8));
        sample.timestamp_us = now;

        switch (tag) {
            case FIFO_TAG_ACCEL:
                imu_ring_push(&g_accel_ring, &sample);
                break;
            case FIFO_TAG_GYRO:
                imu_ring_push(&g_gyro_ring, &sample);
                break;
            case FIFO_TAG_EMPTY:
                // Досягнуто кінця валідних даних: буфер вичитано повністю
                return;
            default:
                // Невідомий або пошкоджений тег: ознака фазового збою потоку
                bsp_sensor_fifo_reset();
                return;
        }
    }
}
```
```cpp
#include <cstdint>
#include <array>
#include <optional>
#include <atomic>
#include <span>
#include <algorithm>

namespace embedded::sensor {

enum class SensorTag : uint8_t {
    Empty     = 0x00,
    GyroNC    = 0x01,
    AccelNC   = 0x02,
    Timestamp = 0x04,
    Invalid   = 0xFF
};

struct ImuSample {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
    uint32_t timestamp_us{0};
};

template <typename T, size_t Capacity>
class LockFreeRingBuffer {
public:
    bool push(const T& item) noexcept {
        const auto current_head = head_.load(std::memory_order_relaxed);
        const auto next_head = (current_head + 1) % Capacity;
        if (next_head == tail_.load(std::memory_order_acquire)) {
            dropped_count_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }
        storage_[current_head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() noexcept {
        const auto current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }
        T item = storage_[current_tail];
        tail_.store((current_tail + 1) % Capacity, std::memory_order_release);
        return item;
    }

    [[nodiscard]] uint32_t dropped_count() const noexcept {
        return dropped_count_.load(std::memory_order_relaxed);
    }

private:
    std::array<T, Capacity> storage_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
    std::atomic<uint32_t> dropped_count_{0};
};

class FifoDmaReader {
public:
    static constexpr size_t SlotSize = 7;
    static constexpr size_t WatermarkSlots = 64;
    static constexpr size_t DmaBufferSize = WatermarkSlots * SlotSize + 1;

    FifoDmaReader() = default;

    void on_watermark_isr() noexcept {
        if (!dma_busy_.exchange(true, std::memory_order_acq_rel)) {
            tx_buffer_[0] = 0x78 | 0x80; // FIFO_DATA_OUT | SPI Read Bit
            std::fill(tx_buffer_.begin() + 1, tx_buffer_.end(), 0x00);
            
            start_hardware_dma(tx_buffer_.data(), rx_buffer_.data(), DmaBufferSize);
        }
    }

    void on_dma_complete_callback(uint32_t current_time_us) noexcept {
        stop_hardware_spi();
        invalidate_dcache(rx_buffer_.data(), DmaBufferSize);
        dma_busy_.store(false, std::memory_order_release);

        std::span<const uint8_t> payload{&rx_buffer_[1], DmaBufferSize - 1};

        for (size_t offset = 0; offset + SlotSize <= payload.size(); offset += SlotSize) {
            auto slot = payload.subspan(offset, SlotSize);
            auto tag = parse_tag(slot[0]);

            if (tag == SensorTag::Empty) {
                break;
            }

            if (tag == SensorTag::Invalid) {
                trigger_hardware_fifo_reset();
                break;
            }

            ImuSample sample{
                .x = static_cast<int16_t>(slot[1] | (static_cast<uint16_t>(slot[2]) << 8)),
                .y = static_cast<int16_t>(slot[3] | (static_cast<uint16_t>(slot[4]) << 8)),
                .z = static_cast<int16_t>(slot[5] | (static_cast<uint16_t>(slot[6]) << 8)),
                .timestamp_us = current_time_us
            };

            if (tag == SensorTag::AccelNC) {
                accel_queue_.push(sample);
            } else if (tag == SensorTag::GyroNC) {
                gyro_queue_.push(sample);
            }
        }
    }

    LockFreeRingBuffer<ImuSample, 256>& accel_queue() noexcept { return accel_queue_; }
    LockFreeRingBuffer<ImuSample, 256>& gyro_queue() noexcept { return gyro_queue_; }

private:
    [[nodiscard]] static SensorTag parse_tag(uint8_t raw_byte) noexcept {
        uint8_t tag_val = (raw_byte >> 3) & 0x1F;
        switch (tag_val) {
            case 0x00: return SensorTag::Empty;
            case 0x01: return SensorTag::GyroNC;
            case 0x02: return SensorTag::AccelNC;
            case 0x04: return SensorTag::Timestamp;
            default:   return SensorTag::Invalid;
        }
    }

    // Низькорівневі апаратні функції платформи
    void start_hardware_dma(const uint8_t* tx, uint8_t* rx, size_t len) noexcept;
    void stop_hardware_spi() noexcept;
    void trigger_hardware_fifo_reset() noexcept;
    void invalidate_dcache(const void* addr, size_t size) noexcept;

    alignas(32) std::array<uint8_t, DmaBufferSize> tx_buffer_{};
    alignas(32) std::array<uint8_t, DmaBufferSize> rx_buffer_{};
    std::atomic<bool> dma_busy_{false};

    LockFreeRingBuffer<ImuSample, 256> accel_queue_{};
    LockFreeRingBuffer<ImuSample, 256> gyro_queue_{};
};

} // namespace embedded::sensor
```
:::

---

### Детальний покроковий розбір конвеєра обробки

#### 1. Апаратне налаштування периферійних блоків мікроконтролера

Для забезпечення стабільного функціонування неблокуючого обміну драйвер спирається на три периферійні вузли мікроконтролера: контролер зовнішніх переривань EXTI, модуль послідовної шини SPI Master та два канали прямого доступу до пам'яті DMA (TX та RX).

- **Конфігурація шини SPI:** Модуль налаштовується в режим Master, формат даних 8 біт, порядок бітів MSB First. Фаза і полярність тактового сигналу (CPOL/CPHA) повинні відповідати режиму SPI Mode 3 (CPOL=1, CPHA=1) або Mode 0 (CPOL=0, CPHA=0) згідно з даташитом сенсора. Тактова частота встановлюється на рівні 10–20 МГц.
- **Конфігурація DMA каналів:** Канал передачі (SPI_TX_DMA) налаштовується в режимі Memory-to-Peripheral з автоінкрементом адреси пам'яті. Канал прийому (SPI_RX_DMA) налаштовується в режимі Peripheral-to-Memory з інкрементом буфера призначення. Пріоритет каналу RX встановлюється вищим за пріоритет TX для запобігання переповненню вхідного буферного регістра SPI (Overrun Error).
- **Конфігурація контролера переривань NVIC:** Перериванню EXTI від ніжки сенсора присвоюється високий рівень пріоритету, але нижчий за пріоритети критичних системних таймерів. Перериванню завершення DMA присвоюється середній пріоритет.

#### 2. Атомарний прапорець зайнятості DMA (`g_dma_in_progress` / `dma_busy_`)

У системах реального часу з витісненням (*Preemptive RTOS*) або при виникненні завад на сигнальній лінії лінія `INT1` може сформувати додатковий імпульс до того, як попередня передача DMA завершиться. Безпечна атомарна перевірка стану через операцію `exchange` гарантує, що обробник EXTI не почне перезаписувати дескриптори DMA та буфери `g_spi_tx_buf`, коли попередня транзакція ще триває.

#### 3. Зсув корисного навантаження на 1 байт (`raw_stream = &g_spi_rx_buf[1]`)

Шина SPI є повнодуплексною: передача кожного біта з лінії MOSI супроводжується одночасним читанням біта з лінії MISO. У момент надсилання першого байта команди (`0x78 | 0x80`) сенсор лише дешифрує адресу та готує внутрішній вказівник читання, повертаючи в лінію MISO невизначений байт (сміття). Корисні байти кадру починають надходити лише з другого тактового циклу, тому парсер зміщує початковий покажчик аналізу на індекс 1.

#### 4. Апаратне вирівнювання та кеш-когерентність (`alignas(32)`)

На сучасних мікроконтролерах із ядрами ARM Cortex-M7 (STM32H7, NXP i.MX RT) та Cortex-A увімкнено апаратне кешування даних (D-Cache). Контролер DMA перекачує байти з шини SPI безпосередньо у фізичну пам'ять SRAM, минаючи L1-кеш процесора. Якщо буфер не вирівняно за межею 32-байтної кеш-лінії і перед його читанням не викликано інвалідацію кешу (`bsp_dcache_invalidate`), ядро прочитає старі закешовані значення (нулі або дані попередньої ітерації). Використання специфікатора `alignas(32)` та виклику інвалідації є обов'язковою умовою надійності.

#### 5. Подвійна буферизація (Double Buffering / Ping-Pong DMA)

Для систем із гранично високими частотами дискретизації (наприклад, 4–6.66 кГц у системах аналізу високошвидкісних вібрацій) обробка вичитаного пакета може не вкладатися в інтервал накопичення наступного блоку. У таких випадках застосовують схему подвійної буферизації (*Ping-Pong Buffer*).

Контролер DMA налаштовується на роботу з подвійним буфером або в кільцевому режимі (*Circular DMA Mode*). Коли перша половина буфера заповнюється, контролер DMA генерує переривання *Half-Transfer Complete*, сигналізуючи ядру про необхідність почати парсинг першого блоку. У цей самий час контролер DMA без жодної мікросекунди паузи продовжує наповнювати другу половину буфера. Після її заповнення генерується переривання *Transfer Complete*, і задачі міняються ролями. Це повністю усуває втрати даних навіть при 100% завантаженні процесора.

#### 6. Компенсація дрейфу годинника (Clock Drift Correction)

Внутрішній кремнієвий RC-генератор сенсора має температурну нестабільність до ±1–2%. Якщо мікроконтролер розраховує фізичні координати чи швидкість методом числового інтегрування, невраховане відхилення часової шкали призводить до накопичення лінійної похибки траєкторії.

Для високоточної навігації драйвер використовує апаратні 32-бітні мітки часу `Timestamp`, які сенсор пакує безпосередньо в кадри FIFO. Порівнюючи приріст апаратних міток сенсора з високоточним кварцовим таймером мікроконтролера (наприклад, лічильником циклів DWT або апаратним таймером TIM), програмний фільтр у реальному часі розраховує коефіцієнт масштабування часу, гарантуючи нульову похибку інтегрування.

---

### Пастки та крайові випадки інженерної реалізації

1. **Читання за межами доступних даних (*Overread Hazard*):**
   Якщо мікроконтролер запросить через DMA більше слотів, ніж реально зберігається у пам'яті сенсора на момент старту, сенсор повертає байти-заповнювачі (зазвичай `0x00` або `0xFF`). Якщо парсер не аналізує тег `0x00` як ознаку порожнечі, драйвер передасть у систему фіктивні нульові прискорення, спотворюючи інтеграл швидкості.
2. **Розрив пакетної сесії через передчасне скидання Chip Select (CS):**
   Внутрішній апаратний вказівник читання FIFO (*Read Pointer*) збільшується автоматично на кожному такті лише доти, доки лінія CS утримується на низькому рівні. Якщо апаратний драйвер SPI мікроконтролера короткочасно піднімає CS між окремими словами або байтами транзакції, сенсор інтерпретує це як завершення операції та скидає автоінкремент.
3. **Блокування лінії переривання через незчитаний статус:**
   У деяких моделях сенсорів (наприклад, InvenSense MPU-6050) переривання вотермарка є рівневим (*Level-triggered*) і скидається виключно після явного читання регістра статусу переривань `INT_STATUS`. Якщо драйвер у відповідь на переривання починає одразу читати `FIFO_DATA`, лінія `INT` залишається у високому рівні назавжди, блокуючи всі наступні виклики обробника EXTI.
4. **Втрата синхронізації при переповненні (*FIFO Overrun*):**
   Якщо в системі виникає затримка виклику DMA і буфер переповнюється, частина вибірок може бути частково перезаписана. Якщо парсер виявляє невідомий тег, єдиним правильним рішенням є негайний виклик `bsp_sensor_fifo_reset()`, що переводить буфер у режим Bypass на 2–3 цикли такту та повертає його в режим Continuous, відновлюючи чистий фазовий початок для наступних пакетів.
