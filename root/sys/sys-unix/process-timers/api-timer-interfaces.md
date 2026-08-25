# 📋 Виклики, структури й помилки чотирьох таймерних інтерфейсів

Це повний контракт усіх чотирьох способів попросити ядро про строк — `alarm`, `setitimer`, POSIX-таймери й `timerfd`: сигнатури, поля структур, перелік годинників, прапорці, коди помилок і поведінка при `fork` та `execve`. Довідка потрібна тому, що спільного між цими інтерфейсами майже немає: різні заголовки, різні структури часу, різні одиниці, різні набори помилок — знання про один про сусідній не каже нічого, а перенести код з одного на інший означає переписати кожен рядок. Значення звірені з man7.org для Linux; де поведінка є розширенням Linux, а не вимогою POSIX, це позначено окремо.

## Орієнтир

Рядок таблиці означає однаковий **намір**, а не однакову семантику: `alarm(0)` і `timer_delete` стоять близько лише тому, що обидва «прибирають таймер» — насправді перший роззброює єдиний вічний таймер процесу, а другий знищує створений вами об'єкт.

| Намір | `alarm` | `setitimer` | POSIX-таймери | `timerfd` |
|---|---|---|---|---|
| створити об'єкт | — (він є завжди) | — (три готові) | `timer_create` | `timerfd_create` |
| озброїти | `alarm(n)` | `setitimer` | `timer_settime` | `timerfd_settime` |
| роззброїти | `alarm(0)` | `setitimer` з нулями | `timer_settime` з нулями | `timerfd_settime` з нулями |
| спитати залишок | значення, яке віддав `alarm` | `getitimer` | `timer_gettime` | `timerfd_gettime` |
| знищити | — | — | `timer_delete` | `close` |
| дізнатися про пропущені | ніяк | ніяк | `timer_getoverrun` | число, яке віддав `read` |
| сповіщення | `SIGALRM` | `SIGALRM`, `SIGVTALRM`, `SIGPROF` | сигнал, потік або нічого | готовність дескриптора |
| одиниця в структурі | секунда | мікросекунда | наносекунда | наносекунда |
| скільки на процес | один | по одному на кожен вид | скільки завгодно | скільки завгодно |
| вибір годинника | немає | зашитий у вид таймера | аргумент `timer_create` | аргумент `timerfd_create` |
| заголовок | `<unistd.h>` | `<sys/time.h>` | `<signal.h>`, `<time.h>` | `<sys/timerfd.h>` |
| збирання | нічого | нічого | `-lrt` | нічого |
| доступний від | завжди | завжди | Linux 2.6 | ядро 2.6.25, glibc 2.8 |

`-lrt` потрібен для `timer_*` у glibc **до 2.34**; від 2.34 символи `librt` перенесено в саму `libc`, а порожній стаб бібліотеки лишили, щоб не ламати старі рядки збирання. Заразом варто знати, що `timer_t`, який ви тримаєте, — не той ідентифікатор, яким таймер зветься в ядрі: відповідність між ними веде glibc ([libc як шлюз](topic:sys-unix/libc-as-gateway) — імена системних викликів програмі дає бібліотека C, і між її обгорткою та справжнім входом у ядро часто лежить власна робота бібліотеки).

## alarm

```c
#include <unistd.h>

unsigned int alarm(unsigned int seconds);
```

Повертає, скільки секунд лишалося попередньому будильнику, або `0`, якщо його не було. **Помилок не має взагалі** — переліку `errno` в цього виклику просто немає, як і способу дізнатися, що щось пішло не так. `alarm(0)` скасовує чинний строк і віддає його залишок.

У Linux `alarm` і `setitimer(ITIMER_REAL, …)` — це **той самий таймер** під двома іменами: виклик одного затирає стан іншого. З тієї ж причини погана ідея мішати `alarm` зі `sleep(3)` там, де `sleep` реалізовано через `SIGALRM`.

## getitimer і setitimer

```c
#include <sys/time.h>

int getitimer(int which, struct itimerval *curr_value);
int setitimer(int which, const struct itimerval *restrict new_value,
                               struct itimerval *restrict old_value);

struct itimerval {
    struct timeval it_interval;  /* період переозброєння; нулі — одноразовий */
    struct timeval it_value;     /* до першого спрацювання; нулі — роззброїти */
};

struct timeval {
    time_t      tv_sec;          /* секунди */
    suseconds_t tv_usec;         /* мікросекунди, 0…999999 */
};
```

| `which` | Що рахує | Сигнал |
|---|---|---|
| `ITIMER_REAL` | справжній час на стіні | `SIGALRM` |
| `ITIMER_VIRTUAL` | час процесу в коді користувача | `SIGVTALRM` |
| `ITIMER_PROF` | час процесу в коді користувача **плюс** час ядра на його виклики | `SIGPROF` |

