# ⚙️ Реалізація власного контейнера типів: від C-callback до C++ SBO Type Erasure

Ця практична вставка демонструє повний процес побудови системи стирання типів від найнижчого рівневого концепту до високопродуктивного C++ контейнера. Ми розберемо реалізацію диспатчеризації викликів мовою C через контекстний покажчик `void* user_data`, а потім побудуємо власну повноцінну обгортку `custom_function<R(Args...)>` мовою C++ із підтримкою оптимізації малого буфера (SBO), семантики переміщення та управління часом життя об'єктів.

Побудова власного типу стирання дозволяє зрозуміти, як стандартна бібліотека `std::function` поєднує шаблони під час конструювання з нешаблонним викликом через функціональні вказівники у внутрішній таблиці віртуальних методів.

## 1. Підхід мовою C: Контекстний покажчик void* та функціональні покажчики

У системному програмуванні мовою C стирання типів реалізується через явне розділення даних та коду. Функція обробки приймає сирий вказівник на довільні дані `void* user_data` та вказівник на функцію-перехідник (англ. *trampoline function*). 

Контекстний вказівник `user_data` стирає тип вихідного об'єкта, оскільки приводиться до `void*`. Функція-перехідник знає справжній тип даних, приводить `user_data` назад до точного типу та здійснює виклик операції.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Вказівник на функцію-перехідник у C: приймає контекст та аргумент */
typedef void (*c_callback_t)(void* user_data, int event_id);

/* Структура для зберігання обробника події */
typedef struct {
    void* user_data;
    c_callback_t invoke;
    void (*destroy)(void* user_data);
} c_event_handler_t;

/* Приклад 1: Простий обробник без стану */
void simple_trampoline(void* user_data, int event_id) {
    (void)user_data;
    printf("[C Simple] Received event: %d\n", event_id);
}

/* Приклад 2: Обробник зі станом (структура у купі) */
typedef struct {
    char prefix[32];
    int counter;
} logger_context_t;

void logger_trampoline(void* user_data, int event_id) {
    logger_context_t* ctx = (logger_context_t*)user_data;
    ctx->counter++;
    printf("[C Logger %s #%d] Event ID: %d\n", ctx->prefix, ctx->counter, event_id);
}

void logger_destroy(void* user_data) {
    free(user_data);
}

/* Ініціалізація обробника зі станом */
c_event_handler_t create_logger(const char* prefix) {
    logger_context_t* ctx = (logger_context_t*)malloc(sizeof(logger_context_t));
    strncpy(ctx->prefix, prefix, sizeof(ctx->prefix) - 1);
    ctx->prefix[sizeof(ctx->prefix) - 1] = '\0';
    ctx->counter = 0;

    c_event_handler_t handler;
    handler.user_data = ctx;
    handler.invoke = logger_trampoline;
    handler.destroy = logger_destroy;
    return handler;
}

void execute_c_handler(const c_event_handler_t* handler, int event_id) {
    if (handler->invoke) {
        handler->invoke(handler->user_data, event_id);
    }
}

void free_c_handler(c_event_handler_t* handler) {
    if (handler->destroy && handler->user_data) {
        handler->destroy(handler->user_data);
        handler->user_data = NULL;
    }
}

