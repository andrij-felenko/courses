# ⚙️ Реалізація власного одноразового каналу передачі результату

Внутрішня будова асинхронного каналу зв'язку між потоками базується на розділенні точок запису та читання через спільний стан (Shared State) із низькорівневими примітивами синхронізації. Створення власного спрощеного аналога `std::promise` та `std::future` розкриває механіку передачі даних, обробку винятків та керування часом життя спільних ресурсів.

## 1. Архітектурний розбір проблеми та проектування Shared State

Щоб зрозуміти, як стандартні класи `std::promise` та `std::future` передають обчислені значення між потоками без гонок за пам'ять (data race), розробнику необхідно розібрати системні процеси, що відбуваються під час асинхронної взаємодії.

При спробі передати значення з одного потоку в інший без спеціальних абстракцій ми зіштовхуємося з трьома фундаментальними проблемами обчислювальних систем:

1. **Невизначеність часу життя даних (Lifetime Mismatch):** Якщо потік-виробник обчислює результат і зберігає його на власному стеку, то після завершення функції потоку стек руйнується. Якщо потік-споживач спробує прочитати цей результат пізніше, він отримає звернення до звільненої пам'яті (Dangling Reference / Use-After-Free). Якщо ж виділити пам'ять у купі (`malloc` / `new`), виникає питання: хто саме відповідальний за її звільнення? Якщо споживач не прочитає результат, виникне витік пам'яті; якщо прочитає й видалить, а виробник спробує звернутися до стану ще раз — відбудеться падіння програми.
2. **Перевпорядкування інструкцій та видимість пам'яті (Memory Visibility & Reordering):** Сучасні процесори (особливо з слабкими моделями пам'яті, такими як ARM64 чи RISC-V) та оптимізуючі компілятори можуть перевпорядковувати операції запису. Якщо потік-виробник спочатку запише результат у змінну `data = 42`, а потім встановить прапор готовності `ready = true`, процесор може виконати ці операції у зворотному порядку для кеш-ліній. Без застосування бар'єрів пам'яті (Memory Fences) або примітивів синхронізації потік-споживач може побачити `ready == true`, але прочитати застаріле або сміттєве значення з `data`.
3. **Ефективне очікування без виснаження CPU (Busy Waiting vs Sleeping):** Перевірка прапора готовності в циклі видами `while (!ready) {}` (spin-wait) завантажує процесорне ядро на 100%, витрачаючи електроенергію й відбираючи кванти часу в інших потоків. Потік-споживач має бути занурений у стан сну на рівні операційної системи (за допомогою системних викликів `futex` у Linux чи `WaitForSingleObject` у Windows) і прокинутися лише тоді, коли результат фізично записано.

Для вирішення цих проблем спроектуємо трикомпонентну систему:
- `shared_state<T>` — внутрішня структура в купі, що містить буфер для даних, примітиви синхронізації та прапорці стану.
- `custom_promise<T>` — об'єкт-виробник, який надає інтерфейс запису `set_value()` та `set_exception()`.
- `custom_future<T>` — об'єкт-споживач, який надає блокуючий інтерфейс читання `get()`.

---

## 2. Повна реалізація асинхронного каналу на C та C++

Нижче наведено робочі реалізації каналу. Версія мовою C застосовує POSIX-потоки (`pthreads`), сирі вказувачі, ручне керування лічильником посилань та виділення пам'яті через `malloc`. Версія мовою C++ використовує ідіоми RAII, `std::shared_ptr`, `std::mutex`, `std::condition_variable` та `std::variant` для безпечного зберігання значення або винятку.

