# 📋 Інтерфейси LSM ядра Linux та функції користувацької бібліотеки libselinux

Взаємодія з обов'язковим контролем доступу в Linux відбувається на двох рівнях: на рівні ядра операційної системи, де підсистема Linux Security Modules (LSM) перехоплює системні виклики через ланцюжки хуків, та на рівні простору користувача, де системні бібліотеки (`libselinux`, `libapparmor`, `libsmack`) дозволяють прикладним службам запитувати контексти безпеки, перевіряти вектор дозволів і керувати мітками файлів.

Нижче наведено технічний огляд внутрішніх структур LSM, порядку реєстрації модулів, протоколу взаємодії з віртуальною файловою системою `selinuxfs`, порівняння з API AppArmor/SMACK та функцій простору користувача.

---

### 1. Архітектура хуків підсистеми LSM у ядрі

Підсистема LSM не реалізує власної безпекової політики, а надає ядру уніфікований інтерфейс зворотних викликів. Хуки LSM розміщуються в критичних точках підсистем ядра: безпосередньо перед відкриттям файлу у VFS, перед створенням або підключенням сокета в мережевому стеку, перед надсиланням POSIX-сигналу в планувальнику завдань та під час виклику `execve()`.

Усі зареєстровані хуки зберігаються в глобальній структурі таблиці вказівників `security_hook_heads` (заголовок ядра `include/linux/lsm_hooks.h`). Кожен запис у цій структурі є зв'язним списком `struct hlist_head`, що дозволяє декільком модулям безпеки одночасно реєструвати власні функції-обробники на ту саму системну подію.

```
struct security_hook_heads
  ├── file_open           ──> [ capability_hook ] ──> [ selinux_file_open ] ──> [ apparmor_file_open ]
  ├── inode_permission    ──> [ selinux_inode_permission ] ──> [ smack_inode_permission ]
  ├── task_kill           ──> [ yama_task_kill ] ──> [ selinux_task_kill ]
  ├── socket_connect      ──> [ selinux_socket_connect ] ──> [ smack_socket_connect ]
  └── bprm_creds_for_exec ──> [ selinux_bprm_creds_for_exec ] ──> [ apparmor_bprm_creds ]
```

Коли підсистема VFS викликає хук `security_file_open()`, макрос ядра `call_int_hook` послідовно обходить список зареєстрованих функцій:

```
call_int_hook(file_open, 0, file)
  │
  ├── 1. Виклик selinux_file_open(file)  ==> повертає 0 (OK)
  ├── 2. Виклик apparmor_file_open(file) ==> повертає -EACCES (Заборонено)
  └── 3. Переривання ланцюжка, системний виклик негайно повертає -EACCES
```

Якщо хоча б один модуль повертає ненульовий код помилки (наприклад, `-EACCES` або `-EPERM`), ядро негайно перериває виконання системного виклику і відмовляє у доступі.

---

### 2. Ключові хуки ядра LSM та їхнє призначення

| Сигнатура хука ядра | Підсистема ядра | Призначення перевірки |
|---|---|---|
| `security_bprm_creds_for_exec(bprm)` | `fs/exec.c` | Викликається під час `execve()`. Обчислює новий безпековий контекст процесу, перевіряє право на зміну домену (`type_transition`) та очищає небезпечні змінні оточення |
| `security_file_open(file)` | `fs/open.c` | Перевіряє право процесу на відкриття файлового дескриптора з прапорцями читання/запису (`O_RDONLY`, `O_WRONLY`, `O_RDWR`) |
| `security_inode_permission(inode, mask)` | `fs/namei.c` | Перевіряє право процесу на проходження каталогів файлової системи (`search`), створення нових файлів або видалення існуючих інод |
| `security_task_kill(task, info, sig, cred)` | `kernel/signal.c` | Перевіряє, чи має процес право надіслати сигнал `kill()` (наприклад, `SIGKILL`, `SIGTERM`, `SIGSTOP`) цільовому процесу |
| `security_socket_connect(sock, address, addrlen)` | `net/socket.c` | Перевіряє дозвіл на встановлення вихідного мережевого з'єднання за IP-адресою та TCP/UDP портом |
| `security_ipc_permission(ipcp, flag)` | `ipc/util.c` | Контролює доступ до черг повідомлень System V / POSIX, масивів семафорів та сегментів спільної пам'яті (`shm`) |

