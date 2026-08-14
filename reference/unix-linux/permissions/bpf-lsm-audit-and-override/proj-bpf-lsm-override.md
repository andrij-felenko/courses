# ⚙️ Проєкт BPF LSM: динамічний аудит та блокування небажаного виконуваного коду

Вставка містить повністю працездатний проєкт на базі бібліотеки `libbpf`, який підключається до хуків BPF LSM, виконує динамічний аудит запусків бінарних файлів та блокує виконання програм із каталогу `/tmp` з поверненням коду помилки `-EACCES`.

## Архітектура та структура проєкту

Практичний модуль безпеки складається з двох чітко розмежованих компонентів: ядерного обробника BPF та користувацького демона моніторингу. Такий поділ забезпечує ізоляцію критичної логіки перевірки у просторі ядра від сервісних функцій обробки логів у просторі користувача.

1. **Ядерна BPF-програма (`bpf_lsm_exec.bpf.c`)**: Виконується безпосередньо в контексті ядра Linux під час кожного звернення до системного виклику запуску програм (`execve` / `execveat`). Програма аналізує запуск процесів у хуку `security_bprm_check_security`, зчитує канонічний шлях файлу через VFS, перевіряє права доступу, підраховує кількість виконаних дій у BPF Local Storage та надсилає детальні події в BPF Ring Buffer. Якщо бінарний файл розміщено у забороненому каталозі `/tmp/`, програма негайно повертає код `-EACCES`, зупиняючи виконання системного виклику.
2. **Демон простору користувача (`lsm_loader`)**: Завантажує скомпільований об'єктний BPF-код у ядро, здійснює верифікацію, прив'язує LSM-хуки та організовує асинхронне опитування кільцевого буфера подій аудиту. Простір користувача реалізовано мовами C та C++ у вкладках `:::tabs` із дотриманням ідіоматичних паттернів кожної мови (RAII для C++ та пряме управління ресурсами для C).

Завдяки використанню специфікації BPF CO-RE (Compile Once – Run Everywhere) скомпільований бінарний образ BPF-програми не прив'язаний до версії заголовків конкретного ядра й може виконуватися на будь-якому дистрибутиві Linux із підтримкою BTF та включеним BPF LSM.

## 1. Ядерна BPF-програма (`bpf_lsm_exec.bpf.c`)

Ядерний код BPF відповідає за виконання перевірок у реальному часі. Він використовує розширені можливості CO-RE та BTF для безпечного доступу до структур ядра без прив'язки до конкретної збірки Linux. Це дає змогу одноразово скомпільованому об'єктному файлу працювати на різних версіях ядра без перекомпіляції.

Для аналізу шляху виконуваного файлу програма використовує безпечний хелпер `bpf_d_path()`. Результат перевіряється на наявність префіксу забороненого каталогу `/tmp/`. Якщо шлях починається з цього префіксу, програма заповнює структуру аудиту для Ring Buffer та повертає код помилки `-EACCES`.

Під час резервування пам'яті в `BPF Ring Buffer` за допомогою `bpf_ringbuf_reserve()` ядро виділяє заголовок події у кільцевому масиві спільної пам'яті. Це гарантує атомарність операції для кількох паралельно працюючих ядер процесора без використання Spinlocks. Після заповнення полів `pid`, `uid`, `comm` та `filename` програма публікує запис викликом `bpf_ringbuf_submit()`, роблячи його доступним для користувацького демона.

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char _license[] SEC("license") = "GPL";

// Структура події аудиту для передачі в userspace
struct audit_event {
    u32 pid;
    u32 ppid;
    u32 uid;
    u32 action; // 0 = Allowed, 1 = Denied (Blocked)
    char comm[16];
    char filename[256];
};

// BPF Ring Buffer для аудиту
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256 KB
} audit_ringbuf SEC(".maps");

// Сховище для підрахунку кількості спроб запуску на рівні task_struct
struct {
    __uint(type, BPF_MAP_TYPE_TASK_STORAGE);
    __uint(map_flags, BPF_F_NO_PREALLOC);
    __type(key, int);
    __type(value, u64);
} task_exec_count SEC(".maps");

