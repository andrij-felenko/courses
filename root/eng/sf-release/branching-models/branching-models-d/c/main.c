/* ============================================================================
   Патч виправлення для ядра мережевого драйвера (C-версія)
   Ціль: гілка support/v1.4 (старе ядро Linux, відсутність epoll_create1)
   ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#define TELEMETRY_MAX_PAYLOAD 512
#define RING_BUFFER_CAPACITY  64

typedef struct {
    uint32_t message_id;
    uint16_t payload_len;
    uint8_t  payload[TELEMETRY_MAX_PAYLOAD];
} telemetry_frame_t;

typedef struct {
    telemetry_frame_t frames[RING_BUFFER_CAPACITY];
    uint32_t head;
    uint32_t tail;
    int notify_fd;
} telemetry_ring_t;

/* Безпечне скидання черги з коректним закриттям дескриптора.
   Бекпорт-адаптація: на старому ядрі v1.4 дескриптор сповіщення
   повинен обнулятися атомарно, щоб уникнути витоку при рестарті. */
int telemetry_ring_reset_safe(telemetry_ring_t *ring) {
    if (!ring) {
        return -EINVAL;
    }

    /* Атомарне закриття дескриптора подій */
    if (ring->notify_fd >= 0) {
        int fd_to_close = ring->notify_fd;
        ring->notify_fd = -1; /* Захист від повторного закриття (double close) */
        if (close(fd_to_close) != 0) {
            return -errno;
        }
    }

    ring->head = 0;
    ring->tail = 0;
    memset(ring->frames, 0, sizeof(ring->frames));

    return 0;
}

/* Обробка кадру з суворою валідацією меж */
int telemetry_process_ingress(telemetry_ring_t *ring, const uint8_t *raw_buf, size_t raw_len) {
    if (!ring || !raw_buf) {
        return -EINVAL;
    }

    /* ЗАХИСТ ВІД ПЕРЕПОВНЕННЯ (Бекпорт виправлення CVE) */
    if (raw_len > sizeof(telemetry_frame_t)) {
        return -EMSGSIZE;
    }

    uint32_t next_head = (ring->head + 1) % RING_BUFFER_CAPACITY;
    if (next_head == ring->tail) {
        return -ENOBUFS; /* Буфер переповнено */
    }

    telemetry_frame_t *target = &ring->frames[ring->head];
    memcpy(target, raw_buf, raw_len);
    ring->head = next_head;

    return 0;
}
