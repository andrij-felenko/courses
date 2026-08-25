# ⚙️ Машинна реалізація замикань: товстий покажчик, оточення та виклик

Високорівневі мови створюють ілюзію, ніби функція з захопленими змінними — це звичайне число чи адреса в пам'яті, яку можна вільно передавати між модулями. На рівні ж асемблера та архітектури процесора жодної інструкції на кшталт «викликати замикання» не існує. Процесор фоннейманівської архітектури оперує виключно інструкцією непрямого переходу (наприклад, `CALL RAX` у x86-64 або `BLR X0` в ARM64), яка очікує єдину плоску адресу точки входу в машинний код.

Звичайна статична функція не потребує додаткових структур: її адреса відома на етапі лінкування, а всі параметри передаються через стандартні регістри відповідно до [ABI та calling convention](topic:sf-lang/abi-calling-convention). Але щойно функція захоплює змінні зі свого лексичного контексту, вона перестає бути просто кодом — вона стає **парою з коду та стану**. Якщо передати у виклик лише адресу інструкцій, функція не матиме звідки прочитати значення захоплених змінних.

Щоб передати разом із кодом його динамічний стан, компілятор або системний рантайм мусить самостійно збудувати машинну структуру — **товстий покажчик** (англ. *fat pointer*) або функціональний об'єкт.

## Три підходи до машинної реалізації замикань

В історії системного програмування та трансляції мов склалося три принципові підходи до представлення замикань у пам'яті:

1. **Товстий покажчик (Fat Pointer / Pair):** Замикання представляється парою двох машинних слів: `(code_ptr, env_ptr)`. Перше слово вказує на скомпільований код у сегменті `.text`, друге — на блок пам'яті з захопленими змінними. При виклику рантайм передає `env_ptr` як перший неявний аргумент (у регістрі `RDI` або `RCX`). Це найчистіший підхід, який використовують Go, Rust і сучасні функційні мови.
2. **Трампліни на стеку (Trampolines / Code Generation at Runtime):** Історичний підхід компілятора GCC для вкладених функцій у мові C. Компілятор генерує на стеку мікроскопічний фрагмент виконуваного машинного коду (3–4 інструкції), який завантажує адресу локального кадру в статичний регістр і виконує стрибок `JMP` на тіло функції. Цей підхід дозволяв передавати вкладену функцію як звичайний покажчик `void (*)(void)`, але спричинив катастрофічні проблеми з безпекою: сучасні операційні системи забороняють виконання коду зі стека (політика `W^X` — *Write XOR Execute*, апаратний прапорець NX/DEP).
3. **Стирання типів та функціональні об'єкти (Type Erasure & Functors):** Замикання загортається у структуру з віртуальною таблицею методів або статичним перехідником (Thunk). Цей підхід використовується у `std::function` у C++, де реалізовано оптимізацію малого буфера (SBO) для уникнення динамічного виділення пам'яті на купі.

## Архітектурний контракт товстого покажчика

Щоб замикання могло приймати довільні захоплені змінні, функціонувати в умовах висхідного повернення (upward funarg) та коректно вивільняти пам'ять, воно має інкапсулювати три сутності:

- **Точка входу (Thunk / Invoke-функція):** Статична функція, адреса якої лежить у сегменті коду. Вона знає конкретний тип упакованого оточення, розпаковує його й викликає цільову логіку.
- **Блок оточення (Environment Record):** Ділянка пам'яті (на [купі](topic:sf-lang/heap-dynamic-memory) або [стеку](topic:sf-lang/stack-lifo)), де зберігаються значення або посилання на захоплені змінні.
- **Функція очищення (Destructor / Clean-up):** Процедура деструкції, яка знає, як звільнити ресурси блоку оточення, коли замикання більше не потрібне.

Нижче наведено повну реалізацію системного рантайму замикань з підтримкою динамічного стану на купі (C) та контейнера зі стиранням типів і малим буфером (C++).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Універсальний тип замикання: приймає int, повертає int */
typedef int (*int_invoke_fn)(void *env, int arg);
typedef void (*int_destroy_fn)(void *env);

typedef struct {
    int_invoke_fn  invoke;   /* покажчик на машинний код перехідника */
    void          *env;      /* покажчик на блок захоплених змінних */
    int_destroy_fn destroy;  /* деструктор для очищення оточення */
} int_closure_t;

/* Виклик замикання через розпакування оточення */
static inline int closure_call(const int_closure_t *c, int arg) {
    return c->invoke(c->env, arg);
}

/* Звільнення ресурсів замикання */
static inline void closure_free(int_closure_t *c) {
    if (c->destroy && c->env) {
        c->destroy(c->env);
        c->env = NULL;
    }
}

/* =========================================================================
 * Приклад: Фабрика замикань-накопичувачів (Stateful Accumulator)
 * ========================================================================= */

