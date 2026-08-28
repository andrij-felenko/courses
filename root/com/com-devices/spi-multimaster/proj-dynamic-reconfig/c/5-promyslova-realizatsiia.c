#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Режими тактування шини SPI
typedef enum {
    SPI_CLOCK_MODE_0 = 0, // CPOL = 0, CPHA = 0 (спокій низький, вибірка по наростанню)
    SPI_CLOCK_MODE_1 = 1, // CPOL = 0, CPHA = 1 (спокій низький, вибірка по спаданню)
    SPI_CLOCK_MODE_2 = 2, // CPOL = 1, CPHA = 0 (спокій високий, вибірка по спаданню)
    SPI_CLOCK_MODE_3 = 3  // CPOL = 1, CPHA = 1 (спокій високий, вибірка по наростанню)
} spi_clock_mode_t;

// Порядок передачі розрядів
typedef enum {
    SPI_BIT_ORDER_MSB_FIRST = 0,
    SPI_BIT_ORDER_LSB_FIRST = 1
} spi_bit_order_t;

// Статуси виконання транзакцій
typedef enum {
    SPI_STATUS_OK = 0,
    SPI_STATUS_INVALID_ARG,
    SPI_STATUS_MODE_FAULT,
    SPI_STATUS_TIMEOUT,
    SPI_STATUS_BUSY
} spi_status_t;

// Конфігураційний профіль конкретного веденого пристрою
typedef struct {
    uint32_t         baudrate_hz;    // Бажана тактова частота (Гц)
    spi_clock_mode_t clock_mode;     // Режим фази та полярності (Mode 0..3)
    spi_bit_order_t  bit_order;      // Порядок бітів (MSB / LSB)
    uint8_t          cs_port_id;     // Ідентифікатор порту GPIO
    uint8_t          cs_pin_num;     // Номер виводу GPIO
    uint16_t         lead_delay_us;  // Захисний інтервал t_lead (мкс)
    uint16_t         lag_delay_us;   // Захисний інтервал t_lag (мкс)
    uint16_t         settle_delay_us;// Захисний інтервал t_settle (мкс)
} spi_slave_config_t;

// Апаратний дескриптор шини SPI
typedef struct {
    volatile uint32_t* CR1;          // Регістр керування 1
    volatile uint32_t* CR2;          // Регістр керування 2
    volatile uint32_t* SR;           // Регістр статусу
    volatile uint32_t* DR;           // Регістр даних
    uint32_t           bus_clock_hz; // Базова частота тактування шини (APB)
    bool               mode_fault_flag;
} spi_bus_hw_t;

// Бітові маски регістрів SPI (стандартна архітектура Cortex-M)
#define SPI_CR1_SPE        (1u << 6)  // SPI Enable (дозвіл роботи)
#define SPI_CR1_MSTR       (1u << 2)  // Master Selection (режим ведучого)
#define SPI_CR1_CPOL       (1u << 1)  // Clock Polarity (полярність спокою)
#define SPI_CR1_CPHA       (1u << 0)  // Clock Phase (фаза вибірки)
#define SPI_CR1_LSBFIRST   (1u << 7)  // Frame Format (LSB/MSB)
#define SPI_CR1_BR_MASK    (7u << 3)  // Маска бітів дільника Baud Rate

#define SPI_SR_TXE         (1u << 1)  // Transmit Buffer Empty (буфер передачі порожній)
#define SPI_SR_RXNE        (1u << 0)  // Receive Buffer Not Empty (прийнято байт)
#define SPI_SR_BSY         (1u << 7)  // Busy Flag (шина зайнята обміном)
#define SPI_SR_MODF        (1u << 5)  // Mode Fault Flag (помилка колізії)

// Апаратні зовнішні виклики (HAL / Board Support Package)
extern void gpio_write_pin(uint8_t port, uint8_t pin, bool level);
extern void delay_microseconds(uint32_t us);
extern void spi_mutex_lock(void);
extern void spi_mutex_unlock(void);

// Розрахунок дільника частоти Baud Rate Prescaler
static uint32_t spi_calc_prescaler(uint32_t bus_clk, uint32_t target_baud)
{
    uint32_t div = bus_clk / target_baud;
    if (div <= 2)   return (0u << 3); // Дільник /2
    if (div <= 4)   return (1u << 3); // Дільник /4
    if (div <= 8)   return (2u << 3); // Дільник /8
    if (div <= 16)  return (3u << 3); // Дільник /16
    if (div <= 32)  return (4u << 3); // Дільник /32
    if (div <= 64)  return (5u << 3); // Дільник /64
    if (div <= 128) return (6u << 3); // Дільник /128
    return (7u << 3);                 // Дільник /256
}

