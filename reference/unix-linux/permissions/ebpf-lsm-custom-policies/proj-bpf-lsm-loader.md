# ⚙️ Практична політика BPF-LSM: блокування виконання та телеметрія через Ring Buffer

Цей проєкт демонструє повний виробничий цикл створення, компіляції, верифікації та розгортання кастомної політики безпеки на основі BPF-LSM у ядрі Linux. Реалізоване рішення поєднує два критичні завдання сучасної системної безпеки: активне перехоплення та блокування небажаних дій (Enforcement) та генерацію високонадійного потоку аудиторської телеметрії через кільцевий буфер ядра (BPF Ring Buffer) безпосередньо у простір користувача.

## 1. Архітектурне обґрунтування та схема взаємодії

Взаємодія між ядром Linux та користувацьким простором у цьому рішенні будується на дворівневій архітектурі:
1. У просторі користувача C/C++ демон завантажує eBPF-байтокод через системний виклик `bpf()` і прикріплює його до LSM-хука `security_bprm_check` за допомогою об'єкта `bpf_link`.
2. Під час спроби виконання системного виклику `execve()` ядро передає контроль ядерній BPF-програмі, яка оцінює привілеї та приймає рішення: повернути `0` для дозволу або `-EPERM` для негайного блокування.
3. Одночасно BPF-програма резервує слот у кільцевому буфері `BPF_MAP_TYPE_RINGBUF` та копіює туди метадані процесу (PID, UID, comm, filename).
4. Демон простору користувача асинхронно опитує кільцевий буфер через `ring_buffer__poll()`, отримуючи потік подій аудиту без затримок виконання системних викликів.

```text
  [Ядро Linux (Kernel Space)]                      [Простір користувача (User Space)]
 ┌───────────────────────────┐                    ┌───────────────────────────────────┐
 │ System Call: execve()     │                    │ C / C++ Daemon (Loader & Consumer)│
 └─────────────┬─────────────┘                    └─────────────────┬─────────────────┘
               │                                                    │
               ▼                                                    │ 1. bpf(BPF_PROG_LOAD)
 ┌───────────────────────────┐                                      │    bpf_link_create()
 │ LSM Hook:                 │                                      ▼
 │ security_bprm_check       │ ◀─────────────────────────────── [BPF Link]
 └─────────────┬─────────────┘
               │
               ▼
 ┌───────────────────────────┐ 2. Reserve / Submit  ┌───────────────────────────────────┐
 │ BPF-LSM Program:          │ ───────────────────▶ │ BPF Map: BPF_MAP_TYPE_RINGBUF     │
 │ enforce_exec_policy()     │                      └─────────────────┬─────────────────┘
               │                                                      │
               ├──▶ 0 (Allow: continue execve)                        │ 3. ring_buffer__poll()
               └──▶ -EPERM (Deny: block execve)                       ▼
                                                  ┌───────────────────────────────────┐
                                                  │ Async Audit Logger / SIEM Stream  │
                                                  └───────────────────────────────────┘
```

Така схема дозволяє уникнути інвазивного трасування через `ptrace()` (яке спричиняє значний overhead через постійні перемикання контексту процесора та зупинки процесів) або обмежень статичних правил SELinux / AppArmor, забезпечуючи перехоплення зі швидкістю нативної машинної інструкції ядра.

### 1.1. Порівняльний аналіз механізмів доставки подій: Ring Buffer проти Perf Buffer

У старіших версіях eBPF для передачі подій у простір користувача використовувався механізм `BPF_MAP_TYPE_PERF_EVENT_ARRAY`. Проте він мав суттєвий недолік: пам'ять виділялася окремо під кожне ядро CPU (так звані per-CPU buffers). Якщо одне конкретне ядро генерувало сплеск подій (наприклад, під час масового виклику `execve` у паралельних потоках Build-сервера), його особистий буфер швидко переповнювався і події втрачалися, навіть якщо буфери сусідніх ядер залишалися повністю порожніми.