---

### 3. Протокол selinuxfs та бібліотека простору користувача libselinux

Усі запити простору користувача проходять через віртуальну файлову систему `selinuxfs` (зазвичай змонтовану за шляхом `/sys/fs/selinux`). Ядро надає прикладним програмам спеціальні псевдофайли для взаємодії з монітором безпеки:

- `/sys/fs/selinux/enforce` — читання або запис режиму блокування (`1` — Enforcing, `0` — Permissive);
- `/sys/fs/selinux/access` — бінарний інтерфейс обчислення прав доступу для довільної пари контекстів;
- `/sys/fs/selinux/create` — визначення контексту за замовчуванням при створенні нового об'єкта;
- `/sys/fs/selinux/load` — точка завантаження скомпільованого бінарного образу політики (`policy.33`);
- `/proc/thread-self/attr/current` — прямий доступ до мітки безпеки поточного потоку виконання;
- `/proc/thread-self/attr/fscreate` — налаштування мітки безпеки для створюваних файлів поточного потоку.

Бібліотека `libselinux` (заголовок `<selinux/selinux.h>`) інкапсулює низькорівневі операції з `selinuxfs` у зручний інтерфейс для системних служб (D-Bus, systemd, sshd, sudo, Podman, Nginx).

#### Категорії функцій libselinux

1. **Інспекція глобального стану:**
   - `is_selinux_enabled()` — повертає `1`, якщо SELinux увімкнено, або `0`, якщо модуль вимкнено;
   - `security_getenforce()` — зчитує поточний стан блокування (`1` — Enforcing, `0` — Permissive);
   - `security_setenforce(int mode)` — змінює поточний стан блокування без перезавантаження ОС.

2. **Керування мітками процесів:**
   - `getcon(char **con)` — виділяє динамічну пам'ять і повертає поточний контекст процесу;
   - `setcon(const char *con)` — змінює контекст поточного процесу на новий дозволений домен;
   - `getpidcon(pid_t pid, char **con)` — зчитує безпековий контекст довільного процесу за його числовим PID;
   - `setfscreatecon(const char *con)` — встановлює контекст за замовчуванням для всіх файлів, які створюватимуться цим потоком (корисно для демонів, які розпаковують архіви чи створюють сокети).

3. **Керування мітками файлової системи (xattr):**
   - `getfilecon(const char *path, char **con)` — зчитує мітку безпеки файлу з розширеного атрибута `security.selinux` (переходить за символічними посиланнями);
   - `lgetfilecon(const char *path, char **con)` — зчитує мітку самого символічного посилання без його розіменування;
   - `fgetfilecon(int fd, char **con)` — зчитує мітку безпеки за відкритим файловим дескриптором;
   - `setfilecon(const char *path, const char *con)` — записує новий контекст у розширений атрибут `security.selinux`;
   - `freecon(char *con)` — обов'язкова функція звільнення буфера, виділеного бібліотекою (використання стандартного `free()` заборонено, оскільки внутрішній алокатор бібліотеки може відрізнятися від стандартного).

4. **Програмний запит рішень доступу (Userspace AVC):**
   Служби, що керують власними об'єктами (наприклад, D-Bus повідомленнями або X11 вікнами), використовують функцію `security_compute_av(scon, tcon, tclass, requested, &avd)`. Структура `struct av_decision` повертає повну інформацію про вердикт:
   - `allowed` — бітова маска дозволених операцій для цього класу;
   - `auditallow` — бітова маска операцій, які необхідно логувати навіть у разі дозволу;
   - `auditdeny` — бітова маска операцій, які вимагають запису в аудит при блокуванні;
   - `seqno` — порядковий номер версії політики для інвалідації користувацьких кешів.

---

### 4. Робота з базою відповідностей шляхів (selabel API)

Під час встановлення пакетів чи розгортання образів утиліти (`rpm`, `dpkg`, `tar`) повинні автоматично встановлювати правильні розширені атрибути файлів. Для цього використовується підсистема `selabel`:

```
selabel_open(SELABEL_CTX_FILE, opts, nopts)
  │
  ├── Зчитування файлів /etc/selinux/targeted/contexts/files/file_contexts
  └── Компіляція регулярних виразів шляхів у пам'яті

selabel_lookup(handle, &con, path, mode)
  │
  └── Зіставлення шляху (наприклад, /var/www/html/index.html -> httpd_sys_content_t)
```

Це дозволяє утилітам призначати файлам правильні мітки безпеки ще до того, як відповідна служба почне до них звертатися.

---

### 5. Альтернативні користувацькі інтерфейси: AppArmor та SMACK

Для систем, що використовують інші модулі обов'язкового доступу, ядро Linux надає власні бібліотечні API:

1. **AppArmor (`libapparmor` / `<sys/apparmor.h>`):**
   - `aa_getcon(char **con, char **mode)` — повертає поточний активний профіль процесу та стан його застосування (enforce/complain);
   - `aa_change_profile(const char *profile)` — дозволяє процесу самостійно перейти у більш обмежений профіль (деескалація привілеїв);
   - `aa_change_hat(const char *subprofile, unsigned long magic_token)` — перехід у підпрофіль (Hat) для ізоляції окремих обробників складних демонів (наприклад, окремий Hat для виконання PHP-скриптів у вебсервері Apache) із можливістю безпечного повернення за секретним токеном.

2. **SMACK (`libsmack` та файлова система `smackfs`):**
   - Інтерфейс SMACK повністю побудований на прямих текстових операціях із каталогом `/sys/fs/smackfs/`:
   - `/sys/fs/smackfs/current` — зчитування або встановлення мітки поточного процесу;
   - `/sys/fs/smackfs/load2` — додавання нових рядкових правил доступу;
   - `/sys/fs/smackfs/access2` — перевірка прав між парою міток.
   - Бібліотека `libsmack` надає зручні функції-обгортки: `smack_have_access(subject, object, mode)` та `smack_set_label_for_file(path, label)`.

---

### 6. Приклади використання API мовами C та C++

Нижче наведено повноцінний інженерний приклад утиліти, яка перевіряє стан підсистеми SELinux, інспектує поточний контекст процесу з його декомпозицією на складові (user, role, type, range), зчитує мітку файлу системних паролів та перевіряє права доступу.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <selinux/selinux.h>
#include <selinux/context.h>

/* Отримання та детальний розбір безпекового контексту процесу */
static bool inspect_current_process(void) {
    char *raw_ctx = NULL;
    if (getcon(&raw_ctx) < 0 || !raw_ctx) {
        perror("Помилка виклику getcon()");
        return false;
    }

    printf("Поточний контекст процесу: %s\n", raw_ctx);

    /* Розбір рядка контексту через структуру context_t */
    context_t con = context_new(raw_ctx);
    if (con) {
        printf("  ├── Користувач: %s\n", context_user_get(con));
        printf("  ├── Роль:       %s\n", context_role_get(con));
        printf("  ├── Домен/Тип:  %s\n", context_type_get(con));
        printf("  └── Рівень MLS: %s\n", context_range_get(con) ? context_range_get(con) : "s0");
        context_free(con);
    }

    freecon(raw_ctx);
    return true;
}

/* Зчитування розширеного атрибута security.selinux для файлу */
static bool inspect_file_label(const char *filepath) {
    char *file_ctx = NULL;
    if (getfilecon(filepath, &file_ctx) < 0 || !file_ctx) {
        perror("Помилка виклику getfilecon()");
        return false;
    }

    printf("Мітка безпеки [%s]: %s\n", filepath, file_ctx);
    freecon(file_ctx);
    return true;
}

