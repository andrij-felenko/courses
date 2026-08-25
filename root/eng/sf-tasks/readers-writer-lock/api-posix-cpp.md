# 📋 Інтерфейс RWLock у POSIX Threads та стандартній бібліотеці C++

Замок читачів-письменника реалізований як базовий системний примітив у стандарті POSIX Threads (C) та стандартній бібліотеці мови C++ (починаючи з C++14 та C++17). Нижче наведено детальний довідник інтерфейсів, параметрів, кодів повернення, гарантій пам'яті та правил безпечного використання обох стандартів.

---

### 1. Системний інтерфейс POSIX Threads (`pthread_rwlock_t`)

Заголовок: `<pthread.h>`.  
Тип даних: `pthread_rwlock_t`.  
Атрибути: `pthread_rwlockattr_t`.

#### 1.1. Ініціалізація та знищення

- `int pthread_rwlock_init(pthread_rwlock_t *restrict rwlock, const pthread_rwlockattr_t *restrict attr);`
  - **Призначення:** динамічна ініціалізація структури блокування з вказаними атрибутами (або атрибутами за замовчуванням при `attr == NULL`).
  - **Повертає:** `0` при успіху, або додатний код помилки (`EINVAL`, `ENOMEM`, `EBUSY`).
- `pthread_rwlock_t rwlock = PTHREAD_RWLOCK_INITIALIZER;`
  - **Призначення:** статична ініціалізація глобальних або статичних об'єктів блокування з конфігурацією за замовчуванням.
- `int pthread_rwlock_destroy(pthread_rwlock_t *rwlock);`
  - **Призначення:** звільнення системних ресурсів, асоційованих із замком.
  - **Вимога:** заборонено знищувати замок, поки він утримується хоча б одним потоком або поки на ньому очікують інші потоки (повертає `EBUSY`).

#### 1.2. Операції блокування для читачів (Shared Read Lock)

- `int pthread_rwlock_rdlock(pthread_rwlock_t *rwlock);`
  - **Поведінка:** блокуюче захоплення замка в розділюваному режимі. Якщо замок утримується іншими читачами (і немає пріоритетного очікуючого письменника), потік негайно отримує доступ. Якщо замок утримує письменник, потік засинає в черзі.
  - **Коди помилок:** `0` (успіх), `EDEADLK` (виявлено дедлок), `EAGAIN` (перевищено максимальну кількість одночасних читачів).
- `int pthread_rwlock_tryrdlock(pthread_rwlock_t *rwlock);`
  - **Поведінка:** неблокуюча спроба захоплення. Якщо замок недоступний, функція миттєво повертає код `EBUSY`, не перериваючи виконання потоку.
- `int pthread_rwlock_timedrdlock(pthread_rwlock_t *restrict rwlock, const struct timespec *restrict abstime);`
  - **Поведінка:** захоплення з абсолютним таймаутом `abstime` (час за системним годинником `CLOCK_REALTIME`). При вичерпанні часу повертає `ETIMEDOUT`.

#### 1.3. Операції блокування для письменників (Exclusive Write Lock)

- `int pthread_rwlock_wrlock(pthread_rwlock_t *rwlock);`
  - **Поведінка:** блокуюче захоплення замка в монопольному режимі. Потік блокується, поки всі активні читачі та будь-який активний письменник повністю не звільнять замок.
  - **Коди помилок:** `0` (успіх), `EDEADLK` (потік уже утримує цей замок).
- `int pthread_rwlock_trywrlock(pthread_rwlock_t *rwlock);`
  - **Поведінка:** неблокуюча спроба монопольного захоплення. Повертає `EBUSY`, якщо замок утримується будь-яким читачем або іншим письменником.
- `int pthread_rwlock_timedwrlock(pthread_rwlock_t *restrict rwlock, const struct timespec *restrict abstime);`
  - **Поведінка:** монопольне захоплення з таймаутом. При перевищенні часу повертає `ETIMEDOUT`.

#### 1.4. Звільнення блокування

- `int pthread_rwlock_unlock(pthread_rwlock_t *rwlock);`
  - **Поведінка:** універсальна функція звільнення, яка викликається як після читання (`rdlock`), так і після запису (`wrlock`).
  - **Вимога:** функція має викликатися лише тим потоком, який дійсно утримує блокування. Спроба відпустити чужий замок є невизначеною поведінкою (UB) або повертає `EPERM`.

