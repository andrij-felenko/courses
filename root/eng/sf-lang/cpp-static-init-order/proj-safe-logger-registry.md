# ⚙️ Безпечний реєстр служб та журналювання без катастрофи ініціалізації

У великих проектах мовами C та C++ окремі підсистеми (мережевий стек, сервіс аутентифікації, драйвери периферії, планувальник завдань) мають записувати діагностичні події у єдиний глобальний журнал або реєструватися у центральному диспетчері ще на стадії ініціалізації середовища процесу. Якщо реалізувати ці міжмодульні залежності через звичайні глобальні змінні, порядок зв'язування файлів компонувальником операційної системи спричиняє колізію: конструктор одного сервісу звертається до неініціалізованої пам'яті іншого.

Нижче розглянуто покрокове відтворення катастрофи статичної ініціалізації, автоматичну діагностику дефекту через санітайзери пам'яті, три практичні інженерні патерни усунення проблеми та аналіз крайових випадків у динамічних бібліотеках.

## Відтворення аварії між трьома одиницями трансляції

Створимо мінімальну модель системи, рознесену по трьох вихідних файлах: модуль журналу (`logger.cpp`), залежна мережева служба (`service.cpp`) та точка входу програми (`main.cpp`).

Заголовок журналу визначає інтерфейс та експортує глобальний об'єкт:

:::tabs
```cpp
// logger.hpp
#pragma once
#include <string>
#include <iostream>

class Logger {
public:
    explicit Logger(const std::string& prefix) : m_prefix(prefix), m_ready(true) {
        std::cout << "[LOG INIT] Журнал " << m_prefix << " активовано\n";
    }

    void log(const std::string& msg) const {
        if (!m_ready) {
            std::cerr << "[FATAL] Спроба запису в неініціалізований журнал!\n";
        }
        std::cout << "[" << m_prefix << "] " << msg << "\n";
    }

private:
    std::string m_prefix;
    bool m_ready{false};
};

// Глобальне оголошення зовнішнього символу
extern Logger g_logger;
```
```c
/* logger_c.h - інтерфейс для мови C */
#ifndef LOGGER_C_H
#define LOGGER_C_H

#include <stdio.h>
#include <stdbool.h>

typedef struct {
    const char* prefix;
    bool ready;
} CLogger;

extern CLogger g_c_logger;
void c_logger_init(const char* prefix);
void c_logger_log(const char* msg);

#endif
```
:::

Визначення глобального об'єкта журналу розташовується у файлі `logger.cpp`:

```cpp
// logger.cpp
#include "logger.hpp"

// Визначення екземпляра
Logger g_logger("SYSTEM_LOG");
```

Залежна служба намагається зафіксувати старт власної роботи безпосередньо у тілі свого конструктора під час старту програми:

```cpp
// service.cpp
#include "logger.hpp"

class NetworkService {
public:
    NetworkService() {
        // Критична залежність: g_logger повинен бути готовим до роботи
        g_logger.log("NetworkService: налаштування сокетів та протоколів зв'язку");
    }
};

// Глобальний об'єкт мережевої служби
NetworkService g_network_service;
```

Точка входу викликає журналювання вже після входу у функцію `main()`:

```cpp
// main.cpp
#include "logger.hpp"

int main() {
    g_logger.log("main(): виконання основного робочого циклу");
    return 0;
}
```

Поведінка програми тепер повністю залежить від черговості об'єктних файлів під час виклику компілятора:

1. **Успішний порядок збирання:**
   ```bash
   g++ logger.cpp service.cpp main.cpp -o app_ok
   ./app_ok
   ```
   Компонувальник розміщує ініціалізатор `logger.cpp` першим у секції `.init_array`. Програма виводить повідомлення про успішний старт і коректно завершується.

2. **Аварійний порядок збирання (SIOF):**
   ```bash
   g++ service.cpp logger.cpp main.cpp -o app_crash
   ./app_crash
   ```
   Компонувальник розміщує ініціалізатор `service.cpp` першим. Під час запуску процесу конструктор `NetworkService` викликає метод `g_logger.log()` над пам'яттю, де виконано лише нульову фазу (`.bss`). Внутрішні поля `std::string` містять нульові покажчики, і програма падає з помилкою `Segmentation fault (core dumped)` ще до передачі керування у `main()`.

Ця катастрофа виникає через те, що стандарт C++ не гарантує жодного детермінованого порядку виконання функцій із секції `.init_array` між різними об'єктними файлами. Перестановка аргументів у скрипті збирання або зміна оптимізацій компонувальника мовчки ламає працездатність бінарного образу.

## Діагностика через AddressSanitizer

Компілятори GCC та Clang мають вбудований динамічний інструмент виявлення порушень порядку статичної ініціалізації:

```bash
g++ -fsanitize=address -g service.cpp logger.cpp main.cpp -o app_asan
ASAN_OPTIONS=check_initialization_order=1:strict_init_order=true ./app_asan
```

