#ifndef EOLBOOT_LOG_H
#define EOLBOOT_LOG_H

#include <stddef.h>
#include <stdint.h>

/* Кожен рядок іде з префіксом "[BOOT] " і завершується CRLF */
void log_line(const char *text);
void log_hex(const char *label, const uint8_t *data, size_t len);
void log_u32(const char *label, uint32_t value, const char *suffix);
void log_addr(const char *label, uint32_t value, const char *suffix);

#endif /* EOLBOOT_LOG_H */
