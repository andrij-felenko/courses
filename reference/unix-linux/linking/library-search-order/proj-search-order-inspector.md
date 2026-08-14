# ⚙️ Інспектор шляхів пошуку та залежностей бінарника у C та C++

При інженерній розробці високонавантажених систем, створенні архітектур плагінів та діагностиці збоїв динамічного завантаження у розробників виникає потреба програмно з'ясувати: які саме каталоги перевіряє завантажувач `ld.so` для конкретного модуля, які залежності вже завантажено в адресний простір процесу і чи активовано захищений режим `AT_SECURE`.

Статичний аналіз за допомогою зовнішніх системних утиліт `ldd` або `readelf` показує лише те, що закарбовано у файлі на диску у момент компіляції. Однак під час виконання процес може змінити своє середовище, завантажити додаткові модулі через виклики `dlopen()` або опинитися в ізольованому привілейованому контексті безпеки. Нижче наведено практичний інспектор завантажувача, який використовує розширення C-бібліотеки glibc (`dlinfo`, `dl_iterate_phdr`, `getauxval`), щоб витягти актуальний список шляхів пошуку бібліотек безпосередньо з об'єктів завантажувача під час виконання програми.

## Задача та архітектура рішення

Програма повинна виконати три ключові завдання системного аналізу завантаженого середовища:

1. **Перевірка режиму привілеїв**: Отримати значення тегу `AT_SECURE` з допоміжного вектора ядра (Auxiliary Vector, `auxv`) та з'ясувати, чи ігнорує `ld.so` небезпечні змінні середовища (такі як `LD_LIBRARY_PATH` та `LD_PRELOAD`).
2. **Ітерація завантажених модулів**: Пройтися по всіх розділюваних об'єктах у пам'яті за допомогою функції `dl_iterate_phdr()`, вивівши їхні базові адреси завантаження у віртуальній пам'яті та абсолютні шляхи до файлів.
3. **Запит активних шляхів ld.so**: Для головного модуля програми отримати повний список активних каталогів пошуку за допомогою функції `dlinfo()` з запитом `RTLD_DI_SERINFO`, розібрати джерело походження кожного каталогу та коректно звільнити пам'ять.

Алгоритм взаємодії інспектора з внутрішніми структурами динамічного завантажувача виглядає наступним чином:

```text
[Процес] ──► getauxval(AT_SECURE) ──► Перевірка режиму безпеки
   │
   ├──► dl_iterate_phdr() ──► Обхід усіх ELF-заголовків завантажених .so
   │
   └──► dlopen(NULL) ──► dlinfo(RTLD_DI_SERINFOSIZE) ──► malloc() ──► dlinfo(RTLD_DI_SERINFO) ──► Вивід шляхів
```

## Механіка роботи інспектора під капотом

Під час виклику `dl_iterate_phdr()` динамічний завантажувач бере внутрішнє блокування списку завантажених модулів (`_r_debug.r_map`) і послідовно передає у наший callback структуру `dl_phdr_info`. Це дозволяє отримати точний знімок усіх завантажених `.so`-файлів без ризику стану гонитви (race condition) у багатопотоковому середовищі.

Запит `dlinfo()` з прапорцем `RTLD_DI_SERINFO` розбирає масив `r_searchpath_elem`, який `ld.so` збудував при старті процесу. Оскільки кількість елементів у списку залежить від кількості каталогів у RPATH, RUNPATH та системних налаштуваннях, використання `dlinfo` вимагає двокрокового алгоритму виділення пам'яті: спочатку запитується необхідний розмір у байтах через `RTLD_DI_SERINFOSIZE`, виділяється пам'ять, і лише після цього заповнюється структура `Dl_serinfo`.

## Реалізація

Нижче наведено дві повноцінні, незалежні реалізації інспектора завантажувача: перша мовою C з дотриманням стандарту POSIX та розширень GNU glibc, а друга мовою C++ з використанням сучасних ідіом RAII, обгортки для ресурсу `dlopen`, безпечних контейнерів `std::vector` та обробки помилок через `std::expected`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <link.h>
#include <sys/auxv.h>
#include <stdbool.h>

/* Ітератор завантажених розділюваних об'єктів у адресному просторі */
static int module_callback(struct dl_phdr_info *info, size_t size, void *data) {
    (void)size;
    (void)data;
    const char *name = (info->dlpi_name && info->dlpi_name[0] != '\0') 
                       ? info->dlpi_name 
                       : "[Main Executable]";
    printf("  - Базова адреса: 0x%012lx | Модуль: %s\n", 
           (unsigned long)info->dlpi_addr, name);
    return 0;
}

