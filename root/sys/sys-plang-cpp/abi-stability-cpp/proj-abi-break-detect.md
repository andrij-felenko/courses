# ⚙️ Практичний проєкт: Стійкий каркас плагінів із захистом ABI та CI-аудитом

У великих промислових програмних комплексах — таких як ігрові рушії, CAD-системи, високонавантажені сервери, середовища візуалізації та плагінні хости аудіообробки стандарту VST — динамічні модулі розробляються десятками незалежних команд та сторонніх постачальників. Такі бібліотеки збираються різними версіями компіляторів, із відмінними налаштуваннями оптимізацій, і повинні безперешкодно завантажуватися в основну програму без необхідності її повної перекомпіляції з вихідних текстів.

Якщо на межі взаємодії між виконуваним файлом і динамічною бібліотекою (`.so` у Linux або `.dll` у Windows) необачно використати складні об'єкти стандартної бібліотеки C++ (`std::string`, `std::vector`, `std::shared_ptr` або `std::function`), система стає надзвичайно крихкою. Найменша різниця у версії стандарту (`-std=c++17` проти `-std=c++20`), зміна макросів конфігурації стандартної бібліотеки (`_GLIBCXX_USE_CXX11_ABI` у GCC або `_ITERATOR_DEBUG_LEVEL` у MSVC) чи оновлення версії компілятора призводять до фатальних помилок: тихого пошкодження пам'яті, зсуву покажчиків віртуальних таблиць та аварійного завершення процесу.

Цей практичний проєкт розглядає проектування та реалізацію промислового модульного каркаса (Plugin Framework) на базі стандарту C++20. Архітектура поєднує три взаємодоповнюючі рівні двійкового захисту:
1. **Низькорівневий C-сумісний двійковий шлюз (`extern "C"`)** із непрозорими покажчиками (Opaque Handles), що повністю усуває залежність від манглінгу імен і компіляторних структур;
2. **Високорівневий ідіоматичний C++ шар** на основі ідіоми PImpl (Pointer to Implementation), розумних покажчиків із власними деструкторами та версіонованих просторів імен (`inline namespace`);
3. **Автоматизовану систему безперервного контролю двійкової сумісності в CI/CD** на базі аналізатора налагоджувальних дерев DWARF Libabigail (`abidw` / `abidiff`), яка блокує злиття змін при будь-якій спробі порушити двійковий контракт.

---

## 1. Архітектурні виклики та багаторівнева модель ізоляції

Створення надійного двійкового інтерфейсу вимагає вирішення чотирьох класичних проблем міжмодульної взаємодії у мовах C та C++:

По-перше, **проблема несумісності середовищ виділення пам'яті (Cross-DLL Heap Allocation Trap)**. У середовищі Windows кожна завантажена бібліотека DLL, скомпільована зі своєю версією C Runtime Library (CRT), має власний незалежний дескриптор купи (`HANDLE Heap`). Якщо динамічний плагін виділяє пам'ять через системний виклик `malloc` або оператор `new`, а основна програма намагається звільнити її через `free` або `delete`, це призводить до негайного аварійного краху процесу через спробу повернути блок пам'яті в чужу купу. Щоб запобігти цьому, об'єкт повинен завжди видалятися саме тим модулем, який його створив, що реалізується через спеціальні функції вивільнення (Deleter functions).

По-друге, **проблема манглінгу імен та різниці конвенцій виклику**. Різні компілятори (GCC, Clang, MSVC) застосовують несумісні алгоритми кодування сигнатур у символи лінкера. Більше того, конвенції передачі аргументів відрізняються між операційними системами (System V AMD64 ABI на Linux проти Microsoft x64 на Windows). Передача складних C++ структур за значенням через межу модулів змушує компілятор неявно створювати тимчасові копії на стеку, що знижує швидкодію та створює ризик розсинхронізації вирівнювання (alignment mismatch).

По-третє, **проблема винятків C++ через межу двійкових модулів**. Якщо плагін кидає виняток (`throw std::runtime_error`), а хост-програма скомпільована без підтримки таблиць винятків (`-fno-exceptions`) або з іншою моделлю розгортання стеку (DWARF проти SEH), розгортач стеку середовища виконання не знайде відповідного обробника `catch` і викличе `std::terminate()`. Межа ABI повинна повністю ізолювати винятки всередині модуля і передавати статус помилки у вигляді числових кодів повернення.

