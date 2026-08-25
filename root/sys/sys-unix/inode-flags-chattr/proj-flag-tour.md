# ⚙️ Екскурсія прапорцем: програма на C, яка ставить immutable і ловить кожну відмову

Програма мовою C відкриває файл так, як це робить `chattr`, читає поле прапорців через `ioctl`, вмикає `FS_IMMUTABLE_FL` — і далі по черзі стукає в кожні заборонені двері: `open(O_WRONLY)`, `truncate`, `unlink`, `rename`, `link`, `chmod`, `utimensat`, `setxattr`. Для кожної друкує код помилки. Виходить не переказ того, що заборонено, а вимір: межа гарантії стає стовпчиком виводу, і в цьому стовпчику видно те, чого в жодному довіднику немає — де ваша файлова система поводиться інакше.

Мова тут одна й вибору не має. Це `ioctl` над дескриптором, номери бітів приходять із `linux/fs.h`, а половина цінності — у точному значенні `errno`; будь-яка інша мова говорила б із цим через обгортку, що згладжує саме ті розбіжності, які ми міряємо.

## Чому відкривати треба на читання — і чому неблокуюче

Перше, що дивує в чужому коді: щоб **змінити** прапорці, дескриптор потрібен на **читання**. Логіка проста — прапорці не є вмістом файлу. Вони поле inode, як режим доступу; ядро й не вимагає права писати вміст, щоб їх поміняти, бо вимагає натомість зовсім іншого дозволу.

`chattr` відкриває ціль рівно так:

```c
#define OPEN_FLAGS (O_RDONLY|O_NONBLOCK|O_LARGEFILE|O_NOFOLLOW)
```

Ця ж асиметрія пояснює й набір відмов, які потім доведеться розбирати. Дозволу писати вміст ядро не питає — воно питає інше й у два ходи: спершу «ви власник або маєте `CAP_FOWNER`», потім, окремо для `i` та `a`, «ви маєте [можливість](topic:sys-unix/capabilities) `CAP_LINUX_IMMUTABLE`». А ще перед обома — «том змонтовано на запис», звідки в програмі окрема гілка на `EROFS`.

Кожен прапорець тут закриває свою пастку. `O_NONBLOCK` — бо серед цілей трапляється [іменований канал](topic:sys-unix/pipe-and-fifo): відкриття fifo на читання зупиняється, доки хтось не відкриє його на запис, і команда, яка просто хотіла подивитися атрибути, повисла б назавжди. `O_NOFOLLOW` — бо прапорець лежить в inode, а символьне посилання має свій власний inode; пішовши за посиланням, ви б поставили заборону не тому файлу, який назвали. `O_LARGEFILE` — спадок тридцятидвобітних складань, де без нього великий файл не відкривався взагалі.

## Читати-міняти-писати, інакше затираєте чуже

Друга пастка коштує дорожче. `FS_IOC_SETFLAGS` бере **все поле цілком** — тридцять два біти одним числом, а не «увімкни ось цей». Написавши в нього саме `FS_IMMUTABLE_FL`, ви просите не лише поставити незмінність, а й **погасити все інше**: `noatime`, `nodump`, синхронний запис, вимкнене копіювання-при-записі, а на ext4 ще й `extents` — біт, яким позначено сам спосіб зберігання блоків файлу.

І тут ядро поводиться підступно послідовно: воно ловить помилку не завжди. Погасити `extents` на ext4 — це не зняти позначку, а попросити перекласти весь файл на старе розміщення блоків; ядро береться за це лише в найпростіших випадках, а зазвичай відмовляє всьому виклику з `EOPNOTSUPP`. А на файловій системі, де жоден із загашених бітів не стояв, гасити було нічого — і той самий помилковий виклик спокійно проходить. Тобто хибний код працює доти, доки ви не перенесете його на том, де в полі щось було.

Тому послідовність завжди така: прочитати поле, змінити один біт, записати назад. І прибирання наприкінці — теж не «погасити `i`», а **повернути поле таким, яким воно було**: якщо між цими двома викликами хтось інший поставив на файл `+a`, гасіння одного біта зітре його чужу роботу.

## Три різні «ні»

Найцінніше у виводі — не те, що дії заборонено, а те, **яким саме кодом**. Три коди означають три несумісні висновки, і програма, яка друкує «не вдалося», викидає весь діагноз.

