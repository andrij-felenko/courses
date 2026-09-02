#define _GNU_SOURCE
#include "switchroot.h"

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <unistd.h>

/* Магічні числа файлових систем, які живуть виключно в оперативній пам'яті. */
#ifndef RAMFS_MAGIC
#define RAMFS_MAGIC 0x858458f6
#endif
#ifndef TMPFS_MAGIC
#define TMPFS_MAGIC 0x01021994
#endif

static const char *const PSEUDO_MOUNTS[] = { "/dev", "/proc", "/sys", "/run", NULL };

const char *sr_strerror(enum sr_status st)
{
    switch (st) {
    case SR_OK:                 return "гаразд";
    case SR_ERR_PATH:           return "шлях задовгий";
    case SR_ERR_NOT_MOUNTPOINT: return "новий корінь не є точкою монтування";
    case SR_ERR_NO_INIT:        return "у новому корені немає виконуваного init";
    case SR_ERR_NOT_RAMFS:      return "поточний корінь не ramfs/tmpfs";
    case SR_ERR_OPEN_ROOT:      return "не вдалося відкрити старий корінь";
    case SR_ERR_MOVE:           return "MS_MOVE не вдався";
    case SR_ERR_CHDIR:          return "chdir не вдався";
    case SR_ERR_CHROOT:         return "chroot не вдався";
    case SR_ERR_EXEC:           return "execv не вдався";
    }
    return "невідома помилка";
}

static void warn_call(const char *call, const char *arg)
{
    fprintf(stderr, "switch_root: %s(%s): %s\n", call, arg ? arg : "", strerror(errno));
}

static int join_path(char *dst, size_t dst_size, const char *base, const char *tail)
{
    /* Провідний слеш у хвості з'їдаємо, щоб не вийшло "/sysroot//dev". */
    while (*tail == '/')
        ++tail;
    int n = snprintf(dst, dst_size, "%s/%s", base, tail);
    return (n < 0 || (size_t)n >= dst_size) ? -1 : 0;
}

/* Чи є шлях точкою монтування: пристрій відрізняється від пристрою батька. */
static int is_mount_point(const char *path)
{
    char parent[PATH_MAX];
    struct stat here, up;

    if (stat(path, &here) != 0)
        return 0;
    if (join_path(parent, sizeof(parent), path, "..") != 0)
        return 0;
    if (stat(parent, &up) != 0)
        return 0;

    return here.st_dev != up.st_dev || here.st_ino == up.st_ino;
}

enum sr_status sr_check_new_root(const char *new_root, const char *init_path)
{
    char full[PATH_MAX];

    if (!is_mount_point(new_root))
        return SR_ERR_NOT_MOUNTPOINT;
    if (join_path(full, sizeof(full), new_root, init_path) != 0)
        return SR_ERR_PATH;
    if (access(full, X_OK) != 0) {
        warn_call("access", full);
        return SR_ERR_NO_INIT;
    }
    return SR_OK;
}

enum sr_status sr_move_pseudo_mounts(const char *new_root)
{
    char target[PATH_MAX];
    enum sr_status result = SR_OK;

    for (int i = 0; PSEUDO_MOUNTS[i] != NULL; ++i) {
        const char *src = PSEUDO_MOUNTS[i];

        if (!is_mount_point(src)) {
            /* Наприклад, /run в аскетичному initramfs може й не бути. */
            fprintf(stderr, "switch_root: %s не змонтовано, пропускаємо\n", src);
            continue;
        }
        if (join_path(target, sizeof(target), new_root, src) != 0)
            return SR_ERR_PATH;

        /* Каталог у новому корені може бути відсутній: створюємо мовчки. */
        if (mkdir(target, 0755) != 0 && errno != EEXIST)
            warn_call("mkdir", target);

        if (mount(src, target, NULL, MS_MOVE, NULL) != 0) {
            warn_call("mount MS_MOVE", src);
            /* /run пережити можна, /dev і /proc — ні. */
            if (strcmp(src, "/run") != 0)
                result = SR_ERR_MOVE;
        }
    }
    return result;
}

/*
 * Рекурсивне знищення вмісту rootfs. Ключова умова — st_dev: усе, що лежить
 * на іншій файловій системі (новий корінь, уже перенесені псевдо-ФС), ми
 * навіть не намагаємось прибирати. util-linux робить той самий обхід уже
 * після MS_MOVE нового кореня, тримаючи відкритий дескриптор старого;
 * результат однаковий, бо межу все одно проводить st_dev.
 */