По-четверте, **проблема версіонування символів та виявлення помилок на етапі лінкування**. Якщо розробник змінює внутрішню структуру класу або сигнатуру функції, старий клієнт не повинен мовчки звертатися за зміщеними адресами. Необхідно, щоб будь-яка несумісна зміна автоматично генерувала нове ім'я символу через механізм `inline namespace`, перетворюючи потенційний збій у пам'яті під час виконання на прозору помилку компонування `undefined reference`.

---

## 2. Реалізація стійкого двійкового шлюзу плагіна

Розглянемо повну реалізацію архітектури: публічний заголовок двійкового контракту з підтримкою C та C++, високорівневий безпечний фасад із RAII та реалізацію навантаженого математичного плагіна фільтрації сигналів.

### 2.1. Публічний заголовок двійкового контракту (`plugin_abi.h` / `plugin_abi.hpp`)

Публічний заголовок спроектовано так, щоб він міг безпосередньо включатися як у програми на чистому C, так і в сучасні проекти на C++20.

:::tabs
```c
/* plugin_abi.h — C ABI інтерфейс (рівень двійкової сумісності) */
#ifndef PLUGIN_ABI_H
#define PLUGIN_ABI_H

#include <stdint.h>
#include <stddef.h>

#if defined(_WIN32)
  #ifdef PLUGIN_EXPORTS
    #define PLUGIN_API __declspec(dllexport)
  #else
    #define PLUGIN_API __declspec(dllimport)
  #endif
#else
  #define PLUGIN_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Непрозорий дескриптор екземпляра плагіна */
typedef struct plugin_handle_opaque* plugin_handle_t;

/* Структура інформації про версію та сумісність */
typedef struct {
    uint32_t abi_version_major;
    uint32_t abi_version_minor;
    uint32_t patch_version;
    const char* plugin_name;
    const char* vendor_name;
} plugin_metadata_t;

/* Коди помилок операцій плагіна */
typedef enum {
    PLUGIN_SUCCESS = 0,
    PLUGIN_ERR_INVALID_ARG = -1,
    PLUGIN_ERR_EXECUTION_FAILED = -2,
    PLUGIN_ERR_OUT_OF_MEMORY = -3
} plugin_status_t;

/* Сигнатури точок входу динамічної бібліотеки */
PLUGIN_API plugin_status_t plugin_get_metadata(plugin_metadata_t* out_meta);
PLUGIN_API plugin_status_t plugin_create_instance(plugin_handle_t* out_handle);
PLUGIN_API plugin_status_t plugin_process_data(plugin_handle_t handle, const uint8_t* in_data, size_t size, double* out_metric);
PLUGIN_API void            plugin_destroy_instance(plugin_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif /* PLUGIN_ABI_H */
```
```cpp
// plugin_abi.hpp — C++ ідіоматичний фасад поверх стабільного C ABI
#pragma once
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <span>
#include <system_error>

#if defined(_WIN32)
  #ifdef PLUGIN_EXPORTS
    #define PLUGIN_API __declspec(dllexport)
  #else
    #define PLUGIN_API __declspec(dllimport)
  #endif
#else
  #define PLUGIN_API __attribute__((visibility("default")))
#endif

extern "C" {
    struct plugin_handle_opaque;
    using plugin_handle_t = plugin_handle_opaque*;

    struct plugin_metadata_t {
        uint32_t abi_version_major;
        uint32_t abi_version_minor;
        uint32_t patch_version;
        const char* plugin_name;
        const char* vendor_name;
    };

    enum plugin_status_t : int32_t {
        PLUGIN_SUCCESS = 0,
        PLUGIN_ERR_INVALID_ARG = -1,
        PLUGIN_ERR_EXECUTION_FAILED = -2,
        PLUGIN_ERR_OUT_OF_MEMORY = -3
    };

    PLUGIN_API plugin_status_t plugin_get_metadata(plugin_metadata_t* out_meta);
    PLUGIN_API plugin_status_t plugin_create_instance(plugin_handle_t* out_handle);
    PLUGIN_API plugin_status_t plugin_process_data(plugin_handle_t handle, const uint8_t* in_data, size_t size, double* out_metric);
    PLUGIN_API void            plugin_destroy_instance(plugin_handle_t handle);
}

namespace plugin_system {
inline namespace v1 {

// RAII кастомний деструктор для непрозорого C-дескриптора
struct PluginDeleter {
    void operator()(plugin_handle_t h) const noexcept {
        if (h) {
            plugin_destroy_instance(h);
        }
    }
};

using SafeHandle = std::unique_ptr<plugin_handle_opaque, PluginDeleter>;

// Безпечний C++ клас-клієнт із нульовими накладними витратами
class PluginClient {
public:
    PluginClient() {
        plugin_handle_t raw_handle = nullptr;
        plugin_status_t status = plugin_create_instance(&raw_handle);
        if (status != PLUGIN_SUCCESS || !raw_handle) {
            throw std::runtime_error("Не вдалося створити екземпляр плагіна");
        }
        handle_.reset(raw_handle);
    }

    double process(std::span<const uint8_t> buffer) {
        double result = 0.0;
        plugin_status_t status = plugin_process_data(handle_.get(), buffer.data(), buffer.size(), &result);
        if (status != PLUGIN_SUCCESS) {
            throw std::runtime_error("Збій обробки даних у плагіні");
        }
        return result;
    }

private:
    SafeHandle handle_;
};

} // namespace v1
} // namespace plugin_system
```
:::

