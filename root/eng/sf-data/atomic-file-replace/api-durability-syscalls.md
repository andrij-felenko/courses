# 📋 Системні виклики надійного запису: POSIX, Linux та Windows API

Цей довідник містить вичерпні сигнатури, опис прапорців, семантику повернення помилок та фізичні гарантії надійності для системних викликів синхронізації файлів і каталогів у POSIX-сумісних ОС (Linux, macOS, FreeBSD) та Microsoft Windows.

### 1. Синхронізація файлових буферів та метаданих

Операційні системи суворо розділяють операції скидання самих сторінок даних (байтів тіла файлу) та операції оновлення системних атрибутів (метаданих інода: розмір, часові мітки модифікації, покажчики на виділені дискові екстенти та права доступу).

#### `int fsync(int fd);`
- **Стандарт:** POSIX.1-2001, 4.3BSD, SVr4.
- **Призначення:** Передає всі змінені дані файлу (брудні сторінки в системному кеші Page Cache) та всі службові метадані, пов'язані з файлом (розмір `st_size`, часові мітки `st_mtime`/`st_ctime`, таблиці дискових екстентів), на дисковий накопичувач. Виклик блокує потік виконання доти, доки носій не підтвердить фізичну фіксацію інформації.
- **Гарантія:** Забезпечує повну стійкість до раптового зникнення напруги живлення (англ. *power-loss durability*). Після повернення з `fsync()` стан файлу гарантовано зберігається на носії.
- **Повертане значення:** `0` при успіху; `-1` при виникненні помилки із встановленням глобальної змінної `errno`.
- **Основні коди помилок:**
  - `EBADF`: параметр `fd` не є дійсним файловим дескриптором, відкритим для запису.
  - `EIO`: сталася фізична апаратна помилка введення-виведення під час передачі блоків на накопичувач.
  - `ENOSPC`: на файловій системі з відкладеним виділенням блоків (ext4 delalloc, XFS) вичерпано вільне дискове місце під час спроби матеріалізувати брудні сторінки.
  - `EDQUOT`: перевищено ліміт дискової квоти користувача.
  - `EROFS`, `EINVAL`: дескриптор `fd` вказує на спеціальний об'єкт (канал pipe, сокет чи FIFO), який не підтримує дискову синхронізацію.

#### `int fdatasync(int fd);`
- **Стандарт:** POSIX.1-2001.
- **Призначення:** Оптимізована версія `fsync()`, яка примусово скидає на носій байти даних і лише ті метадані, які є критично необхідними для коректного зчитування файлу в майбутньому (наприклад, зміну довжини файлу `st_size` або нові блоки екстентів). Несуттєві атрибути, такі як час останнього доступу `st_atime` або модифікації `st_mtime`, на диск негайно не виштовхуються.
- **Продуктивність:** Дозволяє уникнути зайвого запису метаданих у журнал файлової системи, якщо файл модифікувався без зміни розміру, зменшуючи затримку синхронізації на шпиндельних дисках (HDD) та SSD.

#### `int sync_file_range(int fd, off64_t offset, off64_t nbytes, unsigned int flags);`
- **Платформа:** Специфічний системний виклик Linux (починаючи з ядра 2.6.17).
- **Призначення:** Дозволяє асинхронно ініціювати скидання діапазону сторінок файлу в фоновому режимі або заблокувати потік до завершення запису конкретного відрізка.
- **Прапорці (`flags`):**
  - `SYNC_FILE_RANGE_WAIT_BEFORE`: очікувати завершення попереднього запису сторінок у зазначеному діапазоні перед початком нового виклику.
  - `SYNC_FILE_RANGE_WRITE`: ініціювати асинхронний запис усіх брудних сторінок діапазону.
  - `SYNC_FILE_RANGE_WAIT_AFTER`: заблокувати потік і дочекатися завершення запису всіх сторінок діапазону на накопичувач.
- **Важливе застереження:** `sync_file_range()` **не скидає метадані файлу** (інод) і не надсилає команду апаратного бар'єра кешу контролера накопичувача. Тому він **не є заміною `fsync()`**, але слугує ефективним інструментом для поступового скидання великих файлів у процесі потокового запису перед фінальним викликом `fsync()`.

