# 📋 Інтерфейс бібліотеки: універсальний навігатор нескінченних дерев

Інтерфейс бібліотеки `tree_explorer` надає продуману програмну абстракцію для інспекції, навігації та пошуку в імпліцитних, нескінченних, але локально скінченних деревах станів. Головне завдання бібліотеки — надати розробнику високорівневий інструментарій, який унеможливлює потрапляння обходу у нескінченні гілки виконання, зберігаючи при цьому оптимальне використання обчислювальних ресурсів пам'яті та процесорного часу.

## 1. Контракт програмного середовища та концептуальна модель

У багатьох сучасних інженерних та дослідницьких завданнях — від автоматичного синтезу програм та символьного виконання коду до штучного інтелекту в іграх та формальної перевірки моделей (model checking) — простір станів не існує у вигляді попередньо згенерованої структури даних у пам'яті. Замість цього простір станів задається **імпліцитно** за допомогою динамічних правил переходу між конфігураціями.

Бібліотека `tree_explorer` впроваджує контракт взаємодії між ядром алгоритму обходу та доменною логікою користувача. Цей контракт базується на трьох фундаментальних стовпах:

1. **Гарантія локальної скінченності (Locally Finite Contract):**
   Доменна логіка користувача подається у вигляді функції генерації нащадків `get_children`. Контракт вимагає, щоб для будь-якого коректного стану `s` кількість згенерованих наступників `Children(s)` була строго скінченним числом `k < ∞`. Бібліотека спирається на цю властивість для забезпечення скінченності кожного рівня обходу.
2. **Абстракція стану та управління пам'яттю (Memory Ownership Model):**
   Стан вузла може бути як простим цілочисловим ідентифікатором, так і складним об'єктом, що містить повний зріз реєстрів та пам'яті віртуальної машини. Бібліотека C надає можливість передачі непрозорого вказівника `void*` з можливістю реєстрації кастомної функції звільнення ресурсів `free_state`. Модуль C++ використовує семантику переміщення (move semantics), концепти C++20 та розумні вказівники (`std::unique_ptr`), унеможливлюючи витоки пам'яті.
3. **Захист від нескінченних траєкторій (Strategy Guarantees):**
   Бібліотека підтримує дві стратегії обходу, кожна з яких має чітко визначені математичні гарантії:
   - **`TREE_STRATEGY_BFS` (Breadth-First Search):** Сканує дерево рівень за рівнем. За лемою Кеніґа кожен рівень локально скінченного дерева є скінченним. Це дає 100% гарантію знаходження будь-якого цільового стану, який розташований на скінченній глибині `d`, незалежно від наявності нескінченних гілок у сусідніх піддеревах.
   - **`TREE_STRATEGY_IDDFS` (Iterative Deepening DFS):** Виконує серію послідовних обходів у глибу з обмеженням граничної глибини `L = 0, 1, 2, ...`. Поєднує гарантію знаходження цілі від BFS із просторовою складністю DFS `O(d)` замість експоненційного споживання пам'яті.

## 2. Архітектурні паттерни та проектування інтерфейсу

При розробці бібліотеки `tree_explorer` було застосовано кілька ключових паттернів проектирування ПЗ:

### Паттерн «Стратегія» (Strategy Pattern)
Алгоритм обходу виділено в окремий обчислювальний модуль, який конфігурується при створенні об'єкта дослідника. Це дозволяє прозоро змінювати стратегію обходу з BFS на IDDFS без зміни коду генерації нащадків та коду перевірки цільових умов.

### Паттерн «Лінивий генератор» (Lazy Generator)
Нащадки кожного вузла не створюються заздалегідь для всього дерева. Вони виклично генеруються функцією `get_children` лише у той момент, коли алгоритм обходу дістається до відповідного батьківського вузла. Це забезпечує мінімальний розмір оперативної пам'яті під час дослідження нескінченних просторів станів.

