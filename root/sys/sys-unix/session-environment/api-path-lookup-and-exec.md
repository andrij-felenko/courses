# 📋 Системні інтерфейси пошуку в PATH та виклики execvp

Цей довідник описує системні інтерфейси стандарту POSIX та C-бібліотеки (`libc`), які реалізують автоматичне розгортання змінної середовища `PATH`, перевірку прав виконання файлів у системі, а також утиліти та вбудовані команди оболонки для керування хеш-таблицею пошуку.

---

## 1. Системні виклики та функції C/C++ для пошуку у PATH

Стандартна бібліотека C надає сімейство функцій `exec`, які виконують обхід каталогів, перерахованих у змінній `PATH`, якщо передане ім'я виконуваного файлу не містить символу косої риски `/`.

### 1.1. Функції execvp(3) та execvpe(3)

Сигнатури функцій у заголовочному файлі `<unistd.h>`:

:::tabs
```c
#include <unistd.h>

/* Виконує файл із пошуком у PATH, успадковуючи поточне середовище environ */
int execvp(const char *file, char *const argv[]);

/* Розширення GNU/BSD: здійснює пошук у PATH, але передає явне середовище envp */
int execvpe(const char *file, char *const argv[], char *const envp[]);
```
```cpp
#include <unistd.h>
#include <vector>
#include <string>
#include <system_error>
#include <cerrno>

// Обгортка C++20 для безпечного виклику execvp з використанням RAII-контейнерів
[[noreturn]] void execute_in_path(const std::string& filename, const std::vector<std::string>& args) {
    std::vector<char*> c_argv;
    c_argv.reserve(args.size() + 1);
    for (const auto& arg : args) {
        c_argv.push_back(const_cast<char*>(arg.c_str()));
    }
    c_argv.push_back(nullptr);

    ::execvp(filename.c_str(), c_argv.data());

    // Якщо execvp повернув управління, виникла помилка
    throw std::system_error(errno, std::generic_category(), "execvp failed for " + filename);
}
```
:::

#### Повна детективна поведінка та алгоритм обробки помилок у `execvp`

Функція `execvp()` реалізує складний внутрішній цикл обходу каталогів з аналізом коди помилок, які повертаються системним викликом `execve()` для кожного знайденого файлу:

1. **Аналіз синтаксису імені**:
   Якщо параметр `file` містить хоча б один символ `/`, функція повністю відмовляється від обходу `PATH` і робить єдину спробу виконати `execve(file, argv, environ)`.

2. **Отримання масиву пошуку**:
   Функція зчитує змінну середовища `PATH` через `getenv("PATH")`. Якщо змінна `PATH` відсутня у середовищі поточного процесу (повертає `NULL`), `execvp` використовує дефолтну константу стандарту POSIX: `:_/usr/bin:/bin` (або системне значення `_CS_PATH`, яке можна отримати через системний виклик `sysconf(_SC_2_CBS_PATH)`).

3. **Цикл послідовного сканування та обробка кодів помилок `errno`**:
   `execvp` по черзі створює повні шляхи для кожного каталогу з `PATH` і намагається виконати системний виклик `execve()`. У цьому циклі ключову роль відіграє аналіз помилок:
   - `ENOENT` (Файл або каталог не існує): Функція ігнорує цю помилку і негайно переходить до наступного каталогу в `PATH`.
   - `ENOTDIR` (Компонент шляху не є каталогом): Помилка ігнорується, сканування триває.
   - `EACCES` (Відсутні права на виконання `X_OK` або читання каталогу): `execvp` запам'ятвує факт виникнення цієї помилки, але продовжує пошук у наступних каталогах. Якщо у наступних каталогах буде знайдено придатний виконуваний файл, він буде успішно запущений. Проте якщо весь список `PATH` вичерпано і жоден придатний бінарник не знайдено, `execvp` повертає управління з `errno = EACCES` (замість `ENOENT`), інформуючи розробника про те, що файл існував, але до нього не було доступу.
   - `ENOEXEC` (Помилка формату виконуваного файлу): Цей випадок є найцікавішим. Якщо файл існує і є виконуваним, але ядро повертає `ENOEXEC` (оскільки файл не містить магічного заголовка ELF `\x7fELF` або коректного шебангу `#!`), `execvp` припускає, що це класичний скрипт оболонки Bourne Shell. Функція створює новий масив аргументів, де першим елементом стає `"/bin/sh"`, другим — шлях до файлу, за яким ідуть решта `argv`, після чого повторно викликає `execve("/bin/sh", new_argv, environ)`.

