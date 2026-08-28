#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/syscall.h>
#include <sys/wait.h>

#define WORK "/tmp/pivot-probe"
#define IMG  WORK "/img"
#define DATA WORK "/data"
#define PROBE_FD 3          /* під цим номером дескриптор або переживе execve, або ні */

static void die(const char *what)
{
    fprintf(stderr, "    %s -> %s\n", what, strerror(errno));
    _exit(1);
}

/* Обгортки в glibc для pivot_root немає — кличемо за номером. */
static int do_pivot_root(const char *new_root, const char *put_old)
{
    return syscall(SYS_pivot_root, new_root, put_old);
}

/* Кілька імен із каталогу: доказ, у якому саме дереві ми стоїмо. */
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

/* Дерево монтувань очима ядра. needle != NULL — показати лише «/» і цікаві рядки. */
static void show_mounts(const char *label, const char *needle)
{
    FILE *f = fopen("/proc/self/mountinfo", "r");
    if (!f) { printf("  %s: mountinfo -> %s\n", label, strerror(errno)); return; }
    printf("  %s (/proc/self/mountinfo):\n", label);
    char line[4096];
    int total = 0, shown = 0;
    while (fgets(line, sizeof line, f)) {
        int id, parent; char dev[32], root[512], point[512];
        total++;
        /* формат: id parent major:minor корінь точка опції … - тип джерело … */
        if (sscanf(line, "%d %d %31s %511s %511s", &id, &parent, dev, root, point) != 5)
            continue;
        char *sep = strstr(line, " - ");
        const char *type = sep ? strtok(sep + 3, " \n") : NULL;
        if (!type) type = "?";
        if (needle && strcmp(point, "/") && !strstr(point, needle)) continue;
        printf("    id=%-4d %-7s root=%-24s point=%-32s %s\n", id, dev, root, point, type);
        shown++;
    }
    printf("    (усього рядків: %d, показано: %d)\n", total, shown);
    fclose(f);
}

static void write_file(const char *path, const char *data)
{
    int fd = open(path, O_WRONLY);
    if (fd < 0) return;                      /* setgroups на дуже старих ядрах відсутній */
    if (write(fd, data, strlen(data)) < 0) perror("    write");
    close(fd);
}

/* Стати нулем у власному просторі користувачів. Непривілейованому процесу
   дозволено записати рівно один рядок — відображення власного uid. */
static void map_self_to_root(uid_t uid, gid_t gid)
{
    char buf[64];
    write_file("/proc/self/setgroups", "deny");   /* без цього gid_map не приймуть */
    snprintf(buf, sizeof buf, "0 %u 1\n", (unsigned)uid);
    write_file("/proc/self/uid_map", buf);
    snprintf(buf, sizeof buf, "0 %u 1\n", (unsigned)gid);
    write_file("/proc/self/gid_map", buf);
}

