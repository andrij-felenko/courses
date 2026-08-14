# ⚙️ Практика: перехоплення викликів та динамічне завантаження коду

Ця практична вставка детально розбирає два фундаментальні системні прийоми роботи з динамічним лінкуванням у Linux: створення розширюваної системи плагінів із явним завантаженням модулів під час виконання (`dlopen`/`dlsym`) та механізм неінвазивного перехоплення системних функцій за допомогою технології `LD_PRELOAD`.

---

## Завдання 1: Розширювана система динамічних плагінів (dlopen / dlsym)

Динамічна система плагінів дозволяє розширювати функціональність додатків без їхньої перекомпіляції. Програма-господар (host application) під час роботи сканує каталог із `.so` файлами, завантажує їх у свій віртуальний адресний простір, отримує вказівники на функції та викликає їх.

### Механіка роботи та проектування бінарного інтерфейсу (ABI)

Щоб програма-господар могла знайти та викликати функцію з динамічно завантаженого плагіна, плагін мусить експортувати інтерфейс із відомим і стабільним C ABI (Application Binary Interface). 

У мові C++ компілятор за замовчуванням виконує декорування імен (Name Mangling) для підтримки перевантаження функцій та шаблонів. Наприклад, функція `void process(const char*)` у C++ перетворюється компілятором `g++` на символ `_Z7processPKc`. Якщо програма-господар виконуватиме пошук символу `dlsym(handle, "process")`, вона отримає помилку `NULL`, оскільки в таблиці динамічних символів `.dynsym` символ із такою назвою відсутній.

Для запобігання декоруванню імен у C++ використовується специфікатор `extern "C"`. Він наказує компілятору C++ зберігати символ у таблиці `.dynsym` у незмінному стилі C (`process`).

Крім того, плагіни часто потребують виконання коду під час завантаження в пам'ять (наприклад, для виділення ресурсів) та під час вивантаження з пам'яті (для очищення). У мові C для цього використовуються атрибути GCC `__attribute__((constructor))` та `__attribute__((destructor))`. У C++ відповідна логіка реалізується через глобальні конструктори та деструктори об'єктів із статичною тривалістю зберігання.

### Крок 1. Код плагіна (libplugin)

Нижче наведено код плагіна, який містить ініціалізатор, фіналізатор та експортовану функцію обробки даних, скомпільований у спільновживаний об'єкт `libplugin.so`.

:::tabs
```c
/* plugin.c — C-реалізація плагіна з конструктором та деструктором */
#include <stdio.h>

/* Функція ініціалізації: викликається при dlopen */
__attribute__((constructor))
static void plugin_init(void) {
    printf("[Plugin C] Ініціалізація модуля (constructor)...\n");
}

/* Функція фіналізації: викликається при dlclose */
__attribute__((destructor))
static void plugin_fini(void) {
    printf("[Plugin C] Завершення роботи модуля (destructor)...\n");
}

/* Експортована функція з C ABI */
void plugin_process(const char *input) {
    printf("[Plugin C] Обробка вхідних даних: %s\n", input);
}
```
```cpp
// plugin.cpp — Ідіоматична C++ реалізація плагіна з extern "C"
#include <iostream>
#include <string_view>

namespace {
    // Глобальний об'єкт: конструктор викликається при dlopen, деструктор — при dlclose
    struct PluginInitializer {
        PluginInitializer() {
            std::cout << "[Plugin C++] Ініціалізація модуля (RAII Init)...\n";
        }
        ~PluginInitializer() {
            std::cout << "[Plugin C++] Завершення роботи модуля (RAII Cleanup)...\n";
        }
    };

    PluginInitializer g_init;
}

extern "C" void plugin_process(const char* input) {
    std::cout << "[Plugin C++] Обробка вхідних даних: " << input << '\n';
}
```
:::

Команда збірки плагіна у спільновживаний об'єкт:
```bash
# Збірка C-версії:
gcc -fPIC -shared plugin.c -o libplugin.so

# Збірка C++ версії:
g++ -fPIC -shared plugin.cpp -o libplugin.so
```

