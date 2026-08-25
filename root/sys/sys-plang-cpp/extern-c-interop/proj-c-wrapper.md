# ⚙️ Проектування стабільного C-API для бібліотеки на C++

Ця практична розробка демонструє повний інженерний цикл проектування двійково-стабільного інтерфейсу (C-API) для складної бібліотеки, написаної на сучасному C++ (із класами, динамічними контейнерами, RAII, багатопотоковістю та винятками), що дозволяє безшовно інтегрувати її в проекти на чистому C, Rust, Python, Go або сторонні C++ додатки без двійкових конфліктів ABI.

## Постановка задачі та інженерні обмеження

У системній інженерії часто виникає фундаментальний конфлікт між зручністю розробки внутрішньої бізнес-логіки та вимогами до двійкової сумісності публічного інтерфейсу. Мова C++ надає багатий набір засобів високого рівня: автоматичне управління пам'яттю через RAII, шаблони, контейнери стандартної бібліотеки (`std::vector`, `std::string`, `std::unordered_map`), винятки та поліморфізм. Проте прямий експорт C++ інтерфейсів у вигляді класів чи функцій із типами стандартної бібліотеки створює жорстку прив'язку до конкретної версії компілятора, стандартної бібліотеки (`libstdc++` vs `libc++` vs `MSVC STL`) та налаштувань прапорців компіляції (`-D_GLIBCXX_USE_CXX11_ABI`).

Розглянемо практичну задачу розробки високопродуктивного криптографічного модуля потокового перетворення даних. Внутрішнє ядро модуля реалізоване на C++20 і використовує класи, контейнери `std::vector<uint8_t>`, рядки `std::string` та винятки `std::runtime_error` для сигналізації про помилки конфігурації чи збої обробки.

До експортованого інтерфейсу висуваються суворі промислові вимоги:
1. **Повна двійкова стабільність (ABI Stability).** Зміна внутрішніх полів C++ класів, додавання нових приватних членів чи зміна версії компілятора не повинні вимагати перекомпіляції клієнтського коду, що викликає бібліотеку через динамічне зв'язування (`.so` або `.dll`).
2. **Ізоляція внутрішніх типів (патерн Opaque Handle).** Клієнт не повинен бачити заголовків C++ або внутрішніх структур даних: взаємодія відбувається виключно через непрозорі покажчики на неповні типи.
3. **Бар'єр винятків (Exception Barrier).** Жоден виняток C++ не повинен виходити за межі експортованої функції в клієнтський стек викликів C. Усі винятки мають перехоплюватися та транслюватися в числові статусні коди.
4. **Потокобезпечна діагностика помилок.** Надання механізму отримання детального текстового опису помилки для поточного потоку виконання за аналогією з функціями `strerror` або `GetLastError`.
5. **Гнучкий механізм зворотних викликів (Callbacks).** Підтримка реєстрації функцій сповіщення про прогрес із безпечною передачею довільного контексту користувача через покажчик `void* user_data`.
6. **Підтримка динамічного завантаження під час виконання (Dynamic Loading).** Можливість завантажувати бібліотеку функціями `dlopen`/`dlsym` у Linux або `LoadLibrary`/`GetProcAddress` у Windows без необхідності лінкування імпортної бібліотеки на етапі збирання.
7. **Сумісність із багатомовними біндінгами (Foreign Function Interface).** Інтерфейс повинен прямо відображатися в FFI інших популярних системних і прикладних мов: Rust (через `bindgen` та `unsafe extern "C"`), Python (через `ctypes` або CFFI), Go (через `cgo`).

## Архітектурне розбиття на рівні ізоляції

Щоб досягти повної двійкової ізоляції, архітектура бібліотеки розділяється на три взаємопов'язані шари:

1. **Публічний C-заголовок (`engine_api.h`).** Містить виключно типи мови C, неповні оголошення структур, переліки статусів і функції, оголошені зі специфікатором зв'язування `extern "C"`. Цей файл може бути включений у вихідний код будь-якої мови, що підтримує C-сумісні заголовки.
2. **Шар FFI-обгортки та бар'єра винятків (`engine_api.cpp`).** Компілюється компілятором C++. Тут визначається повна структура дескриптора, реалізуються функції життєвого циклу, відбувається приведення типів та огортання кожного виклику в блоки `try { ... } catch (...)`.
3. **Внутрішнє C++ ядро (`engine_core.hpp`).** Повноцінний об'єктно-орієнтований C++ код, який використовує всі можливості сучасної мови й нічого не знає про обмеження C-API.

![Архітектура Opaque Handle та Exception Barrier](img/fig-opaque-handle.svg)

*Архітектура шару експорту: неповний тип дескриптора struct engine_ctx_t та бар'єр перехоплення винятків ізолюють внутрішню структуру C++ ядра від двійкового інтерфейсу.*

## 1. Публічний заголовок C-API (engine_api.h)

Заголовок проектується за суворими правилами C-сумісності: макрос перевірки `__cplusplus`, фіксовані типи з `<stdint.h>` та макрос керування двійковим експортом символів `ENGINE_API`.