`old_value` можна передати як `NULL`. Пропущені спрацювання тут не рахуються ніяк: кожного з цих сигналів у процесі може чекати доправлення щонайбільше один примірник, тож усі зайві зливаються з ним безслідно. Історично строк упирався в стелю близько 99.42 доби, бо зберігався в тиках; від Linux 2.6.16 цієї межі немає. У POSIX.1-2008 обидва виклики позначено застарілими на користь `timer_*`.

## POSIX-таймери

```c
#include <signal.h>
#include <time.h>

int timer_create(clockid_t clockid, struct sigevent *restrict sevp,
                 timer_t *restrict timerid);
int timer_settime(timer_t timerid, int flags,
                  const struct itimerspec *restrict new_value,
                        struct itimerspec *restrict old_value);
int timer_gettime(timer_t timerid, struct itimerspec *curr_value);
int timer_getoverrun(timer_t timerid);
int timer_delete(timer_t timerid);

struct itimerspec {
    struct timespec it_interval;  /* період */
    struct timespec it_value;     /* до першого спрацювання */
};

struct timespec {
    time_t tv_sec;                /* секунди */
    long   tv_nsec;               /* наносекунди, 0…999999999 */
};
```

`flags` у `timer_settime` — або `0` (в `it_value` лежить тривалість «через скільки»), або `TIMER_ABSTIME` (в `it_value` лежить абсолютна мить на годиннику цього таймера). На 32-бітних системах `tv_sec` — це `time_t`, тож абсолютні строки далеко в майбутньому впираються в те саме, у що впирається весь календарний час ([подання часу й 2038 рік](topic:sys-unix/time-representation-y2038) — чому 32-бітний лічильник секунд закінчується і як системи переходять на 64-бітний).

### Як описують сповіщення

```c
struct sigevent {
    int             sigev_notify;               /* SIGEV_* — спосіб сповістити */
    int             sigev_signo;                /* номер сигналу */
    union sigval    sigev_value;                /* прийде в si_value чи в аргументі функції */
    void          (*sigev_notify_function)(union sigval);
    pthread_attr_t *sigev_notify_attributes;
    pid_t           sigev_notify_thread_id;     /* лише Linux */
};

union sigval {
    int   sival_int;
    void *sival_ptr;
};
```

| `sigev_notify` | Що робить система |
|---|---|
| `SIGEV_NONE` | не сповіщає нічим; строк питають самі через `timer_gettime` |
| `SIGEV_SIGNAL` | шле `sigev_signo` **процесові**; у `siginfo_t` приходять `si_code == SI_TIMER`, `si_value` і `si_overrun` |
| `SIGEV_THREAD` | викликає `sigev_notify_function` «наче стартову функцію нового потоку»; у glibc це робить не ядро, а допоміжний потік бібліотеки з зарезервованим реальночасовим сигналом |
| `SIGEV_THREAD_ID` | (Linux) шле сигнал **конкретному потоку**, чий номер з `gettid(2)` лежить у `sigev_notify_thread_id` |

`sevp == NULL` рівносильне `SIGEV_SIGNAL` із `sigev_signo = SIGALRM` і `sival_int`, що дорівнює ідентифікаторові таймера.

Одна пастка на збиранні: ім'я `sigev_notify_thread_id` документоване, але заголовки glibc його не оголошують — у коді пишуть внутрішнє `sev._sigev_un._tid` (у musl макрос з документованим іменем є). Обгортка `gettid()` з'явилася в glibc 2.30; раніше писали `syscall(SYS_gettid)`.

```c
struct sigevent sev = {0};
sev.sigev_notify = SIGEV_THREAD_ID;
sev.sigev_signo  = SIGRTMIN;             /* реальночасовий: такі стають у чергу */
sev.sigev_value.sival_ptr = ctx;
sev._sigev_un._tid = gettid();           /* публічного імені поля в glibc немає */
```

Реальночасовий номер тут не випадковий: лише такі сигнали накопичуються чергою й переносять значення ([реальночасові сигнали](topic:sys-unix/realtime-signals) — сигнали від `SIGRTMIN` до `SIGRTMAX`, які не злипаються, стають у чергу й несуть `sigval`).

### Пропущені спрацювання

У черзі на **один** таймер стоїть щонайбільше один сигнал, тож усі спрацювання, що трапилися між породженням сигналу й моментом, коли процес його прийняв, стають «перевищеннями». `timer_getoverrun(timerid)` віддає їхнє число, тобто `0` означає «нічого не пропущено», а `3` — «крім цього спрацювання було ще три». Значення дійсне для щойно прийнятого сповіщення й скидається з доправленням наступного; те саме число видно в `si_overrun` обробника з `SA_SIGINFO` (Linux). Стеля — `DELAYTIMER_MAX`, у Linux це `INT_MAX`; від Linux 4.19 більші значення справді зрізаються до неї. У `siginfo_t` є ще `si_timerid`, але це внутрішній ідентифікатор ядра, не той `timer_t`, що у вас на руках.

