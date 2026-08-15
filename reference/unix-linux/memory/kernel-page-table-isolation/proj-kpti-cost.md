# ⚙️ Стенд: скільки перетин межі коштує саме на цій машині

Будь-який відсоток, який можна прочитати про ціну ізоляції таблиць, стосується чужої машини з чужим ядром і чужим набором пом'якшень. Ця програма на C дає власне число: вона зважує найдешевший системний виклик у тактах і наносекундах, ставить поруч виклик того самого сенсу, що межі не перетинає взагалі, а тоді знімає криву — як та сама ціна росте, коли між викликами програма встигає розворушити пам'ять. Дві години зі стендом варті більше за будь-який чужий звіт: вони відповідають на питання, якого той поставити не міг, — скільки платить **ваше** навантаження.

## Що саме кладемо на терези

Зважити «системний виклик» узагалі неможливо: `read()` із гігабайтом і `read()` із одним байтом коштують геть різного, і майже вся різниця — це робота, а не межа. Тому за вантаж беруть виклик, у якому роботи немає зовсім.

Такий є: `getppid()`. Ядро віддає число, яке вже лежить у структурі задачі, — ні блокувань, ні звернень до пристроїв, ні копіювання буферів. Усе, що лишається в замірі, — це сам перехід: зміна рівня привілею, вхідний код, [два записи в `CR3`](book:unix-linux/syscall-mechanics), повернення. Кличемо його не звичайною функцією libc, а через `syscall(SYS_getppid)`, щоб між нами й ядром не стояла обгортка, яка колись уміла кешувати відповідь: `getpid()` у glibc кешувався роками, і саме такі дрібниці перетворюють вимір на самообман.

Друга пара терезів цікавіша. Візьмімо **один і той самий сенс, добутий двома шляхами**. `clock_gettime(CLOCK_MONOTONIC, …)` у звичайній програмі виконується цілком у просторі процесу: ядро відображає в кожен процес крихітну бібліотеку [vDSO](book:unix-linux/vdso), і код цієї бібліотеки читає поточний час зі спільної сторінки, яку ядро для нього оновлює. Межу тут не перетинають узагалі. Той самий `clock_gettime` можна змусити піти справжнім системним викликом — `syscall(SYS_clock_gettime, …)` обходить vDSO і йде в ядро. Робота обох шляхів однакова з точністю до кількох інструкцій; уся різниця в числах — це плата за межу, і жодного окремого «фонового» виміру для неї не потрібно.

Отже, три проби: `getppid` (межа без роботи), `clock_gettime` через vDSO (робота без межі) і `clock_gettime` крізь межу (робота плюс межа).

## Лінійка, яка сама не бреше

Міряти будемо лічильником міток часу процесора, `RDTSC`. Дві його властивості треба знати наперед, бо кожна з них уміє зіпсувати результат мовчки.

Перша: **`RDTSC` не є бар'єром**. Це звичайна інструкція, і [позачергове ядро процесора](book:programming/out-of-order-execution) має повне право виконати її раніше або пізніше за сусідні — тобто зняти позначку часу тоді, коли вимірюваний код ще не почався або вже закінчився. Огорожа будується так: початок вікна затискають між двома `LFENCE` (перший чекає, поки завершиться все попереднє, другий не пускає наступне поперед позначки), а кінець беруть інструкцією `RDTSCP`, яка сама чекає завершення попереднього, і закривають ще одним `LFENCE`. Огорожа коштує десятки тактів — і саме тому ніколи не міряють один виклик: вікно ставлять навколо десятків тисяч ітерацій, і ціна огорожі розчиняється в діленні.

Друга властивість підступніша. **Такт `RDTSC` — це не такт ядра процесора.** На всіх сучасних машинах лічильник цокає зі сталою частотою незалежно від того, на якій частоті зараз працює ядро й чи працює воно взагалі (прапорці `constant_tsc` і `nonstop_tsc` у `/proc/cpuinfo` саме про це). Частота ця близька до базової, але дорівнює їй не завжди й не зобов'язана. Звідси найпоширеніша помилка всіх саморобних стендів: узяти число з рядка `model name` у `/proc/cpuinfo` і поділити на нього такти. Результат виглядатиме як наносекунди й ними не буде.

Єдиний надійний спосіб — звірити лічильник із годинником ядра: зняти `RDTSC` і `CLOCK_MONOTONIC` на початку й у кінці двохсотмілісекундної паузи й поділити одне на друге. Двісті мілісекунд дають похибку калібрування десь у тисячні частки відсотка — на порядки менше, ніж усе інше в цьому замірі. Про самі [годинники ядра й джерела часу](book:unix-linux/kernel-timekeeping) є окрема розмова; тут вистачить того, що `CLOCK_MONOTONIC` іде рівно й не стрибає, коли правлять настінний час.

## Спершу дізнатися, у якому режимі міряємо

