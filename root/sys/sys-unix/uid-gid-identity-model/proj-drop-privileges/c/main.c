#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <grp.h>
#include <pwd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/resource.h>
#include <sys/wait.h>

static uid_t g_uid = 65534;          /* nobody, якщо в базі його не знайдемо */
static gid_t g_gid = 65534;

/* Прив'язатися до порту нижче 1024 — єдине, заради чого тут потрібен root. */
static int bind_low(int port)
{
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family = AF_INET;
    a.sin_port   = htons(port);
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(fd, (struct sockaddr *)&a, sizeof a) != 0 || listen(fd, 16) != 0) {
        int e = errno; close(fd); errno = e; return -1;
    }
    return fd;
}

/* Ким процес є ЗАРАЗ — не за пам'яттю програми, а прочитавши числа в ядра. */
static void show(const char *label)
{
    uid_t r, e, s;  gid_t rg, eg, sg;  gid_t list[64];
    getresuid(&r, &e, &s);
    getresgid(&rg, &eg, &sg);
    int n = getgroups(64, list);
    printf("    %s uid=%u/%u/%u  gid=%u/%u/%u  групи=",
           label, (unsigned)r, (unsigned)e, (unsigned)s,
           (unsigned)rg, (unsigned)eg, (unsigned)sg);
    for (int i = 0; i < n; i++) printf("%s%u", i ? "," : "", (unsigned)list[i]);
    puts(n > 0 ? "" : "(немає)");
}

/* Чи лишилася дорога назад? Не питаємо — йдемо нею. */
static void probe_return(void)
{
    if (seteuid(0) != 0)
        printf("    seteuid(0)        -> %s  ← дороги назад немає\n", strerror(errno));
    else
        printf("    seteuid(0)        -> ПОВЕРНУЛИСЬ, euid=%u\n", (unsigned)geteuid());

    int fd = open("/etc/shadow", O_RDONLY);
    printf("    open(/etc/shadow) -> %s\n", fd >= 0 ? "ВІДКРИТО" : strerror(errno));
    if (fd >= 0) close(fd);
}

/* Те саме, але очима ядра. */
static void show_status(void)
{
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return;
    char line[256];
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, "Uid:", 4) || !strncmp(line, "Gid:", 4) ||
            !strncmp(line, "Groups:", 7) || !strncmp(line, "CapPrm:", 7) ||
            !strncmp(line, "CapEff:", 7))
            printf("    status  %s", line);
    fclose(f);
}

/* (1) Класика: «знижуємось до того, хто нас запустив». */
static void scene_setuid_getuid(int lfd)
{
    (void)lfd;
    puts("[1] Наївно: setuid(getuid()), код повернення нікого не цікавить");
    show("до зниження:");
    setuid(getuid());
    show("після зниження:");
    probe_return();
}

/* (2) Наївно інакше: міняємо лише ДІЮЧІ числа. */
static void scene_effective_only(int lfd)
{
    (void)lfd;
    puts("[2] Наївно: setegid/seteuid — міняємо лише діючі числа");
    if (setegid(g_gid) != 0 || seteuid(g_uid) != 0) { perror("    seteuid"); _exit(1); }
    show("після зниження:");
    probe_return();
}

/* Незворотний перехід. 0 — вдалося, -1 — ні; служба мусить померти на -1. */
static int drop_forever(uid_t uid, gid_t gid)
{
    if (setgroups(1, &gid)       != 0) return -1;   /* групи — першими */
    if (setresgid(gid, gid, gid) != 0) return -1;   /* усі три групові числа */
    if (setresuid(uid, uid, uid) != 0) return -1;   /* аж тепер користувач */

    uid_t r, e, s;  gid_t rg, eg, sg;               /* звірка читанням назад */
    if (getresuid(&r, &e, &s) != 0 || getresgid(&rg, &eg, &sg) != 0) return -1;
    if (r  != uid || e  != uid || s  != uid) { errno = EPERM; return -1; }
    if (rg != gid || eg != gid || sg != gid) { errno = EPERM; return -1; }

    gid_t list[2];
    int n = getgroups(2, list);
    if (n < 0 || n > 1 || (n == 1 && list[0] != gid)) { errno = EPERM; return -1; }
    return 0;
}

/* (3) Як належить — і перевірка, що назад справді нема куди. */
static void scene_correct(int lfd)
{
    puts("[3] Як треба: setgroups -> setresgid -> setresuid -> звірка");
    if (drop_forever(g_uid, g_gid) != 0) {
        printf("    зниження не вдалося: %s — тут служба мусить померти\n", strerror(errno));
        _exit(1);
    }
    show("після зниження:");
    probe_return();
    show_status();

    struct sockaddr_in sa;  socklen_t sl = sizeof sa;
    if (getsockname(lfd, (struct sockaddr *)&sa, &sl) == 0)
        printf("    успадкований сокет: порт %u — досі наш\n", ntohs(sa.sin_port));
    int fd2 = bind_low(81);
    printf("    bind(127.0.0.1:81) -> %s\n", fd2 >= 0 ? "успіх (!)" : strerror(errno));
    if (fd2 >= 0) close(fd2);
}

/* (4) Усі виклики вдалися. Служба однаково приречена. */
static void scene_nproc(int lfd)
{
    (void)lfd;
    puts("[4] Вичерпаний RLIMIT_NPROC: зниження вдається, а exec — ні");

    int p[2];                                  /* тримач місця: щоб у цільового */
    if (pipe(p) != 0) { perror("    pipe"); _exit(1); }
    pid_t helper = fork();                     /* користувача був хоч один процес */
    if (helper == 0) {
        close(p[0]);
        if (setresuid(g_uid, g_uid, g_uid) != 0) _exit(1);
        char c = 'x';
        if (write(p[1], &c, 1) != 1) _exit(1);
        pause();
        _exit(0);
    }
    close(p[1]);
    char c;
    if (read(p[0], &c, 1) != 1) { puts("    помічник не піднявся"); _exit(1); }

    struct rlimit rl = { 0, 0 };               /* «жодного процесу цьому uid» */
    if (setrlimit(RLIMIT_NPROC, &rl) != 0) { perror("    setrlimit"); _exit(1); }

    if (setresuid(g_uid, g_uid, g_uid) != 0)
        printf("    setresuid -> %s  (так відповідали ядра до 3.1)\n", strerror(errno));
    else
        puts("    setresuid -> успіх; звірка чисел теж пройде — усе ніби гаразд");

    execl("/bin/true", "true", (char *)NULL);
    printf("    execve    -> %s  ← ліміт наздогнав аж тут\n", strerror(errno));
    kill(helper, SIGKILL);
    waitpid(helper, NULL, 0);
}

static void run(void (*scene)(int), int lfd)
{
    pid_t pid = fork();
    if (pid == 0) { scene(lfd); _exit(0); }
    if (pid  > 0) waitpid(pid, NULL, 0);
    putchar('\n');
}

int main(void)
{
    struct passwd *pw = getpwnam("nobody");
    if (pw) { g_uid = pw->pw_uid; g_gid = pw->pw_gid; }

    if (geteuid() != 0) { puts("Потрібен root: усе цікаве починається з привілею."); return 1; }

    int lfd = bind_low(80);
    printf("bind(127.0.0.1:80) -> %s\n\n", lfd >= 0 ? "порт наш" : strerror(errno));
    if (lfd < 0) return 1;

    run(scene_setuid_getuid, lfd);
    run(scene_effective_only, lfd);
    run(scene_correct,        lfd);
    run(scene_nproc,          lfd);

    close(lfd);
    return 0;
}