У цій архітектурі C++ клас `PluginClient` є виключно заголовковою обгорткою (`inline`). Він не генерує жодних експортованих символів у динамічній бібліотеці, а його методи транслюються компілятором у прямі виклики низькорівневих C-функцій. Завдяки кастомному деструктору `PluginDeleter` виклик методу видалення гарантовано перенаправляється у функцію `plugin_destroy_instance()`, яка виконується всередині тієї самої динамічної бібліотеки, повністю розв'язуючи проблему крос-модульної купи.

---

### 2.2. Реалізація динамічного плагіна (`audio_filter_plugin.cpp`)

Всередині динамічного модуля розробники мають абсолютну свободу використовувати будь-які сучасні можливості C++20: стандартні контейнери `std::vector`, розумні покажчики, багатопоточність та алгоритми STL. Жодна з цих деталей реалізації не потрапляє у таблицю символів назовні.

```cpp
// audio_filter_plugin.cpp — реалізація плагіна обробки аудіо
#define PLUGIN_EXPORTS
#include "plugin_abi.hpp"
#include <vector>
#include <numeric>
#include <cmath>
#include <algorithm>

// Внутрішній C++ клас плагіна (повністю прихований від клієнта)
struct plugin_handle_opaque {
    std::vector<double> coefficients;
    double gain = 1.0;
    uint64_t processed_frames = 0;

    plugin_handle_opaque() {
        coefficients.resize(64, 0.015625); // Фільтр ковзного середнього (FIR)
    }

    double compute_filtered_sample(const uint8_t* data, size_t len) {
        double accumulated = 0.0;
        for (size_t i = 0; i < len; ++i) {
            double normalized = static_cast<double>(data[i]) / 255.0;
            accumulated += normalized * coefficients[i % coefficients.size()];
        }
        processed_frames += len;
        return accumulated * gain;
    }
};

plugin_status_t plugin_get_metadata(plugin_metadata_t* out_meta) {
    if (!out_meta) return PLUGIN_ERR_INVALID_ARG;
    out_meta->abi_version_major = 1;
    out_meta->abi_version_minor = 0;
    out_meta->patch_version = 0;
    out_meta->plugin_name = "AudioLowPassFilter";
    out_meta->vendor_name = "AcousticLab";
    return PLUGIN_SUCCESS;
}

plugin_status_t plugin_create_instance(plugin_handle_t* out_handle) {
    if (!out_handle) return PLUGIN_ERR_INVALID_ARG;
    try {
        *out_handle = new plugin_handle_opaque();
        return PLUGIN_SUCCESS;
    } catch (...) {
        return PLUGIN_ERR_OUT_OF_MEMORY;
    }
}

plugin_status_t plugin_process_data(plugin_handle_t handle, const uint8_t* in_data, size_t size, double* out_metric) {
    if (!handle || !in_data || size == 0 || !out_metric) {
        return PLUGIN_ERR_INVALID_ARG;
    }

    try {
        *out_metric = handle->compute_filtered_sample(in_data, size);
        return PLUGIN_SUCCESS;
    } catch (...) {
        return PLUGIN_ERR_EXECUTION_FAILED;
    }
}

void plugin_destroy_instance(plugin_handle_t handle) {
    // Звільнення пам'яті відбувається в тому самому модулі, де був виклик new
    delete handle;
}
```

