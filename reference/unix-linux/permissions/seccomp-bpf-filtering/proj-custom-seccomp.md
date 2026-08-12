# ⚙️ Побудова та інкапсуляція фільтрів Seccomp-BPF мовами C та C++

Практичне створення пісочниць (sandboxes) вимагає переведення високорівневих політики безпеки додатка у байт-код cBPF або виклики високорівневої бібліотеки `libseccomp`. Для безпечної роботи у мовах із керуванням ресурсами важливими є гарантії гарантованого звільнення контекстів та відсутність витоків пам'яті та файлових дескрипторів.

Покрокова побудова практичних пісочниць вимагає від розробника чіткого розуміння архітектурних вимог, послідовності завантаження правил та механізмів обробки помилок виконання. Нижче наведено розбір задач побудови ізольованого обробника даних із використанням низькорівневого сирого cBPF та високорівневої бібліотеки `libseccomp`.

## 1. Архітектурне завдання: Ізоляція обробника даних (Data Worker Sandbox)

Розглянемо практичну задачу побудови захищеного середовища для демона обробки некоординованих даних. Воркер приймає вхідний потік з файлового дескриптора, виконує обчислення у пам'яті і повертає результат у вихідний дескриптор. Для мінімізації поверхні атак воркер повинен мати дозвіл лише на обмежений набір дій:

1. Системний виклик `read` — дозволяється тільки для читання вхідних байтів з відкритого файлового дескриптора.
2. Системний виклик `write` — дозволяється тільки для запису результату у стандартні файлові дескриптори виводу.
3. Виклики управління пам'яттю `brk` та `mmap` — необхідні для функціонування динамічного виділення пам'яті (`malloc` у C та `operator new` у C++).
4. Системні виклики завершення `exit` та `exit_group` — для коректного завершення роботи процесу чи його потоків.

Будь-які інші виклики (створення нових процесів `clone`/`execve`, відкриття нових файлів `openat`, мережеві виклики `socket` або підключення до `ptrace`) повинні негайно знищувати процес з кодом `SECCOMP_RET_KILL_PROCESS`. Це унеможливлює розгортання коду експлойта навіть при наявності уразливості у коді обробки даних.

## 2. Нюанси розрахунку інструкцій cBPF та адресації пам'яті

Класичний BPF використовує 32-бітний акумулятор `A`. Оскільки аргументи системних викликів `args[6]` у структурі `seccomp_data` мають розмірність 64 біти, перевірка аргументу вимагає виконання двох послідовних завантажень по 32 біти (молодше слово та старше слово).

При розрахунку відносних зміщень у переходах `jt` (Jump True) та `jf` (Jump False) слід пам'ятати, що значення зміщення виражається у кількості інструкцій, які потрібно пропустити вперед, починаючи від **наступної** після даної інструкції. Зміщення `jt = 0` означає перехід на відразу наступну інструкцію.

Приклад правильного розрахунку переходів для перевірки архітектури:
- Інструкція `[0]` завантажує `arch` у регістр `A`.
- Інструкція `[1]` порівнює `A` із константою `AUDIT_ARCH_X86_64`. Якщо порівняння істинне, виконується `jt = 0` (тобто перехід до наступної інструкції `[2]`). Якщо хибне, виконується `jf = 9` (тобто пропуск 9 інструкцій і перехід на інструкцію `[11]`, яка повертає `SECCOMP_RET_KILL_PROCESS`).

## 3. Варіант 1: Сирий cBPF фільтр з перевіркою аргументів

Низькорівневий підхід реалізує завантаження BPF без залучення сторонніх бібліотек. Фільтр створюється у вигляді масиву `struct sock_filter`, який включає обов'язкові перевірки номеру архітектури та послідовну перевірку номерів системних викликів.

Перед завантаженням BPF обов'язково встановлюється прапорець `PR_SET_NO_NEW_PRIVS`. Без цього виклик `prctl(PR_SET_SECCOMP)` поверне помилку `EPERM` для непривілейованого користувача.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <unistd.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>

#define syscall_nr (offsetof(struct seccomp_data, nr))
#define arch_nr (offsetof(struct seccomp_data, arch))

