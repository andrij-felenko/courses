# ⚙️ Практикум: портативна перевірка можливостей і поліфіли у C++

При розробці кросплатформних бібліотек і довгоживучих програмних комплексів інженери неминуче стикаються з неоднорідним оточенням компіляції: один розробник працює на свіжій версії Clang під macOS, сервер безперервної інтеграції (CI) збирає образи за допомогою стабільного GCC у середовищі Linux, а корпоративний реліз вимагає складання під Windows за допомогою MSVC. Оскільки підтримка нововведень стандартів впроваджується виробниками компіляторів поступово, нерівномірно і незалежно між синтаксичним аналізатором ядра та стандартною бібліотекою STL, пряма прив'язка сирцевого коду до макросів версій компіляторів (`_MSC_VER >= 1930` чи `__GNUC__ >= 11`) швидко перетворює кодову базу на крихку систему несумісних умовних блоків.

У цьому практикумі розібрано повний цикл побудови надійної системи перевірки можливостей (англ. *Feature Detection System*) на базі стандартного заголовка `<version>` та офіційних макросів робочої групи WG21 SD-6. На детальних прикладах продемонстровано створення чистих поліфілів для синтаксичних конструкцій ядра мови (концепти, багатовимірний оператор індексації C++23), типів і функцій стандартної бібліотеки (`std::expected`, `std::span`, `std::format`, `std::jthread`, `std::to_underlying`, `std::bit_cast`), алгоритмічних конвеєрів діапазонів та платформозалежних атрибутів оптимізації пам'яті.

## 1. Чому перевірка за версіями компіляторів є дефектною

Традиційний підхід до умовної компіляції у старих C++ проєктах спирався на ручну перевірку ідентифікаторів компіляторів та макроса версії стандарту `__cplusplus`:

```cpp
// Антипатерн: крихка перевірка за версіями трансляторів
#if defined(__clang__) && (__clang_major__ >= 13)
    #define USE_CONCEPTS 1
#elif defined(__GNUC__) && (__GNUC__ >= 10)
    #define USE_CONCEPTS 1
#elif defined(_MSC_VER) && (_MSC_VER >= 1928)
    #define USE_CONCEPTS 1
#else
    #define USE_CONCEPTS 0
#endif
```

Цей підхід виглядає простим лише на перший погляд, але містить чотири критичні архітектурні вади, які призводять до неочікуваних падінь збірки на реальних машинах:

1. **Розбіжність нумерації версій (Apple Clang проти LLVM Clang):** Apple використовує власну схему випуску версій Xcode Clang. Версія Apple Clang 14.0 базується на розгалуженні LLVM Clang 14.0, але містить інші набори виправлень дефектів та власні затримки увімкнення компонентів бібліотеки libc++. Перевірка `__clang_major__ >= 14` спрацьовує і для LLVM, і для Apple Clang, проте поведінка компіляторів суттєво відрізняється.
2. **Розрив між версією фронтенду та версією стандартної бібліотеки:** у середовищі Linux ви можете скомпілювати код найновішою версією Clang 17, але Clang за замовчуванням використає системну бібліотеку GNU `libstdc++`, встановлену в операційній системі. Якщо операційна система — це дистрибутив Ubuntu 20.04 LTS з пакетом `libstdc++` від GCC 9, компілятор успішно розпізнає синтаксис концептів ядра, але заголовок `<concepts>` чи `<format>` буде фізично відсутній на диску. Жодна перевірка версії компілятора не здатна передбачити такий стан.
3. **Експериментальні прапорці та робочі чернетки:** коли розробник збирає проєкт із прапорцем `-std=c++2a` чи `-std=c++2b`, компілятор підтримує лише частину запланованого стандарту. Номер версії компілятора залишається незмінним, проте набір діючих можливостей залежить виключно від того, які саме папери WG21 уже інтегровані в поточний реліз.
4. **Застаріле значення `__cplusplus` у MSVC:** компілятор Visual C++ (`cl.exe`) за замовчуванням визначає `__cplusplus` як `199711L` заради сумісності з величезними масивами застарілого корпоративного коду. Без обов'язкового прапорця `/Zc:__cplusplus` будь-яка стандартна перевірка `#if __cplusplus >= 202002L` вважає сучасний MSVC компілятором стандарту C++98.

## 2. Стандартизований механізм перевірки: заголовок `<version>`

Щоб назавжди позбутися перевірок версій компіляторів, комітет WG21 стандартизував механізм Feature Test Macros (документ SD-6, пізніше інкорпорований у C++20). Усі макроси можливостей повертають дату у форматі цілого числа `YYYYMML`, що відповідає місяцю й року офіційного прийняття резолюції робочою групою ISO.

