# 📋 Інтерфейс та API бібліотеки libsolv

Ця довідкова вставка містить системну специфікацію C-бібліотеки `libsolv`, яка є основним математичним розв'язувачем графа залежностей пакунків у менеджері `DNF` (Fedora/RHEL) та `Zypper` (openSUSE). Нижче подано детальний опис внутрішньої архітектури даних, описи ключових структур, прапорців керування, функціонального API та практичні приклади інтеграції мовами C та C++.

## 1. Внутрішня архітектура пам'яті та концепція типів Id

Головною інженерною ідеєю `libsolv` є повна відмова від використання сирих текстових рядків та динамічних об'єктів під час розв'язання залежностей. Усі назви пакунків, номери версій, імена архітектур, вирази зв'язків та метадані репозиторіїв конвертуються в 32-бітні цілі числа типу `Id`.

Рядки зберігаються у централізованій таблиці інтернування (String Pool) всередині об'єкта `Pool`. Якщо назва пакунка `"nginx"` зустрічається у метаданих репозиторію 10 000 разів, у пам'яті виділяється тільки один екземпляр рядка, а всі 10 000 пакунків посилаються на нього за допомогою єдиного `Id`. Це зменшує споживання RAM у 15–20 разів порівняно зі звичайними об'єктно-орієнтованими графами та прискорює порівняння назв до однієї машинної інструкції порівняння цілих чисел `cmp` замість викликів `strcmp()`.

Концептуальна схема типів даних та структур у `libsolv`:

- **Об'єкт `Pool` (Пул пам'яті):** Центральний глобальний контекст системи. Він утримує таблицю інтернування рядків String Pool, глобальний масив усіх відомих пакунків `Solvable`, масиви підключених репозиторіїв та зведені таблиці зворотної відповідності залежностей `whatprovides`.
- **Об'єкт `Repo` (Репозиторій):** Контекст конкретного джерела пакунків (наприклад, локальний системний репозиторій вже встановлених пакунків `@system`, або мережеві репозиторії `fedora-base`, `updates`). Утримує список власних пакунків `Solvable`.
- **Структура `Solvable` (Пакунок):** Внутрішня C-структура, яка описує один бінарний пакунок (назву, версію, реліз, архітектуру, індекси масивів залежностей).
- **Об'єкт `Solver` (SAT-розв'язувач):** Екземпляр CDCL SAT-солвера, прив'язаний до об'єкта `Pool`. Він аналізує булеву матрицю, виконує поширення одиничних диз'юнктів та генерує підсумковий план дій.
- **Структура `Queue` (Черга):** Динамічний масив ідентифікаторів `Id`. Використовується для формування завдань користувача (наприклад, "встановити пакунок X") та зчитування результатів роботи солвера.
- **Об'єкт `Transaction` (Транзакція):** Сформований послідовний план операцій (встановлення, оновлення, видалення, перевстановлення), впорядкований з урахуванням топологічних залежностей файлової системи.
- **Тип `Id` (Числовий ідентифікатор):** 32-бітне ціле число зі знаком. Використовується як універсальний покажчик на рядок, пакунок або зв'язаний вираз залежності.

## 2. Внутрішня структура `Solvable` та збереження зв'язків

Кожен пакунок представлений внутрішньою C-структурою `Solvable`. Залежності не зберігаються у вигляді списків покажчиків чи динамічних зв'язаних списків; замість цього вони посилаються на індекси у глобальному масиві залежностей `pool->whatprovides_data`. Кожен список залежностей завершується спеціальним маркерним значенням `0`.