### Паттерн «Абстракція контексту» (User Data Context)
У C-версії інтерфейсу всі функції зворотного виклику приймають вказівник `void* user_data`. Це дозволяє передавати в алгоритм додаткові параметри середовища — наприклад, таблиці символів, конфігуратори обчислень або хеш-таблиці відвіданих вершин — без використання глобальних змінних.

## 3. Детальний опис функціональних блоків C API

Системний інтерфейс мовою C розроблено з урахуванням суворої ABI-стабільності. Нижче наведено детальний опис кожної функції та структури даних.

### Перелічувальний тип `tree_error_t`
Задає коди повернутих значень для всіх операцій бібліотеки:
- `TREE_SUCCESS (0)` — пошук завершився успішно, знайдено стан, що задовольняє предикату `is_goal`.
- `TREE_ERROR_NULL_POINTER (-1)` — один із обов'язкових аргументів (наприклад, конфігурація або функція генерації) дорівнює `NULL`.
- `TREE_ERROR_OUT_OF_MEMORY (-2)` — системний виклики `malloc` повернув `NULL` під час розширення черги.
- `TREE_ERROR_MAX_VISITED_EXCEEDED (-3)` — алгоритм досяг встановленого ліміту `max_visited_nodes`, але не знайшов цільовий стан.
- `TREE_ERROR_MAX_DEPTH_EXCEEDED (-4)` — обхід досяг граничної глибини `max_depth` у стратегії IDDFS.
- `TREE_ERROR_TARGET_NOT_FOUND (-5)` — дерево виявилося скінченним і було обійдено повністю без виявлення цільового стану.

### Структура конфігурації `tree_config_t`
Містить керуючі параметри для налаштування сесії пошуку:
- `strategy` — обирає між `TREE_STRATEGY_BFS` та `TREE_STRATEGY_IDDFS`.
- `max_visited_nodes` — ліміт кількості вершин для запобігання зацикленню та вичерпанню ресурсів.
- `max_depth` — гранична глибина обходу для IDDFS.
- `max_branching_factor` — оціночний максимум нащадків для попереднього виділення буферів.
- `user_data` — вказівник на довільний контекст користувача.

## 4. Проектні принципи та архітектура викликів у C та C++

Під час проектирування бібліотеки `tree_explorer` особлива увага приділялася накладним витратам при викликах функції генерації нащадків. Оскільки у великих просторах станів кількість викликів `get_children` може досягати мільйонів на секунду, механізм диспетчеризації повинен бути максимально швидким.

### Диспетчеризація у мові C та C++

:::tabs
```c
/* Користувач заповнює готовий буфер без динамічного виділення пам'яті */
size_t my_get_children(tree_state_t state, tree_state_t* out_children, size_t max_children, void* user_data) {
    /* Прямий запис у виділений масив out_children */
    out_children[0] = child1;
    out_children[1] = child2;
    return 2; /* повернути реальну кількість нащадків */
}
```
```cpp
// Ідіоматична C++20 генерація нащадків через RAII-вектор
std::vector<MyState> MyState::get_children() const {
    return { child1, child2 };
}
```
:::

### Мономорфізація шаблонів у C++20
У C++20 застосовано концепт `LocallyFiniteState`, який дозволяє компілятору виконувати **мономорфізацію** (template monomorphization) та повне вбудовування коду (inlining) методів `get_children()` та `is_goal()`. На відміну від класичних віртуальних функцій (virtual functions), шаблони C++20 не потребують таблиці віртуальних методів (vtable), що повністю усуває накладні витрати на непрямі виклики і дозволяє векторну оптимізацію на рівні SIMD-інструкцій процесора.

## 5. Повна специфікація API мовами C та C++

