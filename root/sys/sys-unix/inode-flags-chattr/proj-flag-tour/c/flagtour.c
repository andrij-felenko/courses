/* flagtour.c — поставити FS_IMMUTABLE_FL і зібрати errno кожної забороненої дії.
 *
 *   cc -O2 -std=c11 -D_GNU_SOURCE -o flagtour flagtour.c
 *   sudo ./flagtour /var/tmp/tour.bin        # потрібна CAP_LINUX_IMMUTABLE
 *
 * Файл програма створює САМА (він не має існувати) і сама ж прибирає:
 * тур руйнівний за задумом — він пише в дескриптор і вкорочує файл.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <linux/fs.h>          /* FS_IOC_GETFLAGS, FS_IMMUTABLE_FL, … */
#include <linux/magic.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <sys/xattr.h>
#include <unistd.h>

#ifndef O_LARGEFILE
# define O_LARGEFILE 0
#endif
#ifndef STATX_ATTR_IMMUTABLE
# define STATX_ATTR_IMMUTABLE 0x00000010
#endif

#define NELEM(a) (sizeof(a) / sizeof((a)[0]))

static const char *PATH;      /* ціль */
static int  FD  = -1;         /* на ЧИТАННЯ: через нього йдуть обидва ioctl */
static int  WFD = -1;         /* на запис, відкритий ДО того, як став прапорець */
static int  OLD;              /* поле прапорців, яким ми його застали */
static int  HAVE_OLD;         /* OLD прочитано */
static int  SET;              /* біт справді ввімкнено нами */

struct bit { unsigned int v; const char *name; };

static const struct bit BITS[] = {
    { FS_SECRM_FL,        "secrm(s)"       },
    { FS_UNRM_FL,         "unrm(u)"        },
    { FS_COMPR_FL,        "compr(c)"       },
    { FS_SYNC_FL,         "sync(S)"        },
    { FS_IMMUTABLE_FL,    "immutable(i)"   },
    { FS_APPEND_FL,       "append(a)"      },
    { FS_NODUMP_FL,       "nodump(d)"      },
    { FS_NOATIME_FL,      "noatime(A)"     },
    { FS_INDEX_FL,        "index(I)"       },
    { FS_JOURNAL_DATA_FL, "journal(j)"     },
    { FS_NOTAIL_FL,       "notail(t)"      },
    { FS_DIRSYNC_FL,      "dirsync(D)"     },
    { FS_TOPDIR_FL,       "topdir(T)"      },
    { FS_EXTENT_FL,       "extents(e)"     },
    { FS_VERITY_FL,       "verity(V)"      },
    { FS_NOCOW_FL,        "nocow(C)"       },
    { FS_INLINE_DATA_FL,  "inline_data(N)" },
    { FS_PROJINHERIT_FL,  "projinherit(P)" },
};

/* ── прибирання ─────────────────────────────────────────────────────────── */

/* Вертаємо ПОЛЕ, а не гасимо біт: між нашими двома викликами хтось міг
   поставити свій прапорець, і «зняти i» зітерло б чужу роботу. */
static int put_back(void)
{
    int attr = OLD;

    if (!SET || FD < 0 || !HAVE_OLD)
        return 0;
    if (ioctl(FD, FS_IOC_SETFLAGS, &attr) != 0)
        return -1;
    SET = 0;
    return 0;
}

static void cleanup(void)
{
    if (put_back() != 0)
        fprintf(stderr, "УВАГА: прапорець лишився! знімати: chattr -i %s\n", PATH);
    if (FD >= 0)  close(FD);
    if (WFD >= 0) close(WFD);
    FD = WFD = -1;
    if (!SET && PATH)
        unlink(PATH);
}

/* ioctl і unlink формально не входять до переліку async-signal-safe, але це
   голі системні виклики без стану в бібліотеці. Альтернатива — лишити
   користувачеві незмінний файл після Ctrl-C, що гірше. */
static void on_signal(int sig)
{
    int attr = OLD;

    if (SET && FD >= 0 && HAVE_OLD && ioctl(FD, FS_IOC_SETFLAGS, &attr) == 0)
        SET = 0;
    if (!SET && PATH)
        unlink(PATH);
    _exit(128 + sig);
}

