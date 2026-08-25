# ⚙️ Реалізація наглядача входу: PAM-діалог, зміна сесії та скидання привілеїв

Коли системний адміністратор або інженер створює власний наглядач терміналів, спеціалізований консольний кіоск або кастомний сервіс автентифікації, головне системне завдання полягає не просто в перевірці пароля, а в безпечній координації трьох незалежних підсистем операційної системи: бібліотеки PAM, системних викликів переходу привілеїв ядра Linux та керування сеансами термінала.

Нижче наведено повноцінну робочу реалізацію мінімального наглядача входу `mini-login`. Програма демонструє повний виробничий цикл входу в систему:
1. Ініціалізацію сесії PAM з кастомним обробником діалогу введення (*PAM conversation*);
2. Безпечний запит пароля у користувача з тимчасовим відключенням відлуння в терміналі через інтерфейс `termios`;
3. Проходження фази автентифікації (`auth`) та валідацію стану облікового запису (`account`);
4. Створення та відкриття сеансу облікових даних (`session`);
5. Виконання системних викликів скидання прав у строгому та незворотному порядку (`initgroups` → `setgid` → `setuid`);
6. Створення нового сеансу процесу (`setsid`) та передачу керування командній оболонці через `execve()`.

## Вихідний код наглядача входу

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/ioctl.h>
#include <security/pam_appl.h>

/* Функція діалогу PAM: читання пароля з термінала */
static int login_conv(int num_msg, const struct pam_message **msg,
                      struct pam_response **resp, void *appdata_ptr) {
    if (num_msg <= 0 || num_msg > PAM_MAX_NUM_MSG)
        return PAM_CONV_ERR;

    struct pam_response *reply = calloc(num_msg, sizeof(struct pam_response));
    if (!reply)
        return PAM_BUF_ERR;

    for (int i = 0; i < num_msg; ++i) {
        switch (msg[i]->msg_style) {
            case PAM_PROMPT_ECHO_OFF: {
                /* Вимикаємо відлуння символів для вводу пароля */
                struct termios old_t, new_t;
                tcgetattr(STDIN_FILENO, &old_t);
                new_t = old_t;
                new_t.c_lflag &= ~(ECHO | ECHOE | ECHOK | ECHONL);
                tcsetattr(STDIN_FILENO, TCSANOW, &new_t);

                printf("%s", msg[i]->msg);
                fflush(stdout);

                char buf[256];
                if (!fgets(buf, sizeof(buf), stdin)) {
                    tcsetattr(STDIN_FILENO, TCSANOW, &old_t);
                    free(reply);
                    return PAM_CONV_ERR;
                }
                tcsetattr(STDIN_FILENO, TCSANOW, &old_t);
                printf("\n");

                buf[strcspn(buf, "\r\n")] = '\0';
                reply[i].resp = strdup(buf);
                reply[i].resp_retcode = 0;
                break;
            }
            case PAM_PROMPT_ECHO_ON: {
                printf("%s", msg[i]->msg);
                fflush(stdout);
                char buf[256];
                if (!fgets(buf, sizeof(buf), stdin)) {
                    free(reply);
                    return PAM_CONV_ERR;
                }
                buf[strcspn(buf, "\r\n")] = '\0';
                reply[i].resp = strdup(buf);
                reply[i].resp_retcode = 0;
                break;
            }
            case PAM_ERROR_MSG:
                fprintf(stderr, "%s\n", msg[i]->msg);
                break;
            case PAM_TEXT_INFO:
                printf("%s\n", msg[i]->msg);
                break;
            default:
                free(reply);
                return PAM_CONV_ERR;
        }
    }
    *resp = reply;
    return PAM_SUCCESS;
}