:::tabs
```c
/**
 * @file tree_explorer.h
 * @brief Повний системний інтерфейс C для навігації в локально скінченних нескінченних деревах.
 */

#ifndef TREE_EXPLORER_H
#define TREE_EXPLORER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    TREE_SUCCESS = 0,
    TREE_ERROR_NULL_POINTER = -1,
    TREE_ERROR_OUT_OF_MEMORY = -2,
    TREE_ERROR_MAX_VISITED_EXCEEDED = -3,
    TREE_ERROR_MAX_DEPTH_EXCEEDED = -4,
    TREE_ERROR_TARGET_NOT_FOUND = -5
} tree_error_t;

typedef enum {
    TREE_STRATEGY_BFS = 0,
    TREE_STRATEGY_IDDFS = 1
} tree_strategy_t;

typedef void* tree_state_t;

typedef size_t (*tree_get_children_fn)(tree_state_t state, 
                                       tree_state_t* out_children, 
                                       size_t max_children, 
                                       void* user_data);

typedef bool (*tree_is_goal_fn)(tree_state_t state, void* user_data);

typedef void (*tree_free_state_fn)(tree_state_t state, void* user_data);

typedef struct {
    tree_strategy_t strategy;
    size_t max_visited_nodes;
    size_t max_depth;
    size_t max_branching_factor;
    void* user_data;
} tree_config_t;

typedef struct tree_explorer tree_explorer_t;

tree_explorer_t* tree_explorer_create(const tree_config_t* config,
                                      tree_get_children_fn get_children,
                                      tree_is_goal_fn is_goal,
                                      tree_free_state_fn free_state);

tree_error_t tree_explorer_search(tree_explorer_t* explorer,
                                  tree_state_t root_state,
                                  tree_state_t* out_found_state);

void tree_explorer_get_stats(const tree_explorer_t* explorer,
                             size_t* out_visited_count,
                             size_t* out_max_depth_reached);

void tree_explorer_destroy(tree_explorer_t* explorer);

#ifdef __cplusplus
}
#endif

#endif /* TREE_EXPLORER_H */
```
```cpp
/**
 * @file TreeExplorer.hpp
 * @brief Об'єктно-орієнтований C++20 шаблонний API для безпечної навігації в нескінченних деревах.
 */

#ifndef TREE_EXPLORER_HPP
#define TREE_EXPLORER_HPP

#include <concepts>
#include <vector>
#include <queue>
#include <optional>
#include <expected>
#include <functional>
#include <memory>
#include <algorithm>

namespace tree_analysis {

template<typename T>
concept LocallyFiniteState = requires(const T& node) {
    { node.get_children() } -> std::same_as<std::vector<T>>;
    { node.is_goal() } -> std::same_as<bool>;
};

enum class SearchStatus {
    TargetFound,
    TargetNotFound,
    MaxVisitedExceeded,
    MaxDepthExceeded
};

struct SearchStats {
    size_t visited_nodes{0};
    size_t max_depth_reached{0};
};

template<LocallyFiniteState StateType>
class TreeExplorer {
public:
    enum class Strategy {
        BFS,
        IDDFS
    };

    struct Options {
        Strategy strategy{Strategy::BFS};
        size_t max_visited{100000};
        size_t max_depth{1000};
    };

    explicit TreeExplorer(Options options = {}) : options_(options) {}

    [[nodiscard]] std::expected<StateType, SearchStatus> search(const StateType& root) {
        stats_ = {};
        if (options_.strategy == Strategy::BFS) {
            return search_bfs(root);
        } else {
            return search_iddfs(root);
        }
    }

    [[nodiscard]] const SearchStats& stats() const noexcept {
        return stats_;
    }

private:
    Options options_;
    SearchStats stats_;

    std::expected<StateType, SearchStatus> search_bfs(const StateType& root) {
        std::queue<std::pair<StateType, size_t>> q;
        q.push({root, 0});

        while (!q.empty()) {
            if (stats_.visited_nodes >= options_.max_visited) {
                return std::unexpected(SearchStatus::MaxVisitedExceeded);
            }

            auto [current, depth] = q.front();
            q.pop();
            stats_.visited_nodes++;
            stats_.max_depth_reached = std::max(stats_.max_depth_reached, depth);

            if (current.is_goal()) {
                return current;
            }

            if (depth < options_.max_depth) {
                for (auto&& child : current.get_children()) {
                    q.push({std::move(child), depth + 1});
                }
            }
        }
        return std::unexpected(SearchStatus::TargetNotFound);
    }

    std::expected<StateType, SearchStatus> search_iddfs(const StateType& root) {
        for (size_t limit = 0; limit <= options_.max_depth; ++limit) {
            auto res = dfs_bounded(root, 0, limit);
            if (res.has_value()) return res;
            if (stats_.visited_nodes >= options_.max_visited) {
                return std::unexpected(SearchStatus::MaxVisitedExceeded);
            }
        }
        return std::unexpected(SearchStatus::TargetNotFound);
    }

    std::optional<StateType> dfs_bounded(const StateType& current, size_t depth, size_t limit) {
        stats_.visited_nodes++;
        stats_.max_depth_reached = std::max(stats_.max_depth_reached, depth);

        if (current.is_goal()) return current;

        if (depth < limit) {
            for (const auto& child : current.get_children()) {
                auto res = dfs_bounded(child, depth + 1, limit);
                if (res.has_value()) return res;
            }
        }
        return std::nullopt;
    }
};

} // namespace tree_analysis

#endif // TREE_EXPLORER_HPP
```
:::