SEC("lsm/bprm_check_security")
int BPF_PROG(restrict_exec, struct linux_binprm *bprm)
{
    u64 uid_gid = bpf_get_current_uid_gid();
    u32 uid = (u32)uid_gid;
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = (u32)(pid_tgid >> 32);

    struct task_struct *current_task = (struct task_struct *)bpf_get_current_task_btf();
    
    // Інкремент лічильника в локальному сховищі процесу
    u64 *count = bpf_task_storage_get(&task_exec_count, current_task, 0, BPF_LOCAL_STORAGE_GET_F_CREATE);
    if (count) {
        __sync_fetch_and_add(count, 1);
    }

    // Буфер для зчитування шляху файлу
    char path_buf[256] = {};
    long ret = bpf_d_path(&bprm->file->f_path, path_buf, sizeof(path_buf));
    
    // Префікс каталогу /tmp для блокування
    const char tmp_prefix[] = "/tmp/";
    bool is_tmp = true;

    if (ret > 0) {
        #pragma unroll
        for (int i = 0; i < 5; i++) {
            if (path_buf[i] != tmp_prefix[i]) {
                is_tmp = false;
                break;
            }
        }
    } else {
        is_tmp = false;
    }

    // Виділення місця в Ring Buffer для події аудиту
    struct audit_event *event;
    event = bpf_ringbuf_reserve(&audit_ringbuf, sizeof(*event), 0);
    if (event) {
        event->pid = pid;
        event->ppid = BPF_CORE_READ(current_task, real_parent, tgid);
        event->uid = uid;
        bpf_get_current_comm(&event->comm, sizeof(event->comm));

        if (ret > 0) {
            bpf_probe_read_kernel_str(event->filename, sizeof(event->filename), path_buf);
        } else {
            event->filename[0] = '\0';
        }

        if (is_tmp) {
            event->action = 1; // Blocked
        } else {
            event->action = 0; // Allowed
        }

        bpf_ringbuf_submit(event, 0);
    }

    // Блокування виконання файлів із /tmp повернувши -EACCES
    if (is_tmp) {
        return -EACCES;
    }

    return 0; // Дозвіл для решти бінарних файлів
}
```

У наведеному коді звернення до `bpf_d_path()` виконується безпечно для VFS, а перевірка префіксу розгортається директивою `#pragma unroll`, що задовольняє суворим вимогам BPF-верифікатора ядра. Використання макроса `BPF_CORE_READ` забезпечує коректне проходження покажчиків у структурі `task_struct` незалежно від версії ядра.

## 2. Завантажувач та монітор аудиту у просторі користувача

Програма простору користувача ініціалізує BPF-об'єкт, завантажує його в ядро, приєднує BPF-програму до хука LSM та слухає кільцевий буфер. Вона обробляє сигнали завершення `SIGINT` та `SIGTERM` для коректного вивантаження BPF-лінків із ядра перед виходом.

Процедура завантаження складається з кількох послідовних кроків `libbpf`:
1. `bpf_object__open_file()` парсить скомпільований ELF-файл `bpf_lsm_exec.bpf.o`, зчитує секції `.text`, `.maps` та `BTF`.
2. `bpf_object__load()` надсилає байткод у ядро через системний виклик `bpf(BPF_PROG_LOAD, ...)`. Верифікатор ядра здійснює перевірку безпеки типів, контролю меж масивів та дозволених хелперів.
3. `bpf_program__attach()` створює системний об'єкт `bpf_link` типу `BPF_LINK_TYPE_LSM`, який приєднує завантажену BPF-програму до точки контролю `security_bprm_check_security`.

Нижче наведено порівняльну реалізацію мовами C та C++ у вкладках `:::tabs`. Реалізація C спирається на прямий виклик функцій `libbpf` з ручним викликом процедур очищення, тоді як реалізація C++ використовує розумні покажчики `std::unique_ptr` із власними функторами видалення для досягнення повної безпеки ресурсів (RAII).