int main(int argc, char *argv[]) {
    if (getuid() != 0) {
        fprintf(stderr, "Помилка: mini-login повинен запускатися з правами root (UID 0)\n");
        return EXIT_FAILURE;
    }

    char username[128];
    if (argc > 1) {
        strncpy(username, argv[1], sizeof(username) - 1);
        username[sizeof(username) - 1] = '\0';
    } else {
        printf("login: ");
        fflush(stdout);
        if (!fgets(username, sizeof(username), stdin))
            return EXIT_FAILURE;
        username[strcspn(username, "\r\n")] = '\0';
    }

    struct passwd *pw = getpwnam(username);
    if (!pw) {
        fprintf(stderr, "Невідомий користувач або запис відсутній у NSS\n");
        return EXIT_FAILURE;
    }

    pam_handle_t *pamh = NULL;
    struct pam_conv conv = { .conv = login_conv, .appdata_ptr = NULL };

    int rc = pam_start("login", username, &conv, &pamh);
    if (rc != PAM_SUCCESS) {
        fprintf(stderr, "pam_start збій: %s\n", pam_strerror(pamh, rc));
        return EXIT_FAILURE;
    }

    /* 1. Фаза auth: перевірка пароля */
    rc = pam_authenticate(pamh, 0);
    if (rc != PAM_SUCCESS) {
        fprintf(stderr, "Помилка автентифікації: %s\n", pam_strerror(pamh, rc));
        pam_end(pamh, rc);
        return EXIT_FAILURE;
    }

    /* 2. Фаза account: перевірка терміну дії та блокування */
    rc = pam_acct_mgmt(pamh, 0);
    if (rc != PAM_SUCCESS) {
        fprintf(stderr, "Помилка облікового запису: %s\n", pam_strerror(pamh, rc));
        pam_end(pamh, rc);
        return EXIT_FAILURE;
    }

    /* 3. Фаза session: підготовка облікових даних та сеансу */
    rc = pam_setcred(pamh, PAM_ESTABLISH_CRED);
    if (rc != PAM_SUCCESS) {
        pam_end(pamh, rc);
        return EXIT_FAILURE;
    }

    rc = pam_open_session(pamh, 0);
    if (rc != PAM_SUCCESS) {
        fprintf(stderr, "Збій відкриття сесії PAM: %s\n", pam_strerror(pamh, rc));
        pam_setcred(pamh, PAM_DELETE_CRED);
        pam_end(pamh, rc);
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        pam_close_session(pamh, 0);
        pam_end(pamh, PAM_ABORT);
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Дочірній процес: підготовка середовища та запуск Login Shell */
        if (setsid() < 0)
            perror("setsid");

        /* Критичний порядок скидання привілеїв: initgroups -> setgid -> setuid */
        if (initgroups(pw->pw_name, pw->pw_gid) < 0) {
            perror("initgroups");
            _exit(EXIT_FAILURE);
        }

        if (setgid(pw->pw_gid) < 0) {
            perror("setgid");
            _exit(EXIT_FAILURE);
        }

        if (setuid(pw->pw_uid) < 0) {
            perror("setuid");
            _exit(EXIT_FAILURE);
        }

        /* Налаштування робочого каталогу та змінних */
        if (chdir(pw->pw_dir) < 0) {
            fprintf(stderr, "Попередження: не вдалося перейти в $HOME, перехід у /\n");
            if (chdir("/") < 0) _exit(EXIT_FAILURE);
        }

        setenv("HOME", pw->pw_dir, 1);
        setenv("USER", pw->pw_name, 1);
        setenv("LOGNAME", pw->pw_name, 1);
        setenv("SHELL", pw->pw_shell, 1);

        /* Експорт змінних, створених модулями PAM (pam_env) */
        char **pam_env = pam_getenvlist(pamh);
        if (pam_env) {
            for (char **e = pam_env; *e != NULL; ++e) {
                putenv(*e);
            }
        }

        /* Запуск login shell з дефісом у нульовому аргументі */
        char *shell = pw->pw_shell[0] ? pw->pw_shell : "/bin/sh";
        char *argv0 = malloc(strlen(shell) + 2);
        sprintf(argv0, "-%s", strrchr(shell, '/') ? strrchr(shell, '/') + 1 : shell);

        char *args[] = { argv0, NULL };
        execve(shell, args, environ);

        perror("execve");
        _exit(EXIT_FAILURE);
    }

    /* Батьківський процес: очікування виходу користувача та закриття PAM */
    int status;
    waitpid(pid, &status, 0);

    pam_close_session(pamh, 0);
    pam_setcred(pamh, PAM_DELETE_CRED);
    pam_end(pamh, PAM_SUCCESS);

    return EXIT_SUCCESS;
}
```
```cpp
#define _GNU_SOURCE
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <security/pam_appl.h>

extern char **environ;