Представлений у Linux 5.8 **BPF Ring Buffer** (`BPF_MAP_TYPE_RINGBUF`) вирішує цю проблему за допомогою наступних механізмів:

1. **Єдиний спільний простір пам'яті (Single Shared Memory):** Кільцевий буфер є єдиною неперервною чергою для всіх ядер CPU, що повністю усуває дисбаланс використання пам'яті.
2. **Безблокувальний запис (Lockless MPSC Queue):** Підтримує високопродуктивний механізм Multi-Producer Single-Consumer із нульовим виділенням динамічної пам'яті під час резервування слотів через хелпер `bpf_ringbuf_reserve()`.
3. **Нульове копіювання (Zero-Copy):** BPF-програма копіює зібрані метадані безпосередньо у зарезервований слот пам'яті ядра, який відразу відображається через системний виклик `mmap()` у користувацький простір завантажувача.

---

## 2. Код BPF-програми ядра (`lsm_policy.bpf.c`)

Ядерний модуль C описує структуру події аудиту, BPF Ring Buffer Map та функцію перехоплення LSM-хука `bprm_check_security`.

Для реалізації цієї логіки використовуються такі ключові ядерні механізми та BPF-хелпери:
1. **`bpf_get_current_uid_gid()` та `bpf_get_current_pid_tgid()`:** Ці BPF-хелпери повертають 64-бітні упаковані значення. У системі Linux PID потоку знаходиться у молодших 32 бітах, а TGID (Thread Group ID, який у системних викликах відповідає PID процесу) — у старших 32 бітах. Для витягування PID використовується зсув `pid_tgid >> 32`.
2. **Макрос `BPF_CORE_READ()`:** Використовується для розіменування вказівників на структури ядра через технологію CO-RE. Наприклад, вираз `BPF_CORE_READ(task, real_parent, tgid)` еквівалентний C-коду `task->real_parent->tgid`, проте він автоматично перетворюється на набір релокацій `libbpf`, що захищає програму від зміни offset-ів при оновленні ядра.
3. **`bpf_probe_read_kernel_str()`:** Ця функція є єдиним безпечним способом копіювання рядків із пам'яті ядра у BPF-буфер. Вона запобігає виходу за межі виділеної пам'яті та гарантує наявність нульового термінатора `\0` наприкінці рядка. Порівняння скопійованого шляху з фіксованим рядком у прикладі навмисно просте: запуск через відносний шлях чи символьне посилання його обійде, тож бойова політика канонізує шлях хелпером `bpf_d_path()`.

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

// Структура події аудиту, що передається у User Space
struct audit_event {
    u32 pid;
    u32 ppid;
    u32 uid;
    u32 gid;
    char comm[16];
    char filename[64];
    bool blocked;
};

// Оголошення глобального BPF Ring Buffer на 256 КБ
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256 KB
} audit_ringbuf SEC(".maps");

