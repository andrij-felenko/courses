# 📋 Довідник об'єктів синхронізації та RAII-обгортки стандарту C++

Цей довідник містить систематизований опис усіх інтерфейсів, типів, гарантій безпеки, кодів помилок та прапорців стратегій для м'ютексів і RAII-замків у стандартній бібліотеці C++ (заголовні файли `<mutex>` та `<shared_mutex>`).

![Порівняльна характеристика RAII-замків стандартної бібліотеки](/reference/cpp-standards/concurrency/mutex-and-raii-locks/img/lock-types-comparison.svg)
*Матриця типів RAII-обгорток та їхніх можливостей.*

## 1. Класи м'ютексів (Mutex Primitives)

Усі класи м'ютексів у C++ є некопійованими та непереміщуваними (`deleted copy/move constructors and assignment operators`). Вони задовольняють вимогам концепцій `BasicLockable` або `Lockable`. Конструктори за замовчуванням створюють м'ютекс у незахопленому стані.

### 1.1 `std::mutex` (C++11)
Основоположний ексклюзивний нерекурсивний м'ютекс. Забезпечує ефекти синхронізації пам'яті: успішний виклик `unlock()` на певному м'ютексі синхронізується з наступним успішним викликом `lock()` або `try_lock()` на тому самому м'ютексі (порядок Happens-Before).

```cpp
namespace std {
    class mutex {
    public:
        constexpr mutex() noexcept;
        ~mutex();

        mutex(const mutex&) = delete;
        mutex& operator=(const mutex&) = delete;

        void lock();
        bool try_lock();
        void unlock();

        using native_handle_type = /* implementation-defined */;
        native_handle_type native_handle();
    };
}
```

#### Детальний опис методів:
- **`void lock()`**: Блокує викликальну нитку доти, доки м'ютекс не буде успішно захоплено. 
  - *Винятки*: Може генерувати `std::system_error` із кодами помилок:
    - `std::errc::resource_deadlock_would_occur` — якщо виявлено спробу рекурсивного захоплення тією самою ниткою;
    - `std::errc::operation_not_permitted` — якщо нитка не має відповідних прав.
  - *Невизначена поведінка*: Якщо викликальна нитка вже утримує цей `std::mutex`, повторний виклик `lock()` є невизначеною поведінкою (UB).
- **`bool try_lock()`**: Спробує захопити м'ютекс без блокування викликальної нитки. 
  - *Повертане значення*: `true`, якщо м'ютекс успішно захоплено; `false`, якщо м'ютекс уже утримується іншою ниткою.
  - *Псевдонерозпізнавання (Spurious Failure)*: Стандарт дозволяє `try_lock()` повертати `false` навіть тоді, коли м'ютекс є вільним (наприклад, через особливості атомарних інструкцій процесора).
- **`void unlock()`**: Звільняє м'ютекс.
  - *Вимоги*: Виклик повинен здійснюватися **виключно тією ниткою**, яка раніше успішно захопила цей м'ютекс.
  - *Невизначена поведінка*: Звільнення незахопленого м'ютекса або виклик `unlock()` з іншої нитки є UB.
- **`native_handle_type native_handle()`**: Повертає системний дескриптор підкладного примітива операційної системи (наприклад, `pthread_mutex_t*` під POSIX або `SRWLOCK*` під Windows API).

---

### 1.2 `std::recursive_mutex` (C++11)
Рекурсивний ексклюзивний м'ютекс, який дозволяє одній і тій самій нитці виконання захоплювати його повторно багаторазово без виникнення дедлоку.

```cpp
namespace std {
    class recursive_mutex {
    public:
        recursive_mutex();
        ~recursive_mutex();

        recursive_mutex(const recursive_mutex&) = delete;
        recursive_mutex& operator=(const recursive_mutex&) = delete;

        void lock();
        bool try_lock() noexcept;
        void unlock();

        using native_handle_type = /* implementation-defined */;
        native_handle_type native_handle();
    };
}
```