AddressSanitizer використовує механізм тіньової пам'яті (shadow memory): для кожних восьми байтів адресного простору процесу виділяється один байт тіні, який фіксує доступність пам'яті для читання та запису.

Перед стартом конструкторів рантайм санітайзера забарвлює (отруює червоними зонами) пам'ять усіх глобальних змінних. Щойно конструктор конкретної змінної завершує свою роботу, санітайзер знімає блокування з відповідних тіньових байтів. Якщо конструктор з іншого файлу намагається прочитати байти об'єкта до зняття блокування, ASan миттєво генерує діагностичний звіт:

```text
=================================================================
==18420==ERROR: AddressSanitizer: initialization-order-fiasco on address 0x00000123
READ of size 8 at 0x00000123 thread T0
    #0 0x... in std::__cxx11::basic_string<...>::basic_string
    #1 0x... in Logger::log(std::string const&) logger.hpp:12
    #2 0x... in NetworkService::NetworkService() service.cpp:6
    #3 0x... in __static_initialization_and_destruction_0 service.cpp:11
    #4 0x... in _GLOBAL__sub_I_service.cpp service.cpp:13
0x00000123 is located inside of global variable 'g_logger' defined in 'logger.cpp:4'
=================================================================
```

Звіт чітко показує не тільки місце помилкового звернення (файл `service.cpp`, рядок 6), але й фізичне розташування самого неініціалізованого символу (`g_logger` у `logger.cpp`, рядок 4).

## Стратегія 1: Синглтон Мейєрса (Ініціалізація за першим викликом)

Найпростіший спосіб усунення проблеми в прикладному коді — інкапсуляція глобального об'єкта всередину статичного методу доступу з локальною статичною змінною:

:::tabs
```cpp
// safe_logger_meyers.hpp
#pragma once
#include <string>
#include <iostream>

class SafeLogger {
public:
    explicit SafeLogger(const std::string& prefix) : m_prefix(prefix) {
        std::cout << "[MEYERS INIT] Журнал " << m_prefix << " активовано\n";
    }

    void log(const std::string& msg) const {
        std::cout << "[" << m_prefix << "] " << msg << "\n";
    }

    // Фабричний метод доступу з гарантованою лінивою ініціалізацією
    static SafeLogger& instance() {
        // Потокобезпечно за стандартом C++11 (Magic Statics)
        static SafeLogger s_instance("SAFE_MEYERS_LOG");
        return s_instance;
    }

private:
    std::string m_prefix;
};
```
```c
/* safe_logger_c.h - потокобезпечна реалізація на C через pthread_once */
#ifndef SAFE_LOGGER_C_H
#define SAFE_LOGGER_C_H

#include <stdio.h>
#include <pthread.h>

typedef struct {
    const char* prefix;
} SafeCLogger;

SafeCLogger* get_safe_c_logger(void);
void safe_c_logger_log(const char* msg);

#endif
```
:::

У C-версії для забезпечення надійної потокобезпечної ініціалізації без ризику гонитви потоків застосовується функція `pthread_once`:

:::tabs
```c
/* safe_logger_c.c - реалізація на мові C */
#include "safe_logger_c.h"

static SafeCLogger g_c_logger_inst;
static pthread_once_t g_c_logger_once = PTHREAD_ONCE_INIT;

static void init_c_logger_internal(void) {
    g_c_logger_inst.prefix = "SAFE_C_LOG";
    printf("[C LOG INIT] %s активовано\n", g_c_logger_inst.prefix);
}

SafeCLogger* get_safe_c_logger(void) {
    pthread_once(&g_c_logger_once, init_c_logger_internal);
    return &g_c_logger_inst;
}

void safe_c_logger_log(const char* msg) {
    SafeCLogger* logger = get_safe_c_logger();
    printf("[%s] %s\n", logger->prefix, msg);
}
```
```cpp
// safe_logger_c_wrapper.cpp - еквівалентний C++ RAII адаптер
#include <iostream>
#include <string_view>
#include <mutex>

class SafeCppLoggerWrapper {
public:
    static void log(std::string_view msg) {
        std::call_once(s_init_flag, []() {
            s_prefix = "SAFE_CPP_LOG";
            std::cout << "[CPP LOG INIT] " << s_prefix << " активовано\n";
        });
        std::cout << "[" << s_prefix << "] " << msg << "\n";
    }

private:
    static inline std::string_view s_prefix;
    static inline std::once_flag s_init_flag;
};
```
:::

Коли потік виконання вперше викликає метод `instance()`, рантайм атомарно перевіряє системний прапорець за допомогою інструкцій `__cxa_guard_acquire`. Якщо ініціалізація ще не відбулася, викликається конструктор `SafeLogger`, після чого прапорець переводиться у стан готовності викликом `__cxa_guard_release`. Усі наступні звернення пропускають важку ініціалізацію та негайно повертають готове посилання.