Заголовок `<version>` — це спеціалізований автономний заголовочний файл мови C++20. Він не декларує жодних класів, шаблонів, функцій чи змінних. Його призначення — миттєво оголосити всі макроси перевірки бібліотеки (`__cpp_lib_*`), не додаючи накладних витрат на парсинг великих файлів на кшталт `<iostream>` чи `<algorithm>`.

Для безпечної підтримки старих інструментів заголовок `<version>` підключається за допомогою перевірки наявності файлу `__has_include`:

```cpp
// compat/version_check.hpp
#pragma once

// Безпечне зондування наявності автономного заголовка <version>
#if defined(__has_include)
    #if __has_include(<version>)
        #include <version>
    #endif
#endif
```

Цей мінімальний файл гарантує, що якщо ми працюємо в середовищі C++20 або новішому, всі макроси стану бібліотеки будуть визначені, а для старіших стандартів компілятор просто продовжить трансляцію без зупинки.

### Еволюція значень ключових макросів можливостей

Кожне нове розширення стандарту оновлює числове значення відповідного макроса. Наприклад, макрос `__cpp_constexpr` розвивався таким чином:
- `200704L` (C++11): базові `constexpr`-функції з одним оператором `return` та літеральні типи.
- `201304L` (C++14): цикли `for`/`while`, розгалуження `if` та локальні змінні всередині `constexpr`-функцій.
- `201603L` (C++17): використання лямбда-виразів у `constexpr` та `constexpr if`.
- `201907L` (C++20): виділення динамічної пам'яті (`std::vector`, `std::string`) під час компіляції, віртуальні виклики та `try/catch`.
- `202110L` (C++23): неініціалізовані змінні та послаблені вимоги до типів у `constexpr`.

Порівнюючи макрос зі значенням конкретної дати (`#if __cpp_constexpr >= 201907L`), розробник перевіряє саме ту функціональність, яка потрібна для конкретного алгоритму.

Також стандартна бібліотека оновлює макрос `__cpp_lib_ranges`:
- `201911L` (C++20): базові діапазони, концептуальні ітератори та первинний набір адаптерів (`std::views::filter`, `std::views::transform`).
- `202110L` та `202207L` (C++23): додавання конвеєрів для генерації послідовностей (`std::views::iota`, `std::views::chunk`, `std::views::slide`, `std::views::zip`).

## 3. Адаптація можливостей ядра: концепти C++20 проти SFINAE

Макрос ядра `__cpp_concepts` визначений як `201907L` у стандарті C++20. Він сигналізує, що компілятор повністю підтримує ключові слова `concept` та `requires`, вирази обмежень (англ. *Constraint Expressions*) та скорочений синтаксис обмежених шаблонів функцій.

Створимо утиліту для бінарної серіалізації `compat::serialize`. Для типів, які тривіально копіюються (`std::is_trivially_copyable`), ми виконуємо пряме швидке копіювання байтів пам'яті через покажчик, а для складних об'єктів викликаємо метод користувача `write_custom`:

```cpp
// compat/serialize_feature.hpp
#pragma once

#include <type_traits>
#include <cstring>
#include <vector>
#include <cstdint>

#include "version_check.hpp"

namespace compat {

#if defined(__cpp_concepts) && (__cpp_concepts >= 201907L)

    // Сучасна гілка C++20: декларативні концепти та клаузула requires
    template <typename T>
    concept TriviallyCopyable = std::is_trivially_copyable_v<T>;

    template <typename T>
    concept CustomSerializable = requires(const T& obj, std::vector<uint8_t>& buf) {
        obj.write_custom(buf);
    };

    // Перевантаження для тривіальних типів (висока продуктивність)
    template <TriviallyCopyable T>
    void serialize(const T& value, std::vector<uint8_t>& buffer) {
        const auto* byte_ptr = reinterpret_cast<const uint8_t*>(&value);
        buffer.insert(buffer.end(), byte_ptr, byte_ptr + sizeof(T));
    }

    // Перевантаження для користувацьких типів з методом write_custom
    template <CustomSerializable T>
        requires (!TriviallyCopyable<T>)
    void serialize(const T& value, std::vector<uint8_t>& buffer) {
        value.write_custom(buffer);
    }

#else

    // Запасна гілка C++14/C++17: метапрограмування SFINAE через std::enable_if_t
    template <typename T, std::enable_if_t<std::is_trivially_copyable<T>::value, int> = 0>
    void serialize(const T& value, std::vector<uint8_t>& buffer) {
        const auto* byte_ptr = reinterpret_cast<const uint8_t*>(&value);
        buffer.insert(buffer.end(), byte_ptr, byte_ptr + sizeof(T));
    }

    template <typename T, std::enable_if_t<!std::is_trivially_copyable<T>::value, int> = 0>
    void serialize(const T& value, std::vector<uint8_t>& buffer) {
        value.write_custom(buffer);
    }

#endif

} // namespace compat
```

