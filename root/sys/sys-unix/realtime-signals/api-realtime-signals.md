# 📋 Контракт реальночасових сигналів: підписи, `siginfo_t` за кодами, `sigevent` і помилки

Це довідка на робочий стіл: точні підписи всіх викликів родини, розкладка `siginfo_t` для кожного `si_code` (тобто яким полям взагалі можна вірити), заповнення `struct sigevent`, чому `SIGRTMIN` не пишуть числом і за якої саме умови повертається кожен код помилки.

## Виклики родини

```c
#define _POSIX_C_SOURCE 199309L   /* мінімум для всієї родини */
#include <signal.h>

union sigval {
    int   sival_int;
    void *sival_ptr;
};

int sigqueue(pid_t pid, int sig, const union sigval value);

int sigwaitinfo(const sigset_t *restrict set,
                siginfo_t *restrict info);
int sigtimedwait(const sigset_t *restrict set,
                 siginfo_t *restrict info,
                 const struct timespec *restrict timeout);
int sigwait(const sigset_t *restrict set, int *restrict sig);
```

| Виклик | Успіх | Невдача | Що робить |
|---|---|---|---|
| `sigqueue()` | `0` | `-1`, код в `errno` | кладе в чергу процесу запис із позначкою `SI_QUEUE` і вантажем |
| `sigwaitinfo()` | **номер сигналу** (> 0) | `-1`, код в `errno` | забирає найперший придатний запис, чекає без межі |
| `sigtimedwait()` | номер сигналу (> 0) | `-1`, код в `errno` | те саме, але з межею очікування |
| `sigwait()` | **`0`** | **додатний номер помилки** | те саме, що `sigwaitinfo()`, тільки без `siginfo_t` |

`sigwait()` вибивається з ряду двічі, і на цьому регулярно спотикаються: він повертає не номер сигналу, а нуль (номер кладе за вказівником `sig`), і **не чіпає `errno`** — код помилки їде поверненим значенням. Перевірка `if (sigwait(…) == -1)` не спрацює ніколи.

Другий підводний камінь — `const` перед `timeout`. Ядро не переписує залишок часу назад у структуру, тож після повернення з `EINTR` різницю доводиться рахувати самому, звіряючись із монотонним годинником ([`EINTR` і перезапуск](root:sys-unix/eintr-and-restart) — які виклики ядро переграє саме, а які завжди віддають помилку). Нульовий `timeout` (`{0, 0}`) перетворює виклик на опитування без чекання.

Під бібліотечними обгортками лежать системні виклики, у двох із яких обгорток немає взагалі:

```c
#include <sys/syscall.h>
#include <unistd.h>

/* обгорток у glibc немає — лише через syscall(2) */
long syscall(SYS_rt_sigqueueinfo,   pid_t tgid,            int sig, siginfo_t *info);
long syscall(SYS_rt_tgsigqueueinfo, pid_t tgid, pid_t tid, int sig, siginfo_t *info);

/* під sigwaitinfo() і sigtimedwait(): timeout == NULL означає «без межі» */
long syscall(SYS_rt_sigtimedwait, const sigset_t *set, siginfo_t *info,
             const struct timespec *timeout, size_t sigsetsize);
```

Різниця між `sigqueue()` і `rt_sigqueueinfo` — у тому, хто складає запис. Обгортка обнуляє `siginfo_t` і заповнює його сама (`si_signo`, `si_code = SI_QUEUE`, `si_pid`, `si_uid`, `si_value`); сирий виклик віддає складання вам — саме тому ядро й перевіряє, що ви туди поклали. `rt_tgsigqueueinfo` (від Linux 2.6.31) додає другий номер і цілиться в конкретну задачу, а не в групу потоків ([задача як одиниця планування](root:sys-unix/threads-as-tasks) — чому в процесу є `tgid` і `tid` та чим адресування потокові відрізняється від адресування процесові).

Аргумент `sigsetsize` — розмір **ядрового** набору сигналів, а не бібліотечного. У ядрі це 8 байтів — рівно 64 біти, по одному на кожен номер (`_NSIG` = 64), — а в glibc `sizeof(sigset_t)` дорівнює 128. Підставите друге замість першого — дістанете `EINVAL` і довго шукатимете причину.

## `SIGRTMIN` і `SIGRTMAX` — виклики функцій, а не сталі

