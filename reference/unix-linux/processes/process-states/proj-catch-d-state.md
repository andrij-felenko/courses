# ⚙️ Спіймати стан D: лабораторія на п'ять літер

Стани процесу більшість людей уперше бачить у чужому `ps` посеред аварії — і саме тоді розбиратися найгірше. Тут зібрано протилежне: піддослідну програму, яка сама себе проводить крізь `R`, `S`, `T`, `Z` і `D` за півхвилини, і спостерігача, який друкує цей шлях смугою літер. Усе це працює на здоровій машині, нічого ламати не треба, а найцікавіша літера — `D` — виходить на замовлення двома різними способами. Різниця між цими двома способами і є найкориснішим, що можна винести з досліду.

## Чотири літери задарма й одна складна

Чотири стани з п'яти влаштувати легко, бо кожен має очевидний привід.

`R` — це порожній цикл: задача нічого не чекає, отже стоїть у черзі готових. `S` — `nanosleep()`: сон, який будить таймер і будь-який сигнал. `T` — `raise(SIGSTOP)`: задача не чекає нічого, їй просто заборонено бігти, і вийде вона звідти лише від `SIGCONT`. `Z` — дитина, яка викликала `_exit()`, поки батько ще не забрав її код виходу.

Уся складність у `D`. Наївна спроба виглядає так: «попросимо в диска блок і подивимося». На сучасному NVMe читання чотирьох кілобайтів триває кілька десятків мікросекунд, і спостерігач, який опитує `/proc` двадцять разів на секунду, у цей проміжок майже не влучить. Порахуймо, наскільки саме:

```
шанс, що вибірка впаде всередину епізоду ≈ d / T      (для d < T)

d = 200 мкс — епізод непереривного сну
T = 50 мс   — період опитування

0.0002 / 0.05 = 0.004  →  0.4 %
```

Тобто щоб побачити такий `D` бодай раз, епізодів має бути кілька сотень. Коротких сплесків опитуванням не спіймати — для них є зовсім інший інструмент, і про нього наприкінці.

Отже, потрібен сон, який триває **керовано довго**. Таких способів два, і вони цінні саме тим, що дають `D` різної природи: один — непереривний сон, який усе-таки вбивається, другий — непереривний по-справжньому.

## Спосіб перший: сон, який дарує vfork

Найдешевший `D` не потребує ні root, ні диска, ні жодного пристрою. Його дає `vfork()`.

Коли процес породжує дитину прапорцем `CLONE_VFORK`, ядро зупиняє **батька** й тримає його, поки дитина не викличе `exec` або не вийде. Це і є той рідкісний випадок, коли чекання цілком підконтрольне нам: скільки дитина проспить, стільки батько й простоїть. `clone()` — узагальнення `fork()`, у якому набором прапорців задають, що дитина успадкує, а що поділить із батьком; сам `vfork()` у glibc — це `clone()` із парою `CLONE_VM|CLONE_VFORK` ([vfork, posix_spawn і clone](book:unix-linux/spawn-alternatives)).

Тепер найцікавіше — у якому стані чекає батько. У ядрі це рядок з `kernel/fork.c`:

```c
static int wait_for_vfork_done(struct task_struct *child,
                               struct completion *vfork)
{
    unsigned int state = TASK_KILLABLE|TASK_FREEZABLE;
    ...
    killed = wait_for_completion_state(vfork, state);
```

`TASK_KILLABLE` — це не окремий стан, а сума двох бітів: `TASK_UNINTERRUPTIBLE` плюс `TASK_WAKEKILL`. А назовні `/proc` віддає не всі біти, а лише ті, що входять у маску `TASK_REPORT`; `TASK_WAKEKILL` до неї не належить. Тому з двох бітів у літеру перетворюється тільки перший — і `ps` чесно, за своїми правилами, друкує `D`.

Виходить рівно та ситуація, заради якої дослід і ставиться: перед нами `D`, який виглядає як безнадійне зависання, а насправді слухається `SIGKILL`. Побачити цю різницю можна тільки на дотик: надіслати спершу `SIGTERM`, потім `SIGKILL`.