:::tabs
```c
typedef struct struct_Solvable {
    Id name;           // Id імені пакунка (наприклад, Id для "nginx")
    Id evr;            // Id версії (Epoch-Version-Release, наприклад, "1.20.1-1.el8")
    Id arch;           // Id архітектури (наприклад, "x86_64")
    Repo *repo;        // Покажчик на репозиторій, якому належить пакунок

    Id provides;       // Індекс початку масиву ідентифікаторів наданих послуг/імен
    Id requires;       // Індекс початку масиву необхідних залежностей (Depends)
    Id conflicts;      // Індекс початку масиву конфліктних вимог (Conflicts)
    Id obsoletes;      // Індекс початку масиву замінюваних пакунків (Replaces)
    Id recommends;     // Індекс початку масиву рекомендованих залежностей
    Id suggests;       // Індекс початку масиву пропонованих залежностей
    Id enhances;       // Індекс початку масиву розширювальних залежностей
    Id supplements;    // Індекс початку масиву зворотних рекомендацій
} Solvable;
```
```cpp
struct Solvable {
    Id name;           // Id імені пакунка (string pool index)
    Id evr;            // Id версії (string pool index)
    Id arch;           // Id архітектури (string pool index)
    Repo* repo;        // Покажчик на репозиторій-власник

    Id provides;       // Індекс масиву наданих можливостей у Pool
    Id requires;       // Індекс масиву необхідних залежностей у Pool
    Id conflicts;      // Індекс масиву конфліктних вимог у Pool
    Id obsoletes;      // Індекс масиву замінюваних пакунків у Pool
    Id recommends;     // Індекс масиву рекомендованих залежностей
    Id suggests;       // Індекс масиву пропонованих залежностей
    Id enhances;       // Індекс початку масиву розширень
    Id supplements;    // Індекс початку масиву зворотних рекомендацій
};
```
:::

Зв'язки типу "залежність від конкретної версії" (наприклад, `libssl >= 1.1`) кодуються за допомогою спеціальних складених ідентифікаторів (Relational IDs) через функцію `pool_rel2id()`. Функція приймає `Id` назви бібліотеки, `Id` рядка версії та прапор оператора порівняння (`REL_EQ` для `=`, `REL_GT` для `>`, `REL_GE` для `>=`, `REL_LT` для `<`, `REL_LE` для `<=`). Об'єднаний реляційний ідентифікатор зберігається у загальному String Pool так само, як і звичайні рядки.

## 3. Динамічний масив `Queue` та його механіка

Черга `Queue` є базовим контейнером передачі даних у бібліотеці `libsolv`. Вона реалізує динамічний масив ідентифікаторів `Id` з автоматичним перевиділенням пам'яті при перевищенні ємності.

:::tabs
```c
typedef struct struct_Queue {
    Id *elements;      // Покажчик на динамічний масив ідентифікаторів Id
    int count;         // Поточна кількість елементів у черзі
    int alloc;         // Ємність виділеного блоку пам'яті
} Queue;

void queue_init(Queue *q);
void queue_free(Queue *q);
void queue_push(Queue *q, Id id);
void queue_push2(Queue *q, Id id1, Id id2);
Id queue_pop(Queue *q);
void queue_empty(Queue *q);
```
```cpp
struct Queue {
    Id* elements;      // Покажчик на динамічний масив ідентифікаторів Id
    int count;         // Поточна кількість елементів у черзі
    int alloc;         // Ємність виділеного блоку пам'яті
};

extern "C" {
    void queue_init(Queue* q);
    void queue_free(Queue* q);
    void queue_push(Queue* q, Id id);
    void queue_push2(Queue* q, Id id1, Id id2);
    Id queue_pop(Queue* q);
    void queue_empty(Queue* q);
}
```
:::

Функція `queue_push2()` є найчастіше використовуваною при формуванні запитів до солвера, оскільки кожна вимога складається з пари цілих чисел: прапора дії та ідентифікатора пакунка.

## 4. Головний API керування пулом, репозиторіями та солвером

Процес роботи з бібліотекою `libsolv` підпорядковується чіткій послідовності кроків:
1. Ініціалізація глобального контексту `pool_create()`.
2. Реєстрація системного репозиторію вже встановлених пакунків `@system` за допомогою `pool_set_installed()`.
3. Завантаження та парсинг мережевих репозиторіїв через `repo_add_solvable()`.
4. Обов'язковий виклик `pool_createwhatprovides()` для побудови внутрішньої хеш-таблиці зворотного пошуку залежностей.
5. Формування черги завдань `Queue` та виклик `solver_solve()`.
6. Створення об'єкта транзакції `solver_create_transaction()` та виконання файлових операцій.

### 4.1. Створення пулу та додавання репозиторіїв

