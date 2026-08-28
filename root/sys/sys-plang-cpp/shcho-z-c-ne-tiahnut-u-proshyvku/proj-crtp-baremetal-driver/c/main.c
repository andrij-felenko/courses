#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди результату виконання операцій */
typedef enum {
    DRIVER_OK = 0,
    DRIVER_ERR_BUFFER_OVERFLOW,
    DRIVER_ERR_HARDWARE_TIMEOUT,
    DRIVER_ERR_BUSY
} DriverStatus;

/* Структура апаратних регістрів UART (відповідає адресній карті мікроконтролера) */
typedef struct {
    volatile uint32_t ISR; /* Регістр прапорців стану та переривань */
    volatile uint32_t RDR; /* Регістр прийому вхідних даних */
    volatile uint32_t TDR; /* Регістр передачі вихідних даних */
} HardwareUartRegs;

#define UART_ISR_TXE  (1U << 7) /* Прапорець: буфер передавача готовий до запису */

/* Структура драйвера в процедурному стилі C */
typedef struct {
    HardwareUartRegs* regs;
    uint32_t timeout_cycles;
} UartDriverC;

/* Обчислення контрольної суми CRC-8 (поліном 0x07) */
static inline uint8_t calculate_crc8(const uint8_t* data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x07);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

/* Відправка одного байта з контролем апаратного таймауту */
static DriverStatus uart_send_byte(UartDriverC* self, uint8_t byte) {
    uint32_t counter = self->timeout_cycles;
    while (!(self->regs->ISR & UART_ISR_TXE)) {
        if (--counter == 0) {
            return DRIVER_ERR_HARDWARE_TIMEOUT;
        }
    }
    self->regs->TDR = byte;
    return DRIVER_OK;
}

/* Формування та відправка протокольного кадру */
DriverStatus uart_transmit_packet(UartDriverC* self, const uint8_t* payload, size_t len) {
    if (len > 254) {
        return DRIVER_ERR_BUFFER_OVERFLOW;
    }

    /* 1. Заголовок кадру 0xAA */
    DriverStatus status = uart_send_byte(self, 0xAA);
    if (status != DRIVER_OK) return status;

    /* 2. Байт довжини корисних даних */
    status = uart_send_byte(self, (uint8_t)len);
    if (status != DRIVER_OK) return status;

    /* 3. Корисне навантаження */
    for (size_t i = 0; i < len; ++i) {
        status = uart_send_byte(self, payload[i]);
        if (status != DRIVER_OK) return status;
    }

    /* 4. Контрольна сума CRC */
    uint8_t crc = calculate_crc8(payload, len);
    return uart_send_byte(self, crc);
}
