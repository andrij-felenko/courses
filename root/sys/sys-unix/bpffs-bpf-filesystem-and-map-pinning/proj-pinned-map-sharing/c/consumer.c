/* consumer.c — Відкриття зафіксованої у bpffs мапи та зчитування даних */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <bpf/bpf.h>

#define PIN_PATH "/sys/fs/bpf/shared_stats_map"

int main(void) {
    uint32_t key = 42;
    uint64_t value = 0;

    /* Отримання FD зафіксованої у bpffs мапи */
    int map_fd = bpf_obj_get(PIN_PATH);
    if (map_fd < 0) {
        fprintf(stderr, "Помилка отримання мапи з %s: %s\n", PIN_PATH, strerror(errno));
        return EXIT_FAILURE;
    }

    printf("[Consumer] Успішно отримано FD %d з %s\n", map_fd, PIN_PATH);

    /* Пошук значення за ключем */
    if (bpf_map_lookup_elem(map_fd, &key, &value) < 0) {
        fprintf(stderr, "Помилка зчитування елемента з ключем %u: %s\n", key, strerror(errno));
        close(map_fd);
        return EXIT_FAILURE;
    }

    printf("[Consumer] Прочитано з зафіксованої мапи: ключ %u -> значення %lu\n", key, value);

    /* Інкремент значення у спільній мапі */
    value += 500;
    if (bpf_map_update_elem(map_fd, &key, &value, BPF_EXIST) < 0) {
        fprintf(stderr, "Помилка оновлення значення: %s\n", strerror(errno));
        close(map_fd);
        return EXIT_FAILURE;
    }

    printf("[Consumer] Нове значення для ключа %u успішно оновлено на %lu\n", key, value);

    close(map_fd);
    return EXIT_SUCCESS;
}