Число без режиму нічого не варте, а режим машина повідомляє сама.

```sh
$ cat /sys/devices/system/cpu/vulnerabilities/meltdown
Mitigation: PTI

$ tr ' ' '\n' < /proc/cpuinfo | grep -xE 'pti|pcid|invpcid|constant_tsc' | sort -u
constant_tsc
invpcid
pcid
pti
```

Перший файл — частина спільного інтерфейсу, у якому ядро звітує про кожну відому апаратну ваду через [псевдофайлову систему](book:unix-linux/pseudo-filesystems); там буває `Not affected` (процесор вадою не вражений), `Mitigation: PTI` (ізоляція працює) і `Vulnerable` (вражений, але захист вимкнено). Прапорець `pti` у переліку можливостей процесора ядро підставляє саме тоді, коли ізоляція справді ввімкнена, а `pcid` та `invpcid` кажуть, чи є [мітки адресних просторів](book:programming/tlb), без яких кожен перетин межі перетворюється на повне скидання кешу перекладів.

`Not affected` — не поразка стенда, а корисний контрольний випадок: на такій машині крива покаже чистий тиск на TLB без домішки ізоляції, і її варто зберегти для порівняння.

Програма читає все це сама й друкує в шапці звіту. Заміри без шапки нікуди не годяться: за тиждень ви вже не згадаєте, у якому режимі знято ці числа.

## Тиск на TLB: чому ланцюг, а не пробіг масивом

Тепер найважливіше в конструкції стенда — те, чим саме «розворушувати пам'ять» між викликами.

Спокуса просто пробігтися буфером від початку до кінця хибна. Суцільний пробіг чіпає кожен байт, тобто тисне передусім на кеш даних; апаратне випереджувальне читання при цьому вгадує наступний крок наперед і майже все встигає підвезти. А нас цікавить не кеш даних, а **кеш перекладів**: саме порожній TLB робить перетин межі дорогим після того, як ізоляція позбавила ядерні відображення глобальності.

Отже, чіпати треба по одному байту на сторінку — тоді кожен дотик вимагає окремого перекладу, а даних читається мізер. І порядок сторінок має бути **непередбачуваним**, інакше апаратура здогадається про наступну сторінку раніше, ніж ми до неї дійдемо.

Обидві вимоги задовольняє перемішаний однозв'язний ланцюг: у першому слові кожної сторінки лежить зсув наступної, а порядок сторінок перетасовано. Перехід ланцюгом — це послідовність залежних читань, кожне за адресою, яку щойно принесло попереднє. Їх не можна ні вгадати, ні виконати наперед, ні перекрити одне одним. Розмір буфера й задає [робочу множину](book:programming/working-set) — те, скільки різних перекладів мусить одночасно жити в TLB.

Між двома викликами проходимо фіксовану кількість ланок — шістдесят чотири, — а не весь буфер: інакше велика розгортка тривала б годинами. Позиція в ланцюгу зберігається між ітераціями, тож за десятки тисяч ітерацій програма багато разів обійде навіть найбільший буфер, і в сталому режимі тиск на TLB задає саме розмір буфера.

## Що з чого віднімаємо

Ціну виклику саму по собі вікно не покаже: усередині нього є ще й міряльний цикл, і ті самі шістдесят чотири кроки ланцюгом. Тому вікон завжди два — з викликом і без нього, у тих самих умовах, — а різниця дає шукане.

![Два вікна заміру: із викликом і без нього; різниця дає ціну одного перетину](/reference/unix-linux/memory/kernel-page-table-isolation/img/bench-window.svg)

*Перехід ланцюгом однаковий в обох вікнах і при відніманні зникає. Лишається те, що додав виклик, — разом із тим, як він зіпсував наступні звернення до пам'яті.*

Останнє уточнення важливе, і воно не вада, а суть. Виклик, вирушивши в ядро, витісняє з TLB частину користувацьких перекладів — і наступний перехід ланцюгом стає повільнішим. Різниця вікон припише цей додатковий час викликові, і правильно зробить: **ціна перетину межі — це не лише такти, проведені всередині переходу, а й те, що перехід залишив по собі**. Саме тому ціна залежить від робочої множини, хоча в самому переході ніщо про робочу множину не знає.

За підсумок беремо **мінімум**, а не середнє. Усе, що трапляється під час заміру — переривання, витіснення іншим потоком, міграція, — тільки додає такти й ніколи не віднімає. Найменш потурбований прогін і є найближчим до правди. Це не примха стенда, а обов'язковий мінімум будь-якого [мікробенчмарку](book:programming/microbenchmarking).

## Програма

Три частини нижче складаються в один файл `bordercost.c` у наведеному порядку.

**Частина перша — лінійка та калібрування.**

