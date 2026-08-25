# ⚙️ Реалізація мінімального ініціалізатора-збирача зомбі (Init Shim)

Цей проект демонструє реалізацію легковажного ініціалізатора для контейнерів (аналога `tini` та `dumb-init`), що вирішує фундаментальні проблеми процесу `PID 1`: автоматичне збирання осиротілих процесів-зомбі через `waitpid()` та надійну трансляцію системних сигналів дочірнім процесам.

---

### 1. Архітектурна постановка завдання

Коли контейнер запускає високорівневий застосунок (Node.js, Python, Java) безпосередньо як головний процес, цей процес отримує номер `PID 1` у просторі ідентифікаторів `pid_namespace`. У моделі процесів Unix це накладає на програму дві системні вимоги, для яких типові веб-сервіси не призначені:

1. **Очищення осиротілих нащадків (Zombie Reaping):** Будь-який процес у контейнері, чий батьківський процес завершився раніше за нього, автоматично перепідпорядковується процесу `PID 1`. Коли такий процес-сирота завершує роботу через `exit()`, ядро переводить його в стан `EXIT_ZOMBIE` і надсилає сигнал `SIGCHLD` процесу `PID 1`. Якщо `PID 1` не викликає `waitpid()`, запис `struct task_struct` назавжди залишається в таблиці ядра, що призводить до вичерпання ліміту процесів.
2. **Трансляція сигналів зупинки (Signal Forwarding):** Ядро Linux захищає `PID 1` від випадкового знищення: дія за замовчуванням `SIG_DFL` для сигналів `SIGTERM` та `SIGINT` просто ігнорується, якщо процес не зареєстрував явний обробник. Крім того, сигнал `SIGTERM`, надісланий демоном контейнеризації, доставляється виключно процесу `PID 1` і не транслюється його дочірнім процесам автоматично.

Ініціалізатор-обгортка (*Init Shim*) запускається як справжній `PID 1`, перехоплює всі системні сигнали через неблокуючий файловий дескриптор `signalfd`, породжує цільовий застосунок у новій групі процесів, своєчасно збирає всіх зомбі в циклі `waitpid(..., WNOHANG)` і коректно транслює код завершення застосунку назовні.

---

### 2. Структура ініціалізатора та послідовність системних викликів

Послідовність роботи ініціалізатора складається з п'яти послідовних кроків:

```
[ Ядро Linux ]           [ Init Shim (PID 1) ]             [ Цільовий застосунок (PID 2) ]
      │                            │                                      │
      │── 1. sigprocmask() ───────>│ (Блокування сигналів у потоці)       │
      │── 2. signalfd() ──────────>│ (Створення дескриптора сигналів)     │
      │── 3. fork() + execvp() ───>│─────────────────────────────────────>│
      │                            │                                      │
      │── 4. Сигнал SIGTERM ──────>│                                      │
      │                            │── kill(-PID_2, SIGTERM) ────────────>│
      │                            │                                      │ (Обробка та exit(0))
      │── 5. Сигнал SIGCHLD ──────>│                                      │
      │                            │── waitpid(-1, &status, WNOHANG) ────>│ (Видалення зомбі)
      │<── exit(child_status) ─────│
```

Кожен етап цієї послідовності забезпечує виконання суворого інваріанта:
* **Блокування сигналів:** функція `sigprocmask()` перешкоджає раптовій доставці асинхронних сигналів під час ініціалізації внутрішніх структур і передає керування файловому дескриптору `signalfd`.
* **Створення окремої групи процесів:** виклик `setpgid(0, 0)` у тілі дочірнього процесу після виклику `fork()` формує нову групу процесів. Це гарантує, що наступний виклик `kill(-child_pid, sig)` надішле сигнал усім нащадкам застосунку одночасно.
* **Неблокуюче очищення зомбі:** оскільки сигнал `SIGCHLD` не складається в чергу в ядрі Linux, один сигнал може свідчити про завершення одразу кількох процесів. Тому функція очищення викликається у циклі з прапорцем `WNOHANG`.

---

### 3. Програмна реалізація ініціалізатора

Нижче наведено повний вихідний код ініціалізатора мовами C та C++. Реалізація використовує системний виклик `signalfd` для синхронного читання сигналів через цикл опитування `poll()`, що повністю усуває стан гонитви (*race condition*), притаманний асинхронним обробникам сигналів `sigaction`.

:::tabs
@tab:c
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/signalfd.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <poll.h>
#include <errno.h>

