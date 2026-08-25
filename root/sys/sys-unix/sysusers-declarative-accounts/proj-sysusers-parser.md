# ⚙️ Практична реалізація парсера та атомарного оновлення баз даних користувачів

Ця вставка демонструє практичну реалізацію утиліти злиття та оновлення бази даних користувачів `/etc/passwd` мовами C та C++. Вона висвітлює внутрішній механізм роботи `systemd-sysusers`: файлове блокування `lckpwdf()`, аналіз наявних UID, пошук вільних ідентифікаторів у системному діапазоні та атомарну заміну файлів через тимчасові буфери з `fsync()`.

## Архітектурний підхід: Атомарне оновлення бази даних

Модифікація системних файлів користувачів `/etc/passwd` та `/etc/group` вимагає суворого дотримання трьох фундаментальних вимог системної безпеки та надійності:

1. **Глобальне файлове блокування через POSIX API.** Перед зчитуванням та модифікацією система повинна отримати ексклюзивне блокування `lckpwdf()`. Це системний виклик POSIX, який створює унікальний файл блокування `/etc/.pwd.lock`. Якщо інша утиліта (наприклад, `useradd` або паралельний екземпляр `systemd-sysusers`) одночасно намагається змінити системні бази даних, вона блокується на цьому виклику або повертає помилку `EAGAIN`. Це унеможливлює стан гонки (race condition) та пошкодження списків користувачів.
2. **Атомарний запис через тимчасові файли у тій самій файловій системі.** Заборонено модифікувати файл `/etc/passwd` безпосередньо у режимі перезапису. Якщо під час операції станеться збій живлення або критичне завершення процесу, файл буде обрізано до нуля, що унеможливить завантаження ОС. Новий стан формується у тимчасовому файлі `/etc/passwd.tmp`. Оскільки обидва файли перебувають у межах однієї файлової системи (тобто на тому самому монтованому блоковому пристрої), заміна файлів виконується через системний виклик `rename()`, який лише змінює покажчик в іноді файлової системи POSIX.
3. **Гарантія фізичної персистентності на диску (fsync).** Перш ніж викликати `rename()`, необхідно примусово виштовхнути брудні сторінки (dirty pages) з кешу сторінок ядра (Page Cache) на фізичний накопичувач (NVMe/SSD/HDD). Для цього використовується виклик `fsync()`. Без виклику `fsync()` операційна система може виконати атомарну заміну імені файлу у метаданих файлової системи раніше, ніж самі дані користувачів будуть записані на диск, що у разі збою живлення призведе до появи порожнього файлу `/etc/passwd`.
4. **Гарантоване прибирання та зняття блокувань.** У разі виникнення будь-якої помилки під час форматування, неможливості виділити UID або відмови запису на диск, утиліта зобов'язана негайно вилучити тимчасовий файл `/etc/passwd.tmp` через `unlink()` та зняти блокування `ulckpwdf()`.

## Розбір синтаксичних правил та парсинг маніфестів

Парсер системних маніфестів повинен коректно обробляти текстові рядки, виключаючи коментарі (рядки, що починаються з `#`), порожні рядки та роздільники у вигляді пробілів або табуляцій.

Кожен запис описує правило типу `u` (користувач), `g` (група), `m` (членство) або `r` (діапазон). При розборі полів символ дефісу `-` інтерпретується як виклик стандартної поведінки:
* Якщо поле UID вказано як `-`, утиліта сканує діапазон від `SYS_UID_MIN` (100) до `SYS_UID_MAX` (999) і знаходить найменший не зайнятий UID.
* Якщо поле коментаря GECOS вказано як `-`, використовується порожній рядок або ім'я користувача.
* Якщо поле домашньої теки вказано як `-`, за замовчуванням записується `/`.
* Якщо поле командної оболонки вказано як `-`, записується шлях до забороненої оболонки `/usr/sbin/nologin`.

## Покроковий розбір реалізації мовами C та C++

У реалізації мовою C для блокування бази даних використовується виклик `lckpwdf()`. Зчитання наявних користувачів виконується через послідовний перебір записів за допомогою `setpwent()` та `getpwent()`. Особлива увага приділяється прапорцям створення тимчасового файлу `open("/etc/passwd.tmp", O_WRONLY | O_CREAT | O_EXCL, 0644)`. Прапорець `O_EXCL` гарантує, що якщо файл `/etc/passwd.tmp` уже існує, системний виклик поверне помилку `EEXIST`.

Багатопотокова безпека та реінтерабельність вимагають обережності при роботі з POSIX функціями читання баз даних. Функція `getpwent()` повертає покажчик на статичний внутрішній буфер C-бібліотеки, який перевикористовується при наступних викликах. Тому в багатопотоковому середовищі або при паралельній обробці декількох маніфестів краще використовувати потокобезпечний аналог `getpwent_r()`, який приймає виділений розробником буфер пам'яті.

