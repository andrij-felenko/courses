# 📋 API виконання процесів і маніпуляції оточенням

Ця довідка містить вичерпний специфікаційний контракт системних функцій та інтерфейсів POSIX і Linux для запуску нових процесів, читання й модифікації змінних середовища, а також роботи з допоміжним вектором ядра. Інтерфейси виконання процесів є основним засобом системного програмування для трансформації поточного процесу в нову програму з передачею контексту через аргументи, середовище та метадані ELF.

## 1. Родина функцій exec()

Функції родини `exec()` замінюють поточний образ процесу новим виконуваним файлом. У разі успішного виклику жодна з функцій родини `exec()` не повертає керування викликаючому коду, оскільки кодова секція, купа та стек викликаючого процесу повністю заміщуються сегментами завантаженого виконуваного файлу.

### 1.1. Класифікація та сигнатури функцій

Усі функції родини `exec()` є обгортками над базовими системними викликами ядра Linux `sys_execve` та `sys_execveat`. Назва кожної функції відображає її суфіксальну специфіку:
- **`v`** (vector): Аргументи передаються у вигляді масиву покажчиків (`char *const argv[]`).
- **`l`** (list): Аргументи передаються у вигляді списку аргументів у варіативній функції (`const char *arg0, const char *arg1, ..., NULL`).
- **`p`** (PATH): Якщо ім'я файлу не містить косої риски `/`, функція виконує пошук виконуваного файлу у каталогах, перелічених у змінній середовища `PATH`.
- **`e`** (environment): Розробник явно передає масив змінних середовища (`char *const envp[]`). Якщо суфікса `e` немає, функція використовує поточне глобальне середовище `environ`.
- **`f`** (descriptor): Запуск виконуваного файлу здійснюється через відкритий файловий дескриптор, а не через шлях у файловій системі.

:::tabs
```c
/* POSIX Сигнатури C */
#include <unistd.h>

int execve(const char *pathname, char *const argv[], char *const envp[]);
int execv(const char *pathname, char *const argv[]);
int execvp(const char *file, char *const argv[]);
int execvpe(const char *file, char *const argv[], char *const envp[]);
int execl(const char *pathname, const char *arg0, ... /*, (char *)0 */);
int execlp(const char *file, const char *arg0, ... /*, (char *)0 */);
int execle(const char *pathname, const char *arg0, ... /*, (char *)0, char *const envp[] */);
int fexecve(int fd, char *const argv[], char *const envp[]);
```
```cpp
// C++ POSIX Сигнатури у просторі імен extern "C"
#include <unistd.h>

extern "C" {
int execve(const char *pathname, char *const argv[], char *const envp[]);
int execv(const char *pathname, char *const argv[]);
int execvp(const char *file, char *const argv[]);
int execvpe(const char *file, char *const argv[], char *const envp[]);
int execl(const char *pathname, const char *arg0, ...);
int execlp(const char *file, const char *arg0, ...);
int execle(const char *pathname, const char *arg0, ...);
int fexecve(int fd, char *const argv[], char *const envp[]);
}
```
:::

### 1.2. Механіка fexecve() та системний виклик execveat()

Функція `fexecve()` була додана до стандарту POSIX.1-2008 для розв'язання фундаментальної проблеми безпеки: усунення "стану гонки" (time-of-check to time-of-use, TOCTOU) при відкритті й виконанні файлів. При звичайному виклику `execve("/usr/bin/app", ...)` шкідливий процес може підмінити файл між миттю перевірки прав та миттю передачі керування ядру.

За допомогою `fexecve()` програма спочатку відкриває файл із прапорцями `O_RDONLY` або `O_PATH` та перевіряє його криптографічний геш чи криптографічний підпис. Після цього відкритий дескриптор `fd` передається у `fexecve()`. У системі Linux C-бібліотека реалізує `fexecve()` через звернення до віртуальної файлової системи procfs: вона викликає `execve()` для шляху `/proc/self/fd/<fd>`.

Починаючи з ядра Linux 3.19, операційна система надає прямого нативного системного виклику `execveat()`, який розширює концепцію відносних шляхів `openat()`:

:::tabs
```c
/* Сигнатура execveat C */
#include <unistd.h>
#include <fcntl.h>

int execveat(int dirfd, const char *pathname,
             char *const argv[], char *const envp[],
             int flags);
```
```cpp
// C++ Сигнатура execveat
#include <unistd.h>
#include <fcntl.h>

extern "C" {
int execveat(int dirfd, const char *pathname,
             char *const argv[], char *const envp[],
             int flags);
}
```
:::