/* Отримання та вивід шляхів пошуку ld.so */
static bool print_search_paths(void *handle) {
    Dl_serinfo size_info;
    Dl_serinfo *info = NULL;

    /* Крок 1: Запит необхідного розміру пам'яті */
    if (dlinfo(handle, RTLD_DI_SERINFOSIZE, &size_info) != 0) {
        fprintf(stderr, "Помилка dlinfo(RTLD_DI_SERINFOSIZE): %s\n", dlerror());
        return false;
    }

    info = (Dl_serinfo *)malloc(size_info.dls_size);
    if (!info) {
        perror("Помилка виділення пам'яті під Dl_serinfo");
        return false;
    }

    /* Ініціалізація полів структури перед повторним викликом */
    info->dls_size = size_info.dls_size;
    info->dls_cnt = size_info.dls_cnt;

    /* Крок 2: Отримання детальної інформації про шляхи */
    if (dlinfo(handle, RTLD_DI_SERINFO, info) != 0) {
        fprintf(stderr, "Помилка dlinfo(RTLD_DI_SERINFO): %s\n", dlerror());
        free(info);
        return false;
    }

    printf("\nАктивні шляхи пошуку ld.so (усього: %u):\n", info->dls_cnt);
    for (unsigned int i = 0; i < info->dls_cnt; ++i) {
        printf("  [%u] %s\n", i + 1, info->dls_serpath[i].dls_name);
    }

    free(info);
    return true;
}

