# 📋 Довідник дескрипторно-орієнтованих системних викликів POSIX та Linux

Цей довідник містить повну специфікацію системних викликів сімейства `*at`, прапорців захисту VFS та дескрипторних операцій, що усувають простір для гонок TOCTOU при маніпуляціях файловою системою. На відміну від застарілих викликів, що оперують глобальними рядковими шляхами, дескрипторні функції прив'язують операцію або до відкритого інода (через числовий файловий дескриптор `fd`), або до базового каталогу (`dirfd`), унеможливлюючи підміну проміжних та кінцевих вузлів дерева файлової системи сторонніми процесами.

## Концепція дескрипторної прив'язки у VFS

У традиційному інтерфейсі операційної системи Unix кожен виклик за рядковим шляхом (наприклад, `open("/tmp/app/file", O_RDWR)`) змушує підсистему VFS ядра Linux виконувати повний цикл розв'язання імені (path walk), починаючи від кореневого каталогу процесу або поточного робочого каталогу. Цей процес є вразливим до зовнішніх змін у каталогах, через які проходить шлях.

Дескрипторно-орієнтовані виклики сімейства `*at` (стандартизовані у специфікації POSIX.1-2008) змінюють семантику роботи:
1. Замість неявного поточного робочого каталогу функція явно приймає дескриптор відкритого каталогу `dirfd`.
2. Якщо переданий шлях є відносним, ядро починає розв'язання безпосередньо з інода, на який вказує `dirfd`.
3. Якщо дескриптор каталогу відкрито з прапорцем `O_DIRECTORY | O_CLOEXEC`, сторонні процеси не можуть змінити розташування базової точки входу в дерево, навіть якщо вони перейменують усі батьківські каталоги на диску.

---

## Зведена таблиця системних викликів

| Традиційний виклик (вразливий до TOCTOU) | Дескрипторний аналог для закріпленого файлу | Виклик сімейства `*at` для відносного шляху | Призначення операції |
|---|---|---|---|
| `open(path, flags, mode)` | — | `openat(dirfd, path, flags, mode)` | Відкриття або атомарне створення файлу |
| `creat(path, mode)` | — | `openat(dirfd, path, O_CREAT \| O_WRONLY \| O_TRUNC, mode)` | Створення нового файлу з очищенням |
| `stat(path, &st)` | `fstat(fd, &st)` | `fstatat(dirfd, path, &st, flags)` | Отримання метаданих інода |
| `lstat(path, &st)` | `fstat(fd, &st)` *(із O_PATH)* | `fstatat(dirfd, path, &st, AT_SYMLINK_NOFOLLOW)` | Інспекція самого символьного посилання |
| `chmod(path, mode)` | `fchmod(fd, mode)` | `fchmodat(dirfd, path, mode, flags)` | Зміна бітів режиму доступу |
| `chown(path, uid, gid)` | `fchown(fd, uid, gid)` | `fchownat(dirfd, path, uid, gid, flags)` | Зміна власника та групи інода |
| `unlink(path)` | — | `unlinkat(dirfd, path, 0)` | Видалення імені файлу з каталогу |
| `rmdir(path)` | — | `unlinkat(dirfd, path, AT_REMOVEDIR)` | Видалення порожнього каталогу |
| `rename(old, new)` | — | `renameat2(olddirfd, old, newdirfd, new, flags)` | Атомарне перейменування та заміна |
| `readlink(path, buf, sz)` | — | `readlinkat(dirfd, path, buf, sz)` | Читання вмісту символьного посилання |

---

## Детальний опис інтерфейсів та сигнатур

### 1. `openat()` — безпечне відкриття відносно дескриптора каталогу

Системний виклик `openat()` є основним інструментом для безпечного створення та відкриття файлів у сучасних Unix-подібних системах.