### Крок 2. Код програми-господаря (Host Application)

Програма-господар відкриває бібліотеку за допомогою `dlopen`, перевіряє наявність помилок через `dlerror`, знаходить адресу потрібної функції через `dlsym`, викликає її і вивантажує бібліотеку через `dlclose`.

У C++ версії ми загортаємо небезпечний сирий дескриптор `void*` у розумний вказівник `std::unique_ptr` із кастомним делітером. Це гарантує автоматичний виклик `dlclose()` навіть у разі виникнення винятків у коді господарської програми.

:::tabs
```c
/* main.c — C-реалізація динамічного завантаження плагіна */
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

/* Тип вказівника на функцію плагіна */
typedef void (*plugin_func_t)(const char *);

int main(int argc, char *argv[]) {
    const char *plugin_path = "./libplugin.so";
    if (argc > 1) {
        plugin_path = argv[1];
    }

    /* 1. Динамічне відкриття бібліотеки */
    void *handle = dlopen(plugin_path, RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        fprintf(stderr, "Помилка завантаження %s: %s\n", plugin_path, dlerror());
        return EXIT_FAILURE;
    }

    /* Скидаємо попередній стан помилок */
    dlerror();

    /* 2. Пошук адреси символу */
    plugin_func_t process_func = (plugin_func_t)dlsym(handle, "plugin_process");
    const char *dlsym_err = dlerror();
    if (dlsym_err != NULL) {
        fprintf(stderr, "Символ plugin_process не знайдено: %s\n", dlsym_err);
        dlclose(handle);
        return EXIT_FAILURE;
    }

    /* 3. Виклик функції плагіна */
    process_func("Тестовий пакет даних C");

    /* 4. Закриття дескриптора */
    dlclose(handle);
    return EXIT_SUCCESS;
}
```
```cpp
// main.cpp — Ідіоматична C++ RAII-обгортка для завантаження плагіна
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <dlfcn.h>

// RAII deleter для автоматичного виклику dlclose
struct DlHandleDeleter {
    void operator()(void* handle) const noexcept {
        if (handle) {
            dlclose(handle);
        }
    }
};

using UniqueDlHandle = std::unique_ptr<void, DlHandleDeleter>;

class DynamicPlugin {
public:
    static std::expected<DynamicPlugin, std::string> load(std::string_view path) {
        void* raw_handle = dlopen(path.data(), RTLD_NOW | RTLD_LOCAL);
        if (!raw_handle) {
            const char* err = dlerror();
            return std::unexpected(err ? err : "Невідома помилка dlopen");
        }

        return DynamicPlugin(UniqueDlHandle(raw_handle));
    }

    template <typename FuncSig>
    std::expected<FuncSig*, std::string> get_symbol(std::string_view symbol_name) const {
        dlerror(); // Скидаємо попередній стан помилок
        void* sym = dlsym(m_handle.get(), symbol_name.data());
        const char* err = dlerror();
        if (err != nullptr) {
            return std::unexpected(err);
        }
        return reinterpret_cast<FuncSig*>(sym);
    }

private:
    explicit DynamicPlugin(UniqueDlHandle handle) : m_handle(std::move(handle)) {}
    UniqueDlHandle m_handle;
};

int main(int argc, char* argv[]) {
    std::string_view plugin_path = (argc > 1) ? argv[1] : "./libplugin.so";

    auto plugin_result = DynamicPlugin::load(plugin_path);
    if (!plugin_result) {
        std::cerr << "Помилка завантаження плагіна: " << plugin_result.error() << '\n';
        return EXIT_FAILURE;
    }

    auto& plugin = *plugin_result;
    using ProcessFn = void(const char*);
    
    auto func_result = plugin.get_symbol<ProcessFn>("plugin_process");
    if (!func_result) {
        std::cerr << "Помилка пошуку символу: " << func_result.error() << '\n';
        return EXIT_FAILURE;
    }

    auto process_func = *func_result;
    process_func("Тестовий пакет даних C++ RAII");

    // Деструктор UniqueDlHandle автоматично викличе dlclose при виході з зони видимості
    return EXIT_SUCCESS;
}
```
:::