int main(void) {
    unsigned long secure = getauxval(AT_SECURE);
    printf("=== Інспектор динамічного завантажувача (C) ===\n");
    printf("Режим безпеки AT_SECURE: %lu (%s)\n\n", 
           secure, secure ? "АКТИВНИЙ — LD_LIBRARY_PATH ігнорується" : "Ззвичайний");

    printf("Завантажені ELF-модулі в адресному просторі:\n");
    dl_iterate_phdr(module_callback, NULL);

    void *handle = dlopen(NULL, RTLD_NOW);
    if (!handle) {
        fprintf(stderr, "Помилка dlopen(NULL): %s\n", dlerror());
        return EXIT_FAILURE;
    }

    if (!print_search_paths(handle)) {
        dlclose(handle);
        return EXIT_FAILURE;
    }

    dlclose(handle);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <dlfcn.h>
#include <link.h>
#include <sys/auxv.h>

namespace loader_inspector {

struct SearchPath {
    std::string name;
    unsigned int flags;
};

/* RAII-обгортка для автоматичного закриття дескриптора dlopen */
class DynamicHandle {
public:
    explicit DynamicHandle(void* handle) : handle_(handle) {}
    ~DynamicHandle() {
        if (handle_) {
            ::dlclose(handle_);
        }
    }

    DynamicHandle(const DynamicHandle&) = delete;
    DynamicHandle& operator=(const DynamicHandle&) = delete;

    DynamicHandle(DynamicHandle&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }

    DynamicHandle& operator=(DynamicHandle&& other) noexcept {
        if (this != &other) {
            if (handle_) ::dlclose(handle_);
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] void* get() const noexcept { return handle_; }

private:
    void* handle_{nullptr};
};

struct SerinfoDeleter {
    void operator()(Dl_serinfo* ptr) const noexcept {
        std::free(ptr);
    }
};

using SerinfoPtr = std::unique_ptr<Dl_serinfo, SerinfoDeleter>;

[[nodiscard]] bool is_secure_mode() noexcept {
    return getauxval(AT_SECURE) != 0;
}

[[nodiscard]] std::expected<DynamicHandle, std::string> open_self() {
    void* handle = ::dlopen(nullptr, RTLD_NOW);
    if (!handle) {
        const char* err = ::dlerror();
        return std::unexpected(err ? err : "Невідома помилка dlopen");
    }
    return DynamicHandle(handle);
}

[[nodiscard]] std::expected<std::vector<SearchPath>, std::string> 
fetch_search_paths(const DynamicHandle& handle) {
    Dl_serinfo size_info{};
    if (::dlinfo(handle.get(), RTLD_DI_SERINFOSIZE, &size_info) != 0) {
        const char* err = ::dlerror();
        return std::unexpected(err ? err : "Помилка RTLD_DI_SERINFOSIZE");
    }

    SerinfoPtr info(static_cast<Dl_serinfo*>(std::malloc(size_info.dls_size)));
    if (!info) {
        return std::unexpected("Помилка виділення пам'яті під Dl_serinfo");
    }

    info->dls_size = size_info.dls_size;
    info->dls_cnt = size_info.dls_cnt;

    if (::dlinfo(handle.get(), RTLD_DI_SERINFO, info.get()) != 0) {
        const char* err = ::dlerror();
        return std::unexpected(err ? err : "Помилка RTLD_DI_SERINFO");
    }

    std::vector<SearchPath> paths;
    paths.reserve(info->dls_cnt);

    for (unsigned int i = 0; i < info->dls_cnt; ++i) {
        paths.push_back(SearchPath{
            .name = info->dls_serpath[i].dls_name,
            .flags = info->dls_serpath[i].dls_flags
        });
    }

    return paths;
}

} // namespace loader_inspector

int main() {
    std::cout << "=== C++ Інспектор динамічного завантажувача ===\n";
    std::cout << "Режим безпеки AT_SECURE: " 
              << (loader_inspector::is_secure_mode() 
                  ? "АКТИВНИЙ (SUID/SGID захист)" 
                  : "Вимкнено") 
              << "\n\n";

    std::cout << "Перелік завантажених модулів у пам'яті:\n";
    ::dl_iterate_phdr([](struct dl_phdr_info* info, size_t, void*) -> int {
        std::string_view name = (info->dlpi_name && info->dlpi_name[0] != '\0') 
                                ? info->dlpi_name 
                                : "[Main Executable]";
        std::cout << "  - [0x" << std::hex << info->dlpi_addr << std::dec << "] " 
                  << name << "\n";
        return 0;
    }, nullptr);

    auto handle_result = loader_inspector::open_self();
    if (!handle_result) {
        std::cerr << "Помилка: " << handle_result.error() << "\n";
        return 1;
    }

    auto paths_result = loader_inspector::fetch_search_paths(*handle_result);
    if (!paths_result) {
        std::cerr << "Помилка аналізу шляхів: " << paths_result.error() << "\n";
        return 1;
    }

    std::cout << "\nАктивні шляхи пошуку ld.so (усього: " << paths_result->size() << "):\n";
    std::size_t index = 1;
    for (const auto& path : *paths_result) {
        std::cout << "  [" << index++ << "] " << path.name << "\n";
    }

    return 0;
}
```
:::

## Крок за кроком: детальний розбір механізму

### 1. Двокрокова робота з dlinfo та Dl_serinfo

Розробники C-бібліотеки glibc при проектуванні API `dlinfo` зіткнулися з тим, що кількість каталогів у ланцюжках RPATH, RUNPATH та системних налаштуваннях є змінною величиною. Вона визначається конфігурацією конкретного бінарника та середовища запуску.

Тому структура `Dl_serinfo` використовує шаблону масиву змінної довжини `Dl_serpath dls_serpath[1]`.

Для безпечного виклику та уникнення виходу за межі буфера процедура розділена на два чіткі кроки:

1. **Перший виклик `dlinfo(handle, RTLD_DI_SERINFOSIZE, &size_info)`**: Завантажувач аналізує внутрішній список каталогів для даного модуля, обчислює кількість записів і розраховує точний розмір у байтах, необхідний для зберігання заголовка `Dl_serinfo` та всіх елементів масиву рядків `dls_serpath`. Завантажувач записує обчислений розмір у поле `size_info.dls_size`.
2. **Виділення пам'яті**: Програма виділяє суцільний буфер байтів потрібного розміру у купі через `malloc()` (або `std::malloc` у C++).
3. **Другий виклик `dlinfo(handle, RTLD_DI_SERINFO, info)`**: Програма обов'язково ініціалізує поля `info->dls_size` та `info->dls_cnt` значеннями, отриманими на першому кроці, після чого повторно викликає `RTLD_DI_SERINFO`. Завантажувач копіює абсолютні шляхи каталогів та їхні прапорці джерела безпосередньо у виділений буфер.

### 2. Ітерація модулів через dl_iterate_phdr

Функція `dl_iterate_phdr()` обходить внутрішній зв'язаний список завантажених об'єктів завантажувача (структури `link_map`) і для кожного завантаженого модуля викликає нашу callback-функцію, передаючи структуру `dl_phdr_info`:

- `dlpi_addr`: Базова віртуальна адреса, за якою ELF-модуль відображено у пам'ять процесу.
- `dlpi_name`: Повний абсолютний шлях до `.so`-файлу на диску. Для головного виконуваного файлу програми це поле містить порожній рядок `""`, тому інспектор явно замінює його на позначку `[Main Executable]`.
- `dlpi_phdr`: Вказівник на масив ELF Program Headers у пам'яті, який містить описи сегментів `PT_LOAD`, `PT_DYNAMIC`, `PT_TLS` тощо.

## Пастки та крайові випадки

При використанні описаного API у реальних виробничих проєктах необхідно враховувати наступні чотири пастки:

1. **Відсутність нормалізації dls_size**: Якщо при другому виклику `RTLD_DI_SERINFO` не ініціалізувати поле `info->dls_size` значенням, отриманим від `RTLD_DI_SERINFOSIZE`, завантажувач glibc вважатиме переданий буфер некоректним і поверне помилку `EINVAL`.
2. **Базова адреса для не-PIE бінарників**: Якщо програма скомпільована без підтримки PIE (Position Independent Executable), її сегменти завантажуються за фіксованими віртуальними адресами, вказаними в ELF-заголовку. У цьому випадку `dlpi_addr` поверне `0x0`, хоча програма успішно працює у пам'яті.
3. **Очищення стану dlerror()**: Виклик функції `dlerror()` повертає останнє повідомлення про помилку і **одночасно очищає його**. Якщо викликати `dlerror()` два рази поспіль для логування, другий виклик поверне `NULL`, що призведе до падіння програми при передачі цього вказівника у `printf("%s")`.
4. **Багатопотокова синхронізація**: Функція `dlopen(NULL, RTLD_NOW)` повертає дескриптор головного модуля. Якщо інші потоки процесу в цей самий момент підвантажують нові бібліотеки через `dlopen`, структура `link_map` може змінюватися. Функція `dl_iterate_phdr` є потокобезпечною, бо бере внутрішній мутекс `ld.so`, тоді як серія викликів `dlinfo` для сторонніх дескрипторів вимагає обачності.
