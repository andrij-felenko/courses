#include <stdint.h>
#include <stddef.h>
#include <string.h>

// ── Низькорівневий драйвер чипа (з комп-вставки). Читання-дзеркало до запису:
//    те саме адресування, лише напрям інший; для EEPROM читання без затримок.
void eeprom_write(uint16_t addr, const uint8_t *buf, uint16_t len);
void eeprom_read (uint16_t addr,       uint8_t *buf, uint16_t len);

// ── Геометрія кільця (під конкретний чип і задачу) ───────────────────────────
#define WL_BASE      0        // адреса початку області кільця в EEPROM
#define WL_SLOTS     128      // скільки слотів у кільці (кратне зносу, див. пастки)
#define WL_DATA_LEN  8        // скільки байтів корисних даних у слоті

// Слот на «дроті»: [ дані WL_DATA_LEN ][ seq 4 байти ][ crc 1 байт ].
// seq — монотонна послідовність запису; crc — контрольна сума решти слота.
#define WL_SEQ_LEN   4
#define WL_CRC_LEN   1
#define WL_SLOT_LEN  (WL_DATA_LEN + WL_SEQ_LEN + WL_CRC_LEN)   // = 13 байтів

// Стан кільця в RAM: де голова й яка в неї послідовність (щоб не шукати щоразу).
typedef struct {
    uint16_t head_slot;   // індекс слота з останнім дійсним записом
    uint32_t head_seq;    // послідовність цього запису (0 = кільце ще порожнє)
} wl_ring_t;
