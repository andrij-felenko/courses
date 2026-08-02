# ⚙️ Що насправді переживає exec: стенд і звітувач

Перелік уцілілого можна вивчити напам'ять, а можна поміряти на власній машині — і тоді правило «переживає те, на що можна послатися числом чи іменем; гине те, на що можна послатися лише адресою в старому образі» перестає бути формулюванням і стає спостереженням. Нижче — дві невеликі програми на C. **Стенд** виставляє перед заміною образу все, що взагалі можна виставити: два дескриптори з різними прапорцями, зсув усередині файлу, маску сигналів, відкладений сигнал, обробник і ігнорування, дві різні породи таймерів, `umask`, каталог, ліміт, `nice`, відображену сторінку пам'яті. Тоді він замінює себе **звітувачем**, який про стенд не знає нічого, крім кількох чисел, і чесно доповідає, що з усього цього дожило до першої його інструкції.

Майже все тут — чистий POSIX; лише дві перевірки, перелік дескрипторів і пошук адреси серед відображень, беруть дані з `/proc` і тому працюють тільки в Linux ([/proc: процеси як файли](book:unix-linux/proc-filesystem) — псевдофайлова система, де ядро показує стан кожного процесу звичайними файлами: `/proc/self/fd` — перелік відкритих дескрипторів, `/proc/self/maps` — перелік відображень пам'яті).

## Чому для цього потрібні двоє

Вимір має відбутися **після** заміни, інакше він нічого не доводить. Але після заміни в процесі виконується вже інша програма, і в неї немає жодного спогаду про «до»: її пам'ять збудовано з нуля, її змінні ніхто не заповнював. Програма не може поміряти саму себе крізь `exec` — після `exec` вона вже не вона.

Отже, потрібні двоє: той, хто виставляє, і той, хто дивиться. І потрібен канал, яким «до» дістанеться «після». Канал є, і він не хитрість: масиви аргументів та змінних оточення ядро копіює вбік ще перед точкою неповернення — саме тому, що стара пам'ять зникає. Тож усі еталонні значення — номери дескрипторів, ідентифікатор таймера, адреса відображеної сторінки, накопичений процесорний час — поїдуть у новий образ як текст ([argv, оточення й що успадковує дитина](book:unix-linux/argv-and-environment) — обидва масиви складає той, хто кличе `exec`, а не система, тож покласти в них можна що завгодно; звітувач дістане рівно сім змінних і жодної більше).

Що з чим порівнюємо:

| стенд виставляє | звітувач міряє | має вийти |
|---|---|---|
| `open()` без `FD_CLOEXEC`, зсув 10 | `lseek(fd, 0, SEEK_CUR)` | дескриптор живий, зсув 10 |
| `open(…, O_CLOEXEC)` | `fcntl(fd, F_GETFD)` | `EBADF` |
| `sigprocmask(SIG_BLOCK, {SIGUSR2})` | `sigprocmask(…, NULL, &set)` | заблоковано |
| `kill(getpid(), SIGUSR2)` під маскою | `sigpending()` | у черзі |
| обробник на `SIGUSR1` | `sigaction(SIGUSR1, NULL, &sa)` | `SIG_DFL` |
| `SIGTERM` → `SIG_IGN` | те саме | `SIG_IGN` |
| `alarm(300)` | `getitimer(ITIMER_REAL)` | лишилося ≈ 300 с |
| `timer_create` | `timer_gettime(id)` | `EINVAL` |
| `mmap` однієї сторінки | пошук адреси в `/proc/self/maps` | адреса нічия |
| `umask`, `chdir`, `setrlimit`, `setpriority` | `umask`, `getcwd`, `getrlimit`, `getpriority` | збігається |
| 0.15 с процесорного часу | `clock_gettime(CLOCK_PROCESS_CPUTIME_ID)` | не менше |
| `atexit()` | — | рядок не з'явиться |

Два рядки про таймери стоять поруч навмисно: різниця між ними — найгостріше місце всього досліду ([таймери процесу: alarm, setitimer, POSIX-таймери й timerfd](book:unix-linux/process-timers) — інтервальних таймерів у процесі рівно три, кожен названо сталою; POSIX-таймерів від `timer_create` може бути скільки завгодно, і кожен має ідентифікатор, виданий ядром тій програмі, яка його попросила).

## Стенд

```c
/* setup.c — виставляє все, що можна виставити, і передає естафету.
   Збірка: cc -O2 -Wall -Wextra -o setup setup.c
   Запуск: ./setup ./report                                          */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

static void farewell(void)        /* адреса цієї функції — у старому образі */
{
    fprintf(stderr, "[стенд] atexit пережив заміну — такого не буває\n");
}

static void on_usr1(int signo) { (void) signo; }

static double cpu_now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

static void burn(double seconds)  /* намолоти трохи процесорного часу */
{
    volatile unsigned long long acc = 0;
    double t0 = cpu_now();
    while (cpu_now() - t0 < seconds)
        for (int i = 0; i < 200000; i++)
            acc += i;
}

int main(int argc, char **argv)
{
    char rpath[PATH_MAX];
    struct sigaction sa;
    struct sigevent sev;
    struct itimerspec its;
    struct rlimit rl;
    sigset_t block;
    void *page;
    int keep, gone, ktimer = -1;
    char e_fd[64], e_cloexec[64], e_timer[64], e_addr[64],
         e_pid[64], e_cpu[64], e_nofile[64];
    char *envp[8];

    if (argc < 2) {
        fprintf(stderr, "як користуватися: %s ПРОГРАМА [аргументи]\n", argv[0]);
        return 2;
    }
    /* шлях резолвимо ДО chdir: після нього «./report» означатиме вже інше */
    if (realpath(argv[1], rpath) == NULL) { perror(argv[1]); return 2; }

    atexit(farewell);

    /* 1. Два дескриптори на той самий файл, з різними прапорцями */
    keep = open("/tmp/exec-probe.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (keep < 0) { perror("open"); return 1; }
    if (write(keep, "0123456789abcdefghijklmnopqrstuv", 32) != 32) {
        perror("write"); return 1;
    }
    lseek(keep, 10, SEEK_SET);            /* зсув, який має пережити заміну */
    gone = open("/tmp/exec-probe.dat", O_RDONLY | O_CLOEXEC);
    if (gone < 0) { perror("open O_CLOEXEC"); return 1; }

    /* 2. Прості властивості процесу */
    umask(0027);
    if (chdir("/tmp") != 0) { perror("chdir"); return 1; }
    getrlimit(RLIMIT_NOFILE, &rl);
    if (rl.rlim_cur > 512) { rl.rlim_cur = 512; setrlimit(RLIMIT_NOFILE, &rl); }
    if (setpriority(PRIO_PROCESS, 0, 5) != 0)
        fprintf(stderr, "[стенд] nice не виставився (%s) — звіт це покаже\n",
                strerror(errno));

    /* 3. Сигнали: обробник, ігнорування, маска, відкладений */
    memset(&sa, 0, sizeof sa);
    sigemptyset(&sa.sa_mask);
    sa.sa_handler = on_usr1;
    sigaction(SIGUSR1, &sa, NULL);        /* спіймано → буде скинуто */
    sa.sa_handler = SIG_IGN;
    sigaction(SIGTERM, &sa, NULL);        /* ігнорування → лишиться */

    sigemptyset(&block);
    sigaddset(&block, SIGUSR2);
    sigprocmask(SIG_BLOCK, &block, NULL); /* СПЕРШУ маска... */
    kill(getpid(), SIGUSR2);              /* ...а тоді сигнал самому собі */

    /* 4. Дві породи таймерів */
    alarm(300);                           /* інтервальний, він же ITIMER_REAL */

    memset(&sev, 0, sizeof sev);
    sev.sigev_notify = SIGEV_SIGNAL;
    sev.sigev_signo  = SIGUSR2;
    if (syscall(SYS_timer_create, CLOCK_MONOTONIC, &sev, &ktimer) != 0) {
        perror("timer_create"); return 1;
    }
    memset(&its, 0, sizeof its);
    its.it_value.tv_sec = 600;
    if (syscall(SYS_timer_settime, ktimer, 0, &its, NULL) != 0) {
        perror("timer_settime"); return 1;
    }

    /* 5. Сторінка пам'яті — те, на що можна послатися лише адресою */
    page = mmap(NULL, 4096, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (page == MAP_FAILED) { perror("mmap"); return 1; }
    strcpy((char *) page, "я жив у старому образі");

    burn(0.15);

    /* 6. Єдиний багаж, що переїде: рядки оточення */
    snprintf(e_fd,      sizeof e_fd,      "SURV_FD=%d", keep);
    snprintf(e_cloexec, sizeof e_cloexec, "SURV_FD_CLOEXEC=%d", gone);
    snprintf(e_timer,   sizeof e_timer,   "SURV_TIMER=%d", ktimer);
    snprintf(e_addr,    sizeof e_addr,    "SURV_ADDR=%p", page);
    snprintf(e_pid,     sizeof e_pid,     "SURV_PID=%ld", (long) getpid());
    snprintf(e_cpu,     sizeof e_cpu,     "SURV_CPU=%.3f", cpu_now());
    snprintf(e_nofile,  sizeof e_nofile,  "SURV_NOFILE=%llu",
             (unsigned long long) rl.rlim_cur);
    envp[0] = e_fd;  envp[1] = e_cloexec; envp[2] = e_timer;  envp[3] = e_addr;
    envp[4] = e_pid; envp[5] = e_cpu;     envp[6] = e_nofile; envp[7] = NULL;

    printf("[стенд] pid %ld: fd %d без CLOEXEC (зсув 10), fd %d з O_CLOEXEC,\n"
           "        SIGUSR2 заблоковано й надіслано собі, alarm(300),\n"
           "        POSIX-таймер #%d, сторінка на %p, намелено %.3f с\n\n",
           (long) getpid(), keep, gone, ktimer, page, cpu_now());

    fflush(NULL);        /* буфери stdio — теж пам'ять старого образу */
    execve(rpath, &argv[1], envp);
    perror("execve");
    _exit(127);
}
```

Стенд навмисно бере програму й аргументи з власного командного рядка й передає їх далі як є. Через це він годиться не лише для звітувача: тим самим стендом можна запустити будь-що й подивитися, у якому стані воно прокинеться.

## Звітувач

```c
/* report.c — новий образ: що з виставленого стендом дожило до цієї миті.
   Збірка: cc -O2 -Wall -Wextra -o report report.c                     */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

static int mismatch = 0;

static const char *want(const char *name)
{
    const char *v = getenv(name);
    if (v == NULL) {
        fprintf(stderr, "звітувача запускає стенд, а не оболонка: немає %s\n", name);
        exit(2);
    }
    return v;
}

/* present — чи є воно в новому образі; expected — чи мало бути */
static void check(int present, int expected, const char *what, const char *detail)
{
    if (present != expected) mismatch++;
    printf("  %c%c  %s%s%s\n", present ? '+' : '-',
           present == expected ? ' ' : '!',
           what, *detail ? " — " : "", detail);
}

static int addr_is_mapped(unsigned long long a)
{
    unsigned long long lo, hi;
    char row[512];
    int found = 0;
    FILE *f = fopen("/proc/self/maps", "r");
    if (f == NULL) return -1;
    while (fgets(row, sizeof row, f))
        if (sscanf(row, "%llx-%llx", &lo, &hi) == 2 && a >= lo && a < hi) {
            found = 1;
            break;
        }
    fclose(f);
    return found;
}

static void list_open_fds(void)
{
    struct dirent *e;
    DIR *d = opendir("/proc/self/fd");
    int self;
    if (d == NULL) { printf("     (/proc не змонтовано)\n"); return; }
    self = dirfd(d);          /* власний дескриптор каталогу до переліку не належить */
    while ((e = readdir(d)) != NULL) {
        char path[64], target[PATH_MAX];
        ssize_t n;
        int fd = atoi(e->d_name);
        if (e->d_name[0] == '.' || fd == self) continue;
        snprintf(path, sizeof path, "/proc/self/fd/%d", fd);
        n = readlink(path, target, sizeof target - 1);
        if (n < 0) continue;
        target[n] = '\0';
        printf("     fd %d → %s\n", fd, target);
    }
    closedir(d);
}

int main(int argc, char **argv)
{
    int keep       = atoi(want("SURV_FD"));
    int cloexec    = atoi(want("SURV_FD_CLOEXEC"));
    int ktimer     = atoi(want("SURV_TIMER"));
    long was_pid   = atol(want("SURV_PID"));
    double was_cpu = atof(want("SURV_CPU"));
    unsigned long long addr = strtoull(want("SURV_ADDR"), NULL, 0);
    unsigned long long was_nofile = strtoull(want("SURV_NOFILE"), NULL, 10);

    char detail[256], cwd[PATH_MAX];
    struct sigaction sa;
    struct itimerval it;
    struct itimerspec ts;
    struct timespec cpu;
    struct rlimit rl;
    sigset_t set;
    off_t off;
    mode_t um;
    int cl_alive, mapped, prio;
    long r;
    double now;

    (void) argc;
    printf("[звітувач] pid %ld, argv[0] = «%s»\n", (long) getpid(), argv[0]);
    printf("позначки: «+» є в новому образі, «-» немає; «!» — не збіглося\n\n");

    snprintf(detail, sizeof detail, "у стенді був %ld, зараз %ld",
             was_pid, (long) getpid());
    check(getpid() == was_pid, 1, "той самий номер процесу", detail);

    printf("\n  відкриті дескриптори нового образу:\n");
    list_open_fds();
    printf("\n");

    off = lseek(keep, 0, SEEK_CUR);
    snprintf(detail, sizeof detail, "fd %d, зсув %lld (стенд лишив 10)",
             keep, (long long) off);
    check(off >= 0, 1, "дескриптор без FD_CLOEXEC", detail);

    cl_alive = (fcntl(cloexec, F_GETFD) != -1);
    snprintf(detail, sizeof detail, "fd %d: fcntl → %s", cloexec,
             cl_alive ? "відкритий" : strerror(errno));
    check(cl_alive, 0, "дескриптор з O_CLOEXEC", detail);

    sigprocmask(SIG_BLOCK, NULL, &set);
    check(sigismember(&set, SIGUSR2), 1, "SIGUSR2 у масці заблокованих", "");

    sigpending(&set);
    check(sigismember(&set, SIGUSR2), 1, "відкладений SIGUSR2",
          "надісланий ще старій програмі");

    sigaction(SIGUSR1, NULL, &sa);
    check(sa.sa_handler != SIG_DFL, 0, "обробник SIGUSR1",
          "був адресою в старому образі");

    sigaction(SIGTERM, NULL, &sa);
    check(sa.sa_handler == SIG_IGN, 1, "ігнорування SIGTERM",
          "не адреса, а позначка");

    getitimer(ITIMER_REAL, &it);
    snprintf(detail, sizeof detail, "лишилося %ld.%03ld с із 300",
             (long) it.it_value.tv_sec, (long) it.it_value.tv_usec / 1000);
    check(it.it_value.tv_sec != 0 || it.it_value.tv_usec != 0, 1,
          "alarm(300), він же ITIMER_REAL", detail);

    errno = 0;
    r = syscall(SYS_timer_gettime, ktimer, &ts);
    snprintf(detail, sizeof detail, "ідентифікатор %d: timer_gettime → %s",
             ktimer, r == 0 ? "живий" : strerror(errno));
    check(r == 0, 0, "таймер від timer_create", detail);

    mapped = addr_is_mapped(addr);
    snprintf(detail, sizeof detail, "адреса %#llx у /proc/self/maps %s", addr,
             mapped > 0 ? "усередині відображення" : "не належить нікому");
    check(mapped > 0, 0, "сторінка mmap зі старого образу", detail);

    if (getcwd(cwd, sizeof cwd) == NULL) strcpy(cwd, "?");
    snprintf(detail, sizeof detail, "«%s»", cwd);
    check(strcmp(cwd, "/tmp") == 0, 1, "той самий поточний каталог", detail);

    um = umask(0);
    umask(um);
    snprintf(detail, sizeof detail, "%04o", (unsigned) um);
    check(um == 0027, 1, "той самий umask", detail);

    getrlimit(RLIMIT_NOFILE, &rl);
    snprintf(detail, sizeof detail, "м'який ліміт %llu",
             (unsigned long long) rl.rlim_cur);
    check(rl.rlim_cur == was_nofile, 1, "той самий RLIMIT_NOFILE", detail);

    errno = 0;
    prio = getpriority(PRIO_PROCESS, 0);
    snprintf(detail, sizeof detail, "nice = %d", prio);
    check(errno == 0 && prio == 5, 1, "те саме значення nice", detail);

    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &cpu);
    now = cpu.tv_sec + cpu.tv_nsec / 1e9;
    snprintf(detail, sizeof detail, "стенд намолов %.3f с, лічильник каже %.3f с",
             was_cpu, now);
    check(now >= was_cpu, 1, "процесорний час не скинувся", detail);

    printf("\nневідповідностей: %d\n", mismatch);
    return mismatch == 0 ? 0 : 1;
}
```

## Запуск

```
cc -O2 -Wall -Wextra -o setup  setup.c
cc -O2 -Wall -Wextra -o report report.c
./setup ./report
```

Приблизно такий вигляд має звіт (числа й шляхи, звісно, свої):

```
[стенд] pid 4711: fd 3 без CLOEXEC (зсув 10), fd 4 з O_CLOEXEC,
        SIGUSR2 заблоковано й надіслано собі, alarm(300),
        POSIX-таймер #0, сторінка на 0x7f2c9a3f1000, намелено 0.152 с

[звітувач] pid 4711, argv[0] = «./report»
позначки: «+» є в новому образі, «-» немає; «!» — не збіглося

  +   той самий номер процесу — у стенді був 4711, зараз 4711

  відкриті дескриптори нового образу:
     fd 0 → /dev/pts/3
     fd 1 → /dev/pts/3
     fd 2 → /dev/pts/3
     fd 3 → /tmp/exec-probe.dat

  +   дескриптор без FD_CLOEXEC — fd 3, зсув 10 (стенд лишив 10)
  -   дескриптор з O_CLOEXEC — fd 4: fcntl → Bad file descriptor
  +   SIGUSR2 у масці заблокованих
  +   відкладений SIGUSR2 — надісланий ще старій програмі
  -   обробник SIGUSR1 — був адресою в старому образі
  +   ігнорування SIGTERM — не адреса, а позначка
  +   alarm(300), він же ITIMER_REAL — лишилося 299.847 с із 300
  -   таймер від timer_create — ідентифікатор 0: timer_gettime → Invalid argument
  -   сторінка mmap зі старого образу — адреса 0x7f2c9a3f1000 не належить нікому
  +   той самий поточний каталог — «/tmp»
  +   той самий umask — 0027
  +   той самий RLIMIT_NOFILE — м'який ліміт 512
  +   те саме значення nice — nice = 5
  +   процесорний час не скинувся — стенд намолов 0.152 с, лічильник каже 0.153 с

невідповідностей: 0
```

Рядка «`[стенд] atexit пережив заміну`» у виводі немає — і його відсутність теж результат. Обробник, зареєстрований через `atexit`, — це адреса функції в таблиці, яку веде бібліотека С у пам'яті старого образу; ані таблиці, ані функції вже не існує, і викликати нема чого. Тому програма, яка робить `exec`, ніколи не «завершується» у звичному сенсі: жоден її прибиральник не спрацює.

## Три рядки, заради яких усе це

**Зсув.** Найважливіше в рядку про дескриптор — не те, що номер 3 досі відкритий, а те, що читання почнеться з десятого байта. Номер дескриптора — це індекс у таблиці процесу, а зсув живе не в ньому, а в **описі відкритого файлу** — окремій структурі ядра, на яку той індекс лише посилається ([опис відкритого файлу: що спільне після fork](book:unix-linux/open-file-description) — саме тут зберігаються режим відкриття, прапорці стану й поточна позиція; на один опис можуть посилатися кілька дескрипторів і кілька процесів). Заміна образу не чіпає ані таблиці, ані опису — тому нова програма продовжує рівно з того місця, де спинилася стара. На цьому тримається і `wc -l < data.txt`, і будь-яке інше перенаправлення.

![Таблиця дескрипторів до і після execve: елемент без FD_CLOEXEC переходить у новий образ разом з описом відкритого файлу і його зсувом, елемент з O_CLOEXEC ядро закриває саме в мить заміни](/reference/unix-linux/processes/exec-semantics/img/exec-fd-across.svg)

*Таблиця дескрипторів належить процесові, а не образові, — тому нова програма читає з того самого місця, де спинилася стара.*

**Відкладений сигнал.** Звітувач бачить у черзі `SIGUSR2`, якого йому ніхто не надсилав: його надіслали програмі, якої вже немає. Черга й маска живуть у структурах ядра, тож заміна образу для них — не подія ([маскування сигналів і signalfd](book:unix-linux/signal-mask-signalfd) — маска — це бітова карта «цих поки не доставляти», і заблокований сигнал не зникає, а чекає розблокування). Перевірити це можна жорсткіше: додайте наприкінці звітувача розблокування `SIGUSR2` — і процес умить помре від сигналу, посланого старому образові. Оболонка покаже код 140, тобто 128 + 12, де 12 — номер `SIGUSR2` на x86-64 і arm64 ([код виходу як інтерфейс програми](book:unix-linux/exit-status) — завершення від сигналу оболонка позначає числом 128 плюс номер сигналу).

**Два таймери.** `alarm(300)` перейшов, `timer_create` — ні, і це не примха стандарту. Інтервальний таймер один на кожен із трьох названих сталими ґатунків: нова програма може спитати про `ITIMER_REAL` без жодного знання про стару. POSIX-таймер має ідентифікатор, виданий тому, кого вже немає; новий образ не має чим на нього послатися — а таймер, на який неможливо послатися, неможливо ані спинити, ані переналаштувати. Тому ядро видаляє такі таймери разом зі старим образом, і `timer_gettime` відповідає `EINVAL`: такого таймера в цьому процесі немає.

## Те саме без жодного рядка коду

Стенд бере програму з командного рядка, тож замість звітувача можна запустити будь-що. А частину перевірених величин ядро й само виписує в `/proc`:

```
$ ./setup /usr/bin/grep -E '^(Umask|SigBlk|SigIgn|SigCgt|SigPnd|ShdPnd)' /proc/self/status
Umask:	0027
SigPnd:	0000000000000000
ShdPnd:	0000000000000800
SigBlk:	0000000000000800
SigIgn:	0000000000004000
SigCgt:	0000000000000000
```

Ці маски — шістнадцяткові бітові карти, у яких сигнал із номером *n* займає біт *n−1*. Отже, `0x800` — це біт 11, тобто `SIGUSR2`: він і заблокований (`SigBlk`), і чекає в черзі всього процесу (`ShdPnd`). `0x4000` — біт 14, тобто `SIGTERM`, і він у переліку ігнорованих: позначка перейшла. А `SigCgt` — порожній, хоч стенд і ставив обробник на `SIGUSR1`: спіймані сигнали заміна скидає на типову дію ([диспозиція сигналу: обробник, ігнорування, типова дія](book:unix-linux/signal-disposition) — три можливі стани на кожен номер, і лише один із них є адресою в пам'яті процесу). Сам `grep` про дослід не знає нічого — він просто друкує те, що ядро написало про нього самого.

Зверніть увагу на повний шлях до `grep`. Стенд кличе `execve` напряму, а `execve` не знає про змінну `PATH` — пошук по каталогах роблять обгортки бібліотеки С й оболонки, у просторі користувача.

## Пастки

**`fflush(NULL)` перед заміною — не охайність, а необхідність.** Буфер `stdio` — звичайна пам'ять старого образу. Запустіть стенд у канал (`./setup ./report | cat`): вивід стає поблоковим, буфер не заповниться до кінця, і без `fflush` усі рядки стенда просто зникнуть — не «загубляться в дорозі», а ніколи не будуть записані. Це не властивість досліду, а найпоширеніша справжня помилка коду, який щось друкує перед `exec` ([буферизація stdio: порядкова, поблокова, без буфера](book:unix-linux/stdio-buffering) — режим бібліотека обирає за тим, куди веде дескриптор: термінал — порядково, файл чи канал — поблоково).

**Відносний шлях і `chdir`.** Стенд міняє каталог — і `./report` після цього означає вже інший файл. Тому шлях резолвиться `realpath` **до** зміни каталогу. Той самий підступ ловить кожного, хто пише запускалку: у вікні між розгалуженням і заміною можна змінити стільки, що аргументи самого `exec` перестають означати те, що означали, коли їх складали.

**Порядок: спершу маска, потім сигнал.** `kill(getpid(), SIGUSR2)` без попереднього блокування — це негайна смерть процесу: типова дія `SIGUSR2` — завершити. Переставте два рядки місцями, і замість звіту ви побачите «User defined signal 2».

**Довгий `alarm` — теж навмисно.** `alarm` і `setitimer(ITIMER_REAL)` — один і той самий таймер, і його типова дія теж убиває процес. З `alarm(1)` дослід просто не встиг би надрукувати звіт.

**Вимірювач змінює те, що міряє.** `opendir("/proc/self/fd")` сам відкриває дескриптор — і той з'являється у власному переліку; тому його доводиться відкидати через `dirfd`. Так само середовище, з якого ви запускаєте стенд, може лишити по собі власні дескриптори: усе, що не помічене `FD_CLOEXEC`, звітувач покаже чесно, і це не хиба стенда, а справжній стан процесу.

**Сирі системні виклики для таймера.** Тип `timer_t` у бібліотеці С непрозорий, і узаконеного способу передати його іншій програмі немає — що само по собі вже половина відповіді. Щоб спитати ядро прямо, стенд і звітувач ходять до `timer_create` і `timer_gettime` через `syscall()`: там ідентифікатор — звичайний `int`, виданий ядром. Побічний зиск — не потрібно підключати `librt`, як того вимагають старіші системи. Плата: на 32-бітних системах із 64-бітним `time_t` цих номерів може не бути взагалі (лишилися тільки їхні варіанти з суфіксом `64`), і замість очікуваного `EINVAL` звіт покаже `ENOSYS` — висновок той самий, причина інша.

**`nice` виставляється абсолютно.** `setpriority(…, 5)` не додає п'ятірку, а ставить п'ятірку. Якщо оболонка вже працює з `nice` більше за 5, то це вже підвищення пріоритету, і непривілейований процес дістане `EPERM`; стенд про це скаже й піде далі, а звіт покаже розбіжність у цьому рядку — саме для таких випадків там є знак «!» ([ліміти ресурсів: rlimit і ulimit](book:unix-linux/resource-limits) — так само працює й м'який ліміт дескрипторів: знижувати його вільно, піднімати назад — уже ні).

**Чого тут немає.** Найцікавіший наслідок заміни — підвищення прав через біт `setuid` — стенд не перевіряє: для цього потрібен окремий файл із власником і встановленим бітом, і в такого досліду інший обсяг ([setuid, setgid і підвищення прав](book:unix-linux/setuid-and-privilege)).

Коли якийсь рядок не збігається, найкоротший шлях до причини — подивитися, що насправді покликали: `strace -e trace=execve,timer_create,timer_gettime ./setup ./report` показує один-єдиний `execve` посеред потоку викликів, а поруч — обидва звертання до таймера й те, чим ядро на них відповіло ([трасування системних викликів](book:unix-linux/syscall-tracing)).
