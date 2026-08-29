/* sf_frame.h — формат кадру в енергонезалежній пам'яті.
 *
 * Розкладка байтів (little-endian, як у самого мікроконтролера):
 *
 *   0..1   magic         0xAA55
 *   2      type          SF_TYPE_*
 *   3      flags         біти 0..1 — пріоритет
 *   4..7   seq           монотонний номер кадру
 *   8..15  timestamp_ms  час формування, мілісекунди
 *   16..17 payload_len   1..512
 *   18..19 reserved      0
 *   20..   payload
 *   ...    crc32         за всіма байтами від magic до кінця payload
 *   ...    padding 0xFF  до межі 4 байтів (наступний кадр вирівняний)
 *
 * Структуру НЕ пишемо у флеш через memcpy: розкладка в пам'яті залежить
 * від компілятора й вирівнювання, а формат на носії мусить бути тим самим
 * на будь-якому порту. Тому серіалізація явна, побайтова. Це коштує
 * десяток тактів на кадр і рятує від «прошивка оновилась — історія зникла».
 */
#ifndef SF_FRAME_H
#define SF_FRAME_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define SF_MAGIC        0xAA55u
#define SF_HEADER_SIZE  20u
#define SF_CRC_SIZE     4u
#define SF_ALIGN        4u
#define SF_MAX_PAYLOAD  512u

/* Найбільший кадр з вирівнюванням: 20 + 512 + 4 = 536, уже кратне 4. */
#define SF_RECORD_MAX   (SF_HEADER_SIZE + SF_MAX_PAYLOAD + SF_CRC_SIZE)

/* Пріоритет живе у флагах — від нього залежить, кого викидати при
 * переповненні накопичувача. */
typedef enum {
    SF_PRIORITY_LOW  = 0, /* високочастотна телеметрія — витісняється першою */
    SF_PRIORITY_NORM = 1, /* періодичний статус — витісняє історію за FIFO   */
    SF_PRIORITY_HIGH = 2, /* аварії та події — місце звільняється під них    */
} sf_priority_t;

#define SF_FLAGS_PRIORITY_MASK 0x03u

/* Типи корисного навантаження: сервер розбирає кадр за цим байтом. */
#define SF_TYPE_TELEMETRY 0x01u
#define SF_TYPE_STATUS    0x02u
#define SF_TYPE_ALARM     0x03u

typedef struct {
    uint16_t magic;
    uint8_t  type;
    uint8_t  flags;
    uint32_t seq;
    uint64_t timestamp_ms;
    uint16_t payload_len;
    uint16_t reserved;
} sf_header_t;

/* Скільки місця займе кадр разом із вирівнюванням наступного. */
static inline uint32_t sf_frame_stride(uint16_t payload_len)
{
    uint32_t raw = SF_HEADER_SIZE + (uint32_t)payload_len + SF_CRC_SIZE;
    return (raw + (SF_ALIGN - 1u)) & ~(SF_ALIGN - 1u);
}

static inline sf_priority_t sf_frame_priority(const sf_header_t *h)
{
    return (sf_priority_t)(h->flags & SF_FLAGS_PRIORITY_MASK);
}

/* Пакує заголовок, навантаження, CRC і вирівнювання у dst
 * (щонайменше SF_RECORD_MAX байтів). Повертає stride. */
uint32_t sf_frame_pack(uint8_t *dst, const sf_header_t *hdr, const void *payload);

/* Розбирає перші SF_HEADER_SIZE байтів. false — не кадр:
 * або чужа преамбула, або немислима довжина навантаження. */
bool sf_frame_parse_header(const uint8_t *src, sf_header_t *out);

/* Звіряє контрольний суфікс уже прочитаного кадру. */
bool sf_frame_check_crc(const uint8_t *record, uint16_t payload_len);

/* Чи ділянка стерта (усі байти 0xFF). Стерта голова означає «далі
 * записів немає», а не «дані зіпсовано» — це різні події. */
bool sf_frame_is_blank(const void *buf, uint32_t len);

#endif /* SF_FRAME_H */