#### 1.5. Налаштування політики планування в glibc та C++

У системній бібліотеці `glibc` (GNU/Linux) поведінку черги можна налаштовувати через спеціальні розширення атрибутів `pthread_rwlockattr_setkind_np`. Стандарт надає три режими:
1. `PTHREAD_RWLOCK_PREFER_READER_NP`: поведінка за замовчуванням, де читачі завжди отримують пріоритет.
2. `PTHREAD_RWLOCK_PREFER_WRITER_NP`: пріоритет письменників (вважається застарілим через проблеми з рекурсивним взяттям замка).
3. `PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP`: сучасний суворий пріоритет письменників без рекурсивного читання, що унеможливлює голодування запису.

Нижче наведено приклад налаштування мовами C та C++:

:::tabs
```c
#include <pthread.h>
#include <stdio.h>

int init_writer_preferring_rwlock(pthread_rwlock_t *rwlock) {
    pthread_rwlockattr_t attr;
    if (pthread_rwlockattr_init(&attr) != 0) {
        return -1;
    }

    // Встановлення пріоритету письменників без рекурсивного захоплення читачами
    pthread_rwlockattr_setkind_np(&attr, PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP);

    int res = pthread_rwlock_init(rwlock, &attr);
    pthread_rwlockattr_destroy(&attr);
    return res;
}
```
```cpp
#include <iostream>
#include <pthread.h>
#include <shared_mutex>

// У стандартному C++ std::shared_mutex використовує системну політику за замовчуванням.
// Для явного задання пріоритету письменників створюється RAII-обгортка над POSIX-атрибутами.
class NativeConfiguredRwLock {
public:
    NativeConfiguredRwLock() {
        pthread_rwlockattr_t attr;
        pthread_rwlockattr_init(&attr);
        pthread_rwlockattr_setkind_np(&attr, PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP);
        pthread_rwlock_init(&rwlock_, &attr);
        pthread_rwlockattr_destroy(&attr);
    }

    ~NativeConfiguredRwLock() {
        pthread_rwlock_destroy(&rwlock_);
    }

    void lock_shared() { pthread_rwlock_rdlock(&rwlock_); }
    void unlock_shared() { pthread_rwlock_unlock(&rwlock_); }
    void lock() { pthread_rwlock_wrlock(&rwlock_); }
    void unlock() { pthread_rwlock_unlock(&rwlock_); }

    NativeConfiguredRwLock(const NativeConfiguredRwLock&) = delete;
    NativeConfiguredRwLock& operator=(const NativeConfiguredRwLock&) = delete;

private:
    pthread_rwlock_t rwlock_;
};
```
:::

---

### 2. Інтерфейс стандартної бібліотеки C++ (`<shared_mutex>`)

У сучасному C++ замки читачів-письменника реалізовані через класи `std::shared_mutex` (C++17) та `std::shared_timed_mutex` (C++14). Вони задовольняють концепції *SharedMutex* та *SharedTimedMutex*.

Клас `std::shared_mutex` не підтримує таймаути, завдяки чому має мінімальний розмір у пам'яті (зазвичай розміром з один вказівник або 32-бітне число) і реалізується безпосередньо через системний примітив ядра (наприклад, `futex` у Linux або `SRWLOCK` у Windows).

#### 2.1. Методи класу `std::shared_mutex`

| Метод | Опис | Відповідний RAII-вартовий |
| :--- | :--- | :--- |
| `void lock()` | Монопольне захоплення (запис, Exclusive) | `std::unique_lock`, `std::lock_guard` |
| `bool try_lock()` | Неблокуюче монопольне захоплення | `std::unique_lock(m, std::try_to_lock)` |
| `void unlock()` | Звільнення монопольного блокування | Автоматично в деструкторі вартового |
| `void lock_shared()` | Розділюване захоплення (читання, Shared) | `std::shared_lock` |
| `bool try_lock_shared()` | Неблокуюче розділюване захоплення | `std::shared_lock(m, std::try_to_lock)` |
| `void unlock_shared()` | Звільнення розділюваного блокування | Автоматично в деструкторі вартового |