typedef struct {
    int current_sum;
    int step_multiplier;
} accumulator_env_t;

/* Статична функція виклику: знає точну структуру оточення */
static int accumulator_invoke(void *raw_env, int val) {
    accumulator_env_t *env = (accumulator_env_t *)raw_env;
    env->current_sum += val * env->step_multiplier;
    return env->current_sum;
}

/* Деструктор середовища */
static void accumulator_destroy(void *raw_env) {
    free(raw_env);
}

/* Функція-фабрика, що повертає замикання на купі (Upward Funarg) */
int_closure_t make_accumulator(int initial_val, int multiplier) {
    accumulator_env_t *env = (accumulator_env_t *)malloc(sizeof(accumulator_env_t));
    if (!env) {
        perror("malloc failed");
        exit(EXIT_FAILURE);
    }
    env->current_sum = initial_val;
    env->step_multiplier = multiplier;

    int_closure_t c = {
        .invoke = accumulator_invoke,
        .env = env,
        .destroy = accumulator_destroy
    };
    return c;
}

int main(void) {
    /* Створюємо два незалежні екземпляри замикання зі своїм станом */
    int_closure_t acc1 = make_accumulator(10, 1);  /* стартує з 10, множник 1 */
    int_closure_t acc2 = make_accumulator(0, 10);  /* стартує з 0, множник 10 */

    printf("acc1(5)  -> %d (очікувано: 15)\n", closure_call(&acc1, 5));
    printf("acc1(3)  -> %d (очікувано: 18)\n", closure_call(&acc1, 3));

    printf("acc2(2)  -> %d (очікувано: 20)\n", closure_call(&acc2, 2));
    printf("acc2(4)  -> %d (очікувано: 60)\n", closure_call(&acc2, 4));

    /* Повторний виклик acc1 підтверджує повну ізольованість пам'яті */
    printf("acc1(2)  -> %d (очікувано: 20)\n", closure_call(&acc1, 2));

    closure_free(&acc1);
    closure_free(&acc2);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <utility>
#include <new>

/* =========================================================================
 * Реалізація універсального контейнера замикання (Type Erasure + SBO)
 * Оптимізація малого буфера (SBO): змінні <= 24 байтів не йдуть на купу.
 * ========================================================================= */

template <typename Signature>
class CustomFunction;

template <typename Ret, typename... Args>
class CustomFunction<Ret(Args...)> {
private:
    struct IConcept {
        virtual ~IConcept() = default;
        virtual Ret invoke(Args... args) = 0;
        virtual void move_to(void *dest) noexcept = 0;
    };

    template <typename Callable>
    struct Model final : IConcept {
        Callable callable;

        explicit Model(Callable &&c) : callable(std::forward<Callable>(c)) {}

        Ret invoke(Args... args) override {
            return callable(std::forward<Args>(args)...);
        }

        void move_to(void *dest) noexcept override {
            new (dest) Model(std::move(*this));
        }
    };

    static constexpr size_t SBO_SIZE = 24;
    alignas(max_align_t) char storage_[SBO_SIZE];
    IConcept *concept_ptr_{nullptr};
    bool is_small_{false};

    void clear() noexcept {
        if (concept_ptr_) {
            if (is_small_) {
                concept_ptr_->~IConcept();
            } else {
                delete concept_ptr_;
            }
            concept_ptr_ = nullptr;
        }
    }

public:
    CustomFunction() noexcept = default;

    template <typename F>
    CustomFunction(F &&callable) {
        using ModelType = Model<std::decay_t<F>>;
        if constexpr (sizeof(ModelType) <= SBO_SIZE && alignof(ModelType) <= alignof(max_align_t)) {
            concept_ptr_ = new (storage_) ModelType(std::forward<F>(callable));
            is_small_ = true;
        } else {
            concept_ptr_ = new ModelType(std::forward<F>(callable));
            is_small_ = false;
        }
    }

    ~CustomFunction() noexcept {
        clear();
    }

    CustomFunction(CustomFunction &&other) noexcept {
        if (other.is_small_ && other.concept_ptr_) {
            other.concept_ptr_->move_to(storage_);
            concept_ptr_ = reinterpret_cast<IConcept *>(storage_);
            is_small_ = true;
            other.clear();
        } else {
            concept_ptr_ = other.concept_ptr_;
            is_small_ = other.is_small_;
            other.concept_ptr_ = nullptr;
        }
    }

    CustomFunction &operator=(CustomFunction &&other) noexcept {
        if (this != &other) {
            clear();
            if (other.is_small_ && other.concept_ptr_) {
                other.concept_ptr_->move_to(storage_);
                concept_ptr_ = reinterpret_cast<IConcept *>(storage_);
                is_small_ = true;
                other.clear();
            } else {
                concept_ptr_ = other.concept_ptr_;
                is_small_ = other.is_small_;
                other.concept_ptr_ = nullptr;
            }
        }
        return *this;
    }

    CustomFunction(const CustomFunction &) = delete;
    CustomFunction &operator=(const CustomFunction &) = delete;

    Ret operator()(Args... args) const {
        if (!concept_ptr_) {
            throw std::bad_alloc();
        }
        return concept_ptr_->invoke(std::forward<Args>(args)...);
    }
};

/* =========================================================================
 * Використання: Фабрика та виклики
 * ========================================================================= */

CustomFunction<int(int)> make_accumulator(int initial_val, int multiplier) {
    // Лямбда-вираз автоматично генерує анонімний клас із полями
    return [current_sum = initial_val, multiplier](int val) mutable -> int {
        current_sum += val * multiplier;
        return current_sum;
    };
}

int main() {
    auto acc1 = make_accumulator(10, 1);
    auto acc2 = make_accumulator(0, 10);

    std::cout << "acc1(5)  -> " << acc1(5) << " (очікувано: 15)\n";
    std::cout << "acc1(3)  -> " << acc1(3) << " (очікувано: 18)\n";

    std::cout << "acc2(2)  -> " << acc2(2) << " (очікувано: 20)\n";
    std::cout << "acc2(4)  -> " << acc2(4) << " (очікувано: 60)\n";

    std::cout << "acc1(2)  -> " << acc1(2) << " (очікувано: 20)\n";
    return 0;
}
```
:::

## Покроковий розбір машинного коду виклику

Коли програма викликає замикання через товстий покажчик або стертий тип, процесор виконує інший набір інструкцій порівняно з прямим викликом звичайної функції:

```
; 1. Завантаження адреси перехідника (Thunk) та покажчика на оточення
MOV RAX, [RDI + 0]       ; RAX = closure.invoke (адреса коду)
MOV RDI, [RDI + 8]       ; RDI = closure.env (покажчик на оточення стає 1-м аргументом)
MOV ESI, EDX             ; ESI = фактичний аргумент val (2-й аргумент)

; 2. Непрямий виклик через покажчик
CALL RAX                 ; Непрямий перехід на скомпільований код перехідника
```

Усередині тіла `accumulator_invoke` процесор звертається до захоплених полів через зміщення відносно регістра `RDI`:

```
; Тіло accumulator_invoke(env, val)
MOV EAX, [RDI + 4]       ; EAX = env->step_multiplier (зміщення +4 байти)
IMUL EAX, ESI            ; EAX = val * multiplier
ADD [RDI + 0], EAX       ; env->current_sum += EAX (зміщення +0 байтів)
MOV EAX, [RDI + 0]       ; RAX = результат (повертається з функції)
RET                      ; Повернення у точку виклику
```

## Інженерні наслідки та вартість виконання

Цей розбір на рівні регістрів демонструє три чіткі інженерні висновки:

1. **Ціна непрямого переходу (Indirect Call Overhead):** Інструкція `CALL RAX` залежить від апаратного передбачувача переходів процесора (англ. *Branch Target Buffer*, BTB). Якщо в одному й тому самому циклі чергуються різні типи замикань, передбачувач помиляється, і конвеєр скидає частково виконані мікроінструкції. Накладні витрати такого скидання становлять від 10 до 20 тактів процесора на кожен виклик.
2. **Бар'єр для оптимізаційного вбудовування (Inlining):** Оскільки адреса коду витягується з динамічної структури в пам'яті під час виконання, компілятор на рівні компіляції не може вбудувати тіло замикання безпосередньо в місце виклику (окрім випадків спеціалізації через шаблони або розпізнавання констант).
3. **Оптимізація малого буфера (Small Buffer Optimization, SBO):** Динамічне виділення пам'яті на купі через `malloc` створює накладні витрати на синхронізацію потоків та фрагментацію пам'яті. У С++-реалізації невеличкі замикання розміром до 24 байтів розміщуються безпосередньо у внутрішньому буфері `storage_` всередині об'єкта. Це зводить накладні витрати виділення пам'яті до абсолютного нуля, зберігаючи при цьому семантику універсального замикання першого класу.

Для порівняння, у мові Rust компілятор за замовчуванням генерує для кожного замикання унікальну анонімну структуру `struct`, розмір якої точно дорівнює сумі розмірів захоплених полів. Якщо замикання передається у функцію через узагальнений параметр типу `fn process<F: Fn(i32) -> i32>(f: F)`, компілятор застосовує мономорфізацію: він повністю розгортає структуру на стеку та вбудовує виклик без жодних товстих покажчиків і непрямих переходів. Товстий покажчик `dyn Fn(i32) -> i32` на купі формується лише тоді, коли розробник явно вимагає динамічної диспетчеризації через типаж-об'єкт `Box<dyn Fn>`.
