# ⚙️ Реалізація власного FIFO-планувальника на eBPF

Цей проєкт демонструє створення мінімального робочого планувальника завдань ядра Linux на основі `sched_ext`. Основна мета прикладу — показати повний практичний цикл розробки: від створення розширень BPF-коду ядра до написання завантажувача у просторі користувача та налаштування трасування.

Проєкт складається з двох ключових компонентів:
1. **BPF-програма ядра (`my_fifo.bpf.c`)**: Реалізує логіку черги FIFO (First In, First Out). Вона перехоплює події додавання завдань у систему та видачі їх на процесор, використовуючи механізм `BPF_PROG_TYPE_STRUCT_OPS`.
2. **Завантажувач у просторі користувача (User-space Loader)**: Взаємодіє з підсистемою BPF ядра за допомогою бібліотеки `libbpf`. Він завантажує скомпільований об'єктний BPF-файл, ініціалізує BPF-мапи та приєднує структуру `sched_ext_ops` до ядра Linux.

---

### 1. BPF-програма ядра (my_fifo.bpf.c)

Програма виконується у режимі ядра Linux. Вона створює власну глобальну чергу диспетчеризації `MY_DSQ_ID` і перехоплює додавання та вилучення завдань. Усі операції виконуються з нульовою затримкою на переключення контексту користувача, оскільки BPF-код компілюється в сирі інструкції процесора за допомогою JIT-компілятора ядра.

Під час ініціалізації BPF-хук `my_fifo_init` викликає хелпер `scx_bpf_create_dsq()`, реєструючи власну чергу з ідентифікатором `MY_DSQ_ID`. Коли потік прокидається, хук `my_fifo_enqueue` атомарно збільшує лічильник у BPF-мапі `stats_map` та відправляє потік у чергу `scx_bpf_dispatch`. При звільненні процесора хук `my_fifo_dispatch` споживає перший потік з черги за допомогою `scx_bpf_consume`. Якщо черга порожня, процесор залишається в режимі очікування або переходить до обробки інших переривань. Така схема гарантує мінімальну затримку диспетчеризації для простих робочих навантажень.

BPF-програма повинна містити оголошення ліцензії `SEC("license") = "GPL"`, оскільки функціональність `sched_ext` та хелпери `scx_bpf_*` доступні лише для програм з вільною ліцензією. Оголошення BPF-мапи `stats_map` забезпечує збереження статистики між викликами хуків, що дозволяє користувацькому демону моніторити кількість оброблених перепланувань.

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

// Ліцензія ядра (обов'язкова для BPF struct_ops)
char _license[] SEC("license") = "GPL";

// Ідентифікатор нашої глобальної черги DSQ
#define MY_DSQ_ID 1001

// Лічильник завантажених завдань у мапі
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, u32);
    __type(value, u64);
} stats_map SEC(".maps");

// 1. Хук ініціалізації: створюємо власну чергу DSQ
SEC("struct_ops/my_fifo_init")
s32 BPF_STRUCT_OPS(my_fifo_init)
{
    // Створюємо чергу MY_DSQ_ID на поточному NUMA-вузлі (-1)
    return scx_bpf_create_dsq(MY_DSQ_ID, -1);
}

// 2. Хук enqueue: коли завдання стає готовим, додаємо його в чергу DSQ
SEC("struct_ops/my_fifo_enqueue")
void BPF_STRUCT_OPS(my_fifo_enqueue, struct task_struct *p, u64 enq_flags)
{
    u32 key = 0;
    u64 *cnt = bpf_map_lookup_elem(&stats_map, &key);
    if (cnt) {
        __sync_fetch_and_add(cnt, 1);
    }

    // Додаємо завдання у глобальну чергу MY_DSQ_ID з дефолтним квантом часу (20 мс)
    scx_bpf_dispatch(p, MY_DSQ_ID, SCX_SLICE_DFL, enq_flags);
}

// 3. Хук dispatch: коли CPU звільняється, споживаємо завдання з черги DSQ
SEC("struct_ops/my_fifo_dispatch")
void BPF_STRUCT_OPS(my_fifo_dispatch, s32 cpu, struct task_struct *prev)
{
    // Вилучаємо перше завдання з черги MY_DSQ_ID для виконання на цьому CPU
    scx_bpf_consume(MY_DSQ_ID);
}

