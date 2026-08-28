#include <stdint.h>
#include <stdbool.h>

#define N_CHAN        79        // каналів у смузі 2.4 ГГц (як у Bluetooth)
#define BAD_LIMIT     6         // стільки поспіль збоїв — канал у чорний список
#define GOOD_RECOVER  200       // стільки чистих пакетів — реабілітація каналу

static uint8_t  err_run[N_CHAN];    // поспіль збоїв на каналі
static uint16_t good_run[N_CHAN];   // поспіль чистих пакетів
static bool     blacklisted[N_CHAN];

// Псевдовипадковий генератор розкладу (спільне зерно з передавачем!).
// 16-бітний LFSR, поліном 0xB400 — довга неповторна послідовність.
static uint16_t lfsr = 0xACE1u;    // зерно узгоджене на обох кінцях
static uint16_t hop_prng(void) {
    uint16_t lsb = lfsr & 1u;
    lfsr >>= 1;
    if (lsb) lfsr ^= 0xB400u;      // обернений зв'язок
    return lfsr;
}

// Оновити статистику каналу за результатом прийому одного пакета.
void channel_feedback(uint8_t ch, bool crc_ok) {
    if (crc_ok) {
        err_run[ch] = 0;
        if (blacklisted[ch] && ++good_run[ch] >= GOOD_RECOVER) {
            blacklisted[ch] = false;    // канал очистився — повертаємо в гру
            good_run[ch] = 0;
        }
    } else {
        good_run[ch] = 0;
        if (++err_run[ch] >= BAD_LIMIT)
            blacklisted[ch] = true;     // канал стабільно брудний — геть
    }
}

// Наступний канал за розкладом, але не з чорного списку.
uint8_t next_hop_channel(void) {
    for (int guard = 0; guard < 4 * N_CHAN; ++guard) {
        uint8_t ch = (uint8_t)(hop_prng() % N_CHAN);
        if (!blacklisted[ch])
            return ch;                  // чистий канал за псевдовипадком
    }
    return 0;   // рятівний випадок: усе в чорному списку — беремо нульовий
}