## 6. Порівняльний аналіз стратегій BFS та IDDFS у виробничих умовах

Під час вибору між `TREE_STRATEGY_BFS` та `TREE_STRATEGY_IDDFS` у реальних системах автоматичного аналізу розробнику слід спиратися на характеристики простору станів:

1. **Коли обирати BFS (`TREE_STRATEGY_BFS`):**
   - Коли знаходження **найкоротшого шляху** (найменшої глибини `d*`) є критично важливим.
   - Коли коефіцієнт розгалуження `k` є відносно невеликим (`k ≤ 4`), а оперативна пам'ять дозволяє утримувати чергу розміром до кількох мільйонів елементів.
   - Коли створення станів є дуже «дорогим» обчислювально, і повторне розгортання верхніх рівнів у IDDFS створить небажане навантаження на CPU.

2. **Коли обирати IDDFS (`TREE_STRATEGY_IDDFS`):**
   - Коли фактор розгалуження `k` є великим (`k ≥ 10`), і черга BFS швидко викликає переповнення оперативної пам'яті (`TREE_ERROR_OUT_OF_MEMORY`).
   - Коли обчислення виконуються в обмеженому середовищі (embedded systems, драйвери ядра, автономні контролери).
   - Коли цільовий стан розташований на значній глибині `d* > 50`, що робить тримання фронту BFS неможливим.

## 7. Механізм трасування шляху від цілі до кореня (Path Reconstruction)

Знаходження цільового стану є першою частиною завдання. Для верифікації коду чи формування контрприкладу (counterexample trace) розробнику необхідно відновити повну послідовність кроків від кореня `r` до цілі `Goal`.

### Відновлення шляху у C API
Для відновлення шляху структура вузла може містити вказівник на батьківський стан `parent_state`. Бібліотека надає функцію `tree_explorer_reconstruct_path`, яка ітерується від знайденої цілі до кореня і повертає динамічний масив `tree_path_t`:
- Шлях будується у зворотному порядку від цілі до кореня за час `O(d*)`.
- Після побудови масив розвертається в прямому порядку `r -> v₁ -> ... -> Goal`.

### Відновлення шляху у C++20 API
У C++20 для відновлення шляху використовується згортка типів через `std::vector<StateType>`. Завдяки семантиці переміщення, формування вектора траєкторії не здійснює глибокого копіювання об'єктів станів, забезпечуючи високу швидкість побудови контрприкладів у символьних аналізаторах.

## 8. Інтеграція з SMT-вирішувачами та SAT-двигунами

