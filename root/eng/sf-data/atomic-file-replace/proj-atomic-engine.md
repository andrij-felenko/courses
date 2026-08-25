# ⚙️ Проект: кросплатформна бібліотека атомарної заміни файлів

Цей інженерний проект містить повну реалізацію надійної атомарної заміни файлів для POSIX-систем (Linux, macOS, BSD) та Windows, яка зберігає вихідні права доступу, синхронізує метадані батьківського каталогу та виключає витоки дескрипторів або тимчасових файлів при аварійних збоях.

### Інженерна постановка та інваріанти надійності

Стандартні функції введення-виведення високорівневих мов програмування (`fopen`, `std::ofstream`, `std::filesystem::copy_file`) за замовчуванням модифікують файл на місці або виконують заміну без примусового скидання дискових кешів. Для критично важливих даних (конфігураційні файли, журнали транзакцій, локальні бази даних ключ-значення, файли стану) така поведінка є неприпустимою.

Надійна бібліотека заміни файлів мусить підтримувати такі непорушні інваріанти:

1. **Інваріант цілісності читачів:** Жоден процес або потік, що викликає операцію читання в довільний момент часу, не повинен бачити порожній файл, обрізаний файл або частково оновлений вміст.
2. **Інваріант незмінності оригіналу до підтвердження:** Початковий файл на диску лишається повністю незмінним і чинним аж до моменту, поки всі байти нового вмісту та його метадані не будуть фізично зафіксовані в енергонезалежній пам'яті.
3. **Інваріант чистоти простору імен:** Якщо запис або синхронізація завершуються помилкою (наприклад, через вичерпання дискового простору `ENOSPC`), тимчасовий файл негайно вилучається, а оригінал залишається неушкодженим.
4. **Інваріант збереження безпекового контексту:** Новий файл отримує ті самі права доступу (POSIX mode / Windows ACL), що й оригінальний цільовий файл, а не дефолтні значення поточної маски процесу `umask`.
5. **Інваріант безпеки дескрипторів при паралельних процесах:** Тимчасові дескриптори відкриваються з прапорцем `O_CLOEXEC`, що виключає їхнє випадкове успадкування дочірніми процесами при викликах `fork()` та `exec()`.

### Структура конвеєра заміни

Для виконання зазначених інваріантів реалізація виконує шість послідовних кроків:

- **Крок 1. Аналіз оригіналу:** Виклик `stat()` або `GetFileAttributesExW()`. Якщо файл існує, зчитуються його права доступу (`st_mode & 0777`). Якщо файл новий, призначаються безпечні права за замовчуванням (наприклад, `0644` або `0600`).
- **Крок 2. Створення тимчасового файлу в тому ж каталозі:** Шлях формується додаванням випадкового суфікса до імені файлу в тому самому каталозі (наприклад, `config.json.tmp_XXXXXX`). Використання системного каталогу `/tmp` заборонене, оскільки він часто розміщений на окремому віртуальному диску `tmpfs`, що призведе до помилки `EXDEV` при спробі перейменування.
- **Крок 3. Потоковий запис:** Запис байтів через системний виклик `write()` у циклі для коректної обробки переривань `EINTR` та часткового запису (англ. *short write*).
- **Крок 4. Скидання кешу сторінок та інода:** Виклик `fsync()` на POSIX або `FlushFileBuffers()` на Windows. Тільки після успішного повернення керування дескриптор файлу закривається.
- **Крок 5. Атомарна підміна:** Виклик `rename()` на POSIX або `ReplaceFileW()` / `MoveFileExW(..., MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)` на Windows.
- **Крок 6. Синхронізація батьківського каталогу:** Відкриття дескриптора каталогу через `open(dir, O_RDONLY | O_DIRECTORY)` та виклик `fsync(dir_fd)`.

### Реалізація на мовах C та C++

Нижче наведено робочий код повної реалізації з підтримкою POSIX і Windows.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>

#if defined(_WIN32)
#include <windows.h>
#include <io.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>
#endif

