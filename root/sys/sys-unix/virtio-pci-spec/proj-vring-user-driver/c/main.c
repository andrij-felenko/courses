#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define VIRTQ_DESC_F_NEXT  1
#define VIRTQ_DESC_F_WRITE 2

#define VRING_ALIGN 4096
#define QUEUE_SIZE  16

struct virtq_desc {
    uint64_t addr;
    uint32_t len;
    uint16_t flags;
    uint16_t next;
};

struct virtq_avail {
    uint16_t flags;
    uint16_t idx;
    uint16_t ring[QUEUE_SIZE];
    uint16_t used_event;
};

struct virtq_used_elem {
    uint32_t id;
    uint32_t len;
};

struct virtq_used {
    uint16_t flags;
    uint16_t idx;
    struct virtq_used_elem ring[QUEUE_SIZE];
    uint16_t avail_event;
};

struct virtqueue {
    uint16_t num;
    struct virtq_desc *desc;
    struct virtq_avail *avail;
    struct virtq_used *used;
    uint16_t last_used_idx;
    uint16_t free_head;
    uint16_t num_free;
};

static void memory_write_barrier(void) {
    __asm__ __volatile__("sfence" ::: "memory");
}

static void memory_read_barrier(void) {
    __asm__ __volatile__("lfence" ::: "memory");
}

struct virtqueue *vq_create(uint16_t queue_size) {
    struct virtqueue *vq = (struct virtqueue *)calloc(1, sizeof(struct virtqueue));
    if (!vq) return NULL;

    vq->num = queue_size;
    vq->num_free = queue_size;
    vq->free_head = 0;
    vq->last_used_idx = 0;

    size_t desc_bytes = sizeof(struct virtq_desc) * queue_size;
    size_t avail_bytes = sizeof(uint16_t) * (3 + queue_size);
    size_t used_bytes = sizeof(uint16_t) * 3 + sizeof(struct virtq_used_elem) * queue_size;

    void *mem = NULL;
    size_t total_size = desc_bytes + avail_bytes + used_bytes + VRING_ALIGN;
    if (posix_memalign(&mem, VRING_ALIGN, total_size) != 0) {
        free(vq);
        return NULL;
    }
    memset(mem, 0, total_size);

    vq->desc = (struct virtq_desc *)mem;
    vq->avail = (struct virtq_avail *)((uintptr_t)mem + desc_bytes);

    uintptr_t used_addr = (uintptr_t)vq->avail + avail_bytes;
    used_addr = (used_addr + VRING_ALIGN - 1) & ~(VRING_ALIGN - 1);
    vq->used = (struct virtq_used *)used_addr;

    for (uint16_t i = 0; i < queue_size - 1; i++) {
        vq->desc[i].next = i + 1;
    }
    vq->desc[queue_size - 1].next = 0xFFFF;

    return vq;
}

int vq_add_buffer(struct virtqueue *vq, uint64_t phys_addr, uint32_t len, bool is_write) {
    if (vq->num_free < 1) return -1;

    uint16_t head = vq->free_head;
    vq->desc[head].addr = phys_addr;
    vq->desc[head].len = len;
    vq->desc[head].flags = is_write ? VIRTQ_DESC_F_WRITE : 0;
    vq->free_head = vq->desc[head].next;
    vq->num_free--;

    memory_write_barrier();

    uint16_t avail_slot = vq->avail->idx & (vq->num - 1);
    vq->avail->ring[avail_slot] = head;

    memory_write_barrier();
    vq->avail->idx++;

    return head;
}

void vq_kick_notify(struct virtqueue *vq, volatile uint32_t *doorbell_reg) {
    memory_write_barrier();
    if (doorbell_reg) {
        *doorbell_reg = 0; // Запис у дверний дзвоник (Kick)
    }
}

int vq_poll_used(struct virtqueue *vq, uint32_t *len_written) {
    memory_read_barrier();

    if (vq->last_used_idx == vq->used->idx) {
        return -1; // Немає завершених запитів
    }

    uint16_t used_slot = vq->last_used_idx & (vq->num - 1);
    struct virtq_used_elem *elem = &vq->used->ring[used_slot];

    uint32_t head = elem->id;
    if (len_written) *len_written = elem->len;

    vq->desc[head].next = vq->free_head;
    vq->free_head = head;
    vq->num_free++;

    vq->last_used_idx++;
    return (int)head;
}

void vq_free(struct virtqueue *vq) {
    if (vq) {
        free(vq->desc);
        free(vq);
    }
}

int main(void) {
    struct virtqueue *vq = vq_create(QUEUE_SIZE);
    if (!vq) {
        fprintf(stderr, "Помилка створення virtqueue\n");
        return 1;
    }

    char buffer[512] = "Приклад даних Virtio I/O";
    int head = vq_add_buffer(vq, (uint64_t)(uintptr_t)buffer, sizeof(buffer), false);
    printf("Додано буфер у vring: head index = %d, avail idx = %u\n", head, vq->avail->idx);

    vq_kick_notify(vq, NULL);

    // Симуляція обробки гіпервізором:
    vq->used->ring[0].id = head;
    vq->used->ring[0].len = sizeof(buffer);
    vq->used->idx = 1;

    uint32_t bytes_done = 0;
    int completed_head = vq_poll_used(vq, &bytes_done);
    if (completed_head >= 0) {
        printf("Завершено обробку буфера %d, оброблено байт: %u\n", completed_head, bytes_done);
    }

    vq_free(vq);
    return 0;
}
