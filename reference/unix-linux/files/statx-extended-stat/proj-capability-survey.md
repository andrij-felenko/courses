# ⚙️ Огляд можливостей змонтованих файлових систем

Ця вставка пояснює ⚙️ огляд можливостей змонтованих файлових систем та дозволяє зрозуміти її детальніше. Програма мовою C обходить усі [монтування](book:unix-linux/mount-model), які бачить процес, кладе на кожне файл-зразок, питає про нього `statx` повною маскою — і зводить відповіді в таблицю «файлова система → про що вона справді вміє розповісти». Такої таблиці немає в жодному довіднику, і це не недогляд: відповідь залежить не від назви файлової системи, а від того, як саме цей том відформатовано, з якими опціями його змонтовано, на якому ядрі це працює і якими заголовками зібрано вашу програму.

## Чотири незалежні вісі, через які довідник не допоможе

Кожна з них рухається сама по собі, і жодна не видна з назви `ext4` чи `btrfs`.

**Як том розмічено.** Час створення файлу ext4 тримає в додаткових полях [inode](book:unix-linux/inode-model), і ці поля існують лише тоді, коли inode більший за 128 байтів — саме такий, «добрий старий», розмір дістався ext4 у спадок від ext2. Документація формату каже про додаткові часові поля прямо: вони працюють, «якщо розмір структури inode більший за 128 байтів» і поле `i_extra_isize` дотягується до потрібного часу. Том, розмічений давно або з `mke2fs -I 128`, часу створення не має фізично — і це властивість тому, а не драйвера.

**Як том змонтовано.** FAT не зберігає власника взагалі, тож драйвер бере його з опцій монтування `uid=`/`gid=`. А опція `noatime` знімає з відповіді цілий час доступу: у VFS це один рядок, `if (inode->i_sb->s_flags & SB_NOATIME) stat->result_mask &= ~STATX_ATIME;`. Той самий ext4, змонтований двічі по-різному, відповість по-різному.

**Яке ядро.** Біти маски додавалися роками: `STATX_MNT_ID` — у 5.8, `STATX_DIOALIGN` — у 6.1, `STATX_MNT_ID_UNIQUE` — у 6.8, `STATX_SUBVOL` — у 6.10, атомарний запис — у 6.11. Кожен новий біт спершу вміє одна-дві файлові системи: прямий ввід-вивід описують ext4, f2fs і xfs, номер підтому — btrfs і bcachefs.

**Якими заголовками зібрано вас.** Ім'я `STATX_SUBVOL` живе у файлі `linux/stat.h` на вашій машині, а значення `0x8000` розуміє ядро на тій машині, де програма працюватиме. Ці два віки незалежні. Зібравши старими заголовками, ви не попросите нового біта — і чесно вирішите, що ядро його не вміє.

Отже, відповідь — властивість конкретного монтування тут і зараз. Її не дізнаються, її **міряють**.

## Що вважати відповіддю

Наївний вимір — «спитати все і подивитися, що прийшло» — губить половину інформації. Насправді кожен біт має чотири стани, бо маска запиту й маска відповіді розходяться в обидва боки.