У сучасних автоматичних доводчиках теорем (наприклад, Z3 або CVC5) бінарні та n-арні дерева оцінок утворюють основу процедури DPLL(T).

Бібліотека `tree_explorer` слугує високорівневим каркасом для керування пошуком у просторі часткових моделей:
- Кожен вузол дерева відповідає частковому підстановці значень змінних.
- Функція `get_children` здійснює розгалуження за конфліктними змінними (decision variables).
- Перевірка `is_goal` викликає модуль SMT-перевірки сумісності теорій.
- Завдяки гарантії леми Кеніґа, якщо система формул є несуперечливою, BFS обхід `tree_explorer` гарантовано знаходить модель за скінченне число кроків.

## 9. Оптимізація локальності даних та паралельний обхід (Cache-Friendly Parallel Search)

У високопродуктивних системах перевірки моделей ключовим вузьким місцем стає локальність даних у CPU-кеші (L1/L2 data cache locality).

1. **Арена-алокація (Arena Allocation):** Для зменшення фрагментації пам'яті бібліотека дозволяє зареєструвати власний арена-алокатор для об'єктів черги `QueueItem`. Виділення вузлів у суцільному блоці пам'яті збільшує частоту влучань у кеш (cache line hits) під час сканування рівня.
2. **Паралельний BFS (Work-Stealing Concurrent Search):** При використанні багатьох ядер CPU черга фронту BFS ділиться на смуги (strides). Кожне ядро обробляє свою частину фронту, а в разі завершення роботи «викрадає» піддерева з черги сусіднього ядра (work-stealing queue pattern). Оскільки лема Кеніґа гарантує скінченність кожного рівня, глобальний бар'єр синхронізації між рівнями залишається детермінованим.

## 10. Порівняльний аналіз винятків та std::expected у C++20

У високопродуктивному коді аналізаторів мовою C++ використання класичних механізмів винятків (`try/catch` / `throw`) створює накладні витрати на таблиці розгортання стека (unwind tables) та непередбачувані затримки при обробці витоків пам'яті.

Використання нового стандарту `std::expected<StateType, SearchStatus>` у C++20 дозволяє виразити результат обходу без викликів RTTI та винятків:
- Функція повертає об'єкт-обгортку, який або містить результат `StateType`, або код помилки `SearchStatus`.
- Компілятор здатний згенерувати оптимальний машинний код із застосуванням умовних переходів `test/jmp` на рівні асемблера.
- Це критично важливо під час збірки аналізаторів коду з прапорцем `-fno-exceptions` у системному програмуванні ядра ОС.

## 11. Конфігуратор логування та трасування кроків (Tracing Layer)

Для відлагодження складних символьних аналізаторів бібліотека надає вбудований механізм логування траєкторій обходу `tree_explorer_set_tracer`:
- Користувач реєструє функцію зворотного виклику `tree_trace_fn`, яка приймає поточну глибину `depth`, ідентифікатор вузла та статус обробки (`VISITED`, `DISCARDED`, `EXPANDED`).
- Трасувальний шар працює в умовному режимі компіляції (`#ifdef TREE_ENABLE_TRACING`), що дозволяє повністю відключати накладні витрати на логування у випускних (Release) збірках проекту.

## 12. Керування пам'яттю та гарантії ABI для статичної лінковки

При використанні C API у крос-платформних системах (Windows DLL, Linux SO, macOS dylib) особлива увага приділяється гарантіям сумісності binary ABI:
- Усі структури даних на кшталт `tree_config_t` мають чітко визначене вирівнювання полів (explicit struct alignment / packing).
- Функція `tree_explorer_destroy` гарантує безпечне звільнення системних ресурсів, навіть якщо модулі розширення було завантажено динамічно через `dlopen` або `LoadLibrary`.

## 13. Інтеграція у будівельні системи CMake та Bazel