---

## Завдання 2: Перехоплення системних функцій за допомогою LD_PRELOAD

Технологія `LD_PRELOAD` виступає потужним інструментом діагностики, профільування, збору метрик та тестування ПЗ. Вона дозволяє підмінити будь-яку функцію стандартної C-бібліотеки (наприклад, `write`, `read`, `malloc`, `free`, `connect`, `open`) власною реалізацією без перекомпіляції та модифікації сирцевого коду цільової програми.

### Механізм роботи підміни символів у Link Map

Коли динамічний завантажувач `ld.so` запускає бінарний файл із заданою змінною оточення `LD_PRELOAD`, він відкриває вказану у змінній бібліотеку `.so` і додає її в самий початок внутрішнього зв'язаного списку завантажених модулів (структура `struct link_map`).

Під час вирішення релокацій функцій (наприклад, виклику `write()`), динамічний завантажувач послідовно обходить список `link_map` зліва направо. Оскільки бібліотека з `LD_PRELOAD` стоїть першою, завантажувач знаходить функцію-перехоплювач `write()` раніше, ніж справжню функцію `write()` у `libc.so`, і записує її адресу в GOT-таблицю викликаючого процесу.

Щоб перехоплювач міг викликати справжню системну функцію після виконання власного логування або перевірки, використовується виклик `dlsym(RTLD_NEXT, "function_name")`. Псевдо-дескриптор `RTLD_NEXT` наказує `dlsym` розпочати пошук символу в списку `link_map`, починаючи з модуля, завантаженого *після* поточної бібліотеки-перехоплювача.

### Критична пастка: рекурсивні виклики та зациклення (Recursive Deadlock)

Поширеною помилкою при розробці перехоплювачів є випадковий виклик підміненої функції всередині самого перехоплювача. 

Наприклад, якщо у власному перехоплювачі `write()` викликати функцію `printf()` або `fprintf()`, C-бібліотека для виводу форматованого рядка у `stdout` внутрішньо викличе системну функцію `write()`. Це спричинить нескінченну рекурсію (`write` → `printf` → `write` → `printf`), яка за частки мілісекунди вичерпає стек процесу і призведе до аварійного падіння з помилкою `Segmentation Fault` (Stack Overflow).

Для безпечного виводу повідомлень у перехоплювачах слід використовувати:
1. Кешований вказівник на справжній `write()`, отриманий через `dlsym(RTLD_NEXT, "write")`.
2. Прямий системний виклик ядра через `syscall(SYS_write, fd, buf, count)`.

### Безпечна C та C++ реалізація перехоплювача write