Так було не завжди. До лютого 2012 року батько в `vfork()` чекав у звичайному непереривному сні, і процес, який щойно породив дитину, не вбивався нічим — досить було дитині зависнути. Латку, яка перевела це чекання на `wait_for_completion_killable()`, надіслав Олег Нестеров (Oleg Nesterov); її схвалив Теджун Хо (Tejun Heo). Аргумент у супровідному листі був той самий, що виправдовує весь клас таких змін: якщо чекання обірвано смертельним сигналом, ядро не повертається в простір користувача й не торкається пам'яті, спільної з дитиною, — а отже, повний коректний відкіт і не потрібен.

## Піддослідний

Програма нічого не обчислює — вона лише по черзі стає в кожен зі станів і голосно повідомляє, у який саме. Мова тут не обирається: `clone()`, `raise()`, `_exit()` — це системні виклики, і жодна обгортка не дасть над ними того контролю, який потрібен у досліді.

```c
/* states.c — піддослідний: сам себе проводить крізь R, S, T, Z і D.
 * Збірка:  cc -O2 -o states states.c
 * Запуск:  ./states &   (у фоні, бо фаза T зупиняє процес)
 */
#define _GNU_SOURCE
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static double t0;

static void banner(const char *tag, const char *why)
{
    fprintf(stderr, "%7.3f  [%s] %s\n", now() - t0, tag, why);
    fflush(stderr);
}

/* Літера стану з /proc/PID/stat.
   Друге поле — ім'я програми в дужках, і воно може містити і пробіли,
   і самі дужки. Тому єдиний надійний спосіб — шукати ОСТАННЮ ')'. */
static char state_of(pid_t pid)
{
    char path[64], buf[512];
    snprintf(path, sizeof path, "/proc/%d/stat", (int)pid);
    FILE *f = fopen(path, "r");
    if (!f) return '?';
    size_t n = fread(buf, 1, sizeof buf - 1, f);
    fclose(f);
    buf[n] = '\0';
    char *p = strrchr(buf, ')');
    return (p && p[1] && p[2]) ? p[2] : '?';
}

/* ── R: нічого не бракує, крім вільного ядра ────────────────────────── */
static void phase_running(double secs)
{
    banner("R", "порожній цикл: задача стоїть у черзі готових");
    double end = now() + secs;
    volatile unsigned long x = 0;
    while (now() < end)
        for (int i = 0; i < 100000; i++) x++;
}

/* ── S: сон, який будить і таймер, і сигнал ─────────────────────────── */
static void phase_sleeping(int secs)
{
    banner("S", "nanosleep: переривний сон");
    struct timespec ts = { secs, 0 };
    nanosleep(&ts, NULL);
}

/* ── T: задача не чекає нічого, їй заборонено бігти ─────────────────── */
static void phase_stopped(void)
{
    banner("T", "raise(SIGSTOP): вийти можна лише через SIGCONT");
    raise(SIGSTOP);
    banner("T", "прийшов SIGCONT — знову в черзі готових");
}

/* ── Z: зомбі. Це окремий PID — наша дитина, не ми ──────────────────── */
static void phase_zombie(int secs)
{
    pid_t kid = fork();
    if (kid == 0) _exit(42);

    struct timespec ts = { 0, 50 * 1000 * 1000 };
    nanosleep(&ts, NULL);                  /* дати дитині вийти */
    fprintf(stderr, "%7.3f  [Z] дитина %d у стані '%c' — код виходу ще нічий\n",
            now() - t0, (int)kid, state_of(kid));

    ts.tv_sec = secs; ts.tv_nsec = 0;
    nanosleep(&ts, NULL);
    waitpid(kid, NULL, 0);
    banner("Z", "wait() забрав код виходу — запис зник");
}

/* ── D: непереривний сон на замовлення ──────────────────────────────── */
#define STACK_SZ (256 * 1024)
static int hold_seconds;

static int vfork_child(void *arg)
{
    struct timespec ts = { *(int *)arg, 0 };
    nanosleep(&ts, NULL);
    _exit(0);
}

static void phase_disk_sleep(int secs)
{
    void *stack = mmap(NULL, STACK_SZ, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS | MAP_STACK, -1, 0);
    if (stack == MAP_FAILED) { perror("mmap"); return; }

    hold_seconds = secs;
    banner("D", "clone(CLONE_VFORK): батько стоїть, поки дитина не вийде");
    fprintf(stderr, "         спробуйте в іншому терміналі:  kill -TERM %d\n"
                    "         а потім:                       kill -9 %d\n",
            (int)getpid(), (int)getpid());
    fflush(stderr);

    pid_t kid = clone(vfork_child, (char *)stack + STACK_SZ,
                      CLONE_VFORK | SIGCHLD, &hold_seconds);
    if (kid < 0) { perror("clone"); return; }

    waitpid(kid, NULL, 0);
    munmap(stack, STACK_SZ);
    banner("D", "дитина вийшла — батько прокинувся");
}

int main(void)
{
    t0 = now();
    setvbuf(stderr, NULL, _IONBF, 0);
    fprintf(stderr, "PID %d\n", (int)getpid());

    phase_running(3.0);
    phase_sleeping(3);
    phase_stopped();
    phase_zombie(3);
    phase_disk_sleep(12);
    return 0;
}
```