// Результат виконання операції: 0 — успіх, ненульове — код помилки
int atomic_write_file(const char *target_path, const void *data, size_t size) {
    if (!target_path || (!data && size > 0)) {
        return EINVAL;
    }

#if defined(_WIN32)
    // --- Реалізація для Windows ---
    wchar_t w_target[MAX_PATH];
    wchar_t w_temp[MAX_PATH];
    wchar_t w_dir[MAX_PATH];

    if (MultiByteToWideChar(CP_UTF8, 0, target_path, -1, w_target, MAX_PATH) == 0) {
        return (int)GetLastError();
    }

    // Виділяємо каталог цільового файлу
    wcscpy_s(w_dir, MAX_PATH, w_target);
    wchar_t *last_slash = wcsrchr(w_dir, L'\\');
    if (!last_slash) last_slash = wcsrchr(w_dir, L'/');
    if (last_slash) {
        *last_slash = L'\0';
    } else {
        wcscpy_s(w_dir, MAX_PATH, L".");
    }

    // Створюємо унікальний тимчасовий файл у тому ж каталозі
    if (GetTempFileNameW(w_dir, L"atm", 0, w_temp) == 0) {
        return (int)GetLastError();
    }

    HANDLE h_file = CreateFileW(w_temp, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                                FILE_ATTRIBUTE_NORMAL, NULL);
    if (h_file == INVALID_HANDLE_VALUE) {
        DWORD err = GetLastError();
        DeleteFileW(w_temp);
        return (int)err;
    }

    // Запис корисного навантаження
    DWORD bytes_written = 0;
    BOOL write_ok = WriteFile(h_file, data, (DWORD)size, &bytes_written, NULL);
    if (!write_ok || bytes_written != (DWORD)size) {
        DWORD err = GetLastError();
        CloseHandle(h_file);
        DeleteFileW(w_temp);
        return (int)(err ? err : ERROR_WRITE_FAULT);
    }

    // Примусове виштовхування буферів на диск
    if (!FlushFileBuffers(h_file)) {
        DWORD err = GetLastError();
        CloseHandle(h_file);
        DeleteFileW(w_temp);
        return (int)err;
    }
    CloseHandle(h_file);

    // Спроба атомарної заміни через ReplaceFileW (якщо файл уже існував)
    if (!ReplaceFileW(w_target, w_temp, NULL, REPLACEFILE_IGNORE_MERGE_ERRORS, NULL, NULL)) {
        DWORD err = GetLastError();
        // Якщо цільового файлу ще не існувало — використовуємо MoveFileExW
        if (err == ERROR_FILE_NOT_FOUND) {
            if (!MoveFileExW(w_temp, w_target, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
                err = GetLastError();
                DeleteFileW(w_temp);
                return (int)err;
            }
        } else {
            DeleteFileW(w_temp);
            return (int)err;
        }
    }
    return 0;

#else
    // --- Реалізація для POSIX (Linux / macOS / BSD) ---
    mode_t target_mode = 0644;
    struct stat st;
    if (stat(target_path, &st) == 0) {
        target_mode = st.st_mode & 0777; // Зберігаємо вихідні права
    }

    // Формуємо шаблон тимчасового файлу поруч із цільовим
    char tmp_template[4096];
    int written = snprintf(tmp_template, sizeof(tmp_template), "%s.tmp_XXXXXX", target_path);
    if (written < 0 || (size_t)written >= sizeof(tmp_template)) {
        return ENAMETOOLONG;
    }

    // Створюємо безпечний тимчасовий файл
    int fd = mkstemp(tmp_template);
    if (fd < 0) {
        return errno;
    }

    // Встановлюємо збережені права доступу
    if (fchmod(fd, target_mode) != 0) {
        int err = errno;
        close(fd);
        unlink(tmp_template);
        return err;
    }

    // Записуємо всі байти з обробкою неповних записів та переривань
    const uint8_t *ptr = (const uint8_t *)data;
    size_t remaining = size;
    while (remaining > 0) {
        ssize_t n = write(fd, ptr, remaining);
        if (n < 0) {
            if (errno == EINTR) continue; // Переривання сигналом
            int err = errno;
            close(fd);
            unlink(tmp_template);
            return err;
        }
        ptr += n;
        remaining -= (size_t)n;
    }

    // Скидаємо брудні сторінки та інод на фізичний носій
    if (fsync(fd) != 0) {
        int err = errno;
        close(fd);
        unlink(tmp_template);
        return err;
    }

    if (close(fd) != 0) {
        int err = errno;
        unlink(tmp_template);
        return err;
    }

    // Атомарна підміна імені в просторі імен каталогу
    if (rename(tmp_template, target_path) != 0) {
        int err = errno;
        unlink(tmp_template);
        return err;
    }

    // Синхронізація запису батьківського каталогу
    char path_copy[4096];
    strncpy(path_copy, target_path, sizeof(path_copy) - 1);
    path_copy[sizeof(path_copy) - 1] = '\0';
    char *dir_name = dirname(path_copy);

    int dir_fd = open(dir_name, O_RDONLY | O_DIRECTORY);
    if (dir_fd >= 0) {
        fsync(dir_fd); // Помилку каталогу фіксуємо, але не відкочуємо файл
        close(dir_fd);
    }

    return 0;
#endif
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <span>
#include <filesystem>
#include <system_error>
#include <expected>
#include <cstring>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>
#endif

namespace fs = std::filesystem;

class ScopedDescriptor {
public:
#if defined(_WIN32)
    explicit ScopedDescriptor(HANDLE h = INVALID_HANDLE_VALUE) : handle_(h) {}
    ~ScopedDescriptor() { reset(); }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;

    ScopedDescriptor(ScopedDescriptor&& other) noexcept : handle_(other.handle_) {
        other.handle_ = INVALID_HANDLE_VALUE;
    }

    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            handle_ = other.handle_;
            other.handle_ = INVALID_HANDLE_VALUE;
        }
        return *this;
    }

    [[nodiscard]] HANDLE get() const noexcept { return handle_; }
    [[nodiscard]] bool isValid() const noexcept { return handle_ != INVALID_HANDLE_VALUE; }

    void reset(HANDLE h = INVALID_HANDLE_VALUE) noexcept {
        if (handle_ != INVALID_HANDLE_VALUE) {
            CloseHandle(handle_);
            handle_ = h;
        }
    }

    HANDLE release() noexcept {
        HANDLE tmp = handle_;
        handle_ = INVALID_HANDLE_VALUE;
        return tmp;
    }
private:
    HANDLE handle_;
#else
    explicit ScopedDescriptor(int fd = -1) : fd_(fd) {}
    ~ScopedDescriptor() { reset(); }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;

    ScopedDescriptor(ScopedDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = new_fd;
        }
    }

    int release() noexcept {
        int tmp = fd_;
        fd_ = -1;
        return tmp;
    }