## Стратегія 2: Ідіома Nifty Counter (Schwarz Counter)

Якщо розробник бібліотеки бажає надати користувачам природний синтаксис звернення до глобальної змінної без виклику функцій на кшталт `instance()`, застосовується підрахунок посилань у заголовковому файлі:

```cpp
// nifty_logger.hpp
#pragma once
#include <iostream>
#include <new>

class NiftyLogger {
public:
    void log(const char* msg) const {
        std::cout << "[NIFTY] " << msg << "\n";
    }
};

// Буфер сирої пам'яті для запобігання неконтрольованого виклику конструктора
extern alignas(NiftyLogger) char g_nifty_storage[];
#define g_nifty_logger (*reinterpret_cast<NiftyLogger*>(g_nifty_storage))

// Клас-ініціалізатор у заголовку
class NiftyInitializer {
public:
    NiftyInitializer();
    ~NiftyInitializer();
};

// Кожна одиниця трансляції отримує власну статичну копію
static NiftyInitializer s_nifty_init;
```

```cpp
// nifty_logger.cpp
#include "nifty_logger.hpp"

alignas(NiftyLogger) char g_nifty_storage[sizeof(NiftyLogger)];
static int g_nifty_counter = 0;

NiftyInitializer::NiftyInitializer() {
    if (g_nifty_counter++ == 0) {
        // Перший .cpp модуль створює об'єкт через placement new
        new (g_nifty_storage) NiftyLogger();
        std::cout << "[NIFTY INIT] Системний журнал сконструйовано\n";
    }
}

NiftyInitializer::~NiftyInitializer() {
    if (--g_nifty_counter == 0) {
        // Останній .cpp модуль викликає деструктор
        reinterpret_cast<NiftyLogger*>(g_nifty_storage)->~NiftyLogger();
        std::cout << "[NIFTY DESTROY] Системний журнал коректно звільнено\n";
    }
}
```

У цій схемі кожен `.cpp` файл, який робить `#include "nifty_logger.hpp"`, створює локальний статичний об'єкт `s_nifty_init`. Оскільки заголовок підключається на початку файлу, конструктор `s_nifty_init` гарантовано спрацьовує раніше за будь-які користувацькі глобальні змінні цієї одиниці трансляції. Під час завершення програми останній знищений `s_nifty_init` скидає лічильник до нуля і викликає явний деструктор журналу, запобігаючи аваріям під час виходу з процесу.

## Стратегія 3: C++20 constinit для максимальної швидкодії

Коли об'єкт не вимагає динамічного виділення пам'яті у купі (наприклад, використовує `std::string_view` або фіксовані структури даних), найкращим інженерним вибором є специфікатор `constinit`:

```cpp
// constinit_logger.hpp
#pragma once
#include <string_view>
#include <iostream>

class ConstinitLogger {
public:
    constexpr explicit ConstinitLogger(std::string_view tag) : m_tag(tag) {}

    void log(std::string_view msg) const {
        std::cout << "[" << m_tag << "] " << msg << "\n";
    }

private:
    std::string_view m_tag;
};

// Гарантовано заповнюється нульовою/константною фазою до старту .init_array
inline constinit ConstinitLogger g_constinit_log("SYSTEM_CONSTINIT");
```

Завдяки `constinit` об'єкт `g_constinit_log` стає доступним у пам'ять ще до того, як завантажувач викличе перший конструктор у секції `.init_array`. Це забезпечує нульовий накладний оверхед під час виконання та абсолютну безпеку доступу між модулями.

## Крайові випадки та пастки архітектури

Під час проєктування складних систем розробники часто стикаються з двома небезпечними пастками:

1. **Циклічні залежності між синглтонами Мейєрса.** Якщо конструктор класу `ServiceA` звертається до `ServiceB::instance()`, а конструктор `ServiceB` у процесі власного створення викликає `ServiceA::instance()`, виникає взаємне блокування (deadlock). Оскільки `ServiceA` вже захопив системний прапорець `__cxa_guard_acquire`, рекурсивний повторний вхід у той самий потік спричиняє або вічне очікування, або негайний виклик `std::terminate()`. Для усунення циклів конструктори обов'язково роблять тривіальними, а взаємне зв'язування переносять у фазу явного старту сервісів.
2. **Динамічне завантаження плагінів через dlopen.** Коли спільна бібліотека (`.so` або `.dll`) завантажується у рантаймі через виклик `dlopen()`, операційна система виконує її секцію `.init_array` у контексті поточного потоку. Якщо плагін покладається на глобальні змінні головного виконуваного файлу, які були оголошені з внутрішнім зв'язуванням (`static`), плагін створить власні дублікати цих змінних. Щоб уникнути розсинхронізації стану, експортовані ресурси ядра системи завжди реєструються через явні спільні інтерфейси.
