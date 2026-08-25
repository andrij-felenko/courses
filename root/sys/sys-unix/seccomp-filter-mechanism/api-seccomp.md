# 📋 Контракт seccomp: виклики, прапорці, дії

Це повний перелік того, чим із seccomp розмовляють: два системні виклики, чотири операції, шість прапорців, вісім вироків, півдесятка структур і п'ять ioctl-ів наглядача — з числовими значеннями, версіями ядра й кодами помилок. Числа тут звірено з `include/uapi/linux/seccomp.h`, `kernel/seccomp.c` та сторінками `man 2 seccomp` і `man 2 seccomp_unotify`, і саме числа тут важать: пісочниця не має режиму «майже правильно», а помилковий прапорець дає не попередження, а `EINVAL` посеред уже наполовину зачинених дверей.

## Двоє дверей до одного механізму

```c
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

/* давніші двері: без прапорців і без значення, що повертається */
int prctl(PR_SET_SECCOMP /* 22 */, unsigned long mode, struct sock_fprog *prog);
int prctl(PR_GET_SECCOMP /* 21 */);

/* сучасні двері; обгортки в glibc немає — лише через syscall(2) */
int syscall(SYS_seccomp, unsigned int operation, unsigned int flags, void *args);
```

| що робимо | через `prctl` (з 2.6.23) | через `seccomp()` (з 3.17) |
|---|---|---|
| суворий режим | `prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT /* 1 */, 0)` | `seccomp(SECCOMP_SET_MODE_STRICT, 0, NULL)` |
| фільтр | `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER /* 2 */, &prog)` | `seccomp(SECCOMP_SET_MODE_FILTER, 0, &prog)` |
| фільтр із прапорцями | **неможливо** | `seccomp(SECCOMP_SET_MODE_FILTER, flags, &prog)` |

Рядки таблиці попарно рівносильні: `seccomp()` — це надмножина, і вся її перевага в третьому рядку, бо в `prctl` просто немає куди покласти прапорці. Обидві двері діють на **потік**, а не на процес; поширити фільтр на всі потоки вміє лише прапорець `TSYNC`.

`PR_GET_SECCOMP` виглядає як спосіб спитати «а який у мене зараз режим», але користуватися ним не варто: у суворому режимі сам цей `prctl` заборонений, тож замість відповіді процес отримає `SIGKILL`. Питати треба [файлову систему процесів](topic:sys-unix/proc-reading-process-and-kernel-state) — поле `Seccomp` у `/proc/<pid>/status` (з 3.8) дає те саме число 0/1/2, нікого не вбиваючи, а поле `Seccomp_filters` (з 5.9) показує, скільки фільтрів уже висить на потоці.

## Замок, без якого двері не відчиняться

```c
prctl(PR_SET_NO_NEW_PRIVS /* 38 */, 1, 0, 0, 0);   /* односторонньо, з 3.5 */
prctl(PR_GET_NO_NEW_PRIVS /* 39 */, 0, 0, 0, 0);   /* → 0 або 1 */
```

Установити фільтр дозволено або тому, хто має [можливість](topic:sys-unix/capabilities) `CAP_SYS_ADMIN` у своєму просторі імен користувачів, або тому, хто виставив собі `no_new_privs`. Прапорець назад не знімається, успадковується через `fork`/`clone` і переживає `execve`; для суворого режиму він не потрібен.

## Чотири операції

| операція | значення | `args` | `flags` | успіх повертає | з ядра |
|---|---|---|---|---|---|
| `SECCOMP_SET_MODE_STRICT` | 0 | мусить бути `NULL` | мусять бути 0 | 0 | 3.17 (сам режим — з 2.6.12) |
| `SECCOMP_SET_MODE_FILTER` | 1 | `struct sock_fprog *` | будь-які з наведених нижче | 0, а з `NEW_LISTENER` — **дескриптор** | 3.17 (сам режим — з 3.5) |
| `SECCOMP_GET_ACTION_AVAIL` | 2 | `__u32 *` — одна дія `SECCOMP_RET_*` | мусять бути 0 | 0, тобто дію підтримано | 4.14 |
| `SECCOMP_GET_NOTIF_SIZES` | 3 | `struct seccomp_notif_sizes *` | мусять бути 0 | 0 | 5.0 |