Зверніть увагу: публічний інтерфейс `compat::serialize` залишається абсолютно ідентичним для користувача. Проте на компіляторі C++20 розробник отримує зрозумілі діагностичні повідомлення про порушення вимог концепту замість багатосторінкових розгорток помилок заміщення шаблонів SFINAE. Компілятор оцінює дерево концептів на ранньому етапі семантичного аналізу, уникаючи надмірного генерування тимчасових інстанціацій типів у таблиці символів, що значно прискорює час компіляції великих проєктів.

## 4. Багатовимірний оператор індексації C++23 проти класичного виклику

У C++23 з'явилася можливість передавати декілька аргументів безпосередньо в оператор квадратних дужок: `matrix[row, col]`. Цю можливість контролює макрос `__cpp_multidimensional_subscript >= 202110L`. До появи цього стандарту єдиним способом реалізувати індексацію з кількома вимірами без створення проміжних проксі-об'єктів було перевантаження круглого оператора виклику функції `operator()(row, col)`.

Розробимо клас двовимірної матриці `compat::Matrix2D`, який автоматично підтримує новий елегантний синтаксис індексації при збірці під C++23, зберігаючи сумісність з оператором `operator()(row, col)` для старіших версій:

```cpp
// compat/matrix.hpp
#pragma once

#include <vector>
#include <cstddef>
#include <stdexcept>

#include "version_check.hpp"

namespace compat {

template <typename T>
class Matrix2D {
public:
    Matrix2D(size_t rows, size_t cols)
        : rows_(rows), cols_(cols), data_(rows * cols) {}

    // Традиційний синтаксис виклику (доступний у всіх стандартах)
    T& operator()(size_t r, size_t c) {
        return data_[index(r, c)];
    }

    const T& operator()(size_t r, size_t c) const {
        return data_[index(r, c)];
    }

#if defined(__cpp_multidimensional_subscript) && (__cpp_multidimensional_subscript >= 202110L)
    // Сучасний синтаксис C++23: matrix[row, col]
    T& operator[](size_t r, size_t c) {
        return data_[index(r, c)];
    }

    const T& operator[](size_t r, size_t c) const {
        return data_[index(r, c)];
    }
#endif

    size_t rows() const noexcept { return rows_; }
    size_t cols() const noexcept { return cols_; }

private:
    size_t index(size_t r, size_t c) const {
        if (r >= rows_ || c >= cols_) {
            throw std::out_of_range("Matrix index out of bounds");
        }
        return r * cols_ + c;
    }

    size_t rows_;
    size_t cols_;
    std::vector<T> data_;
};

} // namespace compat
```

## 5. Поліфіл стандартної бібліотеки: `std::span` (C++20)

Тип `std::span<T>` надає неневолодіючий безпечний перегляд неперервної послідовності об'єктів у пам'яті (масив, вектор або сирий буфер), замінюючи небезпечні пари «покажчик + довжина». Макрос `__cpp_lib_span >= 202002L` сигналізує про готовність типу в STL. Він вирішує хронічну проблему безпеки коду C++, запобігаючи деградації типів масивів до сирих покажчиків (*Array-to-Pointer Decay*) та надаючи безпечний інтерфейс зрізів (*subspans*).

Якщо проєкт збирається у режимі C++14/C++17, ми надаємо власний легкий поліфіл `compat::span`:

```cpp
// compat/span.hpp
#pragma once

#include "version_check.hpp"

#if defined(__cpp_lib_span) && (__cpp_lib_span >= 202002L)

    #include <span>

    namespace compat {
        template <typename T, std::size_t Extent = std::dynamic_extent>
        using span = std::span<T, Extent>;
        inline constexpr std::size_t dynamic_extent = std::dynamic_extent;
    }

#else

    #include <cstddef>
    #include <stdexcept>
    #include <vector>
    #include <array>
    #include <type_traits>

    namespace compat {

        inline constexpr std::size_t dynamic_extent = static_cast<std::size_t>(-1);

        template <typename T, std::size_t Extent = dynamic_extent>
        class span {
        public:
            using element_type = T;
            using value_type = std::remove_cv_t<T>;
            using size_type = std::size_t;
            using pointer = T*;
            using const_pointer = const T*;
            using reference = T&;
            using const_reference = const T&;
            using iterator = T*;
            using const_iterator = const T*;

            constexpr span() noexcept : data_(nullptr), size_(0) {}
            constexpr span(pointer ptr, size_type count) noexcept : data_(ptr), size_(count) {}
            constexpr span(pointer first, pointer last) noexcept : data_(first), size_(last - first) {}

            template <std::size_t N>
            constexpr span(element_type (&arr)[N]) noexcept : data_(arr), size_(N) {}

            template <typename Alloc>
            span(std::vector<value_type, Alloc>& vec) noexcept : data_(vec.data()), size_(vec.size()) {}

            template <typename Alloc>
            span(const std::vector<value_type, Alloc>& vec) noexcept : data_(vec.data()), size_(vec.size()) {}

            constexpr pointer data() const noexcept { return data_; }
            constexpr size_type size() const noexcept { return size_; }
            constexpr size_type size_bytes() const noexcept { return size_ * sizeof(T); }
            constexpr bool empty() const noexcept { return size_ == 0; }

            constexpr reference operator[](size_type idx) const {
                return data_[idx];
            }

            constexpr iterator begin() const noexcept { return data_; }
            constexpr iterator end() const noexcept { return data_ + size_; }
            constexpr const_iterator cbegin() const noexcept { return data_; }
            constexpr const_iterator cend() const noexcept { return data_ + size_; }

            constexpr span<T, dynamic_extent> subspan(size_type offset, size_type count = dynamic_extent) const {
                if (offset > size_) {
                    throw std::out_of_range("subspan offset out of range");
                }
                size_type actual_count = (count == dynamic_extent || offset + count > size_) ? (size_ - offset) : count;
                return span<T, dynamic_extent>(data_ + offset, actual_count);
            }

        private:
            pointer data_;
            size_type size_;
        };

    } // namespace compat

#endif
```

## 6. Поліфіл стандартної бібліотеки: `std::expected` (C++23)

Тип `std::expected<T, E>` введено у стандарт C++23 для безпечного повернення результату або коду помилки без накладних витрат на розгортання стека винятків. Його наявність сигналізується макросом `__cpp_lib_expected >= 202202L`. У високонавантажених системах винятки створюють неприпустимі накладні витрати часу виконання через необхідність розгортання фреймів стека, тоді як `std::expected` розміщує значення або помилку в єдиному буфері пам'яті за принципом розміченого об'єднання (*tagged union*).

Якщо проєкт збирається у режимі C++17 або C++20, ми надаємо власний повноцінний поліфіл, побудований на базі `std::variant`:

```cpp
// compat/expected.hpp
#pragma once

#include "version_check.hpp"

#if defined(__cpp_lib_expected) && (__cpp_lib_expected >= 202202L)

    #include <expected>

    namespace compat {
        template <typename T, typename E>
        using expected = std::expected<T, E>;

        template <typename E>
        using unexpected = std::unexpected<E>;
    }

#else

    #include <variant>
    #include <utility>
    #include <stdexcept>

    namespace compat {

        template <typename E>
        class unexpected {
        public:
            constexpr explicit unexpected(const E& e) : error_(e) {}
            constexpr explicit unexpected(E&& e) : error_(std::move(e)) {}
            constexpr const E& error() const noexcept { return error_; }
            constexpr E& error() noexcept { return error_; }
        private:
            E error_;
        };

        template <typename T, typename E>
        class expected {
        public:
            constexpr expected(const T& val) : storage_(val) {}
            constexpr expected(T&& val) : storage_(std::move(val)) {}
            constexpr expected(const unexpected<E>& unexp) : storage_(unexp) {}
            constexpr expected(unexpected<E>&& unexp) : storage_(std::move(unexp)) {}

            constexpr bool has_value() const noexcept {
                return std::holds_alternative<T>(storage_);
            }

            constexpr explicit operator bool() const noexcept {
                return has_value();
            }

            constexpr const T& value() const {
                if (!has_value()) {
                    throw std::runtime_error("Attempt to access value of unexpected result");
                }
                return std::get<T>(storage_);
            }

            constexpr const E& error() const {
                return std::get<unexpected<E>>(storage_).error();
            }

            constexpr const T& value_or(const T& default_val) const noexcept {
                return has_value() ? std::get<T>(storage_) : default_val;
            }

        private:
            std::variant<T, unexpected<E>> storage_;
        };

    } // namespace compat

#endif
```

