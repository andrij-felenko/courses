# ⚙️ Програма дослідження шляхів бібліотек Multilib та Multiarch

Ця вставка містить практичну утиліту аналізу середовища виконання, яка програмно визначає архітектурну структуру поточного дистрибутиву Linux. Вона інспектує шляхи пошуку динамічного завантажувача (`ld.so`), перевіряє наявність каталогів Multilib (`/lib64`) та Multiarch (`/usr/lib/<triplet>`), досліджує карти пам'яті `/proc/self/maps`, перехоплює помилки бінарного класу ELF та показує роботу системного виклику `dlopen()` і низькорівневих внутрішніх структур `struct link_map`.

## 1. Архітектура та внутрішні механізми діагностичного інструменту

Для повного розуміння того, як динамічний завантажувач Linux (`ld.so`) обирає та мапить бібліотеки у віртуальний адресний простір процесу, інструмент діагностики реалізує чотири послідовні рівні аналізу:

### Крок 1: Аналіз бітності та моделі пам'яті процесу
Розрядність поточного бінарного файлу визначається оператором `sizeof(void*)`. На 32-бітних архітектурах x86 розмір вказівника становить 4 байти (32 біти, модель пам'яті ILP32), тоді як на 64-бітних архітектурах x86_64 або ARM64 розмір вказівника становить 8 байтів (64 біти, модель пам'яті LP64). Це фундаментальне число визначає, який саме завантажувач було використано для запуску програми (`/lib/ld-linux.so.2` чи `/lib64/ld-linux-x86-64.so.2`).

### Крок 2: Сканування файлової системи на наявність макетів
Утиліта сканує стандартні шляхи файлової системи Linux:
- **Перевірка макету Multilib (RPM):** Перевірка наявності каталогів `/lib64`, `/usr/lib64`, `/lib32` та `/usr/lib32`.
- **Перевірка макету Multiarch (Debian/GNU Triplets):** Перевірка наявності підкаталогів триплетів `/usr/lib/x86_64-linux-gnu`, `/usr/lib/i386-linux-gnu`, `/usr/lib/aarch64-linux-gnu` та `/usr/lib/arm-linux-gnueabihf`.

### Крок 3: Програмне витягування шляхів завантаження через `dlopen()` та `dlinfo()`
Під час динамічного зв'язування функція `dlopen()` передає запит до завантажувача `ld.so`. Завантажувач знаходить бібліотеку у системних каталогах, мапить її сторінки в адресний простір процесу через системний виклик `mmap()` і будує внутрішній зв'язаний список завантажених об'єктів — структуру `struct link_map`.

Використовуючи функцію `dlinfo()` із прапорцем `RTLD_DI_LINKMAP`, програма отримує прямий вказівник на структуру `struct link_map`, яка містить поле `l_name` — точний абсолютний шлях до відкритого shared object у файловій системі. Крім того, програма додатково аналізує вміст псевдофайлу `/proc/self/maps`, перевіряючи діапазони віртуальних адрес і текстові мітки відображених `.so` файлів.

### Крок 4: Аналіз сегментів пам'яті та релокацій у `/proc/self/maps`
Псевдофайл `/proc/self/maps` відображає таблицю віртуальної пам'яті ядра для поточного процесу. Для кожного завантаженого shared object у пам'яті створюється кілька відображень (vma — virtual memory area):
1. **Кодовий сегмент (text, прапорці `r-xp`):** Інструкції виконуваного коду бібліотеки із дозволом на виконання.
2. **Сегмент даних лише для читання (rodata / relro, прапорці `r--p`):** Таблиці констант та таблиці Global Offset Table (GOT) після завершення релокацій лінкером.
3. **Сегмент змінних даних (data / bss, прапорці `rw-p`):** Глобальні та статичні змінні бібліотеки.

Аналізуючи ці рядки, утиліта підтверджує, що бібліотека не просто існує на диску, а реально завантажена за відповідним абсолютним шляхом (у каталозі триплета або в `/usr/lib64`).

