#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/mount.h>

/* Виклик класичного mount(2) у стилі C */
int mount_filesystem_classic(const char *source, const char *target, const char *fstype) {
    unsigned long flags = MS_RDONLY | MS_NODEV | MS_NOSUID | MS_NOEXEC;
    const char *data_opts = "errors=remount-ro,data=ordered";

    if (mount(source, target, fstype, flags, data_opts) < 0) {
        fprintf(stderr, "Помилка mount(2) для %s на %s: %s (errno=%d)\n",
                source, target, strerror(errno), errno);
        return -1;
    }
    return 0;
}
