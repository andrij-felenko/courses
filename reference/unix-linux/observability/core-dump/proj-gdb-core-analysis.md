# ⚙️ Практика розслідування краху: аналіз core dump у GDB

Цей практичний матеріал демонструє покроковий процес локалізації фатальної помилки некоректного використання пам'яті (Segmentation fault) у багатопотоковому C/C++ сервісі на основі згенерованого аварійного дампа та інструменту зневадження GDB (GNU Debugger).

## 1. Сценарій: аварія у багатопотоковому сервісі обробки пакетів

Уявіть практичну ситуацію: розробляється високонавантажений серверний сервіс обробки мережевих пакетів. Сервіс обробляє вхідний потік даних у декількох паралельних потоках виконання (`POSIX threads`). Під час роботи під навантаженням сервіс раптово припиняє виконання з системним повідомленням `Segmentation fault (core dumped)`.

Причиною краху є стан гонки (race condition), при якому один із потоків обнуляє або звільняє вказівник на спільний буфер даних у момент, коли інший потік намагається прочитати вміст за цим вказівником.

Нижче наведено повний вихідний код тестової програми, яка відтворює даний випадок аварії. Код представлено у двох варіантах — ідіоматичний C++ із використанням розумних вказівників `std::shared_ptr` та стандартних потоків `std::thread`, а також класичний C із використанням бібліотеки `pthread`.

:::tabs
== C++
```cpp
#include <iostream>
#include <vector>
#include <thread>
#include <memory>
#include <chrono>

struct PacketHeader {
    uint32_t magic;
    uint32_t payload_len;
    char* payload_ptr;
};

void process_packet(std::shared_ptr<PacketHeader> pkt, int thread_id) {
    // Невелика затримка для імітації паралельної роботи
    std::this_thread::sleep_for(std::chrono::milliseconds(50 * thread_id));
    
    if (thread_id == 2) {
        // Штучна помилка: обнуляємо вказівник у 2-му потоці без синхронізації
        pkt->payload_ptr = nullptr;
    }
    
    // Спроба зчитати дані за вказівником викликає SIGSEGV у 2-му або суміжних потоках
    std::cout << "Thread " << thread_id 
              << " byte: " << static_cast<int>(pkt->payload_ptr[0]) 
              << std::endl;
}

int main() {
    char data_buffer[] = "CRASH_DATA_PAYLOAD";
    auto pkt = std::make_shared<PacketHeader>();
    pkt->magic = 0xDEADBEEF;
    pkt->payload_len = sizeof(data_buffer);
    pkt->payload_ptr = data_buffer;

    std::vector<std::thread> workers;
    for (int i = 1; i <= 4; ++i) {
        workers.emplace_back(process_packet, pkt, i);
    }

    for (auto& t : workers) {
        if (t.joinable()) {
            t.join();
        }
    }
    return 0;
}
```
== C
```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdint.h>

typedef struct {
    uint32_t magic;
    uint32_t payload_len;
    char* payload_ptr;
} packet_header_t;

typedef struct {
    packet_header_t* pkt;
    int thread_id;
} thread_arg_t;

void* process_packet(void* arg) {
    thread_arg_t* tinfo = (thread_arg_t*)arg;
    usleep(50000 * tinfo->thread_id);
    
    if (tinfo->thread_id == 2) {
        // Штучна помилка: обнуляємо вказівник у 2-му потоці без м'ютекса
        tinfo->pkt->payload_ptr = NULL;
    }
    
    // Спроба зчитати дані за вказівником викликає SIGSEGV у потоці
    printf("Thread %d byte: %d\n", tinfo->thread_id, tinfo->pkt->payload_ptr[0]);
    return NULL;
}

int main(void) {
    char data_buffer[] = "CRASH_DATA_PAYLOAD";
    packet_header_t pkt = {
        .magic = 0xDEADBEEF,
        .payload_len = sizeof(data_buffer),
        .payload_ptr = data_buffer
    };

    pthread_t threads[4];
    thread_arg_t targs[4];

    for (int i = 0; i < 4; ++i) {
        targs[i].pkt = &pkt;
        targs[i].thread_id = i + 1;
        pthread_create(&threads[i], NULL, process_packet, &targs[i]);
    }

    for (int i = 0; i < 4; ++i) {
        pthread_join(threads[i], NULL);
    }
    return 0;
}
```
:::

## 2. Скомпілювання з відлагоджувальною інформацією DWARF

Для забезпечення придатності аварійного дампа до глибокого аналізу програму обов'язково необхідно скомпільувати з включенням таблиць відлагоджувальної інформації DWARF. 

У компіляторах `gcc` та `g++` це виконується за допомогою прапора `-g` (або `-g3` для включення відображення макросів препроцесора). Також на етапі відлагодження рекомендується вимикати оптимізації компілятора прапором `-O0`, щоб запобігти інлайнінгу функцій, агресивній інструкційній реорганізації та видаленню стекових фреймів.

