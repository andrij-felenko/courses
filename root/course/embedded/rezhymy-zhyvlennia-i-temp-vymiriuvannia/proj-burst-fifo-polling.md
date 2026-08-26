# ⚙️ Пакетне зчитування буфера FIFO давача з апаратним перериванням

Використання вбудованого апаратного буфера FIFO (First-In, First-Out) цифрового давача дозволяє розвантажити хост-контролер від необхідності прокидатися на кожен окремий відлік АЦП. Мікроконтролер налаштовує поріг заповнення буфера (Watermark), переходить у глибокий сон (Stop Mode) і прокидається лише тоді, коли давач накопичить пачку вимірювань і виставить апаратне переривання на лінії INT.

Нижче наведено практичну реалізацію драйвера пакетного зчитування FIFO для 3-осьового акселерометра / барометра по шині SPI з використанням прямого доступу до пам'яті (DMA), детальний аналіз енергетичних переходів ядра та алгоритм обробки позаштатних ситуацій на шині.

---

## 1. Архітектура взаємодії та часовий розподіл

У класичній архітектурі опитування давача за сигналом готовності даних (Data Ready, DRDY) хост-контролер прокидається на кожен зразок. Якщо частота вибірки становить 100 Гц, ядро зазнає 100 циклів переходу «сон → робота → сон» за секунду. Кожен такий перехід супроводжується затримкою розгону тактового генератора (HSE або внутрішнього HSI), перезапуском системи фазового автопідстроювання частоти (PLL) та очікуванням стабілізації напруги внутрішнього стабілізатора живлення ядра.

Використання апаратного буфера FIFO докорінно змінює часовий розподіл:

```
Часова шкала взаємодії (FIFO Watermark = 32):

t = 0 мс             t = 10 мс            t = 20 мс            t = 320 мс
  │                    │                    │                    │
  ▼                    ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────┬────────────────┐
│             Давач накопичує відліки у FIFO (100 Гц)          │ INT1 активний  │
│             Мікроконтролер: STOP 2 Mode (1.2 мкА)            │ МК: Burst DMA  │
└──────────────────────────────────────────────────────────────┴────────────────┘
                                                                 ▲
                                                                 └── 1.5 мс обробки
```

1. **Ініціалізація давача:** Налаштовується частота видачі даних (ODR = 100 Гц), режим роботи FIFO (Stream Mode) та поріг переривання Watermark = 32 кадри.
2. **Вхід у глибокий сон:** Головний цикл переводить периферію МК у режим низького енергоспоживання, вимикає тактування ядра та більшості периферійних блоків, викликаючи інструкцію очікування переривання WFI (Wait For Interrupt).
3. **Автономне накопичення в чипі:** Давач самостійно здійснює вибірку кожні 10 мс і записує 6-байтові кадри (координати X, Y, Z по 16 біт кожна) у внутрішню статичну пам'ять (SRAM).
4. **Апаратний тригер:** Після запису 32-го кадру внутрішній лічильник порівнюється з пороговим регістром, і лінія INT1 переходить у високий рівень, генеруючи асинхронний фронт для модуля EXTI мікроконтролера.
5. **Пакетний Burst Read:** МК прокидається, за один сеанс активності лінії вибору кристала (Chip Select) активує вичитування 192 байтів через DMA, обробляє весь масив даних у швидкому режимі та миттєво повертається в режим сну.

---

## 2. Реалізація драйвера пакетного вичитування

Драйвер використовує циклічний обмін SPI через DMA. Перший байт транзакції містить адресу початкового регістру даних `REG_FIFO_DATA_OUT` зі встановленими прапорцями читання (`0x80`) та автоінкременту адреси (`0x40`). Далі контролер DMA тактує шину, одночасно надсилаючи нульові байти та зберігаючи прийняті байти в буфер пам'яті.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "stm32l4xx_hal.h"

#define SENSOR_FIFO_WATERMARK    32
#define SENSOR_FRAME_SIZE        6   /* 2 байти на кожну з осей X, Y, Z */
#define SENSOR_BURST_BUFFER_SIZE (SENSOR_FIFO_WATERMARK * SENSOR_FRAME_SIZE)