int apply_cbpf_worker_sandbox(void) {
    // 1. Обов'язкове вимкнення отримання нових привілеїв
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    struct sock_filter filter[] = {
        // [0] Завантажити номер архітектури у регістр A
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, arch_nr),
        // [1] Перевірити AUDIT_ARCH_X86_64; якщо рівно — перейти далі (jt=0), якщо хиба — перестрибнути до KILL (jf=9)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 0, 9),

        // [2] Завантажити номер системного виклику у регістр A
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, syscall_nr),

        // Перевірка дозволених викликів білого списку
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read, 5, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_brk, 3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mmap, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group, 1, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit, 0, 1),

        // [9] ALLOW — дозволити системний виклик
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        // [10] KILL — негайно вбити процес для будь-якого іншого виклику
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == -1) {
        perror("prctl(SECCOMP_MODE_FILTER)");
        return -1;
    }

    return 0;
}

int main(void) {
    printf("Активація сирого cBPF фільтра...\n");
    if (apply_cbpf_worker_sandbox() < 0) {
        fprintf(stderr, "Помилка встановлення пісочниці\n");
        return 1;
    }

    write(STDOUT_FILENO, "Пісочниця працює успішно!\n", 26);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstddef>
#include <system_error>
#include <expected>
#include <string_view>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>

namespace sandbox {

#define syscall_nr (offsetof(struct seccomp_data, nr))
#define arch_nr (offsetof(struct seccomp_data, arch))

class RawCbpfSandbox {
public:
    static std::expected<void, std::string> apply_strict_worker() noexcept {
        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
            return std::unexpected("Failed to set PR_SET_NO_NEW_PRIVS: " + std::string(strerror(errno)));
        }

        const std::vector<sock_filter> filter = {
            // Завантаження та перевірка архітектури
            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, arch_nr),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 0, 9),

            // Завантаження номера виклику
            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, syscall_nr),

            // Дозволи для необхідних системних викликів
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read, 5, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 4, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_brk, 3, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mmap, 2, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group, 1, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit, 0, 1),

            // Повернення дій: ALLOW або KILL
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
        };

        const sock_fprog prog = {
            .len = static_cast<unsigned short>(filter.size()),
            .filter = const_cast<sock_filter*>(filter.data()),
        };

        if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == -1) {
            return std::unexpected("Failed to apply SECCOMP_MODE_FILTER: " + std::string(strerror(errno)));
        }

        return {};
    }
};

} // namespace sandbox

