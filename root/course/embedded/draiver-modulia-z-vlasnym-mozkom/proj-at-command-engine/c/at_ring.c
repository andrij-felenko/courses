#include "at_ring.h"

#include <string.h>

void at_ring_init(at_ring_t *ring)
{
    memset(ring->data, 0, sizeof(ring->data));
    ring->tail = 0U;
}

uint16_t at_ring_available(const at_ring_t *ring, uint16_t head)
{
    return (uint16_t)((head - ring->tail) & AT_RX_MASK);
}

at_line_status_t at_ring_read_line(at_ring_t *ring, uint16_t head,
                                   char *out, size_t out_size)
{
    if (out_size == 0U) {
        return AT_LINE_NONE;
    }
    if (head == ring->tail) {
        return AT_LINE_NONE;
    }

    /* Крок 1 — розвідка. Йдемо копією індексу й нічого не споживаємо, поки
       не переконалися, що рядок прийшов цілим. */
    uint16_t scan    = ring->tail;
    uint16_t scanned = 0U;
    bool     found   = false;

    while (scan != head) {
        if (ring->data[scan] == (uint8_t)'\n') {
            found = true;
            break;
        }
        scan = (uint16_t)((scan + 1U) & AT_RX_MASK);
        scanned++;

        if (scanned >= AT_MAX_LINE_SIZE) {
            /* Потік без термінаторів: завади в ефірі, неузгоджена швидкість,
               двійкове сміття після скидання модуля. Просуваємо tail силою —
               інакше буфер заповниться й парсер стане назавжди. */
            ring->tail = scan;
            return AT_LINE_OVERFLOW;
        }
    }

    if (!found) {
        return AT_LINE_NONE;
    }

    /* Крок 2 — вибірка. Тепер точно відомо, де кінець рядка. */
    size_t written = 0U;
    bool   visible = false;
    while (ring->tail != scan) {
        const uint8_t b = ring->data[ring->tail];
        if (b != (uint8_t)'\r' && written < (out_size - 1U)) {
            out[written++] = (char)b;
            if (b > (uint8_t)' ') {
                visible = true;
            }
        }
        ring->tail = (uint16_t)((ring->tail + 1U) & AT_RX_MASK);
    }
    ring->tail = (uint16_t)((ring->tail + 1U) & AT_RX_MASK); /* з'їдаємо '\n' */

    out[written] = '\0';
    /* Порожній рядок і рядок з самих пробілів (хвіст запрошення "> ")
       рівноцінні: змісту в них немає, розбирати нічого. */
    return visible ? AT_LINE_OK : AT_LINE_EMPTY;
}

bool at_ring_take_upto(at_ring_t *ring, uint16_t head, char ch)
{
    uint16_t scan = ring->tail;

    while (scan != head) {
        if (ring->data[scan] == (uint8_t)ch) {
            ring->tail = (uint16_t)((scan + 1U) & AT_RX_MASK);
            return true;
        }
        scan = (uint16_t)((scan + 1U) & AT_RX_MASK);
    }
    return false;
}

void at_ring_flush(at_ring_t *ring, uint16_t head)
{
    ring->tail = head;
}
