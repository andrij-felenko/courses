# ⚙️ Лабораторія обліку: спалити пропорцію й опитати чотири джерела

Тут повна програма на C, яка спалює наперед задану суміш власного й ядрового коду, а тоді ставить те саме питання — «скільки процесора я щойно з'їла?» — чотирьом різним інтерфейсам ядра й кладе відповіді поруч. За три секунди на власній машині стає видно те, що з опису звучить як тонкість: **сума** сходиться до мікросекунди щоразу, а **поділ** тієї самої суми на `user` і `sys` гуляє на вісім відсоткових пунктів між прогонами однакового навантаження.

Найкорисніше в цій лабораторії — саме те, що збіг суми виявляється не доказом точності, а її протилежністю. Але це видно лише тоді, коли числа лежать поруч.

## Умова

Лабораторія має показати чотири речі, і кожну — числом на екрані, а не переказом:

- `utime + stime` будь-якого тикового інтерфейсу дорівнює точній сумі планувальника з точністю до мікросекунди — і це **не** свідчення якості обліку;
- поділ між `user` і `sys` на однаковому навантаженні розходиться від прогону до прогону, і розмах цього розходження збігається з тим, що передбачає статистика;
- програма, що не дожила до жодного тику, показує в `/proc` нулі — але не тому, що ядро не має числа;
- `/proc/self/stat` і `/proc/self/schedstat` лежать в одній теці й відповідають на питання про різні речі.

Понад це — одна вимога до самої лабораторії: навантаження мусить бути **керованим**. Спалювати «щось важке» й дивитися на числа марно: неконтрольована робота перетворює кожне з чотирьох джерел на шум, і тоді жодне порівняння нічого не доводить.

## Ідея: чим спалювати кожен із двох режимів

Потрібні дві цеглинки: робота, що гарантовано лишається в режимі користувача, і робота, що гарантовано входить у ядро.

З першою просто — арифметика, яку оптимізатор не має права викинути. Годиться генератор псевдовипадкових чисел `xorshift64`: три зсуви й три «виключних або» на оберт, жодного звертання до пам'яті поза одним регістром, стала ціна на такт.

З другою є пастка, і саме на ній ця лабораторія найчастіше провалюється в чужих руках. Очевидні кандидати на «дешевий системний виклик» — `gettimeofday()`, `time()`, `clock_gettime(CLOCK_MONOTONIC)` — у ядро **не входять узагалі**. Ядро відображає в кожен процес маленьку бібліотеку зі своїм кодом, і ці виклики обслуговуються прямо в режимі користувача, читанням зі спільної сторінки ([vDSO: бібліотека від ядра в кожному процесі](book:unix-linux/vdso) — кілька функцій, які ядро віддає програмі як звичайний код, щоб вона не платила за перетин межі). Цикл із мільйона `clock_gettime(CLOCK_MONOTONIC)` спалює `user`, а не `sys`, — і людина, що будувала на ньому дослід, отримує нулі там, де чекала половини.

Потрібен виклик, у якого немає ані версії у vDSO, ані кешу в libc. `getppid()` підходить: кешувати його нема сенсу, бо батько може змінитися будь-якої миті, а окремої швидкої реалізації для нього ніхто не писав. Щоб не залежати навіть від цього, кличемо його через `syscall(SYS_getppid)` — так межа перетинається напевно. Уся ціна такого виклику — це і є ціна самого перетину, приблизно 300–500 нс ([системний виклик: як програма просить ядро](book:unix-linux/syscall-mechanics) — інструкція переходу, перемикання стека й привілеїв, повернення назад).

Третє рішення — **дрібність чергування**. Якби ми спалили три секунди арифметики, а потім секунду викликів, тик чесно опитав би обидві фази й поділ вийшов би правильним; дивитися було б нема на що. Цікавий режим — той, у якому живуть справжні програми: чергування на масштабі, значно меншому за тик. Тик при HZ = 250 — це 4 мс, тож скибку беремо в одну мілісекунду й менше. Тоді кожен тик застає не фазу, а суміш, — і поділ стає тим, чим він є, вибіркою.

Останнє, що треба сказати чесно **до** запуску: ручка задає, як ділиться **час між двома видами спалювання**, а не як він поділиться між режимами. Цикл навколо системного виклику — лічильник, порівняння, сама обгортка `syscall()` — це власний код. Тому замовлені 35 % «системних скибок» дадуть десь 24 % `sys`. Ця різниця — не похибка досліду, а його перший результат: вона й каже, яка частка циклу `getppid` справді минає в ядрі.

## Каркас: чотири джерела в одному знімку

Уся програма — один файл; шматки нижче йдуть у нього по порядку.

:::tabs
```c
#define _GNU_SOURCE
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

/* Прочитати невеликий файл цілком. Повертає кількість байтів або −1. */
static ssize_t slurp(const char *path, char *buf, size_t cap)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t n = read(fd, buf, cap - 1);
    close(fd);
    if (n < 0) return -1;
    buf[n] = '\0';
    return n;
}

/* Настінний монотонний час. Іде через vDSO, тобто НЕ входить у ядро й нічого
   не додає до системного часу — саме тому ним безпечно керувати спалюванням. */
static double now_mono(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + ts.tv_nsec / 1e9;
}

static double clk_tck(void)
{
    static double hz;
    if (hz == 0.0) hz = (double)sysconf(_SC_CLK_TCK);
    return hz;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <chrono>
#include <thread>
#include <utility>
#include <iomanip>
#include <algorithm>
#include <cstdint>
#include <cerrno>
#include <ctime>
#include <unistd.h>
#include <sys/resource.h>
#include <sys/syscall.h>

// Прочитати невеликий файл цілком у std::string.
static std::string slurp(std::string_view path)
{
    std::ifstream f(path.data());
    if (!f.is_open()) return {};
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

// Настінний монотонний час через std::chrono::steady_clock.
static auto now_mono()
{
    return std::chrono::steady_clock::now();
}

static double clk_tck()
{
    static double hz = static_cast<double>(sysconf(_SC_CLK_TCK));
    return hz;
}
```
:::

Далі — чотири читачі, по одному на джерело.