Зверніть увагу на обробку винятків у кожній експортованій C-функції: будь-який потенційний виняток перехоплюється блоком `try-catch (...)` і перетворюється на числовий статус `PLUGIN_ERR_EXECUTION_FAILED` або `PLUGIN_ERR_OUT_OF_MEMORY`. Це гарантує, що виняток ніколи не перетне межу динамічної бібліотеки і не викличе крах хост-додатку.

---

### 2.3. Завантаження плагіна в хост-додатку через системні виклики (`host_loader.cpp`)

Хост-програма використовує стандартні функції динамічного завантаження операційної системи (`dlopen`, `dlsym`, `dlclose` на POSIX або `LoadLibraryA`, `GetProcAddress`, `FreeLibrary` на Windows) для зв'язування з бібліотекою під час виконання:

```cpp
// host_loader.cpp — безпечне динамічне завантаження плагіна
#include "plugin_abi.hpp"
#include <iostream>
#include <vector>

#if defined(_WIN32)
  #include <windows.h>
  using ModuleHandle = HMODULE;
  #define LOAD_LIB(path) LoadLibraryA(path)
  #define GET_SYM(mod, name) GetProcAddress(mod, name)
  #define CLOSE_LIB(mod) FreeLibrary(mod)
#else
  #include <dlfcn.h>
  using ModuleHandle = void*;
  #define LOAD_LIB(path) dlopen(path, RTLD_NOW | RTLD_LOCAL)
  #define GET_SYM(mod, name) dlsym(mod, name)
  #define CLOSE_LIB(mod) dlclose(mod)
#endif

class DynamicPluginHost {
public:
    explicit DynamicPluginHost(const char* library_path) {
        module_ = LOAD_LIB(library_path);
        if (!module_) {
            throw std::runtime_error("Помилка завантаження бібліотеки плагіна");
        }

        // Перевірка наявності точки отримання метаданих
        auto get_meta = reinterpret_cast<decltype(&plugin_get_metadata)>(GET_SYM(module_, "plugin_get_metadata"));
        if (!get_meta) {
            CLOSE_LIB(module_);
            throw std::runtime_error("Бібліотека не містить точки входу plugin_get_metadata");
        }

        plugin_metadata_t meta{};
        if (get_meta(&meta) == PLUGIN_SUCCESS) {
            std::cout << "Завантажено плагін: " << meta.plugin_name 
                      << " версія ABI: " << meta.abi_version_major << "." << meta.abi_version_minor << "\n";
            if (meta.abi_version_major != 1) {
                CLOSE_LIB(module_);
                throw std::runtime_error("Несумісна major-версія ABI плагіна!");
            }
        }
    }

    ~DynamicPluginHost() {
        if (module_) {
            CLOSE_LIB(module_);
        }
    }

private:
    ModuleHandle module_ = nullptr;
};
```

Цей шаблон завантажувача гарантує, що основна програма спочатку валідує номер версії ABI у заголовку плагіна, і лише після підтвердження сумісності починає викликати функціональні методи.

### 2.4. Синхронізація та зворотні виклики (Callbacks) через межу ABI

У багатопотокових плагінних системах хост-програма часто передає плагіну функції зворотного виклику (Callbacks) для сповіщення про завершення обробки або передачі прогресу. Використання `std::function<void(double)>` або `std::future` на межі ABI суворо заборонено, оскільки внутрішній розмір `std::function` та його таблиця віртуальних функцій (Type Erasure vtable) відрізняються між стандартними бібліотеками (`libstdc++`, `libc++`, MSVC STL).

Натомість застосовують класичний патерн зворотного виклику у стилі C із непрозорим контекстом користувача:

```cpp
// Безпечна сигнатура зворотного виклику на межі ABI
typedef void (*plugin_progress_callback_t)(void* user_data, double progress, const char* status_message);

// Реєстрація зворотного виклику у функціях плагіна
PLUGIN_API plugin_status_t plugin_set_progress_callback(
    plugin_handle_t handle,
    plugin_progress_callback_t callback,
    void* user_data
);
```