#define REG_FIFO_CTRL            0x2E
#define REG_FIFO_SRC             0x2F
#define REG_FIFO_DATA_OUT        0x28
#define REG_INT1_CTRL            0x22
#define REG_CTRL_REG1            0x20

#define SPI_READ_BIT             0x80
#define SPI_AUTO_INCR_BIT        0x40

typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} SensorSample;

typedef struct {
    SPI_HandleTypeDef *hspi;
    GPIO_TypeDef *cs_port;
    uint16_t cs_pin;
    volatile bool data_ready_flag;
    uint8_t rx_raw_buffer[SENSOR_BURST_BUFFER_SIZE + 1];
    uint8_t tx_dummy_buffer[SENSOR_BURST_BUFFER_SIZE + 1];
    SensorSample parsed_samples[SENSOR_FIFO_WATERMARK];
} SensorFifoDriver;

static inline void sensor_cs_low(SensorFifoDriver *dev) {
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_RESET);
}

static inline void sensor_cs_high(SensorFifoDriver *dev) {
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_SET);
}

HAL_StatusTypeDef sensor_write_reg(SensorFifoDriver *dev, uint8_t reg, uint8_t val) {
    uint8_t tx[2] = { reg & ~SPI_READ_BIT, val };
    sensor_cs_low(dev);
    HAL_StatusTypeDef status = HAL_SPI_Transmit(dev->hspi, tx, 2, HAL_MAX_DELAY);
    sensor_cs_high(dev);
    return status;
}

HAL_StatusTypeDef sensor_read_reg(SensorFifoDriver *dev, uint8_t reg, uint8_t *val) {
    uint8_t tx[2] = { reg | SPI_READ_BIT, 0x00 };
    uint8_t rx[2] = { 0 };
    sensor_cs_low(dev);
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(dev->hspi, tx, rx, 2, HAL_MAX_DELAY);
    sensor_cs_high(dev);
    if (status == HAL_OK) {
        *val = rx[1];
    }
    return status;
}

HAL_StatusTypeDef sensor_fifo_init(SensorFifoDriver *dev) {
    /* 1. Налаштування порогу Watermark (32 кадри) у режимі Stream */
    /* FIFO_CTRL: Mode = Stream (0b01000000), FTH = 31 (0b00011111) */
    if (sensor_write_reg(dev, REG_FIFO_CTRL, 0x5F) != HAL_OK) return HAL_ERROR;

    /* 2. Прив'язка переривання Watermark до фізичного виводу INT1 */
    if (sensor_write_reg(dev, REG_INT1_CTRL, 0x08) != HAL_OK) return HAL_ERROR;

    /* 3. Увімкнення вимірювань: ODR = 100 Гц, усі 3 осі активні */
    if (sensor_write_reg(dev, REG_CTRL_REG1, 0x57) != HAL_OK) return HAL_ERROR;

    dev->data_ready_flag = false;
    memset(dev->tx_dummy_buffer, 0x00, sizeof(dev->tx_dummy_buffer));
    /* Перший байт передачі — адреса початкового регістру з бітами читання та автоінкременту */
    dev->tx_dummy_buffer[0] = REG_FIFO_DATA_OUT | SPI_READ_BIT | SPI_AUTO_INCR_BIT;

    return HAL_OK;
}

/* Викликається з обробника зовнішнього переривання EXTI */
void sensor_on_watermark_isr(SensorFifoDriver *dev) {
    dev->data_ready_flag = true;
}

bool sensor_fetch_fifo_burst(SensorFifoDriver *dev) {
    if (!dev->data_ready_flag) return false;

    uint8_t fifo_status = 0;
    if (sensor_read_reg(dev, REG_FIFO_SRC, &fifo_status) != HAL_OK) {
        return false;
    }

    /* Перевірка чи досягнуто порогу Watermark (біт 7) */
    if (!(fifo_status & 0x80)) {
        dev->data_ready_flag = false;
        return false;
    }

    /* Пакетне зчитування 192 байтів через SPI DMA */
    sensor_cs_low(dev);
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive_DMA(
        dev->hspi,
        dev->tx_dummy_buffer,
        dev->rx_raw_buffer,
        sizeof(dev->rx_raw_buffer)
    );

    if (status != HAL_OK) {
        sensor_cs_high(dev);
        return false;
    }

    return true;
}