SEC("lsm/bprm_check_security")
int BPF_PROG(enforce_exec_policy, struct linux_binprm *bprm)
{
    // 1. Отримуємо ідентифікатори поточного процесу та користувача
    u64 uid_gid = bpf_get_current_uid_gid();
    u32 uid = (u32)uid_gid;
    u32 gid = (u32)(uid_gid >> 32);

    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = (u32)(pid_tgid >> 32);

    // 2. Читаємо ім'я файлу виконуваного об'єкта через CO-RE
    const char *fname = BPF_CORE_READ(bprm, filename);
    if (!fname) {
        return 0;
    }

    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));

    // 3. Логіка політики: блокуємо запуск chmod та netcat не-root користувачами (UID != 0)
    bool is_restricted = false;
    
    // Рішення спирається на bprm->filename, а не на comm: у точці виклику хука
    // comm ще містить назву процесу, який викликав execve (наприклад, bash),
    // а на назву нового бінарника ядро змінить її вже після дозволу на запуск.
    char path[64] = {};
    bpf_probe_read_kernel_str(path, sizeof(path), fname);

    if (__builtin_memcmp(path, "/usr/bin/chmod", sizeof("/usr/bin/chmod")) == 0 ||
        __builtin_memcmp(path, "/usr/bin/nc", sizeof("/usr/bin/nc")) == 0 ||
        __builtin_memcmp(path, "/usr/bin/ncat", sizeof("/usr/bin/ncat")) == 0) {
        is_restricted = true;
    }

    bool should_block = (uid != 0) && is_restricted;

    // 4. Формуємо та відправляємо подію у Ring Buffer
    struct audit_event *evt;
    evt = bpf_ringbuf_reserve(&audit_ringbuf, sizeof(*evt), 0);
    if (evt) {
        evt->pid = pid;
        evt->uid = uid;
        evt->gid = gid;
        evt->blocked = should_block;

        // Копіюємо батьківський PID через структуру task_struct
        struct task_struct *task = (struct task_struct *)bpf_get_current_task();
        evt->ppid = BPF_CORE_READ(task, real_parent, tgid);

        // Безпечно зчитуємо рядки з пам'яті ядра
        bpf_probe_read_kernel_str(evt->comm, sizeof(evt->comm), comm);
        bpf_probe_read_kernel_str(evt->filename, sizeof(evt->filename), fname);

        // Публікуємо подію для споживачів у User Space
        bpf_ringbuf_submit(evt, 0);
    }

    // 5. Приймаємо рішення про допуск операції
    if (should_block) {
        bpf_printk("BPF-LSM: DENIED exec '%s' (PID %d, UID %d)\n", comm, pid, uid);
        return -1; // -EPERM (Operation not permitted)
    }

    return 0; // Allow
}
```

---

## 3. Користувацькі завантажувачі: C та C++ імплементації

Для завантаження BPF-байтокоду в ядро та споживання подій з Ring Buffer використовується автозгенерований заголовок скелета (`lsm_policy.skel.h`). Скелет генерується утилітою `bpftool gen skeleton`.

Нижче наведено дві повноцінні ідіоматичні реалізації користувацького демона у вигляді вкладки `:::tabs`.

:::tabs
```c
/* loader.c — C імплементація з класичним низькорівневим API libbpf */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <stdbool.h>
#include <bpf/libbpf.h>
#include "lsm_policy.skel.h"

static volatile bool keep_running = true;

static void sig_handler(int sig) {
    keep_running = false;
}

// Callback-функція, яка викликається при появі нової події у Ring Buffer
static int handle_event(void *ctx, void *data, size_t data_sz) {
    const struct audit_event *evt = data;
    
    printf("[AUDIT LOG] PID: %-6d | PPID: %-6d | UID: %-4d | Comm: %-10s | Action: %s | File: %s\n",
           evt->pid, evt->ppid, evt->uid, evt->comm,
           evt->blocked ? "\033[1;31mDENIED\033[0m" : "\033[1;32mALLOWED\033[0m",
           evt->filename);
    return 0;
}

int main(int argc, char **argv) {
    struct lsm_policy_bpf *skel = NULL;
    struct ring_buffer *rb = NULL;
    int err;

    // Встановлюємо обробники сигналів для коректного завершення
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    // 1. Відкриваємо та завантажуємо BPF-програму в ядро
    skel = lsm_policy_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "ERROR: Failed to open and load BPF skeleton\n");
        return 1;
    }

    // 2. Прикріплюємо програму до LSM-хука
    err = lsm_policy_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "ERROR: Failed to attach BPF LSM program: %d\n", err);
        goto cleanup;
    }

    // 3. Ініціалізуємо споживача Ring Buffer
    rb = ring_buffer__new(bpf_map__fd(skel->maps.audit_ringbuf), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "ERROR: Failed to create ring buffer consumer\n");
        goto cleanup;
    }

    printf("====================================================================\n");
    printf(" BPF-LSM Enforcement & Audit Daemon Started Successfully\n");
    printf(" Monitoring 'bprm_check_security' hook. Press Ctrl+C to stop.\n");
    printf("====================================================================\n");

    // Головний цикл опитування Ring Buffer
    while (keep_running) {
        err = ring_buffer__poll(rb, 100 /* ms timeout */);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "ERROR: Ring buffer polling failed: %d\n", err);
            break;
        }
    }

