#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <dirent.h>
#include <sys/stat.h>

/* Запис текстового значення у файл sysfs із обробкою помилок */
static int write_sysfs_str(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "[-] Помилка відкриття %s: %s\n", path, strerror(errno));
        return -1;
    }
    ssize_t len = strlen(val);
    ssize_t ret = write(fd, val, len);
    int saved_errno = errno;   /* close() і fprintf() можуть перетерти errno */
    close(fd);
    if (ret != len) {
        fprintf(stderr, "[-] Помилка запису '%s' у %s: %s\n", val, path, strerror(saved_errno));
        errno = saved_errno;   /* щоб виклик міг розібрати причину (EBUSY тощо) */
        return -1;
    }
    return 0;
}

/* Перевірка наявності шляху у sysfs */
static int sysfs_exists(const char *path) {
    return access(path, F_OK) == 0;
}

/* Прив'язка окремої VF до драйвера vfio-pci */
static int bind_vf_to_vfio(const char *vf_bdf, const char *vendor_id, const char *device_id) {
    char path[512];
    char id_str[64];

    /* 1. Відв'язуємо VF від поточного драйвера хоста (якщо він був прив'язаний) */
    snprintf(path, sizeof(path), "/sys/bus/pci/devices/%s/driver/unbind", vf_bdf);
    if (sysfs_exists(path)) {
        write_sysfs_str(path, vf_bdf);
    }

    /* 2. Реєструємо ідентифікатори Vendor/Device в vfio-pci */
    snprintf(id_str, sizeof(id_str), "%s %s", vendor_id, device_id);
    write_sysfs_str("/sys/bus/pci/drivers/vfio-pci/new_id", id_str);

    /* 3. Прив'язуємо BDF до vfio-pci */
    snprintf(path, sizeof(path), "/sys/bus/pci/drivers/vfio-pci/bind");
    if (write_sysfs_str(path, vf_bdf) < 0) {
        if (errno != EBUSY) {
            return -1;
        }
    }
    return 0;
}

/* Прогляд створених VF та визначення їхніх IOMMU груп */
static void inspect_iommu_groups(const char *pf_bdf) {
    char dir_path[512];
    snprintf(dir_path, sizeof(dir_path), "/sys/bus/pci/devices/%s", pf_bdf);

    DIR *dir = opendir(dir_path);
    if (!dir) return;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, "virtfn", 6) == 0) {
            char link_path[512];
            char target_path[512];
            snprintf(link_path, sizeof(link_path), "%s/%s", dir_path, entry->d_name);

            ssize_t len = readlink(link_path, target_path, sizeof(target_path) - 1);
            if (len > 0) {
                target_path[len] = '\0';
                char *vf_bdf = strrchr(target_path, '/');
                if (vf_bdf) vf_bdf++; else vf_bdf = target_path;

                char iommu_link[512];
                char iommu_target[512];
                snprintf(iommu_link, sizeof(iommu_link), "%s/%s/iommu_group", dir_path, entry->d_name);

                ssize_t i_len = readlink(iommu_link, iommu_target, sizeof(iommu_target) - 1);
                if (i_len > 0) {
                    iommu_target[i_len] = '\0';
                    char *grp_num = strrchr(iommu_target, '/');
                    if (grp_num) grp_num++; else grp_num = iommu_target;
                    printf("  └─ VF [%s]: %s → IOMMU Group: %s (/dev/vfio/%s)\n", 
                           entry->d_name, vf_bdf, grp_num, grp_num);
                }
            }
        }
    }
    closedir(dir);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Використання: %s <PF_BDF> <NUM_VFS>\n", argv[0]);
        printf("Приклад:     %s 0000:03:00.0 4\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *pf_bdf = argv[1];
    const char *num_vfs_str = argv[2];
    char path[512];

    printf("[+] Ініціалізація управління SR-IOV для PF: %s\n", pf_bdf);

    /* 1. Вимикаємо авто-прив'язку хостових драйверів для нових VF */
    snprintf(path, sizeof(path), "/sys/bus/pci/devices/%s/sriov_drivers_autoprobe", pf_bdf);
    if (write_sysfs_str(path, "0") < 0) {
        fprintf(stderr, "[!] Попередження: Не вдалося встановити sriov_drivers_autoprobe\n");
    }

    /* 2. Скидаємо існуючі VF до 0 */
    snprintf(path, sizeof(path), "/sys/bus/pci/devices/%s/sriov_numvfs", pf_bdf);
    write_sysfs_str(path, "0");

    /* 3. Задаємо нову кількість VF */
    if (write_sysfs_str(path, num_vfs_str) < 0) {
        fprintf(stderr, "[-] Фатальна помилка виділення %s VF для пристрою %s\n", num_vfs_str, pf_bdf);
        return EXIT_FAILURE;
    }

    printf("[+] Успішно створено %s VF для пристрою %s\n", num_vfs_str, pf_bdf);
    
    /* 4. Інспектуємо виділені IOMMU групи */
    inspect_iommu_groups(pf_bdf);

    return EXIT_SUCCESS;
}
