#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <errno.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <src_ifname> <target_ifname>\n", argv[0]);
        return 1;
    }

    const char *src_if = argv[1];
    const char *target_if = argv[2];

    // Перетворюємо текстові назви інтерфейсів у системні числові індекси (ifindex)
    unsigned int src_ifindex = if_nametoindex(src_if);
    unsigned int target_ifindex = if_nametoindex(target_if);

    if (!src_ifindex || !target_ifindex) {
        perror("Помилка if_nametoindex (інтерфейс не знайдено у системі)");
        return 1;
    }

    // 1. Відкриваємо ELF об'єктний файл програми eBPF
    struct bpf_object *obj = bpf_object__open_file("tc_redirect_kern.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "Не вдалося відкрити BPF ELF об'єктний файл\n");
        return 1;
    }

    // 2. Завантажуємо байт-код у ядро (проходження перевіряльника BPF Verifier)
    if (bpf_object__load(obj)) {
        fprintf(stderr, "Помилка BPF Verifier при завантаженні програми у ядро\n");
        bpf_object__close(obj);
        return 1;
    }

    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "tc_redirect_func");
    int prog_fd = bpf_program__fd(prog);

    // 3. Оновлюємо конфігураційну карту BPF Map індексом цільового пристрою
    struct bpf_map *map = bpf_object__find_map_by_name(obj, "config_map");
    int map_fd = bpf_map__fd(map);
    __u32 key = 0;
    if (bpf_map_update_elem(map_fd, &key, &target_ifindex, BPF_ANY) < 0) {
        perror("Помилка bpf_map_update_elem при записі у BPF карту");
        bpf_object__close(obj);
        return 1;
    }

    // 4. Налаштовуємо хук clsact та опції прикріплення Direct-Action
    DECLARE_LIBBPF_OPTS(bpf_tc_hook, hook,
        .sz = sizeof(struct bpf_tc_hook),
        .ifindex = src_ifindex,
        .attach_point = BPF_TC_INGRESS
    );

    DECLARE_LIBBPF_OPTS(bpf_tc_opts, opts,
        .sz = sizeof(struct bpf_tc_opts),
        .prog_fd = prog_fd
    );

    // Створюємо дисципліну черги clsact (операція є ідемпотентною)
    int err = bpf_tc_hook_create(&hook);
    if (err && err != -EEXIST) {
        fprintf(stderr, "Не вдалося створити clsact qdisc: %s\n", strerror(-err));
        bpf_object__close(obj);
        return 1;
    }

    // Прикріплюємо BPF програму до ingress хука у режимі direct-action
    err = bpf_tc_attach(&hook, &opts);
    if (err) {
        fprintf(stderr, "Не вдалося прикріпити TC BPF програму: %s\n", strerror(-err));
        bpf_object__close(obj);
        return 1;
    }

    printf("Успішно прикріплено eBPF TC програму до %s (ingress) -> redirect %s\n", src_if, target_if);
    printf("Натисніть Enter для відкріплення програми та завершення...\n");
    getchar();

    // 5. Очищення ресурсів: відкріплюємо фільтр та видаляємо об'єкт з пам'яті
    opts.prog_fd = 0;
    opts.prog_id = 0;
    bpf_tc_detach(&hook, &opts);
    bpf_object__close(obj);
    return 0;
}