```c
#ifndef ENGINE_API_H
#define ENGINE_API_H

#include <stddef.h>
#include <stdint.h>

/* Макрос експорту символів для динамічних бібліотек */
#if defined(_WIN32) || defined(__CYGWIN__)
  #if defined(ENGINE_EXPORTS)
    #define ENGINE_API __declspec(dllexport)
  #else
    #define ENGINE_API __declspec(dllimport)
  #endif
#else
  #if defined(__GNUC__) && __GNUC__ >= 4
    #define ENGINE_API __attribute__((visibility("default")))
  #else
    #define ENGINE_API
  #endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Статусні коди операцій */
typedef enum engine_status_t {
    ENGINE_STATUS_OK               =  0,
    ENGINE_STATUS_ERR_INVALID_ARG  = -1,
    ENGINE_STATUS_ERR_OUT_OF_MEMORY= -2,
    ENGINE_STATUS_ERR_PROCESSING   = -3,
    ENGINE_STATUS_ERR_UNKNOWN      = -4
} engine_status_t;

/* Непрозорий дескриптор (Opaque Handle / Incomplete Type) */
typedef struct engine_ctx_t engine_ctx_t;

/* Сигнатура функції зворотного виклику */
typedef void (*engine_progress_cb)(size_t bytes_processed, void* user_data);

/* Сигнатура функції звільнення користувацького контексту */
typedef void (*engine_cleanup_cb)(void* user_data);

/* Створення нового екземпляра рушія */
ENGINE_API engine_status_t engine_create(const char* algorithm_name, engine_ctx_t** out_ctx);

/* Безпечне знищення екземпляра рушія */
ENGINE_API void            engine_destroy(engine_ctx_t* ctx);

/* Потокова обробка блоку пам'яті */
ENGINE_API engine_status_t engine_process(engine_ctx_t* ctx,
                                          const uint8_t* input,
                                          size_input_len,
                                          uint8_t* output,
                                          size_t* inout_output_len);

/* Реєстрація функції зворотного виклику з користувацьким контекстом */
ENGINE_API engine_status_t engine_set_progress_callback(engine_ctx_t* ctx,
                                                        engine_progress_cb cb,
                                                        void* user_data,
                                                        engine_cleanup_cb cleanup);

/* Отримання тексту останньої помилки для поточного потоку */
ENGINE_API const char*     engine_get_last_error(void);

#ifdef __cplusplus
}
#endif

#endif /* ENGINE_API_H */
```

## 2. Реалізація внутрішнього ядра та C-обгортки (engine_api.cpp)

У файлі реалізації визначено внутрішній клас `EngineCore`, деструктор якого коректно очищує всі виділені ресурси, включаючи закриття можливих дескрипторів або звільнення користувацького контексту зворотного виклику.