## Годинники

Один і той самий `clockid_t` не всюди приймають: набір `timer_create` ширший.

| `clockid` | `timer_create` | `timerfd_create` | Що це |
|---|---|---|---|
| `CLOCK_REALTIME` | так | так | календарний час; стрибає від `clock_settime` і NTP |
| `CLOCK_MONOTONIC` | так | так | тече рівно від довільної точки, ніколи не стрибає; час у сні системи не рахує |
| `CLOCK_BOOTTIME` | від 2.6.39 | від 3.15 | як монотонний, але **зараховує** час, проведений машиною в сні |
| `CLOCK_REALTIME_ALARM` | від 3.0 | від 3.11 | календарний і має право **розбудити** приспану систему; треба `CAP_WAKE_ALARM` |
| `CLOCK_BOOTTIME_ALARM` | від 3.0 | від 3.11 | те саме, але на шкалі `BOOTTIME`; треба `CAP_WAKE_ALARM` |
| `CLOCK_TAI` | від 3.10 | `EINVAL` | атомна шкала без високосних секунд |
| `CLOCK_PROCESS_CPUTIME_ID` | від 2.6.12 | `EINVAL` | процесорний час усього процесу |
| `CLOCK_THREAD_CPUTIME_ID` | від 2.6.12 | `EINVAL` | процесорний час потоку, що створює таймер |
| з `clock_getcpuclockid`, `pthread_getcpuclockid` | так | `EINVAL` | процесорний час **чужого** процесу чи потоку |

Два `*_ALARM`-годинники — єдині в цьому переліку, що витрачають заряд: вони не дають системі спати до свого строку, тому й закриті окремим дозволом ([можливості процесу](topic:sys-unix/capabilities) — розщеплення всесилля root на незалежні дозволи, кожен з яких видається окремо; `CAP_WAKE_ALARM` — саме право будити систему).

## Одна структура — три стани

`itimerspec` описує всі три режими роботи таймера, і різниця між ними — не в різних викликах, а в заповненні полів. Правило однакове для `timer_settime` і `timerfd_settime`.

| `it_value` | `it_interval` | Що робить ядро |
|---|---|---|
| нулі | будь-що | роззброїти таймер |
| ненульове | нулі | одне спрацювання й тиша |
| ненульове | ненульове | перше спрацювання за `it_value`, далі кожні `it_interval` |

`timer_gettime` і `timerfd_gettime` віддають `it_value` **завжди як залишок часу**, навіть якщо озброювали абсолютною міттю; нульовий `it_value` у відповіді означає, що таймер роззброєний.

## timerfd

```c
#include <sys/timerfd.h>

int timerfd_create(int clockid, int flags);
int timerfd_settime(int fd, int flags,
                    const struct itimerspec *new_value,
                          struct itimerspec *old_value);
int timerfd_gettime(int fd, struct itimerspec *curr_value);
```

| Прапорець | Де | Дія |
|---|---|---|
| `TFD_CLOEXEC` | `timerfd_create` | закрити дескриптор при `execve` |
| `TFD_NONBLOCK` | `timerfd_create` | `read` не спатиме, а поверне `EAGAIN` |
| `TFD_TIMER_ABSTIME` | `timerfd_settime` | в `it_value` лежить абсолютна мить, а не тривалість |
| `TFD_TIMER_CANCEL_ON_SET` | `timerfd_settime` | (від 2.6.30) позначити таймер скасовним при стрибку календарного годинника; лише разом із `TFD_TIMER_ABSTIME` і лише для `CLOCK_REALTIME` чи `CLOCK_REALTIME_ALARM` |

Обидва прапорці створення з'явилися в Linux 2.6.27; у ядрах 2.6.26 і давніших `flags` мусив бути нулем.

Читання має жорсткий контракт. Буфер — рівно `uint64_t`, тобто вісім байтів у порядку байтів машини; менший буфер дає `EINVAL`. Успішний `read` повертає `8`, а в буфер кладе, **скільки спрацювань набігло** від минулого успішного читання або від останнього озброєння, і заразом обнуляє цей лічильник. Якщо спрацювань ще не було, `read` спить (або віддає `EAGAIN` при `O_NONBLOCK`). Дескриптор стає читабельним для `select`, `poll` і `epoll` рівно тоді, коли лічильник ненульовий ([select, poll, epoll](topic:sys-unix/select-poll-epoll) — як один потік чекає на багатьох джерелах відразу й прокидається від будь-якого готового).