:::tabs
```c
/* bordercost.c — ціна перетину межі ядра на цій машині.
 *
 *   cc -O2 -Wall -Wextra -o bordercost bordercost.c
 *   taskset -c 3 ./bordercost 3
 *
 * Лише x86-64 (RDTSC/RDTSCP). Прав root не потребує. */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <x86intrin.h>

#define PAGE       4096u
#define STEPS        64      /* сторінок, яких торкаємося між двома викликами */
#define MAX_KIB  262144u     /* 256 МіБ — стеля розгортки */

/* RDTSC бар'єром не є: процесор має право виконати її раніше або пізніше
   за сусідні інструкції. Тому початок вікна затискаємо між двома LFENCE,
   а кінець беремо RDTSCP (вона сама чекає завершення попереднього)
   і закриваємо ще одним LFENCE, щоб наступне не заповзло всередину. */
static inline uint64_t tsc_open(void)
{
    _mm_lfence();
    uint64_t t = __rdtsc();
    _mm_lfence();
    return t;
}

static inline uint64_t tsc_close(void)
{
    unsigned aux;
    uint64_t t = __rdtscp(&aux);
    _mm_lfence();
    return t;
}

/* Скільки тактів TSC припадає на секунду. Питати про це рядок model name
   у /proc/cpuinfo не можна: TSC цокає зі сталою частотою незалежно від
   того, на якій частоті зараз працює ядро процесора. Єдиний надійний
   спосіб — звірити лічильник із годинником ядра. */
static double tsc_hz(void)
{
    struct timespec a, b, nap = { 0, 200 * 1000 * 1000 };   /* 200 мс */
    uint64_t c0, c1;
    double ns;

    clock_gettime(CLOCK_MONOTONIC, &a);
    c0 = tsc_open();
    while (nanosleep(&nap, &nap) == -1 && errno == EINTR)
        ;
    c1 = tsc_close();
    clock_gettime(CLOCK_MONOTONIC, &b);

    ns = (double)(b.tv_sec - a.tv_sec) * 1e9
       + (double)(b.tv_nsec - a.tv_nsec);
    return (double)(c1 - c0) * 1e9 / ns;
}
```
```cpp
// bordercost.cpp — ціна перетину межі ядра на цій машині (C++20).
//
//   g++ -O2 -Wall -Wextra -std=c++20 -o bordercost bordercost.cpp
//   taskset -c 3 ./bordercost 3

#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <numeric>
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <ctime>
#include <unistd.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <x86intrin.h>

constexpr std::size_t PAGE = 4096;
constexpr int STEPS = 64;
constexpr std::size_t MAX_KIB = 262144;

static inline uint64_t tsc_open()
{
    _mm_lfence();
    uint64_t t = __rdtsc();
    _mm_lfence();
    return t;
}

static inline uint64_t tsc_close()
{
    unsigned aux;
    uint64_t t = __rdtscp(&aux);
    _mm_lfence();
    return t;
}

static double tsc_hz()
{
    struct timespec a{}, b{}, nap{ 0, 200 * 1000 * 1000 };
    clock_gettime(CLOCK_MONOTONIC, &a);
    uint64_t c0 = tsc_open();
    while (nanosleep(&nap, &nap) == -1 && errno == EINTR)
        ;
    uint64_t c1 = tsc_close();
    clock_gettime(CLOCK_MONOTONIC, &b);

    double ns = static_cast<double>(b.tv_sec - a.tv_sec) * 1e9
              + static_cast<double>(b.tv_nsec - a.tv_nsec);
    return static_cast<double>(c1 - c0) * 1e9 / ns;
}
```
:::

**Частина друга — проби, ланцюг і міряльне вікно.**

