# 📋 Контракт корутини: обіцянка, очікувач, `coroutine_handle`

Довідник відповідає на одне питання: **які саме імена компілятор шукатиме у вашому корутинному типі, з якою сигнатурою й у якій миті**. Нижче повний перелік членів обіцянки, три функції очікувача з усіма трьома типами повернення `await_suspend`, повний API `std::coroutine_handle` з передумовами кожного члена й мінімальний тип, який збереться. Формулювання звірені з чинним робочим проєктом стандарту ([dcl.fct.def.coroutine], [expr.await], [coroutine.handle]).

## Обіцянка: повний перелік членів

Тип обіцянки компілятор бере як `std::coroutine_traits<R, P1…Pn>::promise_type`, де `R` — тип повернення корутини, `P1…Pn` — типи її параметрів (для методу першим іде тип об'єкта). Стандартний трейт просто віддає вкладений `R::promise_type`.

Ця зайва ланка потрібна рівно для одного: **зробити корутинним чужий тип**, у який вкладеного `promise_type` не додати. Тоді трейт спеціалізують ззовні:

```cpp
template<class... Args>
struct std::coroutine_traits<my_lib::future<int>, Args...> {
    using promise_type = my_adapter_promise;
};
```

Оскільки в списку параметрів трейта стоять і типи аргументів, спеціалізацію можна звузити до конкретної сигнатури — наприклад, дати окрему обіцянку методам певного класу, поставивши першим параметром `MyClass&`.

| Член | Сигнатура | Коли кличеться | Обов'язковий |
|---|---|---|---|
| конструктор | `promise_type(Args&…)` або `promise_type()` | після копіювання параметрів у кадр, перед усім іншим | так, хоч одна форма |
| `get_return_object` | `R get_return_object()` | один раз, до першого рядка тіла | **так** |
| `initial_suspend` | `/*awaitable*/ initial_suspend()` | одразу після `get_return_object()` | **так** |
| `final_suspend` | `/*awaitable*/ final_suspend() noexcept` | після тіла — і після `co_return`, і після `unhandled_exception()` | **так** |
| `unhandled_exception` | `void unhandled_exception()` | у `catch (...)`, що огортає тіло | **так** |
| `return_void` | `void return_void()` | на `co_return;` і на вихід за кінець тіла | рівно **одна** |
| `return_value` | `void return_value(T)` | на `co_return v;` | з двох |
| `yield_value` | `/*awaitable*/ yield_value(T)` | на кожен `co_yield v` | лише якщо в тілі є `co_yield` |
| `await_transform` | `/*awaitable*/ await_transform(T)` | на кожен **явний** `co_await a` | ні |
| `operator new` | `void* operator new(std::size_t[, Args…])` | виділення кадру, якщо його не усунуто | ні |
| `operator delete` | `void operator delete(void*[, std::size_t])` | знищення кадру | ні |
| `get_return_object_on_allocation_failure` | `static R get_return_object_on_allocation_failure()` | коли виділення віддало `nullptr` | ні |

`/*awaitable*/` означає «будь-який тип, з якого добувається очікувач» — див. розділ нижче. `operator new` і `operator delete` в класі неявно статичні, слово `static` писати не треба.

### Порядок викликів

1. Копії параметрів створюються в кадрі.
2. Конструюється обіцянка. **Попередній перегляд параметрів:** якщо конструктор, придатний для аргументів `(q1, …, qn)` — lvalue-копій параметрів, — існує, кличеться він; ні — конструктор за замовчуванням.
3. `promise.get_return_object()`. Стандарт гарантує: цей виклик **послідовний перед** `initial_suspend()`.
4. `co_await promise.initial_suspend()`.
5. Тіло. `co_yield v` ≡ `co_await promise.yield_value(v)`; `co_return v` ≡ `promise.return_value(v)`; `co_return;` і вихід за кінець ≡ `promise.return_void()`.
6. Виняток із тіла — `promise.unhandled_exception()`.
7. `co_await promise.final_suspend()`.
8. Керування пройшло далі → кадр знищується сам; спинилося → кадр чекає на `h.destroy()`.

Час життя копій параметрів закінчується **одразу після** часу життя обіцянки — тобто вони живі, поки живий кадр.

### Дрібний друк

| Правило | Точне формулювання |
|---|---|
| Результат `get_return_object` | ним ініціалізується результат виклику корутини. Якщо його тип не збігається з `R`, перетворення відкладається до самого повернення — тому в `get_return_object` можна віддавати проміжний тип, який знає лише handle |
| Пошук `operator new` | якщо в області обіцянки знайшлися оголошення — [розв'язання перевантажень](topic:sys-plang-cpp/overload-resolution) на списку `(size, p1, …, pn)`; **придатної не знайшлося — повторний захід лише з `(size)`**; оголошень в обіцянці немає взагалі — пошук у глобальній області з одним `(size)` |
| Вибір `operator delete` | знайшлися і однопараметрична, і двопараметрична звичайні форми → обирається **двопараметрична** `(void*, std::size_t)`; інакше однопараметрична. Це та сама пара форм, що й у [звичайних `new`/`delete`](topic:sys-plang-cpp/new-delete-allocation) |
| `get_return_object_on_allocation_failure` | сама її наявність в області обіцянки перемикає режим: функція виділення вважається такою, що на невдачу віддає `nullptr`, і мусить мати непорожній `noexcept`; із глобальних береться форма `::operator new(std::size_t, std::nothrow_t)`. На `nullptr` кадр не створюється взагалі, керування вертається викликачеві, а результатом виклику стає `T::get_return_object_on_allocation_failure()` |
| `await_transform` — усе або нічого | достатньо, щоб **ім'я** знайшлося в області обіцянки: після цього крізь нього йде кожен явний `co_await`, і невдале перевантаження — помилка компіляції, а не тихий обхід. Саме так тип забороняє чужі очікувачі |
| Що повз `await_transform` | неявні очікування — від `co_yield`, від `initial_suspend` і від `final_suspend` — **не** перетворюються. `operator co_await` до них застосовується як звичайно |
| `return_void` + `return_value` | оголошені обидві — програма неправильна. Немає `return_void`, а керування вийшло за кінець тіла — **невизначена поведінка** |
| Непорушність `final_suspend` | стандарт вимагає, щоб не кидав **увесь вираз** `co_await promise.final_suspend()`: і сама функція, і всі три функції її очікувача. Одного `noexcept` на `final_suspend` замало, якщо очікувач кидальний ([що саме означає `noexcept` у сигнатурі](topic:sys-plang-cpp/noexcept)) |
| Кидальна `unhandled_exception` | якщо виняток вилетів із самої `unhandled_exception()`, корутина вважається призупиненою в кінцевій точці, а виняток летить викликачеві або відновлювачеві. Кадр при цьому живий і чекає на `destroy()` |

## Очікувач: три функції

| Функція | Сигнатура | Коли | Результат |
|---|---|---|---|
| `await_ready` | `bool await_ready()` | перша, ще до будь-якої роботи з призупинення | контекстно перетворюється на `bool`; `true` — призупинення не буде |
| `await_suspend` | `R await_suspend(std::coroutine_handle<P> h)`, де `R` — `void`, `bool` або `std::coroutine_handle<Z>` | кадр уже призупинено, стан збережено | див. таблицю нижче |
| `await_resume` | `T await_resume()` | після відновлення | стає значенням усього виразу `co_await` |

`P` — тип обіцянки **тієї корутини, що чекає**; параметр можна оголосити й ширшим типом, до якого `coroutine_handle<P>` перетворюється, — зазвичай `std::coroutine_handle<>`.

### Три типи повернення `await_suspend`

| Тип | Що робить стандарт | Навіщо |
|---|---|---|
| `void` | керування безумовно вертається тому, хто викликав або відновив корутину | звичайне призупинення |
| `bool` | вираз обчислюється, і **корутина відновлюється, якщо результат `false`**; `true` — до викликача | передумати вже після призупинення: зареєструвалися й побачили, що результат уже є |
| `std::coroutine_handle<Z>` | обчислюється `await-suspend.resume()` — керування переходить **прямо в ту корутину**, симетричним передаванням, без нарощування стека | ланцюжок продовжень; коли відновлювати нікого — `std::noop_coroutine()` |

Дві пастки контракту. **Виняток із `await_suspend`** не пропадає: корутина відновлюється, і виняток кидається повторно вже в її контексті. **Після того, як handle віддано назовні** (записано в чергу, передано в інший потік, ужито в `h.resume()`), кадр і сам об'єкт-очікувач можуть уже не існувати — торкатися своїх членів після цієї миті `await_suspend` не має права.

### Звідки береться очікувач

Вираз `co_await a` перетворюється на очікувача трьома кроками, кожен з яких може нічого не змінити:

1. **`await_transform`** — якщо ім'я є в області обіцянки й очікування явне: `a` → `p.await_transform(a)`.
2. **`operator co_await`** — якщо для отриманого виразу є придатні перевантаження (член або вільна функція): результат стає очікувачем. Неоднозначність тут — помилка компіляції.
3. Не спрацювало ні те, ні те — очікувачем мусить бути сам вираз.

Два готові очікувачі стандарт дає прямо, і обидва — порожні структури:

```cpp
struct suspend_always {
    constexpr bool await_ready() const noexcept { return false; }
    constexpr void await_suspend(coroutine_handle<>) const noexcept {}
    constexpr void await_resume() const noexcept {}
};
struct suspend_never {                      // те саме, але await_ready() → true
    constexpr bool await_ready() const noexcept { return true; }
    constexpr void await_suspend(coroutine_handle<>) const noexcept {}
    constexpr void await_resume() const noexcept {}
};
```

## `std::coroutine_handle`

Заголовок `<coroutine>`. Усередині — один нетипізований вказівник: тип тривіально копійовний, передається за значенням, деструктора не має й кадром **не володіє**.

```cpp
template<class Promise> struct coroutine_handle {
    constexpr coroutine_handle() noexcept;
    constexpr coroutine_handle(nullptr_t) noexcept;
    coroutine_handle& operator=(nullptr_t) noexcept;

    static coroutine_handle from_promise(Promise&);
    constexpr void* address() const noexcept;
    static constexpr coroutine_handle from_address(void* addr);
    constexpr operator coroutine_handle<>() const noexcept;

    constexpr explicit operator bool() const noexcept;
    bool done() const;

    void resume() const;
    void operator()() const;                 // те саме, що resume()
    void destroy() const;

    Promise& promise() const;
};
```

Спеціалізація `coroutine_handle<void>` (вона ж `coroutine_handle<>`) має рівно те саме **без** `from_promise`, `promise()` і перетворення. Це стирання типу в один бік: назад до `coroutine_handle<P>` вертаються лише через `address()` → `from_address()`.

| Член | Передумова (інакше — невизначена поведінка) |
|---|---|
| `from_promise(p)` | `p` — обіцянка **живого** кадру |
| `promise()` | handle указує на кадр |
| `address()` | завжди можна; для порожнього handle віддає `nullptr` |
| `from_address(a)` | `a` здобуто попереднім `address()` handle **із тим самим** типом обіцянки (для `coroutine_handle<>` — з будь-яким) |
| `done()` | кадр **призупинено**. Віддає `true` лише для кінцевої точки. На кадрі, що виконується, питати не можна |
| `resume()` / `operator()()` | кадр призупинено й **не** в кінцевій точці |
| `destroy()` | кадр призупинено — у будь-якій точці, зокрема кінцевій |
| `explicit operator bool` | завжди. **Каже лише, чи вказівник ненульовий** — після `destroy()` handle лишається «істинним» і висячим |

Порівняння: `operator==` і `operator<=>` зіставляють `address()`; спеціалізація `std::hash` увімкнена — handle можна класти в невпорядковані контейнери.

**`std::noop_coroutine()`** віддає `std::noop_coroutine_handle` — handle на кадр без жодного спостережуваного ефекту: `operator bool` завжди `true`, `done()` завжди `false`, `resume()`, `operator()` і `destroy()` не роблять нічого, `address()` ніколи не `nullptr`, усе — `constexpr noexcept`. Це штатна відповідь `await_suspend`, коли треба сказати «нікого відновлювати, вертайся до викликача», не втрачаючи типу `coroutine_handle<Z>`.

## Мінімальний тип, що збереться

Шість обов'язкових членів і нічого зайвого — «гаряча» задача без результату, яка сама прибирає за собою:

```cpp
#include <coroutine>
#include <exception>
#include <print>

struct fire_and_forget {
    struct promise_type {
        fire_and_forget get_return_object() noexcept { return {}; }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }   // кадр гине сам
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };
};

fire_and_forget log_later(int n) {
    co_await std::suspend_never{};   // await_ready() == true → призупинення не буде
    std::print("{}\n", n);           // n — копія, що лежить у кадрі
    co_return;                       // → return_void(), далі final_suspend і смерть кадру
}
```

Замініть `final_suspend` на `std::suspend_always` — і тип зобов'язаний обзавестися handle й деструктором із `h.destroy()`, бо кадр більше не прибирає себе сам.
