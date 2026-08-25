# ⚙️ Реалізація синхронного зчитування на таймерах TRGO та DMA

Коли в польотному контролері безпілотника центральний процесор опитує давачі через блокуючі виклики SPI чи I2C, затримки виконання переривань і планувальника операційної системи спричиняють випадковий джиттер часових міток і розбіг фаз між осями. Щоб досягти детермінованого збору даних із субмікросекундною синхронізацією, всю послідовність — від тактування перетворень до перенесення кадрів у пам'ять — переносять на апаратний рівень. Цей проєкт реалізує апаратний конвеєр зчитування двох незалежних інерційних модулів (IMU) за допомогою головного таймера (Timer TRGO), захоплення апаратних міток часу (Timer Input Capture) та багатоканального прямого доступу до пам'яті (DMA) без участі ядра процесора під час передачі.

## Апаратна архітектура конвеєра

Схема керування складається з чотирьох апаратно пов'язаних вузлів мікроконтролера STM32 (ARM Cortex-M):

1. **Головний таймер синхронізації (TIM1):** працює з базовою частотою 1 кГц і на кожному переповненні генерує внутрішній сигнал запуску `TRGO` (*Trigger Output* — вихід тригера). Цей сигнал одночасно виводиться на зовнішній пін для тактування ліній `FSYNC` обох IMU.
2. **Таймер системного часу (TIM2):** 32-бітний вільнобіжний лічильник із тактовою частотою 1 МГц (дискрет 1 мкс).
3. **Блок захоплення за подією (EXTI + TIM2 Capture):** спадний або наростаючий фронт на лініях готовності даних `DRDY` ініціює апаратне замикання (*latching*) поточного значення лічильника `TIM2` у регістр захоплення без затримок входу в обробник переривання.
4. **Контролер прямого доступу до пам'яті (DMA):** переносить 14-байтні пакети (3 осі акселерометра, 3 осі гіроскопа, температура) з шин `SPI1` та `SPI2` у кільцевий буфер оперативної пам'яті (SRAM).

```
   ┌─────────────────────────────────────────────────────────────┐
   │                    Головний таймер TIM1                     │
   │  Частота 1000 Гц  ───>  Оновлення рахунку  ───>  Подія TRGO │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       ┌────────────────────┐          ┌────────────────────┐
       │ FSYNC -> IMU 1     │          │ FSYNC -> IMU 2     │
       │ Старт АЦП вибірки  │          │ Старт АЦП вибірки  │
       └──────────┬─────────┘          └──────────┬─────────┘
                  │ t_conv                        │ t_conv
                  ▼                               ▼
       ┌────────────────────┐          ┌────────────────────┐
       │ DRDY 1: Готово!    │          │ DRDY 2: Готово!    │
       └──────────┬─────────┘          └──────────┬─────────┘
                  │                               │
                  ├───────────────────────────────┤
                  ▼                               ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  Апаратне захоплення мітки часу TIM2 (CCR1 / CCR2)         │
   │  Запуск каналів DMA (SPI1 RX -> Buf1, SPI2 RX -> Buf2)     │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │         Кільцевий подвійний буфер вибірок у SRAM            │
   │      Готовий синхронізований кадр для фільтра EKF           │
   └─────────────────────────────────────────────────────────────┘
```

## Реалізація конвеєра: структури даних та драйвер

Нижче наведено робочий код конвеєра для двох паралельних шин SPI з підтримкою подвійної буферизації та апаратного захоплення часових міток.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define IMU_PACKET_SIZE       14   /* 6 байтів Accel + 6 байтів Gyro + 2 байти Temp */
#define RING_BUFFER_CAPACITY  64

/* Структура сирого пакета з апаратною міткою часу */
typedef struct {
    uint32_t timestamp_us;         /* Значення захопленого лічильника TIM2 */
    int16_t accel_raw[3];          /* Осі X, Y, Z */
    int16_t gyro_raw[3];           /* Осі X, Y, Z */
    int16_t temp_raw;
    uint8_t sensor_id;
    uint8_t status_flags;
} ImuSampleFrame;

/* Кільцевий буфер синхронізованих кадрів */
typedef struct {
    ImuSampleFrame frames[RING_BUFFER_CAPACITY];
    volatile uint32_t head;
    volatile uint32_t tail;
} ImuRingBuffer;

static ImuRingBuffer g_imu_ring;
static uint8_t g_spi1_rx_dma_buf[IMU_PACKET_SIZE];
static uint8_t g_spi2_rx_dma_buf[IMU_PACKET_SIZE];
static uint8_t g_spi_tx_dummy[IMU_PACKET_SIZE] = {0x80 | 0x1F, 0}; /* Читання з регістру FIFO */

/* Ініціалізація кільцевого буфера */
void imu_ring_buffer_init(void) {
    g_imu_ring.head = 0;
    g_imu_ring.tail = 0;
}

