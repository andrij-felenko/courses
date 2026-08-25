# ⚙️ Ієрархія замків і безпечне захоплення кількох ресурсів

Класична пастка взаємного блокування виникає щоразу, коли системна операція вимагає одночасного монопольного володіння двома або більше ресурсами. Найвідоміший приклад — банківський переказ між двома рахунками: щоб захистити баланси від стану гонитви, потік мусить захопити м'ютекс рахунку-відправника та м'ютекс рахунку-отримувача. Якщо один потік переказує кошти з рахунку `A` на `B`, а інший одночасно виконує переказ із `B` на `A`, наївне захоплення замків у порядку аргументів функції неминуче призведе до дедлоку.

Найефективніший спосіб гарантувати відсутність циклів очікування у коді без використання важких менеджерів транзакцій — це **статична або динамічна ієрархія замків** (англ. *lock hierarchy*).

## Суть методу: лінійне впорядкування адрес

Четверта умова Кофмана стверджує, що дедлок неможливий без циклічного ланцюга очікування `T₁ → L₂ → T₂ → L₁ → T₁`. Якщо змусити всі потоки в системі захоплювати м'ютекси виключно у **строго зростаючому порядку їхніх унікальних ідентифікаторів** (рангів або фізичних адрес у пам'яті), граф очікувань перетворюється на орієнтований ациклічний граф (DAG). У такому графі замкнений цикл сформуватися не може в принципі.

Для довільних двох замків `mutex_a` та `mutex_b`:
1. Порівнюємо їхні адреси вказівників як цілі числа: `(uintptr_t)ptr(A) < (uintptr_t)ptr(B)`.
2. Завжди першим захоплюємо той замок, чия числова адреса менша: спочатку `lock(first)`, потім `lock(second)`.
3. Звільняємо замки у зворотному порядку або одночасно при виході з критичної секції.

Оскільки адреси об'єктів у віртуальній пам'яті процесу є глобально унікальними та незмінними протягом часу життя об'єктів, це створює строгий лінійний порядок для будь-якої пари замків без потреби у ручній нумерації.

## Реалізація безпечного переказу між рахунками

Розглянемо повну реалізацію структури банківського рахунку та безпечної функції переказу коштів двома мовами: C (із використанням POSIX Threads та ручного впорядкування за адресою) та сучасним C++ (із використанням RAII, `std::scoped_lock` та `std::unique_lock`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t id;
    int64_t balance;
    pthread_mutex_t mtx;
} account_t;

int account_init(account_t *acc, uint64_t id, int64_t initial_balance) {
    acc->id = id;
    acc->balance = initial_balance;
    return pthread_mutex_init(&acc->mtx, NULL);
}

void account_destroy(account_t *acc) {
    pthread_mutex_destroy(&acc->mtx);
}

// Безпечний переказ коштів між двома рахунками.
// Запобігає дедлоку шляхом упорядкування адрес замків у пам'яті.
bool transfer_money(account_t *from, account_t *to, int64_t amount) {
    if (from == NULL || to == NULL || amount <= 0) {
        return false;
    }

    // Крайовий випадок 1: переказ на той самий рахунок (self-transfer).
    // Спроба повторно захопити неповоротний (non-recursive) м'ютекс
    // тим самим потоком викликає негайний дедлок самого на себе.
    if (from == to) {
        return true; // Сальдо не змінюється
    }

    // Визначаємо глобальний порядок захоплення на основі адрес у пам'яті.
    // Завжди беремо спершу замок із меншою адресою.
    pthread_mutex_t *first_lock;
    pthread_mutex_t *second_lock;

    if ((uintptr_t)&from->mtx < (uintptr_t)&to->mtx) {
        first_lock = &from->mtx;
        second_lock = &to->mtx;
    } else {
        first_lock = &to->mtx;
        second_lock = &from->mtx;
    }

    // Захоплення замків у строгому порядку
    pthread_mutex_lock(first_lock);
    pthread_mutex_lock(second_lock);

    bool success = false;
    if (from->balance >= amount) {
        from->balance -= amount;
        to->balance += amount;
        success = true;
    }

    // Звільнення замків у зворотному порядку
    pthread_mutex_unlock(second_lock);
    pthread_mutex_unlock(first_lock);

    return success;
}
```
```cpp
#include <iostream>
#include <mutex>
#include <cstdint>
#include <memory>
#include <system_error>

class Account {
public:
    Account(uint64_t id, int64_t initial_balance)
        : id_(id), balance_(initial_balance) {}

    uint64_t id() const noexcept { return id_; }
    int64_t balance() const noexcept {
        std::lock_guard<std::mutex> lock(mtx_);
        return balance_;
    }

