# ⚙️ Мінімальний `generator<T>` із нуля

C++20 дав механіку корутин, але жодного готового типу, у який ту механіку можна повернути, — тож `co_yield` без власного `generator<T>` просто не компілюється. Напишемо цей тип цілком: півсотні рядків, які працюють, і на них видно, як усі гачки обіцянки складаються в одну робочу річ.

## Що він має вміти

Вимог рівно чотири, і кожна тягне за собою свій шматок коду.

Він **лінивий**: доки читач не попросив першого значення, тіло не виконує жодного рядка. Він **тримає кадр до кінця**: коли тіло дійшло до кінця, читач мусить іще встигнути дізнатися, що елементи скінчилися. Він **сам прибирає** кадр — у деструкторі, хоч би читач і кинув обхід посеред нескінченної послідовності. І він **вкладається в `for (auto x : g)`** — це той інтерфейс, заради якого все й робиться.

Звідси три частини: обіцянка (переносить одне значення або виняток із кадру назовні), сам `generator` (єдиний власник handle), ітератор із вартовим (перекладає `resume`/`done` на `++`/`!=`).

## Код

```cpp
#include <coroutine>
#include <exception>
#include <iterator>
#include <memory>
#include <utility>

template <class T>
class generator {
public:
    struct promise_type {
        const T*           value = nullptr;   // дивиться всередину виразу co_yield
        std::exception_ptr error;

        generator get_return_object() noexcept {
            return generator{
                std::coroutine_handle<promise_type>::from_promise(*this) };
        }

        std::suspend_always initial_suspend() const noexcept { return {}; }  // лінивий старт
        std::suspend_always final_suspend()   const noexcept { return {}; }  // кадр не гине сам

        std::suspend_always yield_value(const T& v) noexcept {
            value = std::addressof(v);
            return {};
        }

        void return_void() const noexcept {}
        void unhandled_exception() noexcept { error = std::current_exception(); }

        void await_transform() = delete;      // co_await у цьому типі заборонено

        void rethrow_if_error() const {
            if (error) std::rethrow_exception(error);
        }
    };

    generator(generator&& other) noexcept : h_{ std::exchange(other.h_, {}) } {}

    generator& operator=(generator&& other) noexcept {
        if (this != &other) {
            if (h_) h_.destroy();
            h_ = std::exchange(other.h_, {});
        }
        return *this;
    }

    generator(const generator&)            = delete;
    generator& operator=(const generator&) = delete;

    ~generator() { if (h_) h_.destroy(); }

    struct sentinel {};

    class iterator {
    public:
        using iterator_concept = std::input_iterator_tag;
        using value_type       = T;
        using difference_type  = std::ptrdiff_t;

        iterator() = default;
        explicit iterator(std::coroutine_handle<promise_type> h) noexcept : h_{ h } {}

        const T& operator*()  const noexcept { return *h_.promise().value; }
        const T* operator->() const noexcept { return  h_.promise().value; }

        iterator& operator++() {
            h_.resume();
            h_.promise().rethrow_if_error();
            return *this;
        }
        void operator++(int) { ++*this; }

        bool operator==(sentinel) const noexcept { return !h_ || h_.done(); }

    private:
        std::coroutine_handle<promise_type> h_{};
    };

    iterator begin() {
        if (h_ && !h_.done()) {
            h_.resume();                      // доводимо тіло до першого co_yield
            h_.promise().rethrow_if_error();
        }
        return iterator{ h_ };
    }

    sentinel end() const noexcept { return {}; }

private:
    explicit generator(std::coroutine_handle<promise_type> h) noexcept : h_{ h } {}

    std::coroutine_handle<promise_type> h_{};
};
```

Компілюється як є: `g++ -std=c++20` чи `cl /std:c++20`, без жодних бібліотек понад стандартні заголовки.

## Чому в обіцянці лежить вказівник

Найдивніший рядок тут — `const T* value`. Здається природнішим тримати `T value` і копіювати в нього; так робити не варто з двох причин. По-перше, це вимагало б від `T` конструктора без аргументів і давало б зайву копію на кожен елемент. По-друге — вона просто не потрібна.

`co_yield x` розкривається у `co_await promise.yield_value(x)`. Параметр `const T&` зв'язується з аргументом; якщо аргумент був тимчасовим, тимчасовий живе до кінця **повного виразу**, а повний вираз тут — увесь `co_await` разом. Корутина спиняється всередині нього і завершить його аж після відновлення. Тобто об'єкт, на який дивиться `value`, гарантовано живий рівно доти, доки корутина стоїть на цьому `co_yield`, — а це і є той проміжок, коли читач тримає ітератор і дивиться на значення. Копію робити нема від чого.

Другий тонкий рядок — `void await_transform() = delete;`. Якщо обіцянка має `await_transform`, компілятор проганяє через нього кожен `co_await`, і `co_await щось` тут не знайде відповідного перевантаження — саме те, що треба синхронному генератору. Внутрішній `co_await` із `co_yield` при цьому не постраждає: правило про `await_transform` навмисно **не** застосовується до очікувань, породжених неявно — з `co_yield`, `initial_suspend` і `final_suspend` (це прямо прописано в [expr.await]/3).

## Нескінченна послідовність

```cpp
#include <cstdint>
#include <iostream>

generator<std::uint64_t> fibonacci() {
    std::uint64_t a = 0, b = 1;
    for (;;) {                       // кінця немає — і це нормально
        co_yield a;
        const std::uint64_t next = a + b;
        a = b;
        b = next;
    }
}

int main() {
    int taken = 0;
    for (std::uint64_t n : fibonacci()) {
        std::cout << n << ' ';
        if (++taken == 10) break;    // циклом володіє читач
    }
    std::cout << '\n';               // 0 1 1 2 3 5 8 13 21 34
}
```

