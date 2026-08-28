/* producer.c — Створення eBPF-мапи та її фіксація у bpffs */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>

#define PIN_PATH "/sys/fs/bpf/shared_stats_map"

int main(void) {
    uint32_t key = 42;
    uint64_t initial_value = 1000;

    /* Створення eBPF-мапи HASH: ключ 4 байти, значення 8 байтів, макс 1024 елементи */
    int map_fd = bpf_map_create(BPF_MAP_TYPE_HASH, "shared_stats", sizeof(key), sizeof(initial_value), 1024, NULL);
    if (map_fd < 0) {
        fprintf(stderr, "Помилка створення eBPF мапи: %s\n", strerror(errno));
        return EXIT_FAILURE;
    }

    /* Якщо раніше створена мапа вже існує у bpffs, видаляємо її перед фіксацією */
    unlink(PIN_PATH);

    /* Фіксація мапи у bpffs */
    if (bpf_obj_pin(map_fd, PIN_PATH) < 0) {
        fprintf(stderr, "Помилка фіксації мапи у %s: %s\n", PIN_PATH, strerror(errno));
        close(map_fd);
        return EXIT_FAILURE;
    }

    printf("[Producer] Мапу успішно створено та зафіксовано у %s\n", PIN_PATH);

    /* Запис початкового значення */
    if (bpf_map_update_elem(map_fd, &key, &initial_value, BPF_ANY) < 0) {
        fprintf(stderr, "Помилка запису в мапу: %s\n", strerror(errno));
        unlink(PIN_PATH);   /* розфіксація — це звичайний unlink() */
        close(map_fd);
        return EXIT_FAILURE;
    }

    printf("[Producer] Записано ключ %u зі значенням %lu. Закриваємо FD та виходимо.\n", key, initial_value);
    
    /* Закриваємо FD. Мапа не знищується, бо вона зафіксована у bpffs! */
    close(map_fd);
    return EXIT_SUCCESS;
}