:::tabs
```c
/* Джерело 1: точна сума планувальника, наносекунди, без жодної вибірки. */
static double cpu_clock(clockid_t id)
{
    struct timespec ts;
    if (clock_gettime(id, &ts) < 0) return -1.0;
    return (double)ts.tv_sec + ts.tv_nsec / 1e9;
}

/* Джерело 2: поділ на режими в мікросекундах. */
static void rusage_pair(int who, double *u, double *s)
{
    struct rusage r;
    if (getrusage(who, &r) < 0) { *u = *s = -1.0; return; }
    *u = (double)r.ru_utime.tv_sec + r.ru_utime.tv_usec / 1e6;
    *s = (double)r.ru_stime.tv_sec + r.ru_stime.tv_usec / 1e6;
}

/* Джерело 3: поля 14 і 15 у stat — той самий поділ, але в тиках USER_HZ.
   Розбирати можна лише від ОСТАННЬОЇ дужки: друге поле — ім'я команди,
   і ядро друкує його як є, разом із пробілами й дужками всередині. */
static int proc_stat_cpu(const char *path, double *u, double *s)
{
    char buf[1024];
    if (slurp(path, buf, sizeof buf) < 0) return -1;
    char *p = strrchr(buf, ')');
    if (!p) return -1;

    unsigned long ut = 0, st = 0;
    /* після "») " ідуть поля 3…: state ppid pgrp session tty tpgid flags
       minflt cminflt majflt cmajflt utime stime */
    if (sscanf(p + 2, "%*c %*d %*d %*d %*d %*d %*u %*lu %*lu %*lu %*lu %lu %lu",
               &ut, &st) != 2) return -1;
    *u = ut / clk_tck();
    *s = st / clk_tck();
    return 0;
}

/* Джерело 4: перше число schedstat — se.sum_exec_runtime у наносекундах,
   узяте з поля задачі як є. Файл існує лише при CONFIG_SCHED_INFO;
   немає файлу — немає числа, і це НЕ те саме, що нуль. */
static int proc_runtime(const char *path, double *rt)
{
    char buf[128];
    if (slurp(path, buf, sizeof buf) < 0) return -1;
    unsigned long long ns = 0;
    if (sscanf(buf, "%llu", &ns) != 1) return -1;
    *rt = ns / 1e9;
    return 0;
}
```
```cpp
// Джерело 1: точна сума планувальника, наносекунди, без жодної вибірки.
static double cpu_clock(clockid_t id)
{
    timespec ts{};
    if (clock_gettime(id, &ts) < 0) return -1.0;
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

// Джерело 2: поділ на режими в мікросекундах.
static std::pair<double, double> rusage_pair(int who)
{
    rusage r{};
    if (getrusage(who, &r) < 0) return {-1.0, -1.0};
    double u = r.ru_utime.tv_sec + r.ru_utime.tv_usec / 1e6;
    double s = r.ru_stime.tv_sec + r.ru_stime.tv_usec / 1e6;
    return {u, s};
}

// Джерело 3: поля 14 і 15 у stat — той самий поділ, але в тиках USER_HZ.
static std::pair<bool, std::pair<double, double>> proc_stat_cpu(std::string_view path)
{
    std::string content = slurp(path);
    if (content.empty()) return {false, {-1.0, -1.0}};

    auto pos = content.rfind(')');
    if (pos == std::string::npos || pos + 2 >= content.size())
        return {false, {-1.0, -1.0}};

    std::istringstream iss(content.substr(pos + 2));
    char state;
    int ppid, pgrp, session, tty, tpgid;
    unsigned flags;
    unsigned long minflt, cminflt, majflt, cmajflt, ut = 0, st = 0;

    if (iss >> state >> ppid >> pgrp >> session >> tty >> tpgid
            >> flags >> minflt >> cminflt >> majflt >> cmajflt >> ut >> st) {
        return {true, {ut / clk_tck(), st / clk_tck()}};
    }
    return {false, {-1.0, -1.0}};
}

// Джерело 4: перше число schedstat — se.sum_exec_runtime у наносекундах.
static std::pair<bool, double> proc_runtime(std::string_view path)
{
    std::string content = slurp(path);
    if (content.empty()) return {false, -1.0};

    std::istringstream iss(content);
    unsigned long long ns = 0;
    if (iss >> ns) return {true, ns / 1e9};
    return {false, -1.0};
}
```
:::

Тепер знімок усіх джерел за один захід і різниця двох знімків. Мірятимемо саме приріст: абсолютні числа тягнуть за собою час запуску програми й розбір аргументів, а нас цікавить лише те, що спалено між двома точками.

:::tabs
```c
typedef struct {
    double clk_proc, clk_thr;          /* точна сума: процес і потік        */
    double ru_self_u, ru_self_s;       /* поділ: процес                     */
    double ru_thr_u,  ru_thr_s;        /* поділ: потік                      */
    double stat_u, stat_s;   int stat_ok;
    double sched_grp, sched_thr; int sched_ok;
} snap;

static void take(snap *k)
{
    memset(k, 0, sizeof *k);
    k->stat_ok  = (proc_stat_cpu("/proc/self/stat", &k->stat_u, &k->stat_s) == 0);
    k->sched_ok = (proc_runtime("/proc/self/schedstat",        &k->sched_grp) == 0)
               && (proc_runtime("/proc/thread-self/schedstat", &k->sched_thr) == 0);
    rusage_pair(RUSAGE_SELF,   &k->ru_self_u, &k->ru_self_s);
    rusage_pair(RUSAGE_THREAD, &k->ru_thr_u,  &k->ru_thr_s);
    k->clk_proc = cpu_clock(CLOCK_PROCESS_CPUTIME_ID);
    k->clk_thr  = cpu_clock(CLOCK_THREAD_CPUTIME_ID);
}

static void diff(const snap *a, const snap *b, snap *d)
{
    d->clk_proc  = b->clk_proc  - a->clk_proc;
    d->clk_thr   = b->clk_thr   - a->clk_thr;
    d->ru_self_u = b->ru_self_u - a->ru_self_u;
    d->ru_self_s = b->ru_self_s - a->ru_self_s;
    d->ru_thr_u  = b->ru_thr_u  - a->ru_thr_u;
    d->ru_thr_s  = b->ru_thr_s  - a->ru_thr_s;
    d->stat_u    = b->stat_u    - a->stat_u;
    d->stat_s    = b->stat_s    - a->stat_s;
    d->sched_grp = b->sched_grp - a->sched_grp;
    d->sched_thr = b->sched_thr - a->sched_thr;
    d->stat_ok   = a->stat_ok  && b->stat_ok;
    d->sched_ok  = a->sched_ok && b->sched_ok;
}
```
```cpp
struct snap {
    double clk_proc = 0.0, clk_thr = 0.0;
    double ru_self_u = 0.0, ru_self_s = 0.0;
    double ru_thr_u = 0.0,  ru_thr_s = 0.0;
    double stat_u = 0.0, stat_s = 0.0;
    bool stat_ok = false;
    double sched_grp = 0.0, sched_thr = 0.0;
    bool sched_ok = false;
};

static void take(snap& k)
{
    k = snap{};
    auto [st_ok, st_val] = proc_stat_cpu("/proc/self/stat");
    k.stat_ok = st_ok;
    k.stat_u = st_val.first;
    k.stat_s = st_val.second;

    auto [sc_grp_ok, sc_grp_val] = proc_runtime("/proc/self/schedstat");
    auto [sc_thr_ok, sc_thr_val] = proc_runtime("/proc/thread-self/schedstat");
    k.sched_ok = sc_grp_ok && sc_thr_ok;
    k.sched_grp = sc_grp_val;
    k.sched_thr = sc_thr_val;

    std::tie(k.ru_self_u, k.ru_self_s) = rusage_pair(RUSAGE_SELF);
    std::tie(k.ru_thr_u,  k.ru_thr_s)  = rusage_pair(RUSAGE_THREAD);
    k.clk_proc = cpu_clock(CLOCK_PROCESS_CPUTIME_ID);
    k.clk_thr = cpu_clock(CLOCK_THREAD_CPUTIME_ID);
}

static snap diff(const snap& a, const snap& b)
{
    snap d{};
    d.clk_proc  = b.clk_proc  - a.clk_proc;
    d.clk_thr   = b.clk_thr   - a.clk_thr;
    d.ru_self_u = b.ru_self_u - a.ru_self_u;
    d.ru_self_s = b.ru_self_s - a.ru_self_s;
    d.ru_thr_u  = b.ru_thr_u  - a.ru_thr_u;
    d.ru_thr_s  = b.ru_thr_s  - a.ru_thr_s;
    d.stat_u    = b.stat_u    - a.stat_u;
    d.stat_s    = b.stat_s    - a.stat_s;
    d.sched_grp = b.sched_grp - a.sched_grp;
    d.sched_thr = b.sched_thr - a.sched_thr;
    d.stat_ok   = a.stat_ok  && b.stat_ok;
    d.sched_ok  = a.sched_ok && b.sched_ok;
    return d;
}
```
:::