```cpp
#include "engine_api.h"
#include <vector>
#include <string>
#include <memory>
#include <stdexcept>
#include <new>
#include <cstring>
#include <mutex>

/* Потоколокальне сховище останнього діагностичного повідомлення */
thread_local std::string g_last_error_message;

static void set_last_error(const std::string& msg) noexcept {
    g_last_error_message = msg;
}

/* Внутрішній клас обчислювального ядра */
class EngineCore {
public:
    explicit EngineCore(std::string algo) : algorithm_(std::move(algo)) {
        if (algorithm_.empty()) {
            throw std::invalid_argument("Ім'я алгоритму не може бути порожнім рядком");
        }
        if (algorithm_ != "AES-CTR-STREAM" && algorithm_ != "XOR-FAST") {
            throw std::invalid_argument("Непідтримуваний алгоритм: " + algorithm_);
        }
        buffer_.reserve(8192);
    }

    ~EngineCore() {
        // Якщо клієнт надав функцію очищення контексту, гарантовано викликаємо її
        if (cleanup_ && user_data_) {
            cleanup_(user_data_);
            user_data_ = nullptr;
        }
    }

    // Заборона копіювання для збереження унікального володіння
    EngineCore(const EngineCore&) = delete;
    EngineCore& operator=(const EngineCore&) = delete;

    void set_callback(engine_progress_cb cb, void* user_data, engine_cleanup_cb cleanup) noexcept {
        if (cleanup_ && user_data_ && user_data_ != user_data) {
            cleanup_(user_data_);
        }
        callback_ = cb;
        user_data_ = user_data;
        cleanup_ = cleanup;
    }

    size_t process_data(const uint8_t* in_data, size_t len, uint8_t* out_data, size_t max_out) {
        if (!in_data || !out_data) {
            throw std::invalid_argument("Вхідний або вихідний покажчик буфера дорівнює nullptr");
        }
        if (max_out < len) {
            throw std::runtime_error("Вихідний буфер замалий для збереження результату");
        }

        const uint8_t mask = (algorithm_ == "XOR-FAST") ? 0xAA : 0x55;
        for (size_t i = 0; i < len; ++i) {
            out_data[i] = in_data[i] ^ mask;
        }

        if (callback_) {
            callback_(len, user_data_);
        }
        return len;
    }

private:
    std::string algorithm_;
    std::vector<uint8_t> buffer_;
    engine_progress_cb callback_{nullptr};
    void* user_data_{nullptr};
    engine_cleanup_cb cleanup_{nullptr};
};

/* Повне визначення структури дескриптора у C++ одиниці трансляції */
struct engine_ctx_t {
    std::unique_ptr<EngineCore> core;
};

/* Реалізація експортованого інтерфейсу з повним бар'єром винятків */
extern "C" {

engine_status_t engine_create(const char* algorithm_name, engine_ctx_t** out_ctx) {
    if (!algorithm_name || !out_ctx) {
        set_last_error("Неприпустимий нульовий покажчик аргументу конфігурації");
        return ENGINE_STATUS_ERR_INVALID_ARG;
    }
    *out_ctx = nullptr;

    try {
        auto handle = std::make_unique<engine_ctx_t>();
        handle->core = std::make_unique<EngineCore>(std::string(algorithm_name));
        
        // Передаємо володіння сирому покажчику виключно після успішної ініціалізації
        *out_ctx = handle.release();
        return ENGINE_STATUS_OK;
    } catch (const std::invalid_argument& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_INVALID_ARG;
    } catch (const std::bad_alloc& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_OUT_OF_MEMORY;
    } catch (const std::exception& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_UNKNOWN;
    } catch (...) {
        set_last_error("Невідомий системний виняток у конструкторі рушія");
        return ENGINE_STATUS_ERR_UNKNOWN;
    }
}

void engine_destroy(engine_ctx_t* ctx) {
    if (!ctx) return;
    try {
        // Відновлюємо RAII-володіння: оператор delete викличе деструктори EngineCore,
        // std::string, std::vector та функцію очищення cleanup_
        std::unique_ptr<engine_ctx_t> cleaner(ctx);
    } catch (...) {
        // Захист межі C-ABI: жоден виняток під час руйнування не повинен покинути функцію
    }
}

engine_status_t engine_process(engine_ctx_t* ctx,
                               const uint8_t* input,
                               size_t input_len,
                               uint8_t* output,
                               size_t* inout_output_len) {
    if (!ctx || !ctx->core || !inout_output_len) {
        set_last_error("Недійсний дескриптор рушія або покажчик розміру виходу");
        return ENGINE_STATUS_ERR_INVALID_ARG;
    }

    try {
        size_t written = ctx->core->process_data(input, input_len, output, *inout_output_len);
        *inout_output_len = written;
        return ENGINE_STATUS_OK;
    } catch (const std::invalid_argument& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_INVALID_ARG;
    } catch (const std::runtime_error& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_PROCESSING;
    } catch (const std::bad_alloc& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_OUT_OF_MEMORY;
    } catch (const std::exception& e) {
        set_last_error(e.what());
        return ENGINE_STATUS_ERR_UNKNOWN;
    } catch (...) {
        set_last_error("Критичний невідомий збій під час обробки даних");
        return ENGINE_STATUS_ERR_UNKNOWN;
    }
}

engine_status_t engine_set_progress_callback(engine_ctx_t* ctx,
                                             engine_progress_cb cb,
                                             void* user_data,
                                             engine_cleanup_cb cleanup) {
    if (!ctx || !ctx->core) {
        set_last_error("Недійсний дескриптор рушія");
        return ENGINE_STATUS_ERR_INVALID_ARG;
    }
    ctx->core->set_callback(cb, user_data, cleanup);
    return ENGINE_STATUS_OK;
}

const char* engine_get_last_error(void) {
    return g_last_error_message.c_str();
}

} // extern "C"
```

## 3. Механіка трампліна та керування контекстом

Найважливіший аспект проектування функцій зворотного виклику — передача стану. Сигнатура C-функції `void (*)(size_t, void*)` є звичайним 8-байтовим покажчиком на машинний код. Вона не може зберігати стан лямбда-виразу (наприклад, захоплені змінні `[&total, this]`) чи безпосередньо посилатися на метод класу C++.