int main() {
    std::cout << "Активація C++ cBPF пісочниці...\n";
    auto res = sandbox::RawCbpfSandbox::apply_strict_worker();
    if (!res) {
        std::cerr << "Помилка: " << res.error() << '\n';
        return 1;
    }

    constexpr std::string_view msg = "C++ пісочниця активна!\n";
    write(STDOUT_FILENO, msg.data(), msg.size());
    return 0;
}
```
:::

У наведеному коді макрос `BPF_STMT` формує базові інструкції завантаження даних `BPF_LD`, а `BPF_JUMP` виконує порівняння `BPF_JEQ`. Якщо номер архітектури чи системний виклик не збігаються, перехід спрямовується на інструкцію `SECCOMP_RET_KILL_PROCESS`.

## 4. Варіант 2: Високорівнева реалізація через `libseccomp` та RAII інкапсуляція

Бібліотека `libseccomp` суттєво спрощує підтримку правил, знімаючи з розробника потребу вручну вираховувати відносні індекси переходів (`jt` і `jf`). Вона автоматично генерує збалансоване дерево порівнянь системних викликів і транслює їх у JIT-код.

У мові C++ ми застосовуємо паттерн RAII (Resource Acquisition Is Initialization), створюючи смарт-вказівник із власним кастомним деструктором `seccomp_release`. Це гарантує вивільнення внутрішнього контексту фільтра при виникненні винятків чи помилок під час збирання правил.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <seccomp.h>
#include <unistd.h>

int apply_libseccomp_sandbox(void) {
    // 1. Ініціалізація: дія за замовчуванням — KILL_PROCESS
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
    if (ctx == NULL) {
        fprintf(stderr, "seccomp_init failed\n");
        return -1;
    }

    int ret = -1;

    // 2. Додаємо виклики у білий список
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(brk), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mmap), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0) < 0) goto out;

    // 3. Завантаження фільтра в ядро
    if (seccomp_load(ctx) < 0) {
        fprintf(stderr, "seccomp_load failed\n");
        goto out;
    }

    ret = 0;

out:
    // Контекст вивільняється завжди
    seccomp_release(ctx);
    return ret;
}

int main(void) {
    if (apply_libseccomp_sandbox() < 0) {
        return 1;
    }
    printf("libseccomp увімкнено успішно!\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <expected>
#include <vector>
#include <seccomp.h>
#include <unistd.h>

namespace sandbox {

struct SeccompDeleter {
    void operator()(scmp_filter_ctx ctx) const noexcept {
        if (ctx) {
            seccomp_release(ctx);
        }
    }
};

using ScmpContext = std::unique_ptr<void, SeccompDeleter>;

class LibSeccompSandbox {
public:
    static std::expected<void, std::string> apply_worker_policy() {
        scmp_filter_ctx raw_ctx = seccomp_init(SCMP_ACT_KILL);
        if (!raw_ctx) {
            return std::unexpected("seccomp_init failed");
        }
        ScmpContext ctx(raw_ctx);

        const std::vector<int> allowed_syscalls = {
            SCMP_SYS(read),
            SCMP_SYS(write),
            SCMP_SYS(brk),
            SCMP_SYS(mmap),
            SCMP_SYS(exit_group),
            SCMP_SYS(exit)
        };

        for (int sys_nr : allowed_syscalls) {
            if (seccomp_rule_add(ctx.get(), SCMP_ACT_ALLOW, sys_nr, 0) < 0) {
                return std::unexpected("Failed to add rule for syscall number: " + std::to_string(sys_nr));
            }
        }

        if (seccomp_load(ctx.get()) < 0) {
            return std::unexpected("seccomp_load failed to install filter");
        }

        return {};
    }
};

} // namespace sandbox

int main() {
    auto status = sandbox::LibSeccompSandbox::apply_worker_policy();
    if (!status) {
        std::cerr << "Помилка встановлення політики: " << status.error() << '\n';
        return 1;
    }
    std::cout << "libseccomp RAII пісочниця активована!\n";
    return 0;
}
```
:::

Компіляція проектів із `libseccomp` вимагає лінкування з прапорцем `-lseccomp`:

```bash
# Компіляція прикладу мовою C
gcc -Wall -Wextra -O2 -o worker_c worker.c -lseccomp

# Компіляція прикладу мовою C++23
g++ -std=c++23 -Wall -Wextra -O2 -o worker_cpp worker.cpp -lseccomp
```

## 5. Налагодження та тестування за допомогою strace

При проведенні налагодження створених фільтрів важливо мати змогу ідентифікувати виклики, які блокуються ядром. Інструмент `strace` дозволяє відстежити точну інструкцію, на якій програма завершується:

```bash
strace -f ./worker_c
```

Якщо фільтр блокує виклик дією `SECCOMP_RET_KILL_PROCESS`, вивід `strace` зафіксує сигнал `SIGSYS`:

```
...
openat(AT_FDCWD, "/etc/passwd", O_RDONLY) = ?
+++ killed by SIGSYS (core dumped) +++
```

У разі якщо дія встановлена в `SECCOMP_RET_ERRNO` із кодом `EPERM`, `strace` відобразить системний виклик як такий, що повернув відмову ядра, що полегшує діагностику додатків у контейнерах без зупинки процесу.

## 6. Багатопотоковість та синхронізація через SECCOMP_FILTER_FLAG_TSYNC

При використанні seccomp у багатопотокових додатках важливим фактором є забезпечення того, щоб фільтр застосовувався до **всіх** потоків процесу, а не лише до того потоку, який викликав `seccomp(2)`.

За замовчуванням завантаження фільтра діє лише на поточний потік та його **майбутніх** дітей (створених через `clone`/`pthread_create` після завантаження). Потоки, які вже існували на момент завантаження фільтра, продовжуватимуть виконуватися без обмежень.

Для вирішення цієї проблеми у виклику `seccomp(2)` використовується прапорець `SECCOMP_FILTER_FLAG_TSYNC`. При його вказуванні ядро атомарно проходиться по всіх потоках групи (`thread group`), перевіряє їх придатність і накладає фільтр на кожен потік. Якщо хоч один потік не може прийняти фільтр, оновлення відхиляється повністю з кодом `EBUSY`.