Порядок читання всередині `take()` не випадковий. Найдорожче — два файли в `/proc`: кожен коштує відкриття, читання, закриття й розбору, бо вміст такого файлу не лежить на диску, а формується ядром у мить читання ([/proc: процеси як файли](book:unix-linux/proc-filesystem) — тека на кожен процес, у якій текст народжується під час `read`). Тому вони йдуть першими, а найточніші й найдешевші годинники — останніми: так пізніші читання додають до раніших щонайменше.

Отже, що саме читає кожне з чотирьох джерел:

```
джерело                             поле в ядрі             роздільність
clock_gettime(*_CPUTIME_ID)         sum_exec_runtime        1 нс
/proc/<pid>/schedstat, 1-ше число   sum_exec_runtime сире   1 нс
getrusage()                         cputime_adjust()        1 мкс
/proc/<pid>/stat, поля 14–15        cputime_adjust()        1/USER_HZ = 10 мс
```

Два верхні рядки — точна сума, два нижні — та сама сума, поділена вибіркою. Уся лабораторія — про різницю між цими двома парами.

## Спалювання

:::tabs
```c
static volatile uint64_t sink;   /* щоб оптимізатор не викинув цикл цілком */

/* Власний код: xorshift64 без жодного звертання до ядра. */
static void burn_user(double seconds)
{
    if (seconds <= 0.0) return;
    double deadline = now_mono() + seconds;
    uint64_t x = sink | 1u;
    do {
        for (int i = 0; i < 20000; i++) {
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
        }
        sink = x;
    } while (now_mono() < deadline);
}

/* Код ядра: найдешевший виклик, що ГАРАНТОВАНО перетинає межу.
   Через syscall() навмисно — щоб жодна libc не підмінила його кешем. */
static void burn_sys(double seconds)
{
    if (seconds <= 0.0) return;
    double deadline = now_mono() + seconds;
    do {
        for (int i = 0; i < 64; i++)
            (void)syscall(SYS_getppid);
    } while (now_mono() < deadline);
}

/* Спалити ~seconds часу, чергуючи два види роботи скибками по slice секунд.
   Скибка навмисно менша за тик: саме дрібне чергування й робить поділ вибіркою. */
static void burn_mix(double seconds, double kfrac, double slice)
{
    double deadline = now_mono() + seconds;
    if (kfrac < 0.0) kfrac = 0.0;
    if (kfrac > 1.0) kfrac = 1.0;
    while (now_mono() < deadline) {
        burn_sys(slice * kfrac);
        burn_user(slice * (1.0 - kfrac));
    }
}
```
```cpp
static volatile uint64_t sink;   // щоб оптимізатор не викинув цикл цілком

// Власний код: xorshift64 без жодного звертання до ядра.
static void burn_user(double seconds)
{
    if (seconds <= 0.0) return;
    using namespace std::chrono;
    auto deadline = steady_clock::now() + duration_cast<steady_clock::duration>(duration<double>(seconds));
    uint64_t x = sink | 1u;
    do {
        for (int i = 0; i < 20000; i++) {
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
        }
        sink = x;
    } while (steady_clock::now() < deadline);
}

// Код ядра: найдешевший виклик, що ГАРАНТОВАНО перетинає межу.
static void burn_sys(double seconds)
{
    if (seconds <= 0.0) return;
    using namespace std::chrono;
    auto deadline = steady_clock::now() + duration_cast<steady_clock::duration>(duration<double>(seconds));
    do {
        for (int i = 0; i < 64; i++)
            (void)syscall(SYS_getppid);
    } while (steady_clock::now() < deadline);
}

// Спалити ~seconds часу, чергуючи два види роботи скибками по slice секунд.
static void burn_mix(double seconds, double kfrac, double slice)
{
    using namespace std::chrono;
    auto deadline = steady_clock::now() + duration_cast<steady_clock::duration>(duration<double>(seconds));
    kfrac = std::clamp(kfrac, 0.0, 1.0);
    while (steady_clock::now() < deadline) {
        burn_sys(slice * kfrac);
        burn_user(slice * (1.0 - kfrac));
    }
}
```
:::

Розміри внутрішніх пачок — 20 000 обертів арифметики й 64 виклики — підібрані так, щоб кожна пачка коштувала приблизно 25–30 мкс. Це компроміс: менша пачка означала б, що перевірка часу (нехай і через vDSO, за двадцять наносекунд) починає важити помітну частку роботи; більша не дала б потрапити в мілісекундну скибку.

## Один прогін