Перший `read` після того, як календарний годинник переставили під озброєним таймером із `TFD_TIMER_CANCEL_ON_SET`, падає з `ECANCELED` — це не збій, а сповіщення «перерахуй абсолютний строк і озброй наново». Тим самим кодом може відповісти й `timerfd_settime`.

Є ще `ioctl(fd, TFD_IOC_SET_TICKS, &count)` (від Linux 3.17, за `CONFIG_CHECKPOINT_RESTORE`) — він виставляє лічильник спрацювань примусово; потрібен тим, хто відновлює процес зі знімка, а не звичайному коду.

## fork і execve

Тут інтерфейси розходяться найдужче, і причина структурна: перші три належать **процесові**, а `timerfd` — описові відкритого файлу.

| Інтерфейс | При `fork` | При `execve` |
|---|---|---|
| `alarm`, `setitimer` | дитина **не** успадковує: її таймери порожні | зберігаються й тікають далі |
| POSIX-таймери | дитина **не** успадковує | роззброюються та знищуються |
| `timerfd` | дитина дістає копію дескриптора на **той самий** таймер; лічильник спрацювань спільний, і прочитає його той, хто встиг перший | зберігається й тікає далі, якщо немає `TFD_CLOEXEC` |

Спільний лічильник у дитини й батька — прямий наслідок того, що `fork` копіює дескриптор, а не об'єкт за ним ([опис відкритого файлу](topic:sys-unix/open-file-description) — сутність між дескриптором і файлом, яку копії дескриптора ділять на всіх).

## Помилки

| Код | Виклики | Коли |
|---|---|---|
| `EINVAL` | усі, крім `alarm` | недійсний `which`, `clockid`, `timerid` чи `fd`; `tv_usec` поза 0…999999 або `tv_nsec` поза 0…999999999; від'ємні поля часу; недійсний `flags`; недійсні `sigev_notify` чи `sigev_signo`; потік із `sigev_notify_thread_id` не з цього процесу |
| `EINVAL` | `read` з `timerfd` | буфер коротший за вісім байтів |
| `EAGAIN` | `timer_create` | ядро тимчасово не змогло виділити структури під таймер |
| `EAGAIN` | `read` з `timerfd` | дескриптор неблокуючий, а спрацювань ще не було |
| `ECANCELED` | `read`, `timerfd_settime` | календарний годинник стрибнув під таймером із `TFD_TIMER_CANCEL_ON_SET` |
| `EFAULT` | усі, що беруть покажчики | структура лежить поза доступною пам'яттю |
| `EPERM` | `timer_create`, `timerfd_create` | просили `CLOCK_REALTIME_ALARM` чи `CLOCK_BOOTTIME_ALARM` без `CAP_WAKE_ALARM` |
| `EBADF` | `timerfd_settime`, `timerfd_gettime` | `fd` не є дійсним дескриптором |
| `ENOTSUP` | `timer_create` | ядро не вміє робити таймери на цьому годиннику |
| `ENOMEM` | `timer_create`, `timerfd_create` | бракує пам'яті ядра |
| `EMFILE`, `ENFILE` | `timerfd_create` | уперлися в межу дескрипторів процесу або в системну межу відкритих файлів |
| `ENODEV` | `timerfd_create` | ядру не вдалося змонтувати свій внутрішній пристрій анонімних inode |

`EMFILE` — нагадування, що таймер тут витрачає той самий ресурс, що й відкритий файл, і рахується в `RLIMIT_NOFILE` ([обмеження ресурсів](topic:sys-unix/resource-limits) — м'які й тверді ліміти процесу, які показує `ulimit` і читає `getrlimit`).

## Мінімальний робочий виклик

Повна програма: перший строк через секунду, далі чотири рази на секунду, вісім спрацювань — і вихід.

```c
/* cc -o tick tick.c   (для POSIX-таймерів у glibc до 2.34 знадобився б ще -lrt) */
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>
#include <sys/timerfd.h>

int main(void)
{
    int fd = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC);
    if (fd < 0) { perror("timerfd_create"); return 1; }

    struct itimerspec its = {
        .it_value    = { .tv_sec = 1, .tv_nsec = 0 },          /* перший строк */
        .it_interval = { .tv_sec = 0, .tv_nsec = 250000000 },  /* далі щочверть секунди */
    };
    if (timerfd_settime(fd, 0, &its, NULL) < 0) { perror("timerfd_settime"); return 1; }

    for (int i = 0; i < 8; i++) {
        uint64_t ticks;
        if (read(fd, &ticks, sizeof ticks) != (ssize_t)sizeof ticks) {
            perror("read");                       /* тут же ловиться ECANCELED */
            return 1;
        }
        printf("спрацювань від минулого читання: %llu\n", (unsigned long long)ticks);
    }
    close(fd);
    return 0;
}
```
