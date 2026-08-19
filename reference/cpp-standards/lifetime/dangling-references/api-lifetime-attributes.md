# 📋 Атрибути часу життя та прапорці діагностики компилятора

У класичному C++ сигнатура функції повідомляє типи параметрів та категорію повертаного значення, але нічого не каже компілятору про те, як довго житиме повернене посилання і від якого саме з вхідних аргументів воно залежить. Коли функція повертає `const std::string&` або `std::string_view`, компілятор не має формальних підстав пов'язувати час життя результату з часом життя переданого аргументу поза межами аналізу локального тіла функції.

Атрибути контрактів часу життя (англ. *lifetime contracts*) та прапорці статичного аналізу розв'язують цю фундаментальну проблему: вони переносять інваріанти володіння та запозичення безпосередньо в інтерфейс функції. Це дозволяє статичному аналізатору компілятора перевіряти ланцюжки викликів між різними одиницями трансляції та ловити висячі посилання під час складання проекту без залучення важких динамічних санітайзерів.

## Механізм аналізу часу життя в компіляторі (Lifetime Origin Tracking)

Для того щоб зрозуміти, як працюють атрибути, розгляньмо внутрішню модель, яку будує компілятор (зокрема Clang та MSVC). Під час аналізу виразу компілятор створює граф походження (англ. *origin graph*):

