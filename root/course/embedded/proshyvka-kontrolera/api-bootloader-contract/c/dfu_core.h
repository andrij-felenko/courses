#ifndef DFU_CORE_H
#define DFU_CORE_H

#include <stddef.h>
#include <stdint.h>

#include "dfu_proto.h"

/* Відкладена операція: запит EP0 мусить відповісти за мілісекунди, а стирання
   сектора триває секунди. Тому GETSTATUS лише оголошує таймаут, а роботу
   виконує dfu_poll() із головного циклу. */
typedef enum {
    DFU_OP_NONE = 0,
    DFU_OP_WRITE,
    DFU_OP_ERASE,
    DFU_OP_ERASE_APP,
    DFU_OP_MANIFEST
} dfu_op_t;

typedef struct {
    dfu_state_t  state;
    dfu_status_t status;
    uint32_t     address_pointer; /* його ставить команда DfuSe 0x21 */
    dfu_op_t     op;
    uint32_t     op_address;
    size_t       op_length;
    uint32_t     poll_timeout_ms;
    uint8_t      reply[DFU_GETSTATUS_LEN];
    uint8_t      buffer[DFU_TRANSFER_SIZE];
} dfu_device_t;

void dfu_init(dfu_device_t *dev);

/* Обробка класового запиту на нульовій кінцевій точці.
   Повертає 0, якщо відповідь готова (out/out_len), і -1 — коли треба STALL. */
int dfu_control_request(dfu_device_t *dev,
                        uint8_t request, uint16_t block_num, uint16_t length,
                        const uint8_t *data, size_t data_len,
                        const uint8_t **out, size_t *out_len);

/* Виконує відкладену операцію; кличеться з головного циклу завантажувача. */
void dfu_poll(dfu_device_t *dev);

#endif /* DFU_CORE_H */
