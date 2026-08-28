#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <sys/mount.h>
#include <unistd.h>

/* Обгортки fsopen/fsconfig/fsmount/move_mount є в glibc з 2.36;
   у старших версіях їх викликають через syscall(2). */

static int fail(int fs_fd, const char *what)
{
    char buf[256];
    ssize_t n = read(fs_fd, buf, sizeof buf - 1);   /* черга повідомлень контексту */
    if (n > 0) { buf[n] = '\0'; fprintf(stderr, "%s: %s\n", what, buf); }
    else       perror(what);
    return 1;
}

int main(void)
{
    int fs_fd = fsopen("overlay", FSOPEN_CLOEXEC);
    if (fs_fd < 0) { perror("fsopen"); return 1; }

    /* Перший доданий шар — найвищий. Двокрапку в імені екранувати НЕ треба. */
    if (fsconfig(fs_fd, FSCONFIG_SET_STRING, "lowerdir+", "/l/app", 0) ||
        fsconfig(fs_fd, FSCONFIG_SET_STRING, "lowerdir+", "/l/base:2026", 0) ||
        fsconfig(fs_fd, FSCONFIG_SET_STRING, "upperdir", "/state/upper", 0) ||
        fsconfig(fs_fd, FSCONFIG_SET_STRING, "workdir", "/state/work", 0) ||
        /* metacopy=on сам по собі буде відкинутий: він вимагає redirect_dir=on */
        fsconfig(fs_fd, FSCONFIG_SET_STRING, "redirect_dir", "on", 0) ||
        fsconfig(fs_fd, FSCONFIG_SET_STRING, "metacopy", "on", 0))
        return fail(fs_fd, "fsconfig");

    /* Саме тут спрацьовують усі перевірки шарів і сумісності опцій. */
    if (fsconfig(fs_fd, FSCONFIG_CMD_CREATE, NULL, NULL, 0))
        return fail(fs_fd, "create");

    int mnt_fd = fsmount(fs_fd, FSMOUNT_CLOEXEC, 0);
    if (mnt_fd < 0) return fail(fs_fd, "fsmount");

    if (move_mount(mnt_fd, "", AT_FDCWD, "/merged", MOVE_MOUNT_F_EMPTY_PATH)) {
        perror("move_mount");
        return 1;
    }
    close(mnt_fd);
    close(fs_fd);
    return 0;
}