Хост-програма передає покажчик на статичну функцію-міст або лямбда-вираз без захоплення разом із покажчиком `this` як `user_data`. Усередині плагіна викликається `callback(user_data, 0.75, "Обробка...")`. Це забезпечує 100% міжкомпіляторну сумісність і нульові накладні витрати на виклик.

### 2.5. Низькорівневі відмінності конвенцій виклику між 32-бітними та 64-бітними платформами

Історично на 32-бітній архітектурі x86 існувало понад п'ять несумісних конвенцій виклику: `__cdecl` (аргументи на стеку, очищає викликач), `__stdcall` (аргументи на стеку, очищає функція), `__fastcall` (перші аргументи у регістрах `ecx`, `edx`) та `__thiscall` (MSVC передавав покажчик `this` у регістрі `ecx`, тоді як GCC передавав його як перший параметр на стеку). Будь-яка невідповідність ключових слів у заголовку призводила до негайного руйнування покажчика вершини стеку (`ESP`).

На 64-бітних платформах конвенції виклику були уніфіковані операційними системами:
- **System V AMD64 ABI (Linux, macOS, BSD)**: перші 6 цілочисельних аргументів або покажчиків передаються через регістри `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9`, а числа з рухомою комою — через `xmm0`–`xmm7`. Покажчик `this` для методів C++ є звичайним першим аргументом і передається у `%rdi`.
- **Microsoft x64 Calling Convention (Windows)**: перші 4 аргументи передаються через регістри `rcx`, `rdx`, `r8`, `r9` (або `xmm0`–`xmm3`), а викликач обов'язково резервує на стеку «тіньовий простір» (Shadow Space) розміром 32 байти (`[rsp+0x20]`) для можливості збереження цих регістрів функцією.

Через ці фундаментальні відмінності скомпільований об'єктний код x86_64 не може безпосередньо взаємодіяти між Linux та Windows без емуляції або спеціальних компіляторних атрибутів (`__attribute__((ms_abi))` у GCC/Clang). Аналогічно, під час крос-компіляції під архітектури ARM AArch64 чи RISC-V застосовуються специфічні правила вирівнювання стеку за 16-байтною межею та використання регістрів `x0`–`x7`. Двійковий C-шлюз гарантує, що всередині кожної цільової платформи всі модулі користуються єдиною платформенною конвенцією без прихованих структурних розбіжностей.

---

## 3. Проектування C++ бібліотеки за ідіомою PImpl

Якщо архітектурні вимоги проекту вимагають надання прямого об'єктно-орієнтованого C++ інтерфейсу з методами класів, але без створення C-шлюзу, єдиним стандартизованим засобом збереження двійкової стабільності є ідіома **PImpl (Pointer to Implementation)**.

### 3.1. Заголовок стабільного класу (`engine.hpp`)

Публічний заголовок містить лише оголошення публічних методів та один непрозорий покажчик `std::unique_ptr<EngineImpl>`. Розмір класу `Engine` на 64-бітній архітектурі завжди дорівнює рівно 8 байтам, незалежно від того, скільки полів або підсистем буде додано у внутрішній клас у наступних версіях.

```cpp
// engine.hpp — публічний заголовок бібліотеки з фіксованим ABI
#pragma once
#include <memory>
#include <string_view>

#if defined(_WIN32)
  #ifdef ENGINE_EXPORTS
    #define ENGINE_API __declspec(dllexport)
  #else
    #define ENGINE_API __declspec(dllimport)
  #endif
#else
  #define ENGINE_API __attribute__((visibility("default")))
#endif

namespace engine {
inline namespace v1 {

class ENGINE_API Engine {
public:
    Engine();
    ~Engine(); // Обов'язково неінлайновий деструктор!

    // Конструктори та оператори переміщення
    Engine(Engine&&) noexcept;
    Engine& operator=(Engine&&) noexcept;

    // Підтримка глибокого копіювання через фабричний метод клонування
    Engine(const Engine& other);
    Engine& operator=(const Engine& other);

    void initialize(std::string_view config_path);
    double execute_step(double delta_time);

private:
    struct EngineImpl;                 // Неповний тип (Forward declaration)
    std::unique_ptr<EngineImpl> impl_; // Фіксований розмір: рівно 8 байтів
};

} // namespace v1
} // namespace engine
```

### 3.2. Закрита реалізація PImpl (`engine.cpp`)

Усі важкі внутрішні змінні, буфери, сокети та системні дескриптори оголошуються виключно у вихідному файлі реалізації `engine.cpp`. Клієнтська програма не має до них доступу на рівні компіляції і не залежить від їхньої зміни.

