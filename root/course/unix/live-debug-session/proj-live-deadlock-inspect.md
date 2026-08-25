# ⚙️ Діагностика та розблокування взаємного блокування на живому сервері

Цей практичний практикум демонструє повний цикл польової діагностики та порятунку багатопотокового мережевого сервісу, який перестав відповідати на запити через взаємне блокування (дедлок) робочих потоків. У ньому розбирається практичне відтворення дедлоку, попередня експрес-оцінка через псевдофайлову систему `/proc`, неінвазивне підключення через GDB, аналіз стеків викликів, знаходження конфліктних адрес м'ютексів за допомогою внутрішніх структур glibc, зняття блокування прямо в оперативній пам'яті процесу та безпечне від'єднання без переривання роботи сервера.

## 1. Архітектура проблемного сервісу та сценарій збою

Уявімо платіжний сервіс `payment-gateway`, який виконує паралельні грошові перекази між банківськими рахунками клієнтів. Кожен банківський рахунок захищений окремим екземпляром м'ютекса (`pthread_mutex_t` у C або `std::mutex` у C++). Щоб гарантувати узгодженість балансів, робочий потік транзакції зобов'язаний заблокувати обидва рахунки: рахунок відправника (зняття коштів) та рахунок отримувача (зарахування коштів).

Якщо транзакція 1 переказує кошти з рахунку `A` на рахунок `B`, а транзакція 2 одночасно переказує кошти з рахунку `B` на рахунок `A`, виникає класична ситуація циклічного порушення порядку захоплення ресурсів:
- Потік 1 успішно захоплює м'ютекс рахунку `A` і робить спробу захопити м'ютекс рахунку `B`.
- Потік 2 практично одночасно захоплює м'ютекс рахунку `B` і намагається захопити м'ютекс рахунку `A`.
- Жоден із потоків не може продовжити виконання, оскільки потрібний ресурс утримується іншим потоком. Обидва потоки переходять у ядро через системний виклик `futex(FUTEX_WAIT_PRIVATE)` і зависають назавжди.

У реальному сервісі це призводить до поступового вичерпання пулу робочих потоків, накопичення невідповідних з'єднань і повної зупинки обробки запитів.

Нижче наведено повний робочий код демонстраційного сервера:

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/prctl.h>

typedef struct {
    uint64_t account_id;
    double balance;
    pthread_mutex_t lock;
} Account;

typedef struct {
    uint64_t tx_id;
    Account *src;
    Account *dst;
    double amount;
    volatile bool cancel_flag;
} TransferTask;

static Account g_account_a = { .account_id = 101, .balance = 10000.0, .lock = PTHREAD_MUTEX_INITIALIZER };
static Account g_account_b = { .account_id = 202, .balance = 10000.0, .lock = PTHREAD_MUTEX_INITIALIZER };

static void *worker_thread_1(void *arg) {
    TransferTask *task = (TransferTask *)arg;
    pthread_setname_np(pthread_self(), "tx-worker-A2B");

    printf("[Worker 1] Стартує переказ #%lu: рахунок %lu -> %lu\n",
           task->tx_id, task->src->account_id, task->dst->account_id);

    pthread_mutex_lock(&task->src->lock);
    printf("[Worker 1] Захоплено рахунок %lu, пауза перед наступним захопленням...\n", task->src->account_id);
    usleep(100000); // 100 мс затримки для надійного відтворення гонитви

    printf("[Worker 1] Спроба захопити рахунок %lu...\n", task->dst->account_id);
    pthread_mutex_lock(&task->dst->lock);

    // Критична секція переказу коштів
    task->src->balance -= task->amount;
    task->dst->balance += task->amount;

    pthread_mutex_unlock(&task->dst->lock);
    pthread_mutex_unlock(&task->src->lock);

    printf("[Worker 1] Переказ #%lu успішно завершено!\n", task->tx_id);
    return NULL;
}

static void *worker_thread_2(void *arg) {
    TransferTask *task = (TransferTask *)arg;
    pthread_setname_np(pthread_self(), "tx-worker-B2A");

    printf("[Worker 2] Стартує переказ #%lu: рахунок %lu -> %lu\n",
           task->tx_id, task->src->account_id, task->dst->account_id);

    pthread_mutex_lock(&task->src->lock);
    printf("[Worker 2] Захоплено рахунок %lu, пауза перед наступним захопленням...\n", task->src->account_id);
    usleep(100000); // 100 мс затримки

    printf("[Worker 2] Спроба захопити рахунок %lu...\n", task->dst->account_id);
    pthread_mutex_lock(&task->dst->lock);

    // Критична секція переказу коштів
    task->src->balance -= task->amount;
    task->dst->balance += task->amount;

    pthread_mutex_unlock(&task->dst->lock);
    pthread_mutex_unlock(&task->src->lock);

    printf("[Worker 2] Переказ #%lu успішно завершено!\n", task->tx_id);
    return NULL;
}