## 2. Реалізація утиліти у вихідному коді

Утиліту реалізовано двома мовами — ідіоматичною C та ідіоматичною C++17. Вкладка C++ використовує концепцію RAII для автоматичного управління хендлами `dlopen()`, безпечну роботу з файловою системою через `std::filesystem` та рядкові абстракції `std::string_view`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <link.h>
#include <sys/stat.h>
#include <unistd.h>

static void check_directory(const char *path, const char *description) {
    struct stat st;
    if (stat(path, &st) == 0 && S_ISDIR(st.st_mode)) {
        printf("  [+] Знайдено каталог: %-32s -> %s\n", path, description);
    } else {
        printf("  [-] Відсутній каталог: %-31s -> %s\n", path, description);
    }
}

static void inspect_loaded_library(const char *lib_name) {
    /* Відкриваємо динамічну бібліотеку через динамічний завантажувач ld.so */
    void *handle = dlopen(lib_name, RTLD_LAZY);
    if (!handle) {
        printf("  [!] Помилка dlopen(%s): %s\n", lib_name, dlerror());
        return;
    }

    /* Отримуємо вказівник на внутрішню структуру link_map завантажувача */
    struct link_map *map = NULL;
    if (dlinfo(handle, RTLD_DI_LINKMAP, &map) == 0 && map && map->l_name) {
        printf("  [=>] %s (dlinfo link_map) -> %s\n", lib_name, 
               map->l_name[0] ? map->l_name : "[впроваджено в процес]");
    } else {
        printf("  [!] Не вдалося отримати link_map для %s\n", lib_name);
    }

    /* Додатково перевіряємо карти пам'яті процесу через procfs */
    FILE *maps = fopen("/proc/self/maps", "r");
    if (maps) {
        char line[512];
        int found_in_maps = 0;
        while (fgets(line, sizeof(line), maps)) {
            if (strstr(line, lib_name) && strstr(line, ".so")) {
                char *path = strchr(line, '/');
                if (path) {
                    char *newline = strchr(path, '\n');
                    if (newline) *newline = '\0';
                    printf("  [=>] %s (/proc/self/maps) -> %s\n", lib_name, path);
                    found_in_maps = 1;
                    break;
                }
            }
        }
        fclose(maps);
        if (!found_in_maps) {
            printf("  [?] %s не знайдено серед файлових мапінгів /proc/self/maps\n", lib_name);
        }
    }

    dlclose(handle);
}

