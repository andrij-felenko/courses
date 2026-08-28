#include <stdint.h>

// Кільцевий буфер сирих байтів UART. Розмір — степінь двійки,
// щоб замість ділення на модуль обійтися дешевою маскою «& (SIZE-1)».
#define RB_SIZE 64
#define RB_MASK (RB_SIZE - 1)

typedef struct {
    volatile uint8_t buf[RB_SIZE];
    volatile uint16_t head;   // куди пише перервання
    volatile uint16_t tail;   // звідки читає головний цикл
} ring_t;

static ring_t rb;

// Викликається З ПЕРЕРВАННЯ UART на кожен прийнятий байт. Мусить бути коротким.
void sbus_uart_isr(uint8_t byte) {
    uint16_t next = (rb.head + 1) & RB_MASK;
    if (next != rb.tail) {        // є місце — інакше просто губимо байт
        rb.buf[rb.head] = byte;
        rb.head = next;
    }
}

// Читає один байт із буфера. Повертає 1, якщо байт був; 0, якщо буфер порожній.
static int rb_get(uint8_t *out) {
    if (rb.head == rb.tail) return 0;      // порожньо
    *out = rb.buf[rb.tail];
    rb.tail = (rb.tail + 1) & RB_MASK;
    return 1;
}