cleanup:
    // Порядок очищення ресурсів у C
    if (rb) ring_buffer__free(rb);
    if (skel) lsm_policy_bpf__destroy(skel);
    printf("\n[INFO] BPF-LSM Policy detached. Daemon exiting safely.\n");
    return 0;
}
```
```cpp
// loader.cpp — Сучасна C++20 RAII імплементація демона моніторингу
#include <iostream>
#include <memory>
#include <stdexcept>
#include <csignal>
#include <atomic>
#include <thread>
#include <chrono>
#include <bpf/libbpf.h>
#include "lsm_policy.skel.h"

namespace {
    std::atomic<bool> g_stop_requested{false};

    void signal_handler(int) {
        g_stop_requested.store(true);
    }
}

// Клас-менеджер політики BPF-LSM із використанням принципу RAII (Resource Acquisition Is Initialization)
class BpfPolicyManager {
public:
    BpfPolicyManager() {
        // 1. Відкриваємо та завантажуємо BPF об'єкт
        skel_ = lsm_policy_bpf__open_and_load();
        if (!skel_) {
            throw std::runtime_error("Failed to open and load eBPF skeleton");
        }

        // 2. Прикріплюємо BPF Link до LSM хука
        int err = lsm_policy_bpf__attach(skel_);
        if (err) {
            lsm_policy_bpf__destroy(skel_);
            throw std::runtime_error("Failed to attach eBPF LSM hooks to kernel");
        }

        // 3. Створюємо споживача Ring Buffer
        rb_ = ring_buffer__new(bpf_map__fd(skel_->maps.audit_ringbuf),
                               &BpfPolicyManager::on_event, this, nullptr);
        if (!rb_) {
            lsm_policy_bpf__destroy(skel_);
            throw std::runtime_error("Failed to initialize eBPF Ring Buffer consumer");
        }
    }

    // Деструктор гарантує 100% від'єднання політики з ядра при виході з області видимості
    ~BpfPolicyManager() {
        if (rb_) {
            ring_buffer__free(rb_);
        }
        if (skel_) {
            lsm_policy_bpf__destroy(skel_);
        }
        std::cout << "[RAII Destructor] BPF-LSM Policy detached and resources freed." << std::endl;
    }

    // Забороняємо копіювання об'єкта (Move-only)
    BpfPolicyManager(const BpfPolicyManager&) = delete;
    BpfPolicyManager& operator=(const BpfPolicyManager&) = delete;

    // Метод опитування кільцевого буфера
    void poll(int timeout_ms = 100) {
        if (rb_) {
            int err = ring_buffer__poll(rb_, timeout_ms);
            if (err < 0 && err != -EINTR) {
                throw std::runtime_error("Error during ring buffer polling: " + std::to_string(err));
            }
        }
    }

private:
    // Статичний callback метод обробки подій
    static int on_event(void *ctx, void *data, size_t data_sz) {
        auto *evt = static_cast<const audit_event*>(data);
        
        std::cout << "[C++ AUDIT] PID: " << evt->pid 
                  << " | PPID: " << evt->ppid 
                  << " | UID: " << evt->uid 
                  << " | Comm: " << evt->comm 
                  << " | Status: " << (evt->blocked ? "DENIED" : "ALLOWED")
                  << " | File: " << evt->filename 
                  << std::endl;
        return 0;
    }