```c
/* glibc, <signal.h> */
extern int __libc_current_sigrtmin(void);
extern int __libc_current_sigrtmax(void);

#define SIGRTMIN  (__libc_current_sigrtmin())
#define SIGRTMAX  (__libc_current_sigrtmax())
```

| Величина | Значення | Хто визначає |
|---|---|---|
| ядровий діапазон | 32…64 (`_NSIG` = 64) | стала ядра, у програму не потрапляє |
| 32 — `SIGCANCEL` | скасування потоку (`pthread_cancel`) | реалізація потоків NPTL у glibc |
| 33 — `SIGSETXID` | узгоджена зміна `uid`/`gid` в усіх потоках | NPTL |
| `SIGRTMIN` за NPTL | 34 | обчислює бібліотека при старті |
| `SIGRTMIN` за LinuxThreads | 35 | давня реалізація займала три номери |
| `SIGRTMAX` | 64 | |
| гарантія POSIX | щонайменше 8 номерів (`_POSIX_RTSIG_MAX`) | стандарт |

Бібліотеці ці номери потрібні не про запас. `SIGEV_THREAD` для POSIX-таймерів реалізовано **всередині glibc**, а не в ядрі: бібліотека переписує ваш запит на `SIGEV_THREAD_ID` із власним службовим реальночасовим номером і будить на ньому свій допоміжний потік, який уже кличе вашу функцію.

Наслідок для коду прямий: значення обчислюється під час виконання, тому його **не можна вживати там, де компілятор вимагає сталу** — ні як мітку `case`, ні як розмір масиву, ні в `#if`, ні в ініціалізаторі статичної змінної. Придатних номерів рахують теж під час виконання: `SIGRTMAX - SIGRTMIN + 1`.

> 🔧 **Навіщо це.** Написане числом `32` компілюється й навіть надсилається: `sigqueue()` службові номери не відсіює й передає їх ядру як є. А от `sigaction()` і `sigaddset()` у glibc на 32 і 33 повертають `EINVAL`, бо бібліотека боронить свою кухню. Виходить дорога в один бік: сигнал полетів, перехопити його неможливо, і замість вашої події адресат дістає скасування потоку.

## Розкладка `siginfo_t` за `si_code`

У справжньому оголошенні `siginfo_t` — об'єднання кількох наборів полів. Значущі лише ті, що відповідають конкретному `si_code`; решта містить довільні байти. Тому розбір **завжди** починають із `si_code`, а вже потім читають поля.

| `si_code` | № | Хто заповнив запис | Значущі поля понад `si_signo` |
|---|---|---|---|
| `SI_USER` | 0 | `kill(2)` | `si_pid`, `si_uid`; **`si_value` не заповнено** |
| `SI_KERNEL` | 0x80 | породило саме ядро | залежить від сигналу; на реальночасових номерах не трапляється |
| `SI_QUEUE` | −1 | `sigqueue(3)`, `rt_sigqueueinfo` | `si_pid`, `si_uid`, `si_value` |
| `SI_TIMER` | −2 | доспів POSIX-таймер | `si_value` (з `sigev_value`), `si_overrun`, `si_timerid` |
| `SI_MESGQ` | −3 | `mq_notify(3)` | `si_value` (з `sigev_value`), `si_pid`, `si_uid` — того, хто **написав** повідомлення |
| `SI_ASYNCIO` | −4 | завершилася операція `aio_*` | `si_value` (з `aio_sigevent.sigev_value`) |
| `SI_SIGIO` | −5 | історичний: давня черга `SIGIO`; сучасні ядра його не ставлять | `si_band`, `si_fd` |
| `SI_TKILL` | −6 | `tkill(2)`, `tgkill(2)`, `pthread_kill(3)` — і `raise(3)`, бо glibc робить її через `pthread_kill` | `si_pid`, `si_uid` |
| `POLL_IN`…`POLL_HUP` | 1…6 | готовність дескриптора через `F_SETSIG` | `si_band`, `si_fd` |

Знак коду — це критерій довіри, і в ядрі він оформлений двома макросами: `SI_FROMUSER(si)` — це `si->si_code <= 0`, `SI_FROMKERNEL(si)` — `si->si_code > 0`. Рідше трапляються `SI_ASYNCNL` (−60, завершено асинхронний пошук імені в glibc) і `SI_DETHREAD` (−7, `execve()` убиває решту потоків групи).