Два місця тут варті окремого слова.

Перше — `CLONE_VFORK` **без** `CLONE_VM`. Справжній `vfork()` віддає дитині спільну з батьком пам'ять, і саме через це в ній заборонено робити майже все: спільний стек, спільний `errno`, спільні замки всередині libc. Нам ця спільність не потрібна — потрібне лише те, що батько чекає. Тому ми беремо голий `CLONE_VFORK`: дитина дістає власну копію адресного простору, поводиться як звичайна дитина `fork()`, і при цьому батько так само стоїть у `wait_for_vfork_done()`. Власний стек через `mmap()` ми все одно виділяємо, бо `clone()` іншого й не приймає.

Друге — розбір `/proc/PID/stat` через `strrchr(buf, ')')`. Спокуса взяти третє поле через пробіли велика й закінчується завжди однаково: програма з назвою на кшталт `(sd-pam)` або `kworker/u16:2-events` ламає розбір, і спостерігач починає показувати сміття. Ім'я процесу вибирає користувач, а не ви.

## Спостерігач

Спостерігач робить дві речі: раз на 50 мілісекунд читає літеру стану й веде смугу — рядок, у якому один символ дорівнює одній вибірці. На зміну стану він друкує позначку з часом і `wchan`. Плюс одна активна дія: коли процес просидів у `T` довше двох секунд, спостерігач сам шле йому `SIGCONT` — інакше дослід зупиниться назавжди, бо `T` не минає сам.

