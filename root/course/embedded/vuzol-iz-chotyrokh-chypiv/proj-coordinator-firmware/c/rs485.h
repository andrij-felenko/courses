#ifndef RS485_H
#define RS485_H

/* Напівдуплексний канал RS-485: кадр Modbus RTU відділяється паузою t3.5
 * (детектор Receiver Timeout у USART), лінія DE знімається строго по TC. */

#include "node.h"

#define RS485_NODE_ID 0x01u
#define RS485_BAUD    19200u

void rs485_init(uint32_t kernel_clk_hz);

/* Обробляє зібраний кадр і, якщо він адресований нам, відправляє відповідь.
 * Викликається з головного циклу на подію NODE_EVENT_RS485_FRAME. */
void rs485_service(const telemetry_record_t *last);

bool rs485_tx_busy(void);
bool rs485_frame_waiting(void);

/* Час останнього коректного опитування — з нього робиться прапорець
 * RS485_ACTIVE у записі телеметрії. */
uint32_t rs485_last_poll_ms(void);
bool     rs485_master_active(void);

#endif /* RS485_H */