У реалізації мовою C++ ризики витоку ресурсів та невиконання очищення при виключеннях усуваються за допомогою ідіоми RAII:
* Клас `PasswdLock` гарантовано викликає `ulckpwdf()` у деструкторі при виході з області видимості.
* Клас `ScopeFileCleanup` відповідає за автовидалення тимчасового файлу `/etc/passwd.tmp` при виникненні помилок.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <shadow.h>
#include <pwd.h>
#include <grp.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

#define SYS_UID_MIN 100
#define SYS_UID_MAX 999

typedef struct {
    char type;
    char name[32];
    uid_t requested_uid;
    char comment[64];
    char home[128];
    char shell[64];
} sysuser_rule_t;

/* Перевірка чи існує ім'я або UID у поточній базі passwd */
static int user_exists(const char *name, uid_t uid) {
    struct passwd *pw;
    setpwent();
    while ((pw = getpwent()) != NULL) {
        if (strcmp(pw->pw_name, name) == 0 || (uid != 0 && pw->pw_uid == uid)) {
            endpwent();
            return 1;
        }
    }
    endpwent();
    return 0;
}

/* Пошук першого вільного UID у системному діапазоні SYS_UID_MIN..SYS_UID_MAX */
static uid_t find_free_uid(void) {
    for (uid_t candidate = SYS_UID_MIN; candidate <= SYS_UID_MAX; candidate++) {
        int used = 0;
        struct passwd *pw;
        setpwent();
        while ((pw = getpwent()) != NULL) {
            if (pw->pw_uid == candidate) {
                used = 1;
                break;
            }
        }
        endpwent();
        if (!used) {
            return candidate;
        }
    }
    return 0;
}

/* Атомарне додавання запису користувача у /etc/passwd */
int add_sysuser(const sysuser_rule_t *rule) {
    if (lckpwdf() != 0) {
        fprintf(stderr, "Помилка блокування бази даних passwd: %s\n", strerror(errno));
        return -1;
    }

    if (user_exists(rule->name, rule->requested_uid)) {
        printf("Користувач %s або UID %u вже існує. Пропускаємо.\n", rule->name, rule->requested_uid);
        ulckpwdf();
        return 0;
    }

    uid_t final_uid = rule->requested_uid;
    if (final_uid == 0) {
        final_uid = find_free_uid();
        if (final_uid == 0) {
            fprintf(stderr, "Немає вільних UID у діапазоні %d-%d\n", SYS_UID_MIN, SYS_UID_MAX);
            ulckpwdf();
            return -1;
        }
    }

    /* Відкриваємо існуючий /etc/passwd та створюємо /etc/passwd.tmp */
    FILE *old_fp = fopen("/etc/passwd", "r");
    if (!old_fp) {
        perror("Помилка відкриття /etc/passwd");
        ulckpwdf();
        return -1;
    }

    int tmp_fd = open("/etc/passwd.tmp", O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (tmp_fd < 0) {
        perror("Помилка створення /etc/passwd.tmp");
        fclose(old_fp);
        ulckpwdf();
        return -1;
    }

    FILE *tmp_fp = fdopen(tmp_fd, "w");
    if (!tmp_fp) {
        perror("fdopen помилка");
        close(tmp_fd);
        fclose(old_fp);
        ulckpwdf();
        return -1;
    }

    /* Копіюємо наявні записи */
    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), old_fp)) {
        fputs(buffer, tmp_fp);
    }
    fclose(old_fp);

    /* Записуємо новий рядок користувача */
    fprintf(tmp_fp, "%s:x:%u:%u:%s:%s:%s\n",
            rule->name,
            final_uid,
            final_uid, /* GID дорівнює UID */
            rule->comment[0] ? rule->comment : rule->name,
            rule->home[0] ? rule->home : "/",
            rule->shell[0] ? rule->shell : "/usr/sbin/nologin");

    fflush(tmp_fp);
    if (fsync(fileno(tmp_fp)) != 0) {
        perror("Помилка скидання даних на диск (fsync)");
        fclose(tmp_fp);
        unlink("/etc/passwd.tmp");
        ulckpwdf();
        return -1;
    }
    fclose(tmp_fp);

    /* Атомарна заміна файлу */
    if (rename("/etc/passwd.tmp", "/etc/passwd") != 0) {
        perror("Помилка атомарної заміни rename()");
        unlink("/etc/passwd.tmp");
        ulckpwdf();
        return -1;
    }

    ulckpwdf();
    printf("Успішно додано користувача %s (UID: %u)\n", rule->name, final_uid);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <optional>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cerrno>
#include <cstring>
#include <unistd.h>
#include <shadow.h>
#include <pwd.h>
#include <fcntl.h>
#include <sys/stat.h>

constexpr uid_t SYS_UID_MIN = 100;
constexpr uid_t SYS_UID_MAX = 999;

// RAII обгортка для глобального блокування lckpwdf
class PasswdLock {
public:
    PasswdLock() {
        if (lckpwdf() != 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося отримати блокування lckpwdf");
        }
    }
    ~PasswdLock() {
        ulckpwdf();
    }
    PasswdLock(const PasswdLock&) = delete;
    PasswdLock& operator=(const PasswdLock&) = delete;
};