:::tabs
```c
static void report(const snap *d)
{
    printf("  точна сума (лічильник планувальника)\n");
    printf("    clock_gettime(PROCESS_CPUTIME)   %11.6f с\n", d->clk_proc);
    printf("    clock_gettime(THREAD_CPUTIME)    %11.6f с\n", d->clk_thr);
    if (d->sched_ok) {
        printf("    /proc/self/schedstat  [0]        %11.6f с\n", d->sched_grp);
        printf("    /proc/thread-self/schedstat [0]  %11.6f с\n", d->sched_thr);
    } else {
        printf("    schedstat  нема: ядро зібране без CONFIG_SCHED_INFO\n");
    }

    printf("  поділ на режими (вибірка, зшита з точною сумою)\n");
    printf("    getrusage(RUSAGE_SELF)     user %10.6f  sys %10.6f  сума %11.6f\n",
           d->ru_self_u, d->ru_self_s, d->ru_self_u + d->ru_self_s);
    printf("    getrusage(RUSAGE_THREAD)   user %10.6f  sys %10.6f  сума %11.6f\n",
           d->ru_thr_u, d->ru_thr_s, d->ru_thr_u + d->ru_thr_s);
    if (d->stat_ok)
        printf("    /proc/self/stat 14-15      user %10.2f  sys %10.2f  сума %11.2f"
               "   (крок %.0f мс)\n",
               d->stat_u, d->stat_s, d->stat_u + d->stat_s, 1000.0 / clk_tck());

    double tot = d->ru_self_u + d->ru_self_s;
    printf("  сума rusage − точна сума  %+.6f с\n", tot - d->clk_proc);
    if (tot > 0.0)
        printf("  частка sys за rusage      %.2f %%\n", 100.0 * d->ru_self_s / tot);
}

static int mode_mix(double seconds, double kfrac, double slice)
{
    snap a, b, d;
    printf("спалюємо %.2f с, скибка %.2f мс, задана частка системних скибок %.0f %%\n",
           seconds, slice * 1000.0, kfrac * 100.0);
    take(&a);
    burn_mix(seconds, kfrac, slice);
    take(&b);
    diff(&a, &b, &d);
    report(&d);
    return 0;
}
```
```cpp
static void report(const snap& d)
{
    std::cout << "  точна сума (лічильник планувальника)\n"
              << std::fixed << std::setprecision(6)
              << "    clock_gettime(PROCESS_CPUTIME)   " << std::setw(11) << d.clk_proc << " с\n"
              << "    clock_gettime(THREAD_CPUTIME)    " << std::setw(11) << d.clk_thr << " с\n";
    if (d.sched_ok) {
        std::cout << "    /proc/self/schedstat  [0]        " << std::setw(11) << d.sched_grp << " с\n"
                  << "    /proc/thread-self/schedstat [0]  " << std::setw(11) << d.sched_thr << " с\n";
    } else {
        std::cout << "    schedstat  нема: ядро зібране без CONFIG_SCHED_INFO\n";
    }

    std::cout << "  поділ на режими (вибірка, зшита з точною сумою)\n"
              << "    getrusage(RUSAGE_SELF)     user " << std::setw(10) << d.ru_self_u
              << "  sys " << std::setw(10) << d.ru_self_s
              << "  сума " << std::setw(11) << (d.ru_self_u + d.ru_self_s) << "\n"
              << "    getrusage(RUSAGE_THREAD)   user " << std::setw(10) << d.ru_thr_u
              << "  sys " << std::setw(10) << d.ru_thr_s
              << "  сума " << std::setw(11) << (d.ru_thr_u + d.ru_thr_s) << "\n";
    if (d.stat_ok) {
        std::cout << "    /proc/self/stat 14-15      user " << std::setprecision(2)
                  << std::setw(10) << d.stat_u << "  sys " << std::setw(10) << d.stat_s
                  << "  сума " << std::setw(11) << (d.stat_u + d.stat_s)
                  << std::setprecision(0)
                  << "   (крок " << (1000.0 / clk_tck()) << " мс)\n";
    }

    double tot = d.ru_self_u + d.ru_self_s;
    std::cout << std::setprecision(6) << std::showpos
              << "  сума rusage − точна сума  " << (tot - d.clk_proc) << " с\n"
              << std::noshowpos;
    if (tot > 0.0) {
        std::cout << std::setprecision(2)
                  << "  частка sys за rusage      " << (100.0 * d.ru_self_s / tot) << " %\n";
    }
}

static int mode_mix(double seconds, double kfrac, double slice)
{
    snap a{}, b{};
    std::cout << std::fixed << std::setprecision(2)
              << "спалюємо " << seconds << " с, скибка " << (slice * 1000.0)
              << " мс, задана частка системних скибок " << std::setprecision(0)
              << (kfrac * 100.0) << " %\n";
    take(a);
    burn_mix(seconds, kfrac, slice);
    take(b);
    snap d = diff(a, b);
    report(d);
    return 0;
}
```
:::

Прогін на машині з HZ = 250 і USER_HZ = 100:

```
$ ./cpulab mix 3.0 0.35 1.0
спалюємо 3.00 с, скибка 1.00 мс, задана частка системних скибок 35 %
  точна сума (лічильник планувальника)
    clock_gettime(PROCESS_CPUTIME)      3.001642 с
    clock_gettime(THREAD_CPUTIME)       3.001640 с
    /proc/self/schedstat  [0]           3.000317 с
    /proc/thread-self/schedstat [0]     3.000317 с
  поділ на режими (вибірка, зшита з точною сумою)
    getrusage(RUSAGE_SELF)     user   2.281248  sys   0.720394  сума    3.001642
    getrusage(RUSAGE_THREAD)   user   2.281247  sys   0.720393  сума    3.001640
    /proc/self/stat 14-15      user       2.28  sys       0.72  сума        3.00   (крок 10 мс)
  сума rusage − точна сума  +0.000000 с
  частка sys за rusage      24.00 %
```

Чотири речі в цих рядках варті окремого погляду.

**Сума збігається точно — і це нічого не доводить.** `2.281248 + 0.720394` дорівнює `3.001642` до останньої мікросекунди, тобто рівно тому, що показав годинник планувальника. Спокуса прочитати це як «облік точний» велика й хибна: рівність не виміряна, а **побудована**. Ядро бере довжину в планувальника, ділить її в пропорції, яку намалювали тики, і віддає обидві частки — тож їхня сума не може не збігтися. Збіг суми доводить лише те, що арифметика зроблена правильно.

**Число з `schedstat` менше за годинник на 1.3 мс.** Обидва читають те саме поле, але по-різному. `clock_gettime` іде шляхом, який спершу просить планувальник **довести облік поточної задачі до цієї миті** — дописати те, що вона встигла з останнього оновлення. `schedstat` друкує поле як є, тому відстає рівно на час, що минув з останнього оновлення обліку: від нуля до тику. Це та рідкісна розбіжність, яку видно неозброєним оком і яку легко прийняти за помилку в програмі.

**`/proc` втратив 1.6 мс на порожньому місці.** Показані `2.28` і `0.72` дають рівно `3.00` — на ті самі 1.6 мс менше за справжню суму. Причина не в обліку, а в одиницях: кожне з двох чисел ділиться на USER_HZ і зрізається до цілого тику, тож на кожному губиться до 10 мс.

**Потік і процес збіглися** — бо потік тут один. Саме тому їхньої різниці не видно доти, доки її не зробити видимою навмисно.

## Розмах: те саме вісім разів