## 7. Поліфіл та міст форматування: `std::format` (C++20) проти fallback

Бібліотека форматування `std::format` (макрос `__cpp_lib_format >= 201907L`) надає типобезпечне, швидке та розширюване форматування рядків з підтримкою перевірки рядка формату під час компіляції за допомогою `consteval`-конструкторів `std::format_string<Args...>`. На відміну від небезпечної функції `printf`, де невідповідність специфікатора `%d` типу `int64_t` призводить до невизначеної поведінки, `std::format` витягує типи аргументів автоматично через варіативні шаблони.

Якщо `std::format` недоступний у стандартній бібліотеці платформи, ми будуємо міст: якщо в проєкті доступна бібліотека `{fmt}`, використовуємо її; якщо ні — відкочуємося до легкого форматувача на базі `std::ostringstream`:

```cpp
// compat/format.hpp
#pragma once

#include "version_check.hpp"

#if defined(__cpp_lib_format) && (__cpp_lib_format >= 201907L)

    #include <format>

    namespace compat {
        template <typename... Args>
        std::string format(std::format_string<Args...> fmt_str, Args&&... args) {
            return std::format(fmt_str, std::forward<Args>(args)...);
        }
    }

#else

    #include <string>
    #include <sstream>
    #include <utility>

    namespace compat {

        inline void format_helper(std::ostringstream& ss, std::string_view fmt_str) {
            ss << fmt_str;
        }

        template <typename T, typename... Args>
        void format_helper(std::ostringstream& ss, std::string_view fmt_str, T&& val, Args&&... rest) {
            size_t pos = fmt_str.find("{}");
            if (pos != std::string_view::npos) {
                ss << fmt_str.substr(0, pos);
                ss << val;
                format_helper(ss, fmt_str.substr(pos + 2), std::forward<Args>(rest)...);
            } else {
                ss << fmt_str;
            }
        }

        template <typename... Args>
        std::string format(std::string_view fmt_str, Args&&... args) {
            std::ostringstream ss;
            format_helper(ss, fmt_str, std::forward<Args>(args)...);
            return ss.str();
        }

    } // namespace compat

#endif
```

## 8. Поліфіл потоків з підтримкою скасування: `std::jthread` (C++20)

Клас `std::jthread` (макрос `__cpp_lib_jthread >= 201911L`) автоматично приєднує потік у деструкторі (RAII) та надає вбудований механізм кооперативного переривання через `std::stop_token`. Традиційний клас `std::thread` мови C++11 мав фатальний недолік дизайну: якщо розробник забував явно викликати `join()` або `detach()`, деструктор `~std::thread()` негайно викликав `std::terminate()`, аварійно завершуючи роботу всього процесу. Клас `std::jthread` повністю усуває цю проблему.

Для компіляторів C++14/C++17 створимо клас `compat::jthread` на базі `std::thread`:

```cpp
// compat/jthread.hpp
#pragma once

#include "version_check.hpp"

#if defined(__cpp_lib_jthread) && (__cpp_lib_jthread >= 201911L)

    #include <thread>

    namespace compat {
        using jthread = std::jthread;
        using stop_token = std::stop_token;
        using stop_source = std::stop_source;
    }

#else

    #include <thread>
    #include <atomic>
    #include <memory>
    #include <utility>

    namespace compat {

        class stop_source;

        class stop_token {
        public:
            stop_token() noexcept : flag_(nullptr) {}
            explicit stop_token(const std::atomic<bool>* flag) noexcept : flag_(flag) {}

            bool stop_requested() const noexcept {
                return flag_ && flag_->load(std::memory_order_relaxed);
            }

        private:
            const std::atomic<bool>* flag_;
        };

        class stop_source {
        public:
            stop_source() : flag_(false) {}

            stop_token get_token() const noexcept {
                return stop_token(&flag_);
            }

            bool request_stop() noexcept {
                return !flag_.exchange(true, std::memory_order_relaxed);
            }

        private:
            std::atomic<bool> flag_;
        };

        class jthread {
        public:
            jthread() noexcept = default;

            template <typename Function, typename... Args>
            explicit jthread(Function&& f, Args&&... args) {
                stop_source_ = std::make_unique<stop_source>();
                thread_ = std::thread(std::forward<Function>(f), stop_source_->get_token(), std::forward<Args>(args)...);
            }

            ~jthread() {
                if (joinable()) {
                    request_stop();
                    join();
                }
            }

            jthread(jthread&&) noexcept = default;
            jthread& operator=(jthread&&) noexcept = default;

            bool joinable() const noexcept { return thread_.joinable(); }
            void join() { thread_.join(); }
            void detach() { thread_.detach(); }

            bool request_stop() noexcept {
                return stop_source_ ? stop_source_->request_stop() : false;
            }

            stop_token get_stop_token() const noexcept {
                return stop_source_ ? stop_source_->get_token() : stop_token();
            }

        private:
            std::unique_ptr<stop_source> stop_source_;
            std::thread thread_;
        };

    } // namespace compat

#endif
```

