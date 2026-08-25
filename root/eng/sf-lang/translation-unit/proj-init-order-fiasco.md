# ⚙️ Практикум: діагностика й розв'язання Static Initialization Order Fiasco

У проєктах на мовах C та C++ глобальні змінні та об'єкти зі статичною тривалістю зберігання (*static storage duration*) несуть серйозну архітектурну загрозу. Стандарт мови C++ гарантує сувору послідовність виконання конструкторів у межах **однієї** одиниці трансляції: об'єкти створюються строго згори донизу, у порядку їхнього оголошення в сирцевому тексті. Проте між **різними** одиницями трансляції стандарт свідомо **не визначає жодного порядку ініціалізації**.

Якщо конструктор глобального об'єкта у файлі `logger.cpp` під час виконання звертається до глобального об'єкта конфігурації у файлі `config.cpp`, результат запуску програми залежить від випадкового порядку, у якому компонувальник (лінкер) обробив об'єктні файли. Програма може місяцями стабільно працювати в тестовому середовищі й раптово падати з аварійним завершенням `SIGSEGV` на сервері після простої зміни порядку вихідних файлів у файлі збірки `CMakeLists.txt`. Ця класична інженерна пастка має усталену назву — **Static Initialization Order Fiasco (SIOF)**.

## Анатомія запуску: секції .init_array та .fini_array

Щоб зрозуміти, чому виникає хаос порядку, необхідно простежити, як компілятор і завантажувач операційної системи взагалі запускають код до виклику функції `main()`.

Коли компілятор зустрічає в одиниці трансляції глобальний об'єкт із нетривіальним конструктором (тобто таким, що виконує динамічний код, виділяє пам'ять чи відкриває файли), він виконує кілька прихованих кроків:
1. Генерує анонімну службову функцію ініціалізації (наприклад, `_GLOBAL__sub_I_logger.cpp`).
2. У тіло цієї функції компілятор записує виклики конструкторів усіх глобальних об'єктів цієї TU в порядку їхнього оголошення.
3. Поміщає покажчик на цю службову функцію у спеціальну секцію об'єктного файлу — `.init_array` (у двійковому форматі ELF для Linux) або `.CRT$XCU` (у форматі PE/COFF для Windows).

Коли лінкер збирає докупи готові об'єктні файли `logger.o`, `config.o` та `main.o`, він просто об'єднує масиви покажчиків із секцій `.init_array` кожного файлу в єдину монолітну таблицю. Порядок запису адрес у цій таблиці збігається з порядком аргументів командного рядка або чергою обробки файлів.

Під час старту процесу завантажувач передає керування функції точки входу C-рантайму (`_start` у glibc), яка перед викликом `main()` проходить циклом по масиву `.init_array` і по черзі викликає кожну функцію-ініціалізатор. Якщо функція ініціалізації `logger.o` опинилася в масиві раніше за `config.o`, конструктор логера почне виконуватися в момент, коли пам'ять об'єкта конфігурації ще не містить валідних даних.

## Відтворення катастрофи на мінімальному проєкті

Проілюструємо проблему на мінімальному практичному прикладі з трьох файлів: конфігурації підсистеми, модуля логування та головного файлу програми.

:::tabs
```c
// config.h
#ifndef CONFIG_H
#define CONFIG_H

typedef struct {
    int max_retries;
    int is_initialized;
} Config;

extern Config g_config;
void config_init(void);

#endif // CONFIG_H
```
```cpp
// config.hpp
#pragma once
#include <string>

class Config {
public:
    Config() : log_prefix_("[APP_CORE]") {}
    
    [[nodiscard]] const std::string& prefix() const noexcept {
        return log_prefix_;
    }
private:
    std::string log_prefix_;
};

// Глобальний об'єкт із нетривіальним конструктором (External Linkage)
extern Config g_config;
```
:::

Тепер опишемо модуль логування, конструктор якого звертається до глобальної конфігурації для запису інформаційного повідомлення про готовність підсистеми:

:::tabs
```c
// logger.c
#include "config.h"
#include <stdio.h>

Config g_config;

void config_init(void) {
    g_config.max_retries = 3;
    g_config.is_initialized = 1;
}

void log_message(const char* msg) {
    if (!g_config.is_initialized) {
        fprintf(stderr, "FATAL: config is not initialized yet!\n");
        return;
    }
    printf("%s (retries=%d)\n", msg, g_config.max_retries);
}
```
```cpp
// logger.hpp
#pragma once
#include "config.hpp"
#include <iostream>
#include <string_view>

class Logger {
public:
    Logger() {
        // Небезпека: g_config у сусідньому TU може бути ще не сконструйованим!
        // Читання поля std::string призведе до звернення до нульового покажчика.
        std::cout << g_config.prefix() << " Logger subsystem online.\n";
    }

    void log(std::string_view message) const {
        std::cout << g_config.prefix() << " " << message << "\n";
    }
};

extern Logger g_logger;
```
:::