![Сітка два на два. Стовпці підписано за станом біта у stx_mask: ліворуч біт стоїть, праворуч біт скинуто. Рядки підписано за маскою запиту: угорі біт стояв у масці запиту, унизу біта в масці запиту не було. Чотири клітинки: поле є, значення читати можна; ця файлова система такого не знає, у полі нуль, і він нічого не означає; дісталося задарма, драйвер однаково прочитав inode й позначив біт; тиша — ні прохання, ні відповіді. Унизу на всю ширину жовта рамка з п'ятим випадком: у stx_mask стоїть біт, якого наш заголовок не називає, — ядро новіше за програму, і саме цей залишок каже, наскільки](/reference/unix-linux/files/statx-extended-stat/img/mask-bit-cells.svg)

*Просили й дістали, просили й не дістали, не просили й дістали — це три різні факти про файлову систему, і зливати їх в один прапорець «поле є» означає викинути найцікавіше.*

П'ятий випадок — залишок `stx_mask & ~(усе, що ми вміємо назвати)` — у звичайному прогоні порожній, і саме тому його варто друкувати: щойно він перестане бути порожнім, ви дізнаєтеся, що ядро під вами обігнало ваші заголовки.

## Три різні «ні» — і як їх не переплутати

Поля може не бути з трьох геть різних причин, і програма, яка їх не розрізняє, друкує однакове «немає» там, де насправді три різні висновки.

**Виклик не вдався.** Повернуто `-1`, у `errno` — `ENOENT`, `EACCES`, `EIO`. Про файлову систему це не каже нічого: ми просто не змогли спитати.

**Виклик удався, біт скинуто.** Це і є вимір: «ця файлова система такого не знає». Документація формулює умову ширше — біт буде скинуто, якщо ФС поля не підтримує **або** значення непредставне.

**Виклику немає в ядрі.** Тут ховається пастка, заради якої варто зробити одну незвичну річ. Обгортка glibc, побачивши `ENOSYS`, не здається: вона мовчки підставляє власну заміну, зібрану зі старого запиту атрибутів. Заміна ця чесна — вона виставляє біти лише тих полів, що справді взялися, — але для нашої задачі вона отруйна: усі рядки таблиці стануть однакові, і ви подивитеся на портрет бібліотеки, вважаючи, що дивитеся на ядро. Відрізнити її зсередини за виглядом відповіді не можна: «лише базові поля і жодного атрибута» — цілком законна відповідь і від справжньої файлової системи.

Тому огляд можливостей ядра робить виклик **напряму**, `syscall(__NR_statx, …)`, повз [бібліотеку як шлюз](book:unix-linux/libc-as-gateway). Тоді старе ядро видно як `ENOSYS` на першому ж зразку, і програма скаже це прямо, а не намалює красиву неправду. Це один із небагатьох випадків, коли обходити обгортку правильно: ми міряємо саме ту межу, яку вона для того й існує, щоб згладжувати.

## Пастка повної маски

Здається, що правильний запит — «усі біти, які ми знаємо». Але два з них взаємно виключні, і побачити це можна лише в коді ядра:

```c
if (request_mask & STATX_MNT_ID_UNIQUE) {
        stat->mnt_id = real_mount(path->mnt)->mnt_id_unique;
        stat->result_mask |= STATX_MNT_ID_UNIQUE;
} else {
        stat->mnt_id = real_mount(path->mnt)->mnt_id;
        stat->result_mask |= STATX_MNT_ID;
}
```

Обидва ідентифікатори живуть в одному полі структури, тож ядро віддає рівно один. Попросивши обидва, ви **ніколи** не отримаєте `STATX_MNT_ID` — і наївний огляд напише «жодна файлова система не повідомляє ідентифікатора монтування», хоча повідомляють усі. Ліки прості: другий, крихітний виклик рівно з одним бітом. Але знайти це самотужки, дивлячись лише на таблицю, неможливо — тому висновок варто запам'ятати: **повна маска не є найінформативнішим запитом**.

Поруч видно і межу поблажливості, про яку легко забути. Невідомий біт **маски** ядро мовчки ігнорує, а от невідомий **прапорець** відкидає:

```c
if (flags & ~(AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT | AT_EMPTY_PATH |
              AT_STATX_SYNC_TYPE))
        return -EINVAL;
```

Питання можна ставити з запасом, а вимоги до способу відповіді — ні.

## Зразок, якого не існувало

Лишається дрібниця, від якої залежить усе: **що саме** питати на кожному монтуванні.

Найчистіше — створити свій файл: він щойно народжений, порожній, нічим не позначений, і його історія нам відома. Але створити вдається не скрізь: том змонтовано лише для читання, прав немає, [псевдофайлова система](book:unix-linux/pseudo-filesystems) створення взагалі не підтримує. Тому драбина з трьох щаблів: створити свій → знайти будь-який звичайний файл у корені монтування → взяти сам каталог точки монтування.

Щабель треба друкувати в таблиці поруч із результатом, бо відповіді на різних щаблях **не порівнянні**. Вирівнювання прямого вводу-виводу існує тільки для звичайних файлів — на каталозі бітів `dioalign` не буде ніколи, і це нічого не каже про файлову систему. У зворотний бік працює `STATX_ATTR_MOUNT_ROOT`: він стоїть саме тоді, коли ви спитали про корінь монтування, тобто рівно на третьому щаблі.

Три дрібні пастки, кожна з яких псує вимір тихо:

- **Накрите монтування.** Стовпчик точок у `/proc/self/mountinfo` каже, куди монтування причепили, а не куди зараз веде шлях; якщо зверху лягло інше, ви опитаєте його. Ловиться це тим самим інструментом, який міряємо: `stx_mnt_id` порівнюємо з першим полем рядка, і розбіжність означає «сюди більше не потрапити». Чому так буває і як побудувати дерево як слід — у [майстерні з `mountinfo`](book:unix-linux/mount-model/proj-mountinfo-tree.md).
- **Автомонтування.** Запит атрибутів на точці autofs змонтує її. Прапорець `AT_NO_AUTOMOUNT` просить цього не робити — інакше огляд змінює те, що оглядає.
- **Мертвий сервер.** На [мережевій файловій системі](book:unix-linux/network-filesystems) з недоступним сервером виклик зупиниться надовго й без надії на сигнал. Тому такі типи за замовчуванням пропускаємо, а `-a` вмикає їх свідомо; `-c` додає `AT_STATX_DONT_SYNC`, і тоді відповідь беруть із кеша.

І прибирати за собою обов'язково: створений зразок знімають одразу після виклику.

## Код

Мова тут одна. Це системний виклик: розкладку структури, номери бітів і навіть саме число послуги визначають заголовки ядра, і будь-яка інша мова говорила б із ними через обгортку — тобто саме через той шар, від якого ми навмисно відмовилися.

```c
/* fscaps.c — обійти монтування й спитати кожну файлову систему повною
 * маскою statx: про що вона справді вміє відповідати.
 *
 *   cc -O2 -std=c11 -D_GNU_SOURCE -o fscaps fscaps.c
 *
 * Заголовки потрібні від glibc 2.28 / Linux 4.11 — там з'явилася struct statx.
 * ЯДРО може бути й старішим: виклик іде напряму через syscall(), тож
 * відсутність послуги видно як ENOSYS, а не як підмінену відповідь.
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef STATX_BTIME
# error "заголовки старші за Linux 4.11: struct statx недоступна"
#endif

/* Ім'я біта живе в заголовку, значення розуміє ядро, і ці два віки
   незалежні. Дописуємо те, чого може не бути в заголовках складання, —
   інакше «повна» маска виявиться неповною саме там, де цікаво. */
#ifndef STATX_MNT_ID
# define STATX_MNT_ID            0x00001000U
#endif
#ifndef STATX_DIOALIGN
# define STATX_DIOALIGN          0x00002000U
#endif
#ifndef STATX_MNT_ID_UNIQUE
# define STATX_MNT_ID_UNIQUE     0x00004000U
#endif
#ifndef STATX_SUBVOL
# define STATX_SUBVOL            0x00008000U
#endif
#ifndef STATX_WRITE_ATOMIC
# define STATX_WRITE_ATOMIC      0x00010000U
#endif
#ifndef STATX_DIO_READ_ALIGN
# define STATX_DIO_READ_ALIGN    0x00020000U
#endif
#ifndef STATX_ATTR_MOUNT_ROOT
# define STATX_ATTR_MOUNT_ROOT   0x00002000U
#endif
#ifndef STATX_ATTR_VERITY
# define STATX_ATTR_VERITY       0x00100000U
#endif
#ifndef STATX_ATTR_DAX
# define STATX_ATTR_DAX          0x00200000U
#endif
#ifndef STATX_ATTR_WRITE_ATOMIC
# define STATX_ATTR_WRITE_ATOMIC 0x00400000U
#endif
#ifndef AT_NO_AUTOMOUNT
# define AT_NO_AUTOMOUNT         0x800
#endif
#ifndef AT_STATX_SYNC_AS_STAT
# define AT_STATX_SYNC_AS_STAT   0x0000
#endif
#ifndef AT_STATX_DONT_SYNC
# define AT_STATX_DONT_SYNC      0x4000
#endif

#define NELEM(a) (sizeof(a) / sizeof((a)[0]))

struct bitname { unsigned int bit; const char *name; };

/* STATX_ALL не вживаємо: він оголошений застарілим і знову означає
   «дай усе», не називаючи, що саме. Перелічуємо поіменно. */
static const struct bitname FIELD[] = {
    { STATX_TYPE,           "type"           },
    { STATX_MODE,           "mode"           },
    { STATX_NLINK,          "nlink"          },
    { STATX_UID,            "uid"            },
    { STATX_GID,            "gid"            },
    { STATX_ATIME,          "atime"          },
    { STATX_MTIME,          "mtime"          },
    { STATX_CTIME,          "ctime"          },
    { STATX_INO,            "ino"            },
    { STATX_SIZE,           "size"           },
    { STATX_BLOCKS,         "blocks"         },
    { STATX_BTIME,          "btime"          },
    { STATX_MNT_ID,         "mnt_id"         },
    { STATX_DIOALIGN,       "dioalign"       },
    { STATX_MNT_ID_UNIQUE,  "mnt_id_unique"  },
    { STATX_SUBVOL,         "subvol"         },
    { STATX_WRITE_ATOMIC,   "write_atomic"   },
    { STATX_DIO_READ_ALIGN, "dio_read_align" },
};

static const struct bitname ATTR[] = {
    { STATX_ATTR_COMPRESSED,   "compressed"   },
    { STATX_ATTR_IMMUTABLE,    "immutable"    },
    { STATX_ATTR_APPEND,       "append"       },
    { STATX_ATTR_NODUMP,       "nodump"       },
    { STATX_ATTR_ENCRYPTED,    "encrypted"    },
    { STATX_ATTR_AUTOMOUNT,    "automount"    },
    { STATX_ATTR_MOUNT_ROOT,   "mount_root"   },
    { STATX_ATTR_VERITY,       "verity"       },
    { STATX_ATTR_DAX,          "dax"          },
    { STATX_ATTR_WRITE_ATOMIC, "write_atomic" },
};

/* Типи, на яких виклик може стати надовго: сервера може не бути, а чекання
   тут не переривається сигналом. Умикає їх лише -a. */
static const char *RISKY[] = { "nfs", "nfs4", "cifs", "smb3", "ceph",
                               "afs", "9p", "fuse.sshfs" };

static int sync_flag = AT_STATX_SYNC_AS_STAT;   /* -c ставить DONT_SYNC */

/* Виклик БЕЗ обгортки бібліотеки: нам потрібне ядро, а не його емуляція. */
static int statx_raw(int dirfd, const char *path, int flags,
                     unsigned int mask, struct statx *stx)
{
#ifdef __NR_statx
    return (int)syscall(__NR_statx, dirfd, path, flags, mask, stx);
#else
    (void)dirfd; (void)path; (void)flags; (void)mask; (void)stx;
    errno = ENOSYS;
    return -1;
#endif
}

/* printf("%-10s") міряє БАЙТИ, а кирилична літера важить два, тож стовпці
   роз'їжджаються. Рахуємо позиції: у UTF-8 їх стільки, скільки байтів,
   що не є продовженням (їхні два старші біти — не 10). */
static void putpad(const char *s, int cols)
{
    const unsigned char *p;
    int n = 0;

    for (p = (const unsigned char *)s; *p; p++)
        if ((*p & 0xc0) != 0x80)
            n++;
    fputs(s, stdout);
    while (n++ < cols)
        putchar(' ');
}

/* Імена бітів, що стоять у mask, через пробіл. Повертає, скільки їх. */
static int decode(unsigned int mask, const struct bitname *tab, size_t n,
                  char *buf, size_t cap)
{
    size_t i, len = 0;
    int cnt = 0;

    buf[0] = '\0';
    for (i = 0; i < n; i++) {
        if (!(mask & tab[i].bit))
            continue;
        if (len && len + 1 < cap) {
            buf[len++] = ' ';
            buf[len] = '\0';
        }
        len += (size_t)snprintf(buf + len, cap - len, "%s", tab[i].name);
        if (len >= cap - 1)
            break;
        cnt++;
    }
    return cnt;
}

static unsigned int all_fields(void)
{
    unsigned int m = 0;
    size_t i;

    for (i = 0; i < NELEM(FIELD); i++)
        m |= FIELD[i].bit;
    /* mnt_id_unique витісняє mnt_id — питаємо його окремим викликом. */
    return m & ~STATX_MNT_ID_UNIQUE;
}

/* ── /proc/self/mountinfo ───────────────────────────────────────────────── */

struct mnt {
    int  id;
    char dev[32];
    char point[PATH_MAX];
    char type[64];
    char opts[512];        /* прапорці суперблока: тут живуть uid=, gid= */
};

/* Ядро екранує пробіл, табуляцію, переведення рядка й сам зворотний слеш
   як слеш плюс рівно три вісімкові цифри. Знімаємо ОДНИМ проходом:
   послідовність замін, що починається з \134, псує справжні слеші. */
static void unescape(char *s)
{
    char *o = s, *i = s;

    while (*i) {
        if (i[0] == '\\' && i[1] >= '0' && i[1] <= '7'
                         && i[2] >= '0' && i[2] <= '7'
                         && i[3] >= '0' && i[3] <= '7') {
            *o++ = (char)((i[1] - '0') * 64 + (i[2] - '0') * 8 + (i[3] - '0'));
            i += 4;
        } else {
            *o++ = *i++;
        }
    }
    *o = '\0';
}

/* Спрощений розбір: нам вистачає точки, типу й прапорців суперблока.
   Роздільник «-» ШУКАЄМО, а не рахуємо: необов'язкових полів перед ним
   нуль або кілька, і ядру дозволено додавати нові. */
static int parse_line(char *line, struct mnt *m)
{
    char *f[24];
    char *p = line;
    int n = 0, sep = 6;

    while (*p && n < (int)NELEM(f)) {
        while (*p == ' ')
            *p++ = '\0';
        if (!*p)
            break;
        f[n++] = p;
        while (*p && *p != ' ')
            p++;
    }
    while (sep < n && strcmp(f[sep], "-") != 0)
        sep++;
    if (sep + 3 >= n)
        return -1;

    m->id = atoi(f[0]);
    snprintf(m->dev,   sizeof m->dev,   "%s", f[2]);
    snprintf(m->point, sizeof m->point, "%s", f[4]);
    snprintf(m->type,  sizeof m->type,  "%s", f[sep + 1]);
    snprintf(m->opts,  sizeof m->opts,  "%s", f[sep + 3]);
    unescape(m->point);
    unescape(m->type);
    return 0;
}

/* ── зразок ─────────────────────────────────────────────────────────────── */

struct probe {
    char        path[PATH_MAX];
    const char *kind;      /* «новий», «наявний», «каталог» */
    int         created;
};

static int probe_pick(const struct mnt *m, struct probe *pr)
{
    struct dirent *e;
    struct stat st;
    DIR *d;
    int fd, seen;

    pr->created = 0;
    /* Обрізаний шлях указував би не туди — краще відмовитися. */
    if (snprintf(pr->path, sizeof pr->path, "%s/.fscaps.%ld",
                 m->point, (long)getpid()) >= (int)sizeof pr->path)
        return -1;

    fd = open(pr->path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (fd >= 0) {
        close(fd);
        pr->kind = "новий";
        pr->created = 1;
        return 0;
    }

    d = opendir(m->point);
    if (d) {
        for (seen = 0; seen < 4096 && (e = readdir(d)) != NULL; seen++) {
            if (e->d_name[0] == '.')
                continue;
            if (e->d_type != DT_REG && e->d_type != DT_UNKNOWN)
                continue;
            if (snprintf(pr->path, sizeof pr->path, "%s/%s",
                         m->point, e->d_name) >= (int)sizeof pr->path)
                continue;
            if (lstat(pr->path, &st) == 0 && S_ISREG(st.st_mode)) {
                closedir(d);
                pr->kind = "наявний";
                return 0;
            }
        }
        closedir(d);
    }

    /* Лишається сама точка монтування. Це КАТАЛОГ: dioalign тут не буде
       ніколи, зате mount_root стоятиме саме тут. */
    snprintf(pr->path, sizeof pr->path, "%s", m->point);
    pr->kind = "каталог";
    return 0;
}

/* ── один вимір ─────────────────────────────────────────────────────────── */

struct answer {
    struct probe pr;
    struct statx sx;
    int ok;          /* виклик удався */
    int err;         /* errno, коли ні */
    int uniq;        /* ядро вміє mnt_id_unique */
    int covered;     /* шлях привів в інше монтування */
};

static void ask(const struct mnt *m, struct answer *a)
{
    int flags = AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT | sync_flag;
    struct statx u;

    memset(a, 0, sizeof *a);
    if (probe_pick(m, &a->pr) != 0) {
        a->err = ENAMETOOLONG;
        return;
    }
    if (statx_raw(AT_FDCWD, a->pr.path, flags, all_fields(), &a->sx) != 0) {
        a->err = errno;
    } else {
        a->ok = 1;
        /* Другий виклик рівно з одним бітом: у першому він витіснив би
           mnt_id, за яким ми впізнаємо накрите монтування. */
        if (statx_raw(AT_FDCWD, a->pr.path, flags,
                      STATX_MNT_ID_UNIQUE, &u) == 0)
            a->uniq = (u.stx_mask & STATX_MNT_ID_UNIQUE) != 0;
        if ((a->sx.stx_mask & STATX_MNT_ID) &&
            (int)a->sx.stx_mnt_id != m->id)
            a->covered = 1;
    }
    if (a->pr.created)
        unlink(a->pr.path);
}

/* ── друк ───────────────────────────────────────────────────────────────── */

static int prologue(const struct answer *a, const struct mnt *m)
{
    if (!a->ok) {
        putpad(m->type, 10);
        putpad(m->point, 22);
        printf("не спитати: %s\n",
               a->err == ENOSYS ? "у ядрі немає statx" : strerror(a->err));
        return 0;
    }
    if (a->covered) {
        putpad(m->type, 10);
        putpad(m->point, 22);
        printf("пропущено: точку накрито іншим монтуванням\n");
        return 0;
    }
    return 1;
}

static void row_fields(const struct mnt *m, const struct answer *a)
{
    unsigned int missing, extra, unknown, known = 0;
    char names[512], gone[256];
    size_t i;

    if (!prologue(a, m))
        return;
    for (i = 0; i < NELEM(FIELD); i++)
        known |= FIELD[i].bit;

    missing = STATX_BASIC_STATS & ~a->sx.stx_mask;
    extra   = a->sx.stx_mask & ~STATX_BASIC_STATS;
    unknown = a->sx.stx_mask & ~known;

    putpad(m->type, 10);
    putpad(m->point, 22);
    putpad(a->pr.kind, 9);
    if (missing) {
        decode(missing, FIELD, NELEM(FIELD), gone, sizeof gone);
        snprintf(names, sizeof names, "усі, крім %s", gone);
        putpad(names, 19);
    } else {
        putpad("усі", 19);
    }
    decode(extra, FIELD, NELEM(FIELD), names, sizeof names);
    fputs(names, stdout);
    if (unknown)
        printf("  [не названі заголовком: 0x%x]", unknown);
    putchar('\n');
}

static void row_attrs(const struct mnt *m, const struct answer *a)
{
    char can[512], is[512];

    if (!prologue(a, m))
        return;
    decode(a->sx.stx_attributes_mask, ATTR, NELEM(ATTR), can, sizeof can);
    decode(a->sx.stx_attributes & a->sx.stx_attributes_mask,
           ATTR, NELEM(ATTR), is, sizeof is);

    putpad(m->type, 10);
    putpad(m->point, 22);
    putpad(a->pr.kind, 9);
    putpad(can[0] ? can : "—", 52);
    printf("%s\n", is[0] ? is : "—");
}

/* Скільки підкаталогів у каталозі; -1, якщо не читається. */
static long count_subdirs(const char *dir)
{
    char path[PATH_MAX];
    struct dirent *e;
    struct stat st;
    DIR *d = opendir(dir);
    long n = 0;

    if (!d)
        return -1;
    while ((e = readdir(d)) != NULL) {
        if (strcmp(e->d_name, ".") == 0 || strcmp(e->d_name, "..") == 0)
            continue;
        if (e->d_type == DT_DIR) {
            n++;
        } else if (e->d_type == DT_UNKNOWN &&
                   snprintf(path, sizeof path, "%s/%s",
                            dir, e->d_name) < (int)sizeof path &&
                   lstat(path, &st) == 0 && S_ISDIR(st.st_mode)) {
            n++;
        }
    }
    closedir(d);
    return n;
}

/* Числове значення опції key= серед прапорців; -1, якщо її немає. */
static long opt_num(const char *opts, const char *key)
{
    size_t kl = strlen(key);
    const char *p;

    for (p = opts; p; p = strchr(p, ',')) {
        if (*p == ',')
            p++;
        if (strncmp(p, key, kl) == 0 && p[kl] == '=')
            return strtol(p + kl + 1, NULL, 10);
    }
    return -1;
}

/* Перевірки того, про що маска мовчить: біт стоїть, а значення умовне. */
static void row_checks(const struct mnt *m, const struct answer *a)
{
    struct statx d;
    long subdirs, uid;

    if (!prologue(a, m))
        return;

    subdirs = count_subdirs(m->point);
    if (subdirs >= 0 &&
        statx_raw(AT_FDCWD, m->point, AT_NO_AUTOMOUNT | sync_flag,
                  STATX_NLINK, &d) == 0 && (d.stx_mask & STATX_NLINK)) {
        putpad(m->point, 22);
        putpad(m->type, 10);
        if ((long)d.stx_nlink == subdirs + 2)
            printf("каталог: імен %u = 2 + %ld підкаталогів — "
                   "домовленість тримається\n", d.stx_nlink, subdirs);
        else
            printf("каталог: імен %u, підкаталогів %ld — "
                   "домовленість НЕ тримається\n", d.stx_nlink, subdirs);
    }

    uid = opt_num(m->opts, "uid");
    if (uid >= 0 && (a->sx.stx_mask & STATX_UID)) {
        putpad(m->point, 22);
        putpad(m->type, 10);
        printf("власник: uid %u, і рівно це стоїть в опції монтування "
               "uid=%ld\n", a->sx.stx_uid, uid);
    }
}

/* ── головне ────────────────────────────────────────────────────────────── */

static int wanted(const char *point, int argc, char **argv)
{
    int i, any = 0;

    for (i = 1; i < argc; i++) {
        if (argv[i][0] == '-')
            continue;
        any = 1;
        if (strcmp(argv[i], point) == 0)
            return 1;
    }
    return !any;
}

static int is_risky(const char *type)
{
    size_t i;

    for (i = 0; i < NELEM(RISKY); i++)
        if (strcmp(type, RISKY[i]) == 0)
            return 1;
    return 0;
}

int main(int argc, char **argv)
{
    const char *src = getenv("MOUNTINFO");
    char line[8192], seen[512][32];
    int mode = 'f', risky = 0, nseen = 0, i, j;
    struct answer a;
    struct mnt m;
    FILE *f;

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-A") == 0)      mode = 'a';
        else if (strcmp(argv[i], "-x") == 0) mode = 'x';
        else if (strcmp(argv[i], "-a") == 0) risky = 1;
        else if (strcmp(argv[i], "-c") == 0) sync_flag = AT_STATX_DONT_SYNC;
    }

    f = fopen(src ? src : "/proc/self/mountinfo", "r");
    if (!f) {
        perror("mountinfo");
        return 1;
    }

    if (mode == 'f') {
        printf("програма називає %zu полів і %zu атрибутів\n\n",
               NELEM(FIELD), NELEM(ATTR));
        putpad("ФС", 10); putpad("точка", 22); putpad("зразок", 9);
        putpad("базові", 19); printf("поза базовими\n");
    } else if (mode == 'a') {
        putpad("ФС", 10); putpad("точка", 22); putpad("зразок", 9);
        putpad("уміє відповідати про", 52); printf("стоїть на зразку\n");
    }

    while (fgets(line, sizeof line, f)) {
        line[strcspn(line, "\n")] = '\0';
        if (parse_line(line, &m) != 0)
            continue;
        if (!wanted(m.point, argc, argv))
            continue;
        if (!risky && is_risky(m.type))
            continue;
        /* Одне монтування на суперблок: прив'язки того самого тому
           відповідають однаково, а їх у контейнерному хості десятки. */
        for (j = 0; j < nseen; j++)
            if (strcmp(seen[j], m.dev) == 0)
                break;
        if (j < nseen)
            continue;
        if (nseen < (int)NELEM(seen))
            snprintf(seen[nseen++], sizeof seen[0], "%s", m.dev);

        ask(&m, &a);
        if (mode == 'f')      row_fields(&m, &a);
        else if (mode == 'a') row_attrs(&m, &a);
        else                  row_checks(&m, &a);
    }
    fclose(f);
    return 0;
}
```

## Що воно друкує

Машина з ядром 6.12, заголовки трохи старіші — імена `subvol`, `write_atomic` і `dio_read_align` довелося дописати самим.

```
$ ./fscaps
програма називає 18 полів і 10 атрибутів

ФС        точка                 зразок   базові             поза базовими
ext4      /                     новий    усі                btime mnt_id dioalign
ext4      /home                 новий    усі, крім atime    btime mnt_id dioalign
btrfs     /data                 новий    усі                btime mnt_id subvol
vfat      /mnt/usb              новий    усі                btime mnt_id
tmpfs     /tmp                  новий    усі                btime mnt_id
proc      /proc                 наявний  усі                mnt_id
sysfs     /sys                  каталог  усі                mnt_id
devpts    /dev/pts              каталог  усі                mnt_id
squashfs  /snap/core            каталог  усі                mnt_id
overlay   /var/lib/docker/…     пропущено: точку накрито іншим монтуванням
```

Атрибути окремою таблицею — так рядок лишається читним:

```
$ ./fscaps -A /tmp /mnt/usb /proc /dev/pts
ФС        точка                 зразок   уміє відповідати про                                стоїть на зразку
tmpfs     /tmp                  новий    immutable append nodump automount mount_root dax     —
vfat      /mnt/usb              новий    automount mount_root dax                             —
proc      /proc                 наявний  automount mount_root dax                             —
devpts    /dev/pts              каталог  automount mount_root dax                             mount_root
```

І перевірки того, про що маска мовчить:

```
$ ./fscaps -x
/                     ext4      каталог: імен 21 = 2 + 19 підкаталогів — домовленість тримається
/home                 ext4      каталог: імен 4 = 2 + 2 підкаталогів — домовленість тримається
/data                 btrfs     каталог: імен 1, підкаталогів 19 — домовленість НЕ тримається
/mnt/usb              vfat      каталог: імен 6 = 2 + 4 підкаталогів — домовленість тримається
/mnt/usb              vfat      власник: uid 1000, і рівно це стоїть в опції монтування uid=1000
/tmp                  tmpfs     каталог: імен 8 = 2 + 6 підкаталогів — домовленість тримається
/proc                 proc      каталог: імен 9, підкаталогів 412 — домовленість НЕ тримається
```

## Що ця таблиця показує

**Базова половина всюди однакова — і це не про однаковість файлових систем.** Стовпчик «базові» заповнено словом «усі» майже скрізь, бо [VFS](book:unix-linux/vfs-layer) вмикає ці одинадцять бітів сам, ще до того, як спитає драйвер: `stat->result_mask |= STATX_BASIC_STATS;`. Драйвер може їх лише **скинути**, і робить це рідко. Отже, для старого набору полів маска нікого не рятує: біт стоїть завжди, а от чи стоїть за ним справжнє знання — питання іншого ярусу.

Єдиний виняток у таблиці — рядок `/home`, змонтований із `noatime`. Тут біт справді знято, і саме тому цей рядок цінний: він показує, що відповідь належить **монтуванню**, а не файловій системі. Той самий ext4 двома рядками вище віддає час доступу.

**Час створення розходиться там, де його ніхто не чекає.** `vfat` віддає `btime` — FAT тримає час створення в записі каталогу від самого початку, і драйвер його повертає (класичний `msdos` без довгих імен — ні). А ось ext4 на томі зі 128-байтовим inode його не віддасть, хоча «ext4 уміє час створення» — правда. Це найкорисніший рядок усього огляду: він робить видимим те, що інакше проявиться як дата «1 січня 1970» у резервній копії.

**tmpfs віддає час створення, хоч ніде його не зберігає** — тримає в тій самій оперативній пам'яті, де живе решта файлу. Заразом видно, що вміння відповісти не пов'язане з наявністю носія: [псевдофайлові системи](book:unix-linux/pseudo-filesystems) розходяться між собою сильніше, ніж дискові. `tmpfs` знає три атрибути, `proc` і `sysfs` — жодного власного.

**Атрибути виявляються майже порожніми.** Три імені — `automount`, `mount_root`, `dax` — стоять у **кожному** рядку, бо в маску їх додає сам VFS, ще до того як спитає драйвер. Усе, що зверх них, — заслуга драйвера, і в більшості файлових систем цього «зверх» немає взагалі. Тому порожній рядок атрибутів у таблиці читають так: скинутий біт `compressed` тут не означає «файл не стиснено», він означає «мене про стиснення не питайте».

**А там, де маска мовчить, доводиться міряти інакше.** Це і робить `-x`.

Лічильник імен каталогу за домовленістю дорівнює `2 + кількість підкаталогів`: сам каталог, його запис `.` і по одному `..` з кожної дитини. Домовленість — не вимога, і в самому Unix це визнано давно: у `find(1)` є окремий прапорець `-noleaf` саме для файлових систем, які її не тримають, а в переліку таких названо компакт-диски, файлові системи MS-DOS і точки монтування томів AFS. Btrfs поводиться так само: будь-який каталог там показує рівно одне ім'я. Біт `nlink` при цьому стоїть, значення `1` цілком законне — і [оптимізація обходу дерева](book:unix-linux/directory-as-mapping), побудована на цьому лічильнику, тихо загубить каталоги. Ловиться це лише зустрічним рахунком, який `-x` і робить.

Так само з власником на FAT. Біти `uid` і `gid` стоять, числа правдоподібні — але це рівно ті числа, що стоять в опціях монтування, у чому програма й переконується, зазираючи в прапорці суперблока з `mountinfo`. [Модель власника](book:unix-linux/uid-gid-model) сюди не сягає: у самому томі такого поняття немає.

![Три горизонтальні смуги. Перша: питання «Чи є це поле взагалі?», стрілка до зеленої рамки «відповідає stx_mask», приклад — ext4 на томі зі 128-байтовим inode не має де тримати час створення й чесно не виставляє біт btime. Друга: питання «Чи значення щось означає?», стрілка до червоної рамки «не відповідає ніщо», приклад — FAT віддає власника з опції монтування uid=, а Btrfs пише будь-якому каталогу лічильник імен 1, і біти при цьому стоять. Третя: питання «Чи воно свіже?», стрілка до синьої рамки «відповідає прапорець синхронізації», приклад — на мережевій файловій системі розмір беруть із кеша або звіряють із сервером, і це вибір програми](/reference/unix-linux/files/statx-extended-stat/img/three-questions.svg)

*Маска відповідає на перше питання й нічого не обіцяє про друге. Цю межу видно тільки тоді, коли поруч є зустрічний вимір.*

> 🔧 **Навіщо це.** Огляд варто прогнати не з цікавості, а перед тим, як щось будувати на полях `statx`. Резервне копіювання, синхронізація, дедуплікація, індексатор — усі вони мовчки припускають, що потрібне поле є й означає те, що написано в довіднику. Таблиця перетворює це припущення на рядок виводу: «на цьому томі часу створення немає», «тут лічильник імен нічого не рахує», «власник тут вигаданий при монтуванні». Кожен такий рядок — це або зникла помилка, або усвідомлений компроміс.

## Скільки це коштує

```
розбір mountinfo   O(B)          B — байтів у файлі, один прохід
на монтування      2 виклики     повна маска + окремий mnt_id_unique
                   + 1 create/unlink, якщо зразок створюємо
режим -x           O(E)          E — записів у корені монтування (рахунок підкаталогів)
пам'ять            O(1) на рядок, розбір іде потоком
```

**Умова.** Хост із контейнерами: 300 рядків у `mountinfo`, з них 40 різних суперблоків.

```
викликів statx  = 40 × 2                = 80
час             ≈ 80 × 2 мкс            ≈ 0.16 мс
створень файлу  ≤ 40 × (create + unlink) ≈ одиниці мс на диску
```

Уся вартість — у створенні зразків, а не в опитуванні. Тому режим `-x` дорожчий за основну таблицю на порядки: рахунок підкаталогів у `/proc` — це сотні записів, а на великому каталозі — десятки тисяч.

## Чого ця таблиця не каже

Найважливіша межа — **один зразок описує один файл, а не файлову систему**. Атрибути `stx_attributes` — властивість файлу: наш новий порожній файл не стиснено й не зашифровано, тож стовпчик «стоїть на зразку» майже завжди порожній. Про можливості ФС каже лише `stx_attributes_mask`, і ось він справді спільний для всього тому.

З полями тонше. `btime` на ext4 — властивість тому, і тут зразок відповідає за всіх. А `dioalign` залежить від конкретного файлу: у стисненого чи вбудованого в inode прямого вводу-виводу не буде, хоч сусідній файл на тому самому томі його має. Загальне правило просте: чим ближче поле до вмісту файлу, тим менше один зразок каже про решту.

Далі — те, що ми обрали не питати. Огляд ходить у типовому режимі синхронізації, і на [мережевій ФС](book:unix-linux/network-filesystems) із `-c` набір бітів може виявитися іншим: відповідь належить тому режиму, у якому її отримано, а не файловій системі взагалі. Пропущені рядки з мертвим сервером — теж дані, і в таблиці їх видно.

І нарешті, усе прочитане описує дерево монтувань **того процесу, який читав**. В іншому [просторі імен](book:unix-linux/namespaces) буде інший `mountinfo`, інші точки й інші відповіді — а всередині контейнера половина рядків виявиться прив'язками, які наш дедуплікатор за номером пристрою згорне в один. Це навмисно: одна файлова система відповідає однаково, скільки б разів її не причепили.
