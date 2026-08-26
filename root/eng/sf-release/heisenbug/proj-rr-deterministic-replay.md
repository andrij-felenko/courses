# ⚙️ Детермінований запис і відтворення виконання через Mozilla rr

Цей практичний посібник описує методику детермінованого запису та покрокового зворотного налагодження (*Time-Travel Debugging*) складних низькорівневих дефектів за допомогою інструменту `Mozilla rr`. Ви дізнаєтеся, як захопити плаваючий гейзенбаг під час першого ж його прояву та гарантовано відтворити його стан біт-у-біт у відладчику GDB необмежену кількість разів.

## Межа можливостей класичних відладчиків

Коли програма стикається з рідкісним збоєм пам'яті (наприклад, пошкодження покажчика або псування заголовка кулі), класичний підхід до налагодження полягає у запуску процесу всередині інтерактивного відладчика GDB з установкою точок зупинки (*breakpoints*) або точок спостереження за пам'яттю (*watchpoints*).

Проте для гейзенбагів цей підхід виявляється безпорадним із двох причин:
1. **Зміна часових характеристик.** Точки зупинки GDB реалізуються шляхом заміни одного байта інструкції на опкод `0xCC` (`int 3`). Обробка сигналу `SIGTRAP` ядром та передача керування процесу відладчика займає сотні мікросекунд, що повністю руйнує оригінальний порядок чередування потоків і змушує помилку зникати.
2. **Проблема «стріли часу».** Коли програма падає з помилкою `SIGSEGV` на розіменуванні покажчика `0x00000028`, аварія — це лише *кінцевий наслідок*. Сама помилка (запис сміття в пам'ять) сталася 5 мільйонів інструкцій тому в іншому модулі. Звичайний відладчик не може повернути виконання назад, щоб показати, хто саме виконав цей фатальний запис.

Інструмент **Mozilla rr** (*Record and Replay*) розв'язує обидві проблеми: він записує нативне виконання з мінімальним накладним оверхедом (зазвичай менше 1.2–1.5×), а потім дозволяє запускати процес у зворотному напрямку (*reverse execution*).

## Архітектурний фундамент: детермінізм та апаратні лічильники

Більшість інструкцій сучасного процесора x86-64 є суворо детермінованими: якщо регістри `RAX` і `RBX` містять значення 5 і 10, інструкція `ADD RAX, RBX` завжди встановить `RAX = 15` і встановить однакові прапорці процесора.

Щоб точно відтворити виконання мільярдів інструкцій, `rr` не потрібно записувати кожну зміну регістрів. Достатньо зафіксувати лише **джерела недетермінізму**:
1. **Результати системних викликів** (`read`, `epoll_wait`, `gettimeofday`): байти, які повернуло ядро ОС, зберігаються в журналі запису.
2. **Асинхронні сигнали ядра** (`SIGALRM`, `SIGCHLD`, `SIGIO`): фіксується точний номер інструкції, на якій сигнал перервав потік.
3. **Недетерміновані інструкції CPU** (`rdtsc`, `rdrand`, `cpuid`): перехоплюються та замінюються на зафіксовані значення.
4. **Порядок планування потоків:** багатопотоковий застосунок під час запису виконується на одному фізичному ядрі процесора з детермінованим квантуванням часу.

### Як rr рахує інструкції: магія PMU
Для фіксації точного моменту переривання `rr` використовує модуль апаратного моніторингу продуктивності процесора (англ. *Performance Monitoring Unit*, PMU).

`rr` налаштовує апаратний лічильник процесора Intel на подію **`BR_INST_RETIRED.CONDITIONAL`** (кількість виконаних умовних переходів). Процесор генерує апаратне переривання (*Performance Monitoring Interrupt*, PMI), коли лічильник досягає заданого значення. Це дозволяє зупиняти виконання під час відтворення на тій самій інструкції з абсолютною точністю.

Для синхронізації сторінок розділюваної пам'яті (shared memory між процесами) `rr` скидає біти дозволу на запис у таблицях сторінок MMU. Перша ж спроба модифікації сторінки викликає `SIGSEGV` ядра, `rr` перехоплює подію, зберігає дельту змінених байтів у журнал трейсу і відновлює доступ.

## Практичний сценарій: полювання на розбитий стек

Розглянемо реалістичний приклад програми, де функція обробки мережевих пакетів містить приховане переповнення буфера на стеку (*stack buffer overflow*), яке пошкоджує вказівник повернення, але призводить до аварії лише за специфічної довжини вхідного пакету.

:::tabs
```c
// packet_worker.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

typedef struct {
    char header[8];
    void (*handler)(const char *);
} PacketContext;

void default_logger(const char *msg) {
    printf("[LOG] %s\n", msg);
}

void parse_payload(const char *input, size_t len) {
    char local_buffer[16];
    // Прихована помилка: відсутність перевірки меж len
    // Якщо len > 16, запис затирає сусідні структури на стеку
    memcpy(local_buffer, input, len);
    local_buffer[15] = '\0';
}

void process_network_event(int event_id) {
    PacketContext ctx;
    memcpy(ctx.header, "PKT_HDR", 8);
    ctx.handler = default_logger;

    // Псевдовипадковий генератор розміру для моделювання плаваючого збою
    size_t payload_len = 12 + (rand() % 16); // Довжина від 12 до 27 байтів

    char payload_data[32];
    memset(payload_data, 'A', sizeof(payload_data));

    // Якщо payload_len > 24, пошкоджується покажчик ctx.handler
    parse_payload(payload_data, payload_len);

    if (event_id % 1000 == 0) {
        ctx.handler("Packet processed successfully.");
    }
}

int main(int argc, char **argv) {
    srand(time(NULL));
    printf("[START] Processing network stream...\n");

    for (int i = 0; i < 50000; ++i) {
        process_network_event(i);
    }

    printf("[FINISH] All packets processed without crash.\n");
    return 0;
}
```
```cpp
// packet_worker.cpp
#include <iostream>
#include <vector>
#include <cstring>
#include <functional>
#include <random>

struct PacketContext {
    char header[8]{'P','K','T','_','H','D','R','\0'};
    std::function<void(const char*)> handler;
};

void default_logger(const char* msg) {
    std::cout << "[LOG] " << msg << "\n";
}

void parse_payload(const char* input, size_t len) {
    char local_buffer[16];
    // Потенційне пошкодження стек-фрейму при len > 16
    std::memcpy(local_buffer, input, len);
    local_buffer[15] = '\0';
}

void process_network_event(int event_id, std::mt19937& rng) {
    PacketContext ctx;
    ctx.handler = default_logger;

    std::uniform_int_distribution<size_t> dist(12, 27);
    size_t payload_len = dist(rng);

    char payload_data[32];
    std::memset(payload_data, 'A', sizeof(payload_data));

    parse_payload(payload_data, payload_len);

    if (event_id % 1000 == 0 && ctx.handler) {
        ctx.handler("Packet processed successfully.");
    }
}

int main() {
    std::mt19937 rng(42);
    std::cout << "[START] Processing network stream...\n";

    for (int i = 0; i < 50000; ++i) {
        process_network_event(i, rng);
    }

    std::cout << "[FINISH] All packets processed successfully.\n";
    return 0;
}
```
:::

## Покрокова інструкція роботи з rr

### Крок 1: Підготовка середовища та компіляція
Збираємо застосунок з налагоджувальними символами (`-g`), але зберігаємо стандартний рівень оптимізації:

```bash
gcc -g -O2 packet_worker.c -o packet_worker
```

Для коректної роботи лічильників PMU у середовищі Linux необхідно дозволити доступ до підсистеми `perf_event`:
```bash
sudo sysctl kernel.perf_event_paranoid=1
```

### Крок 2: Запис виконання (Record)
Запускаємо програму під наглядом `rr`. Запис триває доти, доки застосунок не зазнає аварійного збою:

```bash
rr record ./packet_worker
```

Вивід у терміналі:
```text
[START] Processing network stream...
[LOG] Packet processed successfully.
[LOG] Packet processed successfully.
Segmentation fault (core dumped)
rr: Saving execution to trace directory `/home/user/.local/share/rr/packet_worker-0`.
```

Збій успішно зафіксовано. Усі зовнішні взаємодії, системні виклики та стани пам'яті збережено в компактний журнал у директорії трейсу.

### Крок 3: Запуск детермінованого відтворення (Replay)
Запускаємо сесію відтворення:

```bash
rr replay
```

`rr` запускає вбудований GDB-сервер і завантажує зафіксований слід. Програма зупиняється на першій інструкції точки входу:

```text
(rr) continue
Continuing.
[START] Processing network stream...
[LOG] Packet processed successfully.

Program received signal SIGSEGV, Segmentation fault.
0x4141414141414141 in ?? ()
```

Процес упав на спробі виконати інструкцію за адресою `0x4141414141414141` (шістнадцятковий код символів `'AAAA....'`), що підтверджує пошкодження вказівника функції `ctx.handler`.

### Крок 4: Подорож назад у часі (Time-Travel Debugging)
Тепер використовуємо головну перевагу `rr` — команди зворотного виконання.

Дізнаємося, у якому фреймі ми перебуваємо, та встановлюємо **точку спостереження за пам'яттю** (*hardware watchpoint*) на зіпсовану адресу:

```text
(rr) frame
#0  0x4141414141414141 in ?? ()

(rr) info registers rsp
rsp            0x7ffd9c81a248      0x7ffd9c81a248

(rr) watch -l *(void**)0x7ffd9c81a248
Hardware watchpoint 1: *(void**)0x7ffd9c81a248
```

Тепер запускаємо програму **НАЗАД У ЧАСІ** до моменту, коли в цю комірку пам'яті востаннє записувалися дані:

```text
(rr) reverse-continue
Continuing backwards.

Hardware watchpoint 1: *(void**)0x7ffd9c81a248

Old value = (void *) 0x4141414141414141
New value = (void *) 0x401160 <default_logger>
0x00007f31a8041289 in __memcpy_avx_unaligned () from /lib64/libc.so.6
```

`rr` миттєво відмотав виконання назад і зупинив процес рівно на інструкції `memcpy`, яка переповнила буфер!

Піднімаємося вгору по стеку викликів:
```text
(rr) backtrace
#0  0x00007f31a8041289 in __memcpy_avx_unaligned () from /lib64/libc.so.6
#1  0x00000000004011cb in parse_payload (input=0x7ffd9c81a280 'A' <repeats 32 times>, len=26) at packet_worker.c:20
#2  0x0000000000401242 in process_network_event (event_id=42000) at packet_worker.c:38
#3  0x0000000000401280 in main (argc=1, argv=0x7ffd9c81a3d8) at packet_worker.c:48
```

Дивимося на локальні змінні в рядку 20:
```text
(rr) frame 1
#1  0x00000000004011cb in parse_payload (input=..., len=26) at packet_worker.c:20
20      memcpy(local_buffer, input, len);

(rr) print sizeof(local_buffer)
$1 = 16
(rr) print len
$2 = 26
```

Причину виявлено з абсолютною математичною точністю: масив `local_buffer` розміром 16 байтів отримав на вхід 26 байтів, що призвело до затирання покажчика `ctx.handler` на стеку виклику `process_network_event`.

## Основні команди зворотного налагодження в rr

| Команда GDB / rr | Скорочення | Дія |
|---|---|---|
| `reverse-continue` | `rc` | Виконувати програму назад до найближчої точки зупинки або watchpoint |
| `reverse-step` | `rs` | Зробити один крок назад за рядками сирцевого коду (заходячи у функції) |
| `reverse-next` | `rn` | Зробити один крок назад (переступаючи виклики функцій) |
| `reverse-stepi` | `rsi` | Зробити один крок назад на рівні окремої машинної інструкції процесора |
| `reverse-finish` | `rf` | Виконати програму назад до точки виклику поточної функції |
| `when` | — | Показати поточний номер глобальної події в сліді запису |
| `seek <event>` | — | Миттєво переміститися до довільної точки сліду за номером події |

## Апаратні вимоги та обмеження Mozilla rr

Хоча `rr` є найпотужнішим інструментом локалізації плаваючих помилок, його архітектура має чітко окреслені межі застосування:
1. **Архітектура процесора:** `rr` вимагає процесорів Intel із підтримкою архітектурних лічильників продуктивності Nehalem або новіших (на процесорах AMD підтримується починаючи з архітектури Zen 2).
2. **Однопотокове квантування:** `rr` емулює багатопотоковість на одному ядрі, серіалізуючи потоки. Гонки даних, що залежать виключно від паралельного фізичного виконання на різних кешах одночасно (memory bus snooping), можуть маскуватися під час запису в `rr` (для їх ловлі краще підходить ThreadSanitizer).
3. **Віртуалізація:** Для роботи `rr` усередині віртуальних машин (наприклад, VMware або KVM) необхідно активувати в налаштуваннях гіпервізора наскрізну віртуалізацію лічильників PMU (*Virtual CPU Performance Counters*).

Поєднання попереднього виявлення через санітайзери (ASan / TSan) та точної локалізації через `rr` перетворює пошук найзаплутаніших гейзенбагів із лотереї на детермінований інженерний алгоритм.
