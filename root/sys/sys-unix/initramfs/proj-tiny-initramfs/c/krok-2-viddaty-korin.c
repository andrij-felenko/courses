#include <dirent.h>

static void die(const char *what)       /* PID 1 не має права вийти навіть з горя */
{
    printf("[init] %s: %s\n", what, strerror(errno));
    for (;;) pause();                   /* спиняємось, щоб напис лишився на екрані */
}

/* Вичистити старий корінь, НЕ переходячи меж монтувань: у чужого монтування
   інший st_dev — саме на ньому й спиняємось. */
static void wipe(int dirfd)
{
    DIR *d = fdopendir(dirfd);          /* dirfd тепер належить d */
    if (!d) { close(dirfd); return; }
    struct stat here;
    if (fstat(dirfd, &here) != 0) { closedir(d); return; }

    struct dirent *e;
    while ((e = readdir(d))) {
        if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, "..")) continue;
        struct stat st;
        if (fstatat(dirfd, e->d_name, &st, AT_SYMLINK_NOFOLLOW) != 0) continue;
        int isdir = S_ISDIR(st.st_mode);
        if (isdir) {
            if (st.st_dev != here.st_dev) continue;   /* межа монтування */
            int sub = openat(dirfd, e->d_name, O_RDONLY | O_DIRECTORY);
            if (sub >= 0) wipe(sub);
        }
        unlinkat(dirfd, e->d_name, isdir ? AT_REMOVEDIR : 0);
    }
    closedir(d);
}

static void switch_root(const char *newroot, const char *init)
{
    /* 1. перенести вже підняті монтування — піднімати їх удруге марна робота */
    static const char *keep[] = { "/dev", "/proc", "/sys" };
    for (int i = 0; i < 3; i++) {
        char dst[256];
        snprintf(dst, sizeof dst, "%s%s", newroot, keep[i]);
        if (mount(keep[i], dst, NULL, MS_MOVE, NULL) != 0) die(dst);
    }

    /* 2. стати в новий корінь і вичистити старий — саме це повертає пам'ять */
    if (chdir(newroot) != 0) die("chdir newroot");
    int oldroot = open("/", O_RDONLY | O_DIRECTORY);
    if (oldroot < 0) die("open /");
    wipe(oldroot);                      /* зникає й файл, що зараз виконується */

    /* 3. новий корінь — спершу в дереві монтувань, потім у самому процесі */
    if (mount(".", "/", NULL, MS_MOVE, NULL) != 0) die("mount --move . /");
    if (chroot(".") != 0) die("chroot");
    if (chdir("/")  != 0) die("chdir /");

    /* 4. той самий процес міняє образ — PID 1 не переривається ні на мить */
    execl(init, init, NULL);
    die(init);                          /* сюди потрапляємо лише при невдачі */
}
