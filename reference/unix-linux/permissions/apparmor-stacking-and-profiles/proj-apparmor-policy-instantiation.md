# ⚙️ Динамічна інстанціація політик AppArmor та керування стеком у коді

Для динамічних систем контейнеризації, облачних платформ обчислень або sandbox-ізоляції виникає потреба під час виконання програми підготувати профіль на основі шаблону, завантажити його в ядро та запустити цільовий процес у стеку з цим профілем.

Динамічна інстанціація дозволяє не зберігати сотні статичних файлів конфігурації на диску, а генерувати точні правила під конкретний ідентифікатор контейнера чи тимчасовий каталог у пам'яті за декілька мілісекунд.

Нижче наведено практичну реалізацію демона-ізолятора мовами C та C++, який виконує три основні завдання:
1. Зчитує шаблон профілю з підстановкою змінних (динамічний шлях до ізольованого каталогу та ідентифікатор ізоляції).
2. Завантажує інстанційований профіль у ядро Linux через файловий інтерфейс `/sys/kernel/security/apparmor/.load`.
3. Викликає `aa_change_onexec()` або `aa_stack_onexec()` для безпечного переходу в новий стекований профіль при запуску робочого процесу.

:::tabs
```c
/* c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/apparmor.h>
#include <sys/stat.h>

#define PROFILE_TEMPLATE \
    "profile %s flags=(attach_disconnected) {\n" \
    "  file,\n" \
    "  deny /etc/shadow rw,\n" \
    "  %s/ r,\n" \
    "  %s/** rw,\n" \
    "}\n"

static int load_profile_to_kernel(const char *profile_text) {
    int fd = open("/sys/kernel/security/apparmor/.load", O_WRONLY);
    if (fd < 0) {
        perror("Failed to open securityfs .load interface");
        return -1;
    }

    size_t len = strlen(profile_text);
    ssize_t written = write(fd, profile_text, len);
    close(fd);

    if (written != (ssize_t)len) {
        fprintf(stderr, "Failed to write full profile to kernel\n");
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <profile_name> <sandbox_dir>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *prof_name = argv[1];
    const char *sandbox_dir = argv[2];

    char profile_buf[2048];
    snprintf(profile_buf, sizeof(profile_buf), PROFILE_TEMPLATE, prof_name, sandbox_dir, sandbox_dir);

    printf("[C Engine] Instantiating AppArmor profile '%s' for dir '%s'...\n", prof_name, sandbox_dir);

    if (load_profile_to_kernel(profile_buf) < 0) {
        fprintf(stderr, "[C Engine] Error loading instantiated profile.\n");
        return EXIT_FAILURE;
    }

    /* Налаштовуємо стекування профілів під час наступного execve */
    char stack_target[512];
    snprintf(stack_target, sizeof(stack_target), "docker-default//&%s", prof_name);

    printf("[C Engine] Scheduling stacked exec transition to '%s'...\n", stack_target);
    if (aa_change_onexec(stack_target) < 0) {
        perror("[C Engine] aa_change_onexec failed");
        return EXIT_FAILURE;
    }

    /* Запускаємо цільовий процес у стеку */
    char *worker_args[] = { "/bin/bash", "-c", "echo 'Inside sandbox'; id", NULL };
    execvp(worker_args[0], worker_args);

    perror("[C Engine] execvp failed");
    return EXIT_FAILURE;
}
```
```cpp
// cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <format>
#include <filesystem>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/apparmor.h>

namespace fs = std::filesystem;

class AppArmorPolicyEngine {
public:
    static std::expected<void, std::string> load_instantiated_profile(
        std::string_view profile_name, 
        const fs::path& sandbox_path
    ) {
        std::string profile_content = std::format(
            "profile {} flags=(attach_disconnected) {{\n"
            "  file,\n"
            "  deny /etc/shadow rw,\n"
            "  {} r,\n"
            "  {}/** rw,\n"
            "}}\n",
            profile_name, sandbox_path.string(), sandbox_path.string()
        );

        int fd = ::open("/sys/kernel/security/apparmor/.load", O_WRONLY | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::format("Cannot open securityfs .load: {}", ::strerror(errno)));
        }

        ssize_t written = ::write(fd, profile_content.data(), profile_content.size());
        ::close(fd);

        if (written != static_cast<ssize_t>(profile_content.size())) {
            return std::unexpected("Incomplete profile write into securityfs kernel interface");
        }

        return {};
    }

    static std::expected<void, std::string> schedule_stacked_transition(
        std::string_view base_profile, 
        std::string_view target_profile
    ) {
        std::string stack_spec = std::format("{}//&{}", base_profile, target_profile);
        if (::aa_change_onexec(stack_spec.c_str()) < 0) {
            return std::unexpected(std::format("aa_change_onexec failed for '{}': {}", stack_spec, ::strerror(errno)));
        }
        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << std::format("Usage: {} <profile_name> <sandbox_dir>\n", argv[0]);
        return EXIT_FAILURE;
    }

    std::string profile_name = argv[1];
    fs::path sandbox_dir = argv[2];

    std::cout << std::format("[C++ Engine] Instantiating policy '{}' for path '{}'...\n", profile_name, sandbox_dir.string());

    auto load_res = AppArmorPolicyEngine::load_instantiated_profile(profile_name, sandbox_dir);
    if (!load_res) {
        std::cerr << std::format("[C++ Engine] Error: {}\n", load_res.error());
        return EXIT_FAILURE;
    }

    auto stack_res = AppArmorPolicyEngine::schedule_stacked_transition("docker-default", profile_name);
    if (!stack_res) {
        std::cerr << std::format("[C++ Engine] Error: {}\n", stack_res.error());
        return EXIT_FAILURE;
    }

    std::cout << "[C++ Engine] Transition scheduled successfully. Executing worker binary...\n";

    std::vector<const char*> exec_args = { "/bin/bash", "-c", "echo 'Worker process running under stacked AppArmor profile'; id", nullptr };
    ::execvp(exec_args[0], const_cast<char* const*>(exec_args.data()));

    std::perror("[C++ Engine] execvp failed");
    return EXIT_FAILURE;
}
```
:::