Якщо у `execveat()` передано `pathname` як порожній рядок `""` та встановлено прапорець `AT_EMPTY_PATH`, ядро виконує безпосередньо файл, на який вказує `dirfd`, уникаючи додаткових звернень до procfs.

### 1.3. Детальний опис параметрів

- `pathname`: Повний або відносний шлях у файловій системі до виконуваного файлу ELF або скрипту зі строкою інтерпретатора `#!`.
- `file`: Ім'я файлу для пошуку. Якщо `file` містить символ `/`, він розглядається як звичайний шлях і пошук у `PATH` не виконується.
- `fd`: Відкритий файловий дескриптор виконуваного файлу. Дескриптор повинен бути відкритий у режимі тільки для читання (`O_RDONLY` або `O_PATH`). Це критично для захисту від атак типу "race condition" (TOCTOU), коли файл може бути замінений у файловій системі між перевіркою та запуском.
- `argv`: Null-термінований масив покажчиків на символьні рядки аргументів. Перший елемент `argv[0]` за домовленістю містить ім'я програми.
- `envp`: Null-термінований масив покажчиків на рядки `KEY=VALUE`, що формують оточення нового процесу.

### 1.4. Специфікація помилок (errno) та крайові випадки

Якщо системний виклик `execve()` повертає значення `-1`, це свідчить про помилку запуску. Оскільки старий образ процесу не був замінений, програма продовжує виконання й повинна проаналізувати значення змінної `errno`:

- `E2BIG`: Сумарний обсяг байтів у масивах `argv` та `envp` разом із покажчиками перевищує системний ліміт `ARG_MAX`.
- `EACCES`: Відсутні права на виконання файлу, права на читання файлу або права на пошук в одному з батьківських каталогів шляху.
- `ENOENT`: Вказаний файл не існує, або не існує інтерпретатор, вказаний після `#!` у першому рядку скрипту.
- `ENOEXEC`: Файл має нерозпізнаний бінарний формат (не є коректним ELF-файлом і не містить сигнатури `#!`).
- `ETXTBSY`: Виконуваний файл відкритий на запис хоча б одним процесом у системі. Ядро Linux блокує запуск файлів, які в цей момент модифікуються.
- `ENAMETOOLONG`: Довжина шляху `pathname` перевищує `PATH_MAX` (4096 байтів) або довжина окремого компонента шляху перевищує `NAME_MAX` (255 байтів).
- `ENOMEM`: Недостатньо оперативної пам'яті ядра для виділення нових сторінок під початковий стек або відображення сегментів ELF.
- `EFAULT`: Покажчик `pathname`, `argv` або `envp` вказує за межі доступного віртуального адресного простору процесу.

---

## 2. Управління змінними середовища у просторі користувача

Змінні середовища є глобальним масивом рядків `KEY=VALUE`, доступним для всього процесу. З точки зору C-бібліотеки, цей масив представляє собою суцільний список покажчиків, закінчений `NULL`.

### 2.1. Сигнатури функцій POSIX

:::tabs
```c
/* C POSIX Інтерфейс середовища */
#include <stdlib.h>

extern char **environ;

char *getenv(const char *name);
int setenv(const char *name, const char *value, int overwrite);
int unsetenv(const char *name);
int putenv(char *string);
int clearenv(void);
```
```cpp
// C++ Інтерфейс середовища stdlib.h / cstdlib
#include <cstdlib>

extern "C" {
extern char **environ;

char *getenv(const char *name);
int setenv(const char *name, const char *value, int overwrite);
int unsetenv(const char *name);
int putenv(char *string);
int clearenv(void);
}
```
:::

### 2.2. Правила роботи та багатопоточна безпека