:::tabs
```c
/* POSIX C Реалізація одноразового каналу (pthread_mutex + pthread_cond) */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>
#include <string.h>

/* Спільний стан у купі */
typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t  cond;
    int             ref_count;
    bool            ready;
    bool            has_error;
    int             value;
    char            error_msg[128];
} c_shared_state;

/* Виробник (Promise) */
typedef struct {
    c_shared_state* state;
} c_promise;

/* Споживач (Future) */
typedef struct {
    c_shared_state* state;
} c_future;

/* Створення нового каналу обміну */
static c_shared_state* create_shared_state(void) {
    c_shared_state* st = (c_shared_state*)malloc(sizeof(c_shared_state));
    if (!st) return NULL;
    
    pthread_mutex_init(&st->mutex, NULL);
    pthread_cond_init(&st->cond, NULL);
    st->ref_count = 2; /* 1 для promise, 1 для future */
    st->ready = false;
    st->has_error = false;
    st->value = 0;
    st->error_msg[0] = '\0';
    return st;
}

static void release_shared_state(c_shared_state* st) {
    if (!st) return;
    
    pthread_mutex_lock(&st->mutex);
    st->ref_count--;
    int current_refs = st->ref_count;
    pthread_mutex_unlock(&st->mutex);
    
    if (current_refs == 0) {
        pthread_cond_destroy(&st->cond);
        pthread_mutex_destroy(&st->mutex);
        free(st);
    }
}

/* Ініціалізація каналу */
void c_promise_init(c_promise* p, c_future* f) {
    c_shared_state* st = create_shared_state();
    p->state = st;
    f->state = st;
}

/* Запис значення у канал */
void c_promise_set_value(c_promise* p, int val) {
    if (!p->state) return;
    
    pthread_mutex_lock(&p->state->mutex);
    if (!p->state->ready) {
        p->state->value = val;
        p->state->ready = true;
        pthread_cond_signal(&p->state->cond);
    }
    pthread_mutex_unlock(&p->state->mutex);
}

/* Запис помилки у канал */
void c_promise_set_error(c_promise* p, const char* err) {
    if (!p->state) return;
    
    pthread_mutex_lock(&p->state->mutex);
    if (!p->state->ready) {
        p->state->has_error = true;
        strncpy(p->state->error_msg, err, sizeof(p->state->error_msg) - 1);
        p->state->ready = true;
        pthread_cond_signal(&p->state->cond);
    }
    pthread_mutex_unlock(&p->state->mutex);
}

/* Звільнення promise */
void c_promise_destroy(c_promise* p) {
    if (p->state) {
        pthread_mutex_lock(&p->state->mutex);
        if (!p->state->ready) {
            p->state->has_error = true;
            strncpy(p->state->error_msg, "broken_promise", sizeof(p->state->error_msg) - 1);
            p->state->ready = true;
            pthread_cond_signal(&p->state->cond);
        }
        pthread_mutex_unlock(&p->state->mutex);
        
        release_shared_state(p->state);
        p->state = NULL;
    }
}

/* Очікування та читання значення */
int c_future_get(c_future* f, bool* ok_out, char* err_buf, size_t err_buf_sz) {
    if (!f->state) {
        if (ok_out) *ok_out = false;
        return -1;
    }
    
    pthread_mutex_lock(&f->state->mutex);
    while (!f->state->ready) {
        pthread_cond_wait(&f->state->cond, &f->state->mutex);
    }
    
    int res = 0;
    if (f->state->has_error) {
        if (ok_out) *ok_out = false;
        if (err_buf && err_buf_sz > 0) {
            strncpy(err_buf, f->state->error_msg, err_buf_sz - 1);
        }
    } else {
        if (ok_out) *ok_out = true;
        res = f->state->value;
    }
    
    pthread_mutex_unlock(&f->state->mutex);
    return res;
}

void c_future_destroy(c_future* f) {
    if (f->state) {
        release_shared_state(f->state);
        f->state = NULL;
    }
}
```
```cpp
// Ідіоматична C++17/20 реалізація (RAII, variant, exception_ptr, std::shared_ptr)
#include <iostream>
#include <mutex>
#include <condition_variable>
#include <memory>
#include <variant>
#include <exception>
#include <stdexcept>
#include <thread>
#include <string>

namespace custom {

template <typename T>
class custom_future;

template <typename T>
struct shared_state {
    std::mutex mtx;
    std::condition_variable cv;
    bool ready = false;
    std::variant<std::monostate, T, std::exception_ptr> storage;
};

template <typename T>
class custom_promise {
public:
    custom_promise() : state_(std::make_shared<shared_state<T>>()) {}

    ~custom_promise() {
        if (state_) {
            std::lock_guard<std::mutex> lock(state_->mtx);
            if (!state_->ready) {
                state_->storage = std::make_exception_ptr(
                    std::runtime_error("broken_promise: promise destroyed without value")
                );
                state_->ready = true;
                state_->cv.notify_all();
            }
        }
    }

    custom_promise(const custom_promise&) = delete;
    custom_promise& operator=(const custom_promise&) = delete;

    custom_promise(custom_promise&&) noexcept = default;
    custom_promise& operator=(custom_promise&&) noexcept = default;

    custom_future<T> get_future() {
        if (!state_) {
            throw std::logic_error("no_state: promise moved or invalid");
        }
        return custom_future<T>(state_);
    }

    void set_value(T val) {
        std::unique_lock<std::mutex> lock(state_->mtx);
        if (state_->ready) {
            throw std::logic_error("promise_already_satisfied");
        }
        state_->storage = std::move(val);
        state_->ready = true;
        lock.unlock(); // Звільняємо lock перед сповіщенням для зменшення контеншну
        state_->cv.notify_all();
    }

    void set_exception(std::exception_ptr e) {
        std::unique_lock<std::mutex> lock(state_->mtx);
        if (state_->ready) {
            throw std::logic_error("promise_already_satisfied");
        }
        state_->storage = e;
        state_->ready = true;
        lock.unlock();
        state_->cv.notify_all();
    }

private:
    std::shared_ptr<shared_state<T>> state_;
};

template <typename T>
class custom_future {
public:
    custom_future() = default;

    explicit custom_future(std::shared_ptr<shared_state<T>> st) 
        : state_(std::move(st)) {}

    bool valid() const noexcept {
        return state_ != nullptr;
    }

    T get() {
        if (!state_) {
            throw std::logic_error("no_state: future is invalid");
        }

        std::unique_lock<std::mutex> lock(state_->mtx);
        state_->cv.wait(lock, [this]() { return state_->ready; });

        // Після отримання результату зробимо future невалідним (1:1)
        auto st = std::move(state_);

        if (std::holds_alternative<std::exception_ptr>(st->storage)) {
            std::rethrow_exception(std::get<std::exception_ptr>(st->storage));
        }

        return std::get<T>(std::move(st->storage));
    }

    void wait() const {
        if (!state_) throw std::logic_error("no_state");
        std::unique_lock<std::mutex> lock(state_->mtx);
        state_->cv.wait(lock, [this]() { return state_->ready; });
    }

private:
    std::shared_ptr<shared_state<T>> state_;
};

} // namespace custom
```
:::