:::tabs
```sh
#!/bin/sh
# watch-state.sh <pid> [період_мс] — смуга станів одного процесу.
pid=$1
per=${2:-50}
[ -r "/proc/$pid/stat" ] || { echo "немає процесу $pid" >&2; exit 1; }

start=$(date +%s.%N)
nap=$(awk -v p="$per" 'BEGIN{ print p/1000 }')
prev='' band='' held=0 cont=0

elapsed() { awk -v a="$(date +%s.%N)" -v b="$start" 'BEGIN{ printf "%7.3f", a-b }'; }

while [ -r "/proc/$pid/stat" ]; do
    line=$(cat "/proc/$pid/stat" 2>/dev/null) || break
    [ -n "$line" ] || break
    st=${line##*") "}          # ім'я програми може містити ')' — ріжемо по останній
    st=${st%% *}
    band="$band$st"

    if [ "$st" != "$prev" ]; then
        wch=$(cat "/proc/$pid/wchan" 2>/dev/null || echo '?')
        printf '%s  %s   wchan=%s\n' "$(elapsed)" "$st" "$wch"
        prev=$st; held=0
    fi

    held=$((held + 1))
    if [ "$st" = T ] && [ "$cont" -eq 0 ] && [ "$held" -gt $((2000 / per)) ]; then
        kill -CONT "$pid"; cont=1
        printf '%s  →   надіслано SIGCONT\n' "$(elapsed)"
    fi

    sleep "$nap"
done

printf '\nсмуга: %s\n' "$band"
```
```python
#!/usr/bin/env python3
"""watch_state.py <pid> [період_мс] — смуга станів і час у кожному стані."""
import os, signal, sys, time


def state_of(pid):
    with open(f"/proc/{pid}/stat", "rb") as f:
        raw = f.read()
    # ім'я програми — в дужках і може містити ')': ріжемо по ОСТАННІЙ
    return raw[raw.rindex(b")") + 2:].split(b" ", 1)[0].decode()


def wchan_of(pid):
    try:
        with open(f"/proc/{pid}/wchan") as f:
            return f.read().strip() or "0"
    except OSError:
        return "0"


def main():
    pid = int(sys.argv[1])
    nap = (float(sys.argv[2]) if len(sys.argv) > 2 else 50) / 1000
    band, dwell = [], {}
    prev = prev_t = None
    cont_sent = False
    t0 = time.monotonic()

    while True:
        try:
            st = state_of(pid)
        except (OSError, ValueError):
            break
        t = time.monotonic() - t0

        if st != prev:
            if prev is not None:
                dwell[prev] = dwell.get(prev, 0.0) + (t - prev_t)
            print(f"{t:7.3f}  {st}   wchan={wchan_of(pid)}")
            prev, prev_t = st, t
        band.append(st)

        if st == "T" and not cont_sent and t - prev_t > 2.0:
            os.kill(pid, signal.SIGCONT)
            cont_sent = True
            print(f"{t:7.3f}  →   надіслано SIGCONT")

        time.sleep(nap)

    total = time.monotonic() - t0
    if prev is not None:
        dwell[prev] = dwell.get(prev, 0.0) + (total - prev_t)

    print("\nсмуга:", "".join(band))
    for st, sec in sorted(dwell.items(), key=lambda kv: -kv[1]):
        print(f"  {st}: {sec:6.2f} c   ({100 * sec / total:4.1f} %)")


main()
```
:::

Версія на оболонці не потребує нічого, крім `awk`, `date` і `sleep`, який розуміє дробові секунди (coreutils і busybox розуміють). Версія на Python витримує рівніший період і наприкінці підсумовує, скільки часу процес простояв у кожному стані, — саме те число, заради якого такі спостерігачі й пишуть.

## Прогін

```sh
cc -O2 -o states states.c
./states & pid=$!
sh watch-state.sh "$pid"
```

Вивід піддослідного й вивід спостерігача змішуються в одному терміналі, і це якраз добре: видно водночас і те, що програма робить, і те, як це виглядає ззовні.

```
PID 31904
  0.000  [R] порожній цикл: задача стоїть у черзі готових
  0.014  R   wchan=0
  3.001  [S] nanosleep: переривний сон
  3.049  S   wchan=hrtimer_nanosleep
  6.002  [T] raise(SIGSTOP): вийти можна лише через SIGCONT
  6.051  T   wchan=0
  8.104  →   надіслано SIGCONT
  8.106  [T] прийшов SIGCONT — знову в черзі готових
  8.152  S   wchan=hrtimer_nanosleep
  8.157  [Z] дитина 31907 у стані 'Z' — код виходу ще нічий
 11.160  [Z] wait() забрав код виходу — запис зник
 11.161  [D] clone(CLONE_VFORK): батько стоїть, поки дитина не вийде
         спробуйте в іншому терміналі:  kill -TERM 31904
         а потім:                       kill -9 31904
 11.205  D   wchan=kernel_clone

смуга:
RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSTTTTTTTTTTTTTTTTTTTTTTTTTTTT
TTTTTTTTTTTTTSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
```

