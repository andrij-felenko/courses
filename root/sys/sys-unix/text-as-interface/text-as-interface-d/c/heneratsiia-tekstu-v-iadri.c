#include <stdio.h>
#include <stddef.h>

// Генерація форматованого запису таблиці монтування (C)
int format_mount_entry(char *buf, size_t buf_size, int id, int parent_id,
                       unsigned int major, unsigned int minor,
                       const char *mountpoint, const char *root, const char *fstype) {
    return snprintf(buf, buf_size, "%d %d %u:%u %s %s %s\n",
                    id, parent_id, major, minor, mountpoint, root, fstype);
}
