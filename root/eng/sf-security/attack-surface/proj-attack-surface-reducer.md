# ⚙️ Мінімізація поверхні атаки демона: Seccomp-BPF, ізоляція просторів імен та скидання привілеїв

Коли мережевий сервіс приймає складні бінарні пакети від неавтентифікованих клієнтів з відкритої мережі, навіть ретельний аудит коду не може гарантувати відсутності вразливостей переповнення буфера або помилок логіки парсера. Якщо такий сервіс виконується з правами адміністратора (`root`) у глобальному просторі операційної системи, успішна експлуатація парсера дає зловмиснику повний контроль над сервером (виконання довільних команд `execve`, ін'єкція в інші процеси `ptrace`, несанкціоноване відкриття сокетів та читання файлової системи).

Щоб мінімізувати поверхню атаки, застосовують архітектурний патерн **розподілу привілеїв та ізоляції у пісочнику** (англ. *Privilege Separation & Sandboxing*). Вся складна логіка розбору недовірених даних виноситься в ізольований дочірній процес-парсер, який:
1. Повністю скидає системні привілеї та очищає таблицю додаткових груп (перехід до `UID 65534 / nobody`);
2. Закриває всі успадковані дескриптори файлів та сокетів;
3. Відсікає видимість файлової системи та мережі через простори імен Linux (`unshare(2)`);
4. Встановлює фільтр `seccomp-bpf`, скорочуючи доступний набір системних викликів ядра з понад 450 до 5 мінімально необхідних (`read`, `write`, `exit_group`, `futex`, `sigreturn`).

У результаті, навіть якщо зловмисник отримає повне виконання довільного машинно-орієнтованого шеллкоду всередині парсера, він не зможе виконати системний виклик `execve` чи відкрити файл: ядро Linux негайно знищить процес із сигналом `SIGSYS`.

## 1. Архітектурна послідовність та порядок ізоляції

Порядок операцій під час накладання обмежень має фундаментальне значення для безпеки. Будь-яка зміна послідовності кроків створює вікно вразливості, через яке процес може зберегти привілеї або пробити межу ізоляції:

```
[ Батьківський процес: Координатор ]
  1. Відкриває сокет та канали IPC (Unix Pipe / Socketpair)
  2. Створює дочірній процес через fork()
        │
        ▼
[ Дочірній процес: Ізольований парсер ]
  3. Закриває зайві дескриптори: close() в циклі для всіх fd >= 3
  4. Очищає додаткові групи: setgroups(0, NULL)
  5. Безповоротно змінює GID та UID: setresgid(), setresuid()
  6. Ізолює простори імен: unshare(CLONE_NEWNS | CLONE_NEWNET)
  7. Вмикає заборону підвищення прав: prctl(PR_SET_NO_NEW_PRIVS, 1)
  8. Компілює та завантажує фільтр Seccomp-BPF
  9. Блокує всі виклики крім: read(0), write(1), exit_group(), futex, sigreturn
        │
        ▼
  10. Читає сирі байти з Pipe -> Парсить структуру -> Повертає результат
```

### Критичні пастки порядку налаштування

- **Пастка збереженого UID (Saved UID):** Використання застарілого виклику `setuid(uid)` замість `setresuid(uid, uid, uid)` залишає збережений ідентифікатор користувача (`saved-set-UID`) рівним `0`. Зловмисник, захопивши процес, може повернути повні права `root` одним викликом `seteuid(0)`. Виклик `setresuid` одночасно перезаписує real, effective та saved ідентифікатори, роблячи повернення неможливим на рівні ядра.
- **Пастка додаткових груп (Supplementary Groups):** Зміна лише основного `GID` не скидає членство процесу в системних групах (`wheel`, `sudo`, `docker`, `disk`). Якщо перед скиданням `UID` не викликати `setgroups(0, NULL)`, скомпрометований процес зможе напряму читати блокові пристрої дисків або взаємодіяти з демоном Docker через сокети.
- **Пастка витоку дескрипторів (Descriptor Leakage):** Дочірній процес автоматично успадковує всі відкриті файлові дескриптори батьківського процесу (сокет бази даних, лог-файли, конфігураційні файли). Якщо їх не закрити перед запуском логіки, зловмисник зможе записувати дані в базу або читати системні логи через успадковані номери `fd` без системного виклику `openat`.
- **Пастка сумісності архітектур (Multi-arch ABI Bypass):** На 64-бітній платформі x86_64 процесор підтримує як 64-бітний системний інтерфейс, так і 32-бітний режим сумісності `int 0x80`. Номери системних викликів у них різні: наприклад, номер `11` у 32-бітному режимі відповідає `sys_execve`, тоді як у 64-бітному режимі номер `11` відповідає безпечному виклику `sys_munmap`. Фільтр BPF зобов'язаний першою інструкцією перевіряти поле `arch == AUDIT_ARCH_X86_64`.
- **Взаємодія з алокатором пам'яті (Memory Allocator Hooks):** Стандартна бібліотека `glibc` при динамічному виділенні пам'яті (`malloc`) звертається до викликів `brk`, `mmap` або `madvise`. Якщо пісочниця не виділила робочий буфер наперед, спроба динамічного розширення купи викличе аварійне завершення процесу через Seccomp. Усі необхідні буфери слід виділяти до завантаження фільтра або додавати `SYS_brk` до списку дозволених.
- **Динамічне завантаження бібліотек (Dynamic Linking Traps):** Будь-який виклик `dlopen()` або розв'язання лінивих символів (Lazy Binding) потребує викликів `openat`, `mmap`, `mprotect`. У закритій пісочниці ліниве зв'язування призводить до збою. Для запобігання аваріям програму слід лінкувати з прапорцем `-Wl,-z,now` (Immediate Binding), що примусово завантажує всю таблицю глобальних зміщень GOT до накладання Seccomp.

## 2. Реалізація загартованого процесу-пісочника

Нижче наведено повну реалізацію захищеного воркера мовами C та C++.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stddef.h>
#include <grp.h>
#include <sched.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>

#define UNPRIV_UID 65534 /* nobody */
#define UNPRIV_GID 65534 /* nogroup */

/* Встановлення суворого фільтра Seccomp-BPF */
static int install_strict_seccomp(void) {
    struct sock_filter filter[] = {
        /* [0] Завантажуємо номер архітектури процесора з seccomp_data */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        
        /* [1] Перевіряємо відповідність x86_64; якщо ні — аварійне завершення */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* [2] Завантажуємо номер системного виклику */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* [3-7] Білий список дозволених системних викликів */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_read,       4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_write,      3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_exit_group, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_futex,      1, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_sigreturn,  0, 1),

        /* [8] Якщо виклик у білому списку — дозволити виконання */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        /* [9] Усі інші виклики (execve, openat, socket тощо) — миттєве вбивство процесу */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    /* Обов'язкова вимога: процес не може отримати нові привілеї через execve SUID */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    /* Завантаження фільтра BPF у ядро */
    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) == -1) {
        perror("seccomp(SECCOMP_SET_MODE_FILTER)");
        return -1;
    }

    return 0;
}