:::tabs
```c
static int mode_spread(int runs, double seconds, double kfrac, double slice)
{
    if (runs < 2)  runs = 8;
    if (runs > 64) runs = 64;

    double rt_min = 1e30, rt_max = -1e30, sh_min = 1e30, sh_max = -1e30;

    printf("прогін   точна сума        user           sys      частка sys\n");
    for (int i = 1; i <= runs; i++) {
        snap a, b, d;
        take(&a);
        burn_mix(seconds, kfrac, slice);
        take(&b);
        diff(&a, &b, &d);

        double tot = d.ru_self_u + d.ru_self_s;
        double share = tot > 0.0 ? d.ru_self_s / tot : 0.0;
        printf("  %2d    %10.6f   %10.6f   %10.6f     %6.2f %%\n",
               i, d.clk_proc, d.ru_self_u, d.ru_self_s, 100.0 * share);

        if (d.clk_proc < rt_min) rt_min = d.clk_proc;
        if (d.clk_proc > rt_max) rt_max = d.clk_proc;
        if (share < sh_min) sh_min = share;
        if (share > sh_max) sh_max = share;
    }
    printf("\nточна сума: розмах %.6f с  (%.3f %% від %.3f с)\n",
           rt_max - rt_min, 100.0 * (rt_max - rt_min) / rt_min, rt_min);
    printf("частка sys: розмах %.2f відсоткового пункту (від %.2f до %.2f)\n",
           100.0 * (sh_max - sh_min), 100.0 * sh_min, 100.0 * sh_max);
    return 0;
}
```
```cpp
static int mode_spread(int runs, double seconds, double kfrac, double slice)
{
    runs = std::clamp(runs, 2, 64);

    double rt_min = 1e30, rt_max = -1e30, sh_min = 1e30, sh_max = -1e30;

    std::cout << "прогін   точна сума        user           sys      частка sys\n";
    for (int i = 1; i <= runs; i++) {
        snap a{}, b{};
        take(a);
        burn_mix(seconds, kfrac, slice);
        take(b);
        snap d = diff(a, b);

        double tot = d.ru_self_u + d.ru_self_s;
        double share = tot > 0.0 ? d.ru_self_s / tot : 0.0;
        std::cout << std::fixed << std::setprecision(6)
                  << "  " << std::setw(2) << i
                  << "    " << std::setw(10) << d.clk_proc
                  << "   " << std::setw(10) << d.ru_self_u
                  << "   " << std::setw(10) << d.ru_self_s
                  << "     " << std::setprecision(2) << std::setw(6) << (100.0 * share) << " %\n";

        rt_min = std::min(rt_min, d.clk_proc);
        rt_max = std::max(rt_max, d.clk_proc);
        sh_min = std::min(sh_min, share);
        sh_max = std::max(sh_max, share);
    }
    std::cout << "\nточна сума: розмах " << std::setprecision(6) << (rt_max - rt_min)
              << " с  (" << std::setprecision(3) << (100.0 * (rt_max - rt_min) / rt_min)
              << " % від " << std::setprecision(3) << rt_min << " с)\n"
              << "частка sys: розмах " << std::setprecision(2) << (100.0 * (sh_max - sh_min))
              << " відсоткового пункту (від " << (100.0 * sh_min)
              << " до " << (100.0 * sh_max) << ")\n";
    return 0;
}
```
:::

```
$ ./cpulab spread 8 1.0 0.35
прогін   точна сума        user           sys      частка sys
   1      1.000284     0.760216     0.240068      24.00 %
   2      1.000191     0.784150     0.216041      21.60 %
   3      1.000377     0.716270     0.284107      28.40 %
   4      1.000246     0.772190     0.228056      22.80 %
   5      1.000308     0.740228     0.260080      26.00 %
   6      1.000225     0.796179     0.204046      20.40 %
   7      1.000341     0.728248     0.272093      27.20 %
   8      1.000262     0.768201     0.232061      23.20 %

точна сума: розмах 0.000186 с  (0.019 % від 1.000191 с)
частка sys: розмах 8.00 відсоткового пункту (від 20.40 до 28.40)
```

Дві колонки того самого досліду розходяться на три порядки за стабільністю. Точна сума тримається в межах двох сотих відсотка — це просто те, скільки процесора програма справді зайняла, і воно майже не залежить від того, коли б'ють тики. Частка `sys` стрибає між 20.4 % і 28.4 %, хоча навантаження в усіх восьми прогонах абсолютно однакове.

Розмах не випадковий за величиною. Секунда при HZ = 250 — це 250 тиків; кожен тик — незалежна спроба з імовірністю потрапити в ядро близько 0.24. Стандартне відхилення такої оцінки:

```
σ = √(p·(1−p) / n)
  = √(0.24 · 0.76 / 250)
  = √(0.00072960)
  = 0.0270  →  2.7 відсоткового пункту
```

Вісім значень із такого розподілу лягають приблизно в ±1.5σ — тобто в смугу шириною близько восьми пунктів. Саме її і видно у виводі.

Ще одна дрібниця у цій таблиці ховає підказку. Усі частки виявилися кратними 0.4 пункту: 24.00, 21.60, 28.40, 22.80… Це не збіг — пропорція завжди дорівнює `k/n`, де `n` — повне число тиків за прогін, а знаменник 250 дає крок рівно 0.4 %. Дізнатися HZ ядра з простору користувача прямо не можна, зате за кроком розсипу його неважко вгадати; надійніше — подивитися `CONFIG_HZ` у `/boot/config-$(uname -r)`.

> 🔧 **Навіщо це.** З тієї самої формули виводиться відповідь на практичне питання «скільки треба міряти». Якщо потрібна частка `sys` із точністю ±1 пункт при `p ≈ 0.25` і HZ = 250, то `n = p(1−p)/σ² = 0.1875 / 0.0001 = 1875` тиків, тобто **7.5 секунди**; для ±0.5 пункту — уже 30 секунд. Ось чому «швидкий тест на дві секунди» дає різні відсотки щоразу, і ось чому подовження прогону лікує цю хворобу, а повторний запуск — ні. Для самої ж суми таких обмежень немає: вона точна на будь-якій довжині.

## Коротка програма: нулі, яких насправді немає

:::tabs
```c
static int mode_short(double ms)
{
    snap a, b, d;
    take(&a);
    burn_user(ms / 1000.0);
    take(&b);
    diff(&a, &b, &d);
    printf("спалено ~%.0f мс самого лише власного коду\n", ms);
    report(&d);
    return 0;
}
```
```cpp
static int mode_short(double ms)
{
    snap a{}, b{};
    take(a);
    burn_user(ms / 1000.0);
    take(b);
    snap d = diff(a, b);
    std::cout << std::fixed << std::setprecision(0)
              << "спалено ~" << ms << " мс самого лише власного коду\n";
    report(d);
    return 0;
}
```
:::

```
$ ./cpulab short 3
спалено ~3 мс самого лише власного коду
  точна сума (лічильник планувальника)
    clock_gettime(PROCESS_CPUTIME)      0.003104 с
    clock_gettime(THREAD_CPUTIME)       0.003102 с
    /proc/self/schedstat  [0]           0.001487 с
    /proc/thread-self/schedstat [0]     0.001487 с
  поділ на режими (вибірка, зшита з точною сумою)
    getrusage(RUSAGE_SELF)     user   0.003098  sys   0.000000  сума    0.003098
    getrusage(RUSAGE_THREAD)   user   0.003096  sys   0.000000  сума    0.003096
    /proc/self/stat 14-15      user       0.00  sys       0.00  сума        0.00   (крок 10 мс)
  сума rusage − точна сума  -0.000006 с
  частка sys за rusage      0.00 %
```

Три мілісекунди — це менше за один тик при будь-якому HZ, тож тикові лічильники лишилися рівно на місці. І ось як на це відповідають різні інтерфейси.

`/proc/self/stat` показує чесні нулі, але з несподіваної причини. Не тому, що ядро не має числа, — воно має його з наносекундною точністю. А тому, що на виході число ділиться на USER_HZ і зрізається: три мілісекунди — це нуль цілих тиків. Усе, що коротше за 10 мс, у цьому файлі є нулем назавжди, і саме тому `top` однаково показує нуль процесу, що спожив 1 мс, і процесу, що спожив 9 мс.

`getrusage()` натомість показує **весь** час як користувацький. Тут працює явне правило ядра: коли жоден тик не потрапив в один із двох лічильників, увесь виміряний час оголошується користувацьким. У сирці функції, що зшиває вибірку з точною сумою, це записано прямим текстом — «якщо `stime` або `utime` дорівнює нулю, вважаємо весь час користувацьким», з поясненням, що щойно задача набере тиків, механізм монотонності підтягне числа до спостереженої пропорції. Наслідок для практики різкий: **нульовий `sys` у короткої програми не означає, що вона не заходила в ядро.** Вона могла провести там більшість свого життя — просто нікому було це побачити, і правило за замовчуванням віддало все в `user`.