При компіляції оптимізованого коду (наприклад із прапором `-O2`) частина локальних змінних може бути оптимізована у процесорних регістрах або видалена, через що GDB виводитиме значення `<optimized out>`. Для розслідування аварій у продакшн-бінарниках із відокремленими символами (stripped binaries) використовують сервери `debuginfod` або завантажують файли символів `.debug` окремо.

Виконуємо компіляцію та запуск програми у консолі Linux:

```bash
# Складання C++ версії з прапором -g та підтримкою потоків
$ g++ -g -O0 -pthread crash_demo.cpp -o crash_demo

# Перевіряємо увімкнення генерації аварійних дампів для поточної сесії
$ ulimit -c unlimited

# Запускаємо програму до виникнення аварійного завершення
$ ./crash_demo
Segmentation fault (core dumped)
```

За допомогою системної утиліти `coredumpctl` перевіряємо, що ядро та демон `systemd-coredump` успішно перехопили аварію та зберегли дамп:

```bash
$ coredumpctl list crash_demo
TIME                            PID   UID   GID SIG COREFILE EXE
Fri 2026-08-14 14:00:00 EEST  14230  1000  1000  11 present  /home/user/crash_demo
```

## 3. Покроковий розбір аварійного дампа в GDB

Відкриваємо збережений файл аварійного дампа в інструменті GDB. Це можна зробити або автоматично через утиліту `coredumpctl debug crash_demo`, або шляхом прямого передавання шляху до виконуваного бінарника та файлу `core`:

```bash
$ gdb ./crash_demo /var/lib/systemd/coredump/core.crash_demo.14230
```

### Крок 3.1. Первинна інспекція місця аварії

При відкритті дампа GDB автоматично зчитує заголовок `PT_NOTE` та повідомляє сигнал і рядок вихідного коду, на якому припинилося виконання:

```text
Core was generated by `./crash_demo'.
Program terminated with signal SIGSEGV, Segmentation fault.
#0  0x00005555555553b4 in process_packet (pkt=..., thread_id=2) at crash_demo.cpp:21
21          std::cout << "Thread " << thread_id << " byte: " << static_cast<int>(pkt->payload_ptr[0]) << std::endl;
```

З повідомлення випливає, що крах стався у функції `process_packet` на рядку 21 вихідного файлу `crash_demo.cpp`.

### Крок 3.2. Аналіз активних потоків процесу (`info threads`)

Оскільки програма є багатопотоковою, критично важливо з'ясувати стан усіх потоків у момент краху. За допомогою команди `info threads` виводимо список усіх LWP (Lightweight Processes):

```text
(gdb) info threads
  Id   Target Id                                       Frame 
* 1    Thread 0x7ffff7a00640 (LWP 14232) "crash_demo"  0x00005555555553b4 in process_packet (pkt=..., thread_id=2) at crash_demo.cpp:21
  2    Thread 0x7ffff7c00640 (LWP 14231) "crash_demo"  0x00007ffff7e4369d in syscall () from /lib64/libc.so.6
  3    Thread 0x7ffff6800640 (LWP 14233) "crash_demo"  0x00007ffff7e4369d in syscall () from /lib64/libc.so.6
  4    Thread 0x7ffff600640 (LWP 14234) "crash_demo"  0x00007ffff7e4369d in syscall () from /lib64/libc.so.6
```

Символ `*` вказує на потік №1 (LWP 14232), у якому безпосередньо виникла апаратна помилка `SIGSEGV`.

Для отримання повної картини виконання для всіх потоків одночасно застосовуємо команду `thread apply all backtrace`:

```text
(gdb) thread apply all backtrace

Thread 1 (Thread 0x7ffff7a00640 (LWP 14232)):
#0  0x00005555555553b4 in process_packet (pkt=..., thread_id=2) at crash_demo.cpp:21
#1  0x0000555555555678 in std::__invoke_impl<void, void(*)(std::shared_ptr<PacketHeader>, int), std::shared_ptr<PacketHeader>, int> ...
#2  0x00007ffff7ec8a62 in start_thread (arg=<optimized out>) at pthread_create.c:442
#3  0x00007ffff7f4aa4c in clone () from /lib64/libc.so.6

Thread 2 (Thread 0x7ffff7c00640 (LWP 14231)):
#0  0x00007ffff7e4369d in syscall () from /lib64/libc.so.6
#1  0x0000555555555500 in main () at crash_demo.cpp:35
```

### Крок 3.3. Вивчення локальних змінних та вмісту пам'яті (`bt full`, `print`)

Виконуємо команду `bt full` для інспекції стекового фрейму №0 та аналізу локальних змінних:

```text
(gdb) bt full
#0  0x00005555555553b4 in process_packet (pkt=std::shared_ptr<PacketHeader> (use count 5, weak count 0) = {...}, thread_id=2) at crash_demo.cpp:21
        pkt = std::shared_ptr<PacketHeader> (use count 5, weak count 0) = {
          get() = 0x55555556beb0
        }