int main(void) {
    printf("=========================================================\n");
    printf("   ДІАГНОСТИКА АРХІТЕКТУРНОЇ ІЄРАРХІЇ БІБЛІОТЕК (C)\n");
    printf("=========================================================\n\n");

    printf("Параметри поточного бінарного процесу:\n");
    printf("  • Модель пам'яті: %s\n", sizeof(void *) == 8 ? "LP64 (64-біт)" : "ILP32 (32-біт)");
    printf("  • Розмір вказівника: %lu байтів\n\n", (unsigned long)sizeof(void *));

    printf("1. Перевірка наявності каталогів Multilib (RPM-модель):\n");
    check_directory("/lib64", "64-бітні бібліотеки системи");
    check_directory("/usr/lib64", "64-бітні бібліотеки користувача");
    check_directory("/lib32", "32-бітні бібліотеки системи (альтернативні)");
    check_directory("/usr/lib32", "32-бітні бібліотеки користувача (альтернативні)");
    printf("\n");

    printf("2. Перевірка наявності каталогів Multiarch (Debian GNU Triplets):\n");
    check_directory("/usr/lib/x86_64-linux-gnu", "x86_64-linux-gnu (AMD64 / Intel 64)");
    check_directory("/usr/lib/i386-linux-gnu", "i386-linux-gnu (x86 32-bit)");
    check_directory("/usr/lib/aarch64-linux-gnu", "aarch64-linux-gnu (ARM64)");
    check_directory("/usr/lib/arm-linux-gnueabihf", "arm-linux-gnueabihf (ARMhf)");
    printf("\n");

    printf("3. Тестування реальних шляхів резолюції бібліотек системним ld.so:\n");
    inspect_loaded_library("libm.so.6");
    inspect_loaded_library("libc.so.6");
    printf("\n=========================================================\n");

    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <memory>
#include <dlfcn.h>
#include <link.h>

namespace fs = std::filesystem;

// RAII обгортка для безпечного керування дескриптором dlopen
class DynamicLibrary {
private:
    void* handle_{nullptr};

public:
    explicit DynamicLibrary(std::string_view name) {
        handle_ = ::dlopen(name.data(), RTLD_LAZY);
    }

    ~DynamicLibrary() {
        if (handle_) {
            ::dlclose(handle_);
        }
    }

    DynamicLibrary(const DynamicLibrary&) = delete;
    DynamicLibrary& operator=(const DynamicLibrary&) = delete;

    DynamicLibrary(DynamicLibrary&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }

    DynamicLibrary& operator=(DynamicLibrary&& other) noexcept {
        if (this != &other) {
            if (handle_) ::dlclose(handle_);
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] bool is_loaded() const noexcept {
        return handle_ != nullptr;
    }

    [[nodiscard]] void* raw_handle() const noexcept {
        return handle_;
    }

    [[nodiscard]] std::string last_error() const {
        const char* err = ::dlerror();
        return err ? std::string(err) : std::string("невідома помилка");
    }
};

static void check_directory(const fs::path& path, std::string_view description) {
    std::error_code ec;
    if (fs::exists(path, ec) && fs::is_directory(path, ec)) {
        std::cout << "  [+] Знайдено каталог: " << path.string();
        if (path.string().length() < 30) {
            std::cout << std::string(30 - path.string().length(), ' ');
        }
        std::cout << " -> " << description << "\n";
    } else {
        std::cout << "  [-] Відсутній каталог: " << path.string();
        if (path.string().length() < 29) {
            std::cout << std::string(29 - path.string().length(), ' ');
        }
        std::cout << " -> " << description << "\n";
    }
}

static void inspect_loaded_library(std::string_view lib_name) {
    DynamicLibrary lib(lib_name);
    if (!lib.is_loaded()) {
        std::cout << "  [!] Помилка dlopen(" << lib_name << "): " << lib.last_error() << "\n";
        return;
    }

    // Запит структури link_map через dlinfo
    struct link_map* map = nullptr;
    if (::dlinfo(lib.raw_handle(), RTLD_DI_LINKMAP, &map) == 0 && map && map->l_name) {
        std::string_view path_view = map->l_name[0] ? map->l_name : "[впроваджено в процес]";
        std::cout << "  [=>] " << lib_name << " (dlinfo link_map) -> " << path_view << "\n";
    } else {
        std::cout << "  [!] Не вдалося отримати link_map для " << lib_name << "\n";
    }

    // Аналіз карт пам'яті /proc/self/maps
    std::ifstream maps("/proc/self/maps");
    if (!maps.is_open()) {
        std::cout << "  [!] Помилка відкриття /proc/self/maps\n";
        return;
    }

    std::string line;
    bool found = false;
    while (std::getline(maps, line)) {
        if (line.find(lib_name) != std::string::npos && line.find(".so") != std::string::npos) {
            auto pos = line.find('/');
            if (pos != std::string::npos) {
                std::string path = line.substr(pos);
                std::cout << "  [=>] " << lib_name << " (/proc/self/maps) -> " << path << "\n";
                found = true;
                break;
            }
        }
    }

    if (!found) {
        std::cout << "  [?] " << lib_name << " не знайдено серед мапінгів procfs\n";
    }
}

int main() {
    std::cout << "=========================================================\n";
    std::cout << "   ДІАГНОСТИКА АРХІТЕКТУРНОЇ ІЄРАРХІЇ БІБЛІОТЕК (C++17)\n";
    std::cout << "=========================================================\n\n";

    std::cout << "Параметри поточного бінарного процесу:\n";
    std::cout << "  • Модель пам'яті: " << (sizeof(void*) == 8 ? "LP64 (64-біт)" : "ILP32 (32-біт)") << "\n";
    std::cout << "  • Розмір вказівника: " << sizeof(void*) << " байтів\n\n";

    std::cout << "1. Перевірка наявності каталогів Multilib (RPM-модель):\n";
    check_directory("/lib64", "64-бітні бібліотеки системи");
    check_directory("/usr/lib64", "64-бітні бібліотеки користувача");
    check_directory("/lib32", "32-бітні бібліотеки системи (альтернативні)");
    check_directory("/usr/lib32", "32-бітні бібліотеки користувача (альтернативні)");
    std::cout << "\n";

    std::cout << "2. Перевірка наявності каталогів Multiarch (Debian GNU Triplets):\n";
    check_directory("/usr/lib/x86_64-linux-gnu", "x86_64-linux-gnu (AMD64 / Intel 64)");
    check_directory("/usr/lib/i386-linux-gnu", "i386-linux-gnu (x86 32-bit)");
    check_directory("/usr/lib/aarch64-linux-gnu", "aarch64-linux-gnu (ARM64)");
    check_directory("/usr/lib/arm-linux-gnueabihf", "arm-linux-gnueabihf (ARMhf)");
    std::cout << "\n";

    std::cout << "3. Тестування реальних шляхів резолюції бібліотек системним ld.so:\n";
    inspect_loaded_library("libm.so.6");
    inspect_loaded_library("libc.so.6");
    std::cout << "\n=========================================================\n";

    return 0;
}
```
:::

## 3. Інструкція з збирання, виконання та аналізу виводу

Для компіляції C-версії використовуйте компілятор `gcc` з прапорцем `-ldl` для зв'язування з бібліотекою динамічного завантажувача:

```bash
gcc -O2 -Wall proj-multiarch-probe.c -o probe_c -ldl
./probe_c
```

Для компіляції C++-версії потрібен компілятор із підтримкою стандарту C++17 або вище:

```bash
g++ -O2 -std=c++17 -Wall proj-multiarch-probe.cpp -o probe_cpp -ldl
./probe_cpp
```

### Аналіз результатів виконання у різних дистрибутивах:

1. **На дистрибутивах Ubuntu / Debian (Multiarch):**
   Вивід утиліти зафіксує відсутність `/lib64` як самостійного місця збереження бібліотек (у нових випусках `/lib64` є лише симлінком на завантажувач `/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2`) та покаже наявність каталогів `/usr/lib/x86_64-linux-gnu`. Виклики `dlopen("libm.so.6")` повернуть абсолютний шлях `/lib/x86_64-linux-gnu/libm.so.6`.

2. **На дистрибутивах Fedora / RHEL / CentOS (Multilib):**
   Вивід утиліти покаже наявність `/usr/lib64` та відсутність триплетних каталогів у `/usr/lib/`. Завантажувач резолвитиме `libm.so.6` за шляхом `/usr/lib64/libm.so.6`.

3. **Тестування 32-бітного режиму компіляції (при встановленому 32-бітному стекі):**
   Якщо у вашій системі встановлено `gcc-multilib` або `g++-multilib`, зберіть утиліти з прапорцем `-m32`:
   ```bash
   gcc -m32 -O2 -Wall proj-multiarch-probe.c -o probe_c32 -ldl
   ./probe_c32
   ```
   Програма виведе `ILP32 (32-біт)` та розмір вказівника `4 байти`. У середовищі Multiarch `dlopen()` поверне шлях `/lib/i386-linux-gnu/libm.so.6`, а в середовищі Multilib — `/usr/lib/libm.so.6`.

## 4. Глибокий розбір внутрішньої структури `link_map` та діагностика через `LD_DEBUG`

Під час виклику `dlinfo(handle, RTLD_DI_LINKMAP, &map)` завантажувач повертає вказівник на елемент внутрішнього двобічно зв'язаного списку ядра лінкера. Структура `struct link_map` оголошена в заголовковому файлі `<link.h>` і має такий базовий вигляд:

```c
struct link_map {
    ElfW(Addr) l_addr;       /* Різниця між адресою у ELF-файлі та адресою у RAM */
    char *l_name;            /* Абсолютний шлях до файлу shared object */
    ElfW(Dyn) *l_ld;         /* Вказівник на динамічну секцію .dynamic */
    struct link_map *l_next; /* Наступний завантажений модуль у ланцюжку */
    struct link_map *l_prev; /* Попередній завантажений модуль у ланцюжку */
};
```

Значення `l_name` прямо відображає підсумковий вибір системного завантажувача. Якщо бібліотеку було завантажено з клейшу `/etc/ld.so.cache`, `l_name` міститиме точний шлях із триплетом або суфіксом `64`, підтверджуючи коректність роботи конфігурації Multilib або Multiarch.

Для простеження покрокової роботи динамічного завантажувача під час пошуку бібліотек ви можете запустити скомпільовану утиліту із встановленою змінною оточення `LD_DEBUG=libs`:

```bash
LD_DEBUG=libs ./probe_c
```

Утиліта виведе повний журнал трасування завантажувача:
- Список каталогів, обстежених у пошуках кожного shared object.
- Перевірку відповідності ELF-класу (`ELFCLASS64` чи `ELFCLASS32`).
- Відкриття бінарного кешу `/etc/ld.so.cache` та фінальне відображення пам'яті через `mmap()`.

Це трасування дозволяє наочно побачити відмінність між кроками резолюції бібліотек у системі Multilib (де пошук переходить від `LD_LIBRARY_PATH` до `/usr/lib64`) та у системі Multiarch (де завантажувач звертається до триплетного каталогу `/usr/lib/x86_64-linux-gnu`).

## 5. Обробка крайових випадків та відловлювання помилок сумісності

Під час роботи з динамічним завантажувачем `dlopen()` розробники часто стикаються з трьома основними класами крайових випадків у двоархітектурних середовищах:

1. **Конфлікт бінарного класу ELF (`wrong ELF class`):**
   Якщо 64-бітний процес передає у `dlopen()` шлях до 32-бітної бібліотеки (наприклад `/usr/lib/libz.so.1` у системі Multilib), виклик повертає `NULL`. Функція `dlerror()` повертає рядок із поясненням: `wrong ELF class: ELFCLASS32`. Важливо пам'ятати, що `dlerror()` має семантику зі скиданням буфера: перший виклик повертає рядок помилки, а наступний виклик одразу повертає `NULL`.

2. **Вплив прапорців `RTLD_LAZY` та `RTLD_NOW`:**
   Прапорець `RTLD_LAZY` відкладає зв'язування символів точок входу до моменту їх першого виклику через Procedure Linkage Table (PLT). Прапорець `RTLD_NOW` вимагає від завантажувача негайно дозволити всі символи під час виклику `dlopen()`. Якщо бібліотека залежить від інородної версії іншої бібліотеки, виклик з `RTLD_NOW` відразу виявить помилку сумісності.

3. **Безпека потоків та багатопотокове завантаження:**
   У багатопотокових програмах виклики `dlopen()` та `dlinfo()` захищені внутрішніми м'ютексами завантажувача `ld.so`. Однак доступ до системного файлу `/proc/self/maps` є неатомарним: якщо паралельний потік динамічно завантажує або вивантажує бібліотеку через `dlclose()`, читання карти пам'яті може зафіксувати тимчасовий стан відображень віртуальних сторінок.
