# ⚙️ Практична реалізація м'ютекса й умовної змінної на futex

Ця вставка містить повноцінний практичний проект реалізації користувацького м'ютекса з трьома станами (0, 1, 2) та умовної змінної (condition variable) з оптимізованим перепідключенням очікуючих потоків через `FUTEX_CMP_REQUEUE`.

## Архітектура тристанового м'ютекса Ульріха Дреппера

Найпростіший двостановий м'ютекс (де значення `0` означає «вільний», а `1` — «зайнятий») має істотну ваду продуктивності. Коли потік викликає операцію звільнення м'ютекса `unlock()`, він змінює значення з `1` на `0`. Проте у просторі користувача потік не має інформації про те, чи є в цей момент інші потоки, заблоковані у ядрі в очікуванні цього ресурсу.

Через відсутність цієї інформації двостановий м'ютекс змушений виконувати системний виклик `futex(FUTEX_WAKE)` при **кожному** звільненні ресурсу. Це зводить нанівець переваги швидкого шляху (Fast Path), адже звільнення ресурсу за наявності хоча б одного потоку у системі перетворюється на обов'язковий системний виклик.

Для усунення цього недоліку розробник Ульріх Дреппер запропонував концепцію **тристанового м'ютекса**, де значення 32-бітної змінної відображає не лише факт блокування, а й наявність конкуренції:

- **Стан `0` (UNLOCKED)**: М'ютекс повністю вільний. Жоден потік не утримує ресурс, і у ядрі немає заблокованих потоків.
- **Стан `1` (LOCKED_WITHOUT_WAITERS)**: М'ютекс захоплений одним потоком, але у ядрі **немає** жодного заблокованого потоку, що чекає на цей м'ютекс.
- **Стан `2` (LOCKED_WITH_WAITERS)**: М'ютекс захоплений одного потоком, і у ядрі **є принаймні один** заблокований потік у стан очікування `TASK_INTERRUPTIBLE`.

### Покроковий алгоритм захоплення м'ютекса (`lock`)

1. **Спроба швидкого захоплення (Fast Path)**:
   Потік виконує атомарну операцію Compare-And-Swap (CAS), намагаючись змінити значення змінної з `0` на `1`. Якщо початковий стан був `0`, операція завершується успіхом за 5-10 тактів CPU, і потік одразу входить у критичну секцію без системного виклику.

