// loader.c — Класичний завантажувач C за допомогою libbpf
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <cgroup_path> <ip_to_block>\n", argv[0]);
        return 1;
    }

    const char *cgroup_path = argv[1];
    const char *ip_str = argv[2];

    int cgroup_fd = -1;
    int ret = 1;
    struct bpf_object *obj = NULL;

    // 1. Відкриваємо каталог cgroup v2
    cgroup_fd = open(cgroup_path, O_RDONLY);
    if (cgroup_fd < 0) {
        perror("Не вдалося відкрити cgroup каталог");
        return 1;
    }

    // 2. Завантажуємо eBPF об'єктний файл
    obj = bpf_object__open_file("cgroup_fw.bpf.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "Не вдалося відкрити eBPF об'єкт\n");
        goto cleanup;
    }

    if (bpf_object__load(obj)) {
        fprintf(stderr, "Не вдалося завантажити eBPF програму в ядро\n");
        goto cleanup;
    }

    // 3. Знаходимо програму та мапу за іменами
    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "cgroup_egress_firewall");
    if (!prog) {
        fprintf(stderr, "Програму cgroup_egress_firewall не знайдено\n");
        goto cleanup;
    }

    struct bpf_map *map = bpf_object__find_map_by_name(obj, "blocklist");
    if (!map) {
        fprintf(stderr, "Мапу blocklist не знайдено\n");
        goto cleanup;
    }

    int prog_fd = bpf_program__fd(prog);
    int map_fd = bpf_map__fd(map);

    // 4. Перетворюємо рядкову IP-адресу у бінарне число та оновлюємо мапу
    struct in_addr addr;
    if (inet_pton(AF_INET, ip_str, &addr) != 1) {
        fprintf(stderr, "Некоректний формат IP-адреси: %s\n", ip_str);
        goto cleanup;
    }

    __u32 key = addr.s_addr;
    __u64 initial_count = 0;
    if (bpf_map_update_elem(map_fd, &key, &initial_count, BPF_ANY) < 0) {
        perror("Помилка оновлення BPF мапи");
        goto cleanup;
    }

    // 5. Прикріплюємо BPF-програму до cgroup v2 із прапорцем BPF_F_ALLOW_MULTI
    if (bpf_prog_attach(prog_fd, cgroup_fd, BPF_CGROUP_INET_EGRESS, BPF_F_ALLOW_MULTI) < 0) {
        perror("Помилка прикріплення BPF програми до cgroup");
        goto cleanup;
    }

    printf("Файрвол успішно активовано на cgroup '%s'. Заблоковано IP: %s\n", cgroup_path, ip_str);
    printf("Натисніть Ctrl+C для завершення роботи...\n");

    // Очікуємо сигналу завершення
    while (1) {
        sleep(5);
    }

    ret = 0;

cleanup:
    if (obj) {
        bpf_object__close(obj);
    }
    if (cgroup_fd >= 0) {
        close(cgroup_fd);
    }
    return ret;
}
