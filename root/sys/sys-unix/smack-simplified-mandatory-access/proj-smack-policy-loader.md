# ⚙️ Практична реалізація завантажувача правил та управління xattr

Ця вставка містить практичну реалізацію системної утиліти для адміністрування підсистеми розмежування доступу SMACK у ядрі Linux. Програма демонструє виконання трьох фундаментальних операцій: динамічне завантаження нових правил доступу у віртуальний файл `/sys/fs/smackfs/load2`, призначення мандатних розширених атрибутів `security.SMACK64` на об'єкти файлової системи за допомогою системного виклику `setxattr()`, а також виконання програмних перевірок дозволів доступу через інтерфейс `/sys/fs/smackfs/access2`.

## 1. Архітектурна задача та алгоритм розв'язання

При створенні ізольованих середовищ (пісочниць) для системних служб (наприклад, вебсервера, мобільного додатка або демона аудіо) завантажувач повинен динамічно налаштувати політики доступу в ядрі Linux перед запуском цільового процесу.

Для реалізації цієї задачі розробляється програма, яка виконує послідовність дій:
1. **Створення тестового об'єкта:** Створюється новий файл у тимчасовій файловій системі (`/tmp/smack_test.txt`).
2. **Призначення мітки об'єкта:** За допомогою системного виклику `setxattr()` на створений файл встановлюється розширений атрибут `security.SMACK64` зі значенням `"UserData"`.
3. **Завантаження правила політики:** У керувальний файл `/sys/fs/smackfs/load2` відправляється рядок правила `WebBrowser UserData rw`, який дозволяє процесам із міткою `"WebBrowser"` читати та писати у файли з міткою `"UserData"`.
4. **Програмна перевірка правил:** Програма звертається до файлу `/sys/fs/smackfs/access2` і перевіряє, чи надає ядро Linux дозвіл на операцію читання (`r`) та операцію виконання (`x`).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/xattr.h>

#define SMACK_LOAD2_PATH "/sys/fs/smackfs/load2"
#define SMACK_ACCESS_PATH "/sys/fs/smackfs/access2"
#define SMACK_XATTR_NAME "security.SMACK64"

/* Завантаження нового правила доступу у /sys/fs/smackfs/load2 */
static int load_smack_rule(const char *subject, const char *object, const char *access) {
    char rule_buf[768];
    int fd = -1;
    ssize_t bytes_written;
    int len;

    /* Формуємо рядок правила у сучасному форматі load2: "Subject Object Access" */
    len = snprintf(rule_buf, sizeof(rule_buf), "%s %s %s\n", subject, object, access);
    if (len < 0 || len >= (int)sizeof(rule_buf)) {
        fprintf(stderr, "Помилка: правило SMACK не вміщається у буфер\n");
        return -1;
    }

    fd = open(SMACK_LOAD2_PATH, O_WRONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити " SMACK_LOAD2_PATH " (перевірте привілеї або монтування smackfs)");
        return -1;
    }

    bytes_written = write(fd, rule_buf, (size_t)len);
    if (bytes_written < 0) {
        perror("Помилка запису правила у load2");
        close(fd);
        return -1;
    }

    close(fd);
    printf("[C] Успішно завантажено правило: %s %s %s\n", subject, object, access);
    return 0;
}

/* Призначення розширеного атрибута SMACK64 на файл */
static int set_smack_label(const char *filepath, const char *label) {
    size_t label_len = strlen(label);

    /* Зверніть увагу: нульовий байт '\0' НЕ включається у значення xattr для SMACK */
    if (setxattr(filepath, SMACK_XATTR_NAME, label, label_len, 0) < 0) {
        perror("Помилка setxattr security.SMACK64");
        return -1;
    }

    printf("[C] Файлу '%s' успішно призначено мітку '%s'\n", filepath, label);
    return 0;
}