:::tabs
```c
/* hook_write.c — Перехоплення функції write() мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>

/* Сигнатура оригінальної функції write */
typedef ssize_t (*real_write_t)(int fd, const void *buf, size_t count);

ssize_t write(int fd, const void *buf, size_t count) {
    /* 1. Пошук оригінальної функції write у libc за допомогою RTLD_NEXT */
    static real_write_t real_write = NULL;
    if (!real_write) {
        real_write = (real_write_t)dlsym(RTLD_NEXT, "write");
        if (!real_write) {
            char msg[] = "[HOOK] Помилка: не вдалося знайти справжній write\n";
            (void)::write(STDERR_FILENO, msg, sizeof(msg) - 1);
            return -1;
        }
    }

    /* 2. Власна логіка перехоплювача: виводимо лог для stdout (1) та stderr (2) */
    if (fd == STDOUT_FILENO || fd == STDERR_FILENO) {
        char log_buf[128];
        int log_len = snprintf(log_buf, sizeof(log_buf),
                               "[PRELOAD HOOK] Перехоплено write(fd=%d, count=%zu bytes)\n",
                               fd, count);
        if (log_len > 0) {
            /* Викликаємо справжній write для виводу логу у stderr */
            real_write(STDERR_FILENO, log_buf, (size_t)log_len);
        }
    }

    /* 3. Передаємо виконання оригінальній функції write у libc */
    return real_write(fd, buf, count);
}
```
```cpp
// hook_write.cpp — Потокобезпечне перехоплення викликів C++ з атомарним лічильником
#define _GNU_SOURCE
#include <unistd.h>
#include <dlfcn.h>
#include <atomic>
#include <span>
#include <string_view>
#include <array>
#include <cstdio>

namespace {
    using RealWriteFn = ssize_t (*)(int, const void*, size_t);
    std::atomic<size_t> g_total_bytes_written{0};

    RealWriteFn get_real_write() noexcept {
        static RealWriteFn real_fn = reinterpret_cast<RealWriteFn>(dlsym(RTLD_NEXT, "write"));
        return real_fn;
    }
}

extern "C" ssize_t write(int fd, const void* buf, size_t count) noexcept {
    RealWriteFn real_fn = get_real_write();
    if (!real_fn) {
        return -1;
    }

    // Потокобезпечно підраховуємо загальну кількість байтів через атомарний лічильник
    g_total_bytes_written.fetch_add(count, std::memory_order_relaxed);

    if (fd == STDOUT_FILENO || fd == STDERR_FILENO) {
        std::array<char, 256> log_buffer;
        int len = std::snprintf(log_buffer.data(), log_buffer.size(),
                                "[CPP HOOK] write(fd=%d, size=%zu) | Загалом записано: %zu B\n",
                                fd, count, g_total_bytes_written.load());
        if (len > 0) {
            real_fn(STDERR_FILENO, log_buffer.data(), static_cast<size_t>(len));
        }
    }

    return real_fn(fd, buf, count);
}
```
:::

---

## Простеження та відлагодження перехоплювачів за допомогою системних утиліт

Для інтроспекції та аналізу роботи динамічних бібліотек і перехоплювачів у системі Linux використовуються такі інструменти:

### 1. Перевірка динамічних символів утилітами nm та readelf

Після компіляції бібліотеки перехоплювача `libhook.so` важливо переконатися, що функція `write` дійсно експортується як глобальний символ коду:

```bash
nm -D libhook.so | grep write
```
*Очікуваний вивід:* `0000000000001140 T write` (буква `T` означає, що символ розташований у секції коду `.text` і є глобально доступним).

Також можна дослідити секцію `.dynamic` за допомогою `readelf`:
```bash
readelf -d libhook.so
```
*Утиліта покаже список тегів `DT_NEEDED`, зокрема залежність від `libc.so.6` та `libdl.so`.*

### 2. Простеження завантаження через strace та ltrace

Для діагностики виконання програми з підключеним `LD_PRELOAD` утиліта `strace` дозволяє побачити, які саме файли відкриває динамічний завантажувач:

```bash
LD_PRELOAD=./libhook.so strace -e trace=openat,mmap ./my_app
```

У лозі `strace` буде видно, що системний завантажувач першим виконує виклик `openat(AT_FDCWD, "./libhook.so", O_RDONLY)` та відображає його сторінки за допомогою `mmap()`, і лише після цього завантажує стандартну бібліотеку `libc.so`.

---

## Інструкція зі збірки та запуску

1. Скомпілюйте перехоплювач у спільновживаний об'єкт:
   ```bash
   # C-версія:
   gcc -fPIC -shared hook_write.c -o libhook.so -ldl

   # C++ версія:
   g++ -std=c++23 -fPIC -shared hook_write.cpp -o libhook.so -ldl
   ```

2. Запустіть будь-яку стандартну системну утиліту (наприклад, `ls -l` або `cat /etc/hosts`) із підключеним `LD_PRELOAD`:
   ```bash
   LD_PRELOAD=./libhook.so ls -l
   ```

3. **Підсумковий результат:**
   Перед кожним рядочним виводом файлів у консолі з'являтимуться сервісні повідомлення перехоплювача `[PRELOAD HOOK]` або `[CPP HOOK]`, які фіксують точну кількість байтів, що передаються системній функції `write()`, та накопичений лічильник байтів.