/* Функція обмеження та запуску ізольованого парсера */
void run_sandboxed_worker(int input_fd, int output_fd) {
    /* 1. Закриття всіх успадкованих дескрипторів крім input_fd та output_fd */
    for (int fd = 3; fd < 1024; ++fd) {
        if (fd != input_fd && fd != output_fd) {
            close(fd);
        }
    }

    /* 2. Скидання додаткових груп */
    if (setgroups(0, NULL) != 0 && errno != EPERM) {
        perror("setgroups");
        _exit(1);
    }

    /* 3. Скидання привілеїв GID та UID (real, effective, saved) */
    if (setresgid(UNPRIV_GID, UNPRIV_GID, UNPRIV_GID) != 0) {
        perror("setresgid");
        _exit(1);
    }
    if (setresuid(UNPRIV_UID, UNPRIV_UID, UNPRIV_UID) != 0) {
        perror("setresuid");
        _exit(1);
    }

    /* 4. Ізоляція просторів імен (Network + Mount) */
    if (unshare(CLONE_NEWNS | CLONE_NEWNET) != 0 && errno != EPERM) {
        perror("unshare");
    }

    /* 5. Встановлення BPF-фільтра для мінімізації викликів ядра */
    if (install_strict_seccomp() != 0) {
        fprintf(stderr, "Помилка встановлення Seccomp\n");
        _exit(1);
    }

    /* 6. Безпечне читання та розбір вхідного пакету */
    char buffer[256];
    ssize_t bytes_read = read(input_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        const char *resp = "OK: Пакет успішно валідовано в пісочнику\n";
        write(output_fd, resp, strlen(resp));
    }

    _exit(0);
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <system_error>
#include <expected>
#include <cstddef>
#include <unistd.h>
#include <grp.h>
#include <sched.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>

namespace sandbox {

constexpr uid_t kUnprivilegedUid = 65534; // nobody
constexpr gid_t kUnprivilegedGid = 65534; // nogroup

class [[nodiscard]] ScopedDescriptor {
public:
    explicit ScopedDescriptor(int fd = -1) noexcept : fd_{fd} {}
    ~ScopedDescriptor() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;
    ScopedDescriptor(ScopedDescriptor&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_;
};

class SeccompFilterBuilder {
public:
    SeccompFilterBuilder() {
        // Завантаження архітектури та перевірка x86_64
        instructions_.push_back(BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))));
        instructions_.push_back(BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0));
        instructions_.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS));

        // Завантаження номера системного виклику
        instructions_.push_back(BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))));
    }

    void allow_syscall(int syscall_number) {
        allowed_syscalls_.push_back(syscall_number);
    }

    std::expected<void, std::error_code> apply() {
        for (size_t i = 0; i < allowed_syscalls_.size(); ++i) {
            auto remaining = static_cast<uint8_t>(allowed_syscalls_.size() - 1 - i);
            instructions_.push_back(BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 
                                             static_cast<uint32_t>(allowed_syscalls_[i]), 
                                             remaining, 0));
        }

        // Дія за замовчуванням при збігу — дозволити
        instructions_.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW));
        // Усі інші системні виклики призводять до негайного знищення процесу
        instructions_.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS));

        struct sock_fprog prog {
            .len = static_cast<unsigned short>(instructions_.size()),
            .filter = instructions_.data(),
        };

        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }

