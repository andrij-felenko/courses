#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <errno.h>

/* Формування рядка опцій та системний виклик mount(2) для OverlayFS */
int mount_container_rootfs(const char *lower_layers, const char *upper, 
                           const char *work, const char *target) {
    char options[2048];
    snprintf(options, sizeof(options), "lowerdir=%s,upperdir=%s,workdir=%s",
             lower_layers, upper, work);

    /* Системний виклик ядра mount */
    if (mount("overlay", target, "overlay", 0, options) != 0) {
        fprintf(stderr, "Помилка монтування rootfs (%s): %s\n", target, strerror(errno));
        return -1;
    }

    printf("Rootfs успішно змонтовано у %s\n", target);
    return 0;
}