// RAII обгортка для тимчасового вимкнення відлуння в терміналі
class TerminalEchoGuard {
public:
    TerminalEchoGuard() {
        tcgetattr(STDIN_FILENO, &old_termios_);
        termios new_termios = old_termios_;
        new_termios.c_lflag &= ~(ECHO | ECHOE | ECHOK | ECHONL);
        tcsetattr(STDIN_FILENO, TCSANOW, &new_termios);
    }

    ~TerminalEchoGuard() {
        tcsetattr(STDIN_FILENO, TCSANOW, &old_termios_);
    }

    TerminalEchoGuard(const TerminalEchoGuard&) = delete;
    TerminalEchoGuard& operator=(const TerminalEchoGuard&) = delete;

private:
    termios old_termios_{};
};

// RAII делегатор для автоматичного закриття дескриптора PAM
struct PamDeleter {
    void operator()(pam_handle_t *pamh) const noexcept {
        if (pamh) {
            pam_end(pamh, PAM_SUCCESS);
        }
    }
};

using PamHandlePtr = std::unique_ptr<pam_handle_t, PamDeleter>;

// Функція діалогу PAM мовою C++
static int login_conv_cpp(int num_msg, const struct pam_message **msg,
                          struct pam_response **resp, void * /*appdata_ptr*/) {
    if (num_msg <= 0 || num_msg > PAM_MAX_NUM_MSG) {
        return PAM_CONV_ERR;
    }

    auto *reply = static_cast<pam_response *>(std::calloc(num_msg, sizeof(pam_response)));
    if (!reply) {
        return PAM_BUF_ERR;
    }

    for (int i = 0; i < num_msg; ++i) {
        switch (msg[i]->msg_style) {
            case PAM_PROMPT_ECHO_OFF: {
                std::cout << msg[i]->msg << std::flush;
                std::string input;
                {
                    TerminalEchoGuard guard;
                    std::getline(std::cin, input);
                }
                std::cout << std::endl;
                reply[i].resp = strdup(input.c_str());
                reply[i].resp_retcode = 0;
                break;
            }
            case PAM_PROMPT_ECHO_ON: {
                std::cout << msg[i]->msg << std::flush;
                std::string input;
                std::getline(std::cin, input);
                reply[i].resp = strdup(input.c_str());
                reply[i].resp_retcode = 0;
                break;
            }
            case PAM_ERROR_MSG:
                std::cerr << msg[i]->msg << '\n';
                break;
            case PAM_TEXT_INFO:
                std::cout << msg[i]->msg << '\n';
                break;
            default:
                std::free(reply);
                return PAM_CONV_ERR;
        }
    }
    *resp = reply;
    return PAM_SUCCESS;
}