---

## 3. Детальний простеження механізмів синхронізації

Розберемо ключові технічні рішення, використані у реалізації C++ версії `custom_promise` та `custom_future`, і пояснимо їхню роль у забезпеченні потокобезпеки:

### 1. Роль std::variant для збереження результату
У класі `shared_state` поле `storage` має тип `std::variant<std::monostate, T, std::exception_ptr>`. Це типобезпечний об'єднаний тип, який може перебувати в одному з трьох станів:
- `std::monostate` — початковий порожній стан. Показує, що жодне значення або виняток ще не були записані.
- `T` — обчислене значення типу `T`, записане методом `set_value()`.
- `std::exception_ptr` — вказувач на виняток, записаний через `set_exception()` або в деструкторі при `broken_promise`.

Застосування `std::variant` позбавляє необхідності виділяти додаткову динамічну пам'ять під винятки чи значення, розміщуючи їх безпосередньо всередині структури `shared_state`.

### 2. Причини явного виклику lock.unlock() перед notify_all()
У методах `set_value()` та `set_exception()` ми спочатку закриваємо мутекс через `std::unique_lock<std::mutex> lock(state_->mtx)`, записуємо результат у `storage`, міняємо `ready = true`, а потім явно викликаємо `lock.unlock()` **до** виклику `state_->cv.notify_all()`.

Ця оптимізація відома під назвою усунення песимізації замка (lock contention avoidance). Якщо викликати `notify_all()` при ще закритому м'ютексі, умовна змінна негайно будить потік-споживач у ядрі OS. Споживач прокидається, намагається вийти з виклику `wait()`, але для цього йому необхідно знову захопити м'ютекс `state_->mtx`. Оскільки м'ютекс у цей момент все ще утримується потоком-виробником, прокинутий потік негайно занурюється у стан блокування на м'ютексі. Це призводить до двох марних переключень контексту потоків (context switches) у планувальнику OS. Спочатку явний `unlock()`, а потім `notify_all()` дозволяють споживачеві прокинутися й одразу захопити вже вільний м'ютекс без затримок.

