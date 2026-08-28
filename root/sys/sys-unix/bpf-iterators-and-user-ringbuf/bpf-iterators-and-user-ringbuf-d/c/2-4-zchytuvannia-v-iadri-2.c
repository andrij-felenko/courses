/* Передача подій у ядро без системних викликів (Userspace C) */
#include <stdio.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct ip_policy {
    uint32_t ip_address;
    uint8_t  action;
};

int main(void)
{
    int map_fd = bpf_obj_get("/sys/fs/bpf/user_ringbuf_map");
    if (map_fd < 0) {
        perror("Не вдалося відкрити мапу User Ringbuf");
        return 1;
    }

    struct user_ring_buffer *urb = user_ring_buffer__new(map_fd, NULL);
    if (!urb) {
        fprintf(stderr, "Помилка створення user_ring_buffer\n");
        return 1;
    }

    /* Запис 100 000 команд у ядро БЕЗ ЖОДНОГО SYSCALL */
    for (uint32_t i = 0; i < 100000; i++) {
        struct ip_policy *policy = user_ring_buffer__reserve(urb, sizeof(*policy));
        if (policy) {
            policy->ip_address = 0x0A000001 + i; /* 10.0.0.1 + i */
            policy->action = 1;                  /* DROP */
            user_ring_buffer__submit(urb, policy);
        }
    }

    printf("100,000 політик надіслано в ядро без системних викликів!\n");
    user_ring_buffer__free(urb);
    return 0;
}