// 4. Реєстрація структури sched_ext_ops
SEC(".struct_ops.link")
struct sched_ext_ops fifo_ops = {
    .init     = (void *)my_fifo_init,
    .enqueue  = (void *)my_fifo_enqueue,
    .dispatch = (void *)my_fifo_dispatch,
    .name     = "simple_fifo_demo",
};
```

---

### 2. Завантажувач у просторі користувача (User-Space Loader)

Завантажувач відповідає за життєвий цикл BPF-планувальника. При запуску він завантажує скомпільний BPF-код у ядро, після чого вмикає розширення `sched_ext`. Програма залишається у фоновому режимі, очікуючи на сигнал завершення (наприклад, `SIGINT` або `SIGTERM`). При отриманні сигналу завантажувач акуратно вивантажує BPF-структуру з ядра, що повертає систему під управління стандартного планувальника EEVDF.

Нижче наведено варіанти реалізації завантажувача мовами C та C++. Варіант мовою C++ демонструє ідіоматичний RAII-підхід (Resource Acquisition Is Initialization) із використанням `std::unique_ptr` та кастомних деструкторів для гарантованої очистки ресурсів ядра при виникненні винятків.

У варіанті C++ деструктор `ScxScheduler::~ScxScheduler()` виконує послідовне звільнення ресурсів BPF-посилань. Це гарантує, що навіть при виникненні необробленого винятку `std::runtime_error` у користувацькому коді, BPF-планувальник буде коректно вигружений із пам'яті ядра, а процеси безпечно повернуться під контроль EEVDF без ризику зависання системи.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include "my_fifo.skel.h"

static volatile sig_atomic_t stop = 0;

static void sig_handler(int sig)
{
    (void)sig;
    stop = 1;
}

int main(int argc, char **argv)
{
    struct my_fifo_bpf *skel = NULL;
    struct bpf_link *link = NULL;
    int err;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    // 1. Відкриваємо та завантажуємо BPF скелет у ядро
    skel = my_fifo_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка: не вдалося відкрити або завантажити BPF скелет\n");
        return 1;
    }

    // 2. Приєднуємо struct_ops до ядра (вмикає планувальник sched_ext)
    link = bpf_map__attach_struct_ops(skel->maps.fifo_ops);
    if (!link) {
        fprintf(stderr, "Помилка: не вдалося приєднати struct_ops до sched_ext\n");
        my_fifo_bpf__destroy(skel);
        return 1;
    }

    printf("Планувальник simple_fifo успішно завантажено та активовано в ядрі.\n");
    printf("Натисніть Ctrl+C для вивантаження...\n");

    while (!stop) {
        sleep(1);
    }

    printf("\nВигрузка планувальника sched_ext...\n");
    bpf_link__destroy(link);
    my_fifo_bpf__destroy(skel);
    printf("Система повернулася до стандартного планувальника EEVDF.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <csignal>
#include <atomic>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <bpf/libbpf.h>
#include "my_fifo.skel.h"

namespace {
    std::atomic<bool> g_stop{false};

    void signal_handler(int signal) noexcept {
        (void)signal;
        g_stop.store(true, std::memory_order_relaxed);
    }
}

// RAII обгортка для керування BPF-скелетом
class ScxScheduler {
public:
    ScxScheduler() {
        m_skel.reset(my_fifo_bpf__open_and_load());
        if (!m_skel) {
            throw std::runtime_error("Не вдалося відкрити або завантажити BPF-скелет");
        }

        m_link.reset(bpf_map__attach_struct_ops(m_skel->maps.fifo_ops));
        if (!m_link) {
            throw std::runtime_error("Не вдалося приєднати struct_ops до sched_ext");
        }
    }

    ~ScxScheduler() noexcept {
        // Деструктор автоматично вивантажує BPF link та skel у зворотному порядку
        std::cout << "\nВивантаження BPF-планувальника sched_ext через RAII...\n";
    }

    ScxScheduler(const ScxScheduler&) = delete;
    ScxScheduler& operator=(const ScxScheduler&) = delete;

private:
    struct BpfDeleter {
        void operator()(my_fifo_bpf* skel) const noexcept {
            if (skel) my_fifo_bpf__destroy(skel);
        }
    };

    struct LinkDeleter {
        void operator()(bpf_link* link) const noexcept {
            if (link) bpf_link__destroy(link);
        }
    };

    std::unique_ptr<my_fifo_bpf, BpfDeleter> m_skel;
    std::unique_ptr<bpf_link, LinkDeleter> m_link;
};

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        ScxScheduler scheduler;
        std::cout << "Планувальник simple_fifo успішно завантажено в ядрі (C++ RAII).\n";
        std::cout << "Очікування сигналу вивантаження (Ctrl+C)...\n";

        while (!g_stop.load(std::memory_order_relaxed)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }

    std::cout << "Планувальник вивантажено. Автоматичне повернення до EEVDF.\n";
    return 0;
}
```
:::

