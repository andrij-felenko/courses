# 📋 Контракт posix_spawn: дії, атрибути, помилки, версії

Тут зібрано все, чим наповнюють два описи, які `posix_spawn` бере замість проміжку між народженням і заміною образу: повний словник дій із файлами, повний набір атрибутів, точний порядок їх застосування, домовленість про помилки — і версія, з якої кожен пункт існує. Остання колонка тут не формальність: майже все, що робить цей інтерфейс придатним для справжнього запуску програм, з'явилося після 2017 року, і код, написаний за старшою документацією, руками обходить те, що вже є в бібліотеці.

## Заголовок і два підписи

```c
#include <spawn.h>

int posix_spawn (pid_t *restrict pid, const char *restrict path,
                 const posix_spawn_file_actions_t *restrict file_actions,
                 const posix_spawnattr_t *restrict attrp,
                 char *const argv[restrict], char *const envp[restrict]);

int posix_spawnp(pid_t *restrict pid, const char *restrict file,
                 const posix_spawn_file_actions_t *restrict file_actions,
                 const posix_spawnattr_t *restrict attrp,
                 char *const argv[restrict], char *const envp[restrict]);
```

| аргумент | значення |
|---|---|
| `pid` | сюди кладуть номер дитини; заповнено **лише** при поверненні нуля. `NULL` дозволено — тоді номер просто губиться |
| `path` / `file` | що виконати. `posix_spawn` бере шлях як є; `posix_spawnp` за іменем без скісної риски шукає в `PATH` |
| `file_actions` | список дій із дескрипторами, або `NULL` — «нічого не чіпати» |
| `attrp` | набір властивостей дитини, або `NULL` — «нічого не міняти» |
| `argv` | масив аргументів, кінець — `NULL`; `argv[0]` — те, чим програма себе побачить |
| `envp` | оточення новою програмою, кінець — `NULL`; звичайне значення — глобальна `environ` |

Обидві функції живуть у бібліотеці С, окремо лінкувати нічого не треба. Розширення GNU — усе з суфіксом `_np`, `POSIX_SPAWN_SETSID`, `pidfd_spawn` — оголошені лише під `_GNU_SOURCE`, і цей `#define` мусить стояти **перед** усіма `#include`.

Пошук у `PATH` робить бібліотека вже в дитині, тож тут повторюється поведінка `execvp`: файл із невідомим ядру форматом віддають `/bin/sh` першим аргументом ([родина exec](book:unix-linux/exec-semantics) — які форми запуску існують і чим відрізняються). У glibc сам рядок `PATH` при цьому беруть з оточення того, хто кличе, — `getenv("PATH")`, — а не з переданого `envp`; коли в оточенні `PATH` немає, у хід іде типовий системний шлях `_CS_PATH`. Тобто `envp` задає оточення новій програмі, але не керує пошуком, яким її знайшли. Хочете керувати пошуком напевно — складайте повний шлях і кличте `posix_spawn`.

## Порядок: що коли відбувається

Порядок тут — не деталь реалізації, а частина стандарту, і половина непорозумінь із цим інтерфейсом береться з того, що його не прочитали.

