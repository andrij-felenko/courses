#ifndef MODBUS_RTU_H
#define MODBUS_RTU_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Майстер Modbus RTU поверх RS-485.
 *
 * Порт у шлюзі один на весь польовий сегмент, а звертаються до нього дві
 * різні задачі: періодичний опитувач і правило автономії, яке пише котушку
 * аварійного скидання. Тому доступ серіалізовано м'ютексом усередині модуля —
 * два кадри не можуть накластися на одній парі дротів.
 *
 * Напрямок передавача RS-485 перемикає сам перехідник (USB-адаптери й
 * більшість промислових портів роблять це апаратно за фактом передавання).
 */

typedef struct modbus_port modbus_port_t;

typedef enum {
    MB_OK = 0,
    MB_ERR_IO = -1,        /* read/write упав або порт зник із системи */
    MB_ERR_TIMEOUT = -2,   /* підлеглий мовчить довше за дозволений час */
    MB_ERR_CRC = -3,       /* кадр побився в дорозі (наводка на довгій лінії) */
    MB_ERR_FRAME = -4,     /* відповів не той адресат або не та функція */
    MB_ERR_EXCEPTION = -5  /* підлеглий відповів кодом винятку Modbus */
} mb_status_t;

/* baud: 9600 | 19200 | 38400 | 57600 | 115200. Формат кадру — 8E1,
 * як велить стандарт Modbus для RTU. */
modbus_port_t *mb_open(const char *device, int baud, unsigned response_timeout_ms);
void mb_close(modbus_port_t *p);

/* FC 03 — читання holding-регістрів; out_regs має вміщати count слів. */
mb_status_t mb_read_holding(modbus_port_t *p, uint8_t slave, uint16_t start,
                            uint16_t count, uint16_t *out_regs);

/* FC 05 — запис одного дискретного виходу (котушки). */
mb_status_t mb_write_coil(modbus_port_t *p, uint8_t slave, uint16_t addr, bool on);

/* Код винятку останньої відповіді — має сенс лише після MB_ERR_EXCEPTION. */
uint8_t mb_last_exception(const modbus_port_t *p);

/* Пара регістрів → float32 IEEE 754. Порядок слів big-endian (старше слово
 * першим) — так віддають лічильники й перетворювачі тиску за замовчуванням. */
float mb_regs_to_float(const uint16_t *regs);

const char *mb_strerror(mb_status_t st);

#endif /* MODBUS_RTU_H */