/* Перевірка наявності нових зразків */
bool imu_ring_buffer_pop(ImuSampleFrame *out_frame) {
    if (g_imu_ring.head == g_imu_ring.tail) {
        return false; /* Буфер порожній */
    }
    *out_frame = g_imu_ring.frames[g_imu_ring.tail];
    g_imu_ring.tail = (g_imu_ring.tail + 1) % RING_BUFFER_CAPACITY;
    return true;
}

/* Обробник переривання EXTI для лінії DRDY IMU 1 */
void EXTI0_IRQHandler(void) {
    /* 1. Зчитуємо апаратно захоплену мітку часу з регістру захоплення TIM2 */
    uint32_t captured_time_us = TIM2->CCR1;

    /* 2. Опускаємо лінію Chip Select (CS) для SPI1 */
    GPIOA->BSRR = (1U << (4 + 16)); /* PA4 = LOW (CS active) */

    /* 3. Конфігуруємо та запускаємо передачу DMA для читання пакета */
    DMA1_Stream0->NDTR = IMU_PACKET_SIZE;
    DMA1_Stream0->M0AR = (uint32_t)g_spi1_rx_dma_buf;
    DMA1_Stream0->CR |= DMA_SxCR_EN;

    DMA1_Stream3->NDTR = IMU_PACKET_SIZE;
    DMA1_Stream3->M0AR = (uint32_t)g_spi_tx_dummy;
    DMA1_Stream3->CR |= DMA_SxCR_EN;

    /* Скидання прапорця переривання EXTI */
    EXTI->PR = EXTI_PR_PR0;
}

