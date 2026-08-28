#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/xattr.h>
#include <unistd.h>

int handle_oci_whiteout(const char *parent_dir, const char *entry_name) {
    /* Перевірка на маркер непрозорості каталогу */
    if (strcmp(entry_name, ".wh..wh..opq") == 0) {
        /* Спроба встановити системний атрибут trusted */
        if (setxattr(parent_dir, "trusted.overlay.opaque", "y", 1, 0) != 0) {
            /* Fallback для rootless просторів імен */
            setxattr(parent_dir, "user.overlay.opaque", "y", 1, 0);
        }
        return 1; /* Оброблено як спецмаркер */
    }

    /* Перевірка на видалення конкретного файлу */
    if (strncmp(entry_name, ".wh.", 4) == 0) {
        const char *target_filename = entry_name + 4;
        char whiteout_path[1024];
        snprintf(whiteout_path, sizeof(whiteout_path), "%s/%s", parent_dir, target_filename);

        /* Створення спеціального символьного пристрою ядра whiteout (0:0) */
        dev_t dev = makedev(0, 0);
        if (mknod(whiteout_path, S_IFCHR | 0600, dev) != 0) {
            perror("Помилка створення вузла whiteout через mknod");
            return -1;
        }
        return 1; /* Оброблено як спецмаркер */
    }

    return 0; /* Звичайний файл або каталог */
}