    // Дружня функція для виконання атомарного переказу
    friend bool transfer_money(Account& from, Account& to, int64_t amount);

private:
    uint64_t id_;
    int64_t balance_;
    mutable std::mutex mtx_;
};

// Безпечний переказ коштів у C++17.
// std::scoped_lock автоматично реалізує алгоритм уникнення дедлоків
// (Deadlock Avoidance Algorithm) для довільної кількості м'ютексів
// та звільняє їх за принципом RAII.
bool transfer_money(Account& from, Account& to, int64_t amount) {
    if (&from == &to || amount <= 0) {
        return (&from == &to); // Захист від подвійного взяття одного м'ютекса
    }

    // Захоплюємо обидва замки атомарно без ризику дедлоку.
    // std::scoped_lock внутрішньо використовує std::lock, який впорядковує
    // виклики або відкочує захоплення через try_lock при колізії.
    std::scoped_lock lock(from.mtx_, to.mtx_);

    if (from.balance_ < amount) {
        return false;
    }

    from.balance_ -= amount;
    to.balance_ += amount;
    return true;
}
```
:::

## Внутрішній механізм std::lock та запобігання лайвлокам

Варто розуміти, як працює алгоритм `std::lock` у стандартній бібліотеці C++, коли порядок замків не можна визначити адресою наперед (наприклад, для користувацьких блокувальних об'єктів або розподілених м'ютексів):

1. Алгоритм намагається послідовно захопити перший м'ютекс за допомогою блокуючого виклику `lock()`.
2. Для всіх наступних м'ютексів викликається неблокуючий метод `try_lock()`.
3. Якщо на якомусь кроці `try_lock()` повертає `false` (замок зайнятий іншим потоком), алгоритм **негайно звільняє всі раніше успішно захоплені м'ютекси** у зворотній послідовності.
4. Потім потік переходить до м'ютекса, на якому сталася невдача, і викликає для нього блокуючий `lock()`, щоб стати в чергу.
5. Після пробудження цикл спроб повторюється з самого початку.

Такий протокол гарантує, що жоден потік не застигне у стані утримання замка в очікуванні зайнятого сусіда. Проте для запобігання лайвлоку в умовах екстремального навантаження рантайм може застосовувати мікропаузи між ітераціями.

## Реалізація ієрархічного м'ютекса

У складних корпоративних чи системних проектах покладатися лише на самодисципліну окремих розробників небезпечно: випадковий виклик підзамкової функції у зворотній послідовності легко прослизає крізь код-рев'ю. Надійніший підхід — зафіксувати ієрархію на рівні типів даних за допомогою **ієрархічного м'ютекса** (англ. *hierarchical mutex*), який під час виконання автоматично перевіряє, чи не намагається потік порушити встановлену супідрядність.

Кожен такий м'ютекс отримує фіксований числовий ранг (наприклад, 1000 для високорівневих інтерфейсів GUI, 500 для бізнес-логіки транзакцій, 100 для низькорівневих драйверів сховища). Потік має право захопити м'ютекс лише тоді, коли його ранг **суворо нижчий** за ранг будь-якого замка, який цей потік уже утримує.

:::tabs
```cpp
#include <mutex>
#include <stdexcept>
#include <climits>
#include <cstdint>

class HierarchicalMutex {
public:
    explicit HierarchicalMutex(uint64_t hierarchy_value)
        : hierarchy_value_(hierarchy_value), previous_hierarchy_value_(0) {}

    void lock() {
        check_for_hierarchy_violation();
        internal_mutex_.lock();
        update_hierarchy_value();
    }

    void unlock() {
        if (this_thread_hierarchy_value_ != hierarchy_value_) {
            throw std::logic_error("Mutex hierarchy violated: unlocking out of order");
        }
        this_thread_hierarchy_value_ = previous_hierarchy_value_;
        internal_mutex_.unlock();
    }

    bool try_lock() {
        check_for_hierarchy_violation();
        if (!internal_mutex_.try_lock()) {
            return false;
        }
        update_hierarchy_value();
        return true;
    }

    uint64_t get_level() const noexcept { return hierarchy_value_; }

private:
    void check_for_hierarchy_violation() const {
        if (this_thread_hierarchy_value_ <= hierarchy_value_) {
            throw std::logic_error("Deadlock risk: mutex hierarchy violated! "
                                   "Attempting to acquire lock with higher or equal level.");
        }
    }

    void update_hierarchy_value() {
        previous_hierarchy_value_ = this_thread_hierarchy_value_;
        this_thread_hierarchy_value_ = hierarchy_value_;
    }

