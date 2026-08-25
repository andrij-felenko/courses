# ⚙️ Практична реалізація ABI-безпечного паттерна Pimpl

Паттерн Pimpl (Pointer to Implementation) у мові C++ та його аналог у мові C — непрозорий вказівник (Opaque Pointer) — є основними архітектурними прийомами для збереження бінарної сумісності (ABI). Головна ідея полягає у тому, щоб повністю відокремити публічний інтерфейс класу або структури від їхньої конкретної внутрішньої реалізації та розташування полів у пам'яті. Завдяки цьому внутрішній вміст об'єкта може довільно змінюватися у нових версіях динамічної бібліотеки без необхідності перекомпіляції клієнтських програм.

## Постановка практичної задачі

Розробляється системна бібліотека для керування мережевими з'єднаннями `NetworkEngine`. Початкова версія бібліотеки 1.0 містить лише базові поля: IP-адресу вузла та номер мережевого порту.

Під час розробки версії 2.0 виникає потреба розширити внутрішній стан об'єкта: додати налаштування таймаутів, лічильники відправлених пакетів та внутрішні масиви для криптографічних ключів. Головна вимога полягає у тому, щоб нова версія бібліотеки `.so` була повністю бінарно сумісною зі старими клієнтськими бінарними файлами, зібраними ще під версію 1.0.

## Проблема прямого оголошення полів у заголовку

Якщо структура оголошується у відкритому заголовку `engine.h` зі всіма своїми внутрішніми полями, компілятор клієнтського коду фіксує точний розмір об'єкта та зсув кожного поля безпосередньо під час компіляції клієнтського застосунку.

Коли у версії 2.0 розробники бібліотеки додають нові поля у середину або навіть в кінець структури, розмір об'єкта змінюється. Якщо клієнтська програма виділяє об'єкт на власному стеку або у масиві, стара програма виділить менше пам'яті, ніж очікує новий код бібліотеки. Результатом стане катастрофічне руйнування пам'яті (memory corruption), перезапис сусідніх змінних або збій виходу за межі пам'яті (`SIGSEGV`).

## ABI-безпечна реалізація через приховання реалізації

Для досягнення бінарної сумісності публічний заголовок експортує лише вказівник фіксованого розміру на структуру реалізації, повне визначення якої знаходить лише у внутрішньому вихідному файлі бібліотеки (`.c` або `.cpp`). 

:::tabs
```c
// ==================== C ABI (Opaque Pointer) ====================
// engine.h (Публічний API заголовка)
#ifndef ENGINE_H
#define ENGINE_H

#include <stddef.h>

// Непрозорий тип: клієнт бачить лише ім'я структури
typedef struct NetworkEngine NetworkEngine;

NetworkEngine* network_engine_create(const char* host, int port);
void network_engine_destroy(NetworkEngine* engine);
int network_engine_send(NetworkEngine* engine, const void* data, size_t len);

#endif // ENGINE_H

// engine.c (Файл реалізації всередині бібліотеки)
#include "engine.h"
#include <stdlib.h>
#include <string.h>

struct NetworkEngine {
    char host[128];
    int port;
    // Нові поля версії 2.0 додаються сюди абсолютно безпечно!
    int timeout_ms;
    unsigned long packets_sent;
};

NetworkEngine* network_engine_create(const char* host, int port) {
    NetworkEngine* engine = (NetworkEngine*)malloc(sizeof(NetworkEngine));
    if (!engine) return NULL;
    strncpy(engine->host, host, sizeof(engine->host) - 1);
    engine->port = port;
    engine->timeout_ms = 5000;
    engine->packets_sent = 0;
    return engine;
}

void network_engine_destroy(NetworkEngine* engine) {
    free(engine);
}

int network_engine_send(NetworkEngine* engine, const void* data, size_t len) {
    if (!engine) return -1;
    engine->packets_sent++;
    return 0; // Імітація успішної відправки
}
```
```cpp
// ==================== C++ ABI (Pimpl з std::unique_ptr) ====================
// engine.hpp (Публічний API заголовка)
#ifndef ENGINE_HPP
#define ENGINE_HPP

#include <memory>
#include <string_view>
#include <span>

class NetworkEngine {
public:
    NetworkEngine(std::string_view host, int port);
    ~NetworkEngine(); // Оголошено в заголовку, визначено у .cpp!

    // Операції переміщення
    NetworkEngine(NetworkEngine&&) noexcept;
    NetworkEngine& operator=(NetworkEngine&&) noexcept;

    // Забороняємо копіювання для збереження єдиного володіння
    NetworkEngine(const NetworkEngine&) = delete;
    NetworkEngine& operator=(const NetworkEngine&) = delete;

    bool send(std::span<const std::byte> data);

private:
    struct Impl; // Випереджувальне оголошення (forward declaration)
    std::unique_ptr<Impl> impl_; // Фіксований розмір об'єкта (8 байтів)
};

#endif // ENGINE_HPP

// engine.cpp (Файл реалізації всередині бібліотеки)
#include "engine.hpp"
#include <string>
#include <iostream>

struct NetworkEngine::Impl {
    std::string host;
    int port;
    // Нові поля версії 2.0 додаються у цей struct без зміни розміру NetworkEngine!
    int timeout_ms{5000};
    uint64_t packets_sent{0};
};

NetworkEngine::NetworkEngine(std::string_view host, int port)
    : impl_(std::make_unique<Impl>(std::string(host), port)) {}

// Деструктор обов'язково визначено у .cpp, де тип Impl є повністю відомим для std::default_delete!
NetworkEngine::~NetworkEngine() = default;

NetworkEngine::NetworkEngine(NetworkEngine&&) noexcept = default;
NetworkEngine& NetworkEngine::operator=(NetworkEngine&&) noexcept = default;

bool NetworkEngine::send(std::span<const std::byte> data) {
    if (!impl_) return false;
    impl_->packets_sent++;
    std::cout << "Sent " << data.size() << " bytes to " << impl_->host << ":" << impl_->port << "\n";
    return true;
}
```
:::