:::tabs
```c
static volatile uint64_t sink;      /* запис у volatile викинути не можна */

/* Порожня проба — це тло: ціна самого циклу й переходу ланцюгом. */
static void probe_idle(void) { }

/* Найдешевший системний виклик, який тільки є: ядро віддає число,
   що вже лежить у структурі задачі. Кличемо через syscall(), щоб між
   нами й ядром не стояла обгортка libc, здатна закешувати відповідь. */
static void probe_getppid(void)
{
    sink += (uint64_t)syscall(SYS_getppid);
}

/* Той самий сенс двома шляхами. Перший бере час із vDSO і межі не
   перетинає взагалі; другий іде справжнім системним викликом. */
static void probe_vdso(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    sink += (uint64_t)ts.tv_nsec;
}

static void probe_crossing(void)
{
    struct timespec ts;
    syscall(SYS_clock_gettime, CLOCK_MONOTONIC, &ts);
    sink += (uint64_t)ts.tv_nsec;
}

static uint32_t xs32(uint32_t *s)
{
    uint32_t x = *s;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return *s = x;
}

/* Розкладаємо сторінки буфера в перемішаний однозв'язний ланцюг: у першому
   слові кожної сторінки лежить зсув наступної. Перехід ланцюгом чіпає рівно
   одну лінію кешу на сторінку — тобто тисне на TLB, а не на кеш даних, —
   і порядок сторінок випадковий, тож наступний крок не вгадується наперед.
   Зсуви тримаємо в uint32_t: до 4 ГіБ вистачає із запасом. */
static void chain(uint8_t *buf, size_t pages)
{
    uint32_t *perm;
    uint32_t seed = 0x9e3779b9u;
    size_t i;

    if (!pages) return;                        /* інакше pages - 1 переповниться */
    perm = malloc(pages * sizeof *perm);
    if (!perm) { perror("malloc"); exit(1); }
    for (i = 0; i < pages; i++)
        perm[i] = (uint32_t)i;
    for (i = pages - 1; i > 0; i--) {          /* тасування Фішера — Єйтса */
        size_t j = xs32(&seed) % (i + 1);
        uint32_t t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }
    for (i = 0; i < pages; i++) {
        uint32_t here = perm[i] * PAGE;
        uint32_t next = perm[(i + 1) % pages] * PAGE;
        memcpy(buf + here, &next, sizeof next);
    }
    free(perm);
}

static uint64_t window(void (*fn)(void), size_t iters, uint8_t *buf, size_t pages)
{
    uint32_t off = 0;
    uint64_t t0, t1;
    size_t i;
    int s;

    /* Компілятор не має знати, яка саме функція в руках: інакше він
       підставить прямий виклик, а порожню пробу викине зовсім —
       і віднімати стане нічого. Рядок асемблера без жодної інструкції
       переконує його, що покажчик побував у невідомому коді. */
    __asm__ __volatile__("" : "+r"(fn));

    t0 = tsc_open();
    for (i = 0; i < iters; i++) {
        if (pages) {
            for (s = 0; s < STEPS; s++)
                memcpy(&off, buf + off, sizeof off);
            sink += off;
        }
        fn();
    }
    t1 = tsc_close();
    return t1 - t0;
}

/* Мінімум, а не середнє: усе, що трапляється в замірі, тільки додає такти.
   Тло віднімаємо таким самим мінімумом, знятим у тих самих умовах. */
static double cost(void (*fn)(void), size_t iters, uint8_t *buf,
                   size_t pages, int reps)
{
    uint64_t best = UINT64_MAX, base = UINT64_MAX;
    int r;

    window(fn, iters, buf, pages);              /* розігрів — викидаємо */
    window(probe_idle, iters, buf, pages);

    for (r = 0; r < reps; r++) {
        uint64_t a = window(fn, iters, buf, pages);
        uint64_t b = window(probe_idle, iters, buf, pages);
        if (a < best) best = a;
        if (b < base) base = b;
    }
    return ((double)best - (double)base) / (double)iters;
}
```
```cpp
static volatile uint64_t sink;

static void probe_idle() { }

static void probe_getppid()
{
    sink += static_cast<uint64_t>(syscall(SYS_getppid));
}

static void probe_vdso()
{
    struct timespec ts{};
    clock_gettime(CLOCK_MONOTONIC, &ts);
    sink += static_cast<uint64_t>(ts.tv_nsec);
}

static void probe_crossing()
{
    struct timespec ts{};
    syscall(SYS_clock_gettime, CLOCK_MONOTONIC, &ts);
    sink += static_cast<uint64_t>(ts.tv_nsec);
}

static uint32_t xs32(uint32_t& s)
{
    uint32_t x = s;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return s = x;
}

/* Використовуємо std::vector для автоматичного керування пам'яттю
   та std::iota для заповнення початкової послідовності. */
static void chain(uint8_t* buf, std::size_t pages)
{
    if (!pages) return;
    std::vector<uint32_t> perm(pages);
    std::iota(perm.begin(), perm.end(), 0u);

    uint32_t seed = 0x9e3779b9u;
    for (std::size_t i = pages - 1; i > 0; --i) {
        std::size_t j = xs32(seed) % (i + 1);
        std::swap(perm[i], perm[j]);
    }
    for (std::size_t i = 0; i < pages; ++i) {
        uint32_t here = perm[i] * PAGE;
        uint32_t next = perm[(i + 1) % pages] * PAGE;
        std::memcpy(buf + here, &next, sizeof(next));
    }
}

static uint64_t window(void (*fn)(), std::size_t iters, uint8_t* buf, std::size_t pages)
{
    uint32_t off = 0;
    __asm__ __volatile__("" : "+r"(fn));

    uint64_t t0 = tsc_open();
    for (std::size_t i = 0; i < iters; ++i) {
        if (pages) {
            for (int s = 0; s < STEPS; ++s)
                std::memcpy(&off, buf + off, sizeof(off));
            sink += off;
        }
        fn();
    }
    uint64_t t1 = tsc_close();
    return t1 - t0;
}

static double cost(void (*fn)(), std::size_t iters, uint8_t* buf,
                    std::size_t pages, int reps)
{
    uint64_t best = UINT64_MAX, base = UINT64_MAX;

    window(fn, iters, buf, pages);
    window(probe_idle, iters, buf, pages);

    for (int r = 0; r < reps; ++r) {
        uint64_t a = window(fn, iters, buf, pages);
        uint64_t b = window(probe_idle, iters, buf, pages);
        if (a < best) best = a;
        if (b < base) base = b;
    }
    return (static_cast<double>(best) - static_cast<double>(base)) / static_cast<double>(iters);
}
```
:::

