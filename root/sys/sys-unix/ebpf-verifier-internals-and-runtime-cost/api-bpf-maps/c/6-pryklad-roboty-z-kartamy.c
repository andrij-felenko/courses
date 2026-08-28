#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>

int main(void)
{
    /* 1. Створення хеш-карти: ключ = uint32_t (PID), значення = uint64_t (лічильник) */
    int map_fd = bpf_map_create(BPF_MAP_TYPE_HASH, "proc_stats",
                                sizeof(uint32_t), sizeof(uint64_t),
                                1024, NULL);
    if (map_fd < 0) {
        fprintf(stderr, "Помилка створення карти: %s\n", strerror(errno));
        return 1;
    }

    uint32_t key = 1337;
    uint64_t initial_val = 1;

    /* 2. Запис значення з прапорцем BPF_ANY */
    if (bpf_map_update_elem(map_fd, &key, &initial_val, BPF_ANY) != 0) {
        fprintf(stderr, "Помилка оновлення елемента: %s\n", strerror(errno));
        close(map_fd);
        return 1;
    }

    /* 3. Зчитування збереженого значення */
    uint64_t lookup_val = 0;
    if (bpf_map_lookup_elem(map_fd, &key, &lookup_val) == 0) {
        printf("Знайдено значення для PID %u: %lu\n", key, lookup_val);
    }

    close(map_fd);
    return 0;
}