:::tabs
```c
#include <fcntl.h>

int openat(int dirfd, const char *pathname, int flags, ... /* mode_t mode */);
```
```cpp
#include <fcntl.h>
#include <string_view>

// Ідіоматична C++ обгортка для openat
inline int openat_safe(int dirfd, std::string_view pathname, int flags, mode_t mode = 0) {
    return ::openat(dirfd, pathname.data(), flags, mode);
}
```
:::

- **Параметри:**
  - `dirfd`: числовий файловий дескриптор попередньо відкритого каталогу. Може приймати спеціальне значення `AT_FDCWD`, що вказує на використання поточного робочого каталогу процесу (як у класичному `open`).
  - `pathname`: текстовий шлях. Якщо шлях є відносним, пошук починається з каталогу `dirfd`. Якщо шлях є абсолютним (починається з `/`), значення `dirfd` ігнорується, і ядро виконує пошук від глобального кореня.
  - `flags`: бітова маска режиму доступу (`O_RDONLY`, `O_WRONLY`, `O_RDWR`) та прапорців безпеки (`O_CREAT`, `O_EXCL`, `O_NOFOLLOW`, `O_CLOEXEC`, `O_DIRECTORY`, `O_PATH`, `O_TMPFILE`).
  - `mode`: права доступу нового файлу у вісімковому форматі (наприклад, `0600`), які застосовуються з урахуванням `umask` процесу. Обов'язковий при використанні `O_CREAT` або `O_TMPFILE`.
- **Повертане значення:** невід'ємний числовий дескриптор відкритого файлу у разі успіху; `-1` у разі виникнення помилки із записом відповідного коду в глобальну змінну `errno`.

---

### 2. `fstat()` та `fstatat()` — інспекція метаданих без ризику заміни

Системні виклики сімейства `fstat` дозволяють отримати структуру `struct stat` для ресурсу без проходження текстового шляху наново.

:::tabs
```c
#include <sys/stat.h>
#include <fcntl.h>

int fstat(int fd, struct stat *statbuf);
int fstatat(int dirfd, const char *pathname, struct stat *statbuf, int flags);
```
```cpp
#include <sys/stat.h>
#include <fcntl.h>
#include <expected>
#include <system_error>

inline std::expected<struct stat, std::error_code> get_file_stat(int fd) {
    struct stat st{};
    if (::fstat(fd, &st) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return st;
}
```
:::

- **Властивості `fstat`:** операція виконується безпосередньо над структурою `struct file`, яка вже зберігається в пам'яті ядра процесу. Це гарантує, що отримані метадані (тип файлу `st_mode`, ідентифікатор власника `st_uid`, розмір `st_size`, номер інода `st_ino`) точно належать тому об'єкту, з якого відбуватиметься подальше читання чи запис.
- **Прапорець `AT_SYMLINK_NOFOLLOW` у `fstatat`:** якщо кінцевий елемент шляху є символьним посиланням, функція не переходить за ним, а повертає метадані самого посилання (аналог застарілого `lstat`).
- **Прапорець `AT_EMPTY_PATH` (Linux 2.6.39+):** якщо рядок `pathname` є порожнім `""`, функція повертає метадані об'єкта, на який безпосередньо вказує `dirfd` (навіть якщо це дескриптор, відкритий з прапорцем `O_PATH`).

---

### 3. `fchmod()` та `fchown()` — зміна прав закріпленого об'єкта

Класичні виклики `chmod(path, mode)` та `chown(path, uid, gid)` є критично вразливими до підміни файлу між моментом створення та налаштуванням прав. Виклики з префіксом `f` виконують модифікацію за прямим дескриптором.

