#include <stdint.h>
#include <stdbool.h>

#define SLOTS      16u          // місткість кільця (степінь двійки!)
#define SLOT_MASK  (SLOTS - 1u)
#define PAYLOAD    60u          // байтів корисних даних у слоті

// Один слот — рівно те, що передаємо за раз.
typedef struct {
    uint8_t  len;               // скільки байтів у payload насправді
    uint8_t  payload[PAYLOAD];
} slot_t;

// Уся скринька в один бік. Лежить у DPRAM; ОБИДВА ядра бачать однаковий розклад.
typedef struct {
    volatile uint16_t head;     // куди покласти наступний пакет (пише продюсер)
    volatile uint16_t tail;     // звідки взяти наступний (пише споживач)
    volatile uint16_t _pad;     // до вирівнювання 4 (див. пастку про вирівнювання)
    slot_t            slot[SLOTS];
} mailbox_t;