private:
    std::vector<struct sock_filter> instructions_;
    std::vector<int> allowed_syscalls_;
};

void run_sandboxed_worker(int input_fd, int output_fd) {
    // 1. Закриття всіх сторонніх файлових дескрипторів
    for (int fd = 3; fd < 1024; ++fd) {
        if (fd != input_fd && fd != output_fd) {
            ::close(fd);
        }
    }

    // 2. Очищення списку додаткових груп
    if (::setgroups(0, nullptr) != 0 && errno != EPERM) {
        std::_Exit(1);
    }

    // 3. Скидання привілеїв GID та UID (real, effective, saved)
    if (::setresgid(kUnprivilegedGid, kUnprivilegedGid, kUnprivilegedGid) != 0) {
        std::_Exit(1);
    }
    if (::setresuid(kUnprivilegedUid, kUnprivilegedUid, kUnprivilegedUid) != 0) {
        std::_Exit(1);
    }

    // 4. Ізоляція просторів імен (Network + Mount)
    [[maybe_unused]] auto ns_res = ::unshare(CLONE_NEWNS | CLONE_NEWNET);

    // 5. Накладання суворого BPF-фільтра
    SeccompFilterBuilder sandbox;
    sandbox.allow_syscall(SYS_read);
    sandbox.allow_syscall(SYS_write);
    sandbox.allow_syscall(SYS_exit_group);
    sandbox.allow_syscall(SYS_futex);
    sandbox.allow_syscall(SYS_sigreturn);

    if (auto res = sandbox.apply(); !res.has_value()) {
        std::_Exit(1);
    }

    // 6. Безпечне виконання розбору даних
    char buffer[256];
    const auto bytes_read = ::read(input_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        constexpr std::string_view response = "OK: Пакет валідовано в C++ пісочнику\n";
        [[maybe_unused]] auto written = ::write(output_fd, response.data(), response.size());
    }

    std::_Exit(0);
}

} // namespace sandbox
```
:::

## 3. Продуктивність Seccomp: оптимізація порядку інструкцій

Перевірка кожного системного виклику додає накладні витрати на виконання BPF-інструкцій у ядрі. Якщо в ядрі увімкнено JIT-компілятор BPF (`net.core.bpf_jit_enable = 1`), програма Seccomp транслюється у прямі інструкції процесора, додаючи лише 10–20 тактів CPU на виклик, що є незначним порівняно з ціною перемикання контексту процесора (1200–1500 тактів).

Для мінімізації накладних витрат у високонавантажених сервісах:
1. **Сортування за частотою викликів:** Найбільш часті системні виклики (`read`, `write`, `futex`) розміщуються на самому початку ланцюжка порівнянь, забезпечуючи вихід з фільтра за `O(1)` операцій;
2. **Деревоподібний пошук (Binary Search Jump Table):** При великій кількості дозволених викликів (понад 20) лінійний список `BPF_JEQ` замінюють на двійкове дерево пошуку через `BPF_JGT`, скорочуючи кількість переходів з `O(N)` до `O(log N)`.

## 4. Перевірка ефективності пісочника та верифікація захисту

Для інженерної верифікації звуження поверхні атаки використовують дві взаємодоповнюючі методики:

### 4.1. Статистичне трасування через `strace`
Запуск процесу під наглядом трасувальника дозволяє побачити точний список викликів ядра під час штатних операцій:

```bash
# Підрахунок системних викликів процесу
strace -c ./sandboxed_daemon
```

У виведеному звіті повинні бути присутні виключно системні виклики `read`, `write`, `exit_group` та `futex`. Будь-який несподіваний виклик свідчить про наявність неврахованої бібліотечної залежності або стороннього коду ініціалізації.

### 4.2. Симуляція експлуатації вразливості
Якщо зловмисник спробує викликати заборонений системний виклик (наприклад, `execve("/bin/sh")` або відкрити мережевий сокет `socket(AF_INET, SOCK_STREAM, 0)`), ядро миттєво відправить процесу сигнал `SIGSYS` (код завершення `159` або `Bad system call`), а в системний журнал `auditd` буде записано подію аудиту:

```text
type=SECCOMP msg=audit(1692561234.567:42): auid=1000 uid=65534 gid=65534 ses=1 
pid=14208 comm="sandboxed_work" exe="/usr/bin/daemon" sig=31 arch=c000003e 
syscall=59 compat=0 ip=0x7f9a12345678 code=0x0
```

Номер системного виклику `syscall=59` відповідає `execve` на архітектурі x86_64. Ядро заблокувало запуск шелла ще до передачі керування підсистемі керування процесами, повністю знешкодивши вектор експлуатації на фундаментальному рівні ОС.