:::tabs
```c
#include <sys/stat.h>
#include <unistd.h>

int fchmod(int fd, mode_t mode);
int fchown(int fd, uid_t owner, gid_t group);
```
```cpp
#include <sys/stat.h>
#include <unistd.h>
#include <expected>
#include <system_error>

inline std::expected<void, std::error_code> set_permissions_safe(int fd, mode_t mode) {
    if (::fchmod(fd, mode) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

- **Безпековий ефект:** зміна атрибутів виконується атомарно на рівні інода файлової системи. Навіть якщо атакуючий процес перейменує файл у каталозі, права зміняться виключно на цільовому іноді жертви, не торкаючись підсунутих системних файлів.

---

### 4. `unlinkat()` — атомарне вилучення записів із каталогу

:::tabs
```c
#include <unistd.h>
#include <fcntl.h>

int unlinkat(int dirfd, const char *pathname, int flags);
```
```cpp
#include <unistd.h>
#include <fcntl.h>
#include <string_view>

inline int remove_entry_safe(int dirfd, std::string_view pathname, bool is_dir = false) {
    int flags = is_dir ? AT_REMOVEDIR : 0;
    return ::unlinkat(dirfd, pathname.data(), flags);
}
```
:::

- **Параметри:**
  - `flags = 0`: видаляє регулярний файл, символьне посилання, сокет або FIFO з каталогу `dirfd`.
  - `flags = AT_REMOVEDIR`: видаляє порожній каталог (еквівалент виклику `rmdir`).

---

### 5. `renameat2()` — атомарні операції перейменування та обміну (Linux 3.15+)

:::tabs
```c
#include <fcntl.h>
#include <stdio.h>

int renameat2(int olddirfd, const char *oldpath,
              int newdirfd, const char *newpath, unsigned int flags);
```
```cpp
#include <fcntl.h>
#include <string_view>

inline int safe_rename_no_replace(int olddirfd, std::string_view oldpath,
                                  int newdirfd, std::string_view newpath) {
    return ::renameat2(olddirfd, oldpath.data(), newdirfd, newpath.data(), RENAME_NOREPLACE);
}
```
:::

- **Прапорці безпеки `flags`:**
  - `RENAME_NOREPLACE`: гарантує, що файл `newpath` не буде перезаписано, якщо він уже існує. Якщо цільовий файл існує, виклик повертає помилку `EEXIST`. Це ліквідує гонку при збереженні тимчасових файлів на постійне місце.
  - `RENAME_EXCHANGE`: атомарно міняє місцями два існуючі файли `oldpath` та `newpath`. Обидва об'єкти повинні існувати на момент виклику. Операція гарантує, що не існуватиме жодного моменту часу, коли один із шляхів буде відсутній.

---

## Системний виклик `openat2()` та розширення безпеки Linux 5.6+

Для повного контролю над резолвінгом шляхів у контейнерах та пісочницях ядро Linux 5.6 ввело системний виклик `openat2()`.

:::tabs
```c
#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/openat2.h>
#include <unistd.h>

struct open_how {
    __u64 flags;        /* Стандартні прапорці O_RDONLY, O_CREAT тощо */
    __u64 mode;         /* Вісімкові права доступу */
    __u64 resolve;      /* Прапорці сімейства RESOLVE_* */
};

int openat2(int dirfd, const char *pathname,
            struct open_how *how, size_t size);
```
```cpp
#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/openat2.h>
#include <unistd.h>
#include <string_view>
#include <expected>
#include <system_error>