:::tabs
```c
// Створення нового центрального пулу пам'яті
Pool *pool_create(void);

// Звільнення пам'яті пулу та всіх пов'язаних репозиторіїв і пакунків
void pool_free(Pool *pool);

// Перетворення сирого рядка у 32-бітний Id (create = 1 створює новий Id, якщо його не було)
Id pool_str2id(Pool *pool, const char *str, int create);

// Отримання сирого текстового рядка за його Id
const char *pool_id2str(const Pool *pool, Id id);

// Створення об'єкта репозиторію у пулі
Repo *repo_create(Pool *pool, const char *name);

// Призначення репозиторію як системного (містить вже встановлені пакунки)
void pool_set_installed(Pool *pool, Repo *repo);

// Побудова внутрішньої хеш-таблиці зворотної відповідності залежностей
void pool_createwhatprovides(Pool *pool);
```
```cpp
extern "C" {
    Pool* pool_create(void);
    void pool_free(Pool* pool);
    Id pool_str2id(Pool* pool, const char* str, int create);
    const char* pool_id2str(const Pool* pool, Id id);
    Repo* repo_create(Pool* pool, const char* name);
    void pool_set_installed(Pool* pool, Repo* repo);
    void pool_createwhatprovides(Pool* pool);
}
```
:::

### 4.2. Створення та запуск SAT-солвера

:::tabs
```c
// Створення нового екземпляра солвера для вказаного пулу
Solver *solver_create(Pool *pool);

// Звільнення пам'яті екземпляра солвера
void solver_free(Solver *solv);

// Виконання процесу розв'язання залежностей
int solver_solve(Solver *solv, Queue *jobqueue);

// Створення об'єкта підсумкової транзакції
Transaction *solver_create_transaction(Solver *solv);

// Звільнення об'єкта транзакції
void transaction_free(Transaction *trans);
```
```cpp
extern "C" {
    Solver* solver_create(Pool* pool);
    void solver_free(Solver* solv);
    int solver_solve(Solver* solv, Queue* jobqueue);
    Transaction* solver_create_transaction(Solver* solv);
    void transaction_free(Transaction* trans);
}
```
:::

## 5. Прапорці завдань (Job Flags) та конфігураційні налаштування

При передачі завдань у `Queue jobqueue` для функції `solver_solve()` кожна вимога формується поєднанням бітових прапорів дій та прапорів масок типу об'єкта.

Опис прапорів операцій завдань:

- **`SOLVER_INSTALL`:** Вимога встановити вказаний пакунок `Solvable` або задовольнити вираз залежності `Provides`.
- **`SOLVER_ERASE`:** Вимога видалити вказаний пакунок із операційної системи.
- **`SOLVER_UPDATE`:** Вимога оновити пакунок до найновішої доступної сумісної версії.
- **`SOLVER_WEAK`:** Прапор модифікатор: позначає вимогу як слабку (необов'язкову). Застосовується для обробки рекомендованих пакунків `Recommends`.
- **`SOLVER_SOLVABLE`:** Прапор-маска: вказує солверу, що другий параметр у черзі є ідентифікатором конкретного пакунка `Solvable`.
- **`SOLVER_SOLVABLE_NAME`:** Прапор-маска: вказує солверу, що параметр є абстрактним ідентифікатором назви пакунка.
- **`SOLVER_SOLVABLE_PROVIDES`:** Прапор-маска: вказує солверу, що параметр є ідентифікатором віртуальної послуги `Provides`.
- **`SOLVER_FORCEBEST`:** Вимога вибирати тільки найвищу доступну версію пакунка, навіть якщо це призведе до видалення більшої кількості інших компонентів.

Конфігураційні прапорці солвера встановлюються за допомогою виклику `solver_set_flag(solv, FLAG, value)`:

- **`SOLVER_FLAG_ALLOW_DOWNGRADE`:** Дозволяє солверу пропонувати пониження версій (Downgrade) встановлених пакунків задля усунення конфліктів.
- **`SOLVER_FLAG_ALLOW_ARCHCHANGE`:** Дозволяє солверу змінювати архітектуру пакунків (наприклад, замінювати `i686` на `x86_64`).
- **`SOLVER_FLAG_ALLOW_VENDORCHANGE`:** Дозволяє заміну постачальника пакунків (наприклад, перехід пакунка з репозиторію `openSUSE` до `Packman`).
- **`SOLVER_FLAG_NO_AUTOLOCK`:** Вимикає автоматичне блокування встановлених пакунків від оновлення або видалення.

## 6. Діагностика проблем та аналіз Unsat Core

Якщо функція `solver_solve()` повертає значення `problems > 0`, сформована система булевих рівнянь є нездійсненною (Unsat). Для детальної діагностики та виведення причин відмови бібліотека надає спеціальний діагностичний API:

:::tabs
```c
// Отримання кількості виявлених конфліктних проблем
int count = solver_problem_count(solv);

// Отримання внутрішнього ідентифікатора конфліктного диз'юнкта
Id problem = 1;
Id rule_id = solver_findproblemrule(solv, problem);

// Отримання текстового опису причини конфлікту для користувача
const char *reason = solver_problemrule2str(solv, rule_id);
```
```cpp
extern "C" {
    int solver_problem_count(Solver* solv);
    Id solver_findproblemrule(Solver* solv, Id problem);
    const char* solver_problemrule2str(Solver* solv, Id rule_id);
}
```
:::

Функція `solver_problemrule2str()` повертає сформований рядок українською або англійською мовою (залежно від локалі), який детально пояснює причину суперечності, наприклад: `"package A-1.0.0 requires libfoo.so.1, but none of the providers can be installed"`.

## 7. Приклади використання мовами C та C++

Нижче наведено робочі приклади ініціалізації пулу, створення репозиторіїв, формування запиту на встановлення пакунка, запуску солвера та обробки результатів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <solv/pool.h>
#include <solv/repo.h>
#include <solv/solver.h>
#include <solv/selection.h>
#include <solv/transaction.h>

void run_c_libsolv_demo(void) {
    // 1. Створення центрального пулу
    Pool *pool = pool_create();
    if (!pool) {
        fprintf(stderr, "Помилка створення libsolv Pool\n");
        return;
    }

    // 2. Створення системного репозиторію (встановлені пакунки)
    Repo *installed_repo = repo_create(pool, "@system");
    pool_set_installed(pool, installed_repo);

    // 3. Створення мережевого репозиторію
    Repo *updates_repo = repo_create(pool, "updates");

    // 4. Додавання пакунка curl до мережевого репозиторію
    Id pkg_id = repo_add_solvable(updates_repo);
    Solvable *s = pool_id2solvable(pool, pkg_id);
    s->name = pool_str2id(pool, "curl", 1);
    s->evr = pool_str2id(pool, "7.76.1-1.el8", 1);
    s->arch = pool_str2id(pool, "x86_64", 1);

    // 5. Побудова індексу залежностей
    pool_createwhatprovides(pool);

    // 6. Формування черги завдань: встановити пакунок curl
    Queue job;
    queue_init(&job);
    queue_push2(&job, SOLVER_INSTALL | SOLVER_SOLVABLE, pkg_id);

    // 7. Створення та запуск SAT-солвера
    Solver *solver = solver_create(pool);
    int problems = solver_solve(solver, &job);

    if (problems == 0) {
        printf("[libsolv C] Транзакцію успішно розв'язано!\n");
        Transaction *trans = solver_create_transaction(solver);
        printf("  Кількість операцій у транзакції: %d\n", trans->steps.count);
        transaction_free(trans);
    } else {
        printf("[libsolv C] Знайдено %d конфліктів залежностей!\n", problems);
        for (int p = 1; p <= problems; p++) {
            Id rule = solver_findproblemrule(solver, p);
            printf("  Проблема #%d: %s\n", p, solver_problemrule2str(solver, rule));
        }
    }

    // 8. Звільнення ресурсів
    solver_free(solver);
    queue_free(&job);
    pool_free(pool);
}
```
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <string_view>
#include <stdexcept>

#include <solv/pool.h>
#include <solv/repo.h>
#include <solv/solver.h>
#include <solv/selection.h>
#include <solv/transaction.h>

// RAII обгортка для libsolv Pool
struct LibsolvPoolDeleter {
    void operator()(Pool* p) const noexcept {
        if (p) pool_free(p);
    }
};
using UniquePool = std::unique_ptr<Pool, LibsolvPoolDeleter>;

// RAII обгортка для libsolv Solver
struct LibsolvSolverDeleter {
    void operator()(Solver* s) const noexcept {
        if (s) solver_free(s);
    }
};
using UniqueSolver = std::unique_ptr<Solver, LibsolvSolverDeleter>;

// RAII обгортка для libsolv Transaction
struct LibsolvTransactionDeleter {
    void operator()(Transaction* t) const noexcept {
        if (t) transaction_free(t);
    }
};
using UniqueTransaction = std::unique_ptr<Transaction, LibsolvTransactionDeleter>;

// RAII обгортка для черги Queue
class SolvQueue {
public:
    SolvQueue() { queue_init(&q_); }
    ~SolvQueue() { queue_free(&q_); }

    SolvQueue(const SolvQueue&) = delete;
    SolvQueue& operator=(const SolvQueue&) = delete;

    void push(Id flag, Id id) {
        queue_push2(&q_, flag, id);
    }

    Queue* raw() noexcept { return &q_; }

private:
    Queue q_;
};

class PackageSolverEngine {
public:
    PackageSolverEngine() : pool_(pool_create()) {
        if (!pool_) {
            throw std::runtime_error("Не вдалося ініціалізувати libsolv Pool");
        }
    }

    void add_package(std::string_view repo_name, std::string_view pkg_name, std::string_view version, std::string_view arch) {
        Repo* repo = repo_create(pool_.get(), repo_name.data());
        Id id = repo_add_solvable(repo);
        
        Solvable* s = pool_id2solvable(pool_.get(), id);
        s->name = pool_str2id(pool_.get(), pkg_name.data(), 1);
        s->evr = pool_str2id(pool_.get(), version.data(), 1);
        s->arch = pool_str2id(pool_.get(), arch.data(), 1);
        
        last_pkg_id_ = id;
    }

    void solve_installation() {
        pool_createwhatprovides(pool_.get());

        SolvQueue queue;
        queue.push(SOLVER_INSTALL | SOLVER_SOLVABLE, last_pkg_id_);

        UniqueSolver solver(solver_create(pool_.get()));
        int problems = solver_solve(solver.get(), queue.raw());

        if (problems > 0) {
            std::cout << "[libsolv C++] Виявлено " << problems << " конфліктів у транзакції:\n";
            for (int p = 1; p <= problems; ++p) {
                Id rule = solver_findproblemrule(solver.get(), p);
                std::cout << "  - " << solver_problemrule2str(solver.get(), rule) << "\n";
            }
            throw std::runtime_error("Не вдалося розв'язати залежності транзакції");
        }

        UniqueTransaction trans(solver_create_transaction(solver.get()));
        std::cout << "[libsolv C++] Транзакція успішна! Кількість дій: " << trans->steps.count << "\n";
    }

private:
    UniquePool pool_;
    Id last_pkg_id_{0};
};
```
:::

## 8. Детальний покроковий аналіз виконання C та C++ прикладів

1. **Створення контексту `pool_create()`:** Обидва приклади спочатку створюють об'єкт `Pool`. У C++ версії використовується `std::unique_ptr` із власним видалячем `LibsolvPoolDeleter`, що забезпечує автоматичний виклик `pool_free()` при виході з області видимості та запобігає витоку пам'яті навіть при виникненні винятків `std::runtime_error`.
2. **Додавання репозиторіїв та пакунків:** За допомогою `repo_create()` створюється репозиторій `updates`. Виклик `repo_add_solvable()` виділяє новий запис у масиві `Solvable` і повертає його `Id`. Потім назва `"curl"`, версія `"7.76.1-1.el8"` та архітектура `"x86_64"` конвертуються в цілочисельні `Id` через `pool_str2id()`.
3. **Побудова індексу `pool_createwhatprovides()`:** Обов'язковий крок перед запуском розв'язання. `libsolv` сканує всі пакунки в усіх репозиторіях і будує зведену хеш-таблицю відповідності: для кожного `Id` назви чи віртуальної послуги зберігається список `Solvable`, які її надають.
4. **Формування черги запиту `Queue`:** За допомогою `queue_push2()` у чергу записується дія `SOLVER_INSTALL | SOLVER_SOLVABLE` та `Id` пакунка. У C++ версії клас `SolvQueue` обгортає низькорівневу структуру C і гарантує її очищення через `queue_free()` у деструкторі (RAII).
5. **Запуск розв'язувача `solver_solve()`:** Екземпляр `Solver` аналізує згенеровані булеві диз'юнкти. Якщо повернене значення дорівнює `0`, транзакція є здійсненною. Виклик `solver_create_transaction()` створює об'єкт `Transaction`, який містить впорядкований масив кроків встановлення. Якщо виникають конфлікти, цикл виводить людські описи причин через `solver_problemrule2str()`.
