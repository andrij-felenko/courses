#ifndef FLASHER_BOOTLOADER_H
#define FLASHER_BOOTLOADER_H

#include "serial.h"

#define BL_FLASH_BASE 0x08000000u
#define BL_MAX_BLOCK  256u /* межа протоколу: N кодується одним байтом як len-1 */

typedef enum {
    BL_OK = 0,
    BL_ERR_IO,       /* порт не прийняв або не віддав байти */
    BL_ERR_TIMEOUT,  /* завантажувач промовчав */
    BL_ERR_NACK,     /* чип відмовив: команда не підтримується або стоїть захист */
    BL_ERR_PROTOCOL, /* прийшло щось третє — розсинхронізація */
    BL_ERR_ARG
} bl_status;

const char *bl_status_text(bl_status status);

/* Крок 1: 0x7F на швидкості 115200 8E1 — вимірювання бітрейту завантажувачем */
bl_status bl_sync(const serial_port *port);

/* 0x01: версія протоколу та два байти стану захисту */
bl_status bl_get_version(const serial_port *port, uint8_t *version, uint8_t option_bytes[2]);

/* 0x02: 12-бітний Product ID кристала */
bl_status bl_get_id(const serial_port *port, uint16_t *pid);

/* 0x92: зняття RDP level 1. Тягне масове стирання і скидання чипа. */
bl_status bl_readout_unprotect(const serial_port *port);

/* 0x44 з кодом 0xFFFF: стирання всієї матриці Flash */
bl_status bl_mass_erase(const serial_port *port);

/* 0x31: запис блока (1..256 байтів) */
bl_status bl_write_block(const serial_port *port, uint32_t address, const uint8_t *data, size_t len);

/* 0x11: читання блока (1..256 байтів) для верифікації */
bl_status bl_read_block(const serial_port *port, uint32_t address, uint8_t *buf, size_t len);

/* 0x21: передача керування за адресою */
bl_status bl_go(const serial_port *port, uint32_t address);

#endif /* FLASHER_BOOTLOADER_H */
