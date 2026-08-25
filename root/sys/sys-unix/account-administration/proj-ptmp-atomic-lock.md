# ⚙️ Реалізація атомарного блокування баз облікових записів (/etc/ptmp)

Файли `/etc/passwd`, `/etc/shadow`, `/etc/group` та `/etc/gshadow` не мають вбудованої транзакційної підтримки на рівні реляційних СКБД. Це звичайні плоскі текстові файли, які тисячі процесів у системі одночасно відкривають на читання через системні бібліотечні виклики `getpwnam()`, `getpwuid()` або підсистему NSS. Пряма спроба змінити такий файл стандартним відкриттям на запис (з прапорцем `O_TRUNC` або `O_WRONLY`) створює фатальний стан гонки (race condition): будь-який паралельний процес, що виконує читання бази в момент запису, побачить обірваний рядок або нульову довжину файлу і помилково вирішить, що запитаного користувача чи системного демона не існує.

Щоб унеможливити конкурентні конфлікти між різними адміністративними утилітами (`useradd`, `usermod`, `vipw`, `chage`) та забезпечити сувору атомарність модифікацій для всіх паралельних читачів, у системному пакеті `shadow-utils` застосовується класичний протокол блокувального файлу з подальшим атомарним заміщенням через системний виклик `rename()`.

## Архітектурні виклики та обмеження стандартних блокувань

Перше інженерне питання, яке виникає під час проектування системних баз: чому не можна використати звичайні консультативні (advisory) або обов'язкові (mandatory) блокування файлів через `flock()` чи `fcntl(F_SETLK)`?

Причини дві:
1. **Продуктивність читачів:** Читання облікових записів відбувається постійно при кожному системному виклику перевірки прав, виведенні списку файлів у `ls -l` або автентифікації мережевого пакета. Якщо кожне читання `/etc/passwd` вимагатиме захоплення спільного замка `flock(LOCK_SH)`, це створить колосальну точку блокування (lock contention) у багатопотокових високонавантажених серверах. Тому читачі ніколи не ставлять замків і читають файл безпосередньо.
2. **Неможливість атомарної заміни під відкритим дескриптором:** Навіть якщо процес модифікації захопить ексклюзивний замок `flock(LOCK_EX)` на дескрипторі `/etc/passwd`, сам процес запису нових рядків не є миттєвим. Поки утиліта записує нові байти у файл, будь-який сторонній читач, який не використовує `flock`, прочитає частково оновлений файл.

Єдиним надійним вирішенням є підготовка повного нового стану бази в окремому ізольованому файлі з наступною підміною inode за один крок ядра.

## Протокол блокування та атомарної підміни

Алгоритм, реалізований у бібліотеках `shadow-utils` (функції `pw_lock`, `pw_unlock`, `spw_lock`, `spw_unlock`), складається з кількох послідовних кроків:

1. **Ексклюзивне створення замка:** Процес намагається створити тимчасовий файл `/etc/ptmp` (для shadow — `/etc/sptmp`, для group — `/etc/gtmp`) за допомогою системного виклику `open()` із комбінацією прапорців `O_CREAT | O_EXCL | O_RDWR` та правами доступу `0600`. Прапорець `O_EXCL` гарантує на рівні VFS ядра Linux, що файл буде створено лише за умови, що його ще не існувало. Якщо файл уже є на диску, ядро негайно повертає помилку `EEXIST`.
2. **Ідентифікація та виявлення застарілих замків (Stale Locks):** Одразу після створення файлу процес записує у нього свій числовий ідентифікатор процесу (PID) у текстовому вигляді. Якщо інша утиліта натрапляє на наявний файл `/etc/ptmp`, вона може зчитати цей PID і перевірити його життєздатність за допомогою системного виклику `kill(pid, 0)`. Якщо виклик повертає помилку `ESRCH`, процес-власник замка вже завершився аварійно, не встигнувши видалити файл. Якщо час створення файлу перевищує встановлений таймаут (зазвичай 15–30 секунд), утиліта попереджає адміністратора про наявність застарілого замка.
3. **Реєстрація асинхронних обробників сигналів:** Процес модифікації реєструє власні обробники сигналів `SIGINT`, `SIGHUP`, `SIGTERM` та `SIGQUIT`. Якщо адміністратор випадково натисне `Ctrl+C` під час виконання операції, обробник перехопить сигнал, видалить файл блокування `/etc/ptmp` і лише після цього завершить процес через `_exit(1)`. Без перехоплення сигналів будь-яке раптове завершення залишало б замок на диску, блокуючи всі наступні виклики `useradd`.
4. **Трансляція та модифікація даних:** Утиліта відкриває оригінальний `/etc/passwd` на читання, копіює його вміст у створений дескриптор `/etc/ptmp`, виконуючи необхідні зміни (додавання, модифікацію чи видалення рядка) у потоці даних.
5. **Примусове скидання дискових кешів (`fsync`):** Перед виконанням підміни утиліта обов'язково викликає системний виклик `fsync()` для дескриптора `/etc/ptmp`. Це критично важливо для збереження цілісності файлової системи в разі раптового зникнення живлення. Якщо не виконати `fsync()`, метадані каталогу можуть оновитися раніше, ніж байти даних запишуться з кешу сторінок ядра на фізичний диск, що призведе до порожнього файлу `/etc/passwd` після перезавантаження.
6. **Атомарне перейменування (`rename`):** Викликається системний виклик `rename("/etc/ptmp", "/etc/passwd")`. На рівні стандарту POSIX операція `rename()` у межах однієї файлової системи гарантує сувору атомарність: старий зв'язок dentry із старим inode розривається, і каталог починає вказувати на новий inode миттєво. Будь-який процес, що викликає `open("/etc/passwd")`, відкриє або повністю стару, або повністю нову версію файлу, без проміжних станів.
7. **Звільнення ресурсів:** Прапорець блокування знімається, а дескриптори закриваються.

## Практична реалізація: C та сучасний C++

Нижче наведено робочий приклад утиліти оновлення реєстраційної оболонки користувача, що реалізує протокол блокування `ptmp`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
#include <sys/stat.h>
#include <sys/types.h>

static const char *PASSWD_FILE = "/etc/passwd";
static const char *LOCK_FILE   = "/etc/ptmp";
static volatile sig_atomic_t g_locked = 0;

static void cleanup_lock(void) {
    if (g_locked) {
        unlink(LOCK_FILE);
        g_locked = 0;
    }
}

static void sig_handler(int sig) {
    (void)sig;
    cleanup_lock();
    _exit(1);
}