Смуга — найкорисніший рядок у всьому виводі: один символ у ній дорівнює одній вибірці, тож видно не окремі стани, а їхні пропорції. Точний символ у `wchan` залежить від версії ядра й від того, що інлайнер злив із сусідньою функцією; `kernel_clone`, `wait_for_completion_state` і просто `0` — усе це нормальні відповіді, і жодна з них не є ознакою біди.

![П'ять фаз піддослідного і що виводить його з кожної](/reference/unix-linux/processes/process-states/img/lab-run.svg)

*Літера каже, чому задачі немає на процесорі; повернути її може щоразу інша подія — і саме тому станів кілька, а не два.*

Тепер головне. Поки програма стоїть у `D`, в іншому терміналі надішліть `kill -TERM`. Не станеться нічого: сигнал ляже в набір недоправлених і чекатиме. А `kill -9` уб'є процес негайно — бо цей `D` насправді `TASK_KILLABLE`. Літера та сама, поведінка різна, і `ps` цієї різниці не показує ніяк.

## Спосіб другий: диск, який відповідає через три секунди

Щоб побачити `D`, з якого не виводить навіть `SIGKILL`, потрібен пристрій, який поводиться повільно, але передбачувано. Ламати нічого не треба — такий пристрій збирається з файлу за три команди.

Device mapper — підсистема ядра, яка робить блоковий пристрій із **таблиці відображень**: кожен рядок каже, який діапазон секторів кому віддавати й через який шар обробки. Серед цих шарів є `delay` — він просто затримує кожен запит на задану кількість мілісекунд ([device mapper](book:unix-linux/device-mapper)). Тобто повільний диск можна не шукати, а описати.

Другий інгредієнт — `O_DIRECT`. Звичайне читання спершу зазирає в кеш сторінок і, якщо блок там уже є, повертається миттєво, не турбуючи пристрій узагалі; з таким читанням дослід просто не відбувся б. Прапорець `O_DIRECT` каже ядру нести дані повз кеш, прямо між пристроєм і буфером програми ([буферизований і прямий ввід-вивід](book:unix-linux/buffered-and-direct-io)). Задача, яка подала таке читання, чекає на завершення операції в `TASK_UNINTERRUPTIBLE` — тому що операцію вже віддано контролеру й відкликати її нема як.

```sh
#!/bin/bash
# slow-disk.sh — потрібні права root. Робить D, з якого не виводить SIGKILL.
set -e
IMG=/var/tmp/slow.img

modprobe dm-delay || true
truncate -s 64M "$IMG"
LOOP=$(losetup --find --show "$IMG")
dmsetup create slowdisk --table "0 $(blockdev --getsz "$LOOP") delay $LOOP 0 3000"

dd if=/dev/mapper/slowdisk of=/dev/null bs=4k count=1 iflag=direct &
victim=$!

sleep 0.5
echo "--- поки триває читання:"
ps -o pid,stat,wchan:28,comm -p $victim

kill -9 $victim
sleep 0.5
echo "--- через півсекунди після kill -9:"
ps -o pid,stat,wchan:28,comm -p $victim

wait $victim || true
echo "--- операція завершилася — аж тепер сигнал подіяв"

dmsetup remove slowdisk
losetup -d "$LOOP"
rm -f "$IMG"
```

Обидва виклики `ps` покажуть той самий рядок зі станом `D`. Смертельний сигнал уже доправлено, він уже лежить у наборі недоправлених — і не робить нічого, поки `dm-delay` не відлічить свої три секунди. Порівняйте це з попереднім дослідом: там `kill -9` спрацював миттєво, тут не спрацював зовсім. Літера в обох випадках одна.

![Повільний диск, зібраний із файлу: де саме беруться три секунди](/reference/unix-linux/processes/process-states/img/slow-disk-stack.svg)

*Затримку внесено в один-єдиний шар, а стоїть через неї процес нагорі — і стоїть непереривно, бо запит уже пішов униз.*

Затримку варто підняти до `dmsetup create ... delay $LOOP 0 130000` і не вбивати процес узагалі: за 120 секунд `khungtaskd` напише в журнал ядра свій рядок про заблоковану задачу, і ви побачите те саме повідомлення, що зазвичай приходить із бойового сервера, — тільки на власному стенді й із наперед відомою причиною.

## Пастки

**Опитуванням `/proc` короткі стани не ловляться.** Це не хиба спостерігача, а межа методу: епізод коротший за період вибірки видно лише випадково. Коли треба порахувати всі епізоди `D`, а не подивитися на них, потрібні трасувальні точки ядра: `sched_switch` спрацьовує на кожному знятті задачі з процесора й серед іншого друкує поле `prev_state` — ту саму літеру ([ftrace і трасувальні точки](book:unix-linux/ftrace-tracepoints)).

```sh
cd /sys/kernel/tracing
echo 1 > events/sched/sched_switch/enable
grep --line-buffered 'prev_state=D' trace_pipe
```

Готовий інструмент для цього ж — `offcputime` з набору bcc: він збирає стеки ядра, у яких задача сходила з процесора, і вміє фільтрувати за станом (`--state 2` — це рівно `TASK_UNINTERRUPTIBLE`); працює він через [eBPF](book:unix-linux/ebpf).

**`ps` за замовчуванням зводить потоки в один рядок.** Стан лежить у задачі, а не в процесі, тож у багатопотокової програми станів стільки, скільки потоків ([потоки як задачі](book:unix-linux/threads-as-tasks)). Одного потоку, намертво застряглого в `D`, у звичайному `ps` не видно взагалі — процес показується як `S`. Дивитися треба `ps -L -p <pid>` або перелік у `/proc/<pid>/task/`.

**`wchan` часто дорівнює `0`, і це не помилка.** Ядро віддає символ лише тому, кому дозволено `ptrace_may_access()` до цієї задачі — інакше друкує нуль. Нуль вийде й тоді, коли задача не спить, і тоді, коли символ не знайшовся. Так само поводяться `/proc/<pid>/stack` (потрібні root і ядро, зібране з підтримкою збирання стеків) та решта глибоких полів [procfs](book:unix-linux/proc-filesystem).

**Фаза `T` — це пастка для того, хто запустив.** `SIGSTOP` не минає ні від часу, ні від закриття термінала. Якщо запустити піддослідного без спостерігача, він зупиниться назавжди; виводить його лише `kill -CONT <pid>`. Тому в лабораторному сценарії `SIGCONT` шле сам спостерігач, а не людина, — програма не повинна залежати від того, чи хтось за нею стежить.

**`dm-delay` не наводять на робочий диск.** У таблиці ви називаєте справжній блоковий пристрій, і помилка в імені коштує дорого. У досліді підкладкою навмисно служить файл через loop-пристрій: найгірше, що станеться, — зіпсуються 64 мегабайти в `/var/tmp`. Розбирати конструкцію треба в зворотному порядку — спершу `dmsetup remove`, потім `losetup -d`; якщо `dmsetup remove` каже «device busy», значить хтось іще тримає пристрій відкритим, і шукати треба через `lsof` або `dmsetup info -c`.

**Не всюди є з чого будувати.** У контейнері без `--privileged` немає ні `/dev/mapper`, ні права підвантажити модуль; у WSL2 ядро справжнє, але зібране з власним набором параметрів, і модуля `dm-delay` у ньому може просто не бути. Спосіб через `CLONE_VFORK` працює скрізь, де є Linux, і саме тому його варто мати першим у кишені.

**Спостерігач сам є процесом.** Кожна вибірка — це `open`, `read`, `close` по `/proc`, а у версії на оболонці ще й запуск `cat` та `awk`. При періоді 50 мілісекунд це непомітно, при 1 мілісекунді спостерігач починає помітно змагатися з піддослідним за процесор і псує саме те, що міряє. Якщо потрібна така роздільність — це знову означає, що пора переходити на трасувальні точки.