/* Перевірка дозволу доступу через /sys/fs/smackfs/access2 */
static int check_smack_access(const char *subject, const char *object, const char *access_request) {
    char query_buf[768];
    char reply_buf[16];
    int fd = -1;
    ssize_t n;
    int len;

    len = snprintf(query_buf, sizeof(query_buf), "%s %s %s", subject, object, access_request);
    if (len < 0 || len >= (int)sizeof(query_buf)) {
        return -1;
    }

    fd = open(SMACK_ACCESS_PATH, O_RDWR);
    if (fd < 0) {
        perror("Помилка відкриття " SMACK_ACCESS_PATH);
        return -1;
    }

    if (write(fd, query_buf, (size_t)len) < 0) {
        perror("Помилка запису запиту в access");
        close(fd);
        return -1;
    }

    lseek(fd, 0, SEEK_SET);
    n = read(fd, reply_buf, sizeof(reply_buf) - 1);
    close(fd);

    if (n <= 0) {
        fprintf(stderr, "Помилка читання відповіді з access\n");
        return -1;
    }

    reply_buf[n] = '\0';
    /* Повернення '1' означає дозвіл, '0' — відмову */
    int granted = (reply_buf[0] == '1');
    printf("[C] Результат перевірки доступу (%s -> %s [%s]): %s\n",
           subject, object, access_request, granted ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО");
    return granted ? 1 : 0;
}

int main(int argc, char *argv[]) {
    const char *test_file = "/tmp/smack_test_data.txt";
    
    /* 1. Створюємо тестовий файл */
    int fd = open(test_file, O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (fd < 0) {
        perror("Не вдалося створити тестовий файл");
        return EXIT_FAILURE;
    }
    write(fd, "Test Data", 9);
    close(fd);

    /* 2. Призначення мітки об'єкта */
    if (set_smack_label(test_file, "UserData") < 0) {
        return EXIT_FAILURE;
    }

    /* 3. Завантаження правила у ядро */
    if (load_smack_rule("WebBrowser", "UserData", "rw") < 0) {
        return EXIT_FAILURE;
    }

    /* 4. Перевірка доступу */
    check_smack_access("WebBrowser", "UserData", "r");
    check_smack_access("WebBrowser", "UserData", "x");

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <system_error>
#include <filesystem>
#include <expected>
#include <array>
#include <fcntl.h>
#include <unistd.h>
#include <sys/xattr.h>

namespace smack {

constexpr std::string_view load2_path = "/sys/fs/smackfs/load2";
constexpr std::string_view access_path = "/sys/fs/smackfs/access2";
constexpr std::string_view xattr_name = "security.SMACK64";

// RAII обгортка для автоматичного закриття файлового дескриптора
class FileDescriptor {
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
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
    int fd_{-1};
};

// Завантаження правила у /sys/fs/smackfs/load2 з використанням std::expected (C++23)
std::expected<void, std::error_code> load_rule(std::string_view subject,
                                                std::string_view object,
                                                std::string_view access) {
    std::string rule = std::string(subject) + " " + std::string(object) + " " + std::string(access) + "\n";

    FileDescriptor fd(::open(load2_path.data(), O_WRONLY));
    if (!fd.valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ssize_t written = ::write(fd.get(), rule.data(), rule.size());
    if (written < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    std::cout << "[C++] Завантажено правило: " << rule;
    return {};
}

// Призначення мітки SMACK на файл
std::expected<void, std::error_code> set_label(const std::filesystem::path& path,
                                                std::string_view label) {
    int res = ::setxattr(path.c_str(), xattr_name.data(), label.data(), label.size(), 0);
    if (res < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    std::cout << "[C++] Призначено мітку '" << label << "' для файла " << path << "\n";
    return {};
}

// Перевірка прав доступу через /sys/fs/smackfs/access2
std::expected<bool, std::error_code> check_access(std::string_view subject,
                                                   std::string_view object,
                                                   std::string_view access_req) {
    std::string query = std::string(subject) + " " + std::string(object) + " " + std::string(access_req);

    FileDescriptor fd(::open(access_path.data(), O_RDWR));
    if (!fd.valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::write(fd.get(), query.data(), query.size()) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ::lseek(fd.get(), 0, SEEK_SET);

    std::array<char, 16> reply_buf{};
    ssize_t bytes_read = ::read(fd.get(), reply_buf.data(), reply_buf.size() - 1);
    if (bytes_read <= 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    bool granted = (reply_buf[0] == '1');
    std::cout << "[C++] Доступ (" << subject << " -> " << object << " [" << access_req << "]): "
              << (granted ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО") << "\n";
    return granted;
}

} // namespace smack

int main() {
    const std::filesystem::path test_file = "/tmp/smack_test_cpp.txt";

    // Створення тестового файла через C++ filesystem
    {
        std::ofstream ofs(test_file);
        ofs << "CPP Sample Data\n";
    }

    if (auto res = smack::set_label(test_file, "UserData"); !res) {
        std::cerr << "Помилка встановлення мітки: " << res.error().message() << "\n";
        return 1;
    }

    if (auto res = smack::load_rule("WebBrowser", "UserData", "rw"); !res) {
        std::cerr << "Помилка завантаження правила: " << res.error().message() << "\n";
        return 1;
    }

    auto access_r = smack::check_access("WebBrowser", "UserData", "r");
    auto access_x = smack::check_access("WebBrowser", "UserData", "x");

    if (access_r.has_value() && access_x.has_value()) {
        std::cout << "Обидва запити до ядра виконано; 'x' очікувано заборонено правилом rw.\n";
    }

    return 0;
}
```
:::

## 2. Детальний аналіз реалізації та системних викликів

Реалізація завантажувача SMACK спирається на низькорівневі виклики ядра Linux. Розберемо ключові моменти роботи коду у C та C++ версіях.

### Використання системного виклику `setxattr()`
У мові C виклик `setxattr(filepath, "security.SMACK64", label, label_len, 0)` підключається через заголовок `<sys/xattr.h>`.
Параметри виклику:
1. `filepath`: абсолютний шлях до файла у VFS.
2. `"security.SMACK64"`: повна назва розширеного атрибута, включаючи простір імен `security`.
3. `label`: вказівник на буфер із текстом мітки.
4. `label_len`: кількість байтів мітки.
5. `flags`: значення `0` означає створювати або замінювати існуючий атрибут.

У версії C++ використано `std::string_view` для передачі рядків без додаткового виділення пам'яті в купі (англ. *heap allocations*), а шлях до файла обробляється через `std::filesystem::path`.

### Робота з інтерфейсом `/sys/fs/smackfs/load2`
Запис у `load2` виконується через стандартний системний виклик `write()`. У мові C реалізовано форматування рядка через `snprintf()` із перевіркою виходу за межі буфера. У версії C++ використано безпечне склеювання рядків із поверненням об'єкта `std::expected<void, std::error_code>`, що дозволяє обробляти помилки без використання винятків (англ. *exception-free error handling*).

Для забезпечення безпеки ресурсів у C++ реалізовано RAII-обгортку `FileDescriptor`. Вона гарантує негайне закриття файлового дескриптора при виході зі сфери видимості (навіть при виникненні помилок), усуваючи ризик витоку системних дескрипторів (англ. *resource leaks*).

### Зчитування результату перевірки з `/sys/fs/smackfs/access2`
Файл `access2` працює у двонаправленому режимі: запис `write()` надсилає запит, а наступне читання `read()` повертає відповідь ядра. Старий `access` робить те саме, але вимагає полів фіксованої довжини, доповнених пробілами. Оскільки файловий дескриптор зберігає позицію вказівника після запису, перед читанням **обов'язково необхідно виконати `lseek(fd, 0, SEEK_SET)`**, перемістивши вказівник на початок файла. У С++ реалізації використано фіксований стек-масив `std::array<char, 16>` замість сирого буфера.

---

## 3. Часті пастки та граничні випадки при розробці

При роботі з системними інтерфейсами SMACK розробники часто стикаються зі специфічними помилками, які важко діагностувати.

### 1. Пастка завершального нульового символа (`\0`)
Найпоширеніша помилка при використанні `setxattr()` — передача розміру рядка разом із нульовим символом `strlen(label) + 1`.
- **Що відбувається:** Ядро Linux зберігає нульовий символ як частину значення мітки у файловій системі. Мітка файла стає рівною `"UserData\0"`.
- **Наслідок:** При спробі перевірки доступу ядро порівнює рядок правила `"UserData"` із міткою файла `"UserData\0"`. Через розбіжність байтів порівняння повертає незбіг, і ядро блокує доступ з помилкою `-EACCES`, хоча візуально в консолі атрибут виглядає правильним.

### 2. Відсутність привілею `CAP_MAC_ADMIN`
Операції запису в атрибути `security.SMACK64*` та у контрольні файли `/sys/fs/smackfs/` контролюються привілеєм `CAP_MAC_ADMIN`.
- **Що відбувається:** Якщо процес працює під обліковим записом `root` (UID 0), але у файлі `/sys/fs/smackfs/onlycap` вказано мітку, яка не належить даному процесу, ядро відхиляє виклики `setxattr()` та `write()` з помилкою `-EPERM` (Operation not permitted).
- **Виправлення:** Завантажувальні скрипти та адмін-пакети повинні запускатися з міткою, дозволеною у `onlycap`, або до того, як `onlycap` буде заблоковано під час завантаження.

### 3. Застарілий формат `load` проти `load2`
Спроба запису правил у застарілий файл `/sys/fs/smackfs/load` вимагає суворого доповнення пробілами кожного поля мітки до 23 символів.
- **Що відбувається:** Якщо передати рядок `WebBrowser UserData rw\n` у файл `load`, ядро розпарсить перші 23 байти як суб'єкт, наступні 23 байти як об'єкт і поверне помилку формату.
- **Виправлення:** Усі сучасні додатки повинні використовувати виключно файл `/sys/fs/smackfs/load2`.

### 4. Конкурентність та атомарність змін
Ядро Linux захищає внутрішню таблицю `smack_known_list` за допомогою м'ютекса ядра `smack_known_lock`. Запис у `load2` є атомарною операцією. Проте перевірка прав у системному додатку між викликами `open()` та `setxattr()` створить стан гонки (англ. *race condition*), якщо паралельний процес змінить конфігурацію `onlycap` чи `relabel-self`.

### 5. Поведінка на файлових системах без підтримки xattr
Якщо файл створюється у файловій системі, яка не підтримує розширені атрибути `security` (наприклад, деякі віртуальні FS або монтування NFS без підтримки xattr), виклик `setxattr()` повертає помилку `-EOPNOTSUPP` (Operation not supported). У цьому випадку об'єкт назавжди отримує мітку за замовчуванням `_` (floor), що слід враховувати при проєктуванні тимчасових системних сховищ у `/tmp` чи `/dev/shm`.