Суворий режим лишає рівно чотири виклики: `read`, `write`, `_exit` (але не `exit_group`) і `sigreturn`. Інших параметрів у нього немає — це не політика, а вимикач.

Дві операції-питання існують через те, що набір дій і розмір структур ростуть із версіями. `GET_ACTION_AVAIL` — єдиний чесний спосіб дізнатися, чи знає це ядро, скажімо, `SECCOMP_RET_USER_NOTIF`: перевіряти версію ядра марно, бо дистрибутиви переносять зміни в старі гілки. `GET_NOTIF_SIZES` віддає розміри трьох структур сповіщення, які наглядач мусить розподіляти саме за цими числами, а не за `sizeof` зі своїх заголовків, — інакше ядро новішої версії заповнить більше, ніж він виділив.

## Шість прапорців

| прапорець | значення | з ядра | що робить |
|---|---|---|---|
| `SECCOMP_FILTER_FLAG_TSYNC` | `1 << 0` | 3.17 | ставить фільтр **усім** [потокам](topic:sys-unix/threads-as-tasks) процесу — або жодному |
| `SECCOMP_FILTER_FLAG_LOG` | `1 << 1` | 4.14 | усі дії цього фільтра, крім `ALLOW`, ідуть у журнал (з огляду на `actions_logged`) |
| `SECCOMP_FILTER_FLAG_SPEC_ALLOW` | `1 << 2` | 4.17 | **не** вмикати автоматично захист від Spectre v4 (обхід збереження в пам'ять), який seccomp інакше нав'язує процесові |
| `SECCOMP_FILTER_FLAG_NEW_LISTENER` | `1 << 3` | 5.0 | повернути дескриптор сповіщень; живий слухач на процес — лише один |
| `SECCOMP_FILTER_FLAG_TSYNC_ESRCH` | `1 << 4` | 5.7 | при невдачі `TSYNC` повертати `-1` з `ESRCH` замість номера потоку |
| `SECCOMP_FILTER_FLAG_WAIT_KILLABLE_RECV` | `1 << 5` | 5.19 | потік, що вже чекає на вирок наглядача, ігнорує нефатальні сигнали |

`TSYNC` спрацьовує за принципом «усе або нічого» і лише тоді, коли синхронізація нікому не додає прав: якщо якийсь інший потік уже носить власний, відмінний ланцюг фільтрів, операція не вдається й не міняє нічого — ні йому, ні тому, хто викликав.

Два останні прапорці — латки на те саме місце: значення, що повертається, перевантажене. `TSYNC` при невдачі віддає **номер потоку**, який не вдалося синхронізувати, тобто додатне число замість `-1`; `NEW_LISTENER` при успіху віддає дескриптор, теж додатне число. Разом вони роблять результат нерозбірливим, тож ядро відкидає таку пару з `EINVAL` — і дозволяє її лише тоді, коли доданий `TSYNC_ESRCH` прибирає першу двозначність.

## Вирок: вісім дій і три маски

| дія | значення | молодші 16 бітів | що стається |
|---|---|---|---|
| `SECCOMP_RET_ALLOW` | `0x7fff0000` | не вживаються | виклик виконується |
| `SECCOMP_RET_LOG` | `0x7ffc0000` | не вживаються | виконується, але з записом у журнал (з 4.14) |
| `SECCOMP_RET_TRACE` | `0x7ff00000` | число для трасувальника, читається через `PTRACE_GETEVENTMSG` | зупинка з подією `PTRACE_EVENT_SECCOMP`; **без трасувальника** виклик не виконується й повертає `ENOSYS` |
| `SECCOMP_RET_USER_NOTIF` | `0x7fc00000` | не вживаються | сповіщення в дескриптор слухача; **без слухача** — `ENOSYS` (з 5.0) |
| `SECCOMP_RET_ERRNO` | `0x00050000` | код `errno`, обрізаний до `MAX_ERRNO` = 4095 | обробник не запускається, виклик повертає цю помилку |
| `SECCOMP_RET_TRAP` | `0x00030000` | потрапляє в `si_errno` | потокові надсилається `SIGSYS` |
| `SECCOMP_RET_KILL_THREAD` (він же `SECCOMP_RET_KILL`) | `0x00000000` | не вживаються | потік гине |
| `SECCOMP_RET_KILL_PROCESS` | `0x80000000` | не вживаються | гине весь процес (з 4.14) |

```c
#define SECCOMP_RET_ACTION_FULL 0xffff0000U   /* дія РАЗОМ зі старшим бітом */
#define SECCOMP_RET_ACTION      0x7fff0000U   /* давня маска: губить KILL_PROCESS */
#define SECCOMP_RET_DATA        0x0000ffffU

/* зібрати вирок: */
ret = SECCOMP_RET_ERRNO | (EACCES & SECCOMP_RET_DATA);   /* 0x00050000 | 0x0d */
```

Маска `SECCOMP_RET_ACTION` старша за `KILL_PROCESS` і не бачить його старшого біта: `0x80000000 & 0x7fff0000` дає нуль, тобто `KILL_THREAD`. Розбираючи чуже слово вироку, беріть `SECCOMP_RET_ACTION_FULL` — ядро розбирає саме нею.

Ще три подробиці, які легко проґавити. Дію, якої ядро не знає, воно тлумачить як найсуворішу — `KILL_PROCESS` з 4.14 і `KILL_THREAD` раніше, тож несподівано вбитий процес може означати не заборону, а вирок із майбутнього. Смерть від seccomp виглядає як `SIGSYS`, а не `SIGKILL`: у стані завершення `status & 0x7f` дорівнює саме `SIGSYS`. А `TRAP` кладе в опис сигналу все потрібне для діагностики — `si_code` = `SYS_SECCOMP`, `si_syscall` = номер, `si_arch` = архітектура, `si_call_addr` = адреса інструкції виклику, `si_errno` = молодші біти вироку.

Перелік дій, які вміє це ядро, лежить у `/proc/sys/kernel/seccomp/actions_avail` (тільки читання, у порядку спадання суворості), а перелік тих, які дозволено журналювати, — у `/proc/sys/kernel/seccomp/actions_logged`.

## Структури на вході

```c
struct seccomp_data {          /* вхідний буфер програми-фільтра */
    int   nr;                  /* зсув  0 */
    __u32 arch;                /* зсув  4  — константа AUDIT_ARCH_* */
    __u64 instruction_pointer; /* зсув  8 */
    __u64 args[6];             /* зсув 16, далі 24, 32, 40, 48, 56 */
};

struct sock_filter {           /* одна інструкція BPF, рівно 8 байтів */
    __u16 code;                /* що робити */
    __u8  jt, jf;              /* куди стрибати: правда / неправда */
    __u32 k;                   /* стала */
};

struct sock_fprog {
    unsigned short      len;   /* кількість інструкцій, 1…4096 */
    struct sock_filter *filter;
};

#define BPF_STMT(code, k)          { (unsigned short)(code), 0, 0, k }
#define BPF_JUMP(code, k, jt, jf)  { (unsigned short)(code), jt, jf, k }
```

Зсуви в інструкціях `BPF_LD | BPF_W | BPF_ABS` відлічуються від початку `seccomp_data` — пишіть їх через `offsetof`, а не числами. Слово завантаження — 32-бітне, тож 64-бітний аргумент читається двома заходами: `offsetof(struct seccomp_data, args[n])` і те саме плюс 4; на прямому порядку байтів перший захід дає молодшу половину. Стрибки `jt`/`jf` — це кількість інструкцій, які треба **пропустити**, рахуючи від наступної, і лише вперед.

## Наглядач: структури й ioctl-и

```c
struct seccomp_notif_sizes { __u16 seccomp_notif, seccomp_notif_resp, seccomp_data; };

struct seccomp_notif      { __u64 id; __u32 pid; __u32 flags; struct seccomp_data data; };
struct seccomp_notif_resp { __u64 id; __s64 val; __s32 error; __u32 flags; };
struct seccomp_notif_addfd{ __u64 id; __u32 flags; __u32 srcfd, newfd, newfd_flags; };

#define SECCOMP_USER_NOTIF_FLAG_CONTINUE   (1UL << 0)  /* у resp.flags, з 5.5 */
#define SECCOMP_ADDFD_FLAG_SETFD           (1UL << 0)  /* вжити задане newfd */
#define SECCOMP_ADDFD_FLAG_SEND            (1UL << 1)  /* addfd + send атомарно, з 5.14 */
#define SECCOMP_USER_NOTIF_FD_SYNC_WAKE_UP (1UL << 0)  /* у SET_FLAGS, з 6.6 */
```

| ioctl | номер | аргумент | успіх | часті помилки |
|---|---|---|---|---|
| `SECCOMP_IOCTL_NOTIF_RECV` | `_IOWR('!', 0, struct seccomp_notif)` | буфер, **заздалегідь занулений** | 0, буфер заповнено | `ENOENT` — підопічний загинув або його виклик перервано сигналом; `EINVAL` — у буфері були ненульові поля (з 5.5) |
| `SECCOMP_IOCTL_NOTIF_SEND` | `_IOWR('!', 1, struct seccomp_notif_resp)` | заповнена відповідь | 0 | `EINPROGRESS` — на це сповіщення вже відповіли; `ENOENT`; `EINVAL` — `CONTINUE` разом із ненульовими `val`/`error` |
| `SECCOMP_IOCTL_NOTIF_ID_VALID` | `_IOW('!', 2, __u64)` | вказівник на `id` | 0 — сповіщення ще живе | `ENOENT` — уже ні |
| `SECCOMP_IOCTL_NOTIF_ADDFD` | `_IOW('!', 3, struct seccomp_notif_addfd)` | опис дескриптора | номер [дескриптора](topic:sys-unix/file-descriptor) в підопічного | `EBADF` — `srcfd` не відкритий у наглядача; `EMFILE` — упреться в `RLIMIT_NOFILE`; `EBUSY`; `EINPROGRESS`; `ENOENT` |
| `SECCOMP_IOCTL_NOTIF_SET_FLAGS` | `_IOW('!', 4, __u64)` | прапорці самого дескриптора | 0 | `EINVAL` |

Ці ioctl-и живуть під літерою-магією `'!'` — про те, як така [операція над дескриптором](topic:sys-unix/ioctl-interface) кодує напрямок і розмір, варто пам'ятати саме тут: `NOTIF_ID_VALID` спершу описали з неправильним напрямком (`_IOR` замість `_IOW`), і ядро досі приймає обидва номери, щоб не зламати давні програми.

Дві дрібниці у відповіді коштують найбільше налагодження. Поле `pid` у сповіщенні — це ідентифікатор **потоку**, який спіткнувся об фільтр, а не процесу. А поля `val` і `error` у відповіді розділені за знаком і не взаємозамінні: `error = 0` означає вдалий виклик, і тоді підопічний отримає число з `val`; невдачу описують **від'ємним** номером помилки в `error` (скажімо, `-EPERM`), а `val` тоді не вживається. Плюс замість мінуса тут дає підопічному не заборону, а безглуздий успіх.

Сам дескриптор сповіщень поводиться як звичайний файловий об'єкт і його можна тримати в загальному циклі очікування: доки є неотримане сповіщення, він читанний; після `RECV` і до `SEND` — записний; коли підопічний завершився, читання дає ознаку кінця файлу.

Порядок роботи наглядача жорсткий: `RECV` (блокує, доки не буде події) → рішення → `SEND`. Якщо між ними наглядач читає пам'ять підопічного через `/proc/<pid>/mem`, `ID_VALID` треба питати **до і після** читання: інакше можна прочитати пам'ять уже мертвого процесу, чий номер устигли перевикористати. `SECCOMP_USER_NOTIF_FLAG_CONTINUE` каже ядру виконати перехоплений виклик як є — і саме тому на ньому не можна будувати політику безпеки: між перевіркою аргументів наглядачем і виконанням виклику інший потік підопічного встигне їх переписати. Дозволяти цим прапорцем можна лише те, що й так безпечне.

## Стелі

```
BPF_MAXINSNS       = 4096                                   інструкцій на ОДИН фільтр
MAX_INSNS_PER_PATH = (1 << 18) / sizeof(struct sock_filter)
                   = 262144 / 8 = 32768                     інструкцій на весь ланцюг

бюджет ланцюга:  len(новий) + Σ (len(кожного старого) + 4) ≤ 32768
```

Розрізняти дві стелі варто за помилкою: завелика окрема програма (як і `len == 0`) — це `EINVAL` ще на перевірці, а вичерпаний спільний бюджет — `ENOMEM`. Надбавка в чотири інструкції за кожен уже встановлений фільтр — це плата за саме існування ланки в ланцюзі, тож десятки дрібних фільтрів обходяться дорожче за один великий.

## Коди помилок

| errno | коли |
|---|---|
| `EACCES` | немає ні `CAP_SYS_ADMIN` у своєму просторі імен користувачів, ні виставленого `no_new_privs` |
| `EBUSY` | заявлено `NEW_LISTENER`, а слухач у процесі вже є |
| `EFAULT` | `args` або `fprog->filter` показує за межі адресного простору |
| `EINVAL` | невідома операція чи прапорець; ядро зібране без `CONFIG_SECCOMP_FILTER`; `flags ≠ 0` там, де мусять бути 0; `TSYNC` разом із `NEW_LISTENER` без `TSYNC_ESRCH`; `len` дорівнює 0 або більший за 4096; програма не пройшла перевірку (невідомий код операції, зсув поза `seccomp_data` чи невирівняний, стрибок за межі, остання інструкція не `BPF_RET`) |
| `ENOMEM` | не вистачило пам'яті або ланцюг перебрав `MAX_INSNS_PER_PATH` |
| `EOPNOTSUPP` | `GET_ACTION_AVAIL`: такої дії ядро не знає |
| `ESRCH` | `TSYNC`: інший потік має несумісний фільтр (з `TSYNC_ESRCH` — замість номера того потоку) |

## Мінімальний робочий виклик

```c
#define _GNU_SOURCE
#include <errno.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <stddef.h>
#include <stdio.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/utsname.h>
#include <unistd.h>

int main(void)
{
    struct sock_filter code[] = {
        /* 0 */ BPF_STMT(BPF_LD  | BPF_W   | BPF_ABS, offsetof(struct seccomp_data, arch)),
        /* 1 */ BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        /* 2 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        /* 3 */ BPF_STMT(BPF_LD  | BPF_W   | BPF_ABS, offsetof(struct seccomp_data, nr)),
        /* 4 */ BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_uname, 0, 1),
        /* 5 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),
        /* 6 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    struct sock_fprog prog = { .len = sizeof code / sizeof code[0], .filter = code };

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0))
        return perror("no_new_privs"), 1;
    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog))
        return perror("seccomp"), 1;

    struct utsname u;
    if (uname(&u) == -1)
        perror("uname");        /* → uname: Operation not permitted */
    return 0;
}
```

Сім інструкцій показують увесь контракт у зборі: спершу звіряється `arch` (інакше номер `nr` означав би виклик із чужої таблиці), далі один номер відсікається помилкою, решта дозволена. `perror` після заборони працює, бо `write` фільтр пропускає — і це найпростіша перевірка, що політика справді жива.