void sensor_on_dma_complete(SensorFifoDriver *dev) {
    sensor_cs_high(dev);
    dev->data_ready_flag = false;

    /* Розбір отриманого байтового потоку у масив 16-бітних зразків */
    const uint8_t *raw = &dev->rx_raw_buffer[1]; /* Пропускаємо dummy-байт адреси */
    for (size_t i = 0; i < SENSOR_FIFO_WATERMARK; ++i) {
        size_t offset = i * SENSOR_FRAME_SIZE;
        dev->parsed_samples[i].x = (int16_t)((uint16_t)raw[offset + 0] | ((uint16_t)raw[offset + 1] << 8));
        dev->parsed_samples[i].y = (int16_t)((uint16_t)raw[offset + 2] | ((uint16_t)raw[offset + 3] << 8));
        dev->parsed_samples[i].z = (int16_t)((uint16_t)raw[offset + 4] | ((uint16_t)raw[offset + 5] << 8));
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include "stm32l4xx_hal.h"

enum class DriverError {
    BusError,
    Timeout,
    FifoNotReady,
    DmaError
};

struct SensorSample {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
};

template <size_t WatermarkSize = 32>
class FifoSensorDriver {
public:
    static constexpr size_t FrameSize = 6;
    static constexpr size_t BurstSize = WatermarkSize * FrameSize;

    FifoSensorDriver(SPI_HandleTypeDef& hspi, GPIO_TypeDef* cs_port, uint16_t cs_pin)
        : m_hspi(hspi), m_cs_port(cs_port), m_cs_pin(cs_pin) {
        m_tx_cmd_buffer.fill(0x00);
        m_tx_cmd_buffer[0] = RegFifoDataOut | SpiReadBit | SpiAutoIncrBit;
    }

    std::expected<void, DriverError> init() {
        /* Режим FIFO Stream + поріг 32 зразки */
        if (!writeRegister(RegFifoCtrl, 0x5F)) return std::unexpected(DriverError::BusError);
        /* Переривання Watermark на пін INT1 */
        if (!writeRegister(RegInt1Ctrl, 0x08)) return std::unexpected(DriverError::BusError);
        /* Запуск перетворень: 100 Гц ODR */
        if (!writeRegister(RegCtrlReg1, 0x57)) return std::unexpected(DriverError::BusError);

        m_data_ready = false;
        return {};
    }

    void onInterrupt() noexcept {
        m_data_ready = true;
    }

    std::expected<void, DriverError> startBurstReadDma() {
        if (!m_data_ready) {
            return std::unexpected(DriverError::FifoNotReady);
        }

        auto status = readRegister(RegFifoSrc);
        if (!status.has_value() || !(status.value() & 0x80)) {
            m_data_ready = false;
            return std::unexpected(DriverError::FifoNotReady);
        }

        setCs(false);
        HAL_StatusTypeDef hal_stat = HAL_SPI_TransmitReceive_DMA(
            &m_hspi,
            m_tx_cmd_buffer.data(),
            m_rx_raw_buffer.data(),
            static_cast<uint16_t>(m_rx_raw_buffer.size())
        );

        if (hal_stat != HAL_OK) {
            setCs(true);
            return std::unexpected(DriverError::DmaError);
        }

        return {};
    }

    void onDmaComplete() noexcept {
        setCs(true);
        m_data_ready = false;

        const uint8_t* raw = &m_rx_raw_buffer[1];
        for (size_t i = 0; i < WatermarkSize; ++i) {
            size_t offset = i * FrameSize;
            m_samples[i].x = static_cast<int16_t>(static_cast<uint16_t>(raw[offset + 0]) | 
                                                  (static_cast<uint16_t>(raw[offset + 1]) << 8));
            m_samples[i].y = static_cast<int16_t>(static_cast<uint16_t>(raw[offset + 2]) | 
                                                  (static_cast<uint16_t>(raw[offset + 3]) << 8));
            m_samples[i].z = static_cast<int16_t>(static_cast<uint16_t>(raw[offset + 4]) | 
                                                  (static_cast<uint16_t>(raw[offset + 5]) << 8));
        }
    }

    [[nodiscard]] std::span<const SensorSample, WatermarkSize> samples() const noexcept {
        return m_samples;
    }

private:
    static constexpr uint8_t RegCtrlReg1     = 0x20;
    static constexpr uint8_t RegInt1Ctrl     = 0x22;
    static constexpr uint8_t RegFifoDataOut  = 0x28;
    static constexpr uint8_t RegFifoCtrl     = 0x2E;
    static constexpr uint8_t RegFifoSrc      = 0x2F;

    static constexpr uint8_t SpiReadBit      = 0x80;
    static constexpr uint8_t SpiAutoIncrBit  = 0x40;

    void setCs(bool level) const noexcept {
        HAL_GPIO_WritePin(m_cs_port, m_cs_pin, level ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }

    bool writeRegister(uint8_t reg, uint8_t val) const noexcept {
        uint8_t tx[2] = { static_cast<uint8_t>(reg & ~SpiReadBit), val };
        setCs(false);
        bool ok = (HAL_SPI_Transmit(&m_hspi, tx, 2, HAL_MAX_DELAY) == HAL_OK);
        setCs(true);
        return ok;
    }

    std::expected<uint8_t, DriverError> readRegister(uint8_t reg) const noexcept {
        uint8_t tx[2] = { static_cast<uint8_t>(reg | SpiReadBit), 0x00 };
        uint8_t rx[2] = { 0 };
        setCs(false);
        HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(&m_hspi, tx, rx, 2, HAL_MAX_DELAY);
        setCs(true);
        if (status != HAL_OK) return std::unexpected(DriverError::BusError);
        return rx[1];
    }

    SPI_HandleTypeDef& m_hspi;
    GPIO_TypeDef* m_cs_port;
    uint16_t m_cs_pin;
    volatile bool m_data_ready{false};

    alignas(4) std::array<uint8_t, BurstSize + 1> m_tx_cmd_buffer{};
    alignas(4) std::array<uint8_t, BurstSize + 1> m_rx_raw_buffer{};
    std::array<SensorSample, WatermarkSize> m_samples{};
};
```
:::

---

## 3. Організація енергоощадного циклу в `main()`

В основній програмі мікроконтролер конфігурує переривання EXTI від піна INT1 давача, ініціалізує драйвер та переходить у багаторівневий цикл сну:
1. Коли прапорець `data_ready_flag` встановлено, процесор ініціює передачу через DMA.
2. Під час роботи каналу DMA ядро переводиться у режим **Sleep Mode** (ядро зупинено, тактування шин AHB/APB та оперативної пам'яті активно). У цьому режимі струм ядра знижується до 1–2 мА замість 8–10 мА у режимі активного виконання коду.
3. Коли DMA завершує вичитування 192 байтів, викликається переривання `HAL_SPI_TxRxCpltCallback`, де піднімається лінія Chip Select і виконується швидкий розбір координат.
4. Після обробки буфера мікроконтролер переходить у надглибокий **Stop 2 Mode**, у якому струм падає до **1.2–1.5 мкА**, а тактові генератори повністю вимикаються до наступного імпульсу Watermark через 320 мс.

:::tabs
```c
extern SensorFifoDriver g_sensor;
volatile bool g_dma_in_progress = false;

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == SENSOR_INT1_PIN) {
        sensor_on_watermark_isr(&g_sensor);
    }
}

void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi == g_sensor.hspi) {
        sensor_on_dma_complete(&g_sensor);
        g_dma_in_progress = false;
    }
}

