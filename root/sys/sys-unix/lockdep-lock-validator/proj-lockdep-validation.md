# ⚙️ Практика: емуляція перевіряча та усунення дедлоків

Ця практична вставка детально описує роботу з перевіркою залежностей блокувань у двох середовищах: у просторі ядра Linux через створення повноцінного модуля з демонстрацією системного валідатора Lockdep та у просторі користувача через розбір порівняльних реалізацій мовами C та C++ з використанням сучасних безпечних примітивів синхронізації, динамічного впорядкування та шаблонів RAII.

## Демонстраційний модуль ядра Linux: штучний ABBA дедлок

Для вивчення реакції валідатора Lockdep створимо тестовий модуль ядра Linux. Його мета — сформувати два незалежні класи м'ютексів та запустити два фонові потоки ядра (`kthread`), які навмисно звертатимуться до цих м'ютексів у протилежному порядку.

При написанні таких модулів важливо забезпечити часовий перетин викликів. Якщо Потік 1 повністю завершить свою роботу до того, як Потік 2 зробить перший виклик, фізичний дедлок не станеться, але Lockdep все одно зафіксує конфлікт логіки. Додавання невеликої затримки `msleep(50)` між захопленням першого та другого блокувань гарантує, що в моменти викликів обидва потоки перебуватимуть у критичних секціях одночасно.

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/mutex.h>
#include <linux/kthread.h>
#include <linux/delay.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Lockdep Educational Demo");
MODULE_DESCRIPTION("Module demonstrating Lockdep ABBA detection");

/* Оголошення двох статичних класів м'ютексів */
static DEFINE_MUTEX(lock_alpha);
static DEFINE_MUTEX(lock_beta);

static struct task_struct *thread_1;
static struct task_struct *thread_2;

/* Перший потік: Порядок захоплення Alpha -> Beta */
static int worker_thread_1(void *arg)
{
    pr_info("LockdepDemo: Thread 1 starting. Sequence: Alpha -> Beta\n");
    
    mutex_lock(&lock_alpha);
    pr_info("LockdepDemo: Thread 1 acquired Alpha\n");
    
    /* Затримка для перекриття часу виконання потоків */
    msleep(50); 
    
    mutex_lock(&lock_beta);
    pr_info("LockdepDemo: Thread 1 acquired Beta\n");
    
    mutex_unlock(&lock_beta);
    mutex_unlock(&lock_alpha);
    
    pr_info("LockdepDemo: Thread 1 finished cleanly\n");
    return 0;
}

/* Другий потік: Порядок захоплення Beta -> Alpha */
static int worker_thread_2(void *arg)
{
    pr_info("LockdepDemo: Thread 2 starting. Sequence: Beta -> Alpha\n");
    
    mutex_lock(&lock_beta);
    pr_info("LockdepDemo: Thread 2 acquired Beta\n");
    
    msleep(50);
    
    /* Спроба взяти Alpha утримуючи Beta -> Формування ребра Beta -> Alpha */
    mutex_lock(&lock_alpha);
    pr_info("LockdepDemo: Thread 2 acquired Alpha\n");
    
    mutex_unlock(&lock_alpha);
    mutex_unlock(&lock_beta);
    
    pr_info("LockdepDemo: Thread 2 finished cleanly\n");
    return 0;
}

static int __init lockdep_demo_init(void)
{
    pr_info("LockdepDemo: Loading module...\n");
    
    /* Запуск двох фонових потоків ядра */
    thread_1 = kthread_run(worker_thread_1, NULL, "lockdep_wrk1");
    thread_2 = kthread_run(worker_thread_2, NULL, "lockdep_wrk2");
    
    return 0;
}

static void __exit lockdep_demo_exit(void)
{
    pr_info("LockdepDemo: Unloading module\n");
}

