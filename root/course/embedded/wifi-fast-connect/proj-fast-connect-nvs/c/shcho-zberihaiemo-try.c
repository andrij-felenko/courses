#include <stdint.h>

#define FASTCONN_MAGIC   0x57494643u   // "WIFC" — мітка нашого формату
#define FASTCONN_VERSION 1             // версія розкладки полів

// Усе, що зберігаємо між сеансами, — однією структурою, одним блобом.
typedef struct {
    uint32_t magic;        // FASTCONN_MAGIC: чи це взагалі наш запис
    uint8_t  version;      // FASTCONN_VERSION: чи розкладка ще сумісна
    uint8_t  channel;      // канал точки (1..13), 0 = немає підказки
    uint8_t  bssid[6];     // MAC точки — лише для перевірки, не для прив'язки
    uint32_t ip;           // остання видана адреса (network order)
    uint32_t netmask;      // маска (network order)
    uint32_t gw;           // шлюз (network order)
    uint16_t fail_streak;  // скільки теплих стартів поспіль провалилося
} fastconn_t;