/* Уся послідовність рушія контейнерів — від unshare до chdir("/"). */
static void enter_image(uid_t uid, gid_t gid, int cloexec)
{
    if (unshare(CLONE_NEWUSER | CLONE_NEWNS) != 0) die("unshare(NEWUSER|NEWNS)");
    map_self_to_root(uid, gid);

    /* корінь рекурсивно приватний: інакше подія піде в чужі простори */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) die("make-rprivate /");

    /* образ сам до себе: переносити нема чого, потрібен лише об'єкт монтування */
    if (mount(IMG, IMG, NULL, MS_BIND | MS_REC, NULL) != 0) die("bind образу самого до себе");

    /* свій procfs, інакше після підміни дивитися на дерево не буде звідки */
    if (mount("proc", IMG "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) != 0)
        printf("    (свій /proc не змонтувався: %s)\n", strerror(errno));

    /* дескриптор у господарську теку — відкритий ДО підміни кореня */
    int fd = open(DATA, O_RDONLY | O_DIRECTORY | (cloexec ? O_CLOEXEC : 0));
    if (fd < 0) die("open(" DATA ")");
    if (fd != PROBE_FD) {
        if (dup3(fd, PROBE_FD, cloexec ? O_CLOEXEC : 0) < 0) die("dup3");
        close(fd);
    }

    show_mounts("ДО", "pivot-probe");

    if (chdir(IMG) != 0)               die("chdir(образ)");
    if (do_pivot_root(".", ".") != 0)  die("pivot_root(\".\", \".\")");
    if (umount2(".", MNT_DETACH) != 0) die("umount2(\".\", MNT_DETACH)");
    if (chdir("/") != 0)               die("chdir(\"/\")");
}

/* Підйом «..», доки пристрій і вузол не перестануть мінятися. */
static void climb(void)
{
    struct stat prev, cur;
    if (stat(".", &prev) != 0) { perror("    stat(.)"); return; }
    for (int i = 1; i <= 8; i++) {
        if (chdir("..") != 0) { printf("    крок %d вгору -> %s\n", i, strerror(errno)); return; }
        if (stat(".", &cur) != 0) { perror("    stat(.)"); return; }
        printf("    крок %d вгору: %u:%u ino=%lu%s\n", i,
               major(cur.st_dev), minor(cur.st_dev), (unsigned long)cur.st_ino,
               (cur.st_dev == prev.st_dev && cur.st_ino == prev.st_ino) ? " — не змінилось, стеля" : "");
        if (cur.st_dev == prev.st_dev && cur.st_ino == prev.st_ino) { list_dir("стеля", "."); return; }
        prev = cur;
    }
}

/* Те, що виконується вже ПІСЛЯ execve — усередині нового кореня. */
static void payload(void)
{
    list_dir("корінь контейнера", "/");
    show_mounts("ПІСЛЯ", NULL);

    if (fchdir(PROBE_FD) != 0) {
        printf("    fchdir(%d) -> %s — дороги у від'єднане дерево немає\n",
               PROBE_FD, strerror(errno));
        return;
    }
    printf("    fchdir(%d) -> успіх: поточний каталог у від'єднаному дереві\n", PROBE_FD);
    list_dir("під дескриптором", ".");
    climb();
}

static void run(const char *title, int cloexec, uid_t uid, gid_t gid)
{
    printf("== %s ==\n", title);
    fflush(stdout);
    pid_t p = fork();
    if (p == 0) {
        enter_image(uid, gid, cloexec);
        char *av[] = { (char *)"/probe", (char *)"--payload", NULL };
        fflush(NULL);            /* інакше буфер stdout загине разом зі старим образом пам'яті */
        execv("/probe", av);
        die("execv(/probe)");
    }
    waitpid(p, NULL, 0);
    putchar('\n');
}

/* Свідомо зіпсований запуск: кожна пропущена дія дає свій код помилки. */
static void attempt(const char *title, int own_userns, int do_private, int do_bind,
                    int alien_userns, uid_t uid, gid_t gid)
{
    pid_t p = fork();
    if (p != 0) { waitpid(p, NULL, 0); return; }

    printf("  %s\n", title);
    int flags = CLONE_NEWNS | (own_userns ? CLONE_NEWUSER : 0);
    if (unshare(flags) != 0) { printf("    unshare -> %s\n", strerror(errno)); _exit(1); }
    if (own_userns) map_self_to_root(uid, gid);
    if (do_private && mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) die("make-rprivate");
    if (do_bind && mount(IMG, IMG, NULL, MS_BIND, NULL) != 0) die("bind");
    /* другий простір користувачів: простір монтувань лишається за першим,
       а можливостей у ньому в нас уже немає */
    if (alien_userns && unshare(CLONE_NEWUSER) != 0) die("другий unshare(NEWUSER)");

    if (chdir(IMG) != 0) die("chdir(образ)");
    if (do_pivot_root(".", ".") != 0) printf("    pivot_root -> %s\n", strerror(errno));
    else                              printf("    pivot_root -> несподіваний успіх\n");
    _exit(0);
}

static void copy_self(const char *dst)
{
    int in = open("/proc/self/exe", O_RDONLY);
    int out = open(dst, O_WRONLY | O_CREAT | O_TRUNC, 0755);
    if (in < 0 || out < 0) die("копіювання probe в образ");
    char buf[65536]; ssize_t n;
    while ((n = read(in, buf, sizeof buf)) > 0)
        if (write(out, buf, n) != n) die("write");
    close(in); close(out);
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "--payload")) { payload(); return 0; }

    /* ДО unshare: після нього getuid() дасть 65534, бо наш uid ще не відображено */
    uid_t uid = getuid();
    gid_t gid = getgid();

    mkdir(WORK, 0755); mkdir(IMG, 0755); mkdir(IMG "/proc", 0755); mkdir(DATA, 0755);
    close(open(DATA "/host-secret.txt", O_CREAT | O_WRONLY, 0644));
    close(open(IMG  "/only-in-image",   O_CREAT | O_WRONLY, 0644));
    copy_self(IMG "/probe");

    run("A. дескриптор без O_CLOEXEC", 0, uid, gid);
    run("Б. той самий дескриптор із O_CLOEXEC", 1, uid, gid);

    puts("== В. три способи не дійти до підміни ==");
    attempt("образ не прив'язали сам до себе:",            1, 1, 0, 0, uid, gid);
    attempt("простір монтувань належить чужому userns:",   1, 1, 1, 1, uid, gid);
    if (geteuid() == 0)
        attempt("корінь лишився спільним (лише під sudo):", 0, 0, 1, 0, uid, gid);
    else
        puts("  корінь лишився спільним: у безкореневому запуску не відтворюється (див. нижче)");
    return 0;
}