int main(int argc, char *argv[]) {
    if (getuid() != 0) {
        std::cerr << "Помилка: програма вимагає прав root (UID 0)\n";
        return EXIT_FAILURE;
    }

    std::string username;
    if (argc > 1) {
        username = argv[1];
    } else {
        std::cout << "login: " << std::flush;
        if (!std::getline(std::cin, username) || username.empty()) {
            return EXIT_FAILURE;
        }
    }

    struct passwd *pw = getpwnam(username.c_str());
    if (!pw) {
        std::cerr << "Користувача не знайдено в базі passwd\n";
        return EXIT_FAILURE;
    }

    pam_conv conv = { login_conv_cpp, nullptr };
    pam_handle_t *raw_pamh = nullptr;

    int rc = pam_start("login", username.c_str(), &conv, &raw_pamh);
    if (rc != PAM_SUCCESS) {
        std::cerr << "Збій pam_start: " << pam_strerror(raw_pamh, rc) << '\n';
        return EXIT_FAILURE;
    }
    PamHandlePtr pamh(raw_pamh);

    rc = pam_authenticate(pamh.get(), 0);
    if (rc != PAM_SUCCESS) {
        std::cerr << "Помилка автентифікації: " << pam_strerror(pamh.get(), rc) << '\n';
        return EXIT_FAILURE;
    }

    rc = pam_acct_mgmt(pamh.get(), 0);
    if (rc != PAM_SUCCESS) {
        std::cerr << "Помилка валідації облікового запису: " << pam_strerror(pamh.get(), rc) << '\n';
        return EXIT_FAILURE;
    }

    if (pam_setcred(pamh.get(), PAM_ESTABLISH_CRED) != PAM_SUCCESS) {
        return EXIT_FAILURE;
    }

    if (pam_open_session(pamh.get(), 0) != PAM_SUCCESS) {
        std::cerr << "Збій відкриття сесії PAM\n";
        pam_setcred(pamh.get(), PAM_DELETE_CRED);
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        std::perror("fork");
        pam_close_session(pamh.get(), 0);
        pam_setcred(pamh.get(), PAM_DELETE_CRED);
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        // Дочірній процес: створення сесії та скидання прав
        setsid();

        if (initgroups(pw->pw_name, pw->pw_gid) < 0) {
            std::perror("initgroups");
            _exit(EXIT_FAILURE);
        }
        if (setgid(pw->pw_gid) < 0) {
            std::perror("setgid");
            _exit(EXIT_FAILURE);
        }
        if (setuid(pw->pw_uid) < 0) {
            std::perror("setuid");
            _exit(EXIT_FAILURE);
        }

        if (chdir(pw->pw_dir) < 0) {
            std::cerr << "Попередження: chdir $HOME зазнав невдачі, перехід у /\n";
            if (chdir("/") < 0) _exit(EXIT_FAILURE);
        }

        setenv("HOME", pw->pw_dir, 1);
        setenv("USER", pw->pw_name, 1);
        setenv("LOGNAME", pw->pw_name, 1);
        setenv("SHELL", pw->pw_shell, 1);

        char **pam_env = pam_getenvlist(pamh.get());
        if (pam_env) {
            for (char **e = pam_env; *e != nullptr; ++e) {
                putenv(*e);
            }
        }

        std::string shell_path = (pw->pw_shell && pw->pw_shell[0]) ? pw->pw_shell : "/bin/sh";
        std::string shell_name = shell_path.substr(shell_path.find_last_of('/') + 1);
        std::string argv0 = "-" + shell_name;

        std::vector<char *> args = { argv0.data(), nullptr };
        execve(shell_path.c_str(), args.data(), environ);

        std::perror("execve");
        _exit(EXIT_FAILURE);
    }

    int status = 0;
    waitpid(pid, &status, 0);

    pam_close_session(pamh.get(), 0);
    pam_setcred(pamh.get(), PAM_DELETE_CRED);

    return EXIT_SUCCESS;
}
```
:::

## Покроковий розбір коду та підводні камені реалізації

Розробка системного супервізора входу вимагає бездоганного розуміння моделей пам'яті, сигналів та переходу привілеїв у ядрі. Помилка в одній строчці може призвести або до критичної діри в безпеці (надання непривілейованому користувачу прав root), або до зависання сеансів та витоку ресурсів.

### 1. Механіка функції зворотного зв'язку (PAM Conversation)

Бібліотека PAM повністю відокремлена від інтерфейсу користувача: вона не знає, де виконується програма — у віконному менеджері GTK/Qt, у текстовому терміналі чи у мережевому демоні. Тому передача запитань користувачеві реалізується через функцію зворотного виклику `pam_conv`.

Коли модуль `pam_unix.so` потребує пароль, він формує масив повідомлень `struct pam_message`:
* `PAM_PROMPT_ECHO_OFF`: Запит пароля або PIN-коду. Програма зобов'язана вимкнути зворотне відображення символів у терміналі за допомогою `tcsetattr()`, щоб текст не відображався на екрані.
* `PAM_PROMPT_ECHO_ON`: Запит відкритого тексту (наприклад логіна користувача або підтвердження `yes/no`).
* `PAM_ERROR_MSG`: Інформація про критичну помилку (наприклад `Account locked` або `Authentication failure`). Повинна виводитися у потік `stderr`.
* `PAM_TEXT_INFO`: Інформаційне повідомлення (наприклад привітання, статус останнього входу або банер дня).

Функція діалогу виділяє пам'ять під масив відповідей `struct pam_response` за допомогою `calloc()`, а самі рядки копіює через `strdup()`. За специфікацією Linux-PAM, бібліотека бере на себе обов'язок викликати `free()` для кожного елемента `resp` після завершення перевірки. Проте якщо всередині діалогу сталася помилка (користувач натиснув Ctrl+D або перервався потік stdin), наш обробник зобов'язаний самостійно звільнити пам'ять перед виходом з кодом `PAM_CONV_ERR`.

У версії мовою C++ для керування режимами термінала застосовано шаблон RAII через клас `TerminalEchoGuard`. Його конструктор зчитує поточні прапорці `termios` та знімає біти `ECHO`, а деструктор автоматично відновлює вихідний стан термінала навіть у разі генерації винятку.

### 2. Строгий порядок системних викликів скидання привілеїв

Ядро Linux зберігає для кожного процесу три пари ідентифікаторів у внутрішній структурі `struct cred`:
* `Real UID/GID`: Числовий ідентифікатор реального власника процесу;
* `Effective UID/GID`: Ідентифікатор, який ядро використовує для перевірки доступу до файлів VFS та системних ресурсів;
* `Saved Set-UID/GID`: Збережений ідентифікатор для тимчасового перемикання привілеїв.

Коли процес працює з `UID = 0`, він володіє повним набором привілеїв ядра, зокрема можливостями `CAP_SETUID` та `CAP_SETGID`.

Послідовність викликів у дочірньому процесі має залізне правило черговості:
1. `initgroups(pw->pw_name, pw->pw_gid)`: Зчитує всі додаткові групи користувача з `/etc/group` через шар NSS і викликає системний виклик `setgroups()`. Якщо викликати цей крок пізніше або пропустити його, процес або збереже системні групи superuser (`root`, `wheel`), або втратить доступ до групових файлів.
2. `setgid(pw->pw_gid)`: Оскільки процес ще має `EUID == 0`, ядро записує `pw_gid` одночасно у `Real GID`, `Effective GID` та `Saved GID`.
3. `setuid(pw->pw_uid)`: Остаточне скидання UID. Ядро встановлює `RUID = EUID = SUID = pw_uid` і повністю анулює всі біти Capabilities процесу.

> ⚠ **Чому порушення порядку фатальне.**
> Якщо викликати `setuid(pw_uid)` перед `initgroups()` чи `setgid()`, процес миттєво стає непривілейованим. У ту саму мить ядро анулює `CAP_SETGID`. Наступні виклики `setgid()` або `initgroups()` зазнають невдачі з помилкою `EPERM`. Якщо програма не перевірить помилку, користувач отримає шелл із чужими групами!

### 3. Навіщо батьківський процес залишається живим

Поширена помилка початківців — виконати `execve()` безпосередньо в головному процесі після виклику `pam_open_session()`. Це категорично неприпустимо з точки зору архітектури PAM.

Батьківський процес зобов'язаний залишатися наглядачем (*supervisor*):
1. Він очікує завершення дочірнього процесу через системний виклик `waitpid()`.
2. Після виходу користувача батько викликає `pam_close_session(pamh, 0)` та `pam_setcred(pamh, PAM_DELETE_CRED)`.
3. Саме виклик `pam_close_session()` запускає модулі завершення: `pam_systemd.so` повідомляє `systemd-logind` про закриття сеансу (що призводить до знищення скоупу cgroup та звільнення ресурсів), `pam_lastlog.so` записує час завершення у `/var/log/wtmp`, а модулі шифрування (наприклад `pam_mount` або `pam_ecryptfs`) безпечно демонтують домашній каталог користувача.

### 4. Очищення та передача змінних середовища

Модулі PAM (зокрема `pam_env.so` та `pam_systemd.so`) генерують важливі змінні сеансу (`XDG_RUNTIME_DIR`, `XDG_SESSION_ID`, `PATH`). Наглядач входу отримує цей список за допомогою функції `pam_getenvlist(pamh)` і переносить їх у глобальний масив `environ` через `putenv()`. Одночасно програма встановлює базові змінні `HOME`, `USER`, `LOGNAME` та `SHELL` відповідно до запису в `/etc/passwd`.

### 5. Ознака Login Shell та аргумент $0

Коли командна оболонка (наприклад Bash або Zsh) стартує, вона перевіряє свій нульовий аргумент командного рядка `argv[0]`.
* Якщо `argv[0] == "bash"`, оболонка вважає себе звичайним дочірнім процесом (наприклад запущеним із вікна графічного термінала) і читає лише файл `~/.bashrc`.
* Якщо ж перший символ `argv[0]` є дефісом (`argv[0] == "-bash"`), оболонка переходить у режим **Login Shell**. Лише в цьому режимі Bash виконує повний ланцюг ініціалізації: зчитує системний конфігуратор `/etc/profile`, імпортує скрипти `/etc/profile.d/*.sh` та виконує особистий профіль `~/.bash_profile`.