inline std::expected<int, std::error_code> open_beneath_safe(int dirfd, std::string_view path, uint64_t flags) {
    struct open_how how{};
    how.flags = flags;
    how.resolve = RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS;

    long fd = ::syscall(SYS_openat2, dirfd, path.data(), &how, sizeof(how));
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<int>(fd);
}
```
:::

### Прапорці резолвінгу (`RESOLVE_*`)

| Прапорець | Опис та безпековий ефект |
|---|---|
| `RESOLVE_BENEATH` | Забороняє вихід за межі дерева каталогу `dirfd`. Якщо шлях містить `..`, що ведуть вище `dirfd`, або абсолютне символьне посилання на зовнішній каталог, виклик завершується помилкою `EXDEV`. |
| `RESOLVE_IN_ROOT` | Трактує `dirfd` як корінь файлової системи для цього виклику (віртуальний `chroot` на один системний виклик). Будь-який абсолютний шлях або `..` за межі `dirfd` замикається на `dirfd`. |
| `RESOLVE_NO_SYMLINKS` | Забороняє слідування за будь-якими символьними посиланнями на всьому шляху (і проміжними, і кінцевим). У разі виявлення повертає `ELOOP`. |
| `RESOLVE_NO_MAGICLINKS` | Забороняє перехід за «магічними» посиланнями procfs (наприклад, `/proc/self/fd/N` або `/proc/self/exe`). |
| `RESOLVE_NO_XDEV` | Забороняє перетин меж точок монтування (mount points). |
| `RESOLVE_CACHED` | Дозволяє відкриття лише в тому випадку, якщо всі компоненти шляху вже є в dentry-кеші ядра, не викликаючи блокуючого введення-виведення на диск. |

---

## Спеціальні прапорці ядра для запобігання гонкам

### `O_NOFOLLOW`
Якщо останній компонент шляху `pathname` є символьним посиланням, виклик `openat()` не переходить за ним, а негайно повертає помилку `-1`, встановлюючи `errno = ELOOP`.

### `O_CREAT | O_EXCL`
Гарантує атомарне створення нового файлу. Якщо файл уже існує (або шлях вказує на чинне символьне посилання), виклик завершується помилкою `EEXIST`. Ядро виконує перевірку та створення як єдину неподільну транзакцію під внутрішніми блокуваннями VFS, повністю усуваючи простір для гонки станів.

### `O_PATH` (Linux 2.6.39+)
Відкриває дескриптор виключно для маніпуляцій на рівні дерева VFS (отримання метаданих через `fstat`, передача в якості `dirfd` для `openat`, зміна прав), не відкриваючи сам файл на читання чи запис. Дозволяє зафіксувати будь-який вузол (навіть символьне посилання чи спеціальний файл пристрою) без ризику блокування або виконання побічних ефектів драйвера пристрою.

### `O_TMPFILE` (Linux 3.11+)
Створює безіменний тимчасовий файл безпосередньо в іноді файлової системи, не створюючи жодного запису dentry у каталозі `dirfd`. Файл залишається невидимим для всіх сторонніх процесів у системі, унеможливлюючи будь-які атаки на основі імен або символьних посилань. Якщо після запису файл потрібно зберегти на постійній основі, процес викликає `linkat()` через `/proc/self/fd/N` для атомарної публікації в дереві каталогів.

---

## Таблиця типових кодів помилок (`errno`)

| Код помилки | Числове значення | Причина виникнення у захищених патернах |
|---|---|---|
| `EEXIST` | 17 | Спроба створити файл із прапорцями `O_CREAT \| O_EXCL` або `RENAME_NOREPLACE`, коли файл із таким ім'ям уже існує в каталозі. |
| `ELOOP` | 40 | Виявлено символьне посилання під час використання `O_NOFOLLOW` або `RESOLVE_NO_SYMLINKS`. |
| `EXDEV` | 18 | Спроба вийти за межі базового каталогу під час використання `RESOLVE_BENEATH` або `RESOLVE_NO_XDEV`. |
| `ENOTDIR` | 20 | Значення `dirfd` передано як дескриптор файлу, що не є каталогом, або вказано прапорець `O_DIRECTORY` для звичайного файлу. |
| `EACCES` | 13 | Ядро заблокувало відкриття згідно з політиками `fs.protected_symlinks`, `fs.protected_fifos` або правами доступу VFS. |
| `EBADF` | 9 | Передано недійсний файловий дескриптор `fd` або `dirfd`. |
| `EINVAL` | 22 | Передано некоректну комбінацію прапорців у `struct open_how` або несумісні прапорці відкриття. |