## 9. Утиліти `std::to_underlying` (C++23) та `std::bit_cast` (C++20)

Дві надзвичайно корисні утиліти нових стандартів:
1. `std::to_underlying(e)` (C++23, `__cpp_lib_to_underlying >= 202102L`): перетворює значення перелічення `enum class` на його базовий цілочисельний тип без потреби ручного виписування `static_cast<std::underlying_type_t<E>>(e)`. Це значно покращує читабельність коду в системних мережевих протоколах та драйверах апаратного забезпечення.
2. `std::bit_cast<To>(from)` (C++20, `__cpp_lib_bit_cast >= 201806L`): виконує типобезпечну переінтерпретацію бітів пам'яті однакового розміру з підтримкою обчислень у `constexpr`. Традиційні трюки через C-приведення покажчиків `*(To*)&from` чи використання `union` є грубим порушенням правила суворого аліасингу (*Strict Aliasing Rule*) у мові C++ і спричиняють невизначену поведінку.

Реалізуємо їхній поліфіл:

```cpp
// compat/utilities.hpp
#pragma once

#include <type_traits>
#include <cstring>

#include "version_check.hpp"

namespace compat {

#if defined(__cpp_lib_to_underlying) && (__cpp_lib_to_underlying >= 202102L)
    using std::to_underlying;
#else
    template <typename Enum>
    constexpr std::underlying_type_t<Enum> to_underlying(Enum e) noexcept {
        return static_cast<std::underlying_type_t<Enum>>(e);
    }
#endif

#if defined(__cpp_lib_bit_cast) && (__cpp_lib_bit_cast >= 201806L)
    using std::bit_cast;
#else
    template <typename To, typename From>
    To bit_cast(const From& src) noexcept {
        static_assert(sizeof(To) == sizeof(From), "bit_cast types must have identical size");
        static_assert(std::is_trivially_copyable<To>::value, "To type must be trivially copyable");
        static_assert(std::is_trivially_copyable<From>::value, "From type must be trivially copyable");

        To dst;
        std::memcpy(&dst, &src, sizeof(To));
        return dst;
    }
#endif

} // namespace compat
```

## 10. Адаптивні конвеєри діапазонів (Ranges)

Бібліотека діапазонів C++20 дозволяє будувати ланцюжки лінивих трансформацій через оператор каналу `|` (наприклад, `vec | std::views::filter(pred) | std::views::transform(fn)`). Вона усуває необхідність створення тимчасових проміжних контейнерів `std::vector` між послідовними етапами фільтрації та перетворення даних.

Якщо макрос `__cpp_lib_ranges >= 201911L` не визначений, створюємо утиліти сумісності, які виконують аналогічні операції у жадібному (*eager*) режимі через стандартні ітератори та алгоритми:

```cpp
// compat/ranges.hpp
#pragma once

#include <vector>
#include <algorithm>

#include "version_check.hpp"

namespace compat {

#if defined(__cpp_lib_ranges) && (__cpp_lib_ranges >= 201911L)

    #include <ranges>

    namespace views {
        using namespace std::views;
    }

#else

    namespace views {

        template <typename Container, typename Predicate>
        auto filter(const Container& c, Predicate pred) {
            std::vector<typename Container::value_type> result;
            for (const auto& item : c) {
                if (pred(item)) {
                    result.push_back(item);
                }
            }
            return result;
        }

        template <typename Container, typename TransformFn>
        auto transform(const Container& c, TransformFn fn) {
            using OutType = decltype(fn(*std::begin(c)));
            std::vector<OutType> result;
            result.reserve(c.size());
            for (const auto& item : c) {
                result.push_back(fn(item));
            }
            return result;
        }

    } // namespace views

#endif

} // namespace compat
```

## 11. Портативні атрибути та особливості MSVC (`[[no_unique_address]]`)

Атрибути C++ перевіряються за допомогою вбудованого оператора препроцесора `__has_cpp_attribute`.