![Послідовність усередині posix_spawn: атрибути, потім дії з файлами, потім закриття CLOEXEC, потім exec; помилка йде назад до батька спільною пам'яттю](/reference/unix-linux/processes/spawn-alternatives/img/spawn-order.svg)

*Атрибути лягають перед діями з файлами, а закриття «закритих при заміні образу» — після них; переставити ці шари не можна ніяк.*

1. Набір відкритих дескрипторів дитини спочатку такий самий, як у батька.
2. Застосовують **атрибути**: сеанс і група процесів, скидання ідентифікаторів, планування, маска сигналів, скидання диспозицій.
3. Виконують **дії з файлами** — строго в тому порядку, у якому їх додавали.
4. Закривають усі дескриптори, позначені `FD_CLOEXEC`.
5. Виконують `execve` (чи пошук у `PATH` і `execve`).

Три наслідки, які варто витягти з цієї послідовності одразу.

**Дії з файлами йдуть після атрибутів.** Отже, `addopen` уже виконується від нової робочої теки, якщо перед ним у списку стояв `addchdir`, — але від **старих** привілеїв, якщо `POSIX_SPAWN_RESETIDS` не виставлено. Відкрити файл «правами дитини» цим інтерфейсом не можна: права на кроці 3 ще батькові, якщо їх не змінив крок 2.

**Крок 4 — після кроку 3.** Тому дескриптор, який ви поклали на місце через `adddup2`, переживає заміну образу: `dup2` завжди знімає `FD_CLOEXEC` з копії, і крок 4 її не зачепить. А от оригінал, помічений `FD_CLOEXEC`, крок 4 закриє — і це саме те, чого хочуть. Звідси головна практика: труби створюють одразу з `O_CLOEXEC`, а в дитину пускають тільки їхні копії, зроблені `adddup2`.

**Диспозиції сигналів дитина дістає не такі, як у батька.** Стандарт вимагає: сигнали, які батько **ловив**, у дитини стають типовими. Це відбувається саме так і без жодних прапорців — заміна образу все одно скидає обробники, бо їхніх адрес у новій програмі немає. Проігноровані (`SIG_IGN`) сигнали, навпаки, лишаються проігнорованими наскрізь, і маска сигналів переживає заміну образу цілою. Саме заради цих двох речей і існують `POSIX_SPAWN_SETSIGDEF` і `POSIX_SPAWN_SETSIGMASK` ([диспозиція сигналу](book:unix-linux/signal-disposition) — три можливі долі сигналу: обробник, ігнорування, типова дія).

Ще один рядок стандарту редакції 2024 року стосується прапорця `FD_CLOFORK`: дескриптори з ним не потрапляють у дитину взагалі. Linux його не має — там існує лише `FD_CLOEXEC`, і його перевіряють на кроці 4.

## Об'єкт дій із файлами

Об'єкт створюють, наповнюють, віддають у виклик і знищують. Наповнення — це **список**, а не множина: два записи на той самий дескриптор не конфліктують, вони просто виконаються один за одним.

```c
int posix_spawn_file_actions_init   (posix_spawn_file_actions_t *fa);
int posix_spawn_file_actions_destroy(posix_spawn_file_actions_t *fa);
```

| дія | що станеться в дитині | де вона є |
|---|---|---|
| `addopen(fa, fd, path, oflag, mode)` | `open(path, oflag, mode)`, і якщо номер вийшов інший — перенести на `fd`; якщо `fd` уже був відкритий, його спершу закривають | POSIX.1-2001 |
| `addclose(fa, fd)` | `close(fd)`; вже закритий невід'ємний `fd` **не помилка**, а порожня дія | POSIX.1-2001 |
| `adddup2(fa, fd, newfd)` | `dup2(fd, newfd)`; при `fd == newfd` — не порожня дія, а «лишити цей дескриптор відкритим після заміни образу» | POSIX.1-2001; правило рівних номерів — Issue 8 (2024), у glibc з 2.29 |
| `addchdir(fa, path)` | `chdir(path)` | POSIX.1-2024; glibc має як `addchdir_np` з 2.29 |
| `addfchdir(fa, fd)` | `fchdir(fd)` | POSIX.1-2024; glibc має як `addfchdir_np` з 2.29 |
| `addclosefrom_np(fa, from)` | закрити всі дескриптори з номерами ≥ `from` | розширення GNU, glibc 2.34 (є й у Solaris) |
| `addtcsetpgrp_np(fa, fd)` | зробити групу процесів дитини передньою для термінала, на який указує `fd` | розширення GNU, glibc 2.35 |

Усі вони повертають **номер помилки**, а не −1: `ENOMEM`, якщо не вдалося наростити список; `EBADF`, якщо номер дескриптора не пройшов перевірку межі; `EINVAL`, якщо сам об'єкт недійсний. Межа тут не стала: сталої `OPEN_MAX` Linux не має, тож glibc в усіх трьох будівничих звіряє номер із `sysconf(_SC_OPEN_MAX)` — тобто з чинним `RLIMIT_NOFILE` — і відхиляє від'ємний або не менший за неї (якщо межі немає, лишається сама перевірка на від'ємність).

Чотири речі з цієї таблиці варті окремих слів.

**`adddup2` з однаковими номерами — це не `dup2`, а зняття `FD_CLOEXEC`.** Виглядає як дивина, але саме цього бракувало десятиліттями: іншого способу сказати «цей конкретний дескриптор має потрапити в дитину, а решта — ні» в словнику не було. Austin Group оформила це зверненням № 411 (там же зібрано весь атомарний `FD_CLOEXEC`); у чинному тексті стандарту правило стоїть із редакції 2024 року, а glibc реалізувала його на п'ять років раніше, у 2.29.

**Порядок `addclosefrom_np` критичний.** Якщо поставити його першим, він закриє й ті кінці труб, які ви збиралися продублювати наступними рядками. Ставлять останнім, із межею `3` — після того, як усе потрібне вже перенесено на номери 0, 1, 2 ([файловий дескриптор](book:unix-linux/file-descriptor) — мале ціле, індекс у таблиці процесу; саме номер, а не файл, тут головна валюта).

**`addopen` слухається `umask`.** Аргумент `mode` — це бажані права, а не остаточні: біти, зняті маскою процесу, буде знято й тут ([umask і типові права](book:unix-linux/umask-and-defaults) — чому створений файл майже ніколи не має рівно тих прав, які просили).

**Порожній перший-другий-третій.** Класична пастка: якщо в момент виклику дескриптори 0, 1 і 2 закриті, свіжостворена труба сяде саме на них — і подальші `adddup2` на `STDIN_FILENO` почнуть перекривати самі себе. Тому програми, які запускають підпроцеси, на старті переконуються, що три стандартні номери зайняті хоч чимось (`/dev/null` цілком годиться).

Об'єкт дій **не можна копіювати структурним присвоєнням**. У glibc всередині нього лежить покажчик на масив у купі; копія структури й два виклики `destroy` дають подвійне звільнення. Один і той самий об'єкт натомість можна безпечно віддавати в багато викликів поспіль — виклик його не змінює.

## Атрибути

Тут працює правило, порушення якого — найтихіша помилка з усіх: **значення без свого прапорця не робить нічого**. Виставили групу процесів, забули `POSIX_SPAWN_SETPGROUP` — дитина мовчки лишиться в групі батька, жодної помилки ніхто не поверне.

```c
int posix_spawnattr_init   (posix_spawnattr_t *at);
int posix_spawnattr_destroy(posix_spawnattr_t *at);
```

| що зберігає атрибут | сетер і гетер | вмикається прапорцем |
|---|---|---|
| набір прапорців | `setflags` / `getflags` | — |
| група процесів | `setpgroup` / `getpgroup` | `POSIX_SPAWN_SETPGROUP` |
| сигнали, яким повернути типову дію | `setsigdefault` / `getsigdefault` | `POSIX_SPAWN_SETSIGDEF` |
| маска сигналів | `setsigmask` / `getsigmask` | `POSIX_SPAWN_SETSIGMASK` |
| параметри планування (`struct sched_param`) | `setschedparam` / `getschedparam` | `POSIX_SPAWN_SETSCHEDPARAM` |
| політика планування (`SCHED_*`) | `setschedpolicy` / `getschedpolicy` | `POSIX_SPAWN_SETSCHEDULER` |
| дескриптор теки cgroup | `setcgroup_np` / `getcgroup_np` | `POSIX_SPAWN_SETCGROUP` |

| прапорець | що робить у дитині | де він є |
|---|---|---|
| `POSIX_SPAWN_RESETIDS` | дієві UID і GID стають рівними реальним | POSIX.1-2001 |
| `POSIX_SPAWN_SETPGROUP` | `setpgid(0, pgroup)`; значення `0` означає «стань лідером власної групи» | POSIX.1-2001 |
| `POSIX_SPAWN_SETSIGDEF` | сигналам із заданої множини повертають типову дію | POSIX.1-2001 |
| `POSIX_SPAWN_SETSIGMASK` | маску сигналів заміняють на задану | POSIX.1-2001 |
| `POSIX_SPAWN_SETSCHEDPARAM` | ставлять параметри планування, політику лишають | POSIX.1-2001 |
| `POSIX_SPAWN_SETSCHEDULER` | ставлять політику **і** параметри | POSIX.1-2001 |
| `POSIX_SPAWN_SETSID` | `setsid()`: новий сеанс, новий лідер, без керівного термінала | POSIX.1-2024; glibc 2.26, є й у musl |
| `POSIX_SPAWN_SETCGROUP` | дитина народжується одразу в заданій контрольній групі | розширення GNU, glibc 2.39 |
| `POSIX_SPAWN_USEVFORK` | історичний: змушував брати `vfork`. У glibc з 2.24 не робить нічого | розширення GNU |

`POSIX_SPAWN_RESETIDS` варто прочитати точно: він не змінює того, **хто** ви, він лише прибирає підвищення. Дієвий ідентифікатор стає рівним реальному, а наступна заміна образу на файл без бітів підвищення дописує те саме значення й у збережений — тобто після старту програма вже не може повернути підвищені права ([setuid і підвищення прав](book:unix-linux/setuid-and-privilege) — три ідентифікатори процесу й правила переходів між ними). Стати іншим користувачем цим прапорцем неможливо: `setuid` у словнику атрибутів немає.

`POSIX_SPAWN_SETPGROUP` разом із `addtcsetpgrp_np` покривають повний ритуал керування завданнями: дитина дістає власну групу процесів і одразу стає передньою для термінала — без гонитви, у якій оболонка й дитина обидві намагаються призначити передню групу ([керування завданнями](book:unix-linux/job-control) — як оболонка ділить термінал між передніми й фоновими завданнями). Політику планування ставлять `POSIX_SPAWN_SETSCHEDULER`, і тільки він, разом із параметрами, дає повний реальночасовий клас ([пріоритети й реальночасові класи](book:unix-linux/priority-nice-realtime) — чим `SCHED_FIFO` відрізняється від звичайного розділу часу).

> 🔧 **Навіщо це.** Найчастіша реальна поломка тут — не швидкість і не права, а успадковане `SIG_IGN`. Демон чи оболонка ставить `SIG_IGN` на `SIGINT` або `SIGPIPE`, щоб не вмирати від них, запускає підпроцес — і той дістає це ігнорування назавжди, бо заміна образу скидає обробники, але не ігнорування. Наслідок: `Ctrl+C` не спиняє команду, а конвеєр не завершується, коли читач помер. Ліки — один рядок: заповнити `spawn-sigdefault` через `sigfillset` і виставити `POSIX_SPAWN_SETSIGDEF`. Той самий рядок закриває й другу половину: успадковану маску, у якій міг лишитися заблокований `SIGCHLD` чи `SIGTERM` ([маскування сигналів](book:unix-linux/signal-mask-signalfd) — чим блокування відрізняється від ігнорування й чому маска переживає заміну образу).

## Помилки: повертають, а не кладуть у `errno`

Це друга домовленість, яку найчастіше порушують. Уся родина `posix_spawn*` повертає **номер помилки як значення**; `errno` вона не чіпає взагалі, а нуль означає успіх. Тому `perror("posix_spawn")` після виклику друкує невідомо що, а правильний рядок — `strerror(rc)`.

| `errno` | звідки | коли |
|---|---|---|
| `EAGAIN` | народження | вичерпано `RLIMIT_NPROC` або системну межу задач |
| `ENOMEM` | народження, будівничі | бракує пам'яті ядра чи купи |
| `EINVAL` | атрибути | невідомий біт у наборі прапорців, недійсна політика планування, недійсний об'єкт |
| `ENOSYS` | реалізація | система не підтримує спавн узагалі (опція POSIX вимкнена) |
| `EBADF` | дії з файлами | `adddup2` чи `addfchdir` на дескрипторі, якого немає |
| `EMFILE`, `ENFILE` | дії з файлами | `addopen` уперся в ліміт відкритих файлів |
| `ENOENT`, `EACCES`, `ENOTDIR`, `ELOOP`, `ENAMETOOLONG` | `addopen`, `addchdir`, `exec` | звичайні помилки розбору шляху ([розбір шляху](book:unix-linux/path-resolution) — як ім'я перетворюється на файл і де в цьому ланцюжку виникає кожна з цих помилок) |
| `E2BIG`, `ENOEXEC`, `ETXTBSY`, `EPERM`, `EISDIR`, `ELIBBAD` | `exec` | те саме, що в `execve` ([повний перелік помилок exec](book:unix-linux/exec-semantics/api-exec-family.md)) |

Тепер найтонше місце всього інтерфейсу. Стандарт **дозволяє** реалізації не повертати помилки з другої половини списку: якщо збій стався вже після того, як виклик успішно повернувся, дитина просто виходить із кодом 127. Тобто переносний код мусить розрізняти два різні світи.

glibc від версії 2.24 живе в кращому з них. Її `posix_spawn` кличе `clone` із `CLONE_VM | CLONE_VFORK`, тож пам'ять із дитиною спільна; дитина кладе туди номер помилки, батько прокидається, забирає невдалу дитину через `waitid` і **повертає саме цей номер**. Побічний наслідок того ж рішення: обробники, зареєстровані через `pthread_atfork`, не запускаються взагалі. Від версії 2.38 до цього додався `CLONE_CLEAR_SIGHAND` (ядро 5.5, а отже вже `clone3`): він разом скидає всі перехоплені сигнали в `SIG_DFL`, тож бібліотеці більше не треба обходити всі номери двома `sigaction` кожен, і дитина ніде посередині не виконає обробника з таблиці батька. На старішому ядрі виклик відступає на звичайний `clone` і той самий обхід.

Практичний висновок — перевіряти обидва шляхи:

```c
int rc = posix_spawnp(&pid, prog, &fa, &at, argv, environ);
if (rc != 0) {
    /* дитини або немає, або її вже прибрано — waitpid тут НЕ кличуть */
    fprintf(stderr, "%s: %s\n", prog, strerror(rc));
    return -1;
}
int st;
waitpid(pid, &st, 0);
if (WIFEXITED(st) && WEXITSTATUS(st) == 127)
    fprintf(stderr, "%s: схоже, запустити не вдалося\n", prog);
```

Друга гілка — здогад, а не факт: код 127 могла повернути й сама програма ([код виходу як інтерфейс](book:unix-linux/exit-status) — одне число, яким процес звітує про долю). Розрізнити напевно можна лише власним каналом, і саме тому шлях glibc кращий.

## Мінімальний робочий приклад

Запустити `sort -n`, згодувати йому рядки зі своєї пам'яті, відсортоване покласти у файл, повідомлення про помилки викинути, дитину поставити у власну групу процесів і віддати їй чисті сигнали. Усе це — без жодного рядка нашого коду в дитині ([канали](book:unix-linux/pipe-and-fifo) — однобічний потік байтів, у якого закриття кінця на запис означає кінець даних).

:::tabs
```c
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <spawn.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;

#ifdef __GLIBC_PREREQ
# if __GLIBC_PREREQ(2, 34)
#  define HAVE_ADDCLOSEFROM 1
# endif
#endif

/* Будівничі повертають номер помилки; тримаємо перший ненульовий. */
#define STEP(call) do { if (rc == 0) rc = (call); } while (0)

/* 0 — усе гаразд і статус у *status; інакше номер помилки запуску. */
static int run_sort(const char *lines, const char *out_path, int *status)
{
    posix_spawn_file_actions_t fa;
    posix_spawnattr_t at;
    sigset_t empty, all;
    char *argv[] = { "sort", "-n", NULL };
    int pfd[2], rc;
    pid_t pid;

    if (pipe2(pfd, O_CLOEXEC) == -1)     /* обидва кінці — з FD_CLOEXEC */
        return errno;                    /* pipe2 — стара домовленість: −1 і errno */

    rc = posix_spawn_file_actions_init(&fa);
    if (rc != 0) {
        close(pfd[0]); close(pfd[1]);
        return rc;
    }
    rc = posix_spawnattr_init(&at);
    if (rc != 0) {
        posix_spawn_file_actions_destroy(&fa);
        close(pfd[0]); close(pfd[1]);
        return rc;
    }

    /* Дії виконаються рівно в цьому порядку. */
    STEP(posix_spawn_file_actions_adddup2(&fa, pfd[0], STDIN_FILENO));
    STEP(posix_spawn_file_actions_addopen(&fa, STDOUT_FILENO, out_path,
                                          O_WRONLY | O_CREAT | O_TRUNC, 0644));
    STEP(posix_spawn_file_actions_addopen(&fa, STDERR_FILENO, "/dev/null",
                                          O_WRONLY, 0));
#ifdef HAVE_ADDCLOSEFROM
    STEP(posix_spawn_file_actions_addclosefrom_np(&fa, 3));  /* тільки останнім! */
#endif

    sigemptyset(&empty);
    sigfillset(&all);
    STEP(posix_spawnattr_setsigmask(&at, &empty));    /* чиста маска */
    STEP(posix_spawnattr_setsigdefault(&at, &all));   /* жодного успадкованого SIG_IGN */
    STEP(posix_spawnattr_setpgroup(&at, 0));          /* власна група процесів */
    STEP(posix_spawnattr_setflags(&at, POSIX_SPAWN_SETSIGMASK
                                     | POSIX_SPAWN_SETSIGDEF
                                     | POSIX_SPAWN_SETPGROUP));

    if (rc == 0)
        rc = posix_spawnp(&pid, "sort", &fa, &at, argv, environ);

    posix_spawn_file_actions_destroy(&fa);
    posix_spawnattr_destroy(&at);
    close(pfd[0]);                       /* кінець на читання лишається дитині */

    if (rc != 0) {
        close(pfd[1]);
        return rc;
    }

    write(pfd[1], lines, strlen(lines));
    close(pfd[1]);                       /* закриття = кінець вводу для sort */

    return waitpid(pid, status, 0) == -1 ? errno : 0;
}

int main(void)
{
    int status = 0;

    signal(SIGPIPE, SIG_IGN);            /* інакше мертвий sort уб'є нас під час write */

    int err = run_sort("30\n4\n100\n7\n", "sorted.txt", &status);
    if (err != 0) {
        fprintf(stderr, "запустити не вдалося: %s\n", strerror(err));
        return 1;
    }
    if (WIFEXITED(status) && WEXITSTATUS(status) == 127)
        fprintf(stderr, "код 127: на цій системі так звітують про невдалий запуск\n");
    return 0;
}
```
```cpp
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <spawn.h>
#include <sys/wait.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <string_view>
#include <system_error>
#include <vector>

extern char **environ;

#ifdef __GLIBC_PREREQ
# if __GLIBC_PREREQ(2, 34)
#  define HAVE_ADDCLOSEFROM 1
# endif
#endif

class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) ::close(fd_);
        fd_ = new_fd;
    }
    [[nodiscard]] int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

class PosixSpawnFileActions {
    posix_spawn_file_actions_t fa_{};
public:
    PosixSpawnFileActions() {
        if (int err = ::posix_spawn_file_actions_init(&fa_))
            throw std::system_error(err, std::generic_category(), "init file actions");
    }
    ~PosixSpawnFileActions() noexcept { ::posix_spawn_file_actions_destroy(&fa_); }

    void add_dup2(int fd, int newfd) {
        if (int err = ::posix_spawn_file_actions_adddup2(&fa_, fd, newfd))
            throw std::system_error(err, std::generic_category(), "adddup2");
    }
    void add_open(int fd, const char* path, int flags, mode_t mode) {
        if (int err = ::posix_spawn_file_actions_addopen(&fa_, fd, path, flags, mode))
            throw std::system_error(err, std::generic_category(), "addopen");
    }
#ifdef HAVE_ADDCLOSEFROM
    void add_closefrom(int from) {
        if (int err = ::posix_spawn_file_actions_addclosefrom_np(&fa_, from))
            throw std::system_error(err, std::generic_category(), "addclosefrom");
    }
#endif
    const posix_spawn_file_actions_t* get() const noexcept { return &fa_; }
};

class PosixSpawnAttr {
    posix_spawnattr_t at_{};
public:
    PosixSpawnAttr() {
        if (int err = ::posix_spawnattr_init(&at_))
            throw std::system_error(err, std::generic_category(), "init spawn attr");
    }
    ~PosixSpawnAttr() noexcept { ::posix_spawnattr_destroy(&at_); }

    void set_sigmask(const sigset_t& mask) {
        if (int err = ::posix_spawnattr_setsigmask(&at_, &mask))
            throw std::system_error(err, std::generic_category(), "setsigmask");
    }
    void set_sigdefault(const sigset_t& mask) {
        if (int err = ::posix_spawnattr_setsigdefault(&at_, &mask))
            throw std::system_error(err, std::generic_category(), "setsigdefault");
    }
    void set_pgroup(pid_t pg) {
        if (int err = ::posix_spawnattr_setpgroup(&at_, pg))
            throw std::system_error(err, std::generic_category(), "setpgroup");
    }
    void set_flags(short flags) {
        if (int err = ::posix_spawnattr_setflags(&at_, flags))
            throw std::system_error(err, std::generic_category(), "setflags");
    }
    const posix_spawnattr_t* get() const noexcept { return &at_; }
};

static int run_sort(std::string_view lines, const char *out_path, int *status) {
    int pfd[2];
    if (::pipe2(pfd, O_CLOEXEC) == -1)
        return errno;
    UniqueFd read_end(pfd[0]);
    UniqueFd write_end(pfd[1]);

    try {
        PosixSpawnFileActions fa;
        fa.add_dup2(read_end.get(), STDIN_FILENO);
        fa.add_open(STDOUT_FILENO, out_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        fa.add_open(STDERR_FILENO, "/dev/null", O_WRONLY, 0);
#ifdef HAVE_ADDCLOSEFROM
        fa.add_closefrom(3);
#endif

        PosixSpawnAttr at;
        sigset_t empty, all;
        ::sigemptyset(&empty);
        ::sigfillset(&all);
        at.set_sigmask(empty);
        at.set_sigdefault(all);
        at.set_pgroup(0);
        at.set_flags(POSIX_SPAWN_SETSIGMASK | POSIX_SPAWN_SETSIGDEF | POSIX_SPAWN_SETPGROUP);

        std::vector<const char*> argv = { "sort", "-n", nullptr };
        pid_t pid = 0;
        int rc = ::posix_spawnp(&pid, "sort", fa.get(), at.get(),
                               const_cast<char* const*>(argv.data()), environ);
        if (rc != 0) return rc;

        read_end.reset();

        const char* ptr = lines.data();
        size_t remaining = lines.size();
        while (remaining > 0) {
            ssize_t written = ::write(write_end.get(), ptr, remaining);
            if (written < 0) {
                if (errno == EINTR) continue;
                break;
            }
            ptr += written;
            remaining -= written;
        }
        write_end.reset();

        return ::waitpid(pid, status, 0) == -1 ? errno : 0;
    } catch (const std::system_error& e) {
        return e.code().value();
    }
}

int main() {
    int status = 0;
    ::signal(SIGPIPE, SIG_IGN);

    int err = run_sort("30\n4\n100\n7\n", "sorted.txt", &status);
    if (err != 0) {
        std::cerr << "запустити не вдалося: " << std::strerror(err) << '\n';
        return 1;
    }
    if (WIFEXITED(status) && WEXITSTATUS(status) == 127) {
        std::cerr << "код 127: на цій системі так звітують про невдалий запуск\n";
    }
    return 0;
}
```
:::

Два місця тут навмисні. `pipe2` з `O_CLOEXEC` замість `pipe` — щоб між створенням труби й запуском інший потік не встиг зробити свою заміну образу й успадкувати наш кінець на запис; тоді `sort` не дочекався б кінця вводу ніколи. А `adddup2` без жодного `addclose` на кінці труби — бо крок 4 (закриття всіх `FD_CLOEXEC`) прибере обидва оригінали сам, лишивши тільки копію на нульовому номері, з якої `dup2` уже зняв прапорець.

## Розширення glibc: cgroup і pidfd

Два додатки версії 2.39 прибирають ті самі проміжки, що й нові прапорці `clone3`, — тільки на рівні бібліотеки.

```c
#define _GNU_SOURCE
#include <fcntl.h>
#include <spawn.h>
#include <sys/wait.h>

/* Народити дитину одразу в потрібній контрольній групі. */
int cg = open("/sys/fs/cgroup/build.slice/job.scope", O_DIRECTORY | O_RDONLY);
posix_spawnattr_setcgroup_np(&at, cg);
posix_spawnattr_setflags(&at, POSIX_SPAWN_SETCGROUP);

/* Дістати не номер, а дескриптор процесу. */
int pidfd;
char *argv[] = { "sleep", "10", NULL };
int rc = pidfd_spawnp(&pidfd, "sleep", NULL, NULL, argv, environ);
if (rc == 0) {
    siginfo_t info;
    waitid(P_PIDFD, pidfd, &info, WEXITED);
    close(pidfd);
}
```

| що | підпис | версія |
|---|---|---|
| `posix_spawnattr_setcgroup_np` | `int (posix_spawnattr_t *at, int cgroup)` — `cgroup` це дескриптор теки cgroup v2 | glibc 2.39; потребує ядра з `clone3` |
| `posix_spawnattr_getcgroup_np` | `int (const posix_spawnattr_t *restrict at, int *restrict cgroup)` | glibc 2.39 |
| `pidfd_spawn` | як `posix_spawn`, але перший аргумент — `int *pidfd` | glibc 2.39; потребує `CLONE_PIDFD` (ядро 5.2) |
| `pidfd_spawnp` | те саме з пошуком у `PATH` | glibc 2.39 |

Вигода `SETCGROUP` — не зручність, а закритий проміжок: без нього дитина спершу народжується в групі батька й певний час виконується **до** того, як на неї накладуть обмеження ([cgroups](book:unix-linux/cgroups) — облік і межі ресурсів для дерева процесів, а не для одного). Вигода `pidfd_spawn` така сама, тільки з іншого боку: дескриптор процесу не плутається з повторно виданим номером, тож сигнал і очікування завжди стосуються саме тієї дитини, яку ви запустили ([PID і дерево процесів](book:unix-linux/pid-and-hierarchy) — чому номер процесу не є надійним посиланням).

## Що з цього де є

Розбіжності між бібліотеками стосуються лише розширень; базовий набір з редакції 2001 року є всюди, де є `<spawn.h>`.

| реалізація | що є понад базовий набір |
|---|---|
| glibc | усе перелічене вище, з версіями з таблиць |
| musl | `POSIX_SPAWN_SETSID`, `POSIX_SPAWN_USEVFORK`, `addchdir_np`, `addfchdir_np`; `addclosefrom_np`, `addtcsetpgrp_np`, cgroup і `pidfd_spawn` — немає |
| FreeBSD | `addchdir_np`, `addfchdir_np` |
| Solaris, illumos | `addclosefrom_np` — саме звідти його й перенесли в glibc |
| Darwin (macOS) | `posix_spawn` — **справжній системний виклик**, документований у другому розділі довідника, а не бібліотечна обгортка |

Практичне правило: усе з суфіксом `_np` перевіряють під час збірки, а не сподіваються. Імена без `_np` — `posix_spawn_file_actions_addchdir` і `addfchdir` — стандарт узаконив лише 2024 року ([POSIX](book:unix-linux/posix-standard) — що саме зафіксовано стандартом і як читати номери його редакцій), тож на них поки покладаються ще менше, ніж на `_np`-варіанти, і переносний код бере `_np`.

Розбіжність між Linux і Darwin глибша, ніж перелік функцій: там, де glibc виконує список дій кодом бібліотеки в клонованій задачі, ядро Darwin виконує його само, всередині системного виклику. Наслідок для того, хто читає код: на macOS між `posix_spawn` і `execve` немає жодного проміжного шару, який можна було б простежити з простору користувача.
