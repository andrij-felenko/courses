/* lockdown-probe.c — які двері в ядро відчинені на цій машині й чому зачинені решта.
 * gcc -O2 -o lockdown-probe lockdown-probe.c      запускати від root, x86-64
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#if defined(__i386__) || defined(__x86_64__)
#include <sys/io.h>                       /* ioperm() є лише на x86 */
#endif

#define CAP_SYS_RAWIO 17

static int  kmsg = -1;                    /* /dev/kmsg, поставлений на кінець журналу */
static char note[300];                    /* сюди лягає знайдений рядок Lockdown: */

/* Забираємо все, що ядро дописало від попереднього стуку, і шукаємо слід блокування. */
static int lockdown_said_no(void)
{
    char rec[8192];
    int found = 0;

    note[0] = '\0';
    if (kmsg < 0)
        return 0;
    for (;;) {
        ssize_t n = read(kmsg, rec, sizeof rec - 1);
        if (n < 0) {
            if (errno == EPIPE) continue;         /* старі записи витиснули — читаємо далі */
            break;                                /* EAGAIN: нового більше немає */
        }
        rec[n] = '\0';
        char *p = strstr(rec, "Lockdown: ");
        if (p && !found) {
            char *nl = strchr(p, '\n');
            if (nl) *nl = '\0';
            snprintf(note, sizeof note, "%s", p);
            found = 1;
        }
    }
    return found;
}

static unsigned long long cap_eff(void)
{
    unsigned long long v = 0;
    char line[256];
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return 0;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, "CapEff:", 7)) { v = strtoull(line + 7, NULL, 16); break; }
    fclose(f);
    return v;
}

static int knock_devmem(void)   /* перевірка стоїть в open_port() — тобто на відкритті */
{
    int fd = open("/dev/mem", O_RDONLY);
    if (fd < 0) return -errno;
    close(fd);
    return 0;
}

static int knock_kcore(void)
{
    int fd = open("/proc/kcore", O_RDONLY);
    if (fd < 0) return -errno;
    close(fd);
    return 0;
}

static int knock_ioport(void)
{
#if defined(__i386__) || defined(__x86_64__)
    if (ioperm(0x80, 1, 1) < 0) return -errno;    /* лише просимо дозвіл, у порт не пишемо */
    ioperm(0x80, 1, 0);
    return 0;
#else
    return -ENOSYS;
#endif
}

/* MSR: перевірка стоїть НЕ на відкритті, а на записі. Пишемо 4 байти — ядро спитає
 * блокування, потім спіткнеться об «довжина не кратна 8» і поверне EINVAL,
 * так і не діставшись жодного регістра. */
static int knock_msr(void)
{
    unsigned int half = 0;
    int fd = open("/dev/cpu/0/msr", O_RDWR);
    if (fd < 0) return -errno;
    ssize_t r = pwrite(fd, &half, sizeof half, 0x1b0 /* IA32_ENERGY_PERF_BIAS */);
    int e = (r < 0) ? -errno : 0;
    close(fd);
    return (e == -EINVAL) ? 0 : e;                /* EINVAL = блокування пропустило */
}

static int perf_knock(int kernel_regs)
{
    struct perf_event_attr a;
    memset(&a, 0, sizeof a);
    a.type = PERF_TYPE_SOFTWARE;
    a.size = sizeof a;
    a.config = PERF_COUNT_SW_CPU_CLOCK;
    a.sample_period = 1000000;
    a.sample_type = PERF_SAMPLE_IP;
    a.disabled = 1;
    if (kernel_regs) {
        a.sample_type |= PERF_SAMPLE_REGS_INTR;   /* саме це просить регістри ядра */
        a.sample_regs_intr = 1;                   /* один дійсний біт маски — і досить */
    }
    int fd = syscall(__NR_perf_event_open, &a, 0, -1, -1, 0);
    if (fd < 0) return -errno;
    close(fd);
    return 0;
}
static int knock_perf_plain(void) { return perf_knock(0); }
static int knock_perf_regs(void)  { return perf_knock(1); }

static const struct door {
    const char *call;                             /* лише ASCII: за ним іде вирівняне поле */
    int (*knock)(void);
} doors[] = {
    { "open(\"/dev/mem\")",            knock_devmem     },
    { "ioperm(0x80, 1, 1)",            knock_ioport     },
    { "pwrite(\"/dev/cpu/0/msr\")",    knock_msr        },
    { "open(\"/proc/kcore\")",         knock_kcore      },
    { "perf_event_open()",             knock_perf_plain },
    { "perf_event_open(+REGS_INTR)",   knock_perf_regs  },
};

static const char *verdict(int rc, int said, unsigned long long eff)
{
    if (rc == 0)       return "двері відчинені";
    if (said)          return "зачинило блокування";
    if (rc == -EPERM && !((eff >> CAP_SYS_RAWIO) & 1))
                       return "−EPERM, журнал мовчить: найпевніше бракує CAP_SYS_RAWIO";
    if (rc == -EPERM)  return "−EPERM без сліду блокування: інший сторож";
    if (rc == -EACCES) return "відмовив обов'язковий контроль доступу";
    if (rc == -ENOENT || rc == -ENXIO || rc == -ENODEV)
                       return "дверей немає: ядро зібрано без цього інтерфейсу";
    if (rc == -ENOSYS) return "немає на цій архітектурі";
    return "інша причина";
}

int main(void)
{
    char buf[128];
    int fd = open("/sys/kernel/security/lockdown", O_RDONLY);
    if (fd < 0) {
        printf("оголошений рівень: файла немає (%s)\n", strerror(errno));
    } else {
        ssize_t n = read(fd, buf, sizeof buf - 1);
        buf[n > 0 ? n : 0] = '\0';
        printf("оголошений рівень: %s", buf);
        close(fd);
    }

    unsigned long long eff = cap_eff();
    printf("CAP_SYS_RAWIO:     %s\n\n",
           (eff >> CAP_SYS_RAWIO) & 1 ? "є" : "НЕМАЄ — далі буде видно ваші права, а не політику");

    kmsg = open("/dev/kmsg", O_RDONLY | O_NONBLOCK);
    if (kmsg >= 0) lseek(kmsg, 0, SEEK_END);

    for (size_t i = 0; i < sizeof doors / sizeof *doors; i++) {
        int rc   = doors[i].knock();
        int said = lockdown_said_no();
        /* вирок друкуємо ОСТАННІМ: ширина поля рахує байти, а кирилиця в UTF-8
           займає по два — вирівняти можна лише те, що ліворуч від неї */
        printf("%-30s %-24s %s\n", doors[i].call,
               rc == 0 ? "пройшло" : strerror(-rc), verdict(rc, said, eff));
        if (note[0]) printf("%-30s %s\n", "", note);
    }
    return 0;
}
