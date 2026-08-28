/*
 * msix_inspector.c — Перевірка векторів MSI-X та конфігурація SMP Affinity (C11)
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

static void set_irq_affinity(const char *irq_str, int cpu_id)
{
    char path[256];
    snprintf(path, sizeof(path), "/proc/irq/%s/smp_affinity_list", irq_str);

    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return;
    }

    char cpu_buf[32];
    int len = snprintf(cpu_buf, sizeof(cpu_buf), "%d\n", cpu_id);
    if (write(fd, cpu_buf, len) < 0) {
        fprintf(stderr, "Не вдалося записати спорідненість для IRQ %s: %s\n",
                irq_str, strerror(errno));
    } else {
        printf("IRQ %s успішно прив'язано до CPU %d\n", irq_str, cpu_id);
    }

    close(fd);
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PCI BDF, наприклад 0000:01:00.0>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *bdf = argv[1];
    char msi_dir_path[256];
    snprintf(msi_dir_path, sizeof(msi_dir_path), "/sys/bus/pci/devices/%s/msi_irqs", bdf);

    DIR *dir = opendir(msi_dir_path);
    if (!dir) {
        fprintf(stderr, "Каталог %s не знайдено (пристрій не використовує MSI/MSI-X)\n",
                msi_dir_path);
        return EXIT_FAILURE;
    }

    printf("Аналіз переривань для пристрою %s:\n", bdf);
    struct dirent *entry;
    int cpu_counter = 0;
    long num_cpus = sysconf(_SC_NPROCESSORS_ONLN);

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') {
            continue;
        }

        char file_path[512];
        snprintf(file_path, sizeof(file_path), "%s/%s", msi_dir_path, entry->d_name);

        FILE *f = fopen(file_path, "r");
        if (!f) {
            continue;
        }

        char irq_type[32];
        if (fgets(irq_type, sizeof(irq_type), f)) {
            irq_type[strcspn(irq_type, "\r\n")] = '\0';
            printf("  • Знайдено вектор Linux IRQ %s (тип: %s)\n", entry->d_name, irq_type);

            /* Призначаємо спорідненість до CPU */
            int target_cpu = cpu_counter % (int)num_cpus;
            set_irq_affinity(entry->d_name, target_cpu);
            cpu_counter++;
        }
        fclose(f);
    }

    closedir(dir);
    return EXIT_SUCCESS;
}