void enter_system_low_power_loop(void) {
    sensor_fifo_init(&g_sensor);

    while (1) {
        /* 1. Запуск вичитування якщо прийшов тригер Watermark */
        if (g_sensor.data_ready_flag && !g_dma_in_progress) {
            g_dma_in_progress = true;
            if (!sensor_fetch_fifo_burst(&g_sensor)) {
                g_dma_in_progress = false;
            }
        }

        /* 2. Якщо триває передача DMA, чекаємо у режимі Sleep (ядро зупинено, DMA активний) */
        if (g_dma_in_progress) {
            HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
        } else {
            /* 3. Якщо передачу завершено — переходимо в глибокий Stop Mode */
            /* Пробудження відбудеться лише при наступному імпульсі Watermark на лінії EXTI */
            HAL_PWREx_EnterSTOP2Mode(PWR_STOPENTRY_WFI);
        }
    }
}
```
```cpp
extern FifoSensorDriver<32> g_sensor;
volatile bool g_dma_active = false;

extern "C" void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin == SENSOR_INT1_PIN) {
        g_sensor.onInterrupt();
    }
}

extern "C" void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef* hspi) {
    g_sensor.onDmaComplete();
    g_dma_active = false;
}

void runEventLoop() {
    auto init_res = g_sensor.init();
    if (!init_res.has_value()) {
        /* Обробка апаратної помилки ініціалізації */
        return;
    }

    while (true) {
        if (!g_dma_active) {
            auto burst_res = g_sensor.startBurstReadDma();
            if (burst_res.has_value()) {
                g_dma_active = true;
            }
        }

        if (g_dma_active) {
            /* DMA вичитує шину: ядро спить у Sleep Mode (RAM + периферія активні) */
            HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
        } else {
            /* Буфер оброблено: глибокий Stop 2 Mode до наступного переривання Watermark */
            HAL_PWREx_EnterSTOP2Mode(PWR_STOPENTRY_WFI);
        }
    }
}
```
:::

---

## 4. Підводні камені, крайові випадки та діагностика

Під час розробки та налагодження пакетного зчитування FIFO розробник стикається з кількома типовими апаратними пастками:

1. **Переповнення буфера (FIFO Overrun):** Якщо обробка попереднього пакета або інші високопріоритетні переривання затримали вичитування на понад 10 мс, у буфер надійде 33-й відлік.
   * У режимі *Stream Mode* найновіший кадр перезапише найстаріший. При цьому лічильник незчитаних семплів залишиться рівним 32, але часова прив'язка першого зразка зсунеться на один крок ODR (10 мс).
   * У режимі *FIFO Mode* чип виставить біт переповнення `OVRN` у регістрі `REG_FIFO_SRC` та припинить оновлення пам'яті. Щоб відновити роботу, прошивка повинна скинути режим FIFO, виставивши `FIFO_MODE = 0b000` (Bypass), а потім знову повернути `0b001` (FIFO Mode).
2. **Вирівнювання пам'яті для контролера DMA:** Буфери прийому та передачі мають бути вирівняні за 32-бітною межею (`alignas(4)` або `__attribute__((aligned(4)))`). У мікроконтролерах із розділеними шинами пам'яті розміщення буфера у вимкненій під час сну ділянці RAM (наприклад, SRAM2) призведе до зависання контролера DMA або генерації винятку HardFault.
3. **Хибні спрацьовування та завади на лінії переривання (Spurious EXTI Glitches):** Ємнісні наведенки від ліній SPI під час швидкісного обміну можуть викликати хибні фронти на сусідній лінії INT1. Обов'язкове читання регістру статусу `REG_FIFO_SRC` перед запуском DMA захищає від вичитування порожнього буфера.
4. **Простеження логічним аналізатором:**
   * Канал 0 (`CS`): має опускатися в низький рівень рівно один раз на 320 мс і залишатися внизу протягом ~250 мкс на всі 193 байти.
   * Канал 1 (`SCK`): неперервна серія з 193 байтових пачок тактових імпульсів на частоті 8 МГц.
   * Канал 2 (`INT1`): чіткий наростаючий фронт кожні 320 мс, який скидається в низький рівень після читання першого байта статусу або очищення фіксатора.