Тут же видно й найбільше в цій лабораторії відставання `schedstat` — 1.5 мс замість 3.1. Задача проробила три мілісекунди суцільним рахунком, її ніхто не витісняв, тик не встиг ударити двічі, тому сире поле оновлювалося востаннє посеред роботи. Різниця плаває від нуля до тику й залежить лише від того, коли востаннє трапилася подія планувальника.

І остання дрібниця: «сума rusage − точна сума» вийшла від'ємною на шість мікросекунд. Це не збій обліку, а плата за самі вимірювання: `getrusage()` читається раніше за `clock_gettime()`, і між ними встигає минути час на два системні виклики. На трьох тисячних секунди така дрібниця вже помітна.

## Резонанс із тиком

Уся статистика попереднього розділу трималася на одному припущенні: тик не пов'язаний із тим, що робить задача. Це припущення легко зламати — досить зробити період чергування рівним періодові тику.

:::tabs
```c
/* Ті самі умови, різна довжина скибки. Одне зі значень збігається з періодом
   тику ядра — і саме на ньому поділ перестає бути схожим на сусідів. */
static int mode_phase(double seconds, double kfrac)
{
    static const double slices_ms[] = { 0.2, 1.0, 2.0, 4.0, 8.0, 10.0 };

    printf("скибка    частка sys    точна сума\n");
    for (size_t i = 0; i < sizeof slices_ms / sizeof slices_ms[0]; i++) {
        snap a, b, d;
        take(&a);
        burn_mix(seconds, kfrac, slices_ms[i] / 1000.0);
        take(&b);
        diff(&a, &b, &d);

        double tot = d.ru_self_u + d.ru_self_s;
        printf("%5.1f мс     %6.2f %%     %10.6f\n",
               slices_ms[i], tot > 0.0 ? 100.0 * d.ru_self_s / tot : 0.0, d.clk_proc);
    }
    return 0;
}
```
```cpp
// Ті самі умови, різна довжина скибки. Одне зі значень збігається з періодом
// тику ядра — і саме на ньому поділ перестає бути схожим на сусідів.
static int mode_phase(double seconds, double kfrac)
{
    constexpr std::array<double, 6> slices_ms = { 0.2, 1.0, 2.0, 4.0, 8.0, 10.0 };

    std::cout << "скибка    частка sys    точна сума\n";
    for (double slice : slices_ms) {
        snap a{}, b{};
        take(a);
        burn_mix(seconds, kfrac, slice / 1000.0);
        take(b);
        snap d = diff(a, b);

        double tot = d.ru_self_u + d.ru_self_s;
        double share = tot > 0.0 ? 100.0 * d.ru_self_s / tot : 0.0;
        std::cout << std::fixed << std::setprecision(1) << std::setw(5) << slice << " мс     "
                  << std::setprecision(2) << std::setw(6) << share << " %     "
                  << std::setprecision(6) << std::setw(10) << d.clk_proc << "\n";
    }
    return 0;
}
```
:::

```
$ ./cpulab phase 1.0 0.35
скибка    частка sys    точна сума
  0.2 мс      24.31 %       1.000271
  1.0 мс      24.06 %       1.000254
  2.0 мс      23.94 %       1.000262
  4.0 мс      11.72 %       1.000248
  8.0 мс      23.81 %       1.000259
 10.0 мс      24.12 %       1.000255
```

П'ять рядків із шести кажуть те саме — близько 24 %, з розкидом на пів пункта, як і належить вибірці. Той, що лишився, — четвертий, зі скибкою 4 мс, — випадає удвічі. Це рівно період тику при HZ = 250: цикл програми й цикл опитування зчепилися фазами, і кожен тик почав заставати задачу приблизно в одному й тому самому місці її циклу.

На твоїй машині картина буде інша: при HZ = 1000 випаде рядок 1.0 мс, при HZ = 100 — рядок 10 мс, а замість 11.72 % може вийти 38 % або 3 % залежно від того, у яку фазу потрапило зчеплення. Незмінне одне: на одному зі значень поділ перестає узгоджуватися із сусідами, а точна сума в тій самій колонці не ворухнеться.

Це найважливіший рядок усієї лабораторії. Похибка вибірки, яку ми рахували коренем, спадає з часом лише доти, доки спроби незалежні. Щойно незалежність зникла, довший прогін нічого не лікує — програма просто довше й певніше повідомляє неправду. А потрапити в цю пастку легко без жодного наміру: обробник аудіо, ігровий цикл, опитувач із фіксованим періодом, таймер на круглій частоті — усе це кандидати на зчеплення з тиком.

## Процес і потік — одна тека, різні відповіді

:::tabs
```c
struct tharg { double seconds, kfrac, slice, own; };

static void *thread_body(void *p)
{
    struct tharg *a = p;
    burn_mix(a->seconds, a->kfrac, a->slice);
    a->own = cpu_clock(CLOCK_THREAD_CPUTIME_ID);
    return NULL;
}

static int mode_threads(int n, double seconds, double kfrac)
{
    if (n < 1 || n > 16) n = 4;

    pthread_t th[16];
    struct tharg arg[16];
    snap a, b, d;

    take(&a);
    for (int i = 0; i < n; i++) {
        arg[i].seconds = seconds;
        arg[i].kfrac   = kfrac;
        arg[i].slice   = 0.001;
        arg[i].own     = 0.0;
        if (pthread_create(&th[i], NULL, thread_body, &arg[i]) != 0) {
            perror("pthread_create");
            return 1;
        }
    }

    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        pthread_join(th[i], NULL);
        printf("потік %d: CLOCK_THREAD_CPUTIME_ID   %9.4f с\n", i, arg[i].own);
        sum += arg[i].own;
    }
    take(&b);
    diff(&a, &b, &d);

    printf("\nсума по потоках                     %9.4f с\n", sum);
    printf("CLOCK_PROCESS_CPUTIME_ID (приріст)  %9.4f с\n", d.clk_proc);
    if (d.stat_ok)
        printf("/proc/self/stat 14-15    (приріст)  %9.2f с   ← теж уся група\n",
               d.stat_u + d.stat_s);
    if (d.sched_ok)
        printf("/proc/self/schedstat     (приріст)  %9.4f с   ← лише головний потік\n",
               d.sched_grp);
    printf("CLOCK_THREAD_CPUTIME_ID  (приріст)  %9.4f с   ← теж лише головний\n",
           d.clk_thr);
    return 0;
}
```
```cpp
struct tharg {
    double seconds = 0.0;
    double kfrac = 0.0;
    double slice = 0.001;
    double own = 0.0;
};

static int mode_threads(int n, double seconds, double kfrac)
{
    if (n < 1 || n > 16) n = 4;

    std::vector<tharg> args(n);
    std::vector<std::thread> threads;
    threads.reserve(n);

    snap a{}, b{};
    take(a);

    for (int i = 0; i < n; i++) {
        args[i].seconds = seconds;
        args[i].kfrac   = kfrac;
        args[i].slice   = 0.001;
        args[i].own     = 0.0;

        threads.emplace_back([&arg = args[i]]() {
            burn_mix(arg.seconds, arg.kfrac, arg.slice);
            arg.own = cpu_clock(CLOCK_THREAD_CPUTIME_ID);
        });
    }

    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        threads[i].join();
        std::cout << std::fixed << std::setprecision(4)
                  << "потік " << i << ": CLOCK_THREAD_CPUTIME_ID   "
                  << std::setw(9) << args[i].own << " с\n";
        sum += args[i].own;
    }

    take(b);
    snap d = diff(a, b);

    std::cout << std::fixed << std::setprecision(4)
              << "\nсума по потоках                     " << std::setw(9) << sum << " с\n"
              << "CLOCK_PROCESS_CPUTIME_ID (приріст)  " << std::setw(9) << d.clk_proc << " с\n";
    if (d.stat_ok) {
        std::cout << "/proc/self/stat 14-15    (приріст)  " << std::setprecision(2)
                  << std::setw(9) << (d.stat_u + d.stat_s) << " с   ← теж уся група\n";
    }
    if (d.sched_ok) {
        std::cout << "/proc/self/schedstat     (приріст)  " << std::setprecision(4)
                  << std::setw(9) << d.sched_grp << " с   ← лише головний потік\n";
    }
    std::cout << "CLOCK_THREAD_CPUTIME_ID  (приріст)  " << std::setprecision(4)
              << std::setw(9) << d.clk_thr << " с   ← теж лише головний\n";
    return 0;
}
```
:::