static void setup_signals(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = sig_handler;
    sigemptyset(&sa.sa_mask);

    sigaction(SIGINT,  &sa, NULL);
    sigaction(SIGHUP,  &sa, NULL);
    sigaction(SIGQUIT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
}

int acquire_passwd_lock(void) {
    setup_signals();

    int fd = open(LOCK_FILE, O_CREAT | O_EXCL | O_RDWR, 0600);
    if (fd < 0) {
        if (errno == EEXIST) {
            fprintf(stderr, "Помилка: файл блокування %s вже існує.\n", LOCK_FILE);
        } else {
            perror("open(LOCK_FILE)");
        }
        return -1;
    }

    g_locked = 1;
    atexit(cleanup_lock);

    char pid_str[32];
    int len = snprintf(pid_str, sizeof(pid_str), "%d\n", (int)getpid());
    if (write(fd, pid_str, (size_t)len) != len) {
        perror("write(pid)");
        close(fd);
        cleanup_lock();
        return -1;
    }

    return fd;
}

int update_user_shell(const char *target_user, const char *new_shell) {
    int lock_fd = acquire_passwd_lock();
    if (lock_fd < 0) {
        return -1;
    }

    FILE *in = fopen(PASSWD_FILE, "r");
    if (!in) {
        perror("fopen(PASSWD_FILE)");
        close(lock_fd);
        cleanup_lock();
        return -1;
    }

    FILE *out = fdopen(lock_fd, "w");
    if (!out) {
        perror("fdopen(lock_fd)");
        fclose(in);
        close(lock_fd);
        cleanup_lock();
        return -1;
    }

    char line[1024];
    int user_found = 0;
    size_t target_len = strlen(target_user);

    while (fgets(line, sizeof(line), in)) {
        if (strncmp(line, target_user, target_len) == 0 && line[target_len] == ':') {
            user_found = 1;
            char *tokens[7];
            char *saveptr;
            char *tok = strtok_r(line, ":\n", &saveptr);
            int idx = 0;
            while (tok && idx < 7) {
                tokens[idx++] = tok;
                tok = strtok_r(NULL, ":\n", &saveptr);
            }
            if (idx >= 6) {
                fprintf(out, "%s:%s:%s:%s:%s:%s:%s\n",
                        tokens[0], tokens[1], tokens[2],
                        tokens[3], tokens[4], tokens[5],
                        new_shell);
                continue;
            }
        }
        fputs(line, out);
    }

    fclose(in);

    if (!user_found) {
        fprintf(stderr, "Користувача «%s» не знайдено.\n", target_user);
        fclose(out);
        cleanup_lock();
        return -1;
    }

    if (fflush(out) != 0 || fsync(fileno(out)) != 0) {
        perror("fsync(out)");
        fclose(out);
        cleanup_lock();
        return -1;
    }
    fclose(out);

    if (rename(LOCK_FILE, PASSWD_FILE) != 0) {
        perror("rename(LOCK_FILE, PASSWD_FILE)");
        cleanup_lock();
        return -1;
    }

    g_locked = 0;
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <system_error>
#include <csignal>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

class PasswdDatabaseLock {
public:
    static constexpr std::string_view kPasswdPath = "/etc/passwd";
    static constexpr std::string_view kLockPath   = "/etc/ptmp";

    static std::expected<PasswdDatabaseLock, std::error_code> acquire() {
        setup_signal_handlers();

        int fd = ::open(kLockPath.data(), O_CREAT | O_EXCL | O_RDWR, 0600);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        s_active_lock = true;

        std::string pid_str = std::to_string(::getpid()) + "\n";
        if (::write(fd, pid_str.data(), pid_str.size()) != static_cast<ssize_t>(pid_str.size())) {
            ::close(fd);
            ::unlink(kLockPath.data());
            s_active_lock = false;
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return PasswdDatabaseLock(fd);
    }

    ~PasswdDatabaseLock() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        if (m_locked) {
            ::unlink(kLockPath.data());
            s_active_lock = false;
        }
    }

    PasswdDatabaseLock(const PasswdDatabaseLock&) = delete;
    PasswdDatabaseLock& operator=(const PasswdDatabaseLock&) = delete;

    PasswdDatabaseLock(PasswdDatabaseLock&& other) noexcept
        : m_fd(other.m_fd), m_locked(other.m_locked) {
        other.m_fd = -1;
        other.m_locked = false;
    }

    PasswdDatabaseLock& operator=(PasswdDatabaseLock&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            if (m_locked) ::unlink(kLockPath.data());

            m_fd = other.m_fd;
            m_locked = other.m_locked;
            other.m_fd = -1;
            other.m_locked = false;
        }
        return *this;
    }

    int file_descriptor() const noexcept { return m_fd; }

    std::expected<void, std::error_code> commit() {
        if (::fsync(m_fd) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ::close(m_fd);
        m_fd = -1;

        if (::rename(kLockPath.data(), kPasswdPath.data()) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        m_locked = false;
        s_active_lock = false;
        return {};
    }

private:
    explicit PasswdDatabaseLock(int fd) : m_fd(fd), m_locked(true) {}

    int m_fd = -1;
    bool m_locked = false;
    static inline volatile sig_atomic_t s_active_lock = false;

    static void signal_handler(int) {
        if (s_active_lock) {
            ::unlink(kLockPath.data());
            s_active_lock = false;
        }
        ::_exit(1);
    }

    static void setup_signal_handlers() {
        struct sigaction sa{};
        sa.sa_handler = signal_handler;
        ::sigemptyset(&sa.sa_mask);

        ::sigaction(SIGINT,  &sa, nullptr);
        ::sigaction(SIGHUP,  &sa, nullptr);
        ::sigaction(SIGQUIT, &sa, nullptr);
        ::sigaction(SIGTERM, &sa, nullptr);
    }
};

std::expected<void, std::string> update_user_shell_cpp(std::string_view target_user, std::string_view new_shell) {
    auto lock_res = PasswdDatabaseLock::acquire();
    if (!lock_res) {
        return std::unexpected("Не вдалося захопити блокування: " + lock_res.error().message());
    }
    auto lock = std::move(*lock_res);

    std::ifstream in(PasswdDatabaseLock::kPasswdPath.data());
    if (!in.is_open()) {
        return std::unexpected("Не вдалося відкрити " + std::string(PasswdDatabaseLock::kPasswdPath));
    }

    std::ofstream out(PasswdDatabaseLock::kLockPath.data(), std::ios::app);
    if (!out.is_open()) {
        return std::unexpected("Не вдалося відкрити файл блокування для запису");
    }

    std::string line;
    bool user_found = false;
    std::string prefix = std::string(target_user) + ":";

    while (std::getline(in, line)) {
        if (line.starts_with(prefix)) {
            user_found = true;
            std::vector<std::string> parts;
            std::stringstream ss(line);
            std::string item;
            while (std::getline(ss, item, ':')) {
                parts.push_back(item);
            }
            if (parts.size() >= 7) {
                parts[6] = std::string(new_shell);
                for (size_t i = 0; i < parts.size(); ++i) {
                    out << parts[i] << (i + 1 == parts.size() ? "" : ":");
                }
                out << "\n";
                continue;
            }
        }
        out << line << "\n";
    }

    in.close();
    out.flush();

    if (!user_found) {
        return std::unexpected("Користувача «" + std::string(target_user) + "» не знайдено");
    }

    auto commit_res = lock.commit();
    if (!commit_res) {
        return std::unexpected("Помилка атомарної заміни бази: " + commit_res.error().message());
    }

    return {};
}
```
:::

## Інженерні застереження та крайові випадки

1. **Вимога єдиної точки монтування:** Системний виклик `rename()` гарантує атомарність лише за умови, що файл джерела та файл призначення розташовані на одній і тій самій файловій системі (мають однаковий `dev_t`). Якщо спробувати створити файл блокування у `/tmp` (який часто змонтовано на окремому `tmpfs`), а потім виконати `rename("/tmp/ptmp", "/etc/passwd")`, ядро завершить виклик помилкою `EXDEV` (Invalid cross-device link). Заміна між різними файловими системами вимагає копіювання байтів, що руйнує атомарність. Саме тому файл `/etc/ptmp` обов'язково розміщується безпосередньо в каталозі `/etc`.
2. **Права доступу на файл блокування:** Файл `/etc/ptmp` створюється з правами `0600` (або `0640` для `sptmp`). Це запобігає можливості читання проміжного вмісту бази іншими користувачами системи під час формування файлу.
3. **Небезпека прямих редагувань через звичайні редактори:** Використання програм `nano /etc/passwd` або `vim /etc/passwd` у виробничих середовищах суворо заборонено. Такі редактори не знають про файл `/etc/ptmp`, не синхронізуються з утилітами `useradd`/`usermod` і можуть перезаписати файл під час паралельної роботи іншого адміністратора. Для ручного редагування слід застосовувати виключно утиліти `vipw` та `vigr`, які створюють блокування `/etc/ptmp` перед викликом призначеного системного редактора.