### 3. Механіка обробки хибних пробуджень (Spurious Wakeups)
Виклик `state_->cv.wait(lock, [this]() { return state_->ready; })` захищає програму від специфічної поведінки операційних систем. На системному рівні виклик `pthread_cond_wait` або `Futex` може повернути керування навіть тоді, коли жоден потік не кликав `notify_all()` (наприклад, через надходження сигналів ОС POSIX).

Переданий предикат `[this]() { return state_->ready; }` працює як еквівалент наступного циклу:
```cpp
while (!state_->ready) {
    state_->cv.wait(lock);
}
```
Коли умовна змінна прокидається, вона автоматично повторно захоплює м'ютекс `lock` і перевіряє значення `ready`. Якщо `ready == false`, потік відпускає м'ютекс і занурюється в сон знову, унеможливлюючи передчасне читання незаповненого буфера `storage`.

---

## 4. Порівняння м'ютексного та беззамочного (Lock-Free) асинхронного каналу

М'ютексна реалізація `custom_promise` забезпечує 100% надійність та простоту реалізації, але натягує накладні витрати на виклики ядра OS під час очікування. У високонавантажених системах реального часу часто застосовують беззамочні (Lock-Free) канальні абстракції, побудовані на атомарних операціях (`std::atomic`).

Нижче наведено порівняльний аналіз двох підходів:

### М'ютексний канал (Mutex-based Shared State)
- **Механізм:** Використовує `std::mutex` для захисту `storage` та `std::condition_variable` для сну потоку.
- **Накладні витрати:** Захоплення м'ютекса без конкуренції коштує близько 10–20 тактів CPU. Очікування на умовній змінній переводить потік у сон через системний виклик `futex`, що вимагає переключення контексту (від 1000 до 3000 тактів CPU).
- **Перевага:** Звільняє ядро CPU під час очікування. Споживач споживає 0% ресурсів процесора, поки виробник обчислює результат.

### Беззамочний канал (Lock-Free SPSC Future)
- **Механізм:** Застосовує `std::atomic<bool>` з прапорцями впорядкування пам'яті `std::memory_order_release` та `std::memory_order_acquire`.
- **Накладні витрати:** Нуль викликів ядра OS при записі та прочитанні даних. Синхронізація кеш-ліній між ядрами CPU виконується на апаратному рівні шини (MESI protocol) за 20–50 тактів CPU.
- **Недоліки:** Очікування виконується у вигляді активного кручення (`spin-loop`), що навантажує процесорне ядро на 100%, або вимагає комбінованого `spin-then-yield` підходу.

У стандартній бібліотеці C++ реалізація `std::promise` та `std::future` зазвичай поєднує обидва підходи: для швидких операцій застосовуються атомарні прапорці, а при тривалому очікуванні рантайм переходить на системні futex-замочки.

---

## 5. Простеження через системні виклики Linux (futex та sysfs)

Щоб побачити, як наша C++ реалізація або стандартна `std::promise` працюють на рівні ядра операційної системи Linux, можна простежити виконання програми за допомогою утиліти `strace`:

```bash
g++ -std=c++17 main.cpp -pthread -o app
strace -f -e trace=futex ./app
```

При виконанні виклику `future.get()`, коли результат ще не готовий, потік-споживач звертається до умовної змінної `std::condition_variable`. На рівні ядра Linux це перетворюється на системний виклик `futex`:

```text
[pid 12345] futex(0x7fff5fbff800, FUTEX_WAIT_PRIVATE, 0, NULL)
```

Аргумент `FUTEX_WAIT_PRIVATE` вказує ядру Linux перевести поточний потік зі стану `TASK_RUNNING` у стан `TASK_INTERRUPTIBLE` і вилучити його з черги виконання планувальника CPU. Потік перебуває у цьому стані доти, доки потік-виробник у `set_value()` не виконає зворотний системний виклик:

```text
[pid 12346] futex(0x7fff5fbff800, FUTEX_WAKE_PRIVATE, 1) = 1
```

Системний виклик `FUTEX_WAKE_PRIVATE` з аргументом `1` наказує ядру Linux знайти у черзі блокування futex один потік і повернути його у чергу виконання планувальника (`TASK_RUNNING`). Це підтверджує, що очікування результату через `future` є абсолютно неблокуючим для ресурсів процесора (0% завантаження CPU під час сну).