Дві пастки в цій таблиці варті окремого слова. `si_timerid` — **внутрішній номер ядра**, а не ваш `timer_t`; щоб упізнати свій таймер, кладуть мітку в `sigev_value` і читають її з `si_value` ([таймери процесу](root:sys-unix/process-timers) — як `timer_create` заводить лічильник і що означає пропущене спрацювання). А готовність дескриптора сучасні ядра позначають кодами `POLL_*`, а не `SI_SIGIO`: той код лишився від давнішого механізму, де готовність приносив сам `SIGIO` без розбору причини, і нині не виставляється ([ввід-вивід за сигналом](root:sys-unix/signal-driven-io) — як `F_SETOWN` і `F_SETSIG` перетворюють готовність дескриптора на сигнал із номером цього дескриптора).

## `struct sigevent`: як ядро дізнається, куди слати

```c
struct sigevent {
    int              sigev_notify;              /* спосіб сповіщення */
    int              sigev_signo;               /* номер сигналу     */
    union sigval     sigev_value;               /* вантаж            */
    void           (*sigev_notify_function)(union sigval);
    pthread_attr_t  *sigev_notify_attributes;
    pid_t            sigev_notify_thread_id;    /* лише Linux */
};
```

| `sigev_notify` | Що станеться | Які поля читають |
|---|---|---|
| `SIGEV_NONE` | нічого; стан доведеться опитувати самому | жодних |
| `SIGEV_SIGNAL` | сигнал процесові як цілому | `sigev_signo`, `sigev_value` |
| `SIGEV_THREAD` | бібліотека кличе функцію, «наче» це початок нового потоку | `sigev_notify_function`, `sigev_value`, необов'язково `sigev_notify_attributes` |
| `SIGEV_THREAD_ID` | сигнал **конкретній задачі**; лише для POSIX-таймерів | `sigev_signo`, `sigev_value`, `sigev_notify_thread_id` |

Структуру заповнюють після `memset()`: три останні поля в glibc лежать в одному об'єднанні — `sigev_notify_thread_id` ділить місце з парою `sigev_notify_function`/`sigev_notify_attributes`, тож заповнюють рівно ті, що відповідають обраному `sigev_notify`, а решту лишають обнуленою. Приймає `sigevent` не один інтерфейс: `timer_create(2)` бере його другим аргументом, `mq_notify(3)` — теж ([черги повідомлень](root:sys-unix/message-queues) — як процес підписується на появу першого повідомлення в порожній черзі), а `aio_read`/`aio_write` носять його полем `aio_sigevent` усередині `struct aiocb` ([POSIX AIO](root:sys-unix/posix-aio) — асинхронне читання й запис, зроблене в glibc потоками простору користувача).

## Помилки: за яких саме умов

| Виклик | Код | Умова |
|---|---|---|
| `sigqueue` | `EAGAIN` | вичерпано `RLIMIT_SIGPENDING` реального власника (рахунок спільний на всі його процеси) або ядро не змогло виділити запис під тиском на пам'ять |
| `sigqueue` | `EINVAL` | `sig` — не дійсний номер сигналу |
| `sigqueue` | `EPERM` | немає права слати сигнал цьому процесові |
| `sigqueue` | `ESRCH` | процесу з таким `pid` не існує |
| `rt_sigqueueinfo` | `EPERM` | ціль — не свій процес, а `info->si_code` заборонений: будь-яке значення ≥ 0 (тобто `SI_USER` і `SI_KERNEL`), а від Linux 2.6.39 ще й `SI_TKILL` |
| `rt_tgsigqueueinfo` | `EINVAL` | недійсний `sig`, `tgid` або `tid` |
| `rt_tgsigqueueinfo` | `ESRCH` | у групі `tgid` немає потоку `tid` |
| `sigtimedwait` | `EAGAIN` | вийшов час, а жоден сигнал із `set` не став очікуваним |
| `sigtimedwait`, `sigwaitinfo` | `EINTR` | очікування урвав обробник сигналу, якого в `set` **немає** |
| `sigtimedwait` | `EINVAL` | `timeout` недійсний: `tv_nsec` поза 0…999999999 або від'ємні секунди |
| `rt_sigtimedwait` | `EINVAL` | `sigsetsize` не дорівнює розмірові ядрового `sigset_t` |
| `sigwait` | `EINVAL` | у `set` недійсний номер сигналу (код повертається, а не кладеться в `errno`) |

