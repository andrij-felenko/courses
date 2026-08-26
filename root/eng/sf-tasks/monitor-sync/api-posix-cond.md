# 📋 Інтерфейс умовних змінних: POSIX Threads та стандартна бібліотека C++

Умовні змінні надають фундаментальний системний механізм координації потоків, дозволяючи ниткам виконання атомарно звільняти м'ютекс і переходити в режим очікування до моменту настання необхідної умови в спільних даних.

Нижче наведено вичерпний довідник функцій стандарту POSIX Threads (`pthread_cond_*`) та класів стандартної бібліотеки C++ (`std::condition_variable` і `std::condition_variable_any`), включаючи сигнатури, опис параметрів, коди повернення помилок, вимоги до моделей пам'яті, правила взаємодії зі скасуванням потоків та типові пастки при практичній реалізації.

## 1. Специфікація POSIX Threads API (`<pthread.h>`)

У стандарті POSIX синхронізація через умовні змінні спирається на два основні типи даних:
- `pthread_cond_t` — непрозорий тип дескриптора умовної змінної, що зберігає чергу заблокованих задач і внутрішні прапорці налаштувань.
- `pthread_condattr_t` — структура атрибутів, що визначає поведінку умовної змінної під час ініціалізації (зокрема тип годинника для таймаутів та міжпроцесну доступність).

### Статична та динамічна ініціалізація

Для статично виділених умовних змінних у глобальній пам'яті або пам'яті модуля стандарт надає макрос статичної ініціалізації:

:::tabs
```c
#include <pthread.h>

/* Статична ініціалізація зі стандартними налаштуваннями */
static pthread_cond_t global_cond = PTHREAD_COND_INITIALIZER;
```
```cpp
#include <condition_variable>

// У C++ конструктор за замовчуванням виконує повну ініціалізацію
static std::condition_variable global_cond;
```
:::

Якщо умовна змінна розміщується у динамічній пам'яті (`heap`), усередині структури даних або вимагає нестандартних атрибутів, використовується функція динамічної ініціалізації `pthread_cond_init`.

---

### Таблиця функцій POSIX API

| Сигнатура функції | Призначення | Повертані коди помилок |
|---|---|---|
| `int pthread_cond_init(pthread_cond_t *cond, const pthread_condattr_t *attr)` | Динамічно ініціалізує умовну змінну із заданими атрибутами | `0` — успіх, `EAGAIN` — брак системних ресурсів, `ENOMEM` — брак пам'яті, `EBUSY` — спроба повторної ініціалізації |
| `int pthread_cond_destroy(pthread_cond_t *cond)` | Звільняє ресурси умовної змінної | `0` — успіх, `EBUSY` — на змінній усе ще очікують потоки, `EINVAL` — недійсний дескриптор |
| `int pthread_cond_wait(pthread_cond_t *cond, pthread_mutex_t *mutex)` | Атомарно відпускає замок і блокує потік; при пробудженні знову захоплює замок | `0` — успіх, `EINVAL` — недійсні покажчики, `EPERM` — м'ютекс не захоплено поточним потоком |
| `int pthread_cond_timedwait(pthread_cond_t *cond, pthread_mutex_t *mutex, const struct timespec *abstime)` | Блокує потік з обмеженням за абсолютною часовою міткою `abstime` | `0` — успіх, `ETIMEDOUT` — час очікування вичерпано, `EINVAL` — некоректні наносекунди або дескриптор |
| `int pthread_cond_signal(pthread_cond_t *cond)` | Розблоковує щонайменше один потік із черги очікування | `0` — успіх, `EINVAL` — недійсний дескриптор |
| `int pthread_cond_broadcast(pthread_cond_t *cond)` | Розблоковує всі потоки, що наразі перебувають у черзі | `0` — успіх, `EINVAL` — недійсний дескриптор |

---

### Робота з атрибутами: монотонний годинник проти реального часу

Найпідступнішою проблемою функції `pthread_cond_timedwait` є вибір джерела системного часу. За замовчуванням стандарт POSIX використовує годинник `CLOCK_REALTIME` (астрономічний настінний час). Якщо системний адміністратор змінить час сервера, або служба синхронізації часу NTP здійснить корекцію годинника назад чи вперед, виклик `pthread_cond_timedwait` або прокинеться завчасно, або зависне на необмежений час.

Для забезпечення передбачуваності та надійності систем системні інженери налаштовують атрибут умовної змінної на використання монотонного годинника `CLOCK_MONOTONIC`, який неперервно рахує час від моменту завантаження ядра і не піддається стрибкам:

:::tabs
```c
#include <pthread.h>
#include <time.h>
#include <stdio.h>

int init_monotonic_condition(pthread_cond_t *cond) {
    pthread_condattr_t attr;
    int rc;

    rc = pthread_condattr_init(&attr);
    if (rc != 0) return rc;

    /* Встановлюємо монотонний годинник для тайм-аутів */
    rc = pthread_condattr_setclock(&attr, CLOCK_MONOTONIC);
    if (rc != 0) {
        pthread_condattr_destroy(&attr);
        return rc;
    }

    rc = pthread_cond_init(cond, &attr);
    pthread_condattr_destroy(&attr);
    return rc;
}
```
```cpp
#include <condition_variable>
#include <chrono>

// У стандартній бібліотеці C++ методи wait_for та wait_until
// класу std::condition_variable автоматично працюють із std::chrono::steady_clock,
// що усуває потребу в ручному конфігуруванні атрибутів годинника на рівні ОС.
```
:::

### Міжпроцесні умовні змінні (Process-Shared)

Умовні змінні POSIX можуть використовуватися для координації не лише потоків у межах одного процесу, а й повністю незалежних процесів, якщо вони розміщені у спільній пам'яті (`shared memory`, створеній через `shm_open` та `mmap`).

Для цього у структурі атрибутів налаштовується прапорець `PTHREAD_PROCESS_SHARED`:

:::tabs
```c
#include <pthread.h>

int init_pshared_condition(pthread_cond_t *cond) {
    pthread_condattr_t attr;
    pthread_condattr_init(&attr);
    pthread_condattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    int rc = pthread_cond_init(cond, &attr);
    pthread_condattr_destroy(&attr);
    return rc;
}
```
```cpp
#include <condition_variable>

// Стандартний клас std::condition_variable у C++ призначений
// лише для міжпотокової синхронізації в межах одного процесу.
// Для міжпроцесної взаємодії використовують нативні примітиви POSIX/OS.
```
:::

---

## 2. Специфікація C++ API (`<condition_variable>`)

Стандарт C++11 ввів два незалежні класи для роботи з умовними змінними:

### 1. `std::condition_variable`
Високоефективна обгортка над нативними системними примітивами (наприклад, POSIX `pthread_cond_t` або Windows WaitOnAddress).
- **Обмеження**: працює **виключно** з об'єктом блокування типу `std::unique_lock<std::mutex>`.
- **Перевага**: нульові накладні витрати (*zero overhead abstraction*), максимальна швидкість виконання у просторі ядра.

### 2. `std::condition_variable_any`
Універсальний координаційний клас, здатний працювати з **довільним** об'єктом, що задовольняє концепт *BasicLockable* (наявність методів `lock()` та `unlock()`).
- **Сфера застосування**: робота зі `std::shared_lock` (блокування на читання для Read-Write Locks), рекурсивними м'ютексами або власними блокуючими типами.
- **Ціна**: вищі накладні витрати через внутрішню додаткову синхронізацію та управління станом.

---

### Таблиця методів `std::condition_variable`

| Метод | Сигнатура | Детальний опис поведінки |
|---|---|---|
| `notify_one()` | `void notify_one() noexcept` | Будить один із заблокованих потоків. Якщо черга порожня, виклик ігнорується без збереження стану. |
| `notify_all()` | `void notify_all() noexcept` | Будить усі потоки, заблоковані на цій умовній змінній. |
| `wait(lock)` | `void wait(std::unique_lock<std::mutex>& lock)` | Атомарно відпускає `lock`, засинає в ядрі; після отримання сигналу знову захоплює `lock` перед поверненням. |
| `wait(lock, pred)` | `template<class Predicate> void wait(std::unique_lock<std::mutex>& lock, Predicate pred)` | Виконує цикл `while (!pred()) wait(lock);`, надійно захищаючи від хибних пробуджень. |
| `wait_for(lock, rel_time)` | `template<class Rep, class Period> std::cv_status wait_for(std::unique_lock<std::mutex>& lock, const std::chrono::duration<Rep, Period>& rel_time)` | Очікує протягом відносного проміжку часу `rel_time`. Повертає `no_timeout` або `timeout`. |
| `wait_for(lock, rel_time, pred)` | `template<class Rep, class Period, class Predicate> bool wait_for(..., Predicate pred)` | Очікує виконання предикату з тайм-аутом. Повертає булеве значення `pred()` після завершення. |
| `wait_until(lock, abs_time)` | `template<class Clock, class Duration> std::cv_status wait_until(..., const std::chrono::time_point<Clock, Duration>& abs_time)` | Блокує потік до настання абсолютної часової мітки `abs_time`. |
| `wait_until(lock, abs_time, pred)` | `template<class Clock, class Duration, class Predicate> bool wait_until(..., Predicate pred)` | Очікує виконання предикату до абсолютної часової мітки. Повертає булевий результат `pred()`. |

---

## 3. Гарантії пам'яті та зв'язок «виконується-раніше» (Happens-Before)

Умовні змінні забезпечують не лише керування виконанням потоків, а й фундаментальні гарантії видимості змін у пам'яті згідно з моделлю пам'яті C++ та POSIX:

1. **Синхронізація звільнення-захоплення (*Release-Acquire*)**: успішне завершення операцій модифікації даних у потоці-виробнику до моменту виклику `signal()` або `notify_one()` гарантовано синхронізується з розбудженим потоком у момент успішного повернення із `wait()`.
2. **Видимість через спільний м'ютекс**: оскільки зміна спільних змінних відбувається під захистом м'ютексу, операція `unlock()` у виробника створює бар'єр пам'яті типу *Release*, а повторний `lock()` у споживача всередині `wait()` створює бар'єр *Acquire*, що гарантує відсутність кеш-колізій та узгодженість усіх полів структури.

---

## 4. Взаємодія зі скасуванням потоків (Thread Cancellation)

У стандарті POSIX функція `pthread_cond_wait` є офіційною точкою скасування (*cancellation point*). Якщо сторонній потік викликає `pthread_cancel()` для потоку, що заблокований у `pthread_cond_wait`, ядро виконує спеціальний безпечний протокол:
1. Потік вилучається з черги умовної змінної.
2. Перед виконанням будь-яких обробників скасування (*cleanup handlers*, зареєстрованих через `pthread_cleanup_push`) потік **обов'язково знову захоплює зв'язаний м'ютекс**.
3. Це гарантує, що очисні процедури виконуються в узгодженому стані під захистом замка і можуть безпечно відновити інваріанти структури даних та виконати `pthread_mutex_unlock`.

---

## 5. Практичний приклад: синхронізація прапорця події

Нижче наведено порівняння безпечної реалізації прапорця події з підтримкою тайм-аутів мовами C та C++:

:::tabs
```c
#include <pthread.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>

typedef struct {
    pthread_mutex_t mtx;
    pthread_cond_t cv;
    bool ready;
} event_flag_t;

int event_flag_init(event_flag_t *e) {
    e->ready = false;
    pthread_mutex_init(&e->mtx, NULL);

    pthread_condattr_t attr;
    pthread_condattr_init(&attr);
    pthread_condattr_setclock(&attr, CLOCK_MONOTONIC);
    pthread_cond_init(&e->cv, &attr);
    pthread_condattr_destroy(&attr);
    return 0;
}

bool event_flag_wait(event_flag_t *e, long timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    pthread_mutex_lock(&e->mtx);
    while (!e->ready) {
        int rc = pthread_cond_timedwait(&e->cv, &e->mtx, &ts);
        if (rc == ETIMEDOUT) {
            break;
        }
    }
    bool status = e->ready;
    pthread_mutex_unlock(&e->mtx);
    return status;
}

void event_flag_set(event_flag_t *e) {
    pthread_mutex_lock(&e->mtx);
    e->ready = true;
    pthread_cond_broadcast(&e->cv);
    pthread_mutex_unlock(&e->mtx);
}

void event_flag_destroy(event_flag_t *e) {
    pthread_mutex_destroy(&e->mtx);
    pthread_cond_destroy(&e->cv);
}
```
```cpp
#include <mutex>
#include <condition_variable>
#include <chrono>

class EventFlag {
public:
    EventFlag() : ready_(false) {}

    bool wait(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        return cv_.wait_for(lock, timeout, [this] {
            return ready_;
        });
    }

    void set() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            ready_ = true;
        }
        cv_.notify_all();
    }

    void reset() {
        std::lock_guard<std::mutex> lock(mutex_);
        ready_ = false;
    }

private:
    std::mutex mutex_;
    std::condition_variable cv_;
    bool ready_;
};
```
:::

---

## 6. Типові помилки та критичні пастки

1. **Виклик `wait()` без захопленого замка**: Спроба викликати `pthread_cond_wait` або метод `std::condition_variable::wait` без володіння м'ютексом є фатальною помилкою. У POSIX функція повертає помилку `EPERM` або призводить до невизначеної поведінки (*undefined behavior*). У C++ це породжує системний виняток `std::system_error`.
2. **Знищення зайнятого примітива**: Виклик `pthread_cond_destroy` або виклик деструктора об'єкта `std::condition_variable`, доки бодай один потік чекає на змінній, пошкоджує таблиці очікування ядра і викликає аварійне завершення процесу.
3. **Сигналізація під замком проти сигналізації без замка**: Виклик `signal()` або `notify_one()` можна здійснювати як усередині критичної секції (під м'ютексом), так і після його відпускання. Виклик **після** звільнення м'ютексу часто є продуктивнішим, оскільки розбуджений потік не стикається із зайнятим замком і не зазнає додаткового блокування.
4. **Використання предиката з побічними ефектами**: Функція-предикат у `wait(lock, pred)` може викликатися довільну кількість разів через хибні пробудження. Вона повинна бути чистою перевіркою стану без незворотних модифікацій даних.