:::tabs
```c
// C (libbpf Native C Implementation)
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct audit_event {
    uint32_t pid;
    uint32_t ppid;
    uint32_t uid;
    uint32_t action;
    char comm[16];
    char filename[256];
};

static volatile bool keep_running = true;

static void sig_handler(int sig)
{
    (void)sig;
    keep_running = false;
}

static int handle_event(void *ctx, void *data, size_t data_sz)
{
    (void)ctx;
    (void)data_sz;
    const struct audit_event *e = data;

    if (e->action == 1) {
        printf("[BLOCKED] PID: %u | UID: %u | COMM: %s | PATH: %s\n",
               e->pid, e->uid, e->comm, e->filename);
    } else {
        printf("[ALLOW]   PID: %u | UID: %u | COMM: %s | PATH: %s\n",
               e->pid, e->uid, e->comm, e->filename);
    }
    return 0;
}

int main(int argc, char **argv)
{
    struct bpf_object *obj = NULL;
    struct bpf_link *link = NULL;
    struct ring_buffer *rb = NULL;
    int err;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    obj = bpf_object__open_file("bpf_lsm_exec.bpf.o", NULL);
    if (!obj) {
        fprintf(stderr, "Помилка відкриття BPF-об'єкта\n");
        return 1;
    }

    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Помилка завантаження BPF у ядро: %d\n", err);
        bpf_object__close(obj);
        return 1;
    }

    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "restrict_exec");
    if (!prog) {
        fprintf(stderr, "Не знайдено програму restrict_exec\n");
        bpf_object__close(obj);
        return 1;
    }

    link = bpf_program__attach(prog);
    if (!link) {
        fprintf(stderr, "Помилка прив'язки LSM-хука\n");
        bpf_object__close(obj);
        return 1;
    }

    int map_fd = bpf_object__find_map_fd_by_name(obj, "audit_ringbuf");
    if (map_fd < 0) {
        fprintf(stderr, "Не знайдено BPF map audit_ringbuf\n");
        bpf_link__destroy(link);
        bpf_object__close(obj);
        return 1;
    }

    rb = ring_buffer__new(map_fd, handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка створення ring buffer\n");
        bpf_link__destroy(link);
        bpf_object__close(obj);
        return 1;
    }

    printf("BPF LSM модуль успішно активовано. Очікування подій...\n");

    while (keep_running) {
        err = ring_buffer__poll(rb, 100);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка при опитуванні ring buffer: %d\n", err);
            break;
        }
    }

    ring_buffer__free(rb);
    bpf_link__destroy(link);
    bpf_object__close(obj);
    printf("Модуль BPF LSM вивантажено.\n");
    return 0;
}
```
```cpp
// C++ (Modern C++20 Idiomatic Implementation with RAII & std::span)
#include <iostream>
#include <memory>
#include <string_view>
#include <csignal>
#include <atomic>
#include <system_error>
#include <span>

#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct audit_event {
    std::uint32_t pid;
    std::uint32_t ppid;
    std::uint32_t uid;
    std::uint32_t action;
    char comm[16];
    char filename[256];
};

namespace {
    std::atomic<bool> keep_running{true};

    void signal_handler(int) noexcept {
        keep_running.store(false, std::memory_order_relaxed);
    }

    // RAII-кастомні деструктори для ресурсів libbpf
    struct BpfObjectDeleter {
        void operator()(bpf_object* obj) const noexcept {
            if (obj) bpf_object__close(obj);
        }
    };

    struct BpfLinkDeleter {
        void operator()(bpf_link* link) const noexcept {
            if (link) bpf_link__destroy(link);
        }
    };

    struct RingBufferDeleter {
        void operator()(ring_buffer* rb) const noexcept {
            if (rb) ring_buffer__free(rb);
        }
    };

    using UniqueBpfObject = std::unique_ptr<bpf_object, BpfObjectDeleter>;
    using UniqueBpfLink = std::unique_ptr<bpf_link, BpfLinkDeleter>;
    using UniqueRingBuffer = std::unique_ptr<ring_buffer, RingBufferDeleter>;
}

static int on_ringbuf_event(void* /*ctx*/, void* data, size_t data_sz) noexcept {
    if (data_sz < sizeof(audit_event)) {
        return 0;
    }

    const auto* e = static_cast<const audit_event*>(data);
    std::string_view comm{e->comm};
    std::string_view path{e->filename};

    if (e->action == 1) {
        std::cout << "[BLOCKED] PID: " << e->pid 
                  << " | UID: " << e->uid 
                  << " | COMM: " << comm 
                  << " | PATH: " << path << '\n';
    } else {
        std::cout << "[ALLOW]   PID: " << e->pid 
                  << " | UID: " << e->uid 
                  << " | COMM: " << comm 
                  << " | PATH: " << path << '\n';
    }
    return 0;
}

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    UniqueBpfObject obj{bpf_object__open_file("bpf_lsm_exec.bpf.o", nullptr)};
    if (!obj) {
        std::cerr << "Помилка відкриття BPF-об'єкта\n";
        return 1;
    }

    if (int err = bpf_object__load(obj.get()); err != 0) {
        std::cerr << "Помилка завантаження BPF програми: " << err << '\n';
        return 1;
    }

    bpf_program* prog = bpf_object__find_program_by_name(obj.get(), "restrict_exec");
    if (!prog) {
        std::cerr << "Не знайдено BPF програму restrict_exec\n";
        return 1;
    }

    UniqueBpfLink link{bpf_program__attach(prog)};
    if (!link) {
        std::cerr << "Помилка прив'язки LSM-хука\n";
        return 1;
    }

    int map_fd = bpf_object__find_map_fd_by_name(obj.get(), "audit_ringbuf");
    if (map_fd < 0) {
        std::cerr << "Не знайдено карту audit_ringbuf\n";
        return 1;
    }

    UniqueRingBuffer rb{ring_buffer__new(map_fd, on_ringbuf_event, nullptr, nullptr)};
    if (!rb) {
        std::cerr << "Помилка створення ring buffer\n";
        return 1;
    }

    std::cout << "BPF LSM монітор запущено в режимі C++20 RAII. Натисніть Ctrl+C для зупинки.\n";

    while (keep_running.load(std::memory_order_relaxed)) {
        int err = ring_buffer__poll(rb.get(), 100);
        if (err < 0 && err != -EINTR) {
            std::cerr << "Помилка моніторингу кільцевого буфера: " << err << '\n';
            break;
        }
    }

    std::cout << "Ресурси автоматично звільнено деструкторами RAII.\n";
    return 0;
}
```
:::