#### Детальний опис специфіки:
- **Лічильник замикань**: Об'єкт підтримує внутрішній лічильник рівнів замикання для нитки-власника. Кожен успішний виклик `lock()` або `try_lock()` збільшує лічильник на 1.
- **Звільнення**: Кожен виклик `unlock()` зменшує лічильник на 1. М'ютекс стає повністю вільним і доступним для інших ниток лише тоді, коли лічильник дорівнює нулю.
- **Винятки**: `lock()` може кинути `std::system_error` із кодом `std::errc::device_or_resource_busy`, якщо досягнуто максимуму рекурсивних замикань.

---

### 1.3 `std::timed_mutex` та `std::recursive_timed_mutex` (C++11)
Розширюють інтерфейс базових м'ютексів підтримкою методів очікування з часовими лімітами (таймаутами).

```cpp
namespace std {
    class timed_mutex {
    public:
        timed_mutex();
        ~timed_mutex();

        timed_mutex(const timed_mutex&) = delete;
        timed_mutex& operator=(const timed_mutex&) = delete;

        void lock();
        bool try_lock();
        void unlock();

        template <class Rep, class Period>
        bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout_duration);

        template <class Clock, class Duration>
        bool try_lock_until(const std::chrono::time_point<Clock, Duration>& timeout_time);
    };
}
```

#### Детальний опис методик очікування:
- **`try_lock_for(duration)`**: Блокує нитку до успішного захоплення м'ютекса або до закінчення відносного проміжку часу `timeout_duration`. Повертає `true`, якщо замок здобуто, і `false`, якщо вичерпано час очікування.
- **`try_lock_until(time_point)`**: Блокує нитку до настання абсолютного моменту часу `timeout_time` за годинником `Clock`.

---

### 1.4 `std::shared_mutex` (C++17) та `std::shared_timed_mutex` (C++14)
Підтримують два роздільні рівні володіння: ексклюзивне (для ниток-писців) та спільне (для ниток-читачів). Задовольняють вимогам концепції `SharedLockable`.

```cpp
namespace std {
    class shared_mutex {
    public:
        shared_mutex();
        ~shared_mutex();

        shared_mutex(const shared_mutex&) = delete;
        shared_mutex& operator=(const shared_mutex&) = delete;

        // Ексклюзивне володіння (Writers)
        void lock();
        bool try_lock();
        void unlock();

        // Спільне володіння (Readers)
        void lock_shared();
        bool try_lock_shared();
        void unlock_shared();
    };
}
```

#### Детальний опис рівнів доступу:
- **`lock_shared()`**: Захоплює м'ютекс у спільному режимі. Декілька ниток можуть одночасно утримувати спільний замок. Якщо інша нитка утримує м'ютекс в ексклюзивному режимі, викликальна нитка блокується.
- **`unlock_shared()`**: Звільняє спільне володіння. Викликається тільки ниткою, яка утримує shared-замок.
- **`lock()`**: Захоплює м'ютекс в ексклюзивному режимі. Блокує нитку доти, доки всі читачі не звільнять `shared`-замок і доки не завершить роботу попередній писець.

---

## 2. Маркерні прапорці стратегії захоплення (Lock Tag Constants)

Під час створення RAII-обгортки додатковий аргумент типу маркерного тегу визначає стратегію поведінки конструктора щодо м'ютекса.

```cpp
namespace std {
    struct defer_lock_t { explicit defer_lock_t() = default; };
    struct try_to_lock_t { explicit try_to_lock_t() = default; };
    struct adopt_lock_t { explicit adopt_lock_t() = default; };

    inline constexpr defer_lock_t defer_lock{};
    inline constexpr try_to_lock_t try_to_lock{};
    inline constexpr adopt_lock_t adopt_lock{};
}
```

| Прапорець | Опис стратегії | Сигнатура конструктора |
| :--- | :--- | :--- |
| **`std::defer_lock`** | Не викликати `lock()` у конструкторі. Обгортка прив'язується до м'ютекса, але лишається у незахопленому стані. | `unique_lock(mutex_type& m, std::defer_lock_t) noexcept` |
| **`std::try_to_lock`** | Спробувати захопити м'ютекс у конструкторі викликом `m.try_lock()` без блокування нитки. | `unique_lock(mutex_type& m, std::try_to_lock_t)` |
| **`std::adopt_lock`** | Вважати, що викликальна нитка **вже захопила** м'ютекс раніше. Конструктор не викликає `lock()`, а деструктор гарантовано викличе `unlock()`. | `lock_guard(mutex_type& m, std::adopt_lock_t)` |