/* Обробник завершення DMA передачі SPI1 */
void DMA1_Stream0_IRQHandler(void) {
    if (DMA1->LISR & DMA_LISR_TCIF0) {
        DMA1->LIFCR = DMA_LIFCR_CTCIF0;

        /* Піднімаємо CS (PA4 = HIGH) */
        GPIOA->BSRR = (1U << 4);

        /* Розбір отриманого кадру та збереження в кільцевий буфер */
        uint32_t next_head = (g_imu_ring.head + 1) % RING_BUFFER_CAPACITY;
        if (next_head != g_imu_ring.tail) {
            ImuSampleFrame *frame = &g_imu_ring.frames[g_imu_ring.head];
            frame->timestamp_us = TIM2->CCR1;
            frame->sensor_id = 1;

            /* Розпакування 16-бітних слів Big-Endian */
            frame->accel_raw[0] = (int16_t)((g_spi1_rx_dma_buf[1] << 8) | g_spi1_rx_dma_buf[2]);
            frame->accel_raw[1] = (int16_t)((g_spi1_rx_dma_buf[3] << 8) | g_spi1_rx_dma_buf[4]);
            frame->accel_raw[2] = (int16_t)((g_spi1_rx_dma_buf[5] << 8) | g_spi1_rx_dma_buf[6]);

            frame->temp_raw = (int16_t)((g_spi1_rx_dma_buf[7] << 8) | g_spi1_rx_dma_buf[8]);

            frame->gyro_raw[0] = (int16_t)((g_spi1_rx_dma_buf[9] << 8) | g_spi1_rx_dma_buf[10]);
            frame->gyro_raw[1] = (int16_t)((g_spi1_rx_dma_buf[11] << 8) | g_spi1_rx_dma_buf[12]);
            frame->gyro_raw[2] = (int16_t)((g_spi1_rx_dma_buf[13] << 8) | g_spi1_rx_dma_buf[14]);

            g_imu_ring.head = next_head;
        }
    }
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <atomic>
#include <optional>
#include <concepts>

namespace sensor_sync {

inline constexpr std::size_t PacketSize = 14;
inline constexpr std::size_t RingCapacity = 64;

struct ImuRawReading {
    std::uint32_t timestamp_us{0};
    std::array<std::int16_t, 3> accel{0, 0, 0};
    std::array<std::int16_t, 3> gyro{0, 0, 0};
    std::int16_t temperature{0};
    std::uint8_t sensor_id{0};
    std::uint8_t flags{0};
};

template <typename T, std::size_t Capacity>
class LockFreeRingBuffer {
public:
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");

    constexpr LockFreeRingBuffer() : head_{0}, tail_{0} {}

    bool push(const T& item) noexcept {
        const auto current_head = head_.load(std::memory_order_relaxed);
        const auto next_head = (current_head + 1) & BufferMask;

        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; // Буфер переповнено
        }

        storage_[current_head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() noexcept {
        const auto current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt; // Буфер порожній
        }

        T item = storage_[current_tail];
        tail_.store((current_tail + 1) & BufferMask, std::memory_order_release);
        return item;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

private:
    static constexpr std::size_t BufferMask = Capacity - 1;
    std::array<T, Capacity> storage_{};
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
};

class SpiDmaSyncReader {
public:
    explicit constexpr SpiDmaSyncReader(std::uint8_t sensor_id) noexcept
        : sensor_id_{sensor_id} {}

    void on_drdy_trigger(std::uint32_t captured_timestamp_us) noexcept {
        last_timestamp_ = captured_timestamp_us;
        start_dma_transfer();
    }

    void on_dma_complete(std::span<const std::uint8_t, PacketSize> rx_bytes,
                         LockFreeRingBuffer<ImuRawReading, RingCapacity>& queue) noexcept {
        ImuRawReading reading;
        reading.timestamp_us = last_timestamp_;
        reading.sensor_id = sensor_id_;

        // Декодування 16-бітних слів Big-Endian
        reading.accel[0] = static_cast<std::int16_t>((rx_bytes[1] << 8) | rx_bytes[2]);
        reading.accel[1] = static_cast<std::int16_t>((rx_bytes[3] << 8) | rx_bytes[4]);
        reading.accel[2] = static_cast<std::int16_t>((rx_bytes[5] << 8) | rx_bytes[6]);

        reading.temperature = static_cast<std::int16_t>((rx_bytes[7] << 8) | rx_bytes[8]);

        reading.gyro[0] = static_cast<std::int16_t>((rx_bytes[9] << 8) | rx_bytes[10]);
        reading.gyro[1] = static_cast<std::int16_t>((rx_bytes[11] << 8) | rx_bytes[12]);
        reading.gyro[2] = static_cast<std::int16_t>((rx_bytes[13] << 8) | rx_bytes[14]);

        queue.push(reading);
    }

private:
    void start_dma_transfer() noexcept {
        // Активація транзакції DMA через регістри периферії
    }

    std::uint8_t sensor_id_{0};
    std::uint32_t last_timestamp_{0};
};

} // namespace sensor_sync
```
:::

## Покроковий розбір конфігурації апаратних блоків

### Крок 1. Налаштування головного таймера (TIM1 TRGO)

Головний таймер задає період квантування всієї системи. Регістр автоматичного перезавантаження `ARR` (*Auto-Reload Register*) налаштовується на період 1000 мкс:

:::tabs
```c
/* Тактування таймера від шини APB2 (наприклад, 168 МГц) */
TIM1->PSC = 168 - 1;           /* Переддільник: частота лічильника = 1 МГц */
TIM1->ARR = 1000 - 1;          /* Період переповнення = 1000 тактів = 1 мс (1 кГц) */

/* Формування сигналу TRGO при події переповнення (Update Event) */
TIM1->CR2 &= ~TIM_CR2_MMS;
TIM1->CR2 |= TIM_CR2_MMS_1;    /* MMS = 010: Update подія виводиться як TRGO */

/* Вивід імпульсу FSYNC через канал порівняння TIM1_CH1 */
TIM1->CCR1 = 10;               /* Тривалість імпульсу синхронізації 10 мкс */
TIM1->CCMR1 |= (6U << TIM_CCMR1_OC1M_Pos); /* Режим PWM1 */
TIM1->CCER |= TIM_CCER_CC1E;   /* Дозвіл виводу сигналу на пін */
TIM1->CR1 |= TIM_CR1_CEN;      /* Старт лічильника */
```
```cpp
namespace hardware {

struct MasterTimerInit {
    static constexpr std::uint32_t BusClockHz = 168'000'000;
    static constexpr std::uint32_t CounterClockHz = 1'000'000;
    static constexpr std::uint32_t SampleRateHz = 1'000;
    static constexpr std::uint32_t SyncPulseUs = 10;

    static void setup(TIM_TypeDef* tim) noexcept {
        tim->PSC = (BusClockHz / CounterClockHz) - 1;
        tim->ARR = (CounterClockHz / SampleRateHz) - 1;

        // Подія Update виводиться на тригер TRGO
        tim->CR2 = (tim->CR2 & ~TIM_CR2_MMS) | TIM_CR2_MMS_1;

        tim->CCR1 = SyncPulseUs;
        tim->CCMR1 |= (6U << TIM_CCMR1_OC1M_Pos); // PWM1
        tim->CCER |= TIM_CCER_CC1E;
        tim->CR1 |= TIM_CR1_CEN;
    }
};

} // namespace hardware
```
:::

### Крок 2. Апаратне захоплення часових міток (TIM2 Capture)

Щоб виключити вплив затримок обробки переривань на точність мітки, лінія `DRDY` фізично підключається не лише до входу `EXTI`, але й до каналу вхідного захоплення таймера `TIM2_CH1`:

:::tabs
```c
/* TIM2 у режимі 32-бітного лічильника реального часу (тактування 1 МГц) */
TIM2->PSC = 84 - 1;            /* APB1 84 МГц / 84 = 1 МГц */
TIM2->ARR = 0xFFFFFFFF;        /* Максимальний діапазон рахунку (понад 71 хвилина без переповнення) */

/* Канал 1: захоплення за наростаючим фронтом DRDY */
TIM2->CCMR1 |= TIM_CCMR1_CC1S_0; /* Вхід каналу прив'язаний до TI1 */
TIM2->CCER &= ~TIM_CCER_CC1P;    /* Чутливість до наростаючого фронту */
TIM2->CCER |= TIM_CCER_CC1E;     /* Дозвіл захоплення */
TIM2->CR1 |= TIM_CR1_CEN;
```
```cpp
namespace hardware {

struct TimestampCaptureTimer {
    static constexpr std::uint32_t ApbClockHz = 84'000'000;
    static constexpr std::uint32_t TimerFreqHz = 1'000'000;

    static void setup(TIM_TypeDef* tim) noexcept {
        tim->PSC = (ApbClockHz / TimerFreqHz) - 1;
        tim->ARR = 0xFFFFFFFF; // 32-бітний вільний лічильник

        tim->CCMR1 |= TIM_CCMR1_CC1S_0; // Прив'язка до входу TI1
        tim->CCER &= ~TIM_CCER_CC1P;    // Наростаючий фронт
        tim->CCER |= TIM_CCER_CC1E;     // Дозвіл захоплення
        tim->CR1 |= TIM_CR1_CEN;
    }

    [[nodiscard]] static std::uint32_t get_captured_timestamp(const TIM_TypeDef* tim) noexcept {
        return tim->CCR1;
    }
};

} // namespace hardware
```
:::

Коли давач активує лінію `DRDY`, апаратна логіка таймера за 1 такт фіксує поточний час у регістрі `TIM2->CCR1`. Навіть якщо ядро процесора в цей момент зайняте виконанням критичної секції з вимкненими перериваннями, мітка в `CCR1` залишається абсолютно точною.

### Крок 3. Багатоканальна DMA передача по шинах SPI

Для зчитування кадру з FIFO давача контролер DMA налаштовується на роботу в режимі перенесення пам'ять-периферія з повною розв'язкою від CPU:

:::tabs
```c
/* Налаштування потоку приймання DMA1_Stream0 (SPI1_RX) */
DMA1_Stream0->CR = 0;
while (DMA1_Stream0->CR & DMA_SxCR_EN); /* Очікування зупинки */

DMA1_Stream0->PAR = (uint32_t)&(SPI1->DR);
DMA1_Stream0->M0AR = (uint32_t)g_spi1_rx_dma_buf;
DMA1_Stream0->NDTR = IMU_PACKET_SIZE;
DMA1_Stream0->CR = DMA_SxCR_MINC |            /* Інкремент адреси в пам'яті */
                   DMA_SxCR_TCIE |            /* Переривання по завершенню */
                   (0U << DMA_SxCR_PL_Pos);   /* Пріоритет */

/* Дозвіл запитів DMA від SPI */
SPI1->CR2 |= SPI_CR2_RXDMAEN | SPI_CR2_TXDMAEN;
```
```cpp
namespace hardware {

template <std::size_t BufferSize>
class DmaSpiReceiver {
public:
    static void configure(DMA_Stream_TypeDef* stream, SPI_TypeDef* spi, std::uint8_t* destination) noexcept {
        stream->CR = 0;
        while (stream->CR & DMA_SxCR_EN) {} // Очікування вимкнення

        stream->PAR = reinterpret_cast<std::uint32_t>(&(spi->DR));
        stream->M0AR = reinterpret_cast<std::uint32_t>(destination);
        stream->NDTR = BufferSize;
        stream->CR = DMA_SxCR_MINC | DMA_SxCR_TCIE;

        spi->CR2 |= SPI_CR2_RXDMAEN | SPI_CR2_TXDMAEN;
    }

    static void start_transfer(DMA_Stream_TypeDef* stream, std::size_t length) noexcept {
        stream->NDTR = length;
        stream->CR |= DMA_SxCR_EN;
    }
};

} // namespace hardware
```
:::

## Подвійна буферизація DMA (Double-Buffered Mode / DBM)

У високопродуктивних системах зчитування 8 кГц IMU навіть мінімальна затримка програмного перезапуску дескриптора DMA може призвести до втрати байтів. Для повної ліквідації програмних пауз контролер DMA STM32 підтримує апаратний режим подвійної буферизації `DMA_SxCR_DBM` (*Double Buffer Mode*).

У цьому режимі потік DMA має два цільові регістри пам'яті: `M0AR` (Memory 0 Target) та `M1AR` (Memory 1 Target). Поки контролер заповнює буфер 0, процесор безпечно зчитує дані з буфера 1. По завершенню передачі апаратна логіка DMA автоматично перемикає покажчик на інший буфер без зупинки шини SPI:

:::tabs
```c
/* Конфігурація апаратного подвійного буфера DMA (Ping-Pong) */
void dma_double_buffer_init(uint8_t *buf0, uint8_t *buf1, uint16_t size) {
    DMA1_Stream0->CR &= ~DMA_SxCR_EN;
    while (DMA1_Stream0->CR & DMA_SxCR_EN);

    DMA1_Stream0->PAR = (uint32_t)&(SPI1->DR);
    DMA1_Stream0->M0AR = (uint32_t)buf0;
    DMA1_Stream0->M1AR = (uint32_t)buf1;
    DMA1_Stream0->NDTR = size;

    /* Вмикаємо режим DBM та дозволяємо переривання перемикання буферів */
    DMA1_Stream0->CR |= DMA_SxCR_DBM | DMA_SxCR_MINC | DMA_SxCR_TCIE;
    DMA1_Stream0->CR |= DMA_SxCR_EN;
}
```
```cpp
namespace hardware {

class DoubleBufferedDma {
public:
    static void configure(DMA_Stream_TypeDef* stream, SPI_TypeDef* spi,
                          std::span<std::uint8_t> buf0,
                          std::span<std::uint8_t> buf1) noexcept {
        stream->CR &= ~DMA_SxCR_EN;
        while (stream->CR & DMA_SxCR_EN) {}

        stream->PAR = reinterpret_cast<std::uint32_t>(&(spi->DR));
        stream->M0AR = reinterpret_cast<std::uint32_t>(buf0.data());
        stream->M1AR = reinterpret_cast<std::uint32_t>(buf1.data());
        stream->NDTR = static_cast<std::uint16_t>(buf0.size());

        stream->CR |= DMA_SxCR_DBM | DMA_SxCR_MINC | DMA_SxCR_TCIE;
        stream->CR |= DMA_SxCR_EN;
    }

    [[nodiscard]] static std::uint8_t get_current_target(const DMA_Stream_TypeDef* stream) noexcept {
        return (stream->CR & DMA_SxCR_CT) ? 1 : 0;
    }
};

} // namespace hardware
```
:::

## Модель пам'яті ARM та бар'єри синхронізації (DMB / DSB / ISB)

У високопродуктивних мікроконтролерах із конвеєрним виконанням інструкцій (ARM Cortex-M7) ядро може змінювати черговість операцій запису в пам'ять (*Out-of-Order Store Buffering*).

Якщо обробник DMA записує розпакований кадр у масив `g_imu_ring.frames[head]`, а потім негайно збільшує індекс `g_imu_ring.head`, компілятор або процесор можуть переставити ці операції місцями: індекс `head` стане видимим для іншого ядра або головного потоку RTOS раніше, ніж завершиться фізичний запис даних у SRAM. У результаті споживач зчитає старе сміття з пам'яті.

Щоб запобігти цьому, застосовують апаратний бар'єр пам'яті `__DMB()` (*Data Memory Barrier*):

:::tabs
```c
/* Безпечний запис у чергу без блокувань із бар'єром пам'яті */
void push_frame_safe(const ImuSampleFrame* frame) {
    uint32_t h = g_imu_ring.head;
    g_imu_ring.frames[h] = *frame;

    /* Гарантуємо, що запис корисного навантаження завершено до оновлення head */
    __DMB();

    g_imu_ring.head = (h + 1) % RING_BUFFER_CAPACITY;
}
```
```cpp
namespace concurrency {

template <typename T, std::size_t Capacity>
struct MemoryBarrierQueue {
    static void publish_frame(std::atomic<std::size_t>& head,
                              std::array<T, Capacity>& storage,
                              const T& item) noexcept {
        const auto current_head = head.load(std::memory_order_relaxed);
        storage[current_head] = item;

        // Встановлюємо бар'єр вивільнення пам'яті (Release Barrier)
        head.store((current_head + 1) % Capacity, std::memory_order_release);
    }
};

} // namespace concurrency
```
:::

## Узгодження таймінгу сигналів SPI (Setup, Hold та фази CPOL/CPHA)

При роботі на високих частотах SPI (20–24 МГц) тривалість одного тактового напівперіоду становить лише 20–25 нс. У промислових платах польотних контролерів обов'язково враховують такі параметри часової діаграми:

1. **Час встановлення даних (Data Setup Time, `t_SU`):** лінія MISO повинна встановити стабільний рівень напруги щонайменше за 5–8 нс до активного фронту тактового сигналу SCK.
2. **Час утримання даних (Data Hold Time, `t_HD`):** рівень напруги на лінії MISO повинен утримуватися не менше 5 нс після фронту тактування.
3. **Вибір режиму SPI (Mode 0 vs Mode 3):**
   - У режимі `Mode 0` (`CPOL=0, CPHA=0`) лінія SCK у стані спокою знаходиться в нулі.
   - У режимі `Mode 3` (`CPOL=1, CPHA=1`) лінія SCK у стані спокою підтягнута до живлення (HIGH). У зашумлених дронах режим `Mode 3` є більш завадостійким, оскільки лінія живлення забезпечує кращу стабільність відносно імпульсних просадок землі (Ground Bounce).

Ємність траси друкованої плати `C_trace` та вхідна ємність пінів давача формують RC-ланцюг із вихідним опором драйвера GPIO. Час наростання фронту оцінюється як:

```
t_rise ≈ 2.2 · R_out · C_total
```

При вихідному опорі піна `R_out ≈ 30 Ом` та сумарній ємності траси `C_total ≈ 25 пФ`, час наростання становить `t_rise ≈ 1.65 нс`, що повністю задовольняє вимогам високошвидкісного зчитування 24 МГц.

## Часове розділення спільної шини (Time-Division Multiplexing)

Коли через обмеження площі друкованої плати кілька різнорідних давачів (швидкий IMU 1 кГц, магнітометр 100 Гц та барометр 50 Гц) змушені сидіти на одній фізичній шині SPI зі спільними лініями SCK, MISO, MOSI, пряме накладання їхніх переривань DRDY спричинить колізію шини.

Для впорядкування доступу застосовують розклад із часовим розділенням слотів (TDM):
1. Кожен мілісекундний інтервал таймера TRGO ділиться на три суб-фази:
   - `0.0 – 0.3 мс:` транзакція DMA швидкого IMU (пріоритет 1).
   - `0.4 – 0.6 мс:` опитування магнітометра (активне лише кожен 10-й мілісекундний такт).
   - `0.7 – 0.9 мс:` опитування барометра (активне лише кожен 20-й такт).
2. Завдяки такому жорсткому рознесенню транзакцій у часі лінія Chip Select кожного приладу активується без ризику колізії або затримки DMA іншого сенсора.

## Векторизована нормалізація вибірок (SI Unit Scaling)

Зчитані цілочисельні 16-бітні значення мають бути перетворені у фізичні величини міжнародної системи одиниць (радіани за секунду та метри за секунду у квадраті).

На ядрах ARM Cortex-M4/M7 із підтримкою SIMD та FPU операція масштабування виконується за один такт за допомогою векторних інструкцій обчислення з плаваючою комою:

```
accel_mps2 = raw_accel * (accel_scale_factor * 9.80665f / 32768.0f)
gyro_radps  = raw_gyro  * (gyro_scale_factor  * (PI / 180.0f) / 32768.0f)
```

Завдяки перенесенню цих обчислень у робочий потік обробки векторів система гарантує, що час між отриманням кадру DMA та готовністю фізичного вектора для фільтра EKF становить менше 2.5 мікросекунди. Застосування апаратних векторних операцій звільняє до 85 % часу процесора для складних матричних перетворень фільтра навігації.

## Профіль енергоспоживання: опитування проти DMA зі сном (WFI)

У малопотужних робототехнічних платформах та автономних сенсорних маяках критичним показником є струм споживання мікроконтролера.

Порівняння двох підходів показує колосальну різницю:
1. **Програмне опитування (Active Polling):** ядро процесора постійно працює на максимальній частоті 168 МГц, споживаючи близько 55–65 мА. Процесор очікує готовності прапорців шини в холостих циклах (*spin-lock*).
2. **Апаратний конвеєр DMA + режим WFI (*Wait For Interrupt*):** ядро налаштовує таймер TRGO та канали DMA, після чого переходить у режим сну Sleep Mode командою `__WFI()`. Споживання мікроконтролера падає до 10–14 мА. Процесор прокидається лише на 15 мкс раз на мілісекунду для виконання швидкого кроку фільтра Калмана.

Середнє енергоспоживання обчислювального блоку зменшується на 75–80 %, що критично подовжує час автономної роботи пристрою. У мобільних батарейних платформах це дозволяє збільшити час активного польоту на 15–20 хвилин без збільшення ваги акумулятора.

## Апаратна перевірка контрольних сум CRC для захисту від збоїв

У зашумлених силових системах (високовольтні інвертори моторів) імпульсні наводки на шину SPI можуть спотворювати окремі біти даних. Сучасні сенсори підтримують апаратний розрахунок полінома CRC8 або CRC16 на кожному зчитаному пакеті.

Мікроконтролер розраховує контрольну суму паралельно з передачею DMA або у фінальному обробнику кадру. Якщо розрахована сума не збігається з контрольним байтом у хвості пакета, кадр негайно відкидається, прапорець `status_flags` фіксує помилку шини, а фільтр орієнтації тимчасово продовжує роботу в режимі екстраполяції без прийняття пошкодженого відліку. Це захищає алгоритм синтезу станів від руйнівних сплесків та фазових розривів.

## Аналіз затримок шини та арбітражу пам'яті

Щоб зрозуміти, чому прямий доступ до пам'яті перевершує звичайні обробники переривань, проаналізуємо рух байтів на рівні шинної матриці (*Bus Matrix*) мікроконтролера.

У мікроконтролерах сімейства STM32F4/F7/H7 периферійні контролери SPI та контролери DMA підключені до багатошарової комутаційної матриці AHB (*Advanced High-performance Bus*). Коли ядро виконує інструкції з флеш-пам'яті або пам'яті TCM (*Tightly Coupled Memory*), шини інструкцій (I-Bus) та шини даних (D-Bus) працюють паралельно з шинами доступу DMA до внутрішньої SRAM.

Коли приходить запит від передавача SPI, контролер DMA виконує два цикли передачі:
1. Зчитування одного байта з регістру даних `SPI->DR` через периферійний міст APB-AHB.
2. Запис байта в масив SRAM за адресою `M0AR` з автоматичним автоінкрементом адреси.

Обидва цикли займають близько 4–6 тактів системної шини AHB (приблизно 25–35 нс при частоті 168 МГц). Весь 14-байтний пакет переноситься в пам'ять за 5.6 мкс при швидкості SPI 20 МГц, і протягом усього цього інтервалу процесор не витрачає жодного такту на обслуговування шини, продовжуючи виконувати обчислення фільтра EKF.

### Захист пам'яті через блок MPU

У системах на ядрах ARM Cortex-M7 (наприклад, STM32H753) внутрішня пам'ять SRAM1/SRAM2 охоплена кешем першого рівня L1 Data Cache. Якщо дескриптор буфера DMA розташовано у кешованій області пам'яті за замовчуванням, ядро та контролер DMA бачитимуть різні копії пам'яті: контролер DMA оновить фізичну комірку в SRAM, а ядро під час читання візьме застарілий байт із L1-кешу.

Найбільш надійним апаратним рішенням цієї проблеми є конфігурація окремого регіону блоку захисту пам'яті MPU (*Memory Protection Unit*), який оголошує область буферів DMA некешованою (*Non-Cacheable, Normal Memory*):

:::tabs
```c
/* Налаштування регіону MPU для некешованого буфера DMA */
void mpu_setup_dma_buffers(void) {
    /* Вимикаємо MPU перед конфігурацією */
    MPU->CTRL = 0;

    /* Вибираємо регіон 0 для буферів сенсорної шини */
    MPU->RNR = 0;
    MPU->RBAR = (uint32_t)g_spi1_rx_dma_buf & MPU_RBAR_ADDR_Msk;
    MPU->RASR = (0 << MPU_RASR_XN_Pos)   |  /* Дозвіл виконання (не має значення) */
                (3 << MPU_RASR_AP_Pos)   |  /* Повний доступ (Read/Write) */
                (0 << MPU_RASR_TEX_Pos)  |  /* TEX=001, C=0, B=0: Normal Non-Cacheable */
                (1 << MPU_RASR_C_Pos)    |
                (0 << MPU_RASR_B_Pos)    |
                (0 << MPU_RASR_S_Pos)    |  /* Not Shareable */
                (5 << MPU_RASR_SIZE_Pos) |  /* Розмір регіону 64 байти (2^(5+1)) */
                (1 << MPU_RASR_ENABLE_Pos);

    /* Вмикаємо MPU з дозволом фонового простору */
    MPU->CTRL = MPU_CTRL_ENABLE_Msk | MPU_CTRL_PRIVDEFENA_Msk;
    __DSB();
    __ISB();
}
```
```cpp
namespace hardware {

struct MpuConfiguration {
    static constexpr std::uint32_t RegionSize64Bytes = 5; // 2^(5+1) = 64

    static void configure_noncacheable_region(void* base_address) noexcept {
        MPU->CTRL = 0;
        MPU->RNR = 0;
        MPU->RBAR = reinterpret_cast<std::uint32_t>(base_address) & MPU_RBAR_ADDR_Msk;
        MPU->RASR = (3 << MPU_RASR_AP_Pos) |
                    (1 << MPU_RASR_C_Pos)  |
                    (RegionSize64Bytes << MPU_RASR_SIZE_Pos) |
                    (1 << MPU_RASR_ENABLE_Pos);

        MPU->CTRL = MPU_CTRL_ENABLE_Msk | MPU_CTRL_PRIVDEFENA_Msk;
        __DSB();
        __ISB();
    }
};

} // namespace hardware
```
:::

## Інженерні пастки та крайові випадки

1. **Когерентність кешу даних (D-Cache Coherency на ARM Cortex-M7):**
   Якщо блок MPU не використовується, перед кожним зверненням ядра до результатів передачі DMA необхідно викликати функцію інвалідації кешу за адресою буфера, причому розмір буфера має бути вирівняний за розміром кеш-лінії (32 байти):

:::tabs
```c
/* Очищення та інвалідація кешу для діапазону адреси DMA */
SCB_InvalidateDCache_by_Addr((uint32_t*)g_spi1_rx_dma_buf, IMU_PACKET_SIZE);
```
```cpp
namespace memory {

struct CacheManager {
    static void invalidate_buffer(const void* address, std::size_t size_bytes) noexcept {
        SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(const_cast<void*>(address)),
                                     static_cast<std::int32_t>(size_bytes));
    }
};

} // namespace memory
```
:::

2. **Час утримання сигналу вибору мікросхеми (SPI CS Hold Time):**
   У багатьох сучасних MEMS-давачах (наприклад, TDK InvenSense ICM-42688-P) лінія CS після завершення останнього такту `SCK` повинна залишатися в нулі щонайменше 20–50 нс (*CS Hold Time*). Якщо підняти пін CS занадто швидко прямо в обробнику завершення DMA передачі, останній байт у регістрі зсуву давача може бути спотворений. Слід перевіряти прапорець зайнятості шини `SPI_SR_BSY` перед встановленням CS у високий рівень.

3. **Переповнення черги FIFO давача (FIFO Overflow):**
   Якщо шина заблокована іншою транзакцією або виникла затримка DMA, внутрішня черга FIFO давача переповнюється. У такому разі нові дані або відкидаються, або перезаписують старі зі зсувом вказівника пакета. У прошивці слід перевіряти біт статусу переповнення у заголовку кадру й у разі збою скидати буфер командою `FIFO_RESET`.

4. **Джиттер фронту лінії DRDY через брязкіт живлення:**
   При різких стрибках споживання струму силовими моторами цифрові шуми на шині живлення можуть спричиняти помилкові перепади на вході EXTI. Для придушення таких хибних тригерів у мікроконтролерах вмикають вхідні цифрові фільтри GPIO (*Input Filter*) або налаштовують фільтр захоплення таймера `TIMx_CCMR1_IC1F` на 4–8 тактів стабільності вхідного рівня.

5. **Методологія верифікації на логічному аналізаторі:**
   Для точного вимірювання затримок конвеєра виділяють тестові піни GPIO (Debug Pins), якими маніпулюють у ключових точках програми:
   - Пін 1 перемикається при старті таймера TRGO.
   - Пін 2 перемикається у першому рядку обробника EXTI DRDY.
   - Пін 3 перемикається в обробнику завершення DMA.

   На екрані логічного аналізатора вимірюють інтервал між наростаючим фронтом DRDY та початком тактової серії SCK. Для апаратного таймерного конвеєра цей час становить сталі 1.2–1.8 мкс, тоді як при чисто програмному опитуванні спостерігається неконтрольоване тремтіння від 50 мкс до 1.5 мс.

6. **Аварійне розблокування завислої шини I2C (Bus Lockup Recovery):**
   Якщо під час передачі живлення мікроконтролера перезавантажилося або стався збій, ведений прилад I2C (магнітометр чи барометр) може залишитися в стані утримання лінії `SDA` в нулі. Контролер I2C не зможе сформувати умову START. Для відновлення прошивка тимчасово конфігурує піни `SCL` та `SDA` як звичайні GPIO з відкритим стоком і генерує 9 імпульсів тактування на лінії `SCL`, змушуючи ведений прилад відпустити `SDA`:

:::tabs
```c
/* Програмне розблокування лінії SDA шини I2C */
void i2c_bus_unlock_recovery(GPIO_TypeDef* port, uint16_t scl_pin, uint16_t sda_pin) {
    /* Генеруємо 9 тактів на SCL при відпущеній лінії SDA */
    for (int i = 0; i < 9; i++) {
        port->BSRR = (1U << (scl_pin + 16)); /* SCL = LOW */
        for (volatile int d = 0; d < 50; d++);
        port->BSRR = (1U << scl_pin);        /* SCL = HIGH */
        for (volatile int d = 0; d < 50; d++);
    }
}
```
```cpp
namespace hardware {

struct I2cBusRecovery {
    static void clear_bus_lockup(GPIO_TypeDef* port, std::uint16_t scl_pin) noexcept {
        for (std::size_t i = 0; i < 9; ++i) {
            port->BSRR = static_cast<std::uint32_t>(1U << (scl_pin + 16));
            for (volatile int d = 0; d < 50; ++d) {}
            port->BSRR = static_cast<std::uint32_t>(1U << scl_pin);
            for (volatile int d = 0; d < 50; ++d) {}
        }
    }
};

} // namespace hardware
```
:::

Завдяки поєднанню апаратного тактування таймера TRGO, прямого DMA-перенесення пакетів у SRAM та апаратного замикання міток часу лінія зчитування сенсорної матриці працює як детермінований цифровий конвеєр без джиттера, забезпечуючи найвищу якість первинних даних для фільтрів просторової навігації.
