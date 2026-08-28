#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <errno.h>

int mount_overlay_rootfs(const char **lower_dirs, size_t lower_count,
                         const char *upper_dir, const char *work_dir,
                         const char *merged_target) {
    /* Розрахунок необхідної довжини рядка опцій lowerdir */
    size_t opt_len = 512;
    for (size_t i = 0; i < lower_count; i++) {
        opt_len += strlen(lower_dirs[i]) + 1;
    }
    opt_len += strlen(upper_dir) + strlen(work_dir) + 64;

    char *options = (char *)malloc(opt_len);
    if (!options) {
        perror("Помилка виділення динамічної пам'яті");
        return -1;
    }

    strcpy(options, "lowerdir=");
    for (size_t i = 0; i < lower_count; i++) {
        strcat(options, lower_dirs[i]);
        if (i + 1 < lower_count) {
            strcat(options, ":");
        }
    }

    char buf[512];
    snprintf(buf, sizeof(buf), ",upperdir=%s,workdir=%s", upper_dir, work_dir);
    strcat(options, buf);

    /* Виклик системного монтування OverlayFS у ядрі */
    int ret = mount("overlay", merged_target, "overlay", 0, options);
    if (ret != 0) {
        fprintf(stderr, "Помилка системного виклику mount (%s): %s\n", merged_target, strerror(errno));
        free(options);
        return -1;
    }

    printf("Успішно змонтовано OverlayFS rootfs у %s (кількість нижніх шарів: %zu)\n", merged_target, lower_count);
    free(options);
    return 0;
}
