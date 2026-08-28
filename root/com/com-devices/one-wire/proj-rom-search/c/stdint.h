#include <stdint.h>
#include <stdbool.h>

/* Нижній шар (біт-бенг ведучого) — реалізовано окремо:
   OWReset()      : скидання; true, якщо був імпульс присутності (шина не порожня)
   OWWriteByte(b) : записати байт, молодшим бітом уперед
   OWWriteBit(b)  : записати один біт
   OWReadBit()    : прочитати один біт (монтажне І шини)                     */
bool    OWReset(void);
void    OWWriteByte(uint8_t b);
void    OWWriteBit(uint8_t bit);
uint8_t OWReadBit(void);
