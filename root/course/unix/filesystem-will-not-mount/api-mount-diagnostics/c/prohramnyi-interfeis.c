#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>

/* Визначення номерів системних викликів, якщо вони відсутні в старих версіях libc */
#ifndef __NR_fsopen
#define __NR_fsopen 430
#define __NR_fsconfig 431
#define __NR_fsmount 432
#define __NR_move_mount 429
#endif

#define FSCONFIG_SET_STRING 1
#define FSCONFIG_SET_FLAG   0
#define FSCONFIG_CMD_CREATE 6

int mount_via_new_api(const char *source, const char *target, const char *fstype) {
    /* 1. Створення контексту файлової системи */
    int fs_fd = syscall(__NR_fsopen, fstype, 0);
    if (fs_fd < 0) {
        perror("fsopen");
        return -1;
    }

    /* 2. Поетапне передавання параметрів конфігурації */
    syscall(__NR_fsconfig, fs_fd, FSCONFIG_SET_STRING, "source", source, 0);
    syscall(__NR_fsconfig, fs_fd, FSCONFIG_SET_FLAG, "ro", NULL, 0);
    syscall(__NR_fsconfig, fs_fd, FSCONFIG_SET_STRING, "errors", "remount-ro", 0);

    /* 3. Команда ядру зчитати суперблок та ініціалізувати інстанс ФС */
    if (syscall(__NR_fsconfig, fs_fd, FSCONFIG_CMD_CREATE, NULL, NULL, 0) < 0) {
        perror("fsconfig(CREATE)");
        close(fs_fd);
        return -1;
    }

    /* 4. Матеріалізація суперблоку та отримання дескриптора дерева */
    int mnt_fd = syscall(__NR_fsmount, fs_fd, 0, 0);
    close(fs_fd);
    if (mnt_fd < 0) {
        perror("fsmount");
        return -1;
    }

    /* 5. Атомарне прикріплення дерева монтування до цільового каталогу */
    if (syscall(__NR_move_mount, mnt_fd, "", AT_FDCWD, target, 0x00000004 /* MOVE_MOUNT_F_EMPTY_PATH */) < 0) {
        perror("move_mount");
        close(mnt_fd);
        return -1;
    }

    close(mnt_fd);
    return 0;
}
