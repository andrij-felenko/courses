#include <stdint.h>
#include <stdbool.h>

typedef struct {
    volatile uint32_t SR;   // Status Register
    volatile uint32_t DR;   // Data Register
    volatile uint32_t BRR;  // Baud Rate Register
    volatile uint32_t CR1;  // Control Register 1
} UartHardware_t;

#define UART_SR_TXE   (1u << 7)  // Transmit data register empty
#define UART_SR_RXNE  (1u << 5)  // Read data register not empty
#define UART_SR_ORE   (1u << 3)  // Overrun error

typedef enum {
    DRIVER_OK = 0,
    DRIVER_TIMEOUT = -1,
    DRIVER_HARDWARE_ERROR = -2
} DriverStatus_t;

// Активація та читання лічильника тактів DWT Cortex-M
static inline void DWT_Init(void) {
    volatile uint32_t *DEMCR = (volatile uint32_t *)0xE000EDFC;
    volatile uint32_t *DWT_CTRL = (volatile uint32_t *)0xE0001000;
    *DEMCR |= (1u << 24);     // Вмикаємо TRCENA
    *DWT_CTRL |= (1u << 0);    // Вмикаємо CYCCNTENA
}

static inline uint32_t DWT_GetCycles(void) {
    volatile uint32_t *DWT_CYCCNT = (volatile uint32_t *)0xE0001004;
    return *DWT_CYCCNT;
}

DriverStatus_t Uart_PollWrite(UartHardware_t *hw, const uint8_t *data, uint32_t length, uint32_t timeout_cycles) {
    if (!hw || !data) return DRIVER_HARDWARE_ERROR;

    for (uint32_t i = 0; i < length; ++i) {
        uint32_t start_cycles = DWT_GetCycles();
        while (!(hw->SR & UART_SR_TXE)) {
            if ((DWT_GetCycles() - start_cycles) >= timeout_cycles) {
                return DRIVER_TIMEOUT;
            }
        }
        hw->DR = data[i];
    }
    return DRIVER_OK;
}

DriverStatus_t Uart_PollRead(UartHardware_t *hw, uint8_t *data, uint32_t length, uint32_t timeout_cycles) {
    if (!hw || !data) return DRIVER_HARDWARE_ERROR;

    for (uint32_t i = 0; i < length; ++i) {
        uint32_t start_cycles = DWT_GetCycles();
        while (!(hw->SR & UART_SR_RXNE)) {
            if (hw->SR & UART_SR_ORE) {
                // Скидання помилки переповнення ORE (читання SR, потім DR)
                (void)hw->SR;
                (void)hw->DR;
                return DRIVER_HARDWARE_ERROR;
            }
            if ((DWT_GetCycles() - start_cycles) >= timeout_cycles) {
                return DRIVER_TIMEOUT;
            }
        }
        data[i] = (uint8_t)(hw->DR & 0xFF);
    }
    return DRIVER_OK;
}