```
$ ./cpulab threads 4 1.0 0.35
потік 0: CLOCK_THREAD_CPUTIME_ID      1.0009 с
потік 1: CLOCK_THREAD_CPUTIME_ID      1.0011 с
потік 2: CLOCK_THREAD_CPUTIME_ID      1.0008 с
потік 3: CLOCK_THREAD_CPUTIME_ID      1.0010 с

сума по потоках                        4.0038 с
CLOCK_PROCESS_CPUTIME_ID (приріст)     4.0043 с
/proc/self/stat 14-15    (приріст)        4.00 с   ← теж уся група
/proc/self/schedstat     (приріст)     0.0004 с   ← лише головний потік
CLOCK_THREAD_CPUTIME_ID  (приріст)     0.0004 с   ← теж лише головний
```

Головний потік тут не робить нічого, крім створення інших і очікування на них, — і саме тому дослід виходить показовим. Чотири секунди процесорного часу справді спожито; питання лише в тому, хто з інтерфейсів про це знає.

`CLOCK_PROCESS_CPUTIME_ID` і поля 14–15 у `/proc/self/stat` кажуть «чотири»: обидва підсумовують усю групу потоків, включно з тими, що вже завершилися ([потоки як задачі](book:unix-linux/threads-as-tasks) — потік для ядра є звичайною задачею, а «процес» — це група задач зі спільними ресурсами). `CLOCK_THREAD_CPUTIME_ID` каже «нуль з дрібкою», і це правильна відповідь на інше питання — про потік, що його поставив.

А от `/proc/self/schedstat` — пастка. Він лежить у тій самій теці, що й `stat`, читається так само, віддає наносекунди — і при цьому показує **лише час головного потоку**, бо це поле конкретної задачі, а тека `/proc/self` веде саме до задачі-лідера групи. Ніякого підсумовування там не відбувається й ніколи не відбувалося. Для власного потоку правильний шлях — `/proc/thread-self/schedstat`; сумарного по групі не існує взагалі, і в багатопотоковій програмі це число доводиться збирати самому, обходячи `/proc/<pid>/task/`.

Два сусідні файли в одній теці, однаковий вигляд, різне охоплення — це те місце, де ламаються саморобні монітори. Помилка тиха: на одному потоці все сходиться, і розбіжність з'являється лише тоді, коли програма стає багатопотоковою.

## Як зібрати й запустити

:::tabs
```c
int main(int argc, char **argv)
{
    const char *mode = argc > 1 ? argv[1] : "mix";
    double a2 = argc > 2 ? atof(argv[2]) : 0.0;
    double a3 = argc > 3 ? atof(argv[3]) : 0.0;
    double a4 = argc > 4 ? atof(argv[4]) : 0.0;

    setvbuf(stdout, NULL, _IOLBF, 0);

    if (!strcmp(mode, "mix"))
        return mode_mix(a2 > 0 ? a2 : 3.0, argc > 3 ? a3 : 0.35,
                        (a4 > 0 ? a4 : 1.0) / 1000.0);
    if (!strcmp(mode, "spread"))
        return mode_spread(argc > 2 ? (int)a2 : 8, a3 > 0 ? a3 : 1.0,
                           argc > 4 ? a4 : 0.35, 0.001);
    if (!strcmp(mode, "short"))
        return mode_short(a2 > 0 ? a2 : 3.0);
    if (!strcmp(mode, "phase"))
        return mode_phase(a2 > 0 ? a2 : 1.0, argc > 3 ? a3 : 0.35);
    if (!strcmp(mode, "threads"))
        return mode_threads(argc > 2 ? (int)a2 : 4, a3 > 0 ? a3 : 1.0,
                            argc > 4 ? a4 : 0.35);

    fprintf(stderr,
        "usage: cpulab mix     [с] [частка] [скибка_мс]\n"
        "              spread  [прогонів] [с] [частка]\n"
        "              short   [мс]\n"
        "              phase   [с] [частка]\n"
        "              threads [потоків] [с] [частка]\n");
    return 2;
}
```
```cpp
int main(int argc, char** argv)
{
    std::string_view mode = argc > 1 ? argv[1] : "mix";
    auto parse_double = [](const char* str) {
        try { return std::stod(str); } catch (...) { return 0.0; }
    };

    double a2 = argc > 2 ? parse_double(argv[2]) : 0.0;
    double a3 = argc > 3 ? parse_double(argv[3]) : 0.0;
    double a4 = argc > 4 ? parse_double(argv[4]) : 0.0;

    std::cout << std::unitbuf;

    if (mode == "mix")
        return mode_mix(a2 > 0 ? a2 : 3.0, argc > 3 ? a3 : 0.35,
                        (a4 > 0 ? a4 : 1.0) / 1000.0);
    if (mode == "spread")
        return mode_spread(argc > 2 ? static_cast<int>(a2) : 8, a3 > 0 ? a3 : 1.0,
                            argc > 4 ? a4 : 0.35, 0.001);
    if (mode == "short")
        return mode_short(a2 > 0 ? a2 : 3.0);
    if (mode == "phase")
        return mode_phase(a2 > 0 ? a2 : 1.0, argc > 3 ? a3 : 0.35);
    if (mode == "threads")
        return mode_threads(argc > 2 ? static_cast<int>(a2) : 4, a3 > 0 ? a3 : 1.0,
                            argc > 4 ? a4 : 0.35);

    std::cerr << "usage: cpulab mix     [с] [частка] [скибка_мс]\n"
              << "              spread  [прогонів] [с] [частка]\n"
              << "              short   [мс]\n"
              << "              phase   [с] [частка]\n"
              << "              threads [потоків] [с] [частка]\n";
    return 2;
}
```
:::

