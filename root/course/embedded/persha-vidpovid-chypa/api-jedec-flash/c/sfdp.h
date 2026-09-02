#ifndef SFDP_H
#define SFDP_H

#include <stdbool.h>
#include <stdint.h>

#include "spi_port.h"

#define SFDP_CMD_READ    0x5Au
#define SFDP_MAX_DWORDS  20u   /* JESD216D має 20 подвійних слів; більше не читаємо */
#define SFDP_ERASE_TYPES 4u

typedef enum {
    SFDP_OK = 0,
    SFDP_ERR_SIGNATURE,      /* заголовок не починається з 'S' 'F' 'D' 'P' */
    SFDP_ERR_NO_BASIC_TABLE, /* серед заголовків параметрів немає базової таблиці */
    SFDP_ERR_TRUNCATED       /* таблиця коротша, ніж потрібні нам поля */
} sfdp_status_t;

typedef struct {
    uint8_t  opcode;      /* 0 — цей тип стирання кристал не має */
    uint32_t size_bytes;
    uint32_t typical_ms;  /* 0 — таблиця не містить DWORD10 із часами */
} sfdp_erase_type_t;

typedef struct {
    uint8_t  major;
    uint8_t  minor;
    uint8_t  dwords;             /* оголошена довжина базової таблиці */
    uint8_t  address_bytes;      /* 3 або 4 */
    bool     four_byte_capable;  /* уміє обидва режими адресації */
    uint64_t density_bits;
    uint64_t density_bytes;
    uint32_t page_size_bytes;
    bool     has_1_1_4;
    bool     has_1_4_4;
    uint8_t  op_1_1_4, dummy_1_1_4, mode_1_1_4;
    uint8_t  op_1_4_4, dummy_1_4_4, mode_1_4_4;
    uint8_t  quad_enable;        /* поле QER; 0xFF — таблиця без DWORD15 */
    sfdp_erase_type_t erase[SFDP_ERASE_TYPES];
} sfdp_params_t;

sfdp_status_t sfdp_read(spi_port_t *port, sfdp_params_t *out);
const char *sfdp_status_text(sfdp_status_t status);
const char *sfdp_quad_enable_text(uint8_t qer);

#endif /* SFDP_H */