---

## 3. RAII-обгортки управління м'ютексами

### 3.1 `std::lock_guard` (C++11)
Строго обмежена за області видимості (scope-based) RAII-обгортка над одним м'ютексом.

```cpp
namespace std {
    template <class Mutex>
    class lock_guard {
    public:
        using mutex_type = Mutex;

        explicit lock_guard(mutex_type& m);
        lock_guard(mutex_type& m, adopt_lock_t t);
        ~lock_guard();

        lock_guard(const lock_guard&) = delete;
        lock_guard& operator=(const lock_guard&) = delete;
    };
}
```

#### Гарантії та обмеження:
- Конструктор `explicit lock_guard(m)` викликає `m.lock()`.
- Конструктор `lock_guard(m, std::adopt_lock)` бере під опіку вже захоплений м'ютекс.
- Деструктор `~lock_guard()` викликає `m.unlock()`.
- Об'єкт не можна копіювати, переміщувати або змінювати його м'ютекс.

---

### 3.2 `std::scoped_lock` (C++17)
Варіативна RAII-обгортка для атомарного захоплення від 0 до `N` м'ютексів із гарантованим уникненням взаємного блокування (Deadlock Avoidance).

```cpp
namespace std {
    template <class... MutexTypes>
    class scoped_lock {
    public:
        using mutex_type = /* лише якщо sizeof...(MutexTypes) == 1 */;

        explicit scoped_lock(MutexTypes&... m);
        scoped_lock(adopt_lock_t t, MutexTypes&... m);
        explicit scoped_lock(MutexTypes& m);
        scoped_lock() noexcept; // порожній замок для 0 м'ютексів
        ~scoped_lock();

        scoped_lock(const scoped_lock&) = delete;
        scoped_lock& operator=(const scoped_lock&) = delete;
    };
}
```

#### Специфіка роботи:
- Для 1 м'ютекса: конструктор викликає `m.lock()`.
- Для кількох м'ютексів: конструктор викликає `std::lock(m1, m2, ...)`.
- Підтримує CTAD у C++17: написання `std::scoped_lock lock(m1, m2);` не вимагає явних типів шаблону.

---

### 3.3 `std::unique_lock` (C++11)
Гнучка RAII-обгортка із підтримкою переміщення володіння, відкладеного захоплення, таймаутів та ручного управління.

```cpp
namespace std {
    template <class Mutex>
    class unique_lock {
    public:
        using mutex_type = Mutex;

        unique_lock() noexcept;
        explicit unique_lock(mutex_type& m);
        unique_lock(mutex_type& m, defer_lock_t) noexcept;
        unique_lock(mutex_type& m, try_to_lock_t);
        unique_lock(mutex_type& m, adopt_lock_t);

        template <class Rep, class Period>
        unique_lock(mutex_type& m, const std::chrono::duration<Rep, Period>& timeout_duration);

        ~unique_lock();

        unique_lock(const unique_lock&) = delete;
        unique_lock& operator=(const unique_lock&) = delete;

        unique_lock(unique_lock&& u) noexcept;
        unique_lock& operator=(unique_lock&& u) noexcept;

        void lock();
        bool try_lock();

        template <class Rep, class Period>
        bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout_duration);

        void unlock();

        bool owns_lock() const noexcept;
        explicit operator bool() const noexcept;

        mutex_type* release() noexcept;
        mutex_type* mutex() const noexcept;
    };
}
```

#### Деталізація методів:
- **`owns_lock()` / `operator bool()`**: Повертає `true`, якщо об'єкт `unique_lock` наразі утримує м'ютекс.
- **`release()`**: Відключає м'ютекс від обгортки та повертає вказівник на нього. М'ютекс залишається у захопленому стані, а деструктор `unique_lock` більше не буде викликати `unlock()`.
- **`mutex()`**: Повертає вказівник на керований `mutex_type` (або `nullptr`).

