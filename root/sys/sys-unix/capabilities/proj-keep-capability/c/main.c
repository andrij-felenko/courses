#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <grp.h>
#include <pwd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <sys/wait.h>
#include <linux/capability.h>

#define CAPMASK(c) (1u << (c))       /* можливості 0..31 живуть у першому слові */
#define NBS        CAPMASK(CAP_NET_BIND_SERVICE)      /* номер 10, тобто 0x400 */

static uid_t g_uid = 65534;                       /* nobody, якщо бази не буде */
static gid_t g_gid = 65534;

/* capset/capget glibc не загортає — кличемо їх напряму.
   pid = 0 в заголовку означає «цей потік», і нічого іншого ядро не бере. */
static int caps_set(uint32_t permitted, uint32_t effective, uint32_t inheritable)
{
    struct __user_cap_header_struct h = { _LINUX_CAPABILITY_VERSION_3, 0 };
    struct __user_cap_data_struct   d[2];
    memset(d, 0, sizeof d);          /* друге слово — можливості 32..40: гасимо */
    d[0].permitted   = permitted;
    d[0].effective   = effective;
    d[0].inheritable = inheritable;
    return syscall(SYS_capset, &h, d);
}

static int caps_get(uint64_t *permitted, uint64_t *effective)
{
    struct __user_cap_header_struct h = { _LINUX_CAPABILITY_VERSION_3, 0 };
    struct __user_cap_data_struct   d[2];
    if (syscall(SYS_capget, &h, d) != 0) return -1;
    *permitted = ((uint64_t)d[1].permitted << 32) | d[0].permitted;
    *effective = ((uint64_t)d[1].effective << 32) | d[0].effective;
    return 0;
}

static void show(const char *label)
{
    uint64_t prm = 0, eff = 0;
    uid_t r, e, s;
    if (getresuid(&r, &e, &s) != 0 || caps_get(&prm, &eff) != 0) { perror("show"); return; }
    printf("    %-20s uid=%u/%u/%u  CapPrm=%016llx CapEff=%016llx\n",
           label, (unsigned)r, (unsigned)e, (unsigned)s,
           (unsigned long long)prm, (unsigned long long)eff);
}

/* Стеля: усе, що колись зможе потрапити в дозволені через exec.
   Звужувати її вільно лише тому, хто має CAP_SETPCAP у діючих, — тобто ще root. */
static int bound_to_only(int keep)
{
    int last = 40;
    FILE *f = fopen("/proc/sys/kernel/cap_last_cap", "r");
    if (f) { if (fscanf(f, "%d", &last) != 1) last = 40; fclose(f); }
    for (int c = 0; c <= last; c++) {
        if (c == keep) continue;
        if (prctl(PR_CAPBSET_DROP, c, 0, 0, 0) != 0 && errno != EINVAL) return -1;
    }
    return 0;
}

/* Кроки 1–3: звузити стелю, підняти прапорець, стати непривілейованим. */
static int drop_uid_keeping_caps(int keep)
{
    if (bound_to_only(keep)                != 0) return -1;
    if (prctl(PR_SET_KEEPCAPS, 1, 0, 0, 0) != 0) return -1;

    if (setgroups(1, &g_gid)               != 0) return -1;   /* групи — першими */
    if (setresgid(g_gid, g_gid, g_gid)     != 0) return -1;
    if (setresuid(g_uid, g_uid, g_uid)     != 0) return -1;   /* аж тепер користувач */
    return 0;
}

/* Кроки 4–5: лишити рівно одну назву, повернути її в діючі, звірити з ядром. */
static int narrow_caps_to(int keep)
{
    uint64_t prm = 0, eff = 0;
    uid_t r, e, s;

    if (caps_set(CAPMASK(keep), CAPMASK(keep), 0) != 0) return -1;
    if (prctl(PR_SET_KEEPCAPS, 0, 0, 0, 0)        != 0) return -1;

    if (caps_get(&prm, &eff) != 0)                      return -1;
    if (prm != CAPMASK(keep) || eff != CAPMASK(keep)) { errno = EPERM; return -1; }
    if (getresuid(&r, &e, &s) != 0)                     return -1;
    if (r != g_uid || e != g_uid || s != g_uid)       { errno = EPERM; return -1; }
    return 0;
}

static void try_bind(int port)
{
    struct sockaddr_in a;
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) { perror("    socket"); return; }
    memset(&a, 0, sizeof a);
    a.sin_family = AF_INET;
    a.sin_port   = htons(port);
    a.sin_addr.s_addr = htonl(INADDR_ANY);
    printf("    bind(0.0.0.0:%d)     -> %s\n", port,
           bind(fd, (struct sockaddr *)&a, sizeof a) == 0 ? "порт наш" : strerror(errno));
    close(fd);
}

/* (1) Усе те саме, лише без одного рядка. */
static void scene_no_keepcaps(void)
{
    puts("[1] Без KEEPCAPS");
    show("до зниження:");
    if (setgroups(1, &g_gid)           != 0 ||
        setresgid(g_gid, g_gid, g_gid) != 0 ||
        setresuid(g_uid, g_uid, g_uid) != 0) { perror("    зниження"); _exit(1); }
    show("після зниження:");
    if (caps_set(NBS, NBS, 0) != 0)
        printf("    capset               -> %s  ← брати вже нема звідки\n", strerror(errno));
    try_bind(443);
}

/* (2) Стеля -> прапорець -> зниження -> capset -> звірка. */
static void scene_keepcaps(void)
{
    int fd;
    puts("[2] З KEEPCAPS");
    if (drop_uid_keeping_caps(CAP_NET_BIND_SERVICE) != 0) {
        printf("    зниження не вдалося: %s — тут служба мусить померти\n", strerror(errno));
        _exit(1);
    }
    show("після зниження:");
    if (narrow_caps_to(CAP_NET_BIND_SERVICE) != 0) {
        printf("    звуження не вдалося: %s — і тут теж\n", strerror(errno));
        _exit(1);
    }
    show("після capset:");
    try_bind(443);
    fd = open("/etc/shadow", O_RDONLY);
    printf("    /etc/shadow          -> %s\n", fd >= 0 ? "ВІДКРИТО" : strerror(errno));
    if (fd >= 0) close(fd);

    fflush(stdout);                       /* що дістанеться запущеному помічникові */
    execl("/bin/sh", "sh", "-c",
          "sed -n 's/^CapPrm:/    після exec: CapPrm:/p' /proc/self/status", (char *)NULL);
    perror("    execl");
}

static void run(void (*scene)(void))
{
    pid_t pid = fork();                   /* зниження безповоротне: сцена — на процес */
    if (pid == 0) { scene(); _exit(0); }
    if (pid  > 0) waitpid(pid, NULL, 0);
    putchar('\n');
}

int main(void)
{
    struct passwd *pw = getpwnam("nobody");
    if (pw) { g_uid = pw->pw_uid; g_gid = pw->pw_gid; }
    if (geteuid() != 0) { puts("Потрібен root: усе цікаве починається з привілею."); return 1; }

    run(scene_no_keepcaps);
    run(scene_keepcaps);
    return 0;
}
