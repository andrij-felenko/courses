# ⚙️ Реалізація рушія санків та редукції графів у пам'яті

Щоб зрозуміти, як виклик за потребою (Call-by-Need) працює на рівні кремнію та байтів, недостатньо читати декларативні формули. Потрібно власноруч побудувати мінімальний, але функціонально повний рантайм: структуру санка в купі, скінченний автомат переходів станів із виявленням нескінченних циклів (Blackholing), мутацію вузлів графа на місці та нескінченні ліниві потоки (Lazy Streams).

### Задача та архітектура рушія

Наше завдання — побудувати обчислювальний рушій, який задовольняє чотири вимоги:
1. **Лінивість (Delayed Execution):** значення не обчислюється, доки його явно не форсують через функцію `force`.
2. **Мемоізація та редукція графа (Sharing):** результат обчислюється рівно один раз. Повторне читання того самого санка різними функціями не виконує жодного рядка коду й коштує лише одне пряме читання поля структури.
3. **Захист від зациклень (Blackholing):** якщо обчислення санка рекурсивно залежить від самого себе без бази (прямий цикл `x = x + 1`), рушій повинен не завішувати програму, а миттєво діагностувати цикл `⊥`.
4. **Нескінченні структури (Infinite Streams):** можливість побудувати потік чисел Фібоначчі чи простих чисел, з якого клієнт бере рівно перші `N` елементів без виділення зайвої пам'яті.

### Механіка станів та організація пам'яті

У строгих мовах аргумент передається як готове значення: 64-бітне число лежить у регістрі процесора або у стековому кадрі. У лінивому середовищі кожен вираз, який ще не було обчислено, мусить існувати як самодостатній об'єкт першого класу на [купі](topic:sf-lang/heap-dynamic-memory).

Санк у пам'яті — це поліморфний контейнер із мутабельним станом. Він об'єднує два взаємовиключні режими життя:
- **До форсування:** містить вказівник на скомпільовану функцію (`ComputeFn`) та покажчик на виділений блок пам'яті із захопленими вільними змінними (оточення замикання).
- **Після форсування:** вихідне замикання знищується, пам'ять оточення негайно звільняється, а тіло санка мутує, вміщуючи вже готове обчислене значення.

Перехід між цими режимами здійснюється через проміжний стан **Blackhole**. Він виконує роль апаратного запобіжника: щойно потік виконання починає обчислювати тіло санка, він стирає адресу функції обчислення й записує маркер активного виконання. Якщо під час обчислення програма випадково звернеться до цього ж санка ще раз (пряма циклічна залежність без розриву рекурсії), рушій не зациклиться на віки, а негайно перехопить спробу повторного входу й викине керовану помилку `<<loop>>`.

### Повна реалізація мовами C та C++

Нижче наведено повний робочий рушій двома мовами: мовою C з ручним керуванням пам'яттю оточення через лічильники посилань та мовою C++ з використанням шаблонних замикань, розумних покажчиків і безпечної системи типів `std::variant`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Стани життєвого циклу санка
typedef enum {
    THUNK_UNTOUCHED,   // Необчислений: містить функцію та оточення
    THUNK_EVALUATING,  // Blackhole: обчислюється прямо зараз (захист від циклів)
    THUNK_EVALUATED    // Обчислений: вузол мутовано, містить готове значення
} ThunkState;

typedef struct Thunk Thunk;

// Сигнатура функції обчислення: приймає вказівник на оточення, повертає ціле число
typedef long long (*ComputeFn)(void *env);
typedef void (*FreeEnvFn)(void *env);

struct Thunk {
    ThunkState state;
    union {
        struct {
            ComputeFn fn;
            void *env;
            FreeEnvFn free_env;
        } unevaluated;
        long long value;
    } data;
    size_t ref_count; // Лічильник посилань для спільного володіння
};

