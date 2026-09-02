#ifndef JEDEC_H
#define JEDEC_H

#include <stdbool.h>
#include <stdint.h>

#include "spi_port.h"

#define JEDEC_CMD_READ_ID      0x9Fu
#define JEDEC_CMD_READ_STATUS1 0x05u
#define JEDEC_CMD_EXIT_QPI     0xFFu

#define JEDEC_ID_MAX_BYTES     6u          /* 3 паспортні байти + запас на банки */
#define JEDEC_MAX_CONTINUATION 3u          /* більше банків у корпусі не чекаємо */
#define JEDEC_SAFE_CLOCK_HZ    20000000u   /* нижче апаратної межі 33–50 МГц для 0x9F */
#define JEDEC_WIP_TIMEOUT_MS   4000u       /* стирання цілого кристала буває довшим, */
                                           /* але тоді bring-up і не робиться */
#define JEDEC_STATUS_WIP       0x01u

/* Аварійні стани шини треба відрізняти від справжніх даних: 0xFF і 0x00 —
   це не «дивний виробник», а обрив і замикання відповідно. */
typedef enum {
    JEDEC_OK = 0,
    JEDEC_ERR_SHORT_ANSWER,   /* відповідь коротша за три байти паспорта */
    JEDEC_ERR_LINE_HIGH,      /* суцільні 0xFF: обрив MISO, немає VCC або чип у QPI */
    JEDEC_ERR_LINE_LOW,       /* суцільні 0x00: замикання MISO на землю або скидання */
    JEDEC_ERR_CONTINUATION,   /* потік 0x7F без кінця — шина шумить */
    JEDEC_ERR_BUSY,           /* прапорець WIP не скинувся за тайм-аут */
    JEDEC_ERR_CAPACITY        /* код ємності поза 0x10..0x1A */
} jedec_status_t;

typedef struct {
    uint8_t  raw[JEDEC_ID_MAX_BYTES];  /* сира відповідь як вона є — для звіту */
    uint8_t  raw_len;
    uint8_t  bank;                     /* 1 + кількість байтів продовження 0x7F */
    uint8_t  manufacturer_id;
    uint8_t  memory_type;
    uint8_t  capacity_id;
    uint32_t total_size_bytes;         /* 2^capacity_id */
    uint32_t page_size_bytes;          /* квант програмування, завжди 256 */
    uint32_t sector_size_bytes;        /* мінімальне стирання, зазвичай 4096 */
    uint32_t total_pages;
    uint32_t total_sectors;
    bool     qpi_recovered;            /* довелося виводити кристал із QPI */
    const char *vendor_name;
} flash_passport_t;

/* Назва виробника за JEP106: код осмислений лише разом із номером банку. */
const char *jedec_vendor_name(uint8_t bank, uint8_t manufacturer_id);

/* Розбір готової відповіді: банки продовження, паспортні байти, геометрія. */
jedec_status_t jedec_decode(const uint8_t *raw, uint8_t len, flash_passport_t *out);

/* Повний цикл опитування з усіма запобіжниками розділу 5. */
jedec_status_t jedec_identify(spi_port_t *port, flash_passport_t *out);

const char *jedec_status_text(jedec_status_t status);

#endif /* JEDEC_H */