---

## 6. Розбір крайових випадків та нештатних ситуацій

Під час проектування асинхронних каналів необхідно враховувати три основні граничні сценарії:

### Крайовий випадок 1: Аварійне руйнування виробника (Broken Promise)
Якщо потік-виробник завершується через виняток або виходить з області видимості до виклику `set_value()`, спрацьовує деструктор `custom_promise`. Деструктор під замком перевіряє `state_->ready`. Якщо прапор `ready == false`, деструктор записує у `storage` виняток `std::runtime_error("broken_promise")` і розблоковує споживача. Без цього деструктор залишив би споживача у вічному блокуванні у `futex_wait`.

### Крайовий випадок 2: Повторний виклик set_value()
Якщо потік-виробник помилково викликає `set_value()` двічі, перевірка `if (state_->ready)` виявляє колізію й кидає виняток `std::logic_error("promise_already_satisfied")`. Це захищає вміст Shared State від перезапису.

### Крайовий випадок 3: Виклик get() на невалідному future
При першому виклику `future.get()` виконується стрічка `auto st = std::move(state_)`. Об'єкт `future` втрачає вказувач на Shared State (`state_ == nullptr`). Повторний виклик `get()` на тому самому `future` перевіряє `if (!state_)` і негайно кидає виняток `std::logic_error("no_state")`, запобігаючи зверненню за нульовим вказувачем (Null Pointer Dereference).

---

## 7. Профілювання та оптимізація False Sharing у кеш-лініях

Під час розробки високоефективних асинхронних каналів у сучасних багатоядерних процесорах виникає підступне явище **False Sharing** (помилкове розділення кеш-ліній).

Кеш-пам'ять процесора L1/L2 оперує блоками фіксованого розміру — кеш-лініями (Cache Lines) розміром зазвичай у 64 байти. Якщо змінні `mtx`, `ready` та `storage` у структурі `shared_state` розміщені в пам'яті занадто щільно й потрапляють у одну 64-байтну кеш-лінію, то записи з ядра CPU 1 (де виконується `set_value()`) постійно інвалідовують кеш L1 ядра CPU 2 (де споживач опитує `ready`).

Щоб запобігти здешевленню пропускної здатності шини пам'яті через False Sharing, поле прапорця та буфер даних варто вирівнювати по межі кеш-лінії:

```cpp
#include <new>

template <typename T>
struct alignas(std::hardware_destructive_interference_size) shared_state_optimized {
    std::mutex mtx;
    std::condition_variable cv;
    
    // Вирівнюємо прапор на окрему кеш-лінію
    alignas(std::hardware_destructive_interference_size) bool ready = false;
    
    std::variant<std::monostate, T, std::exception_ptr> storage;
};
```

Це гарантує, що операції запису виробника на одному ядрі не вибиватимуть кеш-лінію споживача на сусідньому ядрі процесора, підвищуючи продуктивність обміну у 2–4 рази при високій частоті повідомлень.

---

## 8. Спеціалізація каналу для порожнього типу void (custom_promise<void>)

У багатьох випадках асинхронна задача не повертає конкретного значення, а виконує роль суто бар'єра сповіщення ("подію виконано", "файл завантажено", "ініціалізацію завершено"). Для таких задач використовується спеціалізація `custom_promise<void>`.

Нижче наведено концептуальний розбір спеціалізації для `void`:

```cpp
template <>
struct shared_state<void> {
    std::mutex mtx;
    std::condition_variable cv;
    bool ready = false;
    std::exception_ptr exception; // Значення T відсутнє, зберігається лише виняток
};

template <>
class custom_promise<void> {
public:
    void set_value() {
        std::unique_lock<std::mutex> lock(state_->mtx);
        if (state_->ready) throw std::logic_error("promise_already_satisfied");
        state_->ready = true;
        lock.unlock();
        state_->cv.notify_all();
    }
    // інші методи аналогічні
};
```

Спеціалізація для `void` оптимізує споживання пам'яті: Shared State не містить буфера для `T`, зберігаючи лише примітиви синхронізації та вказувач на виняток.

---

## 9. Побудова мульти-споживача (custom_shared_future)