## Аналіз механізму збереження ABI

У обох вищеописаних реалізаціях публічний інтерфейс експортує лише об'єкт із строго фіксованим бінарним розміром:
- У реалізації на C: вказівник `NetworkEngine*` завжди займає рівно 8 байтів на 64-бітній системі. Клієнтський код маніпулює лише цим вказівником.
- У реалізації на C++: об'єкт класу `NetworkEngine` містить єдине поле — розумний вказівник `std::unique_ptr<Impl>`. Зовнішній розмір класу `NetworkEngine` завжди дорівнює 8 байтам, незалежно від того, скільки нових полів буде додано у внутрішню структуру `struct Impl`.

При випуску нової версії бібліотеки розробник додає до `struct Impl` нові поля (наприклад, масиви, лічильники, ресурси). Фізичний розмір `struct Impl` зростає з 132 байтів до 512 байтів у купі. Проте зовнішній розмір `NetworkEngine` у публічному заголовку залишається рівно 8 байтів. Клієнтська програма, скомпільована зі старою версією заголовків, завантажує оновлену динамічну бібліотеку і продовжує стабільно працювати без перекомпіляції.

## Критичні нюанси реалізації C++ Pimpl з `std::unique_ptr`

Під час розробки ABI-безпечних класів на C++ існує класична пастка компіляції, пов'язана з деструктором класу та випереджувальним оголошенням (forward declaration).

### Правило розташування деструктора у `.cpp` файлі

Якщо розробник не оголосить деструктор `~NetworkEngine()` у заголовковому файлі вручну, компілятор згенерує вбудований деструктор за замовчуванням (inline destructor) безпосередньо у публічному заголовку.

У цей момент шаблону `std::unique_ptr<Impl>` знадобиться інстантіювати свій стандартний деструктор `std::default_delete<Impl>`, який викликає оператор `delete ptr`. Але у публічному заголовку тип `struct Impl` лише оголошений наперед (`struct Impl;`) і є незавершеним типом (incomplete type).

Компіляція клієнтського коду завершиться важкою помилкою: `static_assert failed: can't delete an incomplete type`.

Для усунення цієї проблеми деструктор класу зобов'язаний бути лише **оголошеним** у заголовковому `.hpp` файлі, а його визначення `= default;` має знаходитися виключно у файлі реалізації `.cpp`, де повна структура `struct Impl` вже є розкритою та відомою компілятору.

```cpp
// У заголовку engine.hpp:
~NetworkEngine(); // Лише оголошення!

// У файлі реалізації engine.cpp:
NetworkEngine::~NetworkEngine() = default; // Точка виклику std::default_delete<Impl>
```

Аналогічна вимога стосується операторів переміщення `operator=(NetworkEngine&&)` та конструкторів переміщення, оскільки вони також вивільняють попередній екземпляр `unique_ptr`.

### Глибоке копіювання (Deep Copy) та операції копіювання

Якщо клас `NetworkEngine` повинен підтримувати копіювання, звичайне `= default` для конструктора копіювання не спрацює, оскільки `std::unique_ptr` не підлягає копіюванню.

У цьому разі розробник оголошує конструктор копіювання у заголовку, а у `.cpp` файлі виконує глибоку дублікацію об'єкта `Impl`:

```cpp
// У заголовку engine.hpp
NetworkEngine(const NetworkEngine& other);
NetworkEngine& operator=(const NetworkEngine& other);

// У файлі реалізації engine.cpp
NetworkEngine::NetworkEngine(const NetworkEngine& other)
    : impl_(other.impl_ ? std::make_unique<Impl>(*other.impl_) : nullptr) {}

NetworkEngine& NetworkEngine::operator=(const NetworkEngine& other) {
    if (this != &other) {
        if (other.impl_) {
            impl_ = std::make_unique<Impl>(*other.impl_);
        } else {
            impl_.reset();
        }
    }
    return *this;
}
```

## Оцінка продуктивності та оптимізація Fast Pimpl

За збереження бінарної сумісності доводиться платити двома основними факторами:
1. **Додатковий рівень індирекції (Indirection Overhead):** Кожен виклик методу або доступ до даних вимагає додаткового розіменування вказівника (`impl_->field`). Компільований код не може заінлайнити ці звернення, що додає невелику затримку у гарячих циклах.
2. **Динамічне виділення пам'яті у купі:** Створення кожного об'єкта супроводжується окремим викликом системного алокатора пам'яті (`malloc` або `make_unique`), що може впливати на фрагментацію та швидкість локальності кешу процесора.

Для критичних до продуктивності ділянок застосовують технік **Fast Pimpl**. Вона полягає у тому, щоб замість динамічного виділення пам'яті у купі через `malloc` розмістити заздалегідь виділений непідготовлений масив `alignas(T) std::byte storage[N]` безпосередньо всередині класу з фіксованим запасом під майбутній вміст. 

Проте Fast Pimpl є менш гнучким: якщо розмір `struct Impl` з часом перевищить заздалегідь зарезервований розмір `N`, ABI знову буде зламано.

Тим не менше, для публічних системних бібліотек дистрибутивів Linux перевага збереження ABI від використання стандартного Pimpl та Opaque Pointers переважує дрібні накладні витрати продуктивності.