4. **Кінцева помилка**:
   Якщо жоден з каталогів `PATH` не дав результату, функція повертає значення `-1`, а змінна `errno` встановлюється в `ENOENT` (або `EACCES`).

---

### 1.2. Перевірка доступності файлу: access(2) та faccessat(2)

Для перевірки права на виконання файлу перед його запуском ядро Linux надає системні виклики `access` та `faccessat`.

:::tabs
```c
#include <unistd.h>
#include <fcntl.h>

/* Перевірка прав виконання поточного процесу (X_OK) */
int is_executable(const char *path) {
    // AT_EACCESS змушує перевіряти ефективний UID/GID замість реального
    return faccessat(AT_FDCWD, path, X_OK, AT_EACCESS) == 0;
}
```
```cpp
#include <unistd.h>
#include <fcntl.h>
#include <filesystem>

// Перевірка виконання засобами C++17 std::filesystem та POSIX access
bool is_executable(const std::filesystem::path& path) {
    std::error_code ec;
    auto status = std::filesystem::status(path, ec);
    if (ec || !std::filesystem::is_regular_file(status)) {
        return false;
    }
    return ::faccessat(AT_FDCWD, path.c_str(), X_OK, AT_EACCESS) == 0;
}
```
:::

#### Проблема безпеки TOCTOU (Time-Of-Check to Time-Of-Use)

Під час розробки власного алгоритму розгортання `PATH` використання виклику `access()` чи `faccessat()` перед `execve()` створює часове вікно уразливості, відоме як TOCTOU:
- На кроці 1 програма перевіряє право виконання бінарника: `access("/tmp/app", X_OK) == 0`.
- Між кроком 1 та кроком 2 (викликом `execve()`) минають мікросекунди. За цей час інший процес у багатозадачному середовищі може підмінити файл `/tmp/app`, змінити його права або перетворити на символьне посилання.
- На кроці 2 програма викликає `execve()`, сподіваючись, що перевірені на кроці 1 умови залишаються дійсними.

З цієї причини створення високозахищеного софту вимагає мінімізації проміжних перевірок або використання атомних системних викликів з відкриттям дескрипторів та подальшим виконанням через `fexecve(int fd, char *const argv[], char *const envp[])`.

---

### 1.3. Виконання файлу з дескриптора: fexecve(3)

У сучасних системах Linux (починаючи з ядра 2.6.27 та glibc 2.11) доступний системний виклик `fexecve()`, який повністю усуває гонку станів TOCTOU:

:::tabs
```c
#include <unistd.h>
#include <fcntl.h>

int execute_via_fd(const char *path, char *const argv[], char *const envp[]) {
    // Відкриваємо файл лише для читання з прапорцем O_CLOEXEC
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        return -1;
    }
    // Запускаємо файл безпосередньо через дескриптор
    return fexecve(fd, argv, envp);
}
```
```cpp
#include <unistd.h>
#include <fcntl.h>
#include <filesystem>
#include <system_error>

void execute_via_fd(const std::filesystem::path& path, const std::vector<std::string>& args) {
    int fd = ::open(path.c_str(), O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "open failed for " + path.string());
    }
    std::vector<char*> c_argv;
    for (const auto& a : args) c_argv.push_back(const_cast<char*>(a.c_str()));
    c_argv.push_back(nullptr);

    ::fexecve(fd, c_argv.data(), environ);
    ::close(fd);
    throw std::system_error(errno, std::generic_category(), "fexecve failed");
}
```
:::

Виклик `fexecve()` використовує файлову систему `procfs` (вказуючи на `/proc/self/fd/N`), що гарантує виконання саме того файлу, який було відкрито в момент виклику `open()`.

---

## 2. Інтерфейси оболонки для маніпуляції PATH та кешуванням

Командна оболонка Bash та більшість POSIX-сумісних оболонок оптимізують обхід `PATH` за допомогою внутрішнього кешу — таблиці хешування шляхів.

### 2.1. Вбудована команда hash (Bash built-in)

Команда `hash` керує кешем знайдених абсолютних шляхів виконуваних файлів.