Для підтримки сценаріїв «один виробник — багато споживачів» (1:N) шаблон `custom_future` трансформується у `custom_shared_future`.

На відміну від ексклюзивного `custom_future`, об'єкт `custom_shared_future` дозволяє копіювання:
- Конструктор копіювання просто копіює розумний вказувач `std::shared_ptr<shared_state<T>>`, збільшуючи внутрішній лічильник посилань `use_count()`.
- Метод `get()` не обнуляє вказувач `state_` і не переводить об'єкт у невалідний стан. Замість вилучення `std::move(storage)` метод повернути константне посилання `const T&` на значення, збережене всередині `std::variant`.
- Будь-яка кількість потоків може безпечно викликати `get()` одночасно, оскільки константне читання під замком м'ютекса не модифікує внутрішній стан Shared State.

---

## 10. Додавання неблокувальних продовжень (.then continuations)

Фундаментальним обмеженням класичного `std::future` у C++11 є його блокуюча природа у методі `get()`. Щоб перетворити канал на неблокувальну реактивну систему, до об'єкта `custom_future` додають підтримку зворотних викликів (continuations).

Ідея полягає в тому, що замість очікування у `get()` споживач реєструє функцію-продовження:

```cpp
template <typename F>
auto then(F&& func) {
    using R = std::invoke_result_t<F, T>;
    custom_promise<R> next_promise;
    auto next_future = next_promise.get_future();

    std::unique_lock<std::mutex> lock(state_->mtx);
    if (state_->ready) {
        lock.unlock();
        // Якщо результат уже готовий, виконуємо продовження негайно
        try {
            next_promise.set_value(func(std::get<T>(state_->storage)));
        } catch (...) {
            next_promise.set_exception(std::current_exception());
        }
    } else {
        // Якщо результат ще не готовий, зберігаємо функцію в очікування
        state_->continuation = [st = state_, p = std::move(next_promise), f = std::forward<F>(func)]() mutable {
            try {
                p.set_value(f(std::get<T>(st->storage)));
            } catch (...) {
                p.set_exception(std::current_exception());
            }
        };
    }
    return next_future;
}
```

Такий підхід дозволяє створювати асинхронні ланцюжки обчислень без занурення потоків у сон і лежить в основі сучасних бібліотек асинхронності (зокрема Concurrency TS та проєктів з корутинами).

---

## 11. Порівняння з промисловими реалізаціями стандартних бібліотек

Створена нами навчальна реалізація `custom_promise` за своєю логічною будовою тотожна промисловим реалізаціям стандартних бібліотек C++:

- **GNU libstdc++ (GCC):** Використовує базовий клас `_State_baseV2`, у якому прапор готовності захищено за допомогою `std::mutex` та `std::condition_variable`. Для оптимізації `libstdc++` застосовує атомарні лічильники посилань для керування життєвим циклом Shared State без використання `std::shared_ptr`, що зменшує розмір об'єкта `future` до одного сирого вказувача.
- **LLVM libc++ (Clang):** Використовує внутрішню ієрархію `__assoc_state<T>`, де винятки зберігаються у вигляді `std::exception_ptr`. Для забезпечення невипадання у витік пам'яті деструктор `__assoc_state` явно перевіряє прапори володіння виробника й споживача.
- **MSVC STL (Microsoft):** Використовує систему внутрішніх подій на основі Windows Concurrency Runtime (`Concurrency::details::_Associated_state`), що оптимізує роботу з системними потоками Windows Thread Pool.

---

## 12. Гарантії безпеки винятків (Exception Safety)

Спроектований нами асинхронний канал забезпечує строгу гарантію безпеки винятків (Strong Exception Guarantee):
- Якщо конструювання або переміщення об'єкта `T` всередині `set_value()` кидає виняток, стан `ready` залишається `false`, а самі заблоковані ресурси м'ютекса успішно звільняються за допомогою RAII-обгортки `std::unique_lock`.
- Подібним чином, виклик `get()` залишає `valid() == false` навіть тоді, коли повторне викидання винятку через `std::rethrow_exception()` перериває звичайне виконання потоку-споживача.

---

## 13. Реалізація затриманого сповіщення при завершенні потоку

Для повноти аналізу розглянемо, як реалізується аналог стандартного методу `set_value_at_thread_exit()`. 