Механізм трампліна розв'язує цю проблему через розділення коду і даних:
1. Клієнт передає статичну функцію-перехідник (трамплін), яка має сигнатуру C-функції.
2. Контекстні дані (екземпляр C++ об'єкта, структура або обгортка `std::function`) передаються через нетипізований покажчик `void* user_data`.
3. Усередині трампліна покажчик відновлюється за допомогою `static_cast<TargetType*>(user_data)` і викликає цільовий метод.

![Трамплін зворотного виклику](img/fig-callback-trampoline.svg)

*Трамплін зворотного виклику: статична функція-перехідник відновлює C++ контекст із покажчика user_data без накладних витрат на віртуальну диспетчеризацію.*

Розглянемо, як це працює на рівні машинного коду: під час виклику функції зворотного виклику за стандартом System V AMD64 ABI значення `bytes_processed` передається в регістрі `%rdi`, а покажчик `user_data` — у регістрі `%rsi`. Статичний трамплін не виконує жодних динамічних алокацій чи пошуку у віртуальних таблицях: він просто перекладає покажчик контексту в регістр `%rdi` (неявний перший параметр `this` для виклику методу) і робить прямий безумовний стрибок `jmp` на цільовий машинний код. Накладні витрати такого містка дорівнюють одиницям тактів процесора.

## 4. Використання бібліотеки: клієнт на C та ідіоматичний клієнт на C++

Нижче наведено практичне порівняння двох підходів до використання скомпільованого C-API: прямого виклику з чистого C з ручною обробкою ресурсів та ідіоматичної C++ обгортки, яка надає сучасний інтерфейс на основі `std::span`, лямбда-функцій та розумного покажчика `std::unique_ptr` із власним делетером.

:::tabs
```c
#include "engine_api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Користувацька структура стану для зворотного виклику */
typedef struct AppStats {
    size_t total_processed;
    int chunk_count;
} AppStats;

static void on_progress(size_t bytes, void* user_data) {
    AppStats* stats = (AppStats*)user_data;
    if (stats) {
        stats->total_processed += bytes;
        stats->chunk_count++;
        printf("[C Client] Оброблено фрагмент: %zu байтів (разом: %zu, викликів: %d)\n",
               bytes, stats->total_processed, stats->chunk_count);
    }
}

int main(void) {
    engine_ctx_t* ctx = NULL;
    engine_status_t st = engine_create("XOR-FAST", &ctx);
    if (st != ENGINE_STATUS_OK) {
        fprintf(stderr, "[C Client] Помилка створення: %s\n", engine_get_last_error());
        return EXIT_FAILURE;
    }

    AppStats stats = { 0, 0 };
    st = engine_set_progress_callback(ctx, on_progress, &stats, NULL);
    if (st != ENGINE_STATUS_OK) {
        fprintf(stderr, "[C Client] Помилка реєстрації callback: %s\n", engine_get_last_error());
        engine_destroy(ctx);
        return EXIT_FAILURE;
    }

    const uint8_t payload[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08 };
    uint8_t buffer[32];
    size_t out_len = sizeof(buffer);

    st = engine_process(ctx, payload, sizeof(payload), buffer, &out_len);
    if (st != ENGINE_STATUS_OK) {
        fprintf(stderr, "[C Client] Помилка обробки: %s\n", engine_get_last_error());
        engine_destroy(ctx);
        return EXIT_FAILURE;
    }

    printf("[C Client] Успішно отримано %zu байтів. Перший байт результату: 0x%02X\n",
           out_len, buffer[0]);

    engine_destroy(ctx);
    return EXIT_SUCCESS;
}
```
```cpp
#include "engine_api.h"
#include <iostream>
#include <memory>
#include <vector>
#include <span>
#include <string_view>
#include <functional>
#include <stdexcept>

// Власний Deleter для безпечного автоматичного виклику engine_destroy
struct EngineDeleter {
    void operator()(engine_ctx_t* ptr) const noexcept {
        engine_destroy(ptr);
    }
};

using ScopedEngineHandle = std::unique_ptr<engine_ctx_t, EngineDeleter>;

// Ідіоматична обгортка мовою C++ з повним контролем винятків та RAII
class CryptoEngine {
public:
    explicit CryptoEngine(std::string_view algo) {
        engine_ctx_t* raw_ptr = nullptr;
        engine_status_t st = engine_create(algo.data(), &raw_ptr);
        if (st != ENGINE_STATUS_OK) {
            throw std::runtime_error(std::string("Не вдалося ініціалізувати рушій: ") + 
                                     engine_get_last_error());
        }
        handle_.reset(raw_ptr);
    }

    // Реєстрація довільної лямбда-функції з підтримкою захоплення стану
    template <typename Callback>
    void set_progress_handler(Callback&& cb) {
        callback_holder_ = std::make_unique<std::function<void(size_t)>>(std::forward<Callback>(cb));

        // Статичний трамплін для перетворення C-виклику у виклик std::function
        auto trampoline = [](size_t bytes, void* user_data) noexcept {
            auto* target = static_cast<std::function<void(size_t)>*>(user_data);
            if (target && *target) {
                (*target)(bytes);
            }
        };

        engine_set_progress_callback(
            handle_.get(),
            trampoline,
            callback_holder_.get(),
            nullptr
        );
    }

    // Зручна обробка через контейнери та std::span
    std::vector<uint8_t> process(std::span<const uint8_t> input) {
        std::vector<uint8_t> output(input.size());
        size_t out_len = output.size();

        engine_status_t st = engine_process(handle_.get(),
                                            input.data(),
                                            input.size(),
                                            output.data(),
                                            &out_len);
        if (st != ENGINE_STATUS_OK) {
            throw std::runtime_error(std::string("Помилка обробки блоку даних: ") + 
                                     engine_get_last_error());
        }
        output.resize(out_len);
        return output;
    }

private:
    ScopedEngineHandle handle_;
    std::unique_ptr<std::function<void(size_t)>> callback_holder_;
};

int main() {
    try {
        CryptoEngine engine("XOR-FAST");

        size_t total_processed = 0;
        engine.set_progress_handler([&total_processed](size_t bytes) {
            total_processed += bytes;
            std::cout << "[C++ Client] Прогрес: оброблено +" << bytes 
                      << " байтів (сумарно: " << total_processed << ")\n";
        });

        const std::vector<uint8_t> input_data = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
        auto result = engine.process(input_data);

        std::cout << "[C++ Client] Завершено успішно. Результат[" << result.size() 
                  << " байтів], перший байт: 0x" << std::hex 
                  << static_cast<int>(result[0]) << std::dec << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "[C++ Client] Виняток: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## 5. Динамічне завантаження бібліотеки під час виконання (Explicit FFI Loading)

Однією з найсильніших переваг C-ABI є можливість завантажувати скомпільовану бібліотеку динамічно в процесі роботи програми (Dynamic Plugin Architecture). Клієнтський додаток не потребує лінкування з імпортною бібліотекою на етапі збирання: адреси функцій отримуються безпосередньо з таблиці експорту за їхніми текстовими C-іменами.

Нижче наведено приклад реалізації динамічного завантажувача з використанням системного API Unix (`dlopen` / `dlsym`):

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <stdint.h>

/* Оголошення покажчиків на функції за C-сигнатурами */
typedef struct engine_ctx_t engine_ctx_t;
typedef int (*fn_engine_create)(const char*, engine_ctx_t**);
typedef void (*fn_engine_destroy)(engine_ctx_t*);
typedef int (*fn_engine_process)(engine_ctx_t*, const uint8_t*, size_t, uint8_t*, size_t*);
typedef const char* (*fn_engine_get_last_error)(void);

int main(void) {
    void* lib_handle = dlopen("./libengine.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib_handle) {
        fprintf(stderr, "Не вдалося завантажити бібліотеку: %s\n", dlerror());
        return EXIT_FAILURE;
    }

    /* Отримання адрес неспотворених C-символів */
    fn_engine_create p_create = (fn_engine_create)dlsym(lib_handle, "engine_create");
    fn_engine_destroy p_destroy = (fn_engine_destroy)dlsym(lib_handle, "engine_destroy");
    fn_engine_process p_process = (fn_engine_process)dlsym(lib_handle, "engine_process");
    fn_engine_get_last_error p_error = (fn_engine_get_last_error)dlsym(lib_handle, "engine_get_last_error");

    if (!p_create || !p_destroy || !p_process || !p_error) {
        fprintf(stderr, "Помилка пошуку C-символів у бібліотеці: %s\n", dlerror());
        dlclose(lib_handle);
        return EXIT_FAILURE;
    }

    engine_ctx_t* ctx = NULL;
    if (p_create("XOR-FAST", &ctx) != 0) {
        fprintf(stderr, "Помилка ініціалізації: %s\n", p_error());
        dlclose(lib_handle);
        return EXIT_FAILURE;
    }

    const uint8_t msg[] = { 0xAA, 0xBB, 0xCC };
    uint8_t out[16];
    size_t out_len = sizeof(out);

    p_process(ctx, msg, sizeof(msg), out, &out_len);
    printf("[Dynamic C] Успішно виконано динамічний виклик. Довжина: %zu\n", out_len);

    p_destroy(ctx);
    dlclose(lib_handle);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <dlfcn.h>
#include <stdexcept>

// RAII обгортка для дескриптора динамічної бібліотеки dlopen
struct DynamicLibDeleter {
    void operator()(void* handle) const noexcept {
        if (handle) dlclose(handle);
    }
};

using ScopedSharedLib = std::unique_ptr<void, DynamicLibDeleter>;

class DynamicEngineLoader {
public:
    explicit DynamicEngineLoader(const std::string& lib_path) {
        void* handle = dlopen(lib_path.c_str(), RTLD_NOW | RTLD_LOCAL);
        if (!handle) {
            throw std::runtime_error(std::string("Помилка завантаження бібліотеки: ") + dlerror());
        }
        lib_ = ScopedSharedLib(handle);

        create_fn_ = reinterpret_cast<CreateFn>(dlsym(lib_.get(), "engine_create"));
        destroy_fn_ = reinterpret_cast<DestroyFn>(dlsym(lib_.get(), "engine_destroy"));
        process_fn_ = reinterpret_cast<ProcessFn>(dlsym(lib_.get(), "engine_process"));
        error_fn_ = reinterpret_cast<ErrorFn>(dlsym(lib_.get(), "engine_get_last_error"));

        if (!create_fn_ || !destroy_fn_ || !process_fn_ || !error_fn_) {
            throw std::runtime_error(std::string("Не знайдено C-символи: ") + dlerror());
        }
    }

    void run_demo() {
        struct engine_ctx_t* ctx = nullptr;
        if (create_fn_("XOR-FAST", &ctx) != 0) {
            throw std::runtime_error(std::string("Збій створення: ") + error_fn_());
        }

        const std::vector<uint8_t> data = {0xAA, 0xBB, 0xCC};
        std::vector<uint8_t> out(data.size());
        size_t out_len = out.size();

        process_fn_(ctx, data.data(), data.size(), out.data(), &out_len);
        std::cout << "[Dynamic C++] Успішно опрацьовано " << out_len << " байтів через dlopen/dlsym\n";

        destroy_fn_(ctx);
    }

private:
    using CreateFn = int (*)(const char*, struct engine_ctx_t**);
    using DestroyFn = void (*)(struct engine_ctx_t*);
    using ProcessFn = int (*)(struct engine_ctx_t*, const uint8_t*, size_t, uint8_t*, size_t*);
    using ErrorFn = const char* (*)(void);

    ScopedSharedLib lib_;
    CreateFn create_fn_{nullptr};
    DestroyFn destroy_fn_{nullptr};
    ProcessFn process_fn_{nullptr};
    ErrorFn error_fn_{nullptr};
};

int main() {
    try {
        DynamicEngineLoader loader("./libengine.so");
        loader.run_demo();
    } catch (const std::exception& ex) {
        std::cerr << "[Dynamic C++] Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## 6. Багатомовна інтеграція: виклик із Rust та Python

Уніфікований C-ABI дозволяє використовувати розроблений модуль у будь-якому сторонньому середовищі без написання складних перехідників:

### Інтеграція в Rust
У мові Rust взаємодія базується на блоках `extern "C"`. Типізація повністю повторює публічний заголовок:

```rust
// Приклад Rust FFI обгортки над engine_api.h
#[repr(C)]
#[derive(Copy, Clone, PartialEq, Debug)]
pub enum EngineStatus {
    Ok = 0,
    ErrInvalidArg = -1,
    ErrOutOfMemory = -2,
    ErrProcessing = -3,
    ErrUnknown = -4,
}

#[repr(C)]
pub struct EngineCtx {
    _private: [u8; 0], // Incomplete / Opaque type
}

extern "C" {
    pub fn engine_create(name: *const libc::c_char, out_ctx: *mut *mut EngineCtx) -> EngineStatus;
    pub fn engine_destroy(ctx: *mut EngineCtx);
    pub fn engine_process(
        ctx: *mut EngineCtx,
        input: *const u8,
        input_len: usize,
        output: *mut u8,
        inout_output_len: *mut usize,
    ) -> EngineStatus;
    pub fn engine_get_last_error() -> *const libc::c_char;
}

// Безпечна RAII обгортка в Rust
pub struct SafeEngine {
    raw: *mut EngineCtx,
}

impl SafeEngine {
    pub fn new(algo: &str) -> Result<Self, String> {
        let c_algo = std::ffi::CString::new(algo).unwrap();
        let mut raw = std::ptr::null_mut();
        unsafe {
            let status = engine_create(c_algo.as_ptr(), &mut raw);
            if status != EngineStatus::Ok {
                let err_ptr = engine_get_last_error();
                let err_str = std::ffi::CStr::from_ptr(err_ptr).to_string_lossy().into_owned();
                return Err(err_str);
            }
            Ok(SafeEngine { raw })
        }
    }
}

impl Drop for SafeEngine {
    fn drop(&mut self) {
        unsafe {
            engine_destroy(self.raw);
        }
    }
}
```

### Інтеграція в Python через `ctypes`
У середовищі Python динамічна бібліотека завантажується за кілька рядків коду, а покажчик дескриптора зберігається як `c_void_p`:

```python
# Приклад завантаження та виклику C-API через Python ctypes
import ctypes
from ctypes import c_char_p, c_int, c_size_t, c_uint8, POINTER, c_void_p

lib = ctypes.CDLL("./libengine.so")

# Налаштування сигнатур функцій
lib.engine_create.argtypes = [c_char_p, POINTER(c_void_p)]
lib.engine_create.restype = c_int

lib.engine_destroy.argtypes = [c_void_p]
lib.engine_destroy.restype = None

lib.engine_process.argtypes = [
    c_void_p,
    POINTER(c_uint8),
    c_size_t,
    POINTER(c_uint8),
    POINTER(c_size_t),
]
lib.engine_process.restype = c_int

lib.engine_get_last_error.argtypes = []
lib.engine_get_last_error.restype = c_char_p

# Створення об'єкта
ctx = c_void_p()
st = lib.engine_create(b"XOR-FAST", ctypes.byref(ctx))
if st != 0:
    raise RuntimeError(lib.engine_get_last_error().decode("utf-8"))

try:
    # Обробка даних
    data = (c_uint8 * 4)(0x11, 0x22, 0x33, 0x44)
    out_buf = (c_uint8 * 4)()
    out_len = c_size_t(4)

    st = lib.engine_process(ctx, data, 4, out_buf, ctypes.byref(out_len))
    if st != 0:
        raise RuntimeError(lib.engine_get_last_error().decode("utf-8"))

    print(f"[Python Client] Результат: {[hex(x) for x in out_buf]}")
finally:
    lib.engine_destroy(ctx)
```

## 7. Конфігурація збирання CMake та версіонування символів

Для коректного формування динамічної бібліотеки в системі збирання CMake необхідно налаштувати правила експорту символів та приховати всі внутрішні реалізації C++.

```cmake
cmake_minimum_required(VERSION 3.20)
project(EngineCoreLibrary LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Глобальне приховування символів у Linux/macOS
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# Створення динамічної бібліотеки
add_library(engine SHARED
    src/engine_api.cpp
)

# Визначення макроса ENGINE_EXPORTS під час компіляції самої бібліотеки
target_compile_definitions(engine PRIVATE ENGINE_EXPORTS)

target_include_directories(engine PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Версіонування бібліотеки для Linux (soname)
set_target_properties(engine PROPERTIES
    VERSION 1.0.0
    SOVERSION 1
)
```

У середовищі Linux для захисту від випадкового підмішування однакових імен у спільний адресний простір додатково застосовують карту символів компонувача (Linker Version Script, наприклад `engine.map`):

```text
ENGINE_1.0 {
    global:
        engine_create;
        engine_destroy;
        engine_process;
        engine_set_progress_callback;
        engine_get_last_error;
    local:
        *;
};
```

Такий скрипт передається компонувальнику через прапорець `-Wl,--version-script=engine.map` і гарантує, що жодна внутрішня допоміжна функція чи спотворений символ класу `EngineCore` не потрапить до динамічної таблиці `.dynsym`.

## 8. Простеження життєвого циклу пам'яті та потокобезпека

Розглянемо фізичний стан оперативної пам'яті під час проходження всіх етапів роботи з дескриптором `engine_ctx_t`:

1. **Фаза створення (`engine_create`).** 
   - Виклик `std::make_unique<engine_ctx_t>()` виділяє блок розміром 8 байтів у купі під покажчик `std::unique_ptr<EngineCore>`.
   - Конструктор `EngineCore` виділяє пам'ять під об'єкт класу, динамічний буфер `std::string` (якщо довжина рядка перевищує Small String Optimization буфер, зазвичай 15 байтів) та викликає `reserve(8192)` для вектора, резервуючи 8 КіБ неперервної пам'яті. Усі структури вирівнюються за межами 8 або 16 байтів згідно з вимогами цільової архітектури.
   - Якщо на будь-якому з цих етапів виникає брак пам'яті (`std::bad_alloc`), розумні покажчики автоматично звільняють уже виділені блоки в зворотному порядку, а `*out_ctx` залишається рівним `nullptr`. Витік пам'яті виключений.
2. **Фаза обробки (`engine_process`).**
   - Функція не виконує жодних динамічних алокацій пам'яті, якщо вихідний буфер передано клієнтом. Робота відбувається безпосередньо над сирими масивами пам'яті, що забезпечує максимальну пропускну здатність шини пам'яті (Memory Bandwidth).
3. **Фаза знищення (`engine_destroy`).**
   - Створення тимчасового об'єкта `std::unique_ptr<engine_ctx_t> cleaner(ctx)` передає контроль деструктору `unique_ptr`.
   - Деструктор викликає `delete ctx`, що запускає деструктор `EngineCore`.
   - Звільняється буфер `std::vector`, рядок `algorithm_`, і, якщо була зареєстрована функція `cleanup_`, викликається очищення користувацького контексту `user_data_`.

Щодо моделі багатопотоковості (Concurrency Model):
- Сам дескриптор `engine_ctx_t` за замовчуванням є потоко-небезпечним для одночасного запису: два потоки не повинні одночасно викликати `engine_process` над одним і тим самим екземпляром дескриптора без зовнішнього м'ютекса.
- Проте різні потоки можуть абсолютно безпечно створювати й незалежно використовувати власні окремі дескриптори `engine_ctx_t` паралельно, оскільки стан `EngineCore` повністю інкапсульований і не використовує спільних глобальних змінних.
- Повідомлення про помилки зберігаються в `thread_local std::string`, тому виклик `engine_get_last_error()` повертає діагностику виключно того збою, що стався в поточному потоці виконання, не перетираючи повідомлення інших потоків.

## 9. Глибокий аналіз низькорівневого виконання, накладних витрат та бар'єра винятків

Щоб оцінити продуктивність запропонованого C-API, проаналізуємо накладні витрати (Overhead) у щасливому шляху (Happy Path) та під час виникнення помилок:

- **Витрати на виклик функції:** Прямий виклик `engine_process` через таблицю символів виконується через стандартну інструкцію процесора `call`. Він займає стільки ж тактів, скільки будь-яка звичайна функція мови C (близько 1–2 наносекунд).
- **Витрати на блок try/catch (Zero-Cost Exceptions):** У сучасних компіляторах за стандартом Itanium ABI реалізована безвитратна модель винятків за таблицями. Доки виняток не згенеровано, виконання блоку `try` не додає жодної додаткової інструкції перевірки в асемблерний потік. Таблиці `.eh_frame` розміщуються в окремих секціях пам'яті, які не завантажуються в кеш процесора під час нормального виконання коду.
- **Витрати на трамплін зворотного виклику:** Статична функція-трамплін виконує лише одне перекладання регістра `mov %rsi, %rdi` та прямий стрибок `jmp` на метод обробника. Це не викликає скидання конвеєра процесора чи промахів кешу команд, забезпечуючи практично нульову ціну абстракції.

Проте під час генерації винятку процесор переходить у режим важкої обробки:
1. Виконується функція `__cxa_throw`, яка зупиняє лінійне виконання і запускає двофазне розгортання стека (Search Phase та Cleanup Phase).
2. Підсистема `__gxx_personality_v0` покроково сканує дескриптори `.gcc_except_table` для кожного стекового кадру.
3. Знайшовши запис перехоплення у функції `engine_process`, середовище викликає деструктори локальних об'єктів C++ і передає керування на Landing Pad у гілку `catch`.
4. Текст повідомлення копіюється в `thread_local std::string`, а функція повертає числовий код через регістр `%eax`.

Оскільки винятки є винятковими подіями, така затримка (близько кількох мікросекунд) є цілком прийнятною і повністю захищає клієнтський додаток від падіння.

## 10. Пастки та критичні помилки на двійковій межі C/C++

Під час проектування й супроводу C-сумісних інтерфейсів розробники найчастіше стикаються з п'ятьма категоріями критичних дефектів:

### 1. Невідповідність алокаторів пам'яті (CRT Allocator Mismatch)
Якщо пам'ять для екземпляра виділяється всередині бібліотеки через C++ оператор `new` (або `std::make_unique`), а клієнтський додаток викликає стандартну функцію `free(ctx)` з бібліотеки `libc`, виникає фатальна аварія пам'яті. По-перше, не викликаються деструктори внутрішніх полів (`std::string`, `std::vector`, файлові дескриптори), що спричиняє витік системних ресурсів. По-друге, в операційних системах (зокрема Windows під час статичного лінкування C Runtime або при різних версіях `msvcrt.dll`) бібліотека та клієнтський додаток мають окремі незалежні пули купи (Heap). Спроба звільнити блок з однієї купи функцією з іншої призводить до негайного падіння з помилкою `Heap Corruption`. Звільнення ресурсів завжди повинно відбуватися виключно через експортовану функцію `engine_destroy`.

### 2. Вихід винятків у стек C-викликів
Якщо всередині C++ методу генерується виняток, а C-обгортка не перехоплює його через `catch (...)`, механізм розгортання стека починає шукати обробник у стекових кадрах клієнта на мові C. Оскільки код мовою C зазвичай компілюється без інформації про винятки (без таблиць DWARF `.eh_frame` у Linux або структурованих таблиць SEH у Windows), підсистема розгортання втрачає контекст і викликає аварійне завершення `std::terminate()`. Повний бар'єр винятків у кожній точці входу C-API є обов'язковою вимогою надійності.

### 3. Час життя та синхронізація покажчика `user_data`
У синхронних API час життя об'єкта, переданого у `user_data`, прив'язаний до тривалості виклику `engine_process`. Проте якщо обробка виконується асинхронно у фонових потоках бібліотеки, передача покажчика на локальну стекову змінну призводить до виникнення висячого покажчика (Dangling Pointer) і звернення до зруйнованого стеку. Для асинхронних API обов'язково впроваджується параметр `engine_cleanup_cb`: бібліотека бере на себе володіння контекстом і викликає функцію очищення під час власного знищення або завершення фонового завдання.

### 4. Порушення вирівнювання структур при передачі за значенням
Передача складних структур за значенням через C-API є джерелом прихованих помилок ABI. Якщо структура містить поля різних розмірів, різні компілятори або різні налаштування оптимізації можуть вставити різну кількість байтів заповнення (Padding). Щоб уникнути розбіжностей у зсувах полів, C-API повинен або передавати непрозорі покажчики, або суворо дотримуватися вимог Standard Layout із обов'язковою перевіркою `static_assert(sizeof(MyStruct) == EXPECTED_SIZE)` та `static_assert(offsetof(MyStruct, field) == EXPECTED_OFFSET)`.

### 5. Приховування внутрішніх символів (Symbol Stripping & Hidden Visibility)
Під час компіляції бібліотеки на C++ усі внутрішні допоміжні класи, методи та функції ядра можуть випадково потрапити до таблиці експортованих динамічних символів `.dynsym`, якщо компілятор працює з налаштуваннями видимості за замовчуванням (`-fvisibility=default`). Це не лише збільшує розмір двійкового файлу та час його завантаження динамічним лінкером, але й створює ризик колізій імен із іншими бібліотеками в адресному просторі процесу. Правильна інженерна практика полягає в компіляції всієї бібліотеки з прапорцем `-fvisibility=hidden` та явному експорті виключно функцій публічного C-API через макрос `ENGINE_API` (`__attribute__((visibility("default")))`).