// Створення нового санка
Thunk* thunk_create(ComputeFn fn, void *env, FreeEnvFn free_env) {
    Thunk *t = (Thunk*)malloc(sizeof(Thunk));
    if (!t) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    t->state = THUNK_UNTOUCHED;
    t->data.unevaluated.fn = fn;
    t->data.unevaluated.env = env;
    t->data.unevaluated.free_env = free_env;
    t->ref_count = 1;
    return t;
}

// Створення вже готового значення (оптимізація для констант)
Thunk* thunk_value(long long val) {
    Thunk *t = (Thunk*)malloc(sizeof(Thunk));
    if (!t) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    t->state = THUNK_EVALUATED;
    t->data.value = val;
    t->ref_count = 1;
    return t;
}

// Форсування санка (Force / Eval)
long long thunk_force(Thunk *t) {
    if (!t) return 0;

    // Швидкий шлях: значення вже готове (O(1) читання з пам'яті)
    if (t->state == THUNK_EVALUATED) {
        return t->data.value;
    }

    // Захист від зациклення: якщо ми зайшли в той самий санк двічі
    if (t->state == THUNK_EVALUATING) {
        fprintf(stderr, "[Runtime Error] <<loop>>: виявлено пряму циклічну залежність санка!\n");
        exit(EXIT_FAILURE);
    }

    // Перехід у стан Blackhole
    t->state = THUNK_EVALUATING;
    ComputeFn fn = t->data.unevaluated.fn;
    void *env = t->data.unevaluated.env;
    FreeEnvFn free_env = t->data.unevaluated.free_env;

    // Виконання обчислення
    long long res = fn(env);

    // Звільнення захопленого оточення (GC promptness)
    if (free_env && env) {
        free_env(env);
    }

    // Мутація вузла графа на місці (Update)
    t->state = THUNK_EVALUATED;
    t->data.value = res;

    return res;
}

Thunk* thunk_retain(Thunk *t) {
    if (t) t->ref_count++;
    return t;
}

void thunk_release(Thunk *t) {
    if (!t) return;
    if (--t->ref_count == 0) {
        if (t->state == THUNK_UNTOUCHED && t->data.unevaluated.free_env && t->data.unevaluated.env) {
            t->data.unevaluated.free_env(t->data.unevaluated.env);
        }
        free(t);
    }
}

// --- Лінивий нескінченний потік (Lazy Stream) ---
typedef struct StreamNode StreamNode;

struct StreamNode {
    long long head;
    Thunk *tail_thunk; // Санк, що повертає наступний (StreamNode*)
};

typedef struct {
    long long a;
    long long b;
} FibEnv;

long long fib_stream_compute(void *env_ptr);

Thunk* make_fib_thunk(long long a, long long b) {
    FibEnv *env = (FibEnv*)malloc(sizeof(FibEnv));
    env->a = a;
    env->b = b;
    return thunk_create(fib_stream_compute, env, free);
}

static size_t g_eval_count = 0;

long long fib_stream_compute(void *env_ptr) {
    g_eval_count++;
    FibEnv *env = (FibEnv*)env_ptr;
    long long current = env->a;
    long long next = env->b;

    StreamNode *node = (StreamNode*)malloc(sizeof(StreamNode));
    node->head = current;
    node->tail_thunk = make_fib_thunk(next, current + next);

    // Повертаємо адресу вузла у вигляді цілого числа (вказівник)
    return (long long)node;
}

// Взяття перших N елементів зі списку
void stream_take(Thunk *stream_thunk, size_t n) {
    Thunk *curr_thunk = thunk_retain(stream_thunk);
    printf("Перші %zu чисел Фібоначчі: [", n);

    for (size_t i = 0; i < n; i++) {
        StreamNode *node = (StreamNode*)thunk_force(curr_thunk);
        printf("%lld%s", node->head, (i + 1 < n) ? ", " : "");

        Thunk *next_thunk = thunk_retain(node->tail_thunk);
        thunk_release(curr_thunk);
        curr_thunk = next_thunk;
    }
    printf("]\n");
    thunk_release(curr_thunk);
}