**Частина третя — шапка режиму й розгортка.**

:::tabs
```c
/* Стовпчиків не вирівнюємо: printf рахує в %-24s байти, а не літери,
   тож на кириличному написі поле «поїде». Двокрапка чесніша за таблицю. */
static void show_file(const char *path, const char *label)
{
    char line[256];
    FILE *f = fopen(path, "r");

    if (!f) { printf("  %s: файлу немає\n", label); return; }
    if (fgets(line, sizeof line, f)) {
        line[strcspn(line, "\n")] = '\0';
        printf("  %s: %s\n", label, line);
    }
    fclose(f);
}

/* Прапорці процесора — рядок flags у /proc/cpuinfo. Шукаємо прапорець
   у пробільній рамці, щоб «pcid» не знайшовся всередині «invpcid». */
static int has_flag(const char *flag)
{
    char line[8192], needle[64];
    FILE *f = fopen("/proc/cpuinfo", "r");
    int found = 0;

    if (!f) return -1;
    snprintf(needle, sizeof needle, " %s ", flag);
    while (fgets(line, sizeof line, f)) {
        char *nl;
        if (strncmp(line, "flags", 5) != 0) continue;
        nl = strchr(line, '\n');
        if (nl) *nl = ' ';                  /* щоб рамка спрацювала й для останнього */
        found = strstr(line, needle) != NULL;
        break;
    }
    fclose(f);
    return found;
}

int main(int argc, char **argv)
{
    static const unsigned KIB[] = { 0, 64, 256, 1024, 4096, 16384, 65536, 262144 };
    static const struct { const char *name; void (*fn)(void); } PROBES[] = {
        { "clock_gettime через vDSO", probe_vdso     },
        { "clock_gettime крізь межу", probe_crossing },
        { "getppid",                  probe_getppid  },
    };
    size_t bytes = (size_t)MAX_KIB * 1024;
    int cpu = (argc > 1) ? atoi(argv[1]) : 0;
    int thp = (argc > 2 && strcmp(argv[2], "--thp") == 0);
    cpu_set_t set;
    uint8_t *buf;
    double hz;
    size_t k;

    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof set, &set) != 0) {
        perror("sched_setaffinity");
        return 1;
    }

    buf = mmap(NULL, bytes, PROT_READ | PROT_WRITE,
               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED) { perror("mmap"); return 1; }

    /* Прозорі великі сторінки вмикаємо або вимикаємо явно: інакше система
       підкладе 2-мебібайтні сторінки на свій розсуд — і крива тиску на TLB
       зникне сама собою, без жодного пояснення. */
    madvise(buf, bytes, thp ? MADV_HUGEPAGE : MADV_NOHUGEPAGE);
    memset(buf, 0, bytes);                  /* заселяємо сторінки наперед */

    hz = tsc_hz();

    printf("режим вимірювання\n");
    printf("  ядро процесора: %d, частота TSC: %.0f МГц\n", cpu, hz / 1e6);
    show_file("/sys/devices/system/cpu/vulnerabilities/meltdown", "meltdown");
    printf("  прапорці: pti=%d pcid=%d invpcid=%d constant_tsc=%d\n",
           has_flag("pti"), has_flag("pcid"),
           has_flag("invpcid"), has_flag("constant_tsc"));
    printf("  великі сторінки: %s\n",
           thp ? "MADV_HUGEPAGE" : "MADV_NOHUGEPAGE");

    printf("\nбез робочої множини (тактів / нс на виклик)\n");
    for (k = 0; k < sizeof PROBES / sizeof *PROBES; k++) {
        double t = cost(PROBES[k].fn, 200000, buf, 0, 5);
        printf("  %s: %.1f / %.1f\n", PROBES[k].name, t, t * 1e9 / hz);
    }

    printf("\ngetppid під тиском на TLB (тактів / нс на виклик)\n");
    for (k = 0; k < sizeof KIB / sizeof *KIB; k++) {
        size_t pages = (size_t)KIB[k] * 1024 / PAGE;
        double t;
        if (pages) chain(buf, pages);
        t = cost(probe_getppid, 20000, buf, pages, 3);
        printf("  %8u КіБ: %7.1f / %7.1f\n", KIB[k], t, t * 1e9 / hz);
    }

    munmap(buf, bytes);
    return 0;
}
```
```cpp
/* Використовуємо std::ifstream замість FILE*, std::string_view
   для пошуку прапорців у /proc/cpuinfo та RAII для очищення ресурсів. */
static void show_file(const std::string& path, const std::string& label)
{
    std::ifstream f(path);
    if (!f.is_open()) {
        std::cout << "  " << label << ": файлу немає\n";
        return;
    }
    std::string line;
    if (std::getline(f, line)) {
        std::cout << "  " << label << ": " << line << "\n";
    }
}

static bool has_flag(std::string_view flag)
{
    std::ifstream f("/proc/cpuinfo");
    if (!f.is_open()) return false;
    std::string line;
    std::string needle = " ";
    needle += flag;
    needle += " ";
    while (std::getline(f, line)) {
        if (line.rfind("flags", 0) != 0) continue;
        line += " ";
        return line.find(needle) != std::string::npos;
    }
    return false;
}

int main(int argc, char** argv)
{
    static constexpr std::array<unsigned, 8> KIB = { 0, 64, 256, 1024, 4096, 16384, 65536, 262144 };
    struct Probe {
        std::string_view name;
        void (*fn)();
    };
    static const std::array<Probe, 3> PROBES = {{
        { "clock_gettime через vDSO", probe_vdso     },
        { "clock_gettime крізь межу", probe_crossing },
        { "getppid",                  probe_getppid  },
    }};

    std::size_t bytes = static_cast<std::size_t>(MAX_KIB) * 1024;
    int cpu = (argc > 1) ? std::atoi(argv[1]) : 0;
    bool thp = (argc > 2 && std::string_view(argv[2]) == "--thp");

    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof(set), &set) != 0) {
        std::perror("sched_setaffinity");
        return 1;
    }

    auto* buf = static_cast<uint8_t*>(mmap(nullptr, bytes, PROT_READ | PROT_WRITE,
                                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    if (buf == MAP_FAILED) { std::perror("mmap"); return 1; }

    madvise(buf, bytes, thp ? MADV_HUGEPAGE : MADV_NOHUGEPAGE);
    std::memset(buf, 0, bytes);

    double hz = tsc_hz();

    std::cout << "режим вимірювання\n";
    std::cout << "  ядро процесора: " << cpu << ", частота TSC: " << static_cast<long>(hz / 1e6) << " МГц\n";
    show_file("/sys/devices/system/cpu/vulnerabilities/meltdown", "meltdown");
    std::cout << "  прапорці: pti=" << has_flag("pti")
              << " pcid=" << has_flag("pcid")
              << " invpcid=" << has_flag("invpcid")
              << " constant_tsc=" << has_flag("constant_tsc") << "\n";
    std::cout << "  великі сторінки: " << (thp ? "MADV_HUGEPAGE" : "MADV_NOHUGEPAGE") << "\n";

    std::cout << "\nбез робочої множини (тактів / нс на виклик)\n";
    for (const auto& probe : PROBES) {
        double t = cost(probe.fn, 200000, buf, 0, 5);
        std::cout << "  " << probe.name << ": " << t << " / " << (t * 1e9 / hz) << "\n";
    }

    std::cout << "\ngetppid під тиском на TLB (тактів / нс на виклик)\n";
    for (unsigned kib : KIB) {
        std::size_t pages = static_cast<std::size_t>(kib) * 1024 / PAGE;
        if (pages) chain(buf, pages);
        double t = cost(probe_getppid, 20000, buf, pages, 3);
        std::cout << "  " << kib << " КіБ: " << t << " / " << (t * 1e9 / hz) << "\n";
    }

    munmap(buf, bytes);
    return 0;
}
```
:::