Стандартний атрибут C++20 `[[no_unique_address]]` вказує компілятору, що поле класу, яке має порожній тип (stateless allocator, deleter чи функтор), не зобов'язане займати окрему унікальну адресу в пам'яті. Це усуває необхідність застосування складного трюку оптимізації порожньої бази (Empty Base Optimization, EBO) через множинне успадкування.

Проте в компіляторі MSVC виникла критична колізія з двійковою сумісністю (ABI): розробники Windows SDK тривалий час розраховували на те, що всі поля структури мають ненульовий розмір. Щоб не зламати двійкову сумісність існуючих бібліотек, MSVC ігнорує стандартний атрибут `[[no_unique_address]]`, а для реальної оптимізації розміщення в пам'яті ввів власний атрибут `[[msvc::no_unique_address]]`.

Створимо портативний набір атрибутів:

```cpp
// compat/attributes.hpp
#pragma once

// Портативний атрибут оптимізації порожніх членів
#if defined(_MSC_VER) && !defined(__clang__)
    // Для компілятора MSVC використовуємо вендорний атрибут
    #define COMPAT_NO_UNIQUE_ADDRESS [[msvc::no_unique_address]]
#elif defined(__has_cpp_attribute)
    #if __has_cpp_attribute(no_unique_address) >= 201803L
        #define COMPAT_NO_UNIQUE_ADDRESS [[no_unique_address]]
    #else
        #define COMPAT_NO_UNIQUE_ADDRESS
    #endif
#else
    #define COMPAT_NO_UNIQUE_ADDRESS
#endif

// Портативний атрибут [[nodiscard]] з підтримкою текстового пояснення (C++20)
#if defined(__has_cpp_attribute)
    #if __has_cpp_attribute(nodiscard) >= 201907L
        #define COMPAT_NODISCARD_MSG(msg) [[nodiscard(msg)]]
        #define COMPAT_NODISCARD [[nodiscard]]
    #elif __has_cpp_attribute(nodiscard) >= 201603L
        #define COMPAT_NODISCARD_MSG(msg) [[nodiscard]]
        #define COMPAT_NODISCARD [[nodiscard]]
    #else
        #define COMPAT_NODISCARD_MSG(msg)
        #define COMPAT_NODISCARD
    #endif
#else
    #define COMPAT_NODISCARD_MSG(msg)
    #define COMPAT_NODISCARD
#endif
```

### Застосування у структурі оптимізації пам'яті

```cpp
// Приклад використання портативного атрибута
struct EmptyStatelessAllocator {};

template <typename T, typename Allocator = EmptyStatelessAllocator>
class CustomBuffer {
public:
    COMPAT_NODISCARD_MSG("Ignoring empty check result is likely a bug")
    bool empty() const noexcept {
        return size_ == 0;
    }

private:
    T* data_{nullptr};
    size_t size_{0};

    // Завдяки макросу розмір об'єкта не збільшується на 8 байтів вирівнювання у GCC, Clang та MSVC
    COMPAT_NO_UNIQUE_ADDRESS Allocator alloc_;
};
```

## 12. Інтеграція перевірки можливостей у CMake

Система збірки CMake дозволяє не лише задавати стандарт на рівні цілей, але й виконувати активні перевірки під час конфігурації проєкту за допомогою модуля `CheckCXXSourceCompiles`.