static void reap_zombies(pid_t primary_child, int *primary_status, int *primary_exited) {
    pid_t pid;
    int status;

    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        if (pid == primary_child) {
            *primary_status = status;
            *primary_exited = 1;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    /* 1. Оголошення себе збирачем сиріт (subreaper) на випадок запуску не під PID 1 */
    if (prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) < 0) {
        perror("prctl(PR_SET_CHILD_SUBREAPER)");
    }

    /* 2. Блокування сигналів для перехоплення через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGQUIT);
    sigaddset(&mask, SIGHUP);
    sigaddset(&mask, SIGCHLD);

    if (sigprocmask(SIG_BLOCK, &mask, NULL) < 0) {
        perror("sigprocmask");
        return 1;
    }

    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd < 0) {
        perror("signalfd");
        return 1;
    }

    /* 3. Породження цільового процесу застосунку */
    pid_t child_pid = fork();
    if (child_pid < 0) {
        perror("fork");
        close(sfd);
        return 1;
    }

    if (child_pid == 0) {
        /* Дочірній процес: розблокування сигналів перед запуском */
        sigprocmask(SIG_UNBLOCK, &mask, NULL);
        close(sfd);

        /* Створення власної групи процесів для ізольованої доставки сигналів */
        setpgid(0, 0);

        execvp(argv[1], &argv[1]);
        perror("execvp");
        _exit(127);
    }

    /* 4. Головний цикл супервізора */
    struct pollfd pfd = { .fd = sfd, .events = POLLIN, .revents = 0 };
    int primary_exited = 0;
    int primary_status = 0;

    while (1) {
        int ret = poll(&pfd, 1, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            perror("poll");
            break;
        }

        if (pfd.revents & POLLIN) {
            struct signalfd_siginfo fdsi;
            ssize_t s = read(sfd, &fdsi, sizeof(fdsi));
            if (s != sizeof(fdsi)) continue;

            if (fdsi.ssi_signo == SIGCHLD) {
                reap_zombies(child_pid, &primary_status, &primary_exited);
                if (primary_exited) {
                    /* Головний процес завершився, дозбируємо залишкових сиріт */
                    reap_zombies(child_pid, &primary_status, &primary_exited);
                    break;
                }
            } else {
                /* Трансляція сигналів усій групі процесів дочірньої програми */
                kill(-child_pid, (int)fdsi.ssi_signo);
            }
        }
    }

    close(sfd);

    /* 5. Трансляція коду завершення */
    if (WIFEXITED(primary_status)) {
        return WEXITSTATUS(primary_status);
    } else if (WIFSIGNALED(primary_status)) {
        return 128 + WTERMSIG(primary_status);
    }

    return 1;
}
```
@tab:cpp
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <array>
#include <span>
#include <unistd.h>
#include <signal.h>
#include <sys/signalfd.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <poll.h>

class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_{fd} {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{other.release()} {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

struct ExecutionResult {
    bool exited{false};
    int raw_status{0};
};

static void reap_all_zombies(pid_t primary_pid, ExecutionResult& result) noexcept {
    pid_t pid = 0;
    int status = 0;

    while ((pid = ::waitpid(-1, &status, WNOHANG)) > 0) {
        if (pid == primary_pid) {
            result.raw_status = status;
            result.exited = true;
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <команда> [аргументи...]\n";
        return 1;
    }

    // 1. Оголошення себе subreaper
    ::prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0);

    // 2. Налаштування маски та signalfd
    sigset_t mask;
    ::sigemptyset(&mask);
    ::sigaddset(&mask, SIGTERM);
    ::sigaddset(&mask, SIGINT);
    ::sigaddset(&mask, SIGQUIT);
    ::sigaddset(&mask, SIGHUP);
    ::sigaddset(&mask, SIGCHLD);

    if (::sigprocmask(SIG_BLOCK, &mask, nullptr) < 0) {
        std::cerr << "Помилка блокування сигналів у sigprocmask\n";
        return 1;
    }

    UniqueFd sfd{::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC)};
    if (!sfd.valid()) {
        std::cerr << "Помилка створення signalfd\n";
        return 1;
    }

    // 3. Запуск дочірньої програми
    const pid_t child_pid = ::fork();
    if (child_pid < 0) {
        std::cerr << "Помилка системного виклику fork\n";
        return 1;
    }

    if (child_pid == 0) {
        ::sigprocmask(SIG_UNBLOCK, &mask, nullptr);
        sfd.reset();

        ::setpgid(0, 0);

        std::vector<char*> raw_args;
        raw_args.reserve(static_cast<size_t>(argc));
        for (int i = 1; i < argc; ++i) {
            raw_args.push_back(argv[i]);
        }
        raw_args.push_back(nullptr);

        ::execvp(raw_args[0], raw_args.data());
        std::_Exit(127);
    }

    // 4. Головний цикл моніторингу подій
    struct pollfd pfd{ .fd = sfd.get(), .events = POLLIN, .revents = 0 };
    ExecutionResult result{};

    while (!result.exited) {
        const int ret = ::poll(&pfd, 1, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }

        if (pfd.revents & POLLIN) {
            struct signalfd_siginfo fdsi{};
            const auto bytes = ::read(sfd.get(), &fdsi, sizeof(fdsi));
            if (bytes != sizeof(fdsi)) continue;

            if (fdsi.ssi_signo == SIGCHLD) {
                reap_all_zombies(child_pid, result);
            } else {
                // Доставка сигналу дочірній групі процесів
                ::kill(-child_pid, static_cast<int>(fdsi.ssi_signo));
            }
        }
    }

    // Дозбируємо залишкових сиріт після завершення головного процесу
    reap_all_zombies(child_pid, result);

    // 5. Трансляція статусу завершення
    if (WIFEXITED(result.raw_status)) {
        return WEXITSTATUS(result.raw_status);
    }
    if (WIFSIGNALED(result.raw_status)) {
        return 128 + WTERMSIG(result.raw_status);
    }

    return 1;
}
```
:::

