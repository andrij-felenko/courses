#include <stdint.h>
#include <string.h>

#define PRE_SAMPLES 32000            // 2 с при 16 кГц (передзвук)
static int16_t  ring[PRE_SAMPLES];
static uint32_t head = 0;            // куди писати наступний відлік
static uint32_t filled = 0;         // скільки відліків уже реально в кільці

// Викликаємо на КОЖЕН блок із конвеєра захоплення — кільце крутиться завжди.
void ring_push(const int16_t *blk, uint32_t n) {
    for (uint32_t i = 0; i < n; i++) {
        ring[head] = blk[i];
        head = (head + 1) % PRE_SAMPLES;    // дійшов до кінця — на початок
        if (filled < PRE_SAMPLES) filled++;
    }
}

// Подія! Вивантажуємо передзвук У ХРОНОЛОГІЧНОМУ порядку: від найстарішого.
// Найстаріший відлік — це той, що ЗАРАЗ під головою (його ось-ось затерли б).
void ring_drain(void (*sink)(const int16_t*, uint32_t)) {
    uint32_t start = (filled < PRE_SAMPLES) ? 0 : head;   // початок хронології
    for (uint32_t i = 0; i < filled; i++) {
        int16_t s = ring[(start + i) % PRE_SAMPLES];
        sink(&s, 1);                        // віддаємо на запис у файл
    }
}