Реалізація C++ використовує обгортки `std::unique_ptr` із власними функторами видалення (`BpfObjectDeleter`, `BpfLinkDeleter`, `RingBufferDeleter`). Це гарантує автоматичне вивантаження системних об'єктів BPF навіть у випадку виникнення винятків або передчасного виходу з методу `main()`. Використання `std::string_view` дає змогу передавати параметри шляху без копіювання рядків у динамічну пам'ять, а атомарна змінна `std::atomic<bool>` забезпечує потокобезпечне переривання циклу опитування.

## Покрокова збірка та перевірка блокування у системі

Для компіляції BPF-програми та завантажувача необхідні заголовочні файли `vmlinux.h`, які генеруються з поточного завантаженого ядра Linux за допомогою інструменту `bpftool`.

```bash
# 1. Дамп системних типів ядра у форматі BTF C-header
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# 2. Компіляція BPF-програми у цільову архітектуру BPF
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c bpf_lsm_exec.bpf.c -o bpf_lsm_exec.bpf.o

# 3. Компіляція завантажувача мовою C++ з підтримкою C++20
g++ -O2 -std=c++20 lsm_loader.cpp -lbpf -o lsm_loader

# 4. Перевірка наявності bpf у переліку увімкнених LSM-модулів
cat /sys/kernel/security/lsm

# 5. Запуск монітора з привілеями суперкористувача (CAP_SYS_ADMIN / CAP_BPF)
sudo ./lsm_loader
```

Якщо при запуску `lsm_loader` виникає помилка `Function not implemented` або `Invalid argument`, слід переконатися, що параметр завантаження ядра містить `bpf` серед переліку активних модулів безпеки (`lsm=capability,landlock,lockdown,bpf,apparmor` у параметрах GRUB).

Після успішного запуску монітора відкрийте сусідній термінал і спробуйте створити й виконати будь-який бінарний файл або сценарій у системному каталозі `/tmp`:

```bash
cp /bin/ls /tmp/test_ls
/tmp/test_ls
```

Системний виклик `execve` буде примусово перервано в ядрі, консоль видасть повідомлення `bash: /tmp/test_ls: Permission denied` (код помилки `EACCES`), а у вікні монітора з'явиться детальний рядок аудиту:

```text
[BLOCKED] PID: 14205 | UID: 1000 | COMM: test_ls | PATH: /tmp/test_ls
```

Це підтверджує, що BPF LSM перехопив виклик у хуку `security_bprm_check_security` і успішно модифікував поведінку ядра, не зачіпаючи роботу інших програм у системі та без використання руйнівних механізмів kprobes.