(gdb) print *pkt.get()
$1 = {
  magic = 3735928559, 
  payload_len = 19, 
  payload_ptr = 0x0
}
```

Вивчення полів об'єкта `PacketHeader` надає вичерпну відповідь про причину краху:
- Поле `magic` містить очікуваний сигнатурний маркер `0xDEADBEEF` (3735928559).
- Поле `payload_len` дорівнює `19` байтам.
- Однак поле `payload_ptr` має значення `0x0` (`nullptr`).

Спроба виразу `pkt->payload_ptr[0]` намагається прочитати перший байт за адресою `0x0000000000000000`, що викликає фатальну помилку порушення сегментації `SIGSEGV`.

### Крок 3.4. Перевірка регістрів процесора та дамп пам'яті (`info registers`, `x/`)

Для підтвердження гіпотези на рівні машинних інструкцій виводимо вміст CPU-регістрів у момент аварії за допомогою `info registers`:

```text
(gdb) info registers
rax            0x0                 0
rbx            0x2                 2
rcx            0x7ffff7f00123      140737353072931
rdx            0x55555556beb0      93824992444080
rsi            0x2                 2
rdi            0x0                 0
rbp            0x7ffff79ffa60      0x7ffff79ffa60
rsp            0x7ffff79ff9c0      0x7ffff79ff9c0
rip            0x00005555555553b4  0x5555555553b4 <process_packet+164>
eflags         0x10246             [ PF ZF IF RF ]
```

Регістр `RIP` (Instruction Pointer) вказує на ассемблерну інструкцію зсуву `+164` всередині функції `process_packet`, а в регістрі `RAX` збережено нульове значення `0x0`, яке використовувалося для непрямого витягування байта даних.

За допомогою команди дампа пам'яті `x/` (examine) можна проінспектувати прямо за адресою пам'яті `0x55555556beb0`, де розташовано об'єкт `PacketHeader`:

```text
(gdb) x/4xg 0x55555556beb0
0x55555556beb0: 0x00000013deadbeef  0x0000000000000000
0x55555556bec0: 0x0000000000000000  0x0000000000000021
```

Перші 8 байтів розгортаються як `magic = 0xDEADBEEF` та `payload_len = 0x13` (19), а наступні 8 байтів є нульовими (`payload_ptr = 0x0`).

### Крок 3.5. Розбір дисасембльованого коду (`disassemble`)

Для того щоб переконатися, яка саме інструкція викликала переривання, виконаємо дисасемблювання поточного контексту:

```text
(gdb) disassemble process_packet
Dump of assembler code for function process_packet:
   0x00005555555553a0 <+144>: mov    -0x18(%rbp),%rax
   0x00005555555553a4 <+148>: mov    0x8(%rax),%rax
=> 0x00005555555553b4 <+164>: movzbl (%rax),%eax
   0x00005555555553b7 <+167>: movsbl %al,%edx
End of assembler dump.
```

Вказувальна стрілка `=>` посилається на інструкцію `movzbl (%rax),%eax`. Оскільки значення регістра `%rax` у цей момент дорівнювало `0`, спроба прочитати пам'ять `(%rax)` завершилася генерацією апаратного переривання захисту пам'яті.

## 4. Специфічні випадки аналізу аварійних дампів

У практичній роботі системного програміста зустрічаються складніші випадки краху, ніж розіменування нульового вказівника:

### Пошкодження стеку (Stack Corruption / Stack Overflow)

Якщо програма переповнила стековий буфер або пошкодила адресу повернення на стеку, команда `backtrace` виведе серію знаків питаннь `?? ()` замість імен функцій. 

У цьому випадку аналіз вимагає вручну оглядати регістри `RSP` та `RBP`, а також дампувати пам'ять довкола стекового вказівника (`x/32xg $rsp`), відшукуючи збережені адреси повернення, що належать сегменту коду `.text`.

### Пошкодження купи (Heap Corruption / Use-After-Free)

При повторному звільненні пам'яті (`double free`) або записі за межі виділеного блоку аллокатор `glibc malloc` генерує сигнал `SIGABRT` через функцію `abort()`. У цьому разі дамп зберігає внутрішні структури `malloc_chunk`, що дозволяє проінспектувати цілісність службових метаданих аллокатора.

## 5. Підсумки розслідування та спосіб виправлення

Завдяки посмертному аналізу аварійного дампа у GDB вдалося:
1. Точно встановити потік процесу (TID `14232`), у якому виникла помилка.
2. З'ясувати, що причиною падіння є не пошкодження стеку чи витік пам'яті, а конкретне обнулення вказівника `payload_ptr` у 2-му потоці без використання механізмів синхронізації (`std::mutex` чи `pthread_mutex_t`).
3. Виправлення даної помилки вимагає захисту спільного стану структури `PacketHeader` за допомогою примітивів взаємного виключення чи переходу до незмінних (immutable) даних.