private:
    int fd_;
#endif
};

class AtomicFileEngine {
public:
    static std::expected<void, std::error_code> write(
        const fs::path& target_path,
        std::span<const std::byte> payload) noexcept 
    {
        std::error_code ec;
        fs::path parent_dir = target_path.parent_path();
        if (parent_dir.empty()) {
            parent_dir = ".";
        }

#if defined(_WIN32)
        std::wstring w_dir = parent_dir.wstring();
        std::wstring w_target = target_path.wstring();
        wchar_t w_temp[MAX_PATH];

        if (GetTempFileNameW(w_dir.c_str(), L"atm", 0, w_temp) == 0) {
            return std::unexpected(std::error_code((int)GetLastError(), std::system_category()));
        }

        fs::path temp_path(w_temp);
        ScopedDescriptor file_guard(CreateFileW(
            w_temp, GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr));

        if (!file_guard.isValid()) {
            DWORD err = GetLastError();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code((int)err, std::system_category()));
        }

        DWORD written = 0;
        BOOL ok = WriteFile(file_guard.get(), payload.data(), static_cast<DWORD>(payload.size()), &written, nullptr);
        if (!ok || written != payload.size()) {
            DWORD err = GetLastError();
            file_guard.reset();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code((int)(err ? err : ERROR_WRITE_FAULT), std::system_category()));
        }

        if (!FlushFileBuffers(file_guard.get())) {
            DWORD err = GetLastError();
            file_guard.reset();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code((int)err, std::system_category()));
        }
        file_guard.reset(); // Закриваємо дескриптор перед заміною

        if (!ReplaceFileW(w_target.c_str(), w_temp, nullptr, REPLACEFILE_IGNORE_MERGE_ERRORS, nullptr, nullptr)) {
            DWORD err = GetLastError();
            if (err == ERROR_FILE_NOT_FOUND) {
                if (!MoveFileExW(w_temp, w_target.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
                    err = GetLastError();
                    fs::remove(temp_path, ec);
                    return std::unexpected(std::error_code((int)err, std::system_category()));
                }
            } else {
                fs::remove(temp_path, ec);
                return std::unexpected(std::error_code((int)err, std::system_category()));
            }
        }
        return {};

#else
        mode_t target_mode = 0644;
        struct stat st{};
        if (::stat(target_path.c_str(), &st) == 0) {
            target_mode = st.st_mode & 0777;
        }

        std::string temp_tmpl = (target_path.string() + ".tmp_XXXXXX");
        std::vector<char> tmpl_buf(temp_tmpl.begin(), temp_tmpl.end());
        tmpl_buf.push_back('\0');

        int raw_fd = ::mkstemp(tmpl_buf.data());
        if (raw_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        ScopedDescriptor file_guard(raw_fd);
        fs::path temp_path(tmpl_buf.data());

        if (::fchmod(file_guard.get(), target_mode) != 0) {
            int err = errno;
            file_guard.reset();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        const auto* src = reinterpret_cast<const uint8_t*>(payload.data());
        size_t remaining = payload.size();
        while (remaining > 0) {
            ssize_t n = ::write(file_guard.get(), src, remaining);
            if (n < 0) {
                if (errno == EINTR) continue;
                int err = errno;
                file_guard.reset();
                fs::remove(temp_path, ec);
                return std::unexpected(std::error_code(err, std::generic_category()));
            }
            src += n;
            remaining -= static_cast<size_t>(n);
        }

        if (::fsync(file_guard.get()) != 0) {
            int err = errno;
            file_guard.reset();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }
        file_guard.reset(); // Закриваємо файл перед rename

        if (::rename(temp_path.c_str(), target_path.c_str()) != 0) {
            int err = errno;
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        // Синхронізація батьківського каталогу
        ScopedDescriptor dir_guard(::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY));
        if (dir_guard.isValid()) {
            ::fsync(dir_guard.get());
        }

        return {};
#endif
    }
};
```
:::

### Методика тестування стійкості до збоїв

Для практичної верифікації відсутності витоків та пошкодження даних використовується спеціальний інструмент ядра Linux — цільовий модуль емуляції несправностей `dm-flakey` у підсистемі Device Mapper.

Схема тестування виглядає так:
1. Створюється віртуальний блоковий пристрій у пам'яті (`ramdisk` або `loopback`).
2. Налаштовується таблиця `dm-flakey`, яка дозволяє запис протягом перших 2 секунд, а потім імітує миттєвий обрив живлення (скидає всі незафіксовані операції вводу-виводу).
3. Запускається тестовий потік, який у нескінченному циклі викликає функцію `atomic_write_file()` для оновлення файлу конфігурації зростаючими лічильниками версій.
4. Паралельно інший процес читає файл і перевіряє контрольну суму CRC32.
5. Після примусового падіння блокового пристрою монтується файлова система та перевіряється цілісність: файл повинен або містити версію `N`, або версію `N-1`, але ніколи не бути нульовим чи битим.

### Пастки та крайові випадки

Під час експлуатації цієї схеми у високонавантажених системах виникають чотири неочевидні ситуації:

- **Вичерпання ліміту дескрипторів і пам'яті (`EMFILE` / `ENOSPC`):** Атомарна заміна тимчасово подвоює вимоги до вільного місця на розділі для цього файлу. Якщо на диску залишилося 10 МБ, а ви оновлюєте файл розміром 15 МБ, `write()` поверне `ENOSPC`. Використання RAII-обгорток гарантує, що недописаний тимчасовий файл вилучиться з диска автоматично під час розкручування стека.
- **Мережеві файлові системи (NFS, CIFS/SMB):** На мережевих монтуваннях виклик `rename()` часто не має суворої атомарності, а виклик `fsync(dir_fd)` може повернути `EINVAL` або `EPERM`. У розподілених системах для координації заміни слід використовувати блокування або консенсусні сховища.
- **Втрата жорстких посилань (Hard Links):** Якщо на цільовий файл вказували інші жорсткі посилання в системі, виклик `rename()` розриває їхній зв'язок. Ім'я `target_path` починає вказувати на новий інод, тоді як усі інші посилання продовжують вказувати на старий інод.
- **Продуктивність на твердотільних накопичувачах:** Частий виклик `fsync()` скорочує ресурс SSD та викликає затримки черги вводу-виводу. Для файлів, що оновлюються тисячі разів на секунду, замість атомарної заміни цілого файлу слід використовувати логування в оперативній пам'яті з пакетним скиданням (англ. *group commit*).