![Таблиця з трьох рядків. Перший рядок: код помилки ENOTTY, значення — у ядрі для цієї файлової системи немає обробника прапорців узагалі, і ioctl каже недоречний виклик; дія — робити нічого, тут немає чого ані прочитати, ані поставити. Другий рядок: код EOPNOTSUPP, значення — поле є, але цього біта файлова система не має, або ви просите погасити біт, який гасити не можна, як extents на ext4; дія — звузити прохання, читати-міняти-писати замість запису всього поля одним числом. Третій рядок: код EPERM, значення — поле є, біт є, бракує повноваження, бо саме i та a вимагають можливості CAP_LINUX_IMMUTABLE; дія — дати процесові цю можливість і не забувати, що вона ж дозволяє зняти. Унизу підсумок: нема де, є та не це, є та не тобі — програма, що друкує лише «не вдалося», викидає весь діагноз](img/three-refusals.svg)

*Ті самі три слова щоразу: «нема де», «є, та не це», «є, та не тобі».*

`ENOTTY` виглядає тут недоречно — «невідповідний виклик для пристрою» звучить так, ніби ми переплутали термінал із файлом. Насправді це загальна відповідь ядра на `ioctl`, якого ніхто не обробив: шар VFS повертає внутрішнє «команду не впізнано», а обгортка виклику перетворює його на `ENOTTY`. Так і виглядає файлова система без поля прапорців.

І ось тут доречно перевірити те, що «всі знають». Здається очевидним, що `/tmp` прапорців не має: tmpfs живе в пам'яті, inode там несправжній. Це було правдою до липня 2022 року, коли Теодор Цо додав до shmem підтримку `FS_IOC_[SG]ETFLAGS`, а Г'ю Дікінз доробив її в 6.0-rc3 — відтоді tmpfs розуміє рівно чотири букви: `a`, `i`, `A`, `d`. На ядрі 6.x той самий `/tmp` віддає поле й приймає `+i`; на ядрі 5.x — `ENOTTY`. Жодного способу вгадати це з назви файлової системи немає, і саме тому програма друкує магічне число тому з `statfs` поруч із результатом: рядок виводу відповідає на питання, на яке довідник відповісти не може.

## Код

```c
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
```

## Що воно друкує

ext4, ядро 6.12, від root:

```
$ sudo ./flagtour /var/tmp/tour.bin
ФС під шляхом: ext2/3/4 (0xef53)
поле прапорців: 0x00080000
  0x00080000  extents(e)

+i поставлено. Якщо процес уб'ють: chattr -i /var/tmp/tour.bin

заборонене:
  open(O_WRONLY)                 Operation not permitted (errno 1)
  truncate(path, 0)              Operation not permitted (errno 1)
  chmod(path, 0600)              Operation not permitted (errno 1)
  utimensat(явний час)           Operation not permitted (errno 1)
  setxattr(user.tour)            Operation not permitted (errno 1)
  link(path, path.tour)          Operation not permitted (errno 1)
  rename(path -> path.tour)      Operation not permitted (errno 1)
  unlink(path)                   Operation not permitted (errno 1)

через дескриптор, відкритий ДО +i:
  write(1 байт)                  Operation not permitted (errno 1)
  ftruncate(0)                   Operation not permitted (errno 1)

дозволене:
  read(fd)                       11 байтів
  statx                          STATX_ATTR_IMMUTABLE стоїть

прибрано: поле повернуто в 0x00080000
```

Той самий двійковий файл, той самий root — і три інші відповіді, кожна з іншої причини:

```
$ ./flagtour /var/tmp/tour.bin                  ← звичайний користувач
ФС під шляхом: ext2/3/4 (0xef53)
поле прапорців: 0x00080000
  0x00080000  extents(e)
FS_IOC_SETFLAGS: Operation not permitted — бракує можливості CAP_LINUX_IMMUTABLE

$ sudo ./flagtour -raw /var/tmp/tour.bin        ← запис усього поля одним бітом
ФС під шляхом: ext2/3/4 (0xef53)
поле прапорців: 0x00080000
  0x00080000  extents(e)

запис одним бітом: Operation not supported (errno 95) — ядро відхилило виклик цілком

$ sudo ./flagtour -raw /tmp/tour.bin            ← та сама помилка, інший том
ФС під шляхом: tmpfs (0x1021994)
поле прапорців: 0x00000000
  (поле порожнє)

запис одним бітом: ПРОЙШЛО, і з поля тихо зникло 0x00000000
```