module_init(lockdep_demo_init);
module_exit(lockdep_demo_exit);
```

## Порядковий аналіз звіту `dmesg`

При завантаженні побудованого модуля в ядро з увімкненим прапорцем `CONFIG_PROVE_LOCKING` у системний журнал виводиться діагностичне повідомлення високої деталізації. Розберемо його структуру шар за шаром, щоб навчитися швидко читати результати перевірки Lockdep.

```text
[ INFO: possible circular locking dependency detected ]
6.6.0-rc1+ #1 Not tainted
------------------------------------------------------
lockdep_wrk2/1420 is trying to acquire lock:
ffffffff82c40020 (lock_alpha){+.+.}-{3:3}, at: worker_thread_2+0x42/0x80 [lockdep_demo]

but task is already holding lock:
ffffffff82c40060 (lock_beta){+.+.}-{3:3}, at: worker_thread_2+0x1c/0x80 [lockdep_demo]

which lock already depends on the new lock.
```

### Аналіз першого блоку звіту:
1. **Заголовок `possible circular locking dependency detected`**: Сигналізує про виявлення циклу у графі залежностей (ABBA).
2. **Інформація про процес**: Потік `lockdep_wrk2` із PID 1420 намагається взяти `lock_alpha`.
3. **Адреси та назви класів**: `ffffffff82c40020 (lock_alpha)` — адреса об'єкта та назва класу блокування.
4. **Матриця станів `({+.+.}-{3:3})`**:
   - Перший символ `+`: Клас використовувався з увімкненими hardirq (`hardirq-unsafe`).
   - Другий символ `.`: Стан для softirq не порушено.
   - Третій символ `+`: Клас брався у звичайному процесному контексті з увімкненими перериваннями.
   - Четвертий символ `.`: Режим читання/запису без зауважень.
   - Цифри `{3:3}`: Рівень вкладеності та глибина ланцюжка захоплення.

Далі у звіті наводиться зворотне розгортання графа залежностей (reverse dependency chain):

```text
the existing dependency chain (in reverse order) is:

-> #1 (lock_beta){+.+.}-{3:3}:
       lock_acquire+0xbd/0x2a0
       __mutex_lock+0x8e/0x970
       worker_thread_1+0x42/0x80 [lockdep_demo]

-> #0 (lock_alpha){+.+.}-{3:3}:
       lock_acquire+0xbd/0x2a0
       __mutex_lock+0x8e/0x970
       worker_thread_2+0x42/0x80 [lockdep_demo]
```

### Розшифровка графа залежностей:
- **Запис `#1`**: Вказує на ребро `lock_alpha -> lock_beta`, яке було встановлено раніше потоком `worker_thread_1` на зсуві `0x42`.
- **Запис `#0`**: Вказує на поточну спробу потоку `worker_thread_2` встановити ребро `lock_beta -> lock_alpha`.
- **Висновок валідатора**: Ядро виявило факт того, що `lock_beta` вже залежить від `lock_alpha`. Повторна спроба взяти `lock_alpha` при утримуваному `lock_beta` замикає цикл і робить можливим дедлок.

---

## Чотири стратегії усунення дедлоків у коді ядра

Після виявлення попередження Lockdep розробник ядра має кілька стандартних паттернів для виправлення помилки:

1. **Глобальне впорядкування блокувань (Strict Lock Ordering):** Переписати виклики так, щоб усі підсистеми завжди забирали замки в одному й тому ж порядку (спочатку Alpha, потім Beta). Якщо код мусить обробити об'єкти у зворотному порядку, перед викликом `mutex_lock(&lock_beta)` попередній лок `lock_alpha` має бути тимчасово звільнений (`mutex_unlock`).
2. **Спроба захоплення із відкатом (`mutex_trylock`):** Замість блокуючого виклику використовувати `mutex_trylock()`. Якщо замок вже зайнятий, потік звільняє власні утримувані блокування, поступається процесором (`schedule()` або `msleep()`) і повторює спробу спочатку.
3. **Розділення класів через підкласи (`mutex_lock_nested`):** Якщо дедлок є хибним спрацьовуванням через обробку двох об'єктів одного типу (наприклад, батьківська та дочірня інода), слід явно вказати підклас `mutex_lock_nested(&node->lock, I_MUTEX_CHILD)`.
4. **Об'єднання під єдиний батьківський лок або перехід на RCU:** Якщо два ресурси завжди модифікуються разом, замість двох окремих м'ютексів доцільно запровадити один спільний м'ютекс вищого рівня або використати механізм RCU для безпечного читання без блокувань.