/* ── друк ───────────────────────────────────────────────────────────────── */

static void print_bits(int attr)
{
    unsigned int rest = (unsigned int)attr;
    size_t i;

    if (attr == 0) {
        puts("  (поле порожнє)");
        return;
    }
    for (i = 0; i < NELEM(BITS); i++)
        if (rest & BITS[i].v) {
            printf("  0x%08x  %s\n", BITS[i].v, BITS[i].name);
            rest &= ~BITS[i].v;
        }
    if (rest)
        printf("  0x%08x  (не названі нашим заголовком)\n", rest);
}

/* rc < 0 — дія не пройшла; саме це нас і цікавить. */
static int report(const char *what, int rc)
{
    if (rc >= 0)
        printf("  %-30s ПРОЙШЛО\n", what);
    else
        printf("  %-30s %s (errno %d)\n", what, strerror(errno), errno);
    return rc;
}

static void show_fs(void)
{
    static const struct { unsigned long m; const char *n; } KNOWN[] = {
        { 0xEF53UL,     "ext2/3/4" }, { 0x01021994UL, "tmpfs"  },
        { 0x58465342UL, "xfs"      }, { 0x9123683EUL, "btrfs"  },
        { 0x4D44UL,     "vfat"     }, { 0xF2F52010UL, "f2fs"   },
    };
    struct statfs sfs;
    size_t i;

    if (statfs(PATH, &sfs) != 0)
        return;
    for (i = 0; i < NELEM(KNOWN); i++)
        if ((unsigned long)sfs.f_type == KNOWN[i].m) {
            printf("ФС під шляхом: %s (0x%lx)\n", KNOWN[i].n, KNOWN[i].m);
            return;
        }
    printf("ФС під шляхом: невідома (0x%lx)\n", (unsigned long)sfs.f_type);
}

/* ── власне тур ─────────────────────────────────────────────────────────── */

static void forbidden(void)
{
    /* Час беремо явний: тоді запит іде як ATTR_TIMES_SET і впирається в
       may_setattr(). З NULL він пішов би іншим шляхом — через перевірку
       права писати, — і теж дав би EPERM, але з іншого місця ядра. */
    struct timespec times[2] = { { 0, UTIME_OMIT }, { 1000000000, 0 } };
    char sibling[PATH_MAX];
    int fd;

    if (snprintf(sibling, sizeof sibling, "%s.tour", PATH) >= (int)sizeof sibling)
        return;

    fd = open(PATH, O_WRONLY);
    report("open(O_WRONLY)", fd);
    if (fd >= 0)
        close(fd);

    report("truncate(path, 0)", truncate(PATH, 0));
    report("chmod(path, 0600)", chmod(PATH, 0600));
    report("utimensat(явний час)", utimensat(AT_FDCWD, PATH, times, 0));
    /* EOPNOTSUPP тут означав би не незмінність, а том без розширених
       атрибутів користувача — тому код помилки й друкуємо. */
    report("setxattr(user.tour)", setxattr(PATH, "user.tour", "1", 1, 0));

    /* Якщо ФС прапорця не шанує, ці дві дії пройдуть — і треба відіграти
       назад, інакше ми самі зіпсуємо те, що вимірюємо. */
    if (report("link(path, path.tour)", link(PATH, sibling)) == 0)
        unlink(sibling);
    if (report("rename(path -> path.tour)", rename(PATH, sibling)) == 0)
        rename(sibling, PATH);

    /* unlink — ОСТАННІМ: єдина дія туру, яку не відіграти назад. */
    report("unlink(path)", unlink(PATH));
}

static void via_old_fd(void)
{
    if (WFD < 0) {
        puts("  (дескриптора на запис не було)");
        return;
    }
    report("write(1 байт)", (int)write(WFD, "x", 1));
    report("ftruncate(0)", ftruncate(WFD, 0));
}