1. **Джерело (Origin)**: кореневий об'єкт, який володіє пам'яттю (локальна змінна, член класу або матеріалізований тимчасовий об'єкт `prvalue`). Джерело має чітко визначену область видимості або межу повного виразу.
2. **Запозичення (Borrow/Reference)**: посилання, вказівник або невласницький тип-в'ювер, що вказує на джерело чи його підоб'єкт.
3. **Розповсюдження (Propagation)**: правила, за якими запозичення передається через виклики функцій. За замовчуванням компілятор вважає, що повернене з функції посилання не залежить від вхідних параметрів (консервативне припущення). Атрибут `[[clang::lifetimebound]]` вказує компілятору додати ребро залежності від джерела параметра до поверненого результату.

Якщо в графі виявляється ребро, де запозичення зберігається в змінній, чий час життя перевищує час життя відповідного джерела (наприклад, посилання зберігається в локальній змінній, а джерело було тимчасовим об'єктом і померло на крапці з комою), компілятор негайно формує діагностичне повідомлення про дефект.

## Атрибут `[[clang::lifetimebound]]`

Атрибут `[[clang::lifetimebound]]` (підтримується Clang з версії 7.0, MSVC під назвою `[[msvc::lifetimebound]]`, та входить до стандартних пропозицій комітету стандартизації ISO C++) вказує компілятору, що повернене функцією посилання або невласницький в'ювер (як-от `std::string_view`, `std::span` чи користувацький ітератор) запозичує пам'ять у позначеного параметра або неявного об'єкта `*this`.

Якщо джерело, з якого запозичено ресурс, є тимчасовим і знищується наприкінці повного виразу, компілятор видає попередження `-Wdangling` або `-Wdangling-gsl` при спробі зберегти повернене посилання.

### Анотація функцій-членів (запозичення з `*this`)

Коли функція-член повертає посилання на внутрішнє поле або в'ювер на внутрішній буфер, її обов'язково слід позначити атрибутом:

```cpp
#include <string>
#include <string_view>

class UserProfile {
    std::string nickname_;
    std::string email_;
public:
    UserProfile(std::string nick, std::string mail)
        : nickname_(std::move(nick)), email_(std::move(mail)) {}

    // Повертає посилання, що прив'язане до часу життя об'єкта UserProfile
    const std::string& get_nickname() const [[clang::lifetimebound]] {
        return nickname_;
    }

    // Повертає view, прив'язаний до часу життя *this
    std::string_view get_email_view() const [[clang::lifetimebound]] {
        return email_;
    }
};
```

Тепер, якщо користувач викличе метод на тимчасовому об'єкті, компілятор негайно виявить дефект:

```cpp
UserProfile fetch_user();

// Помилка під час компіляції: тимчасовий UserProfile гине на ';',
// а посилання ref_nick лишається висячим!
const std::string& ref_nick = fetch_user().get_nickname(); // warning: temporary bound to local reference

// Помилка: view вказує на зруйнований рядок тимчасового об'єкта
std::string_view view_mail = fetch_user().get_email_view(); // warning: temporary whose address is used as value of local variable
```

### Анотація вільних функцій і шаблонів

Атрибут можна застосовувати до окремих параметрів вільних функцій, перевантажених операторів та конструкторів класів-обгорток:

```cpp
#include <string>
#include <string_view>

// Функція повертає посилання на один із двох переданих аргументів
template <typename T>
const T& custom_min(const T& a [[clang::lifetimebound]], 
                    const T& b [[clang::lifetimebound]]) {
    return (b < a) ? b : a;
}

// Конструктор в'ювера, що запозичує буфер у контейнера
template <typename T>
class MySpan {
    const T* data_;
    size_t size_;
public:
    template <typename Container>
    MySpan(const Container& c [[clang::lifetimebound]])
        : data_(c.data()), size_(c.size()) {}
};
```

Перевірка коректності викликів:

```cpp
std::string make_temp();
std::string persistent = "permanent";

// Попередження компілятора: custom_min може повернути посилання на тимчасовий об'єкт!
const std::string& chosen = custom_min(persistent, make_temp());

// Попередження компілятора: MySpan запозичує буфер у тимчасового контейнера
MySpan<char> span = std::string("temporary text");
```

### Анотація ланцюжкових викликів (Fluent API та Builder Pattern)

У патернах побудови об'єктів (Builder) або текучих інтерфейсах (Fluent API) методи зазвичай повертають посилання `Builder&` на самих себе (`return *this;`). Якщо такий ланцюжок викликається над тимчасовим об'єктом Builder, проміжне посилання може вислизнути назовні:

```cpp
#include <string>
#include <vector>

class QueryBuilder {
    std::string query_;
public:
    QueryBuilder& add_filter(std::string_view f) [[clang::lifetimebound]] {
        query_ += " WHERE " + std::string(f);
        return *this;
    }

    QueryBuilder& set_limit(int limit) [[clang::lifetimebound]] {
        query_ += " LIMIT " + std::to_string(limit);
        return *this;
    }

    std::string build() const {
        return query_;
    }
};

void run() {
    // Безпечно: виклик build() повертає значення std::string за значенням до кінця повного виразу
    std::string q = QueryBuilder{}.add_filter("active=1").set_limit(10).build();

    // Небезпечно: збереження посилання на проміжний тимчасовий Builder
    // Завдяки [[clang::lifetimebound]] компілятор видасть попередження
    QueryBuilder& builder_ref = QueryBuilder{}.add_filter("active=1"); // warning: temporary bound to reference
}
```

## Атрибут `[[clang::lifetime_capture_by(X)]]`

Починаючи з версії Clang 18, додано спеціалізований атрибут `[[clang::lifetime_capture_by(X)]]`, який моделює ситуації зворотного запозичення: коли функція не повертає посилання негайно, а поглинає переданий аргумент всередину іншого існуючого об'єкта (наприклад, додає вказівник у внутрішню чергу, контейнер чи замикання обробника подій).

Синтаксис дозволяє явно вказати ім'я цільового параметра-власника, який захоплює посилання:

```cpp
#include <vector>
#include <string_view>

struct EventSink {
    std::vector<std::string_view> subscribers;

    // Вказує, що метод зберігає view всередині об'єкта 'this'
    void subscribe(std::string_view sv [[clang::lifetime_capture_by(this)]]) {
        subscribers.push_back(sv);
    }
};

void register_events(EventSink& sink) {
    std::string temp_event = "on_network_timeout";
    sink.subscribe(temp_event); 
    // warning: object backing 'temp_event' captured by 'sink' will be destroyed on scope exit, leaving dangling view in 'sink'
}
```

Якщо `EventSink` живе довше за функцію `register_events`, компілятор попередить, що внутрішній вектор `subscribers` отримав недійсне посилання на стек.

## Анотації C++ Core Guidelines Lifetime Profile

Проект **Lifetime Profile** (розроблений Гербом Саттером та Б'ярном Страуструпом) формалізує правила безпеки пам'яті для C++ через систему контрактів. Специфікація розділяє всі типи на дві взаємодоповнюючі категорії:

1. **Власник (Owner)**: тип, який володіє виділеним ресурсом і відповідає за його своєчасне звільнення за семантикою RAII (`std::unique_ptr`, `std::shared_ptr`, `std::vector`, `std::string`, файлові дескриптори).
2. **Вказівник / В'ювер (Pointer)**: тип, який не володіє ресурсом, а лише надає тимчасовий доступ до нього (`T*`, `T&`, `std::string_view`, `std::span`, ітератори `std::vector::iterator`).

Бібліотека GSL (Guidelines Support Library) та інструменти аналізу надають відповідні атрибути для явного декларування ролі користувацьких класів:

```cpp
#include <gsl/gsl>

// Декларуємо власника ресурсу
template <typename T>
class [[gsl::Owner(T)]] CustomBuffer {
    T* data_;
    size_t size_;
public:
    CustomBuffer(size_t n) : data_(new T[n]), size_(n) {}
    ~CustomBuffer() { delete[] data_; }
};

// Декларуємо невласницький в'ювер
template <typename T>
class [[gsl::Pointer(T)]] CustomBufferView {
    const T* ptr_;
    size_t size_;
public:
    CustomBufferView(const CustomBuffer<T>& buf) 
        : ptr_(buf.data()), size_(buf.size()) {}
};
```

Коли компілятор або статичний аналізатор (MSVC Lifetime Checker чи Clang static analyzer) обробляє класи, помічені цими атрибутами, він застосовує такі суворі правила:
1. Заборонено створювати об'єкт-Pointer від тимчасового об'єкта-Owner поза межами повного виразу.
2. Повернення Pointer із функції, що приймає Owner за значенням, позначається як висячий стан.
3. Будь-яка мутація цільового об'єкта Owner (наприклад, виклик неконстантного методу) автоматично інвалідує всі пов'язані з ним активні об'єкти Pointer у поточній області видимості.

## Повний звід прапорців діагностики компіляторів

У таблиці наведено всі ключові прапорці компіляторів GCC, Clang та MSVC, які відповідають за виявлення висячих посилань і часу життя об'єктів:

| Прапорець компілятора | Компілятор | Призначення та тип дефекту | Рівень небезпеки |
|---|---|---|---|
| `-Wdangling` | Clang 13+, GCC 13+ | Базовий прапорець для перевірки висячих посилань і тимчасових об'єктів | Високий (вмикається за `-Wall`) |
| `-Wreturn-stack-address` | Clang, GCC | Виявляє пряме повернення вказівника або посилання на локальну змінну | Критичний (помилка або суворе попередження) |
| `-Wdangling-gsl` | Clang 10+ | Перевірка висячих посилань у класах GSL, `std::string_view`, `std::span` | Критичний |
| `-Wdangling-field` | Clang 12+ | Ініціалізація посилання-члена класу тимчасовим об'єктом у конструкторі | Критичний |
| `-Wdangling-initializer-list` | Clang 10+, GCC 11+ | Збереження або повернення масиву-підкладки `std::initializer_list` | Критичний |
| `-Wreturn-local-addr` | GCC | Діагностика повернення адреси локальної стекової змінної в C/C++ | Критичний |
| `-Wrange-loop-construct` | Clang | Попереджає про створення небажаної копії чи висячого посилання у `for (auto&& x : ...)` | Середній |
| `/analyze` | MSVC | Вмикає вбудований статичний аналізатор MSVC | Високий |
| `/analyze:plugin EspXEngine.dll` | MSVC | Активує C++ Core Guidelines Lifetime Checker у середовищі Visual Studio | Критичний |

## Підтримка атрибутів у стандартній бібліотеці (Standard Library Adoption)

Починаючи зі стандартів C++20 та C++23, розробники стандартних бібліотек (LLVM `libc++`, GNU `libstdc++`, Microsoft STL) активно впроваджують атрибути часу життя всередину стандартних заголовків.

Ось ключові стандартні функції та методи, які вже містять атрибут `[[clang::lifetimebound]]` у сучасних версіях компіляторів:

1. **Алгоритми вибору**: `std::min`, `std::max`, `std::clamp` — анотовані для запобігання зв'язуванню з результатом, якщо хоча б один аргумент є тимчасовим.
2. **Невласницькі типи-в'ювери**: конструктори `std::string_view(const std::string&)` та `std::span(const Container&)` позначені для блокування створення в'юверів над тимчасовими контейнерами.
3. **Методи доступу до елементів**: `std::vector::operator[]`, `std::vector::front()`, `std::vector::back()`, `std::vector::data()`, `std::string::c_str()`, `std::string::data()`.
4. **Контейнери значень-обгорток**: `std::optional::operator*()`, `std::optional::value()`, `std::expected::value()`.
5. **Кортежі та пари**: `std::get<I>(std::pair&)`, `std::get<I>(std::tuple&)`.

Завдяки цьому навіть звичайний код без явних анотацій з боку розробника отримує повноцінний статичний контроль часу життя при використанні стандартних компонентів.

## Практична таблиця контрактів і поведінки компілятора

Порівняймо, як компілятор реагує на різні форми використання функцій за наявності та відсутності атрибутів:

| Сигнатура та виклик | Без атрибутів | З `[[clang::lifetimebound]]` | Рекомендована дія |
|---|---|---|---|
| `const T& f(const T& a);`<br>`const T& r = f(T{});` | Мовчазна компіляція (UB під час виконання) | Попередження: `temporary bound to local reference` | Повертати значення за копією/переміщенням або приймати `T` за значенням |
| `string_view(const string& s);`<br>`string_view sv = string("abc");` | Clang частково ловить через хардкод для `std::string_view` | Гарантоване попередження для будь-яких користувацьких класів | Оголошувати параметр конструктора в'ювера з `[[clang::lifetimebound]]` |
| `auto&& x = make_struct().member_ref;` | Тимчасовий об'єкт живе до кінця повного виразу, `x` висне | Попередження `binding reference to member of temporary` | Використовувати пряме значення `auto x = ...` |
| `auto&& x = make_vec()[0];` | Мовчазне проходження (виклик функції ламає подовження) | Попередження при анотації `operator[]` | Зберігати весь контейнер у локальній змінній |

## Інтеграція статичного аналізу в Clang-Tidy

Окрім прямих прапорців компіляції, потужний статичний аналіз надає утиліта **Clang-Tidy**. Вона включає спеціалізовані модулі перевірки життєвого циклу:

- **`bugprone-dangling-handle`**: знаходить випадки, коли невласницькі об'єкти (`std::string_view`, `std::span`) ініціалізуються тимчасовими об'єктами або коли функція повертає в'ювер на локальну змінну.
- **`bugprone-use-after-move`**: перевіряє використання об'єктів після того, як їхній стан було переміщено через `std::move`.
- **`cppcoreguidelines-pro-type-member-init`**: перевіряє гарантовану ініціалізацію посилань-членів у конструкторах.
- **`cppcoreguidelines-avoid-capturing-lambda-coroutines`**: забороняє захоплення локальних змінних за посиланням у корутинах (`co_await`, `co_yield`), оскільки корутина гарантовано переживе стек виклику.

Приклад конфігураційного файлу `.clang-tidy` для проекту з високими вимогами до безпеки пам'яті:

```yaml
Checks: >
  -*,
  bugprone-dangling-handle,
  bugprone-use-after-move,
  cppcoreguidelines-pro-type-member-init,
  cppcoreguidelines-avoid-capturing-lambda-coroutines,
  clang-analyzer-cplusplus.Move,
  clang-analyzer-core.uninitialized.*
WarningsAsErrors: 'bugprone-dangling-handle,bugprone-use-after-move'
```

## Рекомендації щодо впровадження у виробничі кодові бази

1. **Позначайте всі власні класи-в'ювери**: якщо ваш проект реалізує аналоги `std::span`, `std::string_view`, ітератори або легковагі обгортки матриць/буферів, їхні конструктори від контейнерів обов'язково повинні містити `[[clang::lifetimebound]]`.
2. **Анотуйте методи доступу (Getters)**: усі методи, що повертають `const Field&` або невласницький в'ювер на внутрішні дані класу, слід позначати `[[clang::lifetimebound]]`.
3. **Увімкніть `-Werror=return-stack-address` та `-Werror=dangling` у прапорцях компіляції**: це гарантує, що жодне очевидне висяче посилання не пройде етап збірки на CI/CD сервері.
4. **Використовуйте Clang-Tidy як автоматичний лінтер під час створення Pull Request**: автоматична перевірка правил Core Guidelines відсікає потенційні витоки посилань ще на етапі рецензування коду.