Квота, за яку відповідає `EAGAIN`, — межа `RLIMIT_SIGPENDING`; вона рахується на **реального власника**, а не на процес, і бачити її можна командою `ulimit -i` ([ліміти ресурсів](root:sys-unix/resource-limits) — м'які й жорсткі межі `RLIMIT_*` та хто має право їх піднімати). POSIX гарантує процесові щонайменше `_POSIX_SIGQUEUE_MAX` = 32 записи; Linux дає порядку десятків тисяч на користувача. Перевіряє межу ядро лише для записів із **від'ємним** `si_code` — тобто саме для `sigqueue()`; `kill()` із позначкою `SI_USER` (число 0) її обходить, тому вбити процес удається й тоді, коли квоту вичерпано.

Правило `EPERM` для `sigqueue()` — те саме, що для `kill()`: збіг ідентифікаторів або `CAP_KILL` у просторі імен адресата ([як надсилають сигнали](root:sys-unix/signal-model/api-sending-signals.md) — повна перевірка права й чому `EPERM` для групи означає «нікому»).

Три випадки виглядають як помилка, а нею не є. Перший: якщо адресат **ігнорує** цей номер і не заблокував його, ядро відкидає запис ще до черги — `sigqueue()` поверне `0`, а квота не витратиться. Другий: `sigaction()` із `SIG_IGN` викидає вже накопичені записи цього номера, тому «ігнорувати на хвилинку» означає втратити все, що встигло приїхати. Третій: `SIGKILL` і `SIGSTOP` у наборі для `sigtimedwait()` ядро мовчки прибирає — помилки не буде, чекання на них просто не станеться ([маска сигналів і `signalfd`](root:sys-unix/signal-mask-signalfd) — які сигнали взагалі піддаються блокуванню й куди дівається заблоковане).

## Мінімальний робочий виклик

```c
#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <string.h>
#include <time.h>
#include <stdio.h>

/* Номер беруть під час виконання — і звіряють із верхньою межею. */
static int rt_slot(int n)
{
    int sig = SIGRTMIN + n;
    return sig <= SIGRTMAX ? sig : -1;
}

/* Таймер, який принесе назад власну мітку в si_value. */
static int arm_timer(timer_t *tid, int sig, void *tag)
{
    struct sigevent sev;

    memset(&sev, 0, sizeof sev);         /* три останні поля — в об'єднанні */
    sev.sigev_notify = SIGEV_SIGNAL;
    sev.sigev_signo  = sig;
    sev.sigev_value.sival_ptr = tag;     /* приїде в si_value */

    return timer_create(CLOCK_MONOTONIC, &sev, tid);
}

/* Розбір запису: які поля значущі, каже si_code — і тільки він. */
static void describe(const siginfo_t *si)
{
    switch (si->si_code) {          /* si_code — стала, на відміну від SIGRTMIN */
    case SI_QUEUE:
        printf("sigqueue: pid %d, uid %u, вантаж %d\n",
               (int)si->si_pid, (unsigned)si->si_uid, si->si_value.sival_int);
        break;
    case SI_TIMER:
        printf("таймер %p, пропущено %d спрацювань\n",
               si->si_value.sival_ptr, si->si_overrun);
        break;
    case SI_MESGQ:
        printf("черга повідомлень: писав pid %d\n", (int)si->si_pid);
        break;
    case SI_USER:
    case SI_TKILL:
        printf("kill або pthread_kill від pid %d — вантажу немає\n",
               (int)si->si_pid);
        break;
    default:
        printf("код %d: si_value не читаємо\n", si->si_code);
    }
}
```

Збирати з `-lrt` (від glibc 2.34 бібліотеку злито в libc, але прапорець лишається нешкідливим). Контраст у `switch` показовий: `SI_QUEUE` — звичайна стала препроцесора й міткою `case` бути може, `SIGRTMIN + 1` — виклик функції й не може.

Приймати ці записи обробником не обов'язково, а часто й не варто: із прапорцем `SA_SIGINFO` у `sigaction()` обробник дістає три аргументи замість одного, але виконується в довільній точці програми ([`struct sigaction` і прапорці `SA_*`](root:sys-unix/signal-disposition/api-sigaction.md) — повний склад структури, усі прапорці доставки й таблиця номерів із типовими діями). Без `SA_SIGINFO` вантаж просто нікуди подіти. Явне забирання через `sigwaitinfo()` чи `sigtimedwait()` цього прапорця не потребує зовсім — воно не викликає обробника, а віддає `siginfo_t` просто в змінну на стеку.