2. **Перехід у повільний шлях (Slow Path)**:
   Якщо початковий стан не дорівнював `0` (тобто м'ютекс уже був у стані `1` або `2`), потік виконує атомарну операцію `exchange`, встановлюючи стан `2`. Ця дія гарантує, що прапорець наявності очікуючих потоків встановлено.

3. **Засинання у ядрі**:
   Потік у циклі викликає системний виклик `futex_wait(uaddr, 2)`. Ядро перевіряє, чи значення за адресою `uaddr` досі дорівнює `2`. Якщо так, потік засинає. Після пробудження потік знову намагається атомарно встановити стан `2` і повторює цикл, доки не перехопить стан `0`.

### Покроковий алгоритм звільнення м'ютекса (`unlock`)

1. **Перевірка наявності очікуючих**:
   Потік атомарно зменшує значення м'ютекса на одиницю за допомогою інструкції `fetch_sub(1)`.

2. **Швидке звільнення (Fast Path)**:
   Якщо значення перед зменшенням дорівнювало `1` (тобто м'ютекс був у стані `LOCKED_WITHOUT_WAITERS`), нове значення стає `0`. Потік завершує виконання `unlock()` миттєво без виклику ядра.

3. **Повільне звільнення з пробудженням (Slow Path)**:
   Якщо значення перед зменшенням дорівнювало `2` (або вище), це означає, що в ядрі чекають інші потоки. Потік атомарно записує `0` у значення м'ютекса й здійснює системний виклик `futex_wake(uaddr, 1)`, розбуджуючи рівно один заблокований потік.

## Архітектура умовної змінної з `FUTEX_CMP_REQUEUE`

Умовна змінна (Condition Variable) в описуваному проекті будується на основі 32-бітного атомарного лічильника послідовності `sequence`.

1. **Механіка виклику `wait(mutex)`**:
   Потік зчитує поточне значення `sequence`, після чого атомарно звільняє м'ютекс за допомогою `futex_mutex_unlock()`. Далі потік здійснює системний виклик `futex_wait(&sequence, seq)`. Якщо значення `sequence` не змінювалося, потік засинає у ядрі. Після пробудження потік повторно захоплює м'ютекс через `futex_mutex_lock()`.

2. **Механіка виклику `signal()`**:
   Потік атомарно збільшує значення `sequence` на одиницю й викликає `futex_wake(&sequence, 1)`, розбуджуючи один потік із черги умовної змінної.

3. **Механіка виклику `broadcast(mutex)` із запобіганням шторму пробуджень**:
   При масовому сповіщенні розбудження всіх потоків викликало б масову конкуренцію за м'ютекс у просторі користувача. Замість цього потік збільшує `sequence` на 1 і викликає `futex_cmp_requeue(&sequence, &mutex->state, 1, INT_MAX, seq)`. Ядро атомарно розбуджує 1 потік, а всі інші потоки переносить із черги `sequence` безпосередньо у чергу `mutex->state` всередині ядра.

## Реалізація вихідного коду

Нижче наведено ідіоматичні реалізації тристанового м'ютекса та умовної змінної мовами C (з використанням `stdatomic.h` та системних обгорток) та C++ (із застосуванням `std::atomic`, моделей пам'яті та RAII-обгортки `lock_guard`).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <time.h>
#include <pthread.h>

// Системна обгортка для операції очікування futex_wait
static inline int futex_wait(atomic_uint *uaddr, unsigned int val) {
    return syscall(SYS_futex, uaddr, FUTEX_WAIT_PRIVATE, val, NULL, NULL, 0);
}

// Системна обгортка для операції пробудження futex_wake
static inline int futex_wake(atomic_uint *uaddr, int count) {
    return syscall(SYS_futex, uaddr, FUTEX_WAKE_PRIVATE, count, NULL, NULL, 0);
}

// Системна обгортка для операції перепідключення futex_cmp_requeue
static inline int futex_cmp_requeue(atomic_uint *uaddr1, atomic_uint *uaddr2,
                                   int wake_count, int requeue_count, unsigned int val3) {
    return syscall(SYS_futex, uaddr1, FUTEX_CMP_REQUEUE_PRIVATE, wake_count,
                   requeue_count, uaddr2, val3);
}

// Структура тристанового м'ютекса
typedef struct {
    atomic_uint state; // 0 = unlocked, 1 = locked without waiters, 2 = locked with waiters
} futex_mutex_t;

void futex_mutex_init(futex_mutex_t *m) {
    atomic_store(&m->state, 0);
}

void futex_mutex_lock(futex_mutex_t *m) {
    unsigned int c = 0;
    // Швидкий шлях: спроба змінити 0 -> 1 у просторі користувача
    if (atomic_compare_exchange_strong(&m->state, &c, 1)) {
        return; // Захоплено швидко без системного виклику
    }

    // Повільний шлях: м'ютекс зайнятий, фіксуємо наявність очікуючих
    if (c != 2) {
        c = atomic_exchange(&m->state, 2);
    }
    
    while (c != 0) {
        // Засинаємо у ядрі, лише якщо стан досі 2
        futex_wait(&m->state, 2);
        c = atomic_exchange(&m->state, 2);
    }
}

void futex_mutex_unlock(futex_mutex_t *m) {
    // Якщо стан був 1, новий стан 0, повертаємося швидко
    if (atomic_fetch_sub(&m->state, 1) != 1) {
        // Були очікуючі потоки (стан був 2)
        atomic_store(&m->state, 0);
        // Будимо 1 очікуючий потік у ядрі
        futex_wake(&m->state, 1);
    }
}

// Структура умовної змінної
typedef struct {
    atomic_uint sequence;
} futex_cond_t;

void futex_cond_init(futex_cond_t *c) {
    atomic_store(&c->sequence, 0);
}

void futex_cond_wait(futex_cond_t *c, futex_mutex_t *m) {
    unsigned int seq = atomic_load(&c->sequence);
    
    // Відпускаємо м'ютекс перед засинанням
    futex_mutex_unlock(m);
    
    // Чекаємо на зміну sequence у ядрі
    futex_wait(&c->sequence, seq);
    
    // Після пробудження знову захоплюємо м'ютекс
    futex_mutex_lock(m);
}

void futex_cond_signal(futex_cond_t *c) {
    atomic_fetch_add(&c->sequence, 1);
    futex_wake(&c->sequence, 1);
}

void futex_cond_broadcast(futex_cond_t *c, futex_mutex_t *m) {
    unsigned int seq = atomic_fetch_add(&c->sequence, 1) + 1;
    // Будимо 1 потік на condvar, а решту (INT_MAX) переносимо в чергу м'ютекса m
    futex_cmp_requeue(&c->sequence, &m->state, 1, 2147483647, seq);
}
```
```cpp
#include <iostream>
#include <atomic>
#include <cstdint>
#include <climits>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>

namespace sys {

class futex_mutex {
public:
    enum class state : uint32_t {
        unlocked = 0,
        locked_no_waiters = 1,
        locked_with_waiters = 2
    };

    constexpr futex_mutex() noexcept : state_{0} {}

    void lock() noexcept {
        uint32_t expected = 0;
        // Швидкий шлях (Fast Path): 0 -> 1 у просторі користувача з аквізиційною семантикою
        if (state_.compare_exchange_strong(expected, 1, std::memory_order_acquire)) {
            return;
        }

        if (expected != 2) {
            expected = state_.exchange(2, std::memory_order_acquire);
        }

        while (expected != 0) {
            futex_wait(reinterpret_cast<uint32_t*>(&state_), 2);
            expected = state_.exchange(2, std::memory_order_acquire);
        }
    }

    void unlock() noexcept {
        // Релізна семантика вивантаження критичної секції
        if (state_.fetch_sub(1, std::memory_order_release) != 1) {
            state_.store(0, std::memory_order_release);
            futex_wake(reinterpret_cast<uint32_t*>(&state_), 1);
        }
    }

    uint32_t* native_handle() noexcept {
        return reinterpret_cast<uint32_t*>(&state_);
    }

private:
    static inline int futex_wait(uint32_t* uaddr, uint32_t val) noexcept {
        return ::syscall(SYS_futex, uaddr, FUTEX_WAIT_PRIVATE, val, nullptr, nullptr, 0);
    }

    static inline int futex_wake(uint32_t* uaddr, int count) noexcept {
        return ::syscall(SYS_futex, uaddr, FUTEX_WAKE_PRIVATE, count, nullptr, nullptr, 0);
    }

    std::atomic<uint32_t> state_;
};

// RAII обгортка для автоматичного керування блокуванням м'ютекса
class lock_guard {
public:
    explicit lock_guard(futex_mutex& m) : mutex_(m) {
        mutex_.lock();
    }
    ~lock_guard() {
        mutex_.unlock();
    }

    lock_guard(const lock_guard&) = delete;
    lock_guard& operator=(const lock_guard&) = delete;

private:
    futex_mutex& mutex_;
};

class futex_condvar {
public:
    constexpr futex_condvar() noexcept : sequence_{0} {}

    void wait(futex_mutex& m) noexcept {
        uint32_t seq = sequence_.load(std::memory_order_relaxed);
        m.unlock();
        futex_wait(reinterpret_cast<uint32_t*>(&sequence_), seq);
        m.lock();
    }

    void signal() noexcept {
        sequence_.fetch_add(1, std::memory_order_release);
        futex_wake(reinterpret_cast<uint32_t*>(&sequence_), 1);
    }

    void broadcast(futex_mutex& m) noexcept {
        uint32_t seq = sequence_.fetch_add(1, std::memory_order_release) + 1;
        futex_cmp_requeue(reinterpret_cast<uint32_t*>(&sequence_),
                          m.native_handle(), 1, INT_MAX, seq);
    }

private:
    static inline int futex_wait(uint32_t* uaddr, uint32_t val) noexcept {
        return ::syscall(SYS_futex, uaddr, FUTEX_WAIT_PRIVATE, val, nullptr, nullptr, 0);
    }

    static inline int futex_wake(uint32_t* uaddr, int count) noexcept {
        return ::syscall(SYS_futex, uaddr, FUTEX_WAKE_PRIVATE, count, nullptr, nullptr, 0);
    }

    static inline int futex_cmp_requeue(uint32_t* uaddr1, uint32_t* uaddr2,
                                       int wake_count, int requeue_count, uint32_t val3) noexcept {
        return ::syscall(SYS_futex, uaddr1, FUTEX_CMP_REQUEUE_PRIVATE,
                          wake_count, requeue_count, uaddr2, val3);
    }

    std::atomic<uint32_t> sequence_;
};

} // namespace sys
```
:::

## Детальний розбір потенційних пасток та крайових випадків

### 1. Гонка запізнілого пробудження (Lost Wakeup) у `condvar.wait()`
У реалізації умовної змінної існує часове вікно між моментом, коли потік вичитує `sequence`, і моментом, коли починає виконуватися системний виклик `futex_wait`. Якщо інший потік викличе `signal()` і збільшить `sequence` у цьому проміжку, перший потік міг би заснути назавжди.
Проте системний виклик `futex_wait` приймає локально зчитане значення `seq` і порівнює його з поточним значенням у пам'яті вже під захистом внутрішнього спінлока ядра. Оскільки `sequence` було збільшено, ядро виявить розбіжність і поверне помилку `EWOULDBLOCK`, запобігаючи нескінченній блокуванню.

### 2. Моделі впорядкування пам'яті (Memory Ordering)
При реалізації у мові C++ надзвичайно важливо дотримуватися правил упорядкування інструкцій:
- Захоплення м'ютекса (`lock`) зобов'язане використовувати семантику `std::memory_order_acquire`. Це гарантує, що жодне зчитування чи запис даних із критичної секції не буде перенесене компілятором або процесором до моменту успішного захоплення блокування.
- Звільнення м'ютекса (`unlock`) зобов'язане використовувати семантику `std::memory_order_release`. Це гарантує, що всі модифікації даних критичної секції будуть записані у кеш-пам'ять і стануть видимими для інших ядер до того, як м'ютекс перейде у стан `0`.

### 3. Захист від хибних пробуджень (Spurious Wakeups)
Системний виклик `futex_wait` може повернути керування у простір користувача не лише при виклику `FUTEX_WAKE`, а й при надходженні POSIX-сигналу (`EINTR`) або при внутрішніх оптимізаціях планувальника ядра. Тому перевірка бізнес-умови навколо `condvar.wait()` у прикладній програмі завжди зобов'язана виконуватися всередині циклу `while (!condition_met)`, а не поодинокого розгалуження `if`.