// Безпечна динамічна реконфігурація регістрів
static spi_status_t spi_reconfigure(spi_bus_hw_t* bus, const spi_slave_config_t* cfg)
{
    // 1. Перевірка прапорця Mode Fault від попередніх операцій
    if (*(bus->SR) & SPI_SR_MODF) {
        // Очищення MODF: читання регістра SR з наступним записом CR1
        volatile uint32_t dummy = *(bus->SR);
        (void)dummy;
        *(bus->CR1) |= SPI_CR1_MSTR; // Відновлення біта ведучого
        bus->mode_fault_flag = true;
        return SPI_STATUS_MODE_FAULT;
    }

    // 2. Очікування повного звільнення апаратного зсувного регістра
    uint32_t timeout = 100000;
    while ((*(bus->SR) & SPI_SR_BSY) && (--timeout > 0));
    if (timeout == 0) {
        return SPI_STATUS_TIMEOUT;
    }

    // 3. Тимчасове вимкнення модуля SPI для розблокування регістрів
    *(bus->CR1) &= ~SPI_CR1_SPE;

    // 4. Формування нового значення конфігураційного слова CR1
    uint32_t cr1_val = *(bus->CR1);
    cr1_val &= ~(SPI_CR1_CPOL | SPI_CR1_CPHA | SPI_CR1_LSBFIRST | SPI_CR1_BR_MASK);

    // Встановлення полярності та фази
    if (cfg->clock_mode == SPI_CLOCK_MODE_2 || cfg->clock_mode == SPI_CLOCK_MODE_3) {
        cr1_val |= SPI_CR1_CPOL;
    }
    if (cfg->clock_mode == SPI_CLOCK_MODE_1 || cfg->clock_mode == SPI_CLOCK_MODE_3) {
        cr1_val |= SPI_CR1_CPHA;
    }

    // Встановлення порядку бітів
    if (cfg->bit_order == SPI_BIT_ORDER_LSB_FIRST) {
        cr1_val |= SPI_CR1_LSBFIRST;
    }

    // Встановлення швидкості тактування
    cr1_val |= spi_calc_prescaler(bus->bus_clock_hz, cfg->baudrate_hz);
    cr1_val |= SPI_CR1_MSTR; // Завжди ведучий

    // 5. Запис конфігурації та повторне увімкнення блоку SPI
    *(bus->CR1) = cr1_val;
    *(bus->CR1) |= SPI_CR1_SPE;

    // 6. Захисна пауза стабілізації рівня спокою SCK перед активацією CS
    if (cfg->settle_delay_us > 0) {
        delay_microseconds(cfg->settle_delay_us);
    }

    return SPI_STATUS_OK;
}

// Виконання повнодуплексної транзакції
spi_status_t spi_transfer_transaction(
    spi_bus_hw_t*             bus,
    const spi_slave_config_t* cfg,
    const uint8_t*            tx_buf,
    uint8_t*                  rx_buf,
    size_t                    len)
{
    if (!bus || !cfg || len == 0) {
        return SPI_STATUS_INVALID_ARG;
    }

    // Захоплення м'ютекса для взаємного виключення в RTOS
    spi_mutex_lock();

    // 1. Динамічна реконфігурація регістрів під цільовий ведений
    spi_status_t status = spi_reconfigure(bus, cfg);
    if (status != SPI_STATUS_OK) {
        spi_mutex_unlock();
        return status;
    }

    // 2. Активація виводу CS (опускання в нуль)
    gpio_write_pin(cfg->cs_port_id, cfg->cs_pin_num, false);

    // 3. Затримка t_lead перед генерацією першого такту
    if (cfg->lead_delay_us > 0) {
        delay_microseconds(cfg->lead_delay_us);
    }

    // 4. Побайтний дуплексний обмін через апаратний регістр даних
    for (size_t i = 0; i < len; ++i) {
        // Перевірка колізії Mode Fault під час транзакції
        if (*(bus->SR) & SPI_SR_MODF) {
            status = SPI_STATUS_MODE_FAULT;
            break;
        }

        // Очікування готовності передавача (TXE = 1)
        uint32_t timeout = 100000;
        while (!(*(bus->SR) & SPI_SR_TXE) && (--timeout > 0));
        if (timeout == 0) { status = SPI_STATUS_TIMEOUT; break; }

        uint8_t byte_out = tx_buf ? tx_buf[i] : 0xFF;
        *(bus->DR) = byte_out;

        // Очікування прийому байта у відповідь (RXNE = 1)
        timeout = 100000;
        while (!(*(bus->SR) & SPI_SR_RXNE) && (--timeout > 0));
        if (timeout == 0) { status = SPI_STATUS_TIMEOUT; break; }

        uint8_t byte_in = (uint8_t)(*(bus->DR));
        if (rx_buf) {
            rx_buf[i] = byte_in;
        }
    }

    // 5. Очікування повного завершення передачі останнього біта (BSY = 0)
    uint32_t timeout = 100000;
    while ((*(bus->SR) & SPI_SR_BSY) && (--timeout > 0));

    // 6. Затримка t_lag після останнього такту
    if (cfg->lag_delay_us > 0) {
        delay_microseconds(cfg->lag_delay_us);
    }

    // 7. Деактивація виводу CS (підняття у високий рівень)
    gpio_write_pin(cfg->cs_port_id, cfg->cs_pin_num, true);

    // Звільнення блокування шини
    spi_mutex_unlock();

    return status;
}
