#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RING_BUF_SIZE 256
#define HIGH_WATERMARK (RING_BUF_SIZE * 3 / 4) // 192 байти: зняти RTS
#define LOW_WATERMARK  (RING_BUF_SIZE * 1 / 4) // 64 байти: відновити RTS

typedef void (*rts_set_fn)(bool active_low_ready);

typedef struct {
    uint8_t storage[RING_BUF_SIZE];
    volatile size_t head;
    volatile size_t tail;
    volatile size_t count;
    rts_set_fn set_rts;
    bool rts_asserted;
} FlowRingBuffer;

void flow_ring_init(FlowRingBuffer *rb, rts_set_fn rts_cb) {
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
    rb->set_rts = rts_cb;
    rb->rts_asserted = true;
    if (rb->set_rts) {
        rb->set_rts(true); // Готовий до прийому (лінія /RTS = 0 В)
    }
}

// Викликається з ISR прийому UART або DMA half-transfer callback
bool flow_ring_push_isr(FlowRingBuffer *rb, uint8_t byte) {
    if (rb->count >= RING_BUF_SIZE) {
        return false; // Фатальне переповнення (буфер вичерпано повністю)
    }

    rb->storage[rb->head] = byte;
    rb->head = (rb->head + 1) % RING_BUF_SIZE;
    rb->count++;

    // Перевірка верхнього порогу: піднімаємо RTS у High (стан Busy)
    if (rb->rts_asserted && rb->count >= HIGH_WATERMARK) {
        rb->rts_asserted = false;
        if (rb->set_rts) {
            rb->set_rts(false); // /RTS = 3.3 В (заборона передачі)
        }
    }
    return true;
}

// Викликається з основного циклу або фонового завдання RTOS
bool flow_ring_pop(FlowRingBuffer *rb, uint8_t *out_byte) {
    if (rb->count == 0) {
        return false; // Буфер порожній
    }

    *out_byte = rb->storage[rb->tail];
    rb->tail = (rb->tail + 1) % RING_BUF_SIZE;
    rb->count--;

    // Перевірка нижнього порогу: опускаємо RTS у Low (стан Ready)
    if (!rb->rts_asserted && rb->count <= LOW_WATERMARK) {
        rb->rts_asserted = true;
        if (rb->set_rts) {
            rb->set_rts(true); // /RTS = 0 В (дозвіл передачі)
        }
    }
    return true;
}
