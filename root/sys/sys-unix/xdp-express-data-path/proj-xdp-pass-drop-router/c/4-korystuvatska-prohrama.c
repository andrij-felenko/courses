/* C Implementation: Manual lifecycle management using libbpf C API */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <net/if.h>
#include <linux/if_link.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <interface> <path_to_bpf_obj>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *ifname = argv[1];
    const char *bpf_file = argv[2];

    /* Отримуємо числовий системний індекс мережевого інтерфейсу */
    unsigned int ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        perror("Помилка if_nametoindex");
        return EXIT_FAILURE;
    }

    /* 1. Відкриваємо та завантажуємо BPF-об'єктний файл */
    struct bpf_object *obj = bpf_object__open_file(bpf_file, NULL);
    if (!obj) {
        fprintf(stderr, "Не вдалося відкрити BPF об'єкт %s\n", bpf_file);
        return EXIT_FAILURE;
    }

    if (bpf_object__load(obj)) {
        fprintf(stderr, "Не вдалося завантажити BPF програму в ядро (помилка верифікатора)\n");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* 2. Знаходимо програму у завантаженому об'єкті за її назвою у SEC() */
    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "xdp_router_filter");
    if (!prog) {
        fprintf(stderr, "Не знайдено секцію xdp_router_filter у BPF об'єкті\n");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    int prog_fd = bpf_program__fd(prog);

    /* 3. Прив'язуємо XDP програму спочатку у Native режимі (XDP_FLAGS_DRV_MODE) */
    __u32 attach_flags = XDP_FLAGS_DRV_MODE;
    int err = bpf_xdp_attach(ifindex, prog_fd, attach_flags, NULL);
    if (err) {
        fprintf(stderr, "Native XDP не підтримується драйвером (код %d), пробуємо Generic mode...\n", err);
        attach_flags = XDP_FLAGS_SKB_MODE;
        err = bpf_xdp_attach(ifindex, prog_fd, attach_flags, NULL);
        if (err) {
            fprintf(stderr, "Помилка bpf_xdp_attach: %s\n", strerror(-err));
            bpf_object__close(obj);
            return EXIT_FAILURE;
        }
    }

    printf("XDP програму успішно завантажено на інтерфейс %s (ifindex %u)!\n", ifname, ifindex);
    printf("Натисніть Ctrl+C для вивантаження та завершення...\n");

    /* Тримаємо процес активним, поки працює XDP хук */
    while (1) {
        sleep(1);
    }

    /* Відв'язуємо програму та звільняємо ресурси при виході */
    bpf_xdp_detach(ifindex, attach_flags, NULL);
    bpf_object__close(obj);
    return EXIT_SUCCESS;
}