int main(void) {
    c_event_handler_t h1 = { NULL, simple_trampoline, NULL };
    c_event_handler_t h2 = create_logger("NetworkSubsystem");

    execute_c_handler(&h1, 101);
    execute_c_handler(&h2, 202);
    execute_c_handler(&h2, 203);

    free_c_handler(&h2);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <utility>

// Ідіоматичний еквівалент C++: Використання RAII та поліморфного класу
class CppEventHandler {
public:
    virtual ~CppEventHandler() = default;
    virtual void invoke(int event_id) = 0;
};

class SimpleHandler : public CppEventHandler {
public:
    void invoke(int event_id) override {
        std::cout << "[C++ Simple] Received event: " << event_id << '\n';
    }
};

class LoggerHandler : public CppEventHandler {
private:
    std::string prefix_;
    int counter_{0};

public:
    explicit LoggerHandler(std::string prefix) : prefix_(std::move(prefix)) {}

    void invoke(int event_id) override {
        counter_++;
        std::cout << "[C++ Logger " << prefix_ << " #" << counter_ << "] Event ID: " << event_id << '\n';
    }
};

int main() {
    std::unique_ptr<CppEventHandler> h1 = std::make_unique<SimpleHandler>();
    std::unique_ptr<CppEventHandler> h2 = std::make_unique<LoggerHandler>("NetworkSubsystem");

    h1->invoke(101);
    h2->invoke(202);
    h2->invoke(203);
}
```
:::

Використання сирих `void*` у C вимагає ручного стеження за руйнуванням об'єктів та позбавлене перевірки типів на етапі компіляції. Якщо розробник передасть не той тип контексту в `logger_trampoline`, програма зазнає пошкодження пам'яті (Memory Corruption) через неправильне зчитування полів структури.

ООП-підхід у C++ із віртуальними функціями гарантує тип-безпеку та автоматичний виклик деструкторів, але змушує створювати класи-спадкоємці для кожної лямбди або стороннього функтора, що ускладнює архітектуру та змушує робити динамічні виділення пам'яті для кожного об'єкта.

---

## 2. Реалізація custom_function<R(Args...)> у C++ з оптимізацією SBO

Побудуємо повноцінний клас `custom_function`, який стирає типи довільних викликальних об'єктів без обов'язкового спадкування та підтримує **Small Buffer Optimization (SBO)** для усунення виділень пам'яті у купі для малих лямбд.

### Архітектура системи custom_function:
1. **Буфер SBO**: Масив байтів `alignas(std::max_align_t) char storage_[24]` розміром 24 байти. Якщо об'єкт малогабаритний, він розміщується безпосередньо в цьому масиві через placement new.
2. **Таблиця виклику та управління (Vtable)**: Структура з 3 функціональних вказівників:
   - `invoker`: здійснює виклик `operator()` з приведенням типу з `storage_`;
   - `destroyer`: викликає деструктор об'єкта у SBO-буфері або робить `delete` для купового буфера;
   - `relocator`: переміщує або копіює вміст `storage_` при переміщенні `custom_function`.

Завдяки статичним шаблонам усередині конструктора, компілятор автоматично генерує унікальні функції-тланки для кожного переданого типу `F`.

```cpp
#include <iostream>
#include <utility>
#include <new>
#include <type_traits>
#include <cstddef>
#include <cassert>
#include <string>

template <typename Signature>
class custom_function;

template <typename R, typename... Args>
class custom_function<R(Args...)> {
private:
    static constexpr std::size_t SBO_SIZE = 24;

    // Внутрішній розрівняний буфер для збереження малогабаритних функторів
    alignas(std::max_align_t) mutable char storage_[SBO_SIZE];

    // Вказівники на функції диспатчеризації (Ручний Vtable)
    using invoker_t   = R (*)(const void* storage, Args&&... args);
    using destroyer_t = void (*)(void* storage);
    using relocator_t = void (*)(void* dst_storage, void* src_storage);

    invoker_t   invoker_{nullptr};
    destroyer_t destroyer_{nullptr};
    relocator_t relocator_{nullptr};

    // Перевірка: чи вміщується тип F у буфер SBO?
    template <typename F>
    static constexpr bool fits_in_sbo = (sizeof(F) <= SBO_SIZE) && 
                                        (alignof(F) <= alignof(std::max_align_t)) &&
                                        std::is_nothrow_move_constructible_v<F>;

public:
    // 1. Порожній конструктор
    custom_function() noexcept = default;
    custom_function(std::nullptr_t) noexcept {}

    // 2. Шаблонний конструктор для довільного Callable F
    template <typename F, 
              typename = std::enable_if_t<!std::is_same_v<std::decay_t<F>, custom_function>>>
    custom_function(F&& f) {
        using DecayedF = std::decay_t<F>;

        if constexpr (fits_in_sbo<DecayedF>) {
            // Розміщення всередині SBO-буфера через placement new
            new (storage_) DecayedF(std::forward<F>(f));

            invoker_ = [](const void* storage, Args&&... args) -> R {
                auto* fn = reinterpret_cast<const DecayedF*>(storage);
                return (*fn)(std::forward<Args>(args)...);
            };

            destroyer_ = [](void* storage) {
                auto* fn = reinterpret_cast<DecayedF*>(storage);
                fn->~DecayedF();
            };

            relocator_ = [](void* dst, void* src) {
                auto* src_fn = reinterpret_cast<DecayedF*>(src);
                new (dst) DecayedF(std::move(*src_fn));
                src_fn->~DecayedF();
            };
        } else {
            // Виділення пам'яті у купі для великого об'єкта
            DecayedF* heap_ptr = new DecayedF(std::forward<F>(f));
            *reinterpret_cast<DecayedF**>(storage_) = heap_ptr;

            invoker_ = [](const void* storage, Args&&... args) -> R {
                auto* heap_ptr = *reinterpret_cast<DecayedF* const*>(storage);
                return (*heap_ptr)(std::forward<Args>(args)...);
            };

            destroyer_ = [](void* storage) {
                auto* heap_ptr = *reinterpret_cast<DecayedF**>(storage);
                delete heap_ptr;
            };

            relocator_ = [](void* dst, void* src) {
                *reinterpret_cast<DecayedF**>(dst) = *reinterpret_cast<DecayedF**>(src);
                *reinterpret_cast<DecayedF**>(src) = nullptr;
            };
        }
    }

    // 3. Деструктор
    ~custom_function() {
        reset();
    }

    // 4. Переміщуючий конструктор
    custom_function(custom_function&& other) noexcept {
        move_from(std::move(other));
    }

    // 5. Переміщуючий оператор присвоєння
    custom_function& operator=(custom_function&& other) noexcept {
        if (this != &other) {
            reset();
            move_from(std::move(other));
        }
        return *this;
    }

    // Заборона копіювання для простоти розбору
    custom_function(const custom_function&) = delete;
    custom_function& operator=(const custom_function&) = delete;

    // 6. Оператор виклику
    R operator()(Args... args) const {
        if (!invoker_) {
            throw std::runtime_error("Bad custom_function call: empty object");
        }
        return invoker_(storage_, std::forward<Args>(args)...);
    }

    // 7. Оператор bool
    explicit operator bool() const noexcept {
        return invoker_ != nullptr;
    }

private:
    void reset() noexcept {
        if (destroyer_) {
            destroyer_(storage_);
            destroyer_ = nullptr;
            invoker_ = nullptr;
            relocator_ = nullptr;
        }
    }

    void move_from(custom_function&& other) noexcept {
        invoker_ = other.invoker_;
        destroyer_ = other.destroyer_;
        relocator_ = other.relocator_;

        if (other.relocator_) {
            other.relocator_(storage_, other.storage_);
            other.invoker_ = nullptr;
            other.destroyer_ = nullptr;
            other.relocator_ = nullptr;
        }
    }
};

// --- Демонстраційне використання custom_function ---

void global_print(int x) {
    std::cout << "[Global Function] Value: " << x << '\n';
}

int main() {
    // 1. Збереження сирої глобальної функції (SBO)
    custom_function<void(int)> fn1 = global_print;
    fn1(42);

    // 2. Збереження малої лямбди (SBO active: sizeof <= 24 bytes)
    int capture_val = 10;
    custom_function<void(int)> fn2 = [capture_val](int x) {
        std::cout << "[Small Lambda SBO] Capture: " << capture_val << ", Arg: " << x << '\n';
    };
    fn2(100);

    // 3. Збереження великої лямбди (Heap active: sizeof > 24 bytes)
    std::string large_str1 = "Extremely Large Header String Data Number 1";
    std::string large_str2 = "Extremely Large Header String Data Number 2";
    std::string large_str3 = "Extremely Large Header String Data Number 3";

    custom_function<void(int)> fn3 = [large_str1, large_str2, large_str3](int x) {
        std::cout << "[Large Lambda Heap] Combined size: " 
                  << (large_str1.size() + large_str2.size() + large_str3.size()) 
                  << ", Arg: " << x << '\n';
    };
    fn3(500);

    // 4. Переміщення об'єкта
    custom_function<void(int)> fn4 = std::move(fn3);
    assert(!fn3); // fn3 тепер порожній
    fn4(999);     // fn4 працює коректно
}
```

### Покроковий аналіз низькорівневих механізмів custom_function

#### 1. Оцінка розміру та вирівнювання (fits_in_sbo)
Компілятор перевіряє вираз `fits_in_sbo`. Якщо лямбда захоплює лише кілька цілочисельних змінних (наприклад, 8 чи 16 байтів) і має `noexcept` move-конструктор, вона конструюється безпосередньо у стековому буфері `storage_` через `placement new`. Це гарантує нульові виклики алокатора пам'яті. Вирівнювання `alignas(std::max_align_t)` гарантує, що адреса буфера `storage_` відповідає вимогам найсуворіших базових типів архітектури (наприклад, `double` або `long double`).

#### 2. Статичні тланк-лямбди для Vtable
Усередині конструктора генеруються три анонімні лямбди без захоплення, які безкоштовно конвертуються у сирі функціональні покажчики `invoker_t`, `destroyer_t`, `relocator_t`. Вони виконують роль прив'язки типу: приводять `const void* storage` до точного типу `DecayedF*` і викликають відповідні операції (`operator()`, деструктор `~DecayedF()` або move-конструктор). Оскільки лямбди не мають захоплення контексту, вони вироджуються у звичайні статичні функції без додаткових прихованих покажчиків.

#### 3. Динамічне управління купою для великих функторів
Якщо розмір захопленого контексту перевищує 24 байти (наприклад, лямбда захопила три великі об'єкти `std::string`), `custom_function` виділяє пам'ять у купі через `new DecayedF(...)`, а у внутрішньому буфері `storage_` зберігає лише 8-байтовий вказівник `DecayedF*`. При знищенні такого об'єкта функція `destroyer_` робить `delete heap_ptr`, що повертає пам'ять системному алокатору.

#### 4. Безпека переміщення та зсув адреси у SBO
При переміщенні об'єкта `custom_function` викликається функціональний вказівник `relocator_`. Якщо об'єкт знаходився у купі, `relocator_` просто копіює 8-байтовий покажчик і обнуляє вихідний об'єкт за `O(1)`. Якщо ж об'єкт знаходився у SBO-буфері, `relocator_` викликає placement move-конструктор нового об'єкта на новому місці в пам'яті та руйнує старий об'єкт у вихідному буфері.

#### 5. Гарантія винятків під час конструювання (Exception Safety)
Під час виклику `placement new` у внутрішньому SBO-буфері конструктор функтора може викинути виняток (наприклад, при копіюванні захопленого об'єкта `std::string`). У такому разі пам'ять у буфері `storage_` залишається неініціалізованою, а сам конструктор `custom_function` завершується розгортанням стеку без виклику деструктора. Поля `invoker_` та `destroyer_` залишаються у своєму початковому неініціалізованому або нульовому стані, що повністю запобігає витокам пам'яті або подвійному звільненню ресурсів (Double Free).

#### 6. Оптимізація розміру структури та усунення копіювання
У нашій демонстраційній реалізації `custom_function` свідомо вилучено конструктор копіювання, що робить її еквівалентною за семантикою до `std::move_only_function` із C++23. Додавання копіювання вимагало б 4-го покажчика в Vtable (`cloner_t`), що збільшило б розмір об'єкта на стеку з 48 до 56 байтів. Відмова від копіювання гарантує мінімальний розмір таблиці виклику та дозволяє безперешкодно зберігати move-only лямбди із захопленням `std::unique_ptr`.

У результаті запропонована реалізація `custom_function` повністю відтворює ключову механіку стандартного `std::function` та `std::move_only_function`, поєднуючи нульові алокації для малих функторів із можливістю збереження довільних складних об'єктів виклику.