```cpp
// engine.cpp — реалізація приватного стану
#define ENGINE_EXPORTS
#include "engine.hpp"
#include <string>
#include <vector>
#include <chrono>
#include <iostream>

namespace engine {
inline namespace v1 {

struct Engine::EngineImpl {
    std::string config_path_;
    std::vector<double> performance_history_;
    std::chrono::high_resolution_clock::time_point launch_timestamp_;
    uint64_t step_counter_ = 0;

    void configure(std::string_view path) {
        config_path_ = std::string(path);
        launch_timestamp_ = std::chrono::high_resolution_clock::now();
    }

    double run_simulation(double dt) {
        step_counter_++;
        performance_history_.push_back(dt);
        return dt * 2.0;
    }
};

Engine::Engine() : impl_(std::make_unique<EngineImpl>()) {}

// Деструктор генерується саме тут, де повне визначення EngineImpl відоме компілятору
Engine::~Engine() = default;

Engine::Engine(Engine&&) noexcept = default;
Engine& Engine::operator=(Engine&&) noexcept = default;

// Реалізація глибокого копіювання: викликає конструктор копіювання EngineImpl
Engine::Engine(const Engine& other)
    : impl_(other.impl_ ? std::make_unique<EngineImpl>(*other.impl_) : nullptr) {}

Engine& Engine::operator=(const Engine& other) {
    if (this != &other) {
        if (other.impl_) {
            impl_ = std::make_unique<EngineImpl>(*other.impl_);
        } else {
            impl_.reset();
        }
    }
    return *this;
}

void Engine::initialize(std::string_view config_path) {
    impl_->configure(config_path);
}

double Engine::execute_step(double delta_time) {
    return impl_->run_simulation(delta_time);
}

} // namespace v1
} // namespace engine
```

**Критичний інженерний нюанс деструктора та копіювання PImpl:**
Якщо не визначити деструктор `Engine::~Engine()` та конструктор копіювання у файлі `engine.cpp`, компілятор згенерує їх за замовчуванням у заголовку (`inline`). Коли клієнтська програма скомпілює виклик деструктора `Engine`, вона спробує згенерувати інструкцію видалення `delete impl_.get()`, що призведе до помилки компіляції про видалення неповного типу (`incomplete type EngineImpl`) або, що гірше, до виклику деструктора без очищення полів `std::string` та `std::vector`, спричиняючи витік пам'яті. Розміщення деструктора в `.cpp` файлі гарантує, що клієнт лише викликає скомпільовану функцію, не знаючи нічого про внутрішні типи.

---

## 4. COM-подібні інтерфейси віртуальних таблиць (Pure Virtual Interfaces)

Альтернативним промисловим стандартом побудови ABI (який використовується у DirectX, Windows Runtime, VST3 та багатьох ігрових плагінах) є використання суто абстрактних C++ класів із чистими віртуальними методами.

Такий підхід опирається на суворі правила організації віртуальних таблиць (`vtable`):
1. **Клас не містить жодних полів даних** — лише покажчик на віртуальну таблицю (`vptr`), що гарантує фіксований розмір об'єкта рівно 8 байтів;
2. **Усі методи є чисто віртуальними (`virtual ... = 0`)**;
3. **Нові методи додаються ВИКЛЮЧНО в кінець класу** — це зберігає числові індекси всіх попередніх слотів у таблиці `vtable`, завдяки чому старі бінарні модулі продовжують коректно викликати методи за своїми зміщеннями;
4. **Видалення або перестановка методів суворо заборонені**;
5. **Запит нових інтерфейсів через метод розширення (QueryInterface)** — якщо плагін підтримує нові додаткові можливості, хост отримує покажчик на новий інтерфейс через числовий ідентифікатор без зміни початкового базового класу.