#### `int fcntl(int fd, F_FULLFSYNC);` (Apple macOS / iOS / Darwin)
- **Призначення:** На системах macOS виклик `fsync()` за замовчуванням виштовхує дані лише з буфера ядра в оперативну пам'ять самого накопичувача (On-Drive Volatile Cache), не надсилаючи команду `SYNCHRONIZE CACHE`. Для гарантованого захисту від втрати живлення команда `fcntl(fd, F_FULLFSYNC)` відправляє апаратний бар'єр безпосередньо контролеру носія.

#### `BOOL FlushFileBuffers(HANDLE hFile);` (Microsoft Windows Win32)
- **Призначення:** Скидає всі внутрішні буфери файлової системи Windows (NTFS, ReFS, FAT32) для зазначеного файлу чи каталогу та надсилає команду вивантаження кешу фізичному накопичувачу.
- **Повертане значення:** Ненульове значення при успішному завершенні; `0` у разі збою (детальний код помилки отримується за допомогою функції `GetLastError()`).

---

### 2. Атомарна маніпуляція простором імен каталогу

Операції заміни імен у просторі файлової системи виконуються на рівні записів каталогу (dentry) і є атомарними з точки зору паралельних читачів.

#### `int rename(const char *oldpath, const char *newpath);`
- **Стандарт:** POSIX.1-2001, C89, C99.
- **Семантика заміни:** Якщо файл `newpath` уже існує, він атомарно замінюється на `oldpath`. Паралельні читачі ні за яких обставин не можуть побачити стан, у якому файл `newpath` відсутній.
- **Обмеження та помилки:**
  - `EXDEV` (*Invalid cross-device link*): шляхи `oldpath` та `newpath` розміщені на різних змонтованих розділах або файлових системах.
  - `EACCES` / `EPERM`: відсутні права на запис у батьківський каталог або встановлено прапорець `immutable` (`chattr +i`).
  - `EBUSY`: файл використовується системою у спосіб, що блокує перейменування (наприклад, є точкою монтування).
- **Синхронізація:** Виклик `rename()` оновлює структуру каталогу в пам'яті, але не гарантує негайного запису на диск. Для надійності після `rename()` обов'язково викликається `fsync()` для дескриптора батьківського каталогу.

#### `int renameat2(int olddirfd, const char *oldpath, int newdirfd, const char *newpath, unsigned int flags);`
- **Платформа:** Linux 3.15+.
- **Прапорці (`flags`):**
  - `0`: Повна відповідність стандартному виклику `renameat()`.
  - `RENAME_EXCHANGE`: Атомарно міняє місцями два наявні файли `oldpath` та `newpath`. Обидва об'єкти мусять існувати; жоден із файлів не видаляється.
  - `RENAME_NOREPLACE`: Повертає помилку `EEXIST`, якщо файл `newpath` уже існує в каталозі (унеможливлює випадковий перезапис цілі).
  - `RENAME_WHITEOUT`: Створює спеціальний whiteout-об'єкт, специфічний для шаруватих файлових систем (UnionFS, OverlayFS).

#### `BOOL ReplaceFileW(LPCWSTR lpReplaced, LPCWSTR lpReplacement, LPCWSTR lpBackup, DWORD dwFlags, LPVOID lpExclude, LPVOID lpReserved);`
- **Платформа:** Windows Win32 (NT 4.0 SP6+).
- **Призначення:** Виконує атомарну заміну файлу `lpReplacedFileName` вмістом `lpReplacementFileName` з автоматичним збереженням вихідних списків контролю доступу (NTFS ACL), потоків даних (Alternate Data Streams) та атрибутів безпеки. Опційно створює резервну копію у файлі `lpBackupFileName`.
- **Прапорці (`dwFlags`):**
  - `REPLACEFILE_WRITE_THROUGH`: примусово скидає метадані на диск перед поверненням.
  - `REPLACEFILE_IGNORE_MERGE_ERRORS`: ігнорує несумісності злиття допоміжних атрибутів.