У стандартній бібліотеці C++ затримане сповіщення реалізовано за допомогою змінних із модифікатором тривалості життя `thread_local`. Коли потік викликає `set_value_at_thread_exit()`, результат записується в Shared State, але прапор `ready` та сповіщення `notify_all()` реєструються в спеціальному `thread_local` об'єкті-чистильнику:

```cpp
template <typename T>
void set_value_at_thread_exit_impl(custom_promise<T>& p, T val) {
    // Структура чистильника, деструктор якої викличеться при виході з потоку
    struct thread_exit_notifier {
        std::shared_ptr<shared_state<T>> state;
        T value;

        ~thread_exit_notifier() {
            if (state) {
                std::lock_guard<std::mutex> lock(state->mtx);
                state->storage = std::move(value);
                state->ready = true;
                state->cv.notify_all();
            }
        }
    };

    static thread_local thread_exit_notifier notifier;
    notifier.state = p.get_state_internal();
    notifier.value = std::move(val);
}
```

Цей механізм гарантує, що споживач прокинеться в момент, коли фоновий потік повністю розібрав свій стек і знищив усі свої `thread_local` ресурси, запобігаючи доступу до вже знищених локальних об'єктів.

---

## 14. Налагодовувальний кастомний алокатор для Shared State

У реальних embedded-системах та високопродуктивних фінансових платформах стандартний виклик `operator new` для кожного асинхронного каналу є неприпустимим через невизначену латентність динамічної купи.

Для вирішення цієї проблеми шаблон `std::promise` надає конструктор із підтримкою кастомних алокаторів `std::promise(std::allocator_arg_t, const Allocator&)`. У нашій реалізації це досягається передачею користувацької функції виділення пам'яті з пул-алокатора (Memory Pool), що забезпечує виконання створення канала за сталий час `O(1)` без фрагментації пам'яті.

---

## 15. Семантика обміну (swap) та переміщення каналів

Для забезпечення ефективної роботи в контейнерах та алгоритмах стандартної бібліотеки класи `custom_promise` та `custom_future` реалізують семантику переміщення та обміну станами.

Операція `swap` здійснюється шляхом швидкої заміни двох розумних вказувачів `std::shared_ptr` без потреби захоплення м'ютекса Shared State:

```cpp
template <typename T>
void swap(custom_promise<T>& a, custom_promise<T>& b) noexcept {
    a.swap(b);
}
```

Оскільки обмін зачіпає лише внутрішні керуючі вказувачі на стеку, операція `swap` має гарантовану часову складність `O(1)` і маркується як `noexcept`.

---

## 16. Практичний сценарій використання та тестування

Нижче наведено повністю працездатний демонстраційний приклад, який показує обмін даними та перехоплення винятків між двома потоками виконання з використанням `custom_promise` та `custom_future`:

```cpp
#include <iostream>
#include <thread>
#include <string>
#include <chrono>

int main() {
    std::cout << "--- 1. Успішна передача значення ---" << std::endl;
    {
        custom::custom_promise<std::string> promise;
        custom::custom_future<std::string> future = promise.get_future();

        std::thread worker([p = std::move(promise)]() mutable {
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            p.set_value("Результат обчислень готовий!");
        });

        std::cout << "Головний потік чекає..." << std::endl;
        std::string res = future.get();
        std::cout << "Отримано: " << res << std::endl;
        worker.join();
    }

    std::cout << "\n--- 2. Передача винятку через межу потоків ---" << std::endl;
    {
        custom::custom_promise<int> promise;
        custom::custom_future<int> future = promise.get_future();

        std::thread worker([p = std::move(promise)]() mutable {
            try {
                throw std::invalid_argument("Помилка вхідних даних у фоновому потоці!");
            } catch (...) {
                p.set_exception(std::current_exception());
            }
        });

        try {
            int val = future.get();
            std::cout << "Значення: " << val << std::endl;
        } catch (const std::exception& e) {
            std::cout << "Перехоплено виняток у головному потоці: " << e.what() << std::endl;
        }
        worker.join();
    }

    return 0;
}
```

Цей приклад підтверджує, що створена C++ реалізація точково відтворює поведінку стандартних примітивів `std::promise` та `std::future`, демонструючи внутрішні механізми асинхронного транспортування даних та винятків між потоками у C++.