```sh
cc -O2 -Wall -Wextra -pthread -o cpulab cpulab.c

./cpulab mix 3.0 0.35 1.0
./cpulab spread 8 1.0 0.35
./cpulab short 3
./cpulab phase 1.0 0.35
./cpulab threads 4 1.0 0.35
```

Щоб числа повторювалися від прогону до прогону, варто прибити програму до одного ядра й прибрати з нього конкурентів ([прив'язка задач до ядер](book:unix-linux/cpu-affinity) — маска дозволених ядер, з якою планувальник більше нікуди задачу не переносить):

```sh
taskset -c 3 ./cpulab spread 8 1.0 0.35
```

Перевірити, що системний час спалюють справжні виклики, а не щось стороннє, найпростіше збоку:

```sh
strace -c -f ./cpulab mix 1.0 0.35 1.0
#  % time     seconds  usecs/call     calls    syscall
#  ------ ----------- ----------- ---------  ----------
#   99.31    0.041182           1     21336    getppid
```

Тут важлива лише присутність рядка, а не його числа: під `strace` кожен виклик коштує двох зупинок трасувальника, тож викликів за ту саму секунду виходить у десятки разів менше, і жодне число з цієї таблиці не можна порівнювати з тим, що друкує сама лабораторія ([трасування системних викликів](book:unix-linux/syscall-tracing) — перехоплення викликів збоку, зі спиненням задачі на вході й виході). Якщо ж `getppid` у таблиці немає взагалі — значить, libc чи vDSO десь перехопили виклик, і всі числа з режиму `mix` треба викинути.

## Що це коштує

```
одне читання (x86-64, тепла тека /proc, порядок величини):
  clock_gettime(CLOCK_MONOTONIC)           ~20 нс    vDSO, у ядро не входить
  clock_gettime(CLOCK_THREAD_CPUTIME_ID)   ~0.6 мкс  системний виклик
  clock_gettime(CLOCK_PROCESS_CPUTIME_ID)  ~0.6 мкс  + прохід списком потоків
  getrusage(RUSAGE_THREAD)                 ~0.7 мкс  системний виклик
  getrusage(RUSAGE_SELF)                   ~0.7 мкс  + прохід списком потоків
  /proc/self/stat                          ~8 мкс    open + read + close + розбір
  /proc/self/schedstat                     ~6 мкс    те саме, коротший файл

похибка ПОДІЛУ (сума точна завжди):  σ = √(p·(1−p)/n),  n ≈ rtime · HZ
  p = 0.24, rtime =  1 с, HZ = 250  →  σ = 2.70 в. п.
  p = 0.24, rtime = 60 с, HZ = 250  →  σ = 0.35 в. п.
  зчеплення періоду задачі з періодом тику →  σ не спадає взагалі
```

Два рядки з проходом списком потоків — не дрібниця. У програмі на п'ятсот потоків кожне читання «часу процесу» обходить усі п'ятсот структур під замком; вимірювальний цикл, що робить це щомілісекунди, сам стає помітним навантаженням. Для потоку, який міряє **себе**, правильний вибір — `CLOCK_THREAD_CPUTIME_ID` або `RUSAGE_THREAD`: там обходити нема чого.

## Пастки

**Спалювати `sys` через `clock_gettime(CLOCK_MONOTONIC)` чи `gettimeofday()`.** Ці виклики обслуговує vDSO, і в ядро вони не заходять; цикл із них дає сто відсотків `user`. Той самий підступ псує й вимірювальний код: якщо міряти час усередині гарячого циклу «дешевим» годинником, вибір годинника вирішує, у яку графу піде його ціна.

**Зашивати 100 замість `sysconf(_SC_CLK_TCK)`.** USER_HZ дорівнює 100 на всіх поширених збірках, але це ABI, а не закон; на екзотичній архітектурі зашита сотня дає числа, менші за реальність у кілька разів. Те саме значення ядро кладе процесові на стек при запуску записом `AT_CLKTCK` ([допоміжний вектор](book:unix-linux/auxiliary-vector) — таблиця «ключ → значення», яку ядро передає програмі поверх аргументів і середовища).

**Приймати нуль у `/proc` за відсутність часу.** Крок цього джерела — 10 мс. Усе, що коротше, є нулем; різниці між 1 мс і 9 мс там не буде ніколи. Для коротких вимірів існують `getrusage()` (мікросекунди) і `clock_gettime()` (наносекунди).

**Приймати нульовий `sys` короткої програми за «вона не заходила в ядро».** Правило ядра прямо каже: коли жоден тик не потрапив в один із лічильників, увесь час зараховується як користувацький. Нуль там означає «не було кому побачити», а не «не було чого бачити».

**Рахувати різницю двох зрізаних чисел.** `/proc/<pid>/stat` віддає цілі тики, тож приріст між двома читаннями сам зрізаний і може схибити на цілий тик у кожен бік. На секундних інтервалах це шум у відсоток; на стомілісекундних — половина відповіді.

**Плутати `/proc/self/stat` із `/proc/self/schedstat`.** Перший — уся група потоків, другий — лише задача-лідер. Помилка мовчазна доти, доки програма однопотокова.

**Вважати відсутність `schedstat` нулем.** Файл існує лише в ядрі, зібраному з `CONFIG_SCHED_INFO` (його вмикає `CONFIG_SCHEDSTATS` або облік затримок). Немає файлу — `open` дає `ENOENT`, і код мусить це відрізняти: «не рахують» і «не витратив» — різні відповіді, а мовчазна підстановка нуля перетворює одну на другу.

**Чекати, що `schedstat` збіжиться з `clock_gettime` до наносекунди.** Перший читає поле як є, другий спершу просить планувальник дописати незараховане. Різниця від нуля до тику — норма, а не збій.

**Забути `volatile` або зібрати з `-O0`.** Без `volatile`-приймача оптимізатор має право викинути весь цикл `xorshift`, і замість спалювання вийде миттєвий вихід із нулями. Із `-O0` цикл лишиться, але співвідношення ціни арифметики й ціни системного виклику зміниться в рази, і замовлена частка розійдеться з отриманою ще сильніше.

**Читати точну суму як міру виконаної роботи.** `sum_exec_runtime` рахує **секунди зайнятості процесора**, а не інструкції. Та сама програма на зниженій частоті витратить більше секунд, зробивши те саме; на іншому ядрі з холодним кешем — теж. Порівнювати оптимізації за цим числом можна лише при зафіксованій частоті й прив'язаному ядрі, а питання «де саме витрачено» взагалі не до обліку — воно до [підсистеми perf](book:unix-linux/perf-events), яка збирає вибірку зі стеками замість двох сумарних граф.

**Забути, що вимірювання коштує саме `sys`.** Кожне читання `getrusage` чи `CLOCK_*_CPUTIME_ID` — це системний виклик, кожне читання `/proc` — три. У циклі, що знімає покази щомілісекунди, вимірювач стає помітною часткою того, що він міряє, — і, на відміну від решти навантаження, ця частка цілком лягає в графу `sys`.
