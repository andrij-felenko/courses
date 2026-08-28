#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <net/if.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <rx_ifname> <tx_ifname>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *rx_ifname = argv[1];
    const char *tx_ifname = argv[2];

    unsigned int rx_ifindex = if_nametoindex(rx_ifname);
    unsigned int tx_ifindex = if_nametoindex(tx_ifname);

    if (!rx_ifindex || !tx_ifindex) {
        perror("Не вдалося отримати ifindex для мережевих інтерфейсів");
        return EXIT_FAILURE;
    }

    /* Відкриття та завантаження BPF-об'єкта */
    struct bpf_object *obj = bpf_object__open_file("xdp_router_kern.o", NULL);
    if (!obj) {
        fprintf(stderr, "Помилка відкриття файлу bpf об'єкта\n");
        return EXIT_FAILURE;
    }

    if (bpf_object__load(obj)) {
        fprintf(stderr, "Помилка завантаження eBPF-програми у ядро\n");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* Отримання дескрипторів карт */
    int cpu_map_fd = bpf_object__find_map_fd_by_name(obj, "cpu_map");
    int dev_map_fd = bpf_object__find_map_fd_by_name(obj, "tx_dev_map");

    if (cpu_map_fd < 0 || dev_map_fd < 0) {
        fprintf(stderr, "Помилка знаходження BPF-карт\n");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* Конфігурація CPUMAP: налаштовуємо CPU ID 1 із розміром черги 2048 */
    struct bpf_cpumap_val cpu_val = {
        .qsize = 2048,
        .bpf_prog = {.fd = 0}
    };
    __u32 cpu_key = 1;
    if (bpf_map_update_elem(cpu_map_fd, &cpu_key, &cpu_val, BPF_ANY) < 0) {
        perror("Помилка оновлення елемента CPUMAP");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* Конфігурація DEVMAP: додаємо tx_ifindex у карту */
    struct bpf_devmap_val dev_val = {
        .ifindex = tx_ifindex,
        .bpf_prog = {.fd = 0}
    };
    __u32 dev_key = tx_ifindex;
    if (bpf_map_update_elem(dev_map_fd, &dev_key, &dev_val, BPF_ANY) < 0) {
        perror("Помилка оновлення елемента DEVMAP");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    /* Пошук XDP-програми та прив'язка до RX-інтерфейсу */
    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "xdp_router_entry");
    int prog_fd = bpf_program__fd(prog);

    DECLARE_LIBBPF_OPTS(bpf_xdp_attach_opts, opts);
    if (bpf_xdp_attach(rx_ifindex, prog_fd, XDP_FLAGS_UPDATE_IF_NOEXIST, &opts) < 0) {
        perror("Помилка прикріплення XDP програми до інтерфейсу");
        bpf_object__close(obj);
        return EXIT_FAILURE;
    }

    printf("XDP-маршрутизатор успішно запущено на %s -> %s\n", rx_ifname, tx_ifname);
    printf("Натисніть Ctrl+C для зупинки...\n");

    while (1) {
        sleep(1);
    }

    /* Відкріплення XDP програми */
    bpf_xdp_detach(rx_ifindex, 0, &opts);
    bpf_object__close(obj);
    return EXIT_SUCCESS;
}