---

### 4. Розбір системних пасток реалізації

При створенні та експлуатації подібних ініціалізаторів важливо враховувати тонкі аспекти функціонування ядра Linux, які безпосередньо впливають на надійність системи:

1. **Неблокуючий виклик `waitpid()` з прапорцем `WNOHANG`:**
   Класичний одинарний виклик `wait(&status)` є блокуючим. Якщо програма очікує лише одного конкретного завершення, а кілька інших сиріт ще працюють, супервізор заблокується і перестане обробляти вхідні сигнали зупинки. Використання циклу `while ((pid = waitpid(-1, &status, WNOHANG)) > 0)` забезпечує миттєве вичищення всіх померлих процесів без зависання головного циклу. Якщо черга порожня, `waitpid()` повертає `0`, і супервізор продовжує очікування подій у виклику `poll()`.

2. **Адресація групи процесів через негативний PID у виклику `kill()`:**
   У системі Unix виклик `kill(child_pid, sig)` надсилає сигнал суворо одному процесу з ідентифікатором `child_pid`. Якщо цільовий застосунок (наприклад, веб-сервер або скрипт-оркестратор) створив власні дочірні процеси у фоні, вони не дізнаються про надходження `SIGTERM`. Виклик `kill(-child_pid, sig)` використовує спеціальну семантику ядра: негативне значення ідентифікатора означає відправку сигналу всім процесам, чий ідентифікатор групи процесів (`PGID`) дорівнює абсолютному значенню `child_pid`. Завдяки виклику `setpgid(0, 0)` перед запуском `execvp`, дочірній процес стає лідером нової групи, і сигнал гарантовано доставляється всім його нащадкам.

3. **Прапорець `PR_SET_CHILD_SUBREAPER` та вкладені середовища:**
   Якщо ініціалізатор запускається не як глобальний `PID 1` (наприклад, усередині існуючого контейнера як підпроцес або під час тестування у звичайній системі), ядро за замовчуванням перепідпорядковує всіх сиріт системному init хоста (`systemd`). Системний виклик `prctl(PR_SET_CHILD_SUBREAPER, 1)` реєструє поточний процес як локального збирача сиріт. Будь-який процес у поточному піддереві, що втратив батька, всиновлюється саме цим супервізором, що запобігає витоку зомбі навіть у складних багаторівневих середовищах.

4. **Коректне розкодування статусу завершення:**
   Супервізор зобов'язаний прозоро транслювати результат роботи дочірнього процесу назовні. Якщо процес завершився штатно через виклик `exit(N)`, макрос `WIFEXITED(status)` повертає істину, а макрос `WEXITSTATUS(status)` витягує числовий код `N`. Якщо ж процес загинув від необробленого сигналу (наприклад, `SIGSEGV` або `SIGKILL`), макрос `WIFSIGNALED(status)` повертає істину, а макрос `WTERMSIG(status)` повертає номер сигналу. Відповідно до стандарту POSIX та конвенцій Unix, код завершення програми в такому разі формується як `128 + номер сигналу`.

---

### 5. Інструкція зі збірки та перевірки роботи

Для збірки та тестування ініціалізатора можна використовувати стандартний компілятор GCC або Clang:

```bash
# Збірка версії мовою C
gcc -O2 -Wall -Wextra -pedantic init_shim.c -o init_shim

# Збірка версії мовою C++
g++ -O2 -std=c++20 -Wall -Wextra -pedantic init_shim.cpp -o init_shim_cpp
```

Для перевірки ефективності збирання зомбі можна запустити фоновий скрипт, що навмисно створює сиріт за допомогою подвійного форку:

```bash
# Тестовий запуск під керуванням init_shim
./init_shim sh -c '
  (sleep 1 &)  # Створення фонового процесу-сироти
  echo "Головний скрипт працює..."
  sleep 3
'
```

Під час виконання цього тесту інспектор процесів `ps -eo pid,ppid,stat,comm` зафіксує, що фоновий процес `sleep` після завершення не зависає в стані `Z`, а негайно видаляється супервізором. Коли скрипт завершує роботу, контейнер виходить із кодом `0` без 10-секундної затримки.