```cpp
// IPluginInterface.hpp — COM-подібний абстрактний інтерфейс розширення
#pragma once
#include <cstdint>
#include <cstddef>

// Унікальні ідентифікатори інтерфейсів (Interface IDs)
constexpr uint32_t IID_PROCESSOR_V1 = 0x1001;
constexpr uint32_t IID_PARAM_CONTROLLER_V1 = 0x1002;

struct IPluginBase {
    // Слот 0: Запит підтримуваних інтерфейсів без порушення vtable
    virtual int32_t query_interface(uint32_t iid, void** out_interface) noexcept = 0;

    // Слот 1: Метод вивільнення екземпляра
    virtual void release() noexcept = 0;

protected:
    ~IPluginBase() = default;
};

struct IProcessorV1 : public IPluginBase {
    // Слот 2: Ініціалізація
    virtual int32_t initialize(const char* name) = 0;

    // Слот 3: Основний цикл обробки
    virtual int32_t process_frame(const float* in, float* out, size_t count) = 0;
};

struct IParameterController : public IPluginBase {
    // Слот 2 для IParameterController: керування параметрами
    virtual int32_t set_parameter(uint32_t param_id, double value) = 0;
    virtual double  get_parameter(uint32_t param_id) = 0;
};
```

Завдяки цьому патерну, коли хост-програма хоче дізнатися, чи підтримує старий плагін керування параметрами, вона викликає `query_interface(IID_PARAM_CONTROLLER_V1, &ptr)`. Якщо плагін не знає цього ідентифікатора, він просто повертає статус `PLUGIN_ERR_INVALID_ARG`, і хост продовжує працювати в режимі базової функціональності без збоїв у пам'яті.

---

## 5. Автоматизований контроль розривів ABI в CI через Libabigail

Для запобігання людським помилкам розробників у великих командах ручна перевірка коду замінюється автоматичним бінарним аудитом у конвеєрі CI/CD.

Інструмент **Libabigail** аналізує секції DWARF у скомпільованих динамічних бібліотеках. Він реконструює повну модель типів даних і порівнює новий бінарник з еталонним зліпком ABI попереднього стабільного релізу.

### 5.1. Сценарій автоматичного тестування (`check_abi.sh`)

Сценарій автоматично збирає еталонний та поточний бінарники, генерує файли зліпків ABI (`.abi`) та виконує порівняльний аналіз через `abidiff`:

```bash
#!/usr/bin/env bash
# check_abi.sh — верифікація стабільності двійкового інтерфейсу
set -e

echo "=== 1. Збірка еталонної версії бібліотеки v1.0 ==="
g++ -std=c++20 -O2 -g -shared -fPIC -fvisibility=hidden \
    -DENGINE_EXPORTS engine.cpp -o libengine_v1.so

# Екстракція еталонного XML-зліпка ABI з DWARF інформації
abidw --drop-private-types libengine_v1.so --out-file libengine_v1.abi
echo "✓ Згенеровано зліпок ABI v1.0"

echo "=== 2. Збірка поточної версії бібліотеки v1.1 ==="
g++ -std=c++20 -O2 -g -shared -fPIC -fvisibility=hidden \
    -DENGINE_EXPORTS engine.cpp -o libengine_v1_1.so

echo "=== 3. Виконання диференційного аудиту через abidiff ==="
if abidiff --leaf-changes-only --impacted-interfaces libengine_v1.abi libengine_v1_1.so; then
    echo "=================================================="
    echo "✅ ПЕРЕВІРКУ ПРОЙДЕНО: Двійковий інтерфейс повністю сумісний!"
    echo "=================================================="
    exit 0
else
    echo "=================================================="
    echo "❌ ДЕФЕКТ: Виявлено розрив ABI між версіями!"
    echo "Зміна двійкового контракту вимагає оновлення SONAME або major-версії."
    echo "=================================================="
    exit 1
fi
```

### 5.2. Симуляція трьох типових помилок розробника та звіти `abidiff`

Розглянемо, як саме `abidiff` виявляє та описує спроби випадкового внесення змін у публічний двійковий контракт:

**Випадок 1: Випадкове додавання поля до класу замість PImpl**
Якщо розробник додав поле `int debug_mode_` безпосередньо в клас `Engine`, клієнтські програми, які виділяють об'єкт `Engine` на власному стеку за старим розміром 8 байтів, почнуть перетирати сусідні стекові фрейми. `abidiff` негайно видає звіт:
```text
  [C]'class engine::v1::Engine' size changed from 64 to 128 (in bits)
    1 data member insertion:
      'int engine::v1::Engine::debug_mode_', at offset 64 (in bits)
```