Для підключення C++20 версії `tree_explorer` у проекти на CMake достатньо оголосити header-only ціль:
```cmake
add_library(tree_explorer INTERFACE)
target_include_directories(tree_explorer INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(tree_explorer INTERFACE cxx_std_20)
```
Це забезпечує нульові накладні витрати під час збірки та миттєве затягування концептів `LocallyFiniteState` у систему стабільного аналізу.

Крім того, при використанні системи Bazel додається правило `cc_library` з включенням коду у власну систему збірки через `hdrs = ["TreeExplorer.hpp"]` та прапорець `--cxxopt='-std=c++20'`. Завдяки модульності структури заголовкових файлів бібліотека легко інтегрується у CI/CD контейнери верифікації автоматизованого аналізу просторів станів складних програмних комплексів та моделей штучного інтелекту.

## 14. Обробка крайових випадків та ресурсної безпеки

Під час розробки високонавантажених аналізаторів на основі `tree_explorer` розробнику слід зважати на кілька практичних та інженерних вимог:

### Запобігання витокам пам'яті при аварійному зупиненні
При використанні C API у випадку досягнення ліміту відвіданих вершин `max_visited_nodes`, у внутрішній черзі обходу BFS можуть залишатися сотні або тисячі нерозгорнутих станів `tree_state_t`. Функція `tree_explorer_destroy` автоматично ітерується по всіх елементах черги, що залишилися, та викликає для кожного з них зареєстровану функцію `free_state`. Це повністю усуває загрозу витоків динамічної пам'яті.

Крім того, при роботі з глибокими деревами станів автоматичне очищення черги гарантує відсутність висячих вказівників (dangling pointers) та запобігає фрагментації купи (heap fragmentation).

### Багатопотокова безпека (Thread Safety)
Об'єкт `tree_explorer_t` та клас `TreeExplorer` не є внутрішньо синхронізованими для паралельного виклику методу `search` з кількох потоків над одним і тим самим об'єктом. Для паралельного дослідження різних піддерев рекомендується створювати окремий екземпляр дослідника у кожному робочому потоці (thread-local instance).

### Робота з графами загального вигляду (Graph Unrolling)
Якщо простір станів містить цикли або кратні шляхи до одного й того самого стану, імпліцитний розгорт перетворює його на нескінченне дерево (unrolling tree). За наявності циклів для оптимізації пам'яті рекомендується зберігати зліченну хеш-таблицю відвіданих станів `visited_set`. Якщо стан вже присутній у хеш-таблиці, функція `get_children` повинна повертати порожній масив, що ефективно зрізає цикли та підтримує локальну скінченність.

## 15. Зведена таблиця характеристик методів та параметрів API

| Параметр / Метод | Тип у C | Тип у C++ | Опис та математичні гарантії |
| :--- | :--- | :--- | :--- |
| `strategy` | `tree_strategy_t` | `TreeExplorer::Strategy` | Обрана стратегія пошуку. `BFS` забезпечує 100% покриття рівня за лемою Кеніґа; `IDDFS` зменшує витрати пам'яті до `O(d)`. |
| `max_visited_nodes` | `size_t` | `size_t` | Верхня межа оброблених вершин для захисту від нескінченного зациклення під час роботи з нескінченними деревами. |
| `get_children` | `tree_get_children_fn` | `T::get_children()` | Доменна функція генерування нащадків. Повинна задовольняти вимогу локальної скінченності (`k < ∞`). |
| `is_goal` | `tree_is_goal_fn` | `T::is_goal()` | Предикат перевірки виконання цільової умови на поточному стані. |
| `search()` | `tree_explorer_search()` | `TreeExplorer::search()` | Запускає процес дослідження простору станів. Повертає знайдений стан або відповідний статус завершення. |
| `stats()` | `tree_explorer_get_stats()`| `TreeExplorer::stats()` | Отримання статистики обходу: підрахована кількість перевірених вузлів та максимальна глибина розгортання. |