Це незамінно у випадках, коли заголовки бібліотеки формально присутні, але лінкер не знаходить двійкової реалізації (типова ситуація з `std::format` або `std::filesystem` на старіших версіях Clang та GNU `libstdc++`):

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(FeatureDetectionProject CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(CheckCXXSourceCompiles)

# Перевірка реальної наявності працездатного std::format у середовищі
check_cxx_source_compiles("
    #include <format>
    #include <string>
    int main() {
        std::string s = std::format(\"Test: {}\", 42);
        return s.empty() ? 1 : 0;
    }
" HAVE_STD_FORMAT)

add_executable(app main.cpp)

if(HAVE_STD_FORMAT)
    target_compile_definitions(app PRIVATE HAS_STD_FORMAT=1)
    message(STATUS "Native std::format is available and functional")
else()
    target_compile_definitions(app PRIVATE HAS_STD_FORMAT=0)
    message(STATUS "Native std::format is missing; linking external fmt library fallback")
    # find_package(fmt REQUIRED)
    # target_link_libraries(app PRIVATE fmt::fmt)
endif()

# Налаштування суворої діагностики
if(MSVC)
    target_compile_options(app PRIVATE /W4 /WX /permissive- /Zc:__cplusplus /Zc:preprocessor)
else()
    target_compile_options(app PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
```

## 13. Демонстраційний модуль перевірки працездатності

Об'єднаємо всі створені компоненти у фінальному файлі `main.cpp`, який демонструє автоматичну адаптацію коду до будь-якого компілятора:

```cpp
// main.cpp
#include <iostream>
#include <vector>
#include <string>
#include <chrono>

#include "compat/version_check.hpp"
#include "compat/serialize_feature.hpp"
#include "compat/matrix.hpp"
#include "compat/span.hpp"
#include "compat/expected.hpp"
#include "compat/format.hpp"
#include "compat/jthread.hpp"
#include "compat/utilities.hpp"
#include "compat/ranges.hpp"
#include "compat/attributes.hpp"

enum class Status : uint16_t {
    Ready = 1,
    Processing = 2,
    Failed = 3
};

struct UserData {
    uint32_t id;
    uint32_t flags;
};

compat::expected<UserData, std::string> parse_user(uint32_t raw_id) {
    if (raw_id == 0) {
        return compat::unexpected<std::string>("ID cannot be zero");
    }
    return UserData{raw_id, 0x01};
}

void print_buffer_span(compat::span<const uint8_t> buffer_view) {
    std::cout << "Span view of buffer (size=" << buffer_view.size() << "): ";
    for (auto byte : buffer_view) {
        std::cout << static_cast<int>(byte) << " ";
    }
    std::cout << "\n";
}

int main() {
    std::cout << "Compiler standard check: __cplusplus = " << __cplusplus << "\n";

#if defined(__cpp_concepts)
    std::cout << "Feature: __cpp_concepts = " << __cpp_concepts << " (Active)\n";
#else
    std::cout << "Feature: __cpp_concepts is not active (Using SFINAE fallback)\n";
#endif

#if defined(__cpp_lib_span)
    std::cout << "Library: __cpp_lib_span = " << __cpp_lib_span << " (Standard std::span)\n";
#else
    std::cout << "Library: Using compat::span polyfill\n";
#endif

#if defined(__cpp_lib_expected)
    std::cout << "Library: __cpp_lib_expected = " << __cpp_lib_expected << " (Standard std::expected)\n";
#else
    std::cout << "Library: Using compat::expected polyfill\n";
#endif

#if defined(__cpp_lib_jthread)
    std::cout << "Library: __cpp_lib_jthread = " << __cpp_lib_jthread << " (Standard std::jthread)\n";
#else
    std::cout << "Library: Using compat::jthread polyfill\n";
#endif

    // Тест форматування через міст compat::format
    std::string formatted_msg = compat::format("Formatted user info: id={}, active={}", 101, true);
    std::cout << formatted_msg << "\n";

    // Тест утиліти to_underlying
    auto status_val = compat::to_underlying(Status::Ready);
    std::cout << "Underlying status value: " << status_val << "\n";

    // Тест утиліти bit_cast
    float f_val = 1.0f;
    auto u_val = compat::bit_cast<uint32_t>(f_val);
    std::cout << "Bit cast of 1.0f to uint32: 0x" << std::hex << u_val << std::dec << "\n";

    // Тест серіалізації
    UserData user{101, 0xFF};
    std::vector<uint8_t> buffer;
    compat::serialize(user, buffer);
    std::cout << "Serialized buffer size: " << buffer.size() << " bytes\n";

    // Тест перегляду через span
    print_buffer_span(buffer);

    // Тест матриці та індексації
    compat::Matrix2D<int> mat(3, 3);
    mat(0, 0) = 42;
#if defined(__cpp_multidimensional_subscript)
    mat[1, 1] = 84;
    std::cout << "Matrix[1, 1] via C++23 subscript: " << mat[1, 1] << "\n";
#else
    std::cout << "Matrix(0, 0) via fallback call: " << mat(0, 0) << "\n";
#endif

    // Тест обробки помилок через expected
    auto result = parse_user(0);
    if (!result) {
        std::cout << "Handled expected error: " << result.error() << "\n";
    }

    // Тест кооперативного потоку jthread
    compat::jthread worker([](compat::stop_token st) {
        while (!st.stop_requested()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            break;
        }
    });
    worker.request_stop();

    return 0;
}
```

Така багатошарова архітектура гарантує, що кодова база проєкту завжди використовує найефективніші конструкції нових стандартів там, де вони готові, і коректно компілюється на старіших або консервативних платформах без ручного переписування бізнес-логіки.
