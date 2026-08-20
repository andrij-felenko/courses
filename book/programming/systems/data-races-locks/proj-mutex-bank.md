# ⚙️ Конкурентний банківський рахунок: перегони даних, взаємне виключення та атомарні перекази

У багатопотокових фінансових та транзакційних системах кожна операція над грошовим балансом має бути абсолютно детермінованою. Якщо сотні клієнтів одночасно поповнюють рахунки, знімають кошти чи виконують зустрічні перекази, система зобов'язана гарантувати фундаментальний **закон збереження грошей**: сумарний баланс системи до початку всіх транзакцій і після їх завершення має збігатися з абсолютною точністю до копійки.

Цей інженерний проєкт демонструє еволюцію системи управління рахунками: від виявлення прихованих перегонів даних і дедлоків до побудови надійної багатопотокової архітектури з використанням [замків (м'ютексів)](book:programming/data-races-locks), канонічного впорядкування ресурсів та стандартних алгоритмів C++.

---

### 1. Вразливий рахунок: як несинхронізований код знищує баланс

Спершу розглянемо наївну реалізацію рахунку, де модифікація балансу виконується прямими арифметичними операціями над пам'яттю:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t balance;
} UnsafeAccount;

void account_deposit_unsafe(UnsafeAccount *acc, int64_t amount) {
    acc->balance += amount; // ПЕРЕГОНИ ДАНИХ (Load -> Add -> Store)
}

bool account_withdraw_unsafe(UnsafeAccount *acc, int64_t amount) {
    if (acc->balance >= amount) {
        acc->balance -= amount; // ПЕРЕГОНИ ДАНИХ (Check-Then-Act)
        return true;
    }
    return false;
}
```
```cpp
#include <cstdint>

struct UnsafeAccount {
    int64_t balance{0};

    void deposit(int64_t amount) noexcept {
        balance += amount; // ПЕРЕГОНИ ДАНИХ (неподільна на вигляд, але три кроки в CPU)
    }

    bool withdraw(int64_t amount) noexcept {
        if (balance >= amount) {
            balance -= amount; // ПЕРЕГОНИ ДАНИХ (між перевіркою і відніманням втручається інший потік)
            return true;
        }
        return false;
    }
};
```
:::

#### Анатомія руйнування балансу в апаратурі
Коли компілятор транслює вираз `acc->balance += amount` у машинний код, він розбиває його на три інструкції:
1. Завантаження поточного балансу з оперативної пам'яті в регістр процесора (`mov rax, [rdi]`).
2. Додавання суми депозиту в регістрі (`add rax, rsi`).
3. Запис оновленого значення назад у пам'ять (`mov [rdi], rax`).

Якщо два процесорні ядра одночасно виконують цю функцію для одного рахунку, їхні інструкції перетинаються в часі: обидва ядра зчитують початковий баланс `1000` грн, перше ядро додає `500` і записує `1500`, а друге ядро додає `200` до зчитаного раніше `1000` і записує `1200` поверх значення першого ядра. У результаті `500` грн клієнта безслідно зникають із системи.

---

### 2. Захист окремого рахунку: взаємне виключення за допомогою м'ютекса

Щоб зробити операції поповнення та зняття неподільними (атомарними), пов'яжемо кожен рахунок із його власним замком:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct {
    int64_t balance;
    pthread_mutex_t lock;
} SafeAccount;

void safe_account_init(SafeAccount *acc, int64_t initial_balance) {
    acc->balance = initial_balance;
    pthread_mutex_init(&acc->lock, NULL);
}

void safe_account_destroy(SafeAccount *acc) {
    pthread_mutex_destroy(&acc->lock);
}

void safe_account_deposit(SafeAccount *acc, int64_t amount) {
    pthread_mutex_lock(&acc->lock);
    acc->balance += amount;
    pthread_mutex_unlock(&acc->lock);
}

bool safe_account_withdraw(SafeAccount *acc, int64_t amount) {
    pthread_mutex_lock(&acc->lock);
    if (acc->balance >= amount) {
        acc->balance -= amount;
        pthread_mutex_unlock(&acc->lock);
        return true;
    }
    pthread_mutex_unlock(&acc->lock);
    return false;
}
```
```cpp
#include <cstdint>
#include <mutex>

class SafeAccount {
public:
    explicit SafeAccount(int64_t initial_balance = 0) noexcept
        : balance_(initial_balance) {}

    void deposit(int64_t amount) {
        // std::lock_guard гарантує звільнення замка в деструкторі
        std::lock_guard<std::mutex> guard(mutex_);
        balance_ += amount;
    }

    bool withdraw(int64_t amount) {
        std::lock_guard<std::mutex> guard(mutex_);
        if (balance_ >= amount) {
            balance_ -= amount;
            return true;
        }
        return false;
    }

    int64_t get_balance() const {
        std::lock_guard<std::mutex> guard(mutex_);
        return balance_;
    }

    std::mutex& get_mutex() const noexcept {
        return mutex_;
    }

    // Внутрішні методи для складених операцій (викликати виключно під захопленим замком)
    int64_t raw_balance() const noexcept { return balance_; }
    void raw_modify(int64_t delta) noexcept { balance_ += delta; }

private:
    int64_t balance_{0};
    mutable std::mutex mutex_;
};
```
:::

У C++ версії деструктор `std::lock_guard` автоматично звільняє замок під час повернення з функції (навіть при виникненні винятку), що повністю виключає ризик витоку замків.

---

### 3. Проблема двох замків: зустрічні перекази та пастка дедлоку

Справжня складність виникає під час атомарного переказу коштів між двома рахунками `A` і `B`. Щоб сторонній спостерігач не міг зафіксувати момент, коли гроші вже знято з `A`, але ще не зараховано на `B`, необхідно захопити замки **обох** рахунків одночасно.

Погляньмо на наївну реалізацію переказу:

:::tabs
```c
// НЕБЕЗПЕЧНО: ПРИЗВОДИТЬ ДО ДЕДЛОКУ ПРИ ЗУСТРІЧНИХ ПЕРЕКАЗАХ!
bool bad_transfer(SafeAccount *from, SafeAccount *to, int64_t amount) {
    pthread_mutex_lock(&from->lock); // Захоплюємо перший рахунок
    pthread_mutex_lock(&to->lock);   // Захоплюємо другий рахунок

    bool success = false;
    if (from->balance >= amount) {
        from->balance -= amount;
        to->balance += amount;
        success = true;
    }

    pthread_mutex_unlock(&to->lock);
    pthread_mutex_unlock(&from->lock);
    return success;
}
```
```cpp
// НЕБЕЗПЕЧНО: ПРИЗВОДИТЬ ДО ДЕДЛОКУ!
bool bad_transfer(SafeAccount& from, SafeAccount& to, int64_t amount) {
    std::unique_lock<std::mutex> lock_from(from.get_mutex());
    std::unique_lock<std::mutex> lock_to(to.get_mutex());

    if (from.raw_balance() >= amount) {
        from.raw_modify(-amount);
        to.raw_modify(amount);
        return true;
    }
    return false;
}
```
:::

#### Умови виникнення взаємного блокування (Дедлоку)
Якщо Потік 1 виконує переказ `A → B`, а Потік 2 одночасно виконує переказ `B → A`:
1. Потік 1 захоплює замок рахунку `A` і готується захопити `B`.
2. Потік 2 у цей самий час захоплює замок рахунку `B` і готується захопити `A`.
3. Потік 1 блокується в очікуванні `B`, який тримає Потік 2.
4. Потік 2 блокується в очікуванні `A`, який тримає Потік 1.

Виникає класичний **дедлок** (взаємне блокування за умовами Кофмана: наявність взаємного виключення, утримання ресурсу в очікуванні іншого, відсутність примусового вилучення та замкнений круговий ланцюг залежностей). Обидва потоки засинають назавжди, зупиняючи обробку платежів.

---

### 4. Рішення: Канонічне впорядкування покажчиків та `std::scoped_lock`

Щоб розірвати круговий ланцюг очікування, необхідно ліквідувати четверту умову Кофмана: встановити **строгий глобальний порядок захоплення замків**.

У мові C найефективнішим критерієм глобального порядку є числове порівняння фізичних адрес пам'яті (`uintptr_t`): ми завжди спершу захоплюємо замок з меншою адресою, а другим — замок з більшою адресою.

У сучасному C++ (C++17) для цього створено шаблон `std::scoped_lock`, який приймає довільну кількість м'ютексів і всередині реалізує алгоритм запобігання дедлокам (на основі `std::lock` із механізмом `try_lock` backoff):

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

bool safe_account_transfer(SafeAccount *from, SafeAccount *to, int64_t amount) {
    if (from == to || amount <= 0) {
        return false;
    }

    // Визначаємо канонічний порядок блокування за адресою в пам'яті
    SafeAccount *first = from;
    SafeAccount *second = to;
    if ((uintptr_t)from > (uintptr_t)to) {
        first = to;
        second = from;
    }

    // Захоплюємо замки у строго визначеному порядку: менша адреса -> більша адреса
    pthread_mutex_lock(&first->lock);
    pthread_mutex_lock(&second->lock);

    bool success = false;
    if (from->balance >= amount) {
        from->balance -= amount;
        to->balance += amount;
        success = true;
    }

    // Звільняємо у зворотному порядку
    pthread_mutex_unlock(&second->lock);
    pthread_mutex_unlock(&first->lock);

    return success;
}
```
```cpp
#include <cstdint>
#include <mutex>

bool transfer_money(SafeAccount& from, SafeAccount& to, int64_t amount) {
    if (&from == &to || amount <= 0) {
        return false;
    }

    // std::scoped_lock гарантує одночасне захоплення двох замків без ризику дедлоку
    // і автоматично звільняє їх при будь-якому виході з функції
    std::scoped_lock lock(from.get_mutex(), to.get_mutex());

    if (from.raw_balance() >= amount) {
        from.raw_modify(-amount);
        to.raw_modify(amount);
        return true;
    }

    return false;
}
```
:::

---

### 5. Повний верифікаційний тест: перевірка збереження балансу

Напишемо тестовий стенд, який запускає 8 паралельних потоків. Половина потоків переказує кошти з рахунку 1 на рахунок 2, а інша половина — одночасно з рахунку 2 на рахунок 1. Загалом виконується 4 000 000 зустрічних переказів:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>

#define NUM_TRANSFERS 500000

SafeAccount g_acc1;
SafeAccount g_acc2;

void* worker_1_to_2(void *arg) {
    (void)arg;
    for (int i = 0; i < NUM_TRANSFERS; ++i) {
        safe_account_transfer(&g_acc1, &g_acc2, 10);
    }
    return NULL;
}

void* worker_2_to_1(void *arg) {
    (void)arg;
    for (int i = 0; i < NUM_TRANSFERS; ++i) {
        safe_account_transfer(&g_acc2, &g_acc1, 10);
    }
    return NULL;
}

int main(void) {
    safe_account_init(&g_acc1, 100000);
    safe_account_init(&g_acc2, 100000);

    pthread_t threads[8];
    for (int i = 0; i < 4; ++i) {
        pthread_create(&threads[i], NULL, worker_1_to_2, NULL);
        pthread_create(&threads[i + 4], NULL, worker_2_to_1, NULL);
    }

    for (int i = 0; i < 8; ++i) {
        pthread_join(threads[i], NULL);
    }

    int64_t total = g_acc1.balance + g_acc2.balance;
    printf("Баланс 1: %lld, Баланс 2: %lld, Разом: %lld (Очікувалося: 200000)\n",
           (long long)g_acc1.balance, (long long)g_acc2.balance, (long long)total);

    safe_account_destroy(&g_acc1);
    safe_account_destroy(&g_acc2);
    return (total == 200000) ? 0 : 1;
}
```
```cpp
#include <iostream>
#include <thread>
#include <vector>

constexpr int NUM_TRANSFERS = 500000;

int main() {
    SafeAccount acc1(100000);
    SafeAccount acc2(100000);

    std::vector<std::jthread> threads;
    threads.reserve(8);

    // 4 потоки переказують з acc1 на acc2
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&acc1, &acc2]() {
            for (int k = 0; k < NUM_TRANSFERS; ++k) {
                transfer_money(acc1, acc2, 10);
            }
        });
    }

    // 4 потоки паралельно переказують з acc2 на acc1
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&acc1, &acc2]() {
            for (int k = 0; k < NUM_TRANSFERS; ++k) {
                transfer_money(acc2, acc1, 10);
            }
        });
    }

    // Очікуємо завершення всіх потоків
    threads.clear();

    const int64_t total = acc1.get_balance() + acc2.get_balance();
    std::cout << "Баланс 1: " << acc1.get_balance()
              << ", Баланс 2: " << acc2.get_balance()
              << ", Разом: " << total << " (Очікувалося: 200000)\n";

    return (total == 200000) ? 0 : 1;
}
```
:::

#### Підсумковий результат та аналіз продуктивності

Завдяки впорядкованому захопленню замків тестова програма виконує всі 4 мільйони переказів за частки секунди, жодного разу не зависаючи в дедлоку, а підсумкова сума на обох рахунках точно дорівнює початковим `200 000` грн.

---

### 6. Тонкощі оптимізації: Хибне розділення та нечесність замків

Під час побудови високопродуктивних банківських систем виникають два додаткових апаратних підводних камені:

#### 1. Хибне розділення кеш-ліній (False Sharing)
Якщо два незалежні рахунки `g_acc1` та `g_acc2` розташовані в пам'яті поруч (наприклад, у сусідніх елементах масиву), їхні поля балансу та замків опиняються в межах однієї 64-байтної кеш-лінії процесора.

Коли Потік 1 модифікує замок першого рахунку, апаратний протокол когерентності MESI інвалідує всю 64-байтну лінію в кеші ядра Потоку 2. Виникає так званий пінг-понг кеш-ліній (cache line bouncing): потоки заважають одне одному на рівні шини пам'яті, навіть працюючи з абсолютно різними клієнтськими рахунками.

Для усунення цього ефекту структури рахунків вирівнюють за межею кеш-лінії:
- У C11: `alignas(64)` або `_Alignas(64)`.
- У C++17: `alignas(std::hardware_destructive_interference_size)`.

#### 2. Нечесність замків і явище вклинювання (Lock Barging)
Сучасні замки `pthread_mutex` та `std::mutex` у Linux за замовчуванням є **нечесними (non-fair / barging locks)**:

Коли потік-власник звільняє замок і будить сплячий потік із черги futex, операційній системі потрібні мікросекунди на перемикання контексту. Якщо в цей час на іншому ядрі з'являється свіжий потік, який намагається виконати швидкий `CAS(0, 1)`, він негайно «вклинюється» і забирає вільний замок собі, змушуючи щойно розбуджений потік знову заснути.

Ця нечесність є свідомим компромісом розробників ОС: вона різко збільшує сумарну пропускну здатність системи (бо гаряче ядро не чекає пробудження холодного потоку), але створює ризик короткочасного голодування (starvation) для окремих потоків. Для фінансових транзакцій із суворими вимогами до максимальної затримки (latency SLA) це враховують під час вибору архітектури черг.