Тепер підготуємо файли реалізації та точку входу:

:::tabs
```c
// main.c
#include "config.h"
#include <stdio.h>

int main(void) {
    config_init();
    printf("C program started.\n");
    return 0;
}
```
```cpp
// config.cpp
#include "config.hpp"
Config g_config;

// logger.cpp
#include "logger.hpp"
Logger g_logger;

// main.cpp
#include "logger.hpp"

int main() {
    g_logger.log("Application main() reached.");
    return 0;
}
```
:::

### Спостереження аварії в компіляторі

Зберемо бінарний файл, передавши `config.cpp` першим у списку компіляції:

```bash
g++ -std=c++20 config.cpp logger.cpp main.cpp -o app_working
./app_working
# Вивід:
# [APP_CORE] Logger subsystem online.
# [APP_CORE] Application main() reached.
```

Усе працює, оскільки лінкер зберіг порядок: спочатку ініціалізатор `config.o`, потім `logger.o`. Тепер змінимо лише порядок вихідних файлів у команді збірки:

```bash
g++ -std=c++20 logger.cpp config.cpp main.cpp -o app_broken
./app_broken
# Результат:
# Segmentation fault (core dumped)
```

Програма завершилася аварійно, навіть не дійшовши до функції `main()`. За допомогою зневаджувача `gdb` або `lldb` можна переконатися, що падіння відбулося всередині методу `std::string::size()` або `_M_data()`: об'єкт `std::string log_prefix_` у момент виклику містив сирі нульові байти з сегмента `.bss`, оскільки його конструктор ще не запускався.

## Автоматична діагностика через AddressSanitizer

Ручний пошук подібних помилок у великих проєктах з тисячами вихідних файлів надзвичайно складний: помилка не проявляється під час звичайної компіляції, лінкер не видає попереджень, а збірка може падати лише на окремих операційних системах або архітектурах.

Сучасні інструментальні засоби GCC та Clang мають вбудований динамічний аналізатор порядку ініціалізації в складі AddressSanitizer:

```bash
g++ -std=c++20 -fsanitize=address -g logger.cpp config.cpp main.cpp -o app_sanitized
ASAN_OPTIONS=check_initialization_order=true:strict_init_order=true ./app_sanitized
```

AddressSanitizer перехоплює звернення до глобальної пам'яті у фазі запуску й видає точний діагностичний звіт:

```
==18421==ERROR: AddressSanitizer: initialization-order-fiasco on address 0x0000004051a0
READ of size 8 at 0x0000004051a0 thread T0
    #0 0x401264 in std::__cxx11::basic_string<char>::_M_data() const
    #1 0x4011aa in Config::prefix() const config.hpp:8
    #2 0x4011eb in Logger::Logger() logger.hpp:8
    #3 0x401231 in __static_initialization_and_destruction_0() logger.cpp:3
0x0000004051a0 is located inside the global variable 'g_config' defined in 'config.cpp'
```

Санітайзер чітко вказує: файл `logger.cpp` намагався прочитати байти за адресою змінної `g_config` до того, як її ініціалізатор був викликаний завантажувачем.

## Розв'язання 1: Патерн Construct-On-First-Use (Meyers' Singleton)

Найелегантнішим та найнадійнішим способом ліквідації SIOF є патерн «створення при першому використанні» (*Construct-On-First-Use*), популяризований Скоттом Мейєрсом (*Scott Meyers*).

Ідея полягає у відмові від нелокальних глобальних змінних: замість відкритого об'єкта надається глобальна або вбудована (`inline`) функція, що повертає посилання на локальну `static`-змінну.

:::tabs
```c
// config_safe.h
#ifndef CONFIG_SAFE_H
#define CONFIG_SAFE_H

typedef struct {
    int max_retries;
    int is_initialized;
} Config;

Config* get_config(void);

#endif // CONFIG_SAFE_H

// config_safe.c
#include "config_safe.h"

Config* get_config(void) {
    // У C локальний static ініціалізується нулями або константним виразом
    static Config instance = { .max_retries = 3, .is_initialized = 1 };
    return &instance;
}
```
```cpp
// config_safe.hpp
#pragma once
#include <string>

class Config {
public:
    Config() : log_prefix_("[APP_SAFE]") {}
    
    [[nodiscard]] const std::string& prefix() const noexcept {
        return log_prefix_;
    }
};

// Замість глобальної змінної — функція доступу
inline Config& get_config() {
    // Стандарт C++11 (Magic Statics): локальна статична змінна ініціалізується
    // строго при першому вході в функцію з повною потокобезпекою.
    static Config instance;
    return instance;
}
```
:::