- `getenv(name)`: Виконує лінійний пошук у масиві `environ`. Якщо змінну знайдено, повертає покажчик на символ одразу після `=`. Модифікувати повернутий рядок заборонено. Функція є потокобезпечною для читання, але викликає стан гонки (data race), якщо інший потік паралельно викликає `setenv()` або `putenv()`.
- `setenv(name, value, overwrite)`: Якщо змінна `name` вже існує і `overwrite == 0`, функція завершується успішно без змін. Якщо `overwrite != 0` або змінна відсутня, функція виділяє нову пам'ять за допомогою `malloc()`, копіює туди ключ і значення у форматі `KEY=VALUE` і оновлює масив `environ`.
- `unsetenv(name)`: Шукає всі входження ключа `name` у масиві `environ` і вилучає покажчики на них, зсуваючи наступні елементи масиву вліво. Пам'ять самих рядків при цьому не вивільняється (щоб уникнути пошкодження чужих покажчиків).
- `putenv(string)`: Вставляє покажчик на рядок `string` напряму у масив `environ` без копіювання. **Пастка**: Якщо рядок `string` був виділений на стеку локальної функції, після виходу з цієї функції покажчик в `environ` стане завислим (dangling pointer), що призведе к падінню програми.
- `clearenv()`: Очищує середовище, встановлюючи `environ = NULL` або вказуючи на порожній масив. Використовується в демонах безпеки перед формуванням повністю контрольованого середовища.

У багатопотокових програмах модифікувати змінна середовища через `setenv()` чи `putenv()` під час виконання робочих потоків вкрай не рекомендується, оскільки стандарт POSIX не вимагає внутрішнього блокування мутексом функції `getenv()`. Якщо один потік читає середовище через `getenv()`, а второй реалокує масив `environ` через `setenv()`, процес із високою ймовірністю впаде через звернення за недійсним покажчиком (use-after-free).

---

## 3. Допоміжний вектор ядра (Auxiliary Vector)

Допоміжний вектор `auxv` забезпечує передачу низькорівневої інформації від ядра Linux до простору користувача без виконання додаткових системних викликів.

### 3.1. Інтерфейс getauxval()

:::tabs
```c
/* C getauxval */
#include <sys/auxv.h>

unsigned long getauxval(unsigned long type);
```
```cpp
// C++ getauxval
#include <sys/auxv.h>

extern "C" {
unsigned long getauxval(unsigned long type);
}
```
:::

Якщо вказаний тип `type` присутній у допоміжному векторі поточного процесу, `getauxval()` повертає його значення. Якщо тип відсутній, функція повертає `0` і встановлює `errno` у `ENOENT`.

### 3.2. Повний реєстр типом AT_*

Нижче наведено докладне пояснення системного призначення елементів допоміжного вектора:

- **`AT_NULL` (0)**: Маркер завершення допоміжного вектора. Динамічний лінкер зупиняє сканування стека при виявленні цього елемента.
- **`AT_IGNORE` (1)**: Запис, який слід ігнорувати завантажувачу. Використовується для вилучення записів у ядерних патчах.
- **`AT_EXECFD` (2)**: Файловий дескриптор інтерпретатора, якщо програма була завантажена безпосередньо через відкритий дескриптор.
- **`AT_PHDR` (3)**: Вказівник на таблицю програмних заголовків ELF (Program Headers) у віртуальній пам'яті. Дозволяє `ld.so` розібрати структури сегментів.
- **`AT_PHENT` (4)**: Розмір одного програмного заголовка ELF у байтах (зазвичай 56 байтів на 64-бітних системах).
- **`AT_PHNUM` (5)**: Загальна кількість програмних заголовков у таблиці ELF.
- **`AT_PAGESZ` (6)**: Розмір сторінки віртуальної пам'яті в байтах (наприклад, 4096 байтів). Використовується C-бібліотекою для вирівнювання запитів `mmap`.
- **`AT_BASE` (7)**: Базова адреса завантаження самого динамічного лінкера (`ld.so`) у пам'яті.
- **`AT_FLAGS` (8)**: Процесорні прапорці, передані ядром.
- **`AT_ENTRY` (9)**: Адреса точки входу в програму користувача (символ `_start`). Куди лінкер передає керування після налаштування бібліотек.
- **`AT_NOTELF` (10)**: Вказує, що бінарний файл не є стандартом ELF.
- **`AT_UID` (11)**: Реальний ідентифікатор користувача (Real UID) процесу.
- **`AT_EUID` (12)**: Ефективний ідентифікатор користувача (Effective UID) процесу.
- **`AT_GID` (13)**: Реальний ідентифікатор групи (Real GID) процесу.
- **`AT_EGID` (14)**: Ефективний ідентифікатор групи (Effective GID) процесу.
- **`AT_CLKTCK` (17)**: Частота системного таймера (кількість тактів на секунду, зазвичай 100). Потрібна функціям `times()`.
- **`AT_PLATFORM` (15)**: Вказівник на рядок архітектури процесора (наприклад, `"x86_64"`).
- **`AT_HWCAP` (16)**: Бітова маска апаратних можливостей CPU (SSE, AVX, AES тощо). Дозволяє glibc прозоро обирати оптимізовані версії `memcpy`.
- **`AT_HWCAP2` (26)**: Додаткова бітова маска нових розширень процесора (AVX512, AMX).
- **`AT_SECURE` (23)**: Прапорець безпеки: `1`, якщо запуск відбувся через SetUID/SetGID або з системними capabilities.
- **`AT_RANDOM` (25)**: Вказівник на 16 випадкових байтів від ядрового CSPRNG для ініціалізації канарейки стека (`__stack_chk_guard`).
- **`AT_EXECFN` (31)**: Вказівник на повне ім'я виконуваного файлу, передане у виклику `execve()`.