static void purge_dir(int dfd, dev_t root_dev)
{
    int dup_fd = dup(dfd);
    if (dup_fd < 0) {
        warn_call("dup", NULL);
        return;
    }

    DIR *dir = fdopendir(dup_fd);
    if (dir == NULL) {
        warn_call("fdopendir", NULL);
        close(dup_fd);
        return;
    }

    struct dirent *de;
    while ((de = readdir(dir)) != NULL) {
        if (strcmp(de->d_name, ".") == 0 || strcmp(de->d_name, "..") == 0)
            continue;

        struct stat sb;
        if (fstatat(dfd, de->d_name, &sb, AT_SYMLINK_NOFOLLOW) != 0)
            continue;
        if (sb.st_dev != root_dev)
            continue;  /* чужа ФС: /sysroot і все перенесене — недоторканні */

        int is_dir = S_ISDIR(sb.st_mode);
        if (is_dir) {
            int sub = openat(dfd, de->d_name,
                             O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
            if (sub >= 0) {
                purge_dir(sub, root_dev);
                close(sub);
            } else {
                warn_call("openat", de->d_name);
            }
        }

        if (unlinkat(dfd, de->d_name, is_dir ? AT_REMOVEDIR : 0) != 0 && errno != ENOENT)
            warn_call(is_dir ? "rmdir" : "unlink", de->d_name);
    }

    closedir(dir);  /* закриває dup_fd */
}

enum sr_status sr_purge_old_root(int old_root_fd)
{
    struct statfs sfs;
    struct stat sb;

    if (fstatfs(old_root_fd, &sfs) != 0) {
        warn_call("fstatfs", "/");
        return SR_ERR_OPEN_ROOT;
    }
    /* Запобіжник: якщо ми чомусь стоїмо на справжньому диску — не чіпаємо. */
    if (sfs.f_type != (__typeof__(sfs.f_type))RAMFS_MAGIC &&
        sfs.f_type != (__typeof__(sfs.f_type))TMPFS_MAGIC)
        return SR_ERR_NOT_RAMFS;

    if (fstat(old_root_fd, &sb) != 0) {
        warn_call("fstat", "/");
        return SR_ERR_OPEN_ROOT;
    }

    purge_dir(old_root_fd, sb.st_dev);
    return SR_OK;
}

enum sr_status sr_pivot(const char *new_root)
{
    if (chdir(new_root) != 0) {
        warn_call("chdir", new_root);
        return SR_ERR_CHDIR;
    }
    /* Ось той самий атомарний крок: змонтований диск стає коренем системи. */
    if (mount(".", "/", NULL, MS_MOVE, NULL) != 0) {
        warn_call("mount MS_MOVE", "/");
        return SR_ERR_MOVE;
    }
    if (chroot(".") != 0) {
        warn_call("chroot", ".");
        return SR_ERR_CHROOT;
    }
    if (chdir("/") != 0) {
        warn_call("chdir", "/");
        return SR_ERR_CHDIR;
    }
    return SR_OK;
}

enum sr_status sr_switch_root(const char *new_root, const char *init_path, char *const argv[])
{
    enum sr_status st = sr_check_new_root(new_root, init_path);
    if (st != SR_OK)
        return st;

    /* Дескриптор старого кореня беремо до будь-яких переміщень. */
    int old_root = open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (old_root < 0) {
        warn_call("open", "/");
        return SR_ERR_OPEN_ROOT;
    }

    st = sr_move_pseudo_mounts(new_root);
    if (st != SR_OK) {
        close(old_root);
        return st;
    }

    st = sr_purge_old_root(old_root);
    close(old_root);
    if (st == SR_ERR_NOT_RAMFS) {
        /* Не фатально: просто не звільнимо пам'ять, зате нічого не зіпсуємо. */
        fprintf(stderr, "switch_root: %s — пропускаємо очищення\n", sr_strerror(st));
    } else if (st != SR_OK) {
        return st;
    }

    st = sr_pivot(new_root);
    if (st != SR_OK)
        return st;

    execv(init_path, argv);

    /* Керування повернулося — образ не замінився, PID 1 лишився нашим. */
    warn_call("execv", init_path);
    return SR_ERR_EXEC;
}
