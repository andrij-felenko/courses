#include <stdint.h>
#include <stdbool.h>

// --- Контейнер 1: буфер-черга (коробка "Черга" на діаграмі) ---
typedef struct {
    uint16_t data[64];
    uint8_t  head, tail;
} SampleQueue;

// --- Контейнер 2: сенсорний вузол ---
// Стрілка діаграми "сенсор -> черга" стає ПОЛЕМ-залежністю:
// сенсор знає про чергу рівно тому, що на діаграмі є ця стрілка.
typedef struct {
    SampleQueue *out;   // єдиний дозволений зв'язок — до черги
} SensorNode;

// --- Контейнер 3: передавач у мережу ---
typedef struct {
    SampleQueue *in;    // стрілка "передавач -> черга", теж поле
} Uplink;

bool queue_push(SampleQueue *q, uint16_t v);
bool queue_pop(SampleQueue *q, uint16_t *out);

void sensor_tick(SensorNode *s, uint16_t reading) {
    queue_push(s->out, reading);   // сенсор торкає ЛИШЕ чергу, як на діаграмі
}

void uplink_tick(Uplink *u) {
    uint16_t v;
    while (queue_pop(u->in, &v))
        /* відправити v у мережу */;
}