Ось найдорожчий рядок усього туру. Помилковий виклик на ext4 упирається в `EOPNOTSUPP`, бо разом із бітом `extents` довелося б перекласти весь файл на старе розміщення блоків — і ядро відмовляє **всьому** зверненню замість половинчастої зміни. На tmpfs гасити не було чого — і та сама помилка проходить без сліду. Код, написаний і випробуваний у `/tmp`, поїде на ext4 і зламається на першому ж файлі з непорожнім полем.

## Дозволене — і чому маска важливіша за сам атрибут

Останні два рядки виводу коротші за решту, а важать більше.

`read` працює, бо заборона до шляху читання просто не дотягується: перевірку на незмінність поставлено під умову «просять право писати», і читач її не зачіпає. Найкоротший доказ цього — сама програма: обидва `ioctl` вона робить через дескриптор, здобутий на читання, і з нього ж потім читає вміст незмінного файлу.

З `statx` тонше. Біт `STATX_ATTR_IMMUTABLE` не проставляє загальний код VFS: його виставляє `getattr` самої файлової системи, викликаючи `generic_fill_statx_attr()` — і саме ця функція заразом додає той же біт до `stx_attributes_mask`. Файлова система, яка прапорця шанує, але цієї функції не кличе, чесно відповість нулем.

Звідси й порядок перевірки в програмі: спершу маска, потім атрибут. Нуль в атрибуті **без** перевірки маски означає «мене не питали», а не «не стоїть». Наглядовий скрипт, який дивиться лише на атрибут, на такому томі щоразу бачитиме «файл змінний» — і не спрацює жодного разу, включно з тим, коли захист і справді злетів.

## Пастки

**Прапорець переживає вашу програму.** Це єдина операція туру, після якої машина не повертається в попередній стан сама. Тому прибирання висить на `atexit` **і** на обробнику сигналів, а команду для ручного зняття надруковано ще до першої ризикованої дії — щоб вона вже була на екрані, коли щось піде не так. Проти `SIGKILL` не рятує ніщо, і це не недогляд програми, а властивість самого механізму.

**Уже відкритий дескриптор — місце, де файлові системи розходяться.** У виводі вище `write` через дескриптор, здобутий до `+i`, дістав `EPERM` — але так було не завжди. Перевірка на відкритті вже минула, а в самому шляху запису її колись не було, і кожна файлова система затуляла цю дірку окремо: ext4 — 2019 року, f2fs — наступного. На екзотичнішому томі два рядки цього блоку цілком можуть показати «ПРОЙШЛО», і саме заради них він у турі окремо.

**`EOPNOTSUPP` від `setxattr` не про незмінність.** Той самий код повернеться на томі, змонтованому без розширених [атрибутів користувача](topic:sys-unix/acl-and-xattr), — тому в таблиці друкуємо код, а не слово «заборонено».

**Не переносьте тур на чужий файл.** Він створює власний і сам його прибирає навмисно: серед випробовуваних дій є `rename`, `link` і `unlink`, і на файловій системі, яка прапорця не шанує, вони **пройдуть**. Тому в коді стоїть відіграш назад після перших двох, а `unlink` — останнім у списку: його не відіграти, і після нього решта туру міряла б уже неіснуючий файл. Програма, що міряє заборону, не має права зруйнувати те, що міряє.

## Скільки це коштує

```
ioctl              3        читання поля · встановлення · повернення поля
випробувань        12       кожне — один системний виклик
час                ≈ 15 × 2 мкс ≈ 30 мкс
пам'ять            O(1)
```

Уся вартість — у створенні й видаленні файлу, тобто в диску. Сам обхід прапорця вільний.

> 🔧 **Навіщо це.** Прогнати тур варто перед тим, як спертися на `chattr +i` у розгортанні: він за секунду відповідає на три питання, на які довідник відповісти не може. Чи має **ця** файлова система поле прапорців. Чи шанує вона його в шляху запису, чи лише на відкритті. Чи звітує про нього [statx](topic:sys-unix/statx-mask-and-unknown-values) — бо перевірка «файл незмінний» без перевірки маски атрибутів завжди каже «ні» на тому, який просто не вміє відповідати. Три рядки виводу замість трьох припущень.

Наостанок про напрямок, у якому це рухається. Пара `ioctl` вимагає відкритого дескриптора, а відкрити можна не все: fifo, сокет, пристрій. У ядрі 6.17 з'явилися виклики `file_getattr` і `file_setattr`, що працюють [за схемою *at*](topic:sys-unix/at-family-syscalls) — каталог плюс ім'я, без відкриття, — і саме тому дістають до спецфайлів, до яких пара `ioctl` дотягтися не могла. Поле в них те саме; змінився лише спосіб на нього показати.