### Покроковий розбір коду та архітектурних рішень

Розглянемо детально кожен етап виконання поданої програми та порівняємо реалізації на C та C++:

1. **Формування текстового профілю в пам'яті**: Програма виключає необхідність зберігання тимчасових `.sd` файлів на диску, створюючи текстове представлення профілю безпосередньо у виділеному буфері пам'яті. У C-версії застосовується безпечний форматний виклик `snprintf()`, тоді як у C++20 використовується типабезпечний шаблон `std::format()`. Прапор `flags=(attach_disconnected)` інформує ядро про те, що якщо цільовий процес буде ізольовано у власному маунт-просторі (mount namespace), файли поза його відносною ієрархією мають прив'язуватися до віртуального кореня `/`, а не викликати помилки доступу VFS.
2. **Прямий запис у `securityfs`**: Для завантаження профілю програма відкриває спеціальний системний вузол `/sys/kernel/security/apparmor/.load`. Запис у цей файл здійснює атомарну компіляцію й завантаження нового профілю в ядро. Якщо профіль з таким іменем уже існує, ядро поверне помилку `EEXIST` або `EACCES`; для заміни існуючого профілю слід використовувати файл `.replace`. У C++ реалізації файл відкривається з прапорцем `O_CLOEXEC` для автоматичного закриття дескриптора при подальшому `execve()`.
3. **Планування переходу через `aa_change_onexec`**: Замість негайної зміни профілю в поточному процесі (що призвело б до втрати привілеїв, необхідних для виконання виклику `execve`), програма використовує запланований перехід `aa_change_onexec()`. Рядок `"docker-default//&profile_name"` повідомляє ядру про необхідність створення стеку з хостового профілю контейнера та щойно завантаженого динамічного профілю.

### Порівняльний аналіз ідіом C та C++

У запропонованих прикладах реалізовано різні підходи до керування ресурсами та обробки помилок:

- **C-реалізація** покладається на системний функціонал `POSIX` та базову бібліотеку `libapparmor`. Усі системні помилки перевіряються через повернене значення `-1` та друкуються функцією `perror()`. Помилки введення-виведення при записі в дескриптор обробляються прямою перевіркою повернутої кількості байтів `written == len`.
- **C++20 реалізація** демонструє сучасні об'єктно-орієнтовані ідіоми. Для обробки помилок використовується монодичний тип `std::expected<void, std::string>`, який дозволяє явно повертати статус виконання без викидання винятків (що є критичним для системного коду). Тип `std::filesystem::path` гарантує правильну обробку системних розділювачів шляхів, а `std::string_view` позбавляє від зайвого копіювання рядків у пам'яті.

### Практичні пастки реалізації та запобіжні заходи

Під час розробки виробничих систем інстанціації слід враховувати наступні крайові випадки:

1. **Права доступу до `securityfs`**: Відкриття файлу `/sys/kernel/security/apparmor/.load` у режимі запису вимагає наявності системної capability `CAP_MAC_ADMIN` або виконання від імені `root` у початковому просторі імен системних привілеїв.
2. **Очищення вивантажених політик**: Після завершення роботи ізольованого дочірнього процесу демон має вилучити динамічний профіль з ядра, записавши його ім'я у файл `/sys/kernel/security/apparmor/.remove`. Інакше таблиця профілів ядра поступово засмічуватиметься застарілими записами.
3. **Одноразовість запланованого переходу**: Прапор `aa_change_onexec()` діє строго на один наступний виклик `execve()`. Якщо дочірній процес згодом виконує ще один `execve()`, запланований перехід скидається, і ядро застосовує звичайні правила автоматичного переходу (`px`/`ix`).
4. **Обробка сигналів переривання**: Якщо процес-завантажувач отримує неперехоплений сигнал `SIGKILL` або `SIGSEGV` між кроками `load_profile` та `execve`, інстанційований профіль залишається завантаженим у ядрі. У промислових демонах реалізують обробник сигналів з автоматичним відкатом та вивантаженням через `.remove`.
5. **Валідація синтаксису профілю**: Запис некоректного файлу політики у `.load` поверне помилку `EINVAL`. Рекомендується попередньо перевіряти синтаксис профілю у користувацькому просторі через запуск `apparmor_parser -Q` (quiet check mode) до відкриття системного файлу.
6. **Робота без привілеїв у Rootless-контейнерах**: У rootless-контейнерах спроба запису в `/sys/kernel/security/apparmor/.load` завершиться помилкою `EPERM`, оскільки у незахищеному user namespace права `CAP_MAC_ADMIN` обмежені локально. У таких середовищах інстанціацію має виконувати зовнішній хостовий агент (наприклад, Security Profiles Operator), який спілкується з контейнером через gRPC або Unix domain socket.