---

## Простір користувача: Гарантоване запобігання дедлокам у C та C++

У прикладних програмах простору користувача ядрові макроси Lockdep недоступні. Проте проблему ABBA-дедлоків при роботі з багатьма блокуваннями вирішують або за допомогою строгого порядку захоплення за адресами лока, або через використання сучасних мовних абстракцій та алгоритмів запобігання дедлокам.

Нижче наведено порівняльний приклад переходу від ручного управління POSIX-блокуваннями у C до ідіоматичного RAII-підходу у C++20.

:::tabs
```c
/* POSIX C Implementation: Ручне сортування адрес для запобігання ABBA */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdint.h>
#include <unistd.h>

typedef struct {
    pthread_mutex_t mutex;
    int id;
} resource_t;

/* Безпечна функція захоплення двох ресурсів із сортуванням за адресами */
void acquire_two_resources_safe(resource_t *r1, resource_t *r2) {
    resource_t *first = r1;
    resource_t *second = r2;

    if (r1 == r2) {
        /* Запобігання повторному взяттю одного й того ж лока */
        pthread_mutex_lock(&r1->mutex);
        return;
    }

    /* Динамічне впорядкування за адресами в пам'яті (Lock Ordering) */
    if ((uintptr_t)r1 > (uintptr_t)r2) {
        first = r2;
        second = r1;
    }

    pthread_mutex_lock(&first->mutex);
    pthread_mutex_lock(&second->mutex);

    /* Критична секція */
    printf("C-Safe: Acquired resources %d and %d in strict address order (%p < %p)\n", 
           first->id, second->id, (void*)first, (void*)second);

    pthread_mutex_unlock(&second->mutex);
    pthread_mutex_unlock(&first->mutex);
}

int main(void) {
    resource_t a = { .id = 1 };
    resource_t b = { .id = 2 };
    
    pthread_mutex_init(&a.mutex, NULL);
    pthread_mutex_init(&b.mutex, NULL);

    /* Викликаємо з різним порядком аргументів у двох викликах */
    acquire_two_resources_safe(&a, &b);
    acquire_two_resources_safe(&b, &a);

    pthread_mutex_destroy(&a.mutex);
    pthread_mutex_destroy(&b.mutex);
    return 0;
}
```
```cpp
// Modern C++20 Implementation: RAII та std::scoped_lock
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

struct Resource {
    std::mutex mtx;
    int id;
};

void acquire_two_resources_safe(Resource& r1, Resource& r2) {
    // std::scoped_lock автоматично застосовує алгоритм запобігання дедлокам
    // (використовує std::lock усередині для атомарного та впорядкованого захоплення)
    std::scoped_lock lock(r1.mtx, r2.mtx);

    // Критична секція
    std::cout << "C++ Safe: Acquired resources " << r1.id 
              << " and " << r2.id << " without ABBA deadlock\n";
    
    // Автоматичне звільнення при виході з області видимості (RAII)
}

int main() {
    Resource res_a{.id = 1};
    Resource res_b{.id = 2};

    // Паралельний запуск двох потоків із протилежним порядком аргументів
    std::jthread t1([&]() { acquire_two_resources_safe(res_a, res_b); });
    std::jthread t2([&]() { acquire_two_resources_safe(res_b, res_a); });

    return 0;
}
```
:::

### Детальний аналіз відмінностей C та C++ підходів:

1. **Динамічне впорядкування у C (Address Ordering):** У прикладі мовою C реалізовано патерн порівняння числових значень вказівників `(uintptr_t)r1 > (uintptr_t)r2`. Оскільки адреси об'єктів у віртуальній пам'яті є унікальними та незмінними під час їхнього життя, такий підхід гарантує, що незалежно від порядку передачі аргументів у функцію, блокування `pthread_mutex_t` завжди будуть забиратися у єдиному глобальному порядку адрес. Це повністю ліквідує можливість виникнення ABBA-дедлоку. Однак у C розробник змушений самостійно стежити за викликами `pthread_mutex_unlock` при поверненні з функції на всіх гілках обробки помилок.
2. **Алгоритм запобігання дедлокам у C++20 (`std::scoped_lock`):** У прикладі мовою C++ застосовано стандартну варіативну обгортку `std::scoped_lock`. Усередині себе вона викликає функцію `std::lock()`, яка застосовує алгоритм бек-оффу (deadlock avoidance algorithm): замок намагаються взяти послідовно; якщо черговий м'ютекс виявляється зайнятим, `std::lock` автоматично звільняє всі раніше захоплені у цій операції м'ютекси, поступається процесорним часом і повторює спробу знову. Це гарантує атомарне захоплення довільної кількості `std::mutex` без загрози зависання.
3. **Гарантії RAII (Resource Acquisition Is Initialization):** Клас `std::scoped_lock` зв'язує тривалість життя критичної секції з областю видимості змінної. При виході з функції (включаючи випадки генерації винятків `throw`) деструктор обгортки автоматично звільняє всі м'ютекси у зворотному порядку, що виключає витоки блокувань та людський фактор.

---

## Створення власного валідатора класів у просторі користувача (C++20)

Для демонстрації того, як реалізовано алгоритми Lockdep на високому рівні, розіб'ємо C++ клас для динамічної перевірки порядків блокувань у прикладних програмах. Він використовує локальну пам'ять потоку (`thread_local`) та граф залежностей для пошуку циклів.

```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <stdexcept>
#include <mutex>

class UserLockValidator {
public:
    using LockID = const void*;

    static void on_lock_acquire(LockID lock) {
        auto& current_held = get_held_locks();
        
        for (LockID held : current_held) {
            // Перевіряємо, чи існує зворотне ребро у графі залежностей
            if (has_path(lock, held)) {
                std::cerr << "[LOCKDEP WARNING] Detected potential deadlock cycle! "
                          << "Trying to acquire " << lock 
                          << " while holding " << held << "\n";
                throw std::runtime_error("Deadlock cycle detected by UserLockValidator");
            }
            // Додаємо ребро held -> lock
            get_graph()[held].insert(lock);
        }
        
        current_held.push_back(lock);
    }

    static void on_lock_release(LockID lock) {
        auto& current_held = get_held_locks();
        if (!current_held.empty() && current_held.back() == lock) {
            current_held.pop_back();
        }
    }

private:
    static std::vector<LockID>& get_held_locks() {
        thread_local std::vector<LockID> held;
        return held;
    }

    static std::unordered_map<LockID, std::unordered_set<LockID>>& get_graph() {
        static std::unordered_map<LockID, std::unordered_set<LockID>> graph;
        return graph;
    }

    // Пошук шляху у графі (DFS)
    static bool has_path(LockID start, LockID target) {
        std::unordered_set<LockID> visited;
        std::vector<LockID> stack = {start};

        while (!stack.empty()) {
            LockID curr = stack.back();
            stack.pop_back();

            if (curr == target) return true;

            if (visited.find(curr) == visited.end()) {
                visited.insert(curr);
                auto& neighbors = get_graph()[curr];
                for (LockID next : neighbors) {
                    stack.push_back(next);
                }
            }
        }
        return false;
    }
};

// Обгортка для std::mutex з автоматичною перевіркою
class ValidatedMutex {
public:
    void lock() {
        UserLockValidator::on_lock_acquire(this);
        native_mutex.lock();
    }

    void unlock() {
        native_mutex.unlock();
        UserLockValidator::on_lock_release(this);
    }

private:
    std::mutex native_mutex;
};
```

Ця спрощена реалізація ілюструє ядро роботи Lockdep:
1. Кожен потік підтримує свій стек утримуваних блокувань `held_locks`.
2. При виклику `lock()` система виконує пошук у глибину (DFS) по глобальному графі, перевіряючи, чи не існує вже шляху від нового лока до лока, який тримається зараз.
3. Якщо шлях знайдено, це свідчить про спробу утворити цикл і генерує виняток `std::runtime_error`.

Такий підхід дозволяє перенести концепцію превентивної валідації Lockdep у юзерспейсні мультипотокові додатки, виявляючи архітектурні дефекти синхронізації на ранніх стадіях модульного та інтеграційного тестування.