int main(void) {
    /* 1. Перевірка активності модуля SELinux у ядрі */
    if (!is_selinux_enabled()) {
        puts("Підсистема SELinux вимкнена або не підтримується ядром.");
        return 0;
    }

    /* 2. Визначення робочого режиму */
    const int enforce_mode = security_getenforce();
    printf("Режим роботи SELinux: %s (код: %d)\n",
           enforce_mode == 1 ? "Enforcing" : (enforce_mode == 0 ? "Permissive" : "Disabled"),
           enforce_mode);

    /* 3. Інспекція процесу */
    if (!inspect_current_process()) {
        return 1;
    }

    /* 4. Інспекція файлу */
    if (!inspect_file_label("/etc/shadow")) {
        return 1;
    }

    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <format>
#include <selinux/selinux.h>
#include <selinux/context.h>

/* RAII-обгортка для рядків, виділених бібліотекою libselinux */
struct ContextDeleter {
    void operator()(char* ptr) const noexcept {
        if (ptr) {
            freecon(ptr);
        }
    }
};
using UniqueContextString = std::unique_ptr<char, ContextDeleter>;

/* RAII-обгортка для дескриптора структури context_t */
struct ContextHandleDeleter {
    void operator()(context_s_t* ptr) const noexcept {
        if (ptr) {
            context_free(ptr);
        }
    }
};
using UniqueContextHandle = std::unique_ptr<context_s_t, ContextHandleDeleter>;

struct SecurityLabel {
    std::string full_string;
    std::string user;
    std::string role;
    std::string type;
    std::string mls_range;
};

class SELinuxAPI {
public:
    [[nodiscard]] static bool is_active() noexcept {
        return is_selinux_enabled() == 1;
    }

    [[nodiscard]] static std::string get_mode_name() noexcept {
        const int mode = security_getenforce();
        if (mode == 1) return "Enforcing (блокування порушень)";
        if (mode == 0) return "Permissive (лише аудит)";
        return "Disabled (повністю вимкнено)";
    }

    [[nodiscard]] static std::expected<SecurityLabel, std::string> get_process_label() {
        char* raw_con = nullptr;
        if (getcon(&raw_con) < 0 || !raw_con) {
            return std::unexpected("Не вдалося отримати контекст процесу через getcon()");
        }
        UniqueContextString raw_guard(raw_con);

        UniqueContextHandle handle(context_new(raw_guard.get()));
        if (!handle) {
            return std::unexpected("Помилка розбору структури контексту через context_new()");
        }

        const char* range_ptr = context_range_get(handle.get());

        return SecurityLabel{
            .full_string = raw_guard.get(),
            .user = context_user_get(handle.get()) ? context_user_get(handle.get()) : "",
            .role = context_role_get(handle.get()) ? context_role_get(handle.get()) : "",
            .type = context_type_get(handle.get()) ? context_type_get(handle.get()) : "",
            .mls_range = range_ptr ? range_ptr : "s0"
        };
    }

    [[nodiscard]] static std::expected<std::string, std::string> get_file_label(std::string_view path) {
        char* raw_con = nullptr;
        if (getfilecon(path.data(), &raw_con) < 0 || !raw_con) {
            return std::unexpected("Не вдалося зчитати xattr security.selinux для " + std::string(path));
        }
        UniqueContextString raw_guard(raw_con);
        return std::string(raw_guard.get());
    }
};

int main() {
    if (!SELinuxAPI::is_active()) {
        std::cout << "Підсистема SELinux не активна в поточній операційній системі.\n";
        return 0;
    }

    std::cout << "Режим SELinux: " << SELinuxAPI::get_mode_name() << "\n";

    if (auto proc = SELinuxAPI::get_process_label(); proc.has_value()) {
        std::cout << "Контекст поточного процесу: " << proc->full_string << "\n"
                  << "  ├── Користувач: " << proc->user << "\n"
                  << "  ├── Роль:       " << proc->role << "\n"
                  << "  ├── Домен/Тип:  " << proc->type << "\n"
                  << "  └── Рівень MLS: " << proc->mls_range << "\n";
    } else {
        std::cerr << proc.error() << "\n";
        return 1;
    }

    if (auto file = SELinuxAPI::get_file_label("/etc/shadow"); file.has_value()) {
        std::cout << "Мітка безпеки [/etc/shadow]: " << *file << "\n";
    } else {
        std::cerr << file.error() << "\n";
        return 1;
    }

    return 0;
}
```
:::