// RAII обгортка для контролю файлових дескрипторів та видалення тимчасового файлу при помилках
class ScopeFileCleanup {
    std::string filepath_;
    bool success_{false};
public:
    explicit ScopeFileCleanup(std::string path) : filepath_(std::move(path)) {}
    ~ScopeFileCleanup() {
        if (!success_) {
            ::unlink(filepath_.c_str());
        }
    }
    void mark_success() { success_ = true; }
};

struct SysUserRule {
    char type{'u'};
    std::string name;
    uid_t requested_uid{0};
    std::string comment;
    std::string home{"/"};
    std::string shell{"/usr/sbin/nologin"};
};

class SysUsersEngine {
public:
    static bool user_exists(const std::string& name, uid_t uid) {
        ::setpwent();
        struct passwd* pw = nullptr;
        while ((pw = ::getpwent()) != nullptr) {
            if ((!name.empty() && name == pw->pw_name) || (uid != 0 && pw->pw_uid == uid)) {
                ::endpwent();
                return true;
            }
        }
        ::endpwent();
        return false;
    }

    static std::optional<uid_t> find_free_uid() {
        for (uid_t candidate = SYS_UID_MIN; candidate <= SYS_UID_MAX; ++candidate) {
            if (!user_exists("", candidate)) {
                return candidate;
            }
        }
        return std::nullopt;
    }

    static void apply_rule(const SysUserRule& rule) {
        PasswdLock lock; // Блокування знімається автоматично при виході з області видимості

        if (user_exists(rule.name, rule.requested_uid)) {
            std::cout << "Користувач " << rule.name << " вже існує у системі. Пропускаємо.\n";
            return;
        }

        uid_t final_uid = rule.requested_uid;
        if (final_uid == 0) {
            auto free_uid = find_free_uid();
            if (!free_uid) {
                throw std::runtime_error("Вичерпано вільні UID у системному діапазоні");
            }
            final_uid = *free_uid;
        }

        const std::string target_path = "/etc/passwd";
        const std::string tmp_path = "/etc/passwd.tmp";

        ScopeFileCleanup cleanup(tmp_path);

        std::ifstream input(target_path);
        if (!input.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + target_path);
        }

        int tmp_fd = ::open(tmp_path.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (tmp_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити " + tmp_path);
        }

        // Записуємо через файловий потік
        {
            std::ofstream output("/proc/self/fd/" + std::to_string(tmp_fd));
            std::string line;
            while (std::getline(input, line)) {
                output << line << "\n";
            }

            output << rule.name << ":x:" << final_uid << ":" << final_uid << ":"
                   << (rule.comment.empty() ? rule.name : rule.comment) << ":"
                   << rule.home << ":" << rule.shell << "\n";
            
            output.flush();
        }

        if (::fsync(tmp_fd) != 0) {
            ::close(tmp_fd);
            throw std::system_error(errno, std::generic_category(), "Помилка скидання даних на диск fsync()");
        }
        ::close(tmp_fd);

        if (::rename(tmp_path.c_str(), target_path.c_str()) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка атомарної заміни rename()");
        }

        cleanup.mark_success();
        std::cout << "Успішно створено системного користувача: " << rule.name << " (UID: " << final_uid << ")\n";
    }
};
```
:::

## Крайові випадки та обробка сигналів переривання

Під час виконання операцій оновлення системних файлів у реальних виробничих середовищах можуть виникати крайові випадки, які вимагають додаткової обробки:

1. **Аварійне переривання процесу сигналом SIGINT або SIGTERM.** Якщо утиліта отримує сигнал переривання під час виконання `fsync()`, файлове блокування `lckpwdf()` за замовчуванням не знімається автоматично ОС, оскільки це блокування реалізовано через утворення файлу `/etc/.pwd.lock`. Для захисту від цього `systemd-sysusers` реєструє обробники сигналів (signal handlers) через `sigaction()`, які при отриманні `SIGINT`/`SIGTERM` видаляють тимчасові `.tmp` файли та знімають lock-файл перед завершенням процесу.
2. **Переповнення діапазону системних UID.** Якщо всі системні ідентифікатори в діапазоні 1..999 вже виділені під інші служби, алгоритм `find_free_uid()` повертає `std::nullopt`. Утиліта не намагається самовільно розширити діапазон за межі `SYS_UID_MAX`, оскільки це вторглося б у простір звичайних користувачів. Замість цього утиліта зупиняє транзакцію та генерує критичне повідомлення помилки.
3. **Читання баз даних у режимі Read-Only rootfs.** У разі спроби виконання утиліти на файловій системі, де `/etc` є невпливовою або змонтованою лише для читання, системний виклик `open("/etc/passwd.tmp", O_CREAT)` повертає помилку `EROFS` (Read-only file system). `systemd-sysusers` перехоплює цю ситуацію і, якщо відповідні користувачі вже присутні в системі, не зупиняє завантаження з помилкою.

Порівнюючи C та C++ варіанти, можна чітко побачити переваги сучасних мовних концепцій: використання RAII у C++ унеможливлює витік файлового блокування або залишення сирітського файла `/etc/passwd.tmp` на диску в разі збою чи виключної ситуації.