int main(void) {
    printf("=== Демонстрація рушія санків на C ===\n");

    // 1. Створення нескінченного потоку Фібоначчі: fib(0, 1)
    Thunk *fibs = make_fib_thunk(0, 1);

    // 2. Беремо перші 10 елементів
    stream_take(fibs, 10);
    printf("Кількість реальних обчислень вузлів: %zu (точно 10)\n", g_eval_count);

    // 3. Беремо перші 5 елементів з ТОГО САМОГО потоку (перевірка мемоізації)
    size_t prev_evals = g_eval_count;
    stream_take(fibs, 5);
    printf("Нових обчислень для перших 5 вузлів: %zu (всі взяті з кешу!)\n", g_eval_count - prev_evals);

    thunk_release(fibs);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <functional>
#include <stdexcept>
#include <variant>

// Виняток для детекції нескінченних циклів
class BottomLoopException : public std::runtime_error {
public:
    BottomLoopException() : std::runtime_error("<<loop>>: виявлено пряму циклічну залежність санка!") {}
};

// Узагальнений клас санка
template <typename T>
class Thunk : public std::enable_shared_from_this<Thunk<T>> {
private:
    struct Blackhole {};
    using State = std::variant<std::function<T()>, Blackhole, T>;
    mutable State state_;

public:
    // Конструктор від відкладеного обчислення (лямбди)
    explicit Thunk(std::function<T()> compute_fn)
        : state_(std::move(compute_fn)) {}

    // Конструктор від уже готового значення
    explicit Thunk(T val)
        : state_(std::move(val)) {}

    // Фабричні методи
    static std::shared_ptr<Thunk<T>> delay(std::function<T()> fn) {
        return std::make_shared<Thunk<T>>(std::move(fn));
    }

    static std::shared_ptr<Thunk<T>> value(T val) {
        return std::make_shared<Thunk<T>>(std::move(val));
    }

    // Форсування санка
    const T& force() const {
        if (std::holds_alternative<T>(state_)) {
            return std::get<T>(state_);
        }

        if (std::holds_alternative<Blackhole>(state_)) {
            throw BottomLoopException();
        }

        // Перехід у стан Blackhole
        auto compute_fn = std::move(std::get<std::function<T()>>(state_));
        state_ = Blackhole{};

        // Виконання обчислення та мутація вузла на місці
        T result = compute_fn();
        state_ = std::move(result);

        return std::get<T>(state_);
    }

    bool is_evaluated() const noexcept {
        return std::holds_alternative<T>(state_);
    }
};

// Допоміжний синтаксис
template <typename T>
const T& force(const std::shared_ptr<Thunk<T>>& thunk) {
    return thunk->force();
}

// --- Лінивий нескінченний потік мовою C++ ---
template <typename T>
struct StreamNode {
    T head;
    std::shared_ptr<Thunk<StreamNode<T>>> tail;
};

template <typename T>
using LazyStream = std::shared_ptr<Thunk<StreamNode<T>>>;

static size_t g_cpp_eval_count = 0;

// Генератор чисел Фібоначчі
LazyStream<long long> make_fib_stream(long long a = 0, long long b = 1) {
    return Thunk<StreamNode<long long>>::delay([a, b]() {
        g_cpp_eval_count++;
        return StreamNode<long long>{
            a,
            make_fib_stream(b, a + b)
        };
    });
}

// Друк перших N елементів
template <typename T>
void print_take(LazyStream<T> stream, size_t n) {
    std::cout << "Перші " << n << " елементів: [";
    auto current = stream;
    for (size_t i = 0; i < n; ++i) {
        const auto& node = force(current);
        std::cout << node.head << (i + 1 < n ? ", " : "");
        current = node.tail;
    }
    std::cout << "]\n";
}

int main() {
    std::cout << "=== Демонстрація рушія санків на C++ ===\n";

    // 1. Створюємо нескінченний потік
    auto fibs = make_fib_stream(0, 1);

    // 2. Беремо 10 чисел
    print_take(fibs, 10);
    std::cout << "Кількість викликів лямбди: " << g_cpp_eval_count << " (точно 10)\n";

    // 3. Перевірка кешування: беремо 5 чисел з того самого об'єкта
    size_t prev = g_cpp_eval_count;
    print_take(fibs, 5);
    std::cout << "Нових обчислень для перших 5 чисел: " << (g_cpp_eval_count - prev) << " (0 нових!)\n";

    // 4. Демонстрація перехоплення Blackhole при зацикленні: let x = x + 1
    std::shared_ptr<Thunk<int>> cyclic_thunk;
    cyclic_thunk = Thunk<int>::delay([&cyclic_thunk]() {
        return cyclic_thunk->force() + 1;
    });

    try {
        std::cout << "Спроба форсувати циклічний санк: ";
        cyclic_thunk->force();
    } catch (const BottomLoopException& e) {
        std::cout << "УСПІШНО ПЕРЕХОПЛЕНО -> " << e.what() << "\n";
    }

    return 0;
}
```
:::

### Детальний розбір механізмів, пасток та ціни абстракцій

Розгляньмо ключові інженерні висновки, які випливають із наведеного коду:

#### 1. Мутація вузла та спільне володіння (Sharing)
У методі `force()` найважливішим рядком є перехід `state_ = std::move(result)`.
До моменту виклику поле `state_` зберігало функціональний об'єкт `std::function`, який тримав у собі динамічно виділені вказівники на захоплене оточення. Після обчислення замикання руйнується, а у варіант записується чисте значення типу `T`.
Оскільки на об'єкт `Thunk` вказують кілька розумних покажчиків `std::shared_ptr` (або `ref_count` у версії на C), усі інші гілки графа миттєво отримують доступ до вже збереженого значення. Другий виклик `print_take(fibs, 5)` показує рівно 0 нових викликів функції: граф уже згорнуто до констант.

#### 2. Запобігання зацикленням через стан Blackhole
У тестовому блоці номер 4 ми навмисно створили циклічний санк `cyclic_thunk`, чиє тіло намагається прочитати саме себе (`cyclic_thunk->force() + 1`).
Без механізму Blackhole функція `force()` викликала б `compute_fn()`, та знову викликала б `force()`, і програма миттєво вичерпала б стек викликів процесора, завершившись аварійним падінням (Segmentation Fault) без жодного діагностичного сліду.
Встановлення стану `Blackhole` перед запуском замикання перетворює неконтрольовану аварію на коректно перехоплюваний виняток `BottomLoopException` за `O(1)` часу.

#### 3. Своєчасне звільнення захоплених ресурсів (GC Promptness)
Один із найпідступніших багів у лінивих середовищах — утримання пам'яті через старі замикання. Якщо санк захоплює тимчасовий буфер на 100 МБ, щоб витягнути з нього одне 4-байтне число, буфер зобов'язаний бути звільнений **у ту саму мить, коли число обчислено**.
У нашій реалізації на C функція `thunk_force` викликає `free_env(env)` перед тим, як записати `value` і змінити стан на `THUNK_EVALUATED`. У версії на C++ виклик `std::move(compute_fn)` перед запуском очищає внутрішній стан поля `state_`, відпускаючи захоплені ресурси ще до того, як результат буде повернуто споживачеві.

#### 4. Накладні витрати лінивості проти строгого коду
Ця реалізація наочно демонструє ціну лінивих обчислень у реальному кремнії:
- **Пам'ять:** на кожне числове значення створюється структура санка з лічильником посилань, станом та варіантом (24–48 байтів на одне 8-байтне число).
- **Непрямі виклики:** перший виклик вимагає стрибка за вказівником на функцію, що збиває передбачувач переходів процесора (branch predictor).
- **Кеш процесора:** вузли нескінченного списку розкидані по купі через `malloc`, що погіршує локальність даних порівняно зі звичайним масивом `std::vector`.

Саме тому промислові компілятори лінивих мов (зокрема GHC) виконують глибокий статичний аналіз строгості (strictness analysis), щоб автоматично розгортати санки у звичайні строгі регістрові операції скрізь, де лінивість не є строго необхідною.