## Як запускати, щоб числа щось означали

Програма прив'язується до вказаного ядра сама, але цього мало.

```sh
# 1. зафіксувати частоту: інакше той самий код дасть різні числа
$ sudo cpupower frequency-set -g performance
$ echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo   # якщо є

# 2. запустити на конкретному ядрі
$ taskset -c 3 ./bordercost 3
```

Фіксувати частоту доводиться саме через сталість лічильника. Такти TSC цокають рівномірно, а ядро процесора під [керуванням частотою](book:programming/dvfs) працює то швидше, то повільніше — тож та сама робота вкладається в різну кількість тактів залежно від того, куди зараз хитнувся регулятор. Розгін до турбо-частот під час першого прогону й спад під час третього дадуть розкид, у якому ефект ізоляції потоне.

Обидві прив'язки — `taskset` зовні й `sched_setaffinity` усередині — навмисно дублюють одна одну: перша діє з першої ж інструкції, ще до того, як завантажувач розкладе бібліотеки, друга рятує, коли стенд запустили без `taskset`. Для серйозних замірів ядро краще ще й відібрати в планувальника цілком (`isolcpus=`, `nohz_full=`) — про це є [окрема розмова про прив'язку задач](book:unix-linux/cpu-affinity).

## Що показує вивід