**Випадок 2: Вставка віртуального методу на початок інтерфейсу**
Якщо новий метод було додано перед `initialize()` у класі `IProcessorV1`, усі подальші виклики методів зміщуються на один слот, змушуючи старий хост викликати метод деструкції замість обробки кадру. `abidiff` фіксує це як зміщення віртуальної таблиці:
```text
  [C]'struct IProcessorV1' sub-type changes:
    1 virtual member function insertion:
      'virtual int32_t IProcessorV1::configure()' at vtable offset 2
    2 virtual member functions with offset changes:
      'virtual int32_t IProcessorV1::initialize(const char*)' offset changed from 2 to 3
      'virtual int32_t IProcessorV1::process_frame(...)' offset changed from 3 to 4
```

**Випадок 3: Зміна розрядності числового типу в параметрі**
Зміна `int32_t` на `int64_t` у функції C ABI на 64-бітній архітектурі x86_64 змінює регістр передачі з 32-бітного `%esi` на 64-бітний `%rsi`. Якщо викликач передає від'ємне 32-бітне число, а функція зчитує 64 біти без знакорозширення верхніх 32 бітів, функція отримує некоректне величезне додатне число. `abidiff` запобігає цій катастрофі:
```text
  [C]'function plugin_status_t plugin_process_data(...)' parameter 3 type changed from 'int32_t' to 'int64_t'
```

### 5.3. Конфігурація правил ігнорування (`abi-suppr.ini`)

Щоб уникнути хибних спрацьовувань для приватних внутрішніх класів, створюється конфігураційний файл правил придушення:

```ini
[suppress_type]
  # Дозволити довільні зміни внутрішньої структури PImpl
  name = engine::v1::Engine::EngineImpl
  type_kind = struct

[suppress_function]
  # Ігнорувати зміни приватних неекспортованих допоміжних методів
  namespace_name_regex = ^engine::detail::
```

### 5.4. Інтеграція в конвеєр GitHub Actions

```yaml
name: ABI Compatibility Gate

on:
  pull_request:
    branches: [ main ]

jobs:
  abi-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install Libabigail and build tools
        run: |
          sudo apt-get update
          sudo apt-get install -y abigail-tools libabigail-dev g++

      - name: Build Current Branch
        run: |
          mkdir build && cd build
          cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo ..
          make -j$(nproc)

      - name: Download Baseline ABI Reference
        run: |
          curl -sfO https://storage.googleapis.com/ci-artifacts/abi/libengine-baseline.abi || true

      - name: Run ABI Diff
        run: |
          if [ -f libengine-baseline.abi ]; then
            abidw --drop-private-types build/libengine.so --out-file build/current.abi
            abidiff --suppressions config/abi-suppr.ini libengine-baseline.abi build/current.abi
          else
            echo "Базовий зліпок відсутній, створюємо новий еталон..."
            abidw --drop-private-types build/libengine.so --out-file build/libengine-baseline.abi
          fi
```

---

## 6. Інженерні висновки та правила безпеки ABI

Побудова виробничого плагінного каркаса вимагає суворого дотримання чотирьох головних інженерних правил:

1. **Ізоляція пам'яті через Opaque Handles та PImpl**: Публічні інтерфейси модулів повинні оперувати виключно скалярними типами та непрозорими покажчиками. Звільнення ресурсів завжди виконується через спеціалізовані C-функції бібліотеки-автора, що запобігає конфліктам середовищ виділення пам'яті.
2. **Нульовий експорт внутрішніх символів**: Прапорці компілятора `-fvisibility=hidden` та `-fvisibility-inlines-hidden` у поєднанні з макросами вибіркового експорту (`__attribute__((visibility("default")))`) гарантують, що внутрішні шаблони та приватні класи не потраплять у динамічну таблицю `.dynsym` і не спричинять конфліктів ODR.
3. **Діагностика вирівнювання за допомогою санітайзерів**: Під час тестування плагінів рекомендується вмикати перевірку коректності розіменування покажчиків та вирівнювання структури за допомогою прапорців `-fsanitize=alignment,undefined` із примусовим аварійним завершенням `-fno-sanitize-recover=alignment`. Це дозволяє виявити невідповідність розкладки пам'яті ще на етапі запуску юніт-тестів до передачі бінарників замовникам.
4. **Автоматичний контроль у CI**: Жодна зміна коду не повинна зливатися в основну гілку без успішного проходження перевірки `abidiff`. Це усуває людський фактор і гарантує збереження двійкової сумісності на рівні операційної системи протягом усього життєвого циклу продукту.