static void allowed(void)
{
    struct statx sx;
    char buf[64];
    ssize_t n;

    if (lseek(FD, 0, SEEK_SET) != (off_t)-1) {
        n = read(FD, buf, sizeof buf);
        if (n >= 0)
            printf("  read(fd)                       %zd байтів\n", n);
        else
            report("read(fd)", -1);
    }

    if (statx(AT_FDCWD, PATH, AT_SYMLINK_NOFOLLOW, STATX_ALL, &sx) != 0) {
        report("statx(path)", -1);
    } else if (!(sx.stx_attributes_mask & STATX_ATTR_IMMUTABLE)) {
        /* Нуль в атрибуті без перевірки маски означає «невідомо», а не
           «вимкнено»: біт виставляє getattr самої ФС, і не кожна це робить. */
        puts("  statx                          ця ФС про незмінність не звітує");
    } else {
        printf("  statx                          STATX_ATTR_IMMUTABLE %s\n",
               (sx.stx_attributes & STATX_ATTR_IMMUTABLE) ? "стоїть" : "скинуто");
    }
}

int main(int argc, char **argv)
{
    int attr, want, raw = 0, i;

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-raw") == 0)
            raw = 1;
        else if (!PATH)
            PATH = argv[i];
    }
    if (!PATH) {
        fprintf(stderr, "вжиток: %s [-raw] ШЛЯХ  (файл буде створено й прибрано)\n",
                argv[0]);
        return 2;
    }

    WFD = open(PATH, O_RDWR | O_CREAT | O_EXCL, 0600);
    if (WFD < 0) {
        perror(PATH);
        return 1;
    }
    atexit(cleanup);
    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);
    signal(SIGHUP, on_signal);

    if (write(WFD, "проба\n", 11) < 0) {
        perror("write");
        return 1;
    }

    /* Рівно ті прапорці, з якими відкриває chattr. */
    FD = open(PATH, O_RDONLY | O_NONBLOCK | O_LARGEFILE | O_NOFOLLOW);
    if (FD < 0) {
        perror("open O_RDONLY");
        return 1;
    }

    show_fs();
    if (ioctl(FD, FS_IOC_GETFLAGS, &attr) != 0) {
        fprintf(stderr, "FS_IOC_GETFLAGS: %s — %s\n", strerror(errno),
                errno == ENOTTY ? "у цієї ФС поля прапорців немає взагалі"
                                : "поле є, але прочитати його тут не вийшло");
        return 1;
    }
    OLD = attr;
    HAVE_OLD = 1;
    printf("поле прапорців: 0x%08x\n", (unsigned int)attr);
    print_bits(attr);

    if (raw) {
        /* ТАК РОБИТИ НЕ ТРЕБА — демонстрація ціни. Записуємо все поле одним
           бітом, тобто просимо погасити решту. */
        int bare = FS_IMMUTABLE_FL;

        if (ioctl(FD, FS_IOC_SETFLAGS, &bare) != 0)
            printf("\nзапис одним бітом: %s (errno %d) — ядро відхилило виклик цілком\n",
                   strerror(errno), errno);
        else
            printf("\nзапис одним бітом: ПРОЙШЛО, і з поля тихо зникло 0x%08x\n",
                   (unsigned int)(attr & ~FS_IMMUTABLE_FL));
        SET = 1;          /* хай там що вийшло — прибирати доведеться нам */
    }

    want = attr | FS_IMMUTABLE_FL;     /* читати-міняти-писати */
    if (ioctl(FD, FS_IOC_SETFLAGS, &want) != 0) {
        fprintf(stderr, "FS_IOC_SETFLAGS: %s — %s\n", strerror(errno),
                errno == EPERM      ? "бракує можливості CAP_LINUX_IMMUTABLE" :
                errno == EOPNOTSUPP ? "поле є, а цього біта ця ФС не має" :
                errno == EROFS      ? "том змонтовано лише для читання"
                                    : "несподівано");
        return 1;
    }
    SET = 1;
    printf("\n+i поставлено. Якщо процес уб'ють: chattr -i %s\n", PATH);

    puts("\nзаборонене:");
    forbidden();
    puts("\nчерез дескриптор, відкритий ДО +i:");
    via_old_fd();
    puts("\nдозволене:");
    allowed();

    if (put_back() == 0)
        printf("\nприбрано: поле повернуто в 0x%08x\n", (unsigned int)OLD);
    return 0;
}