    std::mutex internal_mutex_;
    const uint64_t hierarchy_value_;
    uint64_t previous_hierarchy_value_;

    // Змінна потоку, що зберігає ранг останнього захопленого замка
    static thread_local uint64_t this_thread_hierarchy_value_;
};

// Початковий ранг для кожного нового потоку — максимальне можливе значення
thread_local uint64_t HierarchicalMutex::this_thread_hierarchy_value_(ULONG_MAX);
```
```c
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <stdbool.h>

// Для мови C змінна рангу потоку оголошується через специфікатор _Thread_local (C11)
static _Thread_local uint64_t current_thread_hierarchy = UINT64_MAX;

typedef struct {
    pthread_mutex_t mtx;
    uint64_t level;
    uint64_t prev_level;
} hier_mutex_t;

int hier_mutex_init(hier_mutex_t *h, uint64_t level) {
    h->level = level;
    h->prev_level = 0;
    return pthread_mutex_init(&h->mtx, NULL);
}

void hier_mutex_destroy(hier_mutex_t *h) {
    pthread_mutex_destroy(&h->mtx);
}

void hier_mutex_lock(hier_mutex_t *h) {
    if (current_thread_hierarchy <= h->level) {
        fprintf(stderr, "КРИТИЧНА ПОМИЛКА: порушення ієрархії замків! "
                        "Поточний ранг потоку %llu <= ранг замка %llu\n",
                (unsigned long long)current_thread_hierarchy,
                (unsigned long long)h->level);
        abort(); // Негайне аварійне завершення для виявлення дефекту на етапі тестування
    }

    pthread_mutex_lock(&h->mtx);
    h->prev_level = current_thread_hierarchy;
    current_thread_hierarchy = h->level;
}

void hier_mutex_unlock(hier_mutex_t *h) {
    if (current_thread_hierarchy != h->level) {
        fprintf(stderr, "КРИТИЧНА ПОМИЛКА: спроба звільнити замок поза чергою!\n");
        abort();
    }
    current_thread_hierarchy = h->prev_level;
    pthread_mutex_unlock(&h->mtx);
}
```
:::

## Робота з динамічними колекціями замків

Коли системна функція повинна одночасно заблокувати не два, а довільну кількість об'єктів із колекції (наприклад, провести транзакцію між `N` записами таблиці), сортування адрес покажчиків виконується динамічно:

1. Формується масив покажчиків на потрібні замки `mutex_t* locks[N]`.
2. Видаляються можливі дублікати адрес (щоб уникнути подвійного блокування одного ресурсу).
3. Масив сортується за зростанням числових значень адрес `qsort` або `std::sort`.
4. У простому циклі від `0` до `N-1` кожен замок блокується послідовно.

Оскільки всі потоки сортують множину за одним універсальним критерієм (числовою адресою), перехресне очікування стає неможливим незалежно від кількості конкуруючих потоків та ресурсів.

## Аналіз крайових випадків та підводних каменів

Під час проектування систем з ієрархічним блокуванням слід враховувати три типові пастки:

1. **Самовтягнення (Self-transfer / Aliasing)**: Якщо два покажчики або посилання вказують на той самий об'єкт у пам'яті (`&from == &to`), спроба двічі захопити неповоротний м'ютекс (`std::mutex` або стандартний `PTHREAD_MUTEX_DEFAULT`) викликає негайний дедлок одного потоку на самому собі. Перевірка рівності адрес `from == to` мусить стояти на самому початку будь-якої багатозамкової операції.

2. **Зворотні виклики під замком (Alien Methods)**: Якщо тримаючи замок низького рівня (наприклад, замок стану документа), функція викликає користувацький обробник або слухач подій (callback), цей обробник може спробувати звернутися до високорівневого інтерфейсу (наприклад, графічного вікна) і захопити його замок. Це миттєво руйнує ієрархію блокувань. Золоте правило багатопотокового дизайну: **ніколи не викликати сторонній невідомий код, утримуючи замок**.

3. **Рекурсивні замки (Recursive Mutexes)**: Хоча рекурсивні м'ютекси (`std::recursive_mutex`) рятують від самоблокування всередині одного потоку, вони не захищають від взаємного дедлоку між різними потоками. Ба більше, вони приховують помилки архітектури, ускладнюють розуміння меж критичних секцій та погіршують продуктивність через ведення лічильника повторних входів. У системному програмуванні краще уникати рекурсивних замків на користь чіткого розмежування внутрішніх функцій (які очікують, що замок уже утримується) та зовнішніх публічних методів (які захоплюють замок).