    struct lsm_policy_bpf *skel_{nullptr};
    struct ring_buffer *rb_{nullptr};
};

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        BpfPolicyManager manager;
        std::cout << "BPF-LSM C++ Protection Manager running. Press Ctrl+C to exit." << std::endl;

        while (!g_stop_requested.load()) {
            manager.poll(100);
        }
    } catch (const std::exception &ex) {
        std::cerr << "Fatal Exception: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
```
:::

### 3.1. Порівняння підходів у мовах C та C++

* **Реалізація на C:** Використовує ручні виклики функції вивантаження `lsm_policy_bpf__destroy()` та очищення буфера `ring_buffer__free()` через паттерн `goto cleanup`. Цей підхід є стандартним для розробки ядра та системних інструментів C, але вимагає високої уваги розробника для уникнення витоків пам'яті у складних відгалуженнях помилок.
* **Реалізація на C++20:** Використовує шаблон RAII у класі `BpfPolicyManager`. Скелет та Ring Buffer відкриваються в конструкторі (який викидає `std::runtime_error` у разі збою), а вивантаження політики з ядра гарантується деструктором `~BpfPolicyManager()`. Навіть якщо під час обробки подій виникне виняток чи буде отримано сигнал зупинки, деструктор неодмінно викличе `lsm_policy_bpf__destroy()`, що миттєво зніме BPF-LSM лінк із ядра.

---

## 4. Інструкція з компіляції, збирання та верифікації

Для успішної компіляції розробник повинен мати встановлений інструментарій `clang`, `llvm`, `libbpf-dev`, `libelf-dev` та `bpftool`.

### Крок 1: Генерація vmlinux.h та компіляція BPF-об'єкта

Процес збирання BPF-компонента складається з трьох послідовних етапів:
1. **Генерація заголовка типів ядра (`vmlinux.h`):** За допомогою `bpftool` здійснюється дамп усіх BTF-метаданих поточного ядра в єдиний C-заголовок, що позбавляє залежності від заголовкових файлів ядра.
2. **Компіляція в eBPF-байткод:** Clang компілює `lsm_policy.bpf.c` з цільовою архітектурою `-target bpf` та генерацією BTF-інформації (`-g`) для забезпечення CO-RE релокацій.
3. **Генерація C-скелета (`lsm_policy.skel.h`):** Утиліта `bpftool gen skeleton` створює високорівневу C-обгортку над об'єктним файлом, яка спрощує завантаження та управління картами в User Space.

```bash
# 1. Дамп метаданих BTF поточного ядра в єдиний заголовок
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# 2. Компіляція BPF програма за допомогою Clang з генерацією BTF (-g)
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c lsm_policy.bpf.c -o lsm_policy.bpf.o

# 3. Автоматична генерація C-скелета для підключення у завантажувач
bpftool gen skeleton lsm_policy.bpf.o > lsm_policy.skel.h
```

### Крок 2: Збирання користувацьких завантажувачів

Для лінкування користувацьких демонів (C або C++) необхідно підключити три системні бібліотеки:
* `-lbpf` — основна бібліотека для взаємодії з eBPF підсистемою ядра, створення ring buffer та прив'язки BPF-лінків;
* `-lelf` — бібліотека для парсингу секцій ELF та обробки метаданих BTF в об'єктних файлах;
* `-lz` — бібліотека стиснення, необхідна `libbpf` для розпакування BTF-даних.

```bash
# Збирання C завантажувача
gcc -g -Wall loader.c -o loader_c -lbpf -lelf -lz

# Збирання C++ завантажувача
g++ -std=c++20 -g -Wall loader.cpp -o loader_cpp -lbpf -lelf -lz
```

### Крок 3: Тестування роботи політики в реальній системі

1. Запустіть C++ завантажувач у першому терміналі з правами суперкористувача (`root`):
```bash
sudo ./loader_cpp
```

2. У другому терміналі під звичайним користувачем (не root) спробуйте виконати заборонені утиліти `chmod` або `nc`:
```bash
$ chmod 777 /tmp/testfile
bash: /usr/bin/chmod: Operation not permitted
```

3. У першому терміналі демон миттєво друкує структурований лог перехопленої події:
```text
[C++ AUDIT] PID: 14205 | PPID: 12100 | UID: 1000 | Comm: bash | Status: DENIED | File: /usr/bin/chmod
```
Поле `Comm` показує оболонку, яка викликала `execve`, а не заблокований бінарник: назву процесу ядро змінює вже після проходження хука, тому сам об'єкт рішення видно в полі `File`. При виконанні тієї ж команди через `sudo chmod` програма бачить `UID 0` та дозволяє виконання, друкуючи `Status: ALLOWED`.

---

## 5. Інтеграція у Systemd та виробнича експлуатація

При розгортанні BPF-LSM завантажувача у вигляді системної служби systemd необхідно враховувати дві ключові вимоги безпеки та надійності:
1. **Обмеження привілеїв (Capability Trimming):** Демон не повинен запускатися з необмеженими правами root. Через директиву `CapabilityBoundingSet` йому надаються лише мінімально необхідні capabilities: `CAP_BPF` (завантаження BPF-програм і робота з мапами), `CAP_MAC_ADMIN` (встановлення LSM-політик) та `CAP_PERFMON` (читання даних ядра хелперами трасування). Обидві перші виділено з `CAP_SYS_ADMIN` у ядрі 5.8; на давніших ядрах ту саму роботу дозволяє лише `CAP_SYS_ADMIN`, що фактично рівносильне повним правам root.
2. **Гарантія автоочищення через `bpf_link`:** Завдяки використанню новітнього механізму `bpf_link` (замість застарілих прив'язок `bpf_program__attach_lsm`), якщо користувацький демон аварійно зупиняється (наприклад, через SIGKILL або Segmentation Fault), ядро Linux закриває анонімний файловий дескриптор `bpf_link` і автоматично вивантажує LSM-політику з ядра. Це унеможливлює ризик залишення "завислої" політики, яка б назавжди заблокувала системні виклики `execve` у всій системі.

Нижче наведено конфігураційний файл юніта systemd (`/etc/systemd/system/bpf-lsm-guard.service`), який реалізує ці принципи:

```ini
[Unit]
Description=BPF-LSM Custom Security Policy Guard
After=network.target local-fs.target
Documentation=https://kernel.org/doc/html/latest/bpf/

[Service]
Type=simple
ExecStart=/usr/local/bin/loader_cpp
Restart=always
RestartSec=3s
ProtectSystem=full
CapabilityBoundingSet=CAP_BPF CAP_MAC_ADMIN CAP_PERFMON

[Install]
WantedBy=multi-user.target
```

---

## 6. Тестування продуктивності та навантажувальні тести

Методологія тестування продуктивності BPF-LSM політики передбачає генерацію інтенсивного потоку системних викликів `execve` у декількох паралельних потоках для оцінки накладних витрат процесора та затримки обробки хука. Під час навантажувального тестування демон Ring Buffer тримає споживання CPU на рівні часток одного ядра, а приріст затримки `execve` лишається малим на тлі самої вартості запуску процесу; конкретні числа залежать від версії ядра, обсягу політики та заліза, тож їх треба міряти на власному стенді.

Для перевірки стійкості політики під високим навантаженням використовується інструмент `stress-ng`:

```bash
# Навантажувальний тест розгалуження та запуску процесів
stress-ng --exec 8 --timeout 30s --metrics-brief
```

---

## 7. Чеклист діагностики та командні інструменти

Для оперативного аналізу стану завантажених BPF-LSM політик та перевірки наявності помилок верифікації використовується набір стандартних інструментів:

* **Перевірка наявності BPF у списку активних LSM:** `cat /sys/kernel/security/lsm`.
* **Перегляд ідентифікаторів завантажених BPF-програм:** `sudo bpftool prog show type lsm`.
* **Дамп вмісту BPF Map:** `sudo bpftool map dump id <map_id>`.
* **Моніторинг повідомлень bpf_printk:** `sudo cat /sys/kernel/debug/tracing/trace_pipe`.