```
режим вимірювання
  ядро процесора: 3, частота TSC: 2496 МГц
  meltdown: Mitigation: PTI
  прапорці: pti=1 pcid=1 invpcid=1 constant_tsc=1
  великі сторінки: MADV_NOHUGEPAGE

без робочої множини (тактів / нс на виклик)
  clock_gettime через vDSO: 63.4 / 25.4
  clock_gettime крізь межу: 639.8 / 256.3
  getppid: 561.4 / 224.9

getppid під тиском на TLB (тактів / нс на виклик)
         0 КіБ:   561.4 /   224.9
        64 КіБ:   574.9 /   230.3
       256 КіБ:   602.1 /   241.2
      1024 КіБ:   668.3 /   267.7
      4096 КіБ:   781.5 /   313.1
     16384 КіБ:   902.7 /   361.6
     65536 КіБ:   968.0 /   387.7
    262144 КіБ:  1004.2 /   402.3
```

*Вивід з однієї машини — ілюстрація форми, не константа: на іншому процесорі, іншому ядрі й іншому наборі пом'якшень числа будуть інші.*

Читати цей звіт треба відношеннями, а не абсолютними значеннями.

Перше відношення — між першим і другим рядком: та сама робота, здобута без перетину межі й із перетином, різниться приблизно вдесятеро. Це й є плата за межу в чистому вигляді, зважена на одній машині за одну секунду. Вона одразу пояснює, чому `clock_gettime` віддали в vDSO й чому програма, що смикає годинник у циклі, після переходу на прямий системний виклик просідає до невпізнання.

Друге відношення — між першим і останнім рядком розгортки. Той самий `getppid`, той самий код ядра, та сама робота — і майже вдвічі більша ціна тільки тому, що між викликами програма розворушила чверть гігабайта. Ніщо в самому виклику про це не знає; різницю зробив TLB.

> 🔧 **Навіщо це.** Числа зі стенда прямо кажуть, куди дивитися. Якщо ціна перетину стоїть рівно на всій розгортці, ізоляція вашому навантаженню майже нічого не коштує, і шукати треба деінде. Якщо крива круто йде вгору, у вас не «повільні системні виклики», а тиск на TLB — і лікується він не меншою кількістю викликів, а великими сторінками та щільнішим укладанням даних. А якщо `pcid` у шапці стоїть нулем, розмова про оптимізацію починається з питання, чому машина працює без міток адресного простору.

![Форма залежності: ціна перетину як функція робочої множини за трьох режимів](/reference/unix-linux/memory/kernel-page-table-isolation/img/cost-curve.svg)

*Зліва, де робоча множина вміщається в TLB, три режими майже збігаються. Розходяться вони праворуч — і чим більший тиск на TLB, тим дорожче обходиться відсутність міток адресного простору.*

## perf: куди пішли такти

Стенд каже, скільки коштує; [підсистема лічильників](book:unix-linux/perf-events) каже, за що.

```sh
$ perf stat -r 3 -e cycles:u,cycles:k,dTLB-loads,dTLB-load-misses,iTLB-load-misses \
      taskset -c 3 ./bordercost 3
```

Розділення `cycles:u` й `cycles:k` показує, яка частка тактів узагалі проведена в ядрі, — і це перша перевірка того, що ви міряєте те, що думаєте: якщо в ядрі опинилося кілька відсотків, вимір потонув у чомусь іншому. `dTLB-load-misses` росте разом із розгорткою й дає незалежне підтвердження, що тиск на TLB справді зростає, а не примарився. `iTLB-load-misses` цікавий окремо: коли ізоляція знімає з ядерних відображень прапорець «глобальний», переклади для **коду** ядра теж перестають переживати перетин межі, і промахи в кеші перекладів інструкцій — прямий слід цього.

Дві застороги. Звичайному користувачеві апаратні лічильники доступні лише за `kernel.perf_event_paranoid` не більшим від одиниці (`sysctl kernel.perf_event_paranoid`) або коли процесові видано окрему [можливість](book:unix-linux/capabilities) на це. І частина подій буває позначена `<not supported>` — усередині віртуальної машини або на мікроархітектурі, де відповідного лічильника просто немає; тоді точні імена доводиться брати з переліку `perf list` для конкретного процесора.

## Три перемикачі, що зсувають криву

Три параметри змінюють режим — і кожен показує окрему складову ціни.

**`pti=off` — вимкнення ізоляції.** Це не налаштування продуктивності, а свідома відмова від захисту: на машині з вимкненою ізоляцією будь-який код, що там виконується, включно з чужим сценарієм у вкладці браузера, може прочитати пам'ять ядра. Робити це можна **лише на відокремленому стенді, де немає ні чужого коду, ні чужих даних**, і тільки на час замірів. Найбезпечніша форма — не правити конфігурацію завантажувача, а дописати параметр разово в меню GRUB (клавіша `e`, дописати в рядок `linux`, `Ctrl-X`): після перезавантаження машина повернеться в захищений стан сама, і ніхто не забуде відкотити.