int main(void) {
    // Дозволяємо трасування не-нащадкам для сумісності з Yama ptrace_scope=1
    prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0);

    printf("=== Платіжний вузол запущено (PID: %d) ===\n", getpid());
    printf("Адреси м'ютексів: Account A (%p), Account B (%p)\n",
           (void *)&g_account_a.lock, (void *)&g_account_b.lock);

    TransferTask task1 = { .tx_id = 9001, .src = &g_account_a, .dst = &g_account_b, .amount = 150.0, .cancel_flag = false };
    TransferTask task2 = { .tx_id = 9002, .src = &g_account_b, .dst = &g_account_a, .amount = 300.0, .cancel_flag = false };

    pthread_t th1, th2;
    pthread_create(&th1, NULL, worker_thread_1, &task1);
    pthread_create(&th2, NULL, worker_thread_2, &task2);

    pthread_join(th1, NULL);
    pthread_join(th2, NULL);

    printf("Усі транзакції завершено. Баланс A: %.2f, B: %.2f\n",
           g_account_a.balance, g_account_b.balance);
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <chrono>
#include <cstdint>
#include <pthread.h>
#include <unistd.h>
#include <sys/prctl.h>

struct Account {
    uint64_t account_id;
    double balance;
    std::mutex lock;
};

struct TransferTask {
    uint64_t tx_id;
    Account& src;
    Account& dst;
    double amount;
    volatile bool cancel_flag{false};
};

static Account g_account_a{101, 10000.0, {}};
static Account g_account_b{202, 10000.0, {}};

static void worker_func_1(TransferTask& task) {
    pthread_setname_np(pthread_self(), "tx-worker-A2B");
    std::cout << "[Worker 1] Стартує переказ #" << task.tx_id
              << ": рахунок " << task.src.account_id << " -> " << task.dst.account_id << "\n";

    task.src.lock.lock();
    std::cout << "[Worker 1] Захоплено рахунок " << task.src.account_id << ", пауза перед захопленням...\n";
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "[Worker 1] Спроба захопити рахунок " << task.dst.account_id << "...\n";
    task.dst.lock.lock();

    task.src.balance -= task.amount;
    task.dst.balance += task.amount;

    task.dst.lock.unlock();
    task.src.lock.unlock();
    std::cout << "[Worker 1] Переказ #" << task.tx_id << " успішно завершено!\n";
}

static void worker_func_2(TransferTask& task) {
    pthread_setname_np(pthread_self(), "tx-worker-B2A");
    std::cout << "[Worker 2] Стартує переказ #" << task.tx_id
              << ": рахунок " << task.src.account_id << " -> " << task.dst.account_id << "\n";

    task.src.lock.lock();
    std::cout << "[Worker 2] Захоплено рахунок " << task.src.account_id << ", пауза перед захопленням...\n";
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "[Worker 2] Спроба захопити рахунок " << task.dst.account_id << "...\n";
    task.dst.lock.lock();

    task.src.balance -= task.amount;
    task.dst.balance += task.amount;

    task.dst.lock.unlock();
    task.src.lock.unlock();
    std::cout << "[Worker 2] Переказ #" << task.tx_id << " успішно завершено!\n";
}

