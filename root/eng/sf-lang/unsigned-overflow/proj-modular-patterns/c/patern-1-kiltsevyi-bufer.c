#include <stdint.h>
#include <stdbool.h>

#define RB_SIZE 256u                 // ОБОВʼЯЗКОВО степінь двійки
#define RB_MASK (RB_SIZE - 1u)       // 255 = 0x00FF — суцільна маска

static volatile uint8_t  rb_buf[RB_SIZE];
static volatile uint16_t rb_head;    // пише продюсер (ISR)
static volatile uint16_t rb_tail;    // рухає споживач (main)

// --- бік продюсера: викликається з обробника переривання ---
static inline bool rb_push(uint8_t byte) {
    uint16_t next = (rb_head + 1u) & RB_MASK;   // крок по колу маскою
    if (next == rb_tail)                        // наздогнали хвіст — буфер повний
        return false;                           // байт втрачено, але черга ціла
    rb_buf[rb_head] = byte;
    rb_head = next;                             // публікуємо запис ОСТАННІМ
    return true;
}

// --- бік споживача: викликається з головного циклу ---
static inline bool rb_pop(uint8_t *out) {
    if (rb_tail == rb_head)                      // голова = хвіст → порожньо
        return false;
    *out = rb_buf[rb_tail];
    rb_tail = (rb_tail + 1u) & RB_MASK;          // крок по колу маскою
    return true;
}