Що вимкнення справді сталося, підтверджують ті самі два джерела: у файлі `meltdown` з'явиться `Vulnerable`, а прапорець `pti` зникне з `/proc/cpuinfo`. Заразом варто глянути `dmesg | grep -i 'page table isolation'`. І ще: `mitigations=off` вимикає купу пом'якшень одночасно, тож різницю після нього приписати саме ізоляції не вийде — для чистого досліду потрібен лише `pti=off`.

**`nopcid` — ізоляція без міток адресного простору.** Параметр лишає захист на місці, але забирає в ядра механізм, що рятує TLB від скидання на кожному записі в `CR3`. Крива після цього не просто зсувається вгору — вона стає значно крутішою, бо тепер кожен перетин межі викидає з TLB усе. Це та сама конфігурація, з якої взялися страшні числа початку 2018 року, і найкращий спосіб побачити, що більшу частину ціни бере не сам запис у `CR3`, а те, що після нього не лишається перекладів.

**`--thp` — великі сторінки.** Прапорець стенда замінює `MADV_NOHUGEPAGE` на `MADV_HUGEPAGE`, і буфер починає лежати на двомебібайтних сторінках. Кількість перекладів, потрібних для тієї самої робочої множини, падає в п'ятсот разів, тиск на TLB зникає — і крива майже вирівнюється. Це не хитрість стенда, а робочий засіб: [великі сторінки](book:unix-linux/huge-pages) на навантаженні з великою робочою множиною здатні відіграти більше, ніж ізоляція забрала. Перевірити, що вони справді підклалися, можна за `grep AnonHugePages /proc/meminfo` до й під час прогону — на буфері в чверть гігабайта різниця помітна неозброєним оком.

## Пастки, у які падають усі

**Незакріплений потік.** Без прив'язки планувальник переносить програму між ядрами; кожен перенос — холодні кеші, холодний TLB і, на старих машинах, ще й трохи інакший TSC. Половина замірів припаде на одне ядро, половина на друге, і мінімум по прогонах перестане щось означати.

**Плаваюча частота.** Найпідступніше з усього переліку, бо не дає ні помилки, ні підозрілого числа — лише розкид, який легко списати на шум. Ліки описані вище: `performance` і вимкнене турбо. Симптом, за яким її впізнають, — перший прогін систематично гірший за наступні.

**Розігрів.** Перші ітерації платять за помилки сторінок, холодний кеш і холодне передбачення переходів, а процесор ще не встиг піднятися з низької частоти. Тому буфер заселяють `memset`-ом наперед, а перший прогін кожного заміру викидають без розгляду.

**`rdtsc` без огорожі.** Позначка часу, знята інструкцією, яку процесор має право переставити, показує невідомо що. Огорожа обов'язкова — а що коштує вона сама десятки тактів, вікно ставлять навколо десятків тисяч ітерацій, а не навколо однієї.

**Такти, поділені не на ту частоту.** Найтихіша з помилок: результат виглядає як наносекунди, має правдоподібний порядок — і зсунутий рівно на стільки, на скільки частота TSC розійшлася з написаною в назві моделі процесора. Іноді це частки відсотка, іноді разюча відмінність; передбачити, коли саме, не можна. Частоту TSC беруть тільки калібруванням.

**Компілятор, що прибрав зайве.** Цикл, результат якого нікому не потрібен, [правило «ніби»](book:programming/as-if-rule) дозволяє викинути цілком. Порожня проба зникне першою — і від'ємник перетвориться на нуль. Рятують запис у `volatile` і рядок асемблера, що ховає від компілятора значення покажчика на функцію.

**Прозорі великі сторінки, які ніхто не просив.** Якщо система схильна підкладати їх сама, буфер у 64 МіБ може виявитися розкладеним по двомебібайтних сторінках — і крива вийде рівною, ніби тиску на TLB не існує. `MADV_NOHUGEPAGE` у стенді ставиться саме проти цього.

**Сусід по фізичному ядру.** Два логічні процесори одного фізичного ділять і кеші, і кеш перекладів; активний сусід підніме числа й додасть розкиду. Або вибирайте ядро, чий [напарник](book:programming/simultaneous-multithreading) простоює, або вимикайте багатопотоковість на час замірів.

**Віртуальна машина.** `RDTSC` у гості може перехоплюватися або масштабуватися гіпервізором, а файл `meltdown` описує стан гостьового ядра й нічого не каже про хазяйське. Числа з віртуальної машини порівнянні лише з іншими числами з тієї самої віртуальної машини.