---

### 3. Збірка, запуск та діагностика

Процес збірки складається з трьох послідовних кроків: генерації заголовочного файла типізації ядра `vmlinux.h`, компіляції BPF-коду за допомогою Clang та створення автогенерованого C-скелета через `bpftool`.

Під час компіляції Clang використовує опцію `-target bpf`, створюючи об'єктний файл із BPF-інструкціями. Утиліта `bpftool` генерує C-заголовок `my_fifo.skel.h`, який містить закодований байткод і спрощує завантаження BPF-мап із коду користувача. Автогенерований скелет містить методи відкриття `my_fifo_bpf__open()`, компіляції `my_fifo_bpf__load()` та знищення `my_fifo_bpf__destroy()`. При ініціалізації бібліотека `libbpf` перевіряє наявність сумісних точок `struct_ops` у поточному ядрі.

Генерація `vmlinux.h` є вирішальним кроком, оскільки вона експортує у BPF-програму точні описи ядерних структур поточного ядра. Це гарантує сумісність за алгоритмом CO-RE (Compile Once – Run Everywhere), дозволяючи BPF-байткоду виконуватися на різних версіях ядра без перекомпіляції під кожну збірку.

```bash
# 1. Генерація vmlinux.h та BPF-скелета
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
clang -g -O2 -target bpf -c my_fifo.bpf.c -o my_fifo.bpf.o
bpftool gen skeleton my_fifo.bpf.o > my_fifo.skel.h

# 2. Збірка завантажувача C та C++
gcc -O2 my_fifo.c -lbpf -o loader_c
g++ -O2 -std=c++20 my_fifo.cpp -lbpf -o loader_cpp

# 3. Запуск під привілеями root
sudo ./loader_c
```

Після запуску перевірити статус підсистеми `sched_ext` у ядрі можна через псевдофайлову систему `/sys/kernel/sched_ext/`. Якщо завантаження пройшло успішно, файл `state` міститиме рядок `enabled`, а у `root/ops_name` відобразиться назва нашого планировщика `simple_fifo_demo`:

```bash
cat /sys/kernel/sched_ext/state
# Вивід: enabled (simple_fifo_demo)
```

У разі виникнення помилок або спрацювання сторожового таймера `scx_watchdog`, детальну інформацію про причину аварійного переходу системи на EEVDF можна отримати з журналу ядра `dmesg`:

```bash
sudo dmesg | grep -i sched_ext
```

### 4. Практичний аналіз та трасування

Під час роботи `simple_fifo` усі звичайні процеси системи розміщуються в єдину чергу `MY_DSQ_ID`. Для перевірки лічильника оброблених завдань у мапі `stats_map` можна використовувати інструмент `bpftool`:

```bash
sudo bpftool map dump name stats_map
```

Вивід покаже точну кількість викликів хука `ops.enqueue`, підтверджуючи, що BPF-програма активна та успішно обробляє потік подій системи.

### 5. Обробка крайових випадків у FIFO розкладі

Слід враховувати, що чистий глобальний FIFO-планувальник є навчальним прикладом. На реальних багатоядерних серверах тривале виконання одного компуційного потоку в глобальній черзі без витіснення може спричинити голодування (starvation) інших процесів. У реальних розширеннях розробники поєднують FIFO з таймерними витісненнями (`slice`) та створюють окремі DSQ для кожного CPU.

Для розгортання у виробничому середовищі розробники додають обробку міжпроцесорних переривань через `scx_bpf_kick_cpu()`, щоб запобігти ситуації, коли вільний CPU залишається в стані idle при наявності чекаючих завдань у глобальній черзі DSQ. Також додаються перевірки на приналежність завдання до конкретних cgroups v2 для пріоритетного надання ресурсів критичним сервісам.

Крім того, розробники реалізують динамічний розподлі квоти часу `slice`. Якщо потік вичерпує свій квант (наприклад, 20 мс), хук `ops.stopping` перевизначає залишок і знову викликає `scx_bpf_dispatch`, розміщуючи завдання в кінець черги. Це запобігає монополізації процесора одним обчислювальним потоком та підтримує чутливість інтерактивних завдань. Завдяки цьому приклад легко розширюється до повноцінного виробничого алгоритму.
