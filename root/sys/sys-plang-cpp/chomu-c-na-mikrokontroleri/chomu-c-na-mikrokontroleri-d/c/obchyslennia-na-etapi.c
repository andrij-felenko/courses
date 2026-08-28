/* Розрахунок дільника UART мовою C (виконується в рантаймі) */
#include <stdint.h>

typedef struct {
    uint32_t mantissa;
    uint32_t fraction;
} UartBaudDiv;

UartBaudDiv calculate_baud_c(uint32_t f_pclk, uint32_t baud) {
    /* Обчислення при кожному виклику в рантаймі */
    uint32_t div = (25 * f_pclk) / (4 * baud);
    UartBaudDiv res;
    res.mantissa = div / 100;
    res.fraction = (((div - (res.mantissa * 100)) * 16) + 50) / 100;
    return res;
}