int main() {
    prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0);

    std::cout << "=== Платіжний вузол запущено (PID: " << getpid() << ") ===\n";
    std::cout << "Адреси м'ютексів: Account A (" << &g_account_a.lock
              << "), Account B (" << &g_account_b.lock << ")\n";

    TransferTask task1{9001, g_account_a, g_account_b, 150.0};
    TransferTask task2{9002, g_account_b, g_account_a, 300.0};

    std::thread th1(worker_func_1, std::ref(task1));
    std::thread th2(worker_func_2, std::ref(task2));

    th1.join();
    th2.join();

    std::cout << "Усі транзакції завершено. Баланс A: " << g_account_a.balance
              << ", B: " << g_account_b.balance << "\n";
    return 0;
}
```
:::

## 2. Збірка з налагоджувальними символами та запуск процесу

Для того щоб налагоджувач міг точно зіставити асемблерні адреси з іменами функцій і рядками вихідного коду, скомпілюємо бінарний файл із прапорцем збереження повної інформації DWARF рівня 3 (`-g3`) та стандартною оптимізацією продуктивності `-O2`:

```bash
g++ -O2 -g3 -pthread payment_deadlock.cpp -o payment_deadlock
./payment_deadlock
```

Після запуску програма друкує свій PID та адреси внутрішніх об'єктів блокування, після чого потоки входять у взаємне блокування і повністю перестають подавати ознаки життя:

```text
=== Платіжний вузол запущено (PID: 24890) ===
Адреси м'ютексів: Account A (0x55d1a8122048), Account B (0x55d1a8122078)
[Worker 1] Стартує переказ #9001: рахунок 101 -> 202
[Worker 2] Стартує переказ #9002: рахунок 202 -> 101
[Worker 1] Захоплено рахунок 101, пауза перед захопленням...
[Worker 2] Захоплено рахунок 202, пауза перед захопленням...
[Worker 1] Спроба захопити рахунок 202...
[Worker 2] Спроба захопити рахунок 101...
```

Утиліти моніторингу `top` та `ps` показують нульове використання CPU (`0.0% CPU`), оскільки обидва робочі потоки сплять у черзі очікування футекса ядра і не споживають процесорного часу.

## 3. Експрес-діагностика через псевдофайлову систему /proc

Перед тим як підключати важкий налагоджувач GDB, системний інженер може миттєво підтвердити факт блокування потоків через псевдофайлову систему ядра `/proc`:

```bash
cat /proc/24890/task/*/wchan
```

Команда виводить ім'я внутрішньої функції ядра, на якій заблокований кожен потік процесу. Якщо у відповіді фігурує рядок `futex_wait_queue_me` або `futex_wait`, це означає, що потік добровільно поступився процесором і чекає сигналу пробудження від іншого потоку:

```text
futex_wait_queue_me
futex_wait_queue_me
futex_wait_queue_me
```

Також файл `/proc/24890/status` демонструє, що лічильник добровільних перемикань контексту `voluntary_ctxt_switches` перестав зростати, що остаточно підтверджує зависання.

## 4. Підключення GDB та виявлення конфлікту блокувань

У паралельній сесії термінала підключаємося до процесу за отриманим ідентифікатором PID:

```bash
sudo gdb -p 24890
```

GDB надсилає `PTRACE_ATTACH`, ядро зупиняє всі нитки процесу сигналом `SIGSTOP`, і оператор отримує інтерактивний командний рядок.

Насамперед перевіряємо список усіх відомих системі потоків:

```text
(gdb) info threads
  Id   Target Id                                   Frame 
* 1    Thread 0x7f4a81b2e740 (LWP 24890 "payment_deadloc") 0x00007f4a81c4e976 in __futex_abstimed_wait_common64 () from /lib/x86_64-linux-gnu/libc.so.6
  2    Thread 0x7f4a8132d640 (LWP 24891 "tx-worker-A2B")  0x00007f4a81c4e976 in __futex_abstimed_wait_common64 () from /lib/x86_64-linux-gnu/libc.so.6
  3    Thread 0x7f4a80b2c640 (LWP 24892 "tx-worker-B2A")  0x00007f4a81c4e976 in __futex_abstimed_wait_common64 () from /lib/x86_64-linux-gnu/libc.so.6
```

Зі звіту видно три потоки: головний потік 1 чекає завершення роботи нащадків у функції `join()`, тоді як потоки 2 (`tx-worker-A2B`) та 3 (`tx-worker-B2A`) знаходяться у системному виклику очікування футекса `__futex_abstimed_wait_common64`.

Виконуємо команду отримання групового бектрейсу:

```text
(gdb) thread apply all bt

Thread 3 (Thread 0x7f4a80b2c640 (LWP 24892 "tx-worker-B2A")):
#0  0x00007f4a81c4e976 in __futex_abstimed_wait_common64 () from /lib/x86_64-linux-gnu/libc.so.6
#1  0x00007f4a81c51238 in __pthread_mutex_lock_wait () from /lib/x86_64-linux-gnu/libc.so.6
#2  0x000055d1a8121345 in std::mutex::lock (this=0x55d1a8122048 <g_account_a+40>)
#3  0x000055d1a81215b0 in worker_func_2 (task=...) at payment_deadlock.cpp:52
#4  ...

Thread 2 (Thread 0x7f4a8132d640 (LWP 24891 "tx-worker-A2B")):
#0  0x00007f4a81c4e976 in __futex_abstimed_wait_common64 () from /lib/x86_64-linux-gnu/libc.so.6
#1  0x00007f4a81c51238 in __pthread_mutex_lock_wait () from /lib/x86_64-linux-gnu/libc.so.6
#2  0x000055d1a8121345 in std::mutex::lock (this=0x55d1a8122078 <g_account_b+40>)
#3  0x000055d1a81214c0 in worker_func_1 (task=...) at payment_deadlock.cpp:32
#4  ...
```

Аналіз вихідного тексту чітко розкриває граф взаємної залежності:
- Потік 2 (LWP 24891) заблокований у спробі захопити м'ютекс `0x55d1a8122078` (`g_account_b.lock`), але вже утримує м'ютекс `0x55d1a8122048` (`g_account_a.lock`).
- Потік 3 (LWP 24892) заблокований у спробі захопити м'ютекс `0x55d1a8122048` (`g_account_a.lock`), але вже утримує м'ютекс `0x55d1a8122078` (`g_account_b.lock`).

Ми маємо замкнений цикл взаємного очікування між потоками 2 і 3.

## 5. Перевірка власника м'ютекса через внутрішні структури glibc

У бібліотеці glibc об'єкт м'ютекса `pthread_mutex_t` містить поле `__data.__owner`, яке зберігає числовий ідентифікатор TID потоку, що наразі володіє цим блокуванням. Роздрукуємо структури обох м'ютексів безпосередньо:

```text
(gdb) p *(pthread_mutex_t*)0x55d1a8122048
$1 = {
  __data = {
    __lock = 2,
    __count = 0,
    __owner = 24891,
    __nusers = 1,
    __kind = 0,
    __spins = 0,
    __elision = 0,
    __list = { __next = 0x0 }
  }
}

(gdb) p *(pthread_mutex_t*)0x55d1a8122078
$2 = {
  __data = {
    __lock = 2,
    __count = 0,
    __owner = 24892,
    __nusers = 1,
    __kind = 0,
    __spins = 0,
    __elision = 0,
    __list = { __next = 0x0 }
  }
}
```

Значення поля `__owner` остаточно підтверджує діагноз:
- М'ютекс рахунку `A` захоплений потоком із системним LWP `24891` (Worker 1).
- М'ютекс рахунку `B` захоплений потоком із системним LWP `24892` (Worker 2).

## 6. Інспекція фреймів та розблокування процесу на льоту

Перемикаємося на потік 2 для дослідження локальних змінних активного кадру:

```text
(gdb) thread 2
[Switching to thread 2 (Thread 0x7f4a8132d640 (LWP 24891))]
(gdb) frame 3
#3  0x000055d1a81214c0 in worker_func_1 (task=...) at payment_deadlock.cpp:32
32          task.dst.lock.lock();
(gdb) info args
task = @0x7ffdb83210e0: {
  tx_id = 9001, 
  src = @0x55d1a8122020, 
  dst = @0x55d1a8122050, 
  amount = 150, 
  cancel_flag = false
}
```

У критичній виробничій ситуації, коли перезапуск процесу призведе до втрати клієнтських транзакцій, інженер може розблокувати завислий стан безпосередньо у пам'яті через виклик функції `unlock()` або скидання стану блокування:

```text
(gdb) call g_account_a.lock.unlock()
$3 = void
(gdb) print "М'ютекс Account A примусово звільнено на льоту"
```

Коли м'ютекс `g_account_a` звільняється в пам'яті, потік 3 (Worker 2) отримує змогу успішно вийти з виклику `futex_wait`, захопити м'ютекс, провести переказ, після чого звільнити обидва м'ютекси, що автоматично розблокує потік 2.

## 7. Безпечне від'єднання та верифікація

Після зняття блокування обов'язково виконуємо команду `detach`, яка відновлює нормальний стан планування в ядрі:

```text
(gdb) detach
Detaching from program: /path/to/payment_deadlock, process 24890
[Inferior 1 (process 24890) detached]
(gdb) quit
```

У терміналі з працюючою програмою ви бачите, як сервіс миттєво прокидається і завершує обробку:

```text
[Worker 2] Переказ #9002 успішно завершено!
[Worker 1] Переказ #9001 успішно завершено!
Усі транзакції завершено. Баланс A: 10150.00, B: 9850.00
```

Процес успішно завершив роботу без збоїв і без втрати фінансових даних.

## 8. Архітектурне виправлення у вихідному коді

Для остаточного усунення проблеми в кодовій базі стандарт C++11 пропонує використання функції `std::lock`, яка використовує алгоритм уникнення дедлоків (Deadlock Avoidance Algorithm):

```cpp
// Коректне одночасне захоплення кількох м'ютексів без ризику взаємного блокування:
std::unique_lock<std::mutex> lock_src(task.src.lock, std::defer_lock);
std::unique_lock<std::mutex> lock_dst(task.dst.lock, std::defer_lock);
std::lock(lock_src, lock_dst); // гарантує однаковий глобальний порядок захоплення

// Або в стандарті C++17 через RAII scoped_lock:
// std::scoped_lock lock(task.src.lock, task.dst.lock);
```

Цей підхід повністю ліквідує можливість циклічного очікування на рівні компілятора та рантайму.
