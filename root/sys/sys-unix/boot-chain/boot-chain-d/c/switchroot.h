/*
 * switch_root: перенесення псевдо-ФС, знищення rootfs у пам'яті, атомарна
 * заміна кореня і execv справжнього init — усе в тому самому процесі PID 1.
 */
#ifndef SWITCHROOT_H
#define SWITCHROOT_H

enum sr_status {
    SR_OK = 0,
    SR_ERR_PATH,           /* шлях не влазить у PATH_MAX */
    SR_ERR_NOT_MOUNTPOINT, /* новий корінь не є точкою монтування */
    SR_ERR_NO_INIT,        /* у новому корені немає виконуваного init */
    SR_ERR_NOT_RAMFS,      /* поточний "/" не ramfs/tmpfs — чистити не можна */
    SR_ERR_OPEN_ROOT,      /* не відкрився старий корінь */
    SR_ERR_MOVE,           /* MS_MOVE псевдо-ФС не вдався */
    SR_ERR_CHDIR,
    SR_ERR_CHROOT,
    SR_ERR_EXEC
};

const char *sr_strerror(enum sr_status st);

/* 1. Перевірка: /sysroot — окреме монтування, всередині є виконуваний init. */
enum sr_status sr_check_new_root(const char *new_root, const char *init_path);
/* 2. MS_MOVE для /dev, /proc, /sys, /run у новий корінь. */
enum sr_status sr_move_pseudo_mounts(const char *new_root);
/* 3. Деструктивний обхід rootfs: unlink/rmdir усього, що на тій самій ФС. */
enum sr_status sr_purge_old_root(int old_root_fd);
/* 4. chdir + MS_MOVE(".", "/") + chroot(".") + chdir("/"). */
enum sr_status sr_pivot(const char *new_root);
/* 1–5 разом; за успіху не повертається — процес уже виконує новий init. */
enum sr_status sr_switch_root(const char *new_root, const char *init_path, char *const argv[]);

#endif /* SWITCHROOT_H */