Функція без жодного `return` і з нескінченним циклом усередині — і при цьому вона завершується. Ключове тут `break`: він виводить із циклу, тимчасовий `generator` гине в кінці оператора `for`, деструктор кличе `h_.destroy()`, а `destroy()` на призупиненій корутині нищить її локальні змінні й звільняє кадр. Кинути обхід посеред нескінченної послідовності — законна дія, а не витік.

## Виняток із тіла

Тіло корутини виконується у своєму кадрі, тож кинути «нагору» винятку нема куди — його ловить `unhandled_exception()` і кладе в обіцянку як `std::exception_ptr`. Після цього тіло вважається завершеним, корутина стає на `final_suspend`, і найближчий `resume()` із боку читача побачить `done()`. Наші `begin()` і `operator++` одразу після `resume()` питають `rethrow_if_error()` — і виняток вилітає в тому місці, де читач попросив наступний елемент:

```cpp
#include <stdexcept>
#include <string>
#include <vector>

generator<int> parsed(const std::vector<std::string>& rows) {
    for (const std::string& r : rows) {
        if (r.empty()) throw std::runtime_error{ "порожній рядок" };
        co_yield std::stoi(r);
    }
}

int main() {
    const std::vector<std::string> rows{ "10", "20", "", "40" };
    try {
        for (int v : parsed(rows)) std::cout << v << ' ';   // 10 20
    } catch (const std::exception& e) {
        std::cout << "\nобірвалося: " << e.what() << '\n';
    }
}
```

Виняток долає межу кадру рівно так само, як він долає межу потоку у [future й promise](root:sys-plang-cpp/future-promise): переносить не механізм мови, а збережений `exception_ptr`.

## Пастки

**Параметр за посиланням.** `parsed` вище бере `const std::vector<std::string>&`, і це працює лише тому, що `rows` — іменована змінна, яка переживе обхід. Передайте туди тимчасовий вектор — і кадр дивитиметься на мертву пам'ять: лінивий `initial_suspend` означає, що між створенням кадру й першим рядком тіла встигає закінчитися повний вираз виклику, а з ним померти всі тимчасові. Правило просте: параметри генератора беруть **за значенням**, поки не доведено, що джерело точно живе довше.

**Копіювання генератора.** Копіювальні операції видалено не з обережності, а тому, що інакше два об'єкти тримали б один handle і викликали `destroy()` двічі. `generator` — це той самий сирий вказівник під RAII-охороною, що й [unique_ptr](root:sys-plang-cpp/unique-ptr), і [правило п'яти](root:sys-plang-cpp/rule-of-five-zero) тут читається буквально: переміщення забирає handle й лишає в джерелі порожній, деструктор нищить.

**Читання після кінця.** Коли `done()` уже `true`, `*it` віддасть посилання на тимчасовий, який давно помер, а `++it` покличе `resume()` на корутині, що стоїть на фінальній точці. Останнє — невизначена поведінка прямо за передумовою `coroutine_handle::resume`: «корутина не призупинена у своїй фінальній точці». Наш `operator==` захищає штатний цикл `for`, але ітератор, збережений «на потім», нічого не захищає.

**Одноразовість.** Це вхідний ітератор і одноразовий діапазон: другий `begin()` не почне спочатку, а з'їсть іще один елемент. Про такі діапазони варто пам'ятати всюди, де вживають [категорії ітераторів](root:sys-plang-cpp/iterators-model), — алгоритм, що проходить дані двічі, тут просто не працює.

**Немає вкладених `co_yield`.** Віддати з генератора інший генератор одним рядком не вийде — доведеться писати `for (const T& x : inner) co_yield x;`. Це не лише синтаксично довше: обхід дерева глибиною `d` коштуватиме `d` відновлень на кожен елемент, бо значення пропихається через усі проміжні кадри вручну.

## Ціна

Один виклик генератора — одне виділення пам'яті під кадр (компілятор має право його усунути, але не зобов'язаний). Далі кожен елемент коштує два непрямі переходи: `resume()` стрибає в потрібний сегмент тіла, `co_yield` повертає керування назад. Ні виділень, ні копій значення на елемент немає — тому лінива обробка мільйона рядків тримає в пам'яті рівно один рядок.

## Чим це відрізняється від `std::generator`

Готовий тип у стандарті з'явився в C++23 — заголовок `<generator>`, папір P2502 (Кейсі Картер, Microsoft). Наш саморобний накриває його ядро, але поступається в трьох речах.

Він **вміє вкладені генератори**: `co_yield std::ranges::elements_of(rng)` віддає весь піддіапазон, і механіка тримає всередині стос активних кадрів, передаючи керування прямо в найглибший. Обхід дерева коштує одне відновлення на елемент замість `d`.

Він **є `view`** і тому вставляється в [конвеєри ranges](root:sys-plang-cpp/ranges-pipelines) без обгорток. Наш тип моделює `input_range`, але не `view`: для цього бракує успадкування від `view_interface` й позначки `enable_view`.

Він **розрізняє тип посилання й тип значення** (`std::generator<Ref, V, Allocator>`) і має алокатор у параметрах — звідси й `std::pmr::generator` для кадрів із пулу.

Спільним лишається головне: `std::generator` теж суто синхронний, `co_await` у ньому немає, і всі чотири пастки вище чинні для нього так само. Практично його стримує хіба підтримка — libstdc++ має його з GCC 14, MSVC STL — із Visual Studio 2022 17.13, а libc++ на час письма не реалізувала. Докладніше — у [std::generator](root:sys-plang-cpp/std-generator).