---

## 4. Приклади використання на мовах C та C++

Наведені нижче приклади демонструють створення ізольованого середовища виконання та інспектування системних атрибутів процесу.

:::tabs
```c
/* Приклад на мові C: Ізольований запуск процесу з перевіркою помилок execve */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/auxv.h>

void print_system_auxv(void) {
    unsigned long page_size = getauxval(AT_PAGESZ);
    unsigned long entry_addr = getauxval(AT_ENTRY);
    unsigned long is_secure = getauxval(AT_SECURE);
    const char *platform = (const char *)getauxval(AT_PLATFORM);

    printf("=== System Auxiliary Vector Info ===\n");
    printf("Page Size   : %lu bytes\n", page_size);
    printf("Entry Point : 0x%lx\n", entry_addr);
    printf("Secure Mode : %lu\n", is_secure);
    printf("Platform    : %s\n\n", platform ? platform : "unknown");
}

int main(void) {
    print_system_auxv();

    /* Формування чітко контрольованого середовища */
    char *custom_env[] = {
        "PATH=/usr/bin:/bin",
        "LANG=C.UTF-8",
        "SECURE_TOKEN=xyz12345",
        NULL
    };

    /* Аргументи запуску команди /usr/bin/env */
    char *custom_argv[] = {
        "env",
        NULL
    };

    printf("Launching /usr/bin/env with controlled environment...\n");
    fflush(stdout);

    execve("/usr/bin/env", custom_argv, custom_env);

    /* Код після execve виконується ТІЛЬКИ в разі помилки */
    int err = errno;
    fprintf(stderr, "Failed to execute execve: %s (errno: %d)\n", strerror(err), err);

    if (err == ENOENT) {
        fprintf(stderr, "Error: Binary /usr/bin/env not found.\n");
    } else if (err == E2BIG) {
        fprintf(stderr, "Error: Environment or argument list too large.\n");
    }

    return EXIT_FAILURE;
}
```
```cpp
// Приклад на мові C++20: RAII-обгортка для формування середовища та запуску
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span >
#include <system_error>
#include <unistd.h>
#include <sys/auxv.h>

class EnvironmentContainer {
public:
    void add_variable(std::string_view key, std::string_view value) {
        std::string entry;
        entry.reserve(key.size() + 1 + value.size());
        entry.append(key).append("=").append(value);
        storage_.push_back(std::move(entry));
    }

    [[nodiscard]] std::vector<char*> get_c_pointers() {
        std::vector<char*> pointers;
        pointers.reserve(storage_.size() + 1);
        for (auto& str : storage_) {
            pointers.push_back(str.data());
        }
        pointers.push_back(nullptr);
        return pointers;
    }

private:
    std::vector<std::string> storage_;
};

int main() {
    // Зчитування auxv через C++ API
    auto page_size = getauxval(AT_PAGESZ);
    auto secure_mode = getauxval(AT_SECURE);

    std::cout << "=== C++ Process Bootstrap Info ===\n";
    std::cout << "Page Size: " << page_size << " bytes\n";
    std::cout << "AT_SECURE: " << secure_mode << "\n\n";

    EnvironmentContainer env_box;
    env_box.add_variable("PATH", "/usr/bin:/bin");
    env_box.add_variable("APP_MODE", "PRODUCTION");
    env_box.add_variable("CPP_VERSION", "202002L");

    auto envp = env_box.get_c_pointers();

    std::vector<std::string> arg_strings = {"env"};
    std::vector<char*> argv = {arg_strings[0].data(), nullptr};

    ::execve("/usr/bin/env", argv.data(), envp.data());

    // Обробка помилок
    int error_code = errno;
    std::system_error sys_err(error_code, std::generic_category());
    std::cerr << "Execution failed: " << sys_err.what() << '\n';

    return EXIT_FAILURE;
}
```
:::