Для класу `std::shared_timed_mutex` додатково доступні методи з часовими інтервалами та абсолютними часовими мітками з бібліотеки `<chrono>`:
- `try_lock_for(duration)`, `try_lock_until(time_point)`
- `try_lock_shared_for(duration)`, `try_lock_shared_until(time_point)`

#### 2.2. Ідіоматичне використання через RAII

У сучасному C++ прямі виклики `lock()` та `unlock()` вважаються антипатерном, оскільки генерація винятку всередині критичної секції призведе до невивільненого замка і мертвого дедлоку. Застосовуються спеціалізовані RAII-обгортки:

:::tabs
```cpp
#include <chrono>
#include <iostream>
#include <optional>
#include <shared_mutex>
#include <string>
#include <thread>
#include <unordered_map>

class ThreadSafeRegistry {
public:
    // Операція читання: багато потоків читають одночасно
    std::optional<std::string> get(const std::string& key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = map_.find(key);
        if (it != map_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    // Операція запису: монопольний доступ одного потоку
    void set(const std::string& key, const std::string& value) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        map_[key] = value;
    }

    // Операція читання з обмеженням за часом очікування
    std::optional<std::string> get_timed(const std::string& key, std::chrono::milliseconds timeout) const {
        std::shared_lock<std::shared_timed_mutex> lock(timed_mutex_, timeout);
        if (!lock.owns_lock()) {
            return std::nullopt; // Таймаут очікування замка
        }
        auto it = timed_map_.find(key);
        if (it != timed_map_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

private:
    mutable std::shared_mutex                   mutex_;
    std::unordered_map<std::string, std::string> map_;

    mutable std::shared_timed_mutex             timed_mutex_;
    std::unordered_map<std::string, std::string> timed_map_;
};
```
```c
#include <errno.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct {
    pthread_rwlock_t rwlock;
    char             key[64];
    char             value[256];
} registry_entry_t;

void registry_init(registry_entry_t *reg) {
    pthread_rwlock_init(&reg->rwlock, NULL);
    strcpy(reg->key, "status");
    strcpy(reg->value, "active");
}

bool registry_read(registry_entry_t *reg, char *out_buf, size_t max_len) {
    if (pthread_rwlock_rdlock(&reg->rwlock) != 0) {
        return false;
    }
    strncpy(out_buf, reg->value, max_len - 1);
    out_buf[max_len - 1] = '\0';
    pthread_rwlock_unlock(&reg->rwlock);
    return true;
}

bool registry_read_timed(registry_entry_t *reg, char *out_buf, size_t max_len, int timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    int rc = pthread_rwlock_timedrdlock(&reg->rwlock, &ts);
    if (rc == ETIMEDOUT) {
        return false;
    }
    if (rc != 0) {
        return false;
    }

    strncpy(out_buf, reg->value, max_len - 1);
    out_buf[max_len - 1] = '\0';
    pthread_rwlock_unlock(&reg->rwlock);
    return true;
}

bool registry_write(registry_entry_t *reg, const char *new_val) {
    if (pthread_rwlock_wrlock(&reg->rwlock) != 0) {
        return false;
    }
    strncpy(reg->value, new_val, sizeof(reg->value) - 1);
    reg->value[sizeof(reg->value) - 1] = '\0';
    pthread_rwlock_unlock(&reg->rwlock);
    return true;
}

void registry_destroy(registry_entry_t *reg) {
    pthread_rwlock_destroy(&reg->rwlock);
}
```
:::

---

### 3. Безпека скасування потоків (Thread Cancellation)

У системному програмуванні на мові C (POSIX threads) потік може бути асинхронно або синхронно скасований іншим потоком через виклик `pthread_cancel()`. Якщо потік переривається в точці скасування (англ. *cancellation point*), перебуваючи всередині критичної секції `pthread_rwlock_rdlock` або `pthread_rwlock_wrlock`, замок назавжди залишиться заблокованим. Це гарантовано спричиняє дедлок усієї програми.

Для надійного захисту в C обов'язково застосовують стек обробників очищення `pthread_cleanup_push` / `pthread_cleanup_pop`:

:::tabs
```c
#include <pthread.h>
#include <stdio.h>
#include <string.h>

void rwlock_cleanup_handler(void *arg) {
    pthread_rwlock_t *rwlock = (pthread_rwlock_t *)arg;
    pthread_rwlock_unlock(rwlock);
}

void safe_cancellation_read(pthread_rwlock_t *rwlock, char *shared_data, char *out_buf, size_t len) {
    pthread_rwlock_rdlock(rwlock);
    pthread_cleanup_push(rwlock_cleanup_handler, (void *)rwlock);

    // Критична секція читання з потенційними точками скасування (наприклад, операції вводу-виводу)
    strncpy(out_buf, shared_data, len - 1);
    out_buf[len - 1] = '\0';

    // 0 означає не викликати обробник зараз, але безпечно зняти його зі стека
    pthread_cleanup_pop(0);
    pthread_rwlock_unlock(rwlock);
}
```
```cpp
#include <shared_mutex>
#include <string>
#include <string_view>

// У C++ завдяки семантиці RAII об'єкт std::shared_lock автоматично звільняє замок
// як при звичайному виході з області видимості, так і при розгортанні стека винятків (exception unwinding).
void safe_raii_read(std::shared_mutex& mutex, const std::string& shared_data, std::string& out_buf) {
    std::shared_lock<std::shared_mutex> lock(mutex);
    
    // Навіть якщо тут виникне виняток std::bad_alloc або std::runtime_error,
    // деструктор об'єкта lock гарантовано викличе unlock_shared().
    out_buf = shared_data;
}
```
:::

---

### 4. Модель пам'яті та гарантії синхронізації

Як у стандарті POSIX, так і в C++ (згідно з моделлю пам'яті C++11/C++17), операції звільнення та захоплення замка забезпечують суворі відношення впорядкування пам'яті:

1. **Звільнення запису синхронізується з наступним захопленням (Synchronizes-with):**
   Виклик `unlock()` (або `pthread_rwlock_unlock` після `wrlock`) має семантику `memory_order_release`. Усі зміни пам'яті, виконані письменником до моменту відпускання замка, стають видимими для будь-якого наступного потоку, який виконає `lock_shared()` або `lock()` (семантика `memory_order_acquire`).
2. **Паралельні читання не синхронізуються між собою:**
   Між двома паралельними читачами, які тримають `lock_shared()`, немає потреби у взаємній передачі даних, тому вони не витрачають ресурси процесора на обмін міжпотоковими повідомленнями, за винятком атомарного обліку самого лічильника читачів.
3. **Заборона рекурсивного блокування:**
   Повторне взяття `lock()` тим самим потоком призводить до дедлоку. Спроба взяти `lock_shared()` потоком, який уже тримає `lock()` (або навпаки), без проміжного звільнення також є забороненою і тягне за собою дедлок.

---

### 5. Відмінності реалізацій у glibc, musl та MSVC

Архітектура `rwlock` суттєво різниться залежно від використовуваної стандартної бібліотеки C/C++:

1. **GNU C Library (glibc NPTL):**
   У glibc `pthread_rwlock_t` реалізований як компактна структура поверх системного виклику `futex`. Лічильник читачів і прапорець письменника зберігаються в окремих 32-бітних полях, а для пробудження використовуються окремі черги futex для читачів і письменників. За замовчуванням glibc використовує пріоритет читачів, якщо не задано атрибут `PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP`.
2. **musl libc:**
   У бібліотеці musl замок реалізований у мінімалістичному стилі всього через одне 32-бітне число стану та один виклик `futex`. musl реалізує фазово-справедливу чергу за замовчуванням і навмисно ігнорує нестандартні розширення пріоритетів `glibc`, гарантуючи відсутність голодування для обох сторін.
3. **Microsoft Visual C++ (MSVC CRT / Windows):**
   У середовищі Windows клас `std::shared_mutex` транслюється безпосередньо в системний примітив ядра `SRWLOCK` (Slim Reader/Writer Lock). `SRWLOCK` має розмір рівно в один машинний вказівник (8 байт на x64), не вимагає динамічного виділення пам'яті й оптимізований для високої швидкодії без підтримки рекурсивного захоплення.