#### `BOOL MoveFileExW(LPCWSTR lpExisting, LPCWSTR lpNew, DWORD dwFlags);`
- **Платформа:** Windows Win32.
- **Прапорці (`dwFlags`):**
  - `MOVEFILE_REPLACE_EXISTING`: дозволяє замінити наявний цільовий файл.
  - `MOVEFILE_WRITE_THROUGH`: блокує потік до завершення запису змін на фізичний носій.
  - `MOVEFILE_COPY_ALLOWED`: якщо файли розташовані на різних дискових томах, емулює переміщення через копіювання (втрачаючи атомарність).

---

### 3. Анонімні тимчасові файли Linux (`O_TMPFILE`)

Починаючи з Linux 3.11, ядра з підтримкою файлових систем ext4, XFS та Btrfs дозволяють створювати безіменні файли безпосередньо в інодному просторі каталогу:

:::tabs
```c
#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int write_via_tmpfile(const char *dir, const char *target, const void *buf, size_t len) {
    // Створення файлу без імені у просторі каталогу
    int fd = open(dir, O_TMPFILE | O_RDWR, 0600);
    if (fd < 0) return -1;

    // Запис та скидання на диск
    if (write(fd, buf, len) != (ssize_t)len || fsync(fd) != 0) {
        close(fd);
        return -1;
    }

    // Атомарне надання імені (прив'язка до dentry)
    char fd_path[64];
    snprintf(fd_path, sizeof(fd_path), "/proc/self/fd/%d", fd);
    int res = linkat(AT_FDCWD, fd_path, AT_FDCWD, target, AT_SYMLINK_FOLLOW);
    close(fd);
    return res;
}
```
```cpp
#include <fcntl.h>
#include <unistd.h>
#include <filesystem>
#include <span>
#include <string>
#include <system_error>
#include <expected>

namespace fs = std::filesystem;

class AnonymousTempWriter {
public:
    static std::expected<void, std::error_code> writeAndLink(
        const fs::path& directory,
        const fs::path& target_name,
        std::span<const std::byte> data) noexcept 
    {
        int fd = ::open(directory.c_str(), O_TMPFILE | O_RDWR, 0600);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct AutoClose {
            int fd;
            ~AutoClose() { if (fd >= 0) ::close(fd); }
        } guard{fd};

        const auto* ptr = reinterpret_cast<const uint8_t*>(data.data());
        size_t rem = data.size();
        while (rem > 0) {
            ssize_t n = ::write(fd, ptr, rem);
            if (n < 0) {
                if (errno == EINTR) continue;
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            ptr += n;
            rem -= static_cast<size_t>(n);
        }

        if (::fsync(fd) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::string proc_fd = "/proc/self/fd/" + std::to_string(fd);
        fs::path target_full = directory / target_name;
        if (::linkat(AT_FDCWD, proc_fd.c_str(), AT_FDCWD, target_full.c_str(), AT_SYMLINK_FOLLOW) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }
};
```
:::

**Перевага:** Якщо процес вбивають сигналом `SIGKILL` або зникає живлення під час запису, на диску взагалі не залишається сміттєвих тимчасових файлів — інод вилучається ядром автоматично.

---

### 4. Зведена таблиця поведінки системних викликів

| Системний виклик | ОС | Що скидає | Чи гарантує диск | Складність / Ціна |
|---|---|---|---|---|
| `fsync(fd)` | POSIX | Дані + усі метадані інода | Так (flush носія) | Середня (1–15 мс) |
| `fdatasync(fd)` | POSIX | Дані + розмір файлу | Так | Низька (1–5 мс) |
| `sync_file_range` | Linux | Лише брудні сторінки діапазону | Ні (без інода й бар'єра) | Мінімальна (асинхронно) |
| `fcntl(F_FULLFSYNC)` | macOS | Дані + кеш диска | Так (апаратний бар'єр) | Висока (5–30 мс) |
| `FlushFileBuffers` | Windows | Дані + метадані NTFS | Так | Середня (1–10 мс) |
| `rename(old, new)` | POSIX | Змінює пам'ять каталогу | Ні (потрібен `fsync(dir)`) | Мікросекунди |
| `renameat2(EXCHANGE)`| Linux | Обмін покажчиків у dentry | Ні | Мікросекунди |
| `ReplaceFileW` | Windows | Заміна файлу з ACL | Так (з `WRITE_THROUGH`) | Середня |
