/* Формат журналу на Flash: константи, структури, CRC, пакування/розпакування.
 *
 * Усе, що лягає у Flash, серіалізується побайтово little-endian. Структури
 * НЕ пишуться у Flash напряму (жодного memcpy зі struct): формат мусить бути
 * однаковим для мікроконтролера й для розбирача на сервері, а розкладка
 * struct залежить від компілятора, вирівнювання й прапорців збірки. */

#ifndef LOG_FORMAT_H
#define LOG_FORMAT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define FLASH_SECTOR_SIZE   4096u
#define FLASH_SECTOR_COUNT  8u

#define LOG_SECTOR_MAGIC    0xA55Au
#define LOG_RECORD_MAGIC    0x55AAu
#define LOG_FORMAT_VERSION  0x0001u

/* Заголовок сектора — 16 байтів за нульовим зсувом:
 *   [0..1] magic · [2..3] version · [4..7] seq_num · [8..11] erase_count · [12..15] state */
#define SECTOR_HEADER_SIZE  16u
#define SECTOR_STATE_OFFSET 12u

/* Заголовок кадру — 13 байтів:
 *   [0..1] magic · [2] length · [3] level · [4] module_id · [5..8] timestamp · [9..12] token
 * далі корисне навантаження, у хвості 2 байти CRC-16. */
#define RECORD_HEADER_SIZE  13u
#define RECORD_CRC_SIZE     2u
#define RECORD_MAX_SIZE     255u
#define RECORD_MAX_PAYLOAD  (RECORD_MAX_SIZE - RECORD_HEADER_SIZE - RECORD_CRC_SIZE)

/* Стани сектора підібрані так, щоб КОЖЕН перехід лише гасив біти:
 * FFFFFFFF -> FFFFFFFE -> FFFFFFFC -> 00000000. NOR Flash уміє програмувати
 * одиницю в нуль без стирання, тож стан міняється записом 4 байтів на місці. */
typedef enum {
    SECTOR_STATE_ERASED = 0xFFFFFFFFu, /* чистий резерв */
    SECTOR_STATE_ACTIVE = 0xFFFFFFFEu, /* сюди пишемо просто зараз */
    SECTOR_STATE_FULL   = 0xFFFFFFFCu, /* заповнений, чекає вивантаження */
    SECTOR_STATE_DIRTY  = 0x00000000u  /* вивантажений, можна стирати */
} sector_state_t;

typedef enum {
    LOG_LEVEL_TRACE = 0,
    LOG_LEVEL_DEBUG = 1,
    LOG_LEVEL_INFO  = 2,
    LOG_LEVEL_WARN  = 3,
    LOG_LEVEL_ERROR = 4,
    LOG_LEVEL_FATAL = 5
} log_level_t;

/* Модуль 0 зарезервовано за самим логером — його службові записи. */
#define LOG_MODULE_LOGGER       0u

/* Токени службових подій. Верхній діапазон 0xFFFF____ не видається прикладним
 * модулям, щоб розбирач на сервері відрізняв їх від токенів рядків прошивки. */
#define LOG_TOKEN_BAD_SECTOR    0xFFFF0001u /* payload: u32 — індекс дефектного сектора */
#define LOG_TOKEN_ISR_DROPS     0xFFFF0002u /* payload: u32 — скільки кадрів утрачено в черзі ISR */

typedef struct {
    uint16_t magic;
    uint16_t version;
    uint32_t seq_num;
    uint32_t erase_count;
    uint32_t state;
} sector_header_t;

typedef struct {
    uint8_t  length;       /* повна довжина кадру разом із заголовком і CRC */
    uint8_t  level;
    uint8_t  module_id;
    uint32_t timestamp_ms;
    uint32_t token_id;
} record_header_t;

/* Побайтові примітиви little-endian — ними ж користується flash_logger.c,
 * коли гасить біти стану сектора. */
void     log_put_u16(uint8_t *p, uint16_t v);
void     log_put_u32(uint8_t *p, uint32_t v);
uint16_t log_get_u16(const uint8_t *p);
uint32_t log_get_u32(const uint8_t *p);

/* CRC-16-CCITT: поліном 0x1021, початкове значення 0xFFFF, без інверсії на виході. */
uint16_t log_crc16_ccitt(const uint8_t *data, size_t len);

void log_encode_sector_header(const sector_header_t *hdr, uint8_t out[SECTOR_HEADER_SIZE]);
void log_decode_sector_header(const uint8_t in[SECTOR_HEADER_SIZE], sector_header_t *hdr);

/* Повертає повну довжину кадру або 0, якщо навантаження завелике чи буфер малий. */
size_t log_encode_record(const record_header_t *hdr, const uint8_t *payload,
                         uint8_t payload_len, uint8_t *out, size_t out_cap);

/* Розбирає кадр і перевіряє CRC. payload вказує всередину raw. */
bool log_decode_record(const uint8_t *raw, size_t avail, record_header_t *hdr,
                       const uint8_t **payload, uint8_t *payload_len);

#endif /* LOG_FORMAT_H */