Тепер клас `Logger` безпечно звертається до функції `get_config()`:

:::tabs
```c
// logger_safe.c
#include "config_safe.h"
#include <stdio.h>

void safe_log(const char* message) {
    Config* cfg = get_config();
    printf("[%d] %s\n", cfg->max_retries, message);
}
```
```cpp
// logger_safe.hpp
#pragma once
#include "config_safe.hpp"
#include <iostream>
#include <string_view>

class Logger {
public:
    Logger() {
        // Гарантовано безпечно: перший виклик get_config() змусить рантайм
        // сконструювати instance перед тим, як повернути посилання.
        std::cout << get_config().prefix() << " Logger online safely.\n";
    }

    void log(std::string_view message) const {
        std::cout << get_config().prefix() << " " << message << "\n";
    }
};

inline Logger& get_logger() {
    static Logger instance;
    return instance;
}
```
:::

### Як працює механізм Magic Statics під капотом

Починаючи зі стандарту C++11, ініціалізація локальних статичних змінних є гарантовано **потокобезпечною**. Компілятор генерує прихований 64-бітний прапорець захисту (*guard variable*) поруч зі змінною:

```cpp
// Псевдокод того, що насправді генерує компілятор для static Config instance:
static uint64_t guard_flag = 0;
static alignas(Config) char instance_storage[sizeof(Config)];

if ((guard_flag & 0xFF) == 0) { // Швидка атомарна перевірка
    if (__cxa_guard_acquire(&guard_flag)) { // Захоплення системного м'ютекса
        try {
            new (instance_storage) Config();
            __cxa_guard_release(&guard_flag); // Позначення успішної ініціалізації
        } catch (...) {
            __cxa_guard_abort(&guard_flag);
            throw;
        }
    }
}
return *reinterpret_cast<Config*>(instance_storage);
```

Завдяки цьому перший потік, який звернувся до функції, виконує конструктор, а всі паралельні потоки коректно чекають завершення конструювання без ризику читання частково ініціалізованої пам'яті.

## Розв'язання 2: C++20 constinit і статична фаза ініціалізації

Ініціалізація змінних у C++ поділяється на дві принципові фази:
1. **Статична ініціалізація** (*Static Initialization*): виконується компілятором під час збірки (Zero Initialization + Constant Initialization). Значення записуються безпосередньо у бінарний файл.
2. **Динамічна ініціалізація** (*Dynamic Initialization*): виконується під час старту програми викликом конструкторів із секції `.init_array`.

Ключове слово `constinit` (введене в C++20) вимагає від компілятора, щоб змінна зі статичним або потоковим часом життя була ініціалізована строго на етапі компіляції:

```cpp
// compile_time_config.hpp (C++20)
#pragma once
#include <string_view>

struct FastConfig {
    std::string_view prefix;
    int max_retries;

    // constexpr-конструктор дозволяє обчислення під час компіляції
    constexpr FastConfig(std::string_view p, int r) noexcept
        : prefix(p), max_retries(r) {}
};

// constinit гарантує відсутність будь-якого динамічного коду запуску.
// Якщо вираз не може бути обчислений під час компіляції, збірка завершиться з помилкою.
constinit inline FastConfig g_fast_config{"[APP_CONSTINIT]", 5};
```

Оскільки пам'ять під `g_fast_config` вже заповнена правильними байтами ще до початку виконання першої інструкції процесу, жодна інша одиниця трансляції не може застати цей об'єкт неініціалізованим.

## Порівняння підходів

| Підхід | Плюси | Мінуси | Коли застосовувати |
| :--- | :--- | :--- | :--- |
| **Глобальні змінні з конструкторами** | Простий синтаксис | Недетермінований порядок (SIOF), падіння до `main()` | Заборонено в надійному коді |
| **Construct-On-First-Use (Meyers)** | Повна безпека, ліниве створення, thread-safe | Мінімальний оверхед перевірки guard-прапорця | Для об'єктів з важкою динамічною ініціалізацією |
| **C++20 `constinit` / `constexpr`** | Нульова вартість (zero-cost), абсолютна надійність | Вимагає constexpr-конструкторів без динамічної пам'яті | Завжди, де значення можна порахувати при компіляції |
| **`init_priority` (атрибут GCC)** | Дозволяє виставити числовий порядок | Непереносний код, ламається при динамічному підвантаженні `.so` | Лише для низькорівневих системних бібліотек під одне залізо |

Використання `constinit` для конфігурацій часу компіляції та патерну Meyers' Singleton для динамічних сервісів повністю захищає архітектуру проєкту від прихованих збоїв порядку трансляції.
