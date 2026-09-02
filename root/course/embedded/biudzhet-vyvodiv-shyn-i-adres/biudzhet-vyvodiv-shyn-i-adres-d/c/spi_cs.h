#ifndef SPI_CS_H
#define SPI_CS_H

#include "platform.h"

#define CS_NONE 0xFFu

/* Дешифратор 74HC138 як генератор ліній Chip Select.
   pin_a3 == PIN_NONE — один чип, 8 ліній. Інакше два каскадовані чипи:
   старший біт іде на прямий вхід дозволу першого й на інверсний другого,
   а спільний строб pin_en — на інверсний вхід дозволу обох, тобто 16 ліній
   ціною п'яти виводів мікроконтролера. */
typedef struct {
    uint8_t pin_a0;
    uint8_t pin_a1;
    uint8_t pin_a2;
    uint8_t pin_a3;
    uint8_t pin_en;
    uint8_t lines;   /* 8 або 16 */
    uint8_t active;  /* номер вибраного пристрою або CS_NONE */
} cs_decoder_t;

void cs_decoder_init(cs_decoder_t *d, uint8_t a0, uint8_t a1, uint8_t a2,
                     uint8_t a3, uint8_t en);

io_status_t cs_select(cs_decoder_t *d, uint8_t device);
void cs_release(cs_decoder_t *d);

/* Команда й дані в одній сесії CS: лінія знімається і на шляху помилки. */
io_status_t spi_cs_command(cs_decoder_t *d, uint8_t device,
                           const uint8_t *cmd, uint16_t cmd_len,
                           const uint8_t *tx, uint8_t *rx, uint16_t len);

#endif /* SPI_CS_H */