---

### 3.4 `std::shared_lock` (C++14)
RAII-обгортка для поділюваного доступу на читання над об'єктами типу `std::shared_mutex`.

```cpp
namespace std {
    template <class Mutex>
    class shared_lock {
    public:
        using mutex_type = Mutex;

        shared_lock() noexcept;
        explicit shared_lock(mutex_type& m); // викликає m.lock_shared()
        shared_lock(mutex_type& m, defer_lock_t) noexcept;
        shared_lock(mutex_type& m, try_to_lock_t);
        shared_lock(mutex_type& m, adopt_lock_t);
        ~shared_lock();                      // викликає m.unlock_shared()

        shared_lock(const shared_lock&) = delete;
        shared_lock& operator=(const shared_lock&) = delete;

        shared_lock(shared_lock&& u) noexcept;
        shared_lock& operator=(shared_lock&& u) noexcept;

        void lock();
        bool try_lock();
        void unlock();

        bool owns_lock() const noexcept;
        explicit operator bool() const noexcept;
    };
}
```

---

## 4. Вільні функції та допоміжні примітиви

### 4.1 `std::lock` та `std::try_lock` (C++11)

```cpp
namespace std {
    template <class L1, class L2, class... L3>
    void lock(L1& l1, L2& l2, L3&... l3);

    template <class L1, class L2, class... L3>
    int try_lock(L1& l1, L2& l2, L3&... l3);
}
```

- **`std::lock`**: Атомарно захоплює всі передані об'єкти замків (`Lockable`), уникаючи взаємного блокування за допомогою внутрішнього алгоритму спроб та відкатів. Якщо під час захоплення одного з замків виникає виняток, усі вже захоплені у цьому виклику замки автоматично відпускаються.
- **`std::try_lock`**: Послідовно викликає `try_lock()` для кожного об'єкта. Повертає `-1` у разі успіху для всіх. Якщо якийсь замок повернув `false` або викинув виняток, усі попередньо захоплені замки відпускаються, а функція повертає 0-індексований порядковий номер замка, на якому стався збій.

---

### 4.2 Одноразова ініціалізація: `std::call_once` та `std::once_flag` (C++11)

```cpp
namespace std {
    struct once_flag {
        constexpr once_flag() noexcept;
        once_flag(const once_flag&) = delete;
        once_flag& operator=(const once_flag&) = delete;
    };

    template <class Callable, class... Args>
    void call_once(once_flag& flag, Callable&& f, Args&&... args);
}
```

- **`std::call_once`**: Гарантує, що передана функція або об'єкт виклику `f` буде виконано **рівно один раз** на даному екземплярі `once_flag`, навіть якщо `call_once` одночасно викликають сотні паралельних ниток.
- **Гарантія безпеки винятків**: Якщо виклик `f` завершується винятком, прапорець `once_flag` **не вважається встановленим**. Наступна нитка, яка викликає `call_once` з цим прапорцем, знову спробує виконати `f`.

---

## 5. Зведений приклад використання типів замків (C та C++)

:::tabs
```c
#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>

typedef struct {
    pthread_mutex_t lock;
    int data;
} SafeContainer;

void init_container(SafeContainer* c) {
    pthread_mutex_init(&c->lock, NULL);
    c->data = 0;
}

void write_data(SafeContainer* c, int val) {
    pthread_mutex_lock(&c->lock);
    c->data = val;
    pthread_mutex_unlock(&c->lock);
}

void destroy_container(SafeContainer* c) {
    pthread_mutex_destroy(&c->lock);
}
```
```cpp
#include <mutex>
#include <shared_mutex>
#include <iostream>

class SafeContainer {
private:
    mutable std::shared_mutex rw_mtx_;
    int data_ = 0;

public:
    // Читання: багато ниток одночасно через std::shared_lock
    int read_data() const {
        std::shared_lock<std::shared_mutex> lock(rw_mtx_);
        return data_;
    }

    // Запис: ексклюзивно через std::scoped_lock
    void write_data(int val) {
        std::scoped_lock lock(rw_mtx_);
        data_ = val;
    }
};
```
:::