| Команда | Прапорці та параметри | Детальний опис та призначення |
| :--- | :--- | :--- |
| `hash` | *(без параметрів)* | Вивести поточний вміст хеш-таблиці з кількістю звернень (hits) та закешованими шляхами. |
| `hash -r` | `-r` (reset) | Повністю очистити хеш-таблицю оболонки, примушуючи наступні виклики виконувати повторне сканування `PATH`. |
| `hash -d <cmd>` | `-d` (delete) | Видалити з кешу лише конкретну команду `<cmd>`. |
| `hash -p /path <cmd>`| `-p` (path) | Примусово зафіксувати абсолютний шлях `/path` для імені `<cmd>` вмиваючи сканування `PATH`. |
| `hash -t <cmd>` | `-t` (target) | Вивести лише закешований абсолютний шлях команди (або видати помилку, якщо команда не кешована). |
| `hash -l` | `-l` (list) | Вивести вміст хеш-таблиці у форматі повторно виконуваних команд `hash -p ...`. |

### 2.2. Команди інспектування type, which, whereis, command, builtin

Для визначення того, як саме оболонка буде інтерпретувати введений рядок, використовуються наступні інструменти:

```bash
# 1. type — внутрішній аналізатор Bash (показує alias, builtin, function чи file)
$ type ls
ls is aliased to `ls --color=auto'

$ type cd
cd is a shell builtin

$ type grep
grep is hashed (/usr/bin/grep)

# 2. type -a — виводить УСІ можливі збіги в PATH, аліасах та вбудованих елементах
$ type -a echo
echo is a shell builtin
echo is /usr/bin/echo

# 3. command -v — стандартний POSIX-спосіб визначення типу команди (для використання у скриптах)
$ command -v git
/usr/bin/git

# 4. builtin — виклики команди, ігноруючи однойменні функції або псевдоніми
$ builtin cd /tmp

# 5. which — зовнішня утиліта (або builtin у zsh), яка шукає виключно у PATH
$ which grep
/usr/bin/grep

# 6. whereis — шукає бінарники, вихідні коди та man-сторінки у системних каталогах
$ whereis ls
ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz
```

---

## 3. PAM та файл системного середовища /etc/environment

На відміну від `/etc/profile`, файл `/etc/environment` **не є shell-скриптом**. Він обробляється модулем `pam_env.so` під час аутентифікації користувача в системі через PAM (Pluggable Authentication Modules).

### 3.1. Механізм обробки pam_env.so

Коли користувач проходить автентифікацію через `sshd`, `login`, `gdm` або `su`, системна бібліотека PAM послідовно викликає модулі, вказані у конфігурації `/etc/pam.d/`.

Модуль `pam_env.so` читає два конфігураційних файли:
1. `/etc/environment` — прості пари змінних.
2. `/etc/security/pam_env.conf` — файл розширених правил форматування змінних з можливістю підстановки значень за замовчуванням.

### 3.2. Синтаксис файлу /etc/environment

- Формат: лише пари `KEY=VALUE` або `KEY DEFAULT="val" OVERRIDE="val"`.
- Рядки, що починаються з символу `#`, ігноруються як коментарі.
- **Увага**: Підстановка змінних (наприклад `$PATH` або `export KEY=VAL`) у файлі `/etc/environment` **не підтримується**. Якщо записати `PATH=$PATH:/opt/bin`, змінна `PATH` буквально отримає рядок `"$PATH:/opt/bin"`, що зламає роботу оболонки.

### 3.3. Розширений синтаксис /etc/security/pam_env.conf

Для складання динамічних змінних середовища на рівні PAM використовується файл `pam_env.conf`:

```
# Формат: VARIABLE [DEFAULT=value] [OVERRIDE=value]
# Приклад безпечного формування PATH на рівні PAM:
PATH DEFAULT=/usr/local/bin:/usr/bin:/bin OVERRIDE=${PATH}
LANG DEFAULT=en_US.UTF-8
```

Це дозволяє виставити глобальні змінні середовища для всіх користувачів системи ще до того, як буде створено перший процес командної оболонки.

### 3.4. Особливості обробки PATH у системних демонах systemd

Системні сервіси, запущені через `systemd`, за замовчуванням **не зчитують** `/etc/profile` та `~/.bashrc`. Для них `systemd` виставляє власне мінімальне середовище: `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`.

Для налаштування змінних середовища конкретного демона у його unit-файлі використовуються спеціальні директиви:

```ini
[Unit]
Description=Custom Backend Service

[Service]
Type=simple
# Задання явного значення PATH та змінних середовища
Environment="PATH=/opt/myapp/bin:/usr/bin:/bin" "NODE_ENV=production"
# Завантаження з окремого файлу пар KEY=VALUE
EnvironmentFile=/etc/default/myapp
ExecStart=/opt/myapp/bin/server
```

Це забезпечує повне розмежування середовища між інтерактивними сеансами користувача та фоновими демонами операційної системи.
