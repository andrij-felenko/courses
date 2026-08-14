# 📋 Інтерфейсна специфікація стандартних класів винятків C++

Стандартна бібліотека C++ надає розвинену та суворо впорядковану ієрархію зумовлених класів винятків. Вони розподілені за спеціалізованими заголовочними файлами: `<exception>`, `<stdexcept>`, `<system_error>`, `<new>`, `<typeinfo>`, `<optional>`, `<variant>`, `<any>`, `<future>`, `<format>`, `<filesystem>` та `<stacktrace>`.

Усі стандартні винятки успадковують від єдиного базового класу `std::exception`. Фундаментальний контракт передбачає надання віртуального методу `what()` для одержання текстового опису помилки та дотримання суворого специфікатора `noexcept` для всіх деструкторів і конструкторів копіювання, що унеможливлює виникнення повторних збоїв під час розгортання стеку.

---

## 1. Базовий клас std::exception (<exception>)

Клас `std::exception` виступає поліморфним корнем усієї ієрархії винятків стандартної бібліотеки C++. Він визначений у заголовочному файлі `<exception>`.

```cpp
namespace std {
    class exception {
    public:
        // Конструктори та деструктор
        exception() noexcept;
        exception(const exception& other) noexcept;
        exception& operator=(const exception& other) noexcept;
        virtual ~exception() noexcept;

        // Поліморфний доступ до текстового повідомлення про помилку
        virtual const char* what() const noexcept;
    };
}
```

### Члени класу та вимоги контракту:
- `exception()`: Створює базовий об'єкт винятку. Гарантує `noexcept` — не здійснює виділень пам'яті в купі.
- `virtual ~exception() noexcept`: Віртуальний деструктор. Забезпечує коректне очищення ресурсів похідних об'єктів при поліморфному видаленні через вказівник на базовий тип `std::exception*`.
- `virtual const char* what() const noexcept`: Повертає нуль-термінований рядок символів (`const char*`), що описує причину помилки. Повернений вказівник залишається дійсним принаймні до знищення об'єкта винятку або до виклику операторів присвоєння.

---

## 2. Логічні винятки (<stdexcept>): std::logic_error та похідні

Класи цієї групи описують помилки в логіці програми. Вони виникають у ситуаціях, які теоретично могли бути виявлені й відвернені на етапі проєктування або статичного аналізу коду (порушення прекондицій, передача некоректних аргументів, некоректний стан об'єкта).

### 2.1. std::logic_error
Базовий клас для всіх логічних помилок. Зберігає текстовий буфер повідомлення, переданий під час конструювання.

```cpp
namespace std {
    class logic_error : public exception {
    public:
        explicit logic_error(const string& what_arg);
        explicit logic_error(const char* what_arg);
        logic_error(const logic_error& other) noexcept;
        logic_error& operator=(const logic_error& other) noexcept;
        virtual ~logic_error() noexcept;
    };
}
```

### 2.2. Похідні класи std::logic_error

1. **`std::invalid_argument`**: Сигналізує про передачу некоректного аргументу у функцію (наприклад, передача від'ємного значення у функцію, що обчислює факторіал).
2. **`std::domain_error`**: Виникає при виході за межі математичної області визначення функції (наприклад, спроба обчислити логарифм або квадратний корінь від від'ємного числа у дійсних числах).
3. **`std::length_error`**: Сигналізує про спробу перевищити максимально допустимий розмір контейнера або масиву (перевищення межі `max_size()`).
4. **`std::out_of_range`**: Виникає при спробі доступу до елемента за межами допустимого діапазону індексів (наприклад, виклик `std::vector::at(index)` або `std::string::at(index)` з індексом, що перевищує `size() - 1`).
5. **`std::future_error` (<future>, C++11)**: Виникає при некоректній взаємодії з асинхронними об'єктами `std::future` або `std::promise` (наприклад, повторний запит результату з `future`). Надає спеціалізований метод `const error_code& code() const noexcept` для отримання деталізованого коду помилки `std::future_errc`.

---

## 3. Системні винятки виконання (<stdexcept>, <system_error>): std::runtime_error

Класи цієї групи описують помилки середовища виконання, які неможливо виявити статичним аналізом коду, оскільки вони залежать від зовнішніх ресурсів, стану операційної системи або фізичного обладнання.

### 3.1. std::runtime_error
Базовий клас для всіх помилок середовища виконання.

```cpp
namespace std {
    class runtime_error : public exception {
    public:
        explicit runtime_error(const string& what_arg);
        explicit runtime_error(const char* what_arg);
        runtime_error(const runtime_error& other) noexcept;
        runtime_error& operator=(const runtime_error& other) noexcept;
        virtual ~runtime_error() noexcept;
    };
}
```

### 3.2. Похідні класи std::runtime_error

1. **`std::range_error`**: Виникає при внутрішньому обчисленні результату, який виходить за межі допустимого діапазону результатів (range error у математичних алгоритмах).
2. **`std::overflow_error`**: Сигналізує про математичне переповнення верхньої межі типу даних (arithmetic overflow).
3. **`std::underflow_error`**: Сигналізує про математичне втрачання значущості під нижню межу типів із плаваючою крапкою (arithmetic underflow).
4. **`std::system_error` (<system_error>, C++11)**: Інтегрує винятки C++ із числовими кодами системних помилок операційної системи (`errno` в POSIX або `GetLastError()` у Win32 API).

```cpp
namespace std {
    class system_error : public runtime_error {
    public:
        system_error(error_code ec, const string& what_arg);
        system_error(error_code ec, const char* what_arg);
        system_error(error_code ec);
        system_error(int ev, const error_category& ecat, const string& what_arg);
        system_error(int ev, const error_category& ecat, const char* what_arg);
        system_error(int ev, const error_category& ecat);

        const error_code& code() const noexcept;
        virtual const char* what() const noexcept override;
    };
}
```

5. **`std::filesystem_error` (<filesystem>, C++17)**: Похідний від `std::system_error`. Інформує про помилки файлової системи та надає шляхи до проблемних файлів.

```cpp
namespace std::filesystem {
    class filesystem_error : public std::system_error {
    public:
        filesystem_error(const string& what_arg, error_code ec);
        filesystem_error(const string& what_arg, const path& p1, error_code ec);
        filesystem_error(const string& what_arg, const path& p1, const path& p2, error_code ec);

        const path& path1() const noexcept;
        const path& path2() const noexcept;
        virtual const char* what() const noexcept override;
    };
}
```

6. **`std::format_error` (<format>, C++20)**: Виникає при помилках форматування рядків через `std::format` або `std::print` (некоректний специфікатор формату).

---

## 4. Інтерфейси категорій системних помилок (<system_error>)

Для підтримки роботи `std::system_error` стандарт C++11 вводить допоміжні типи `std::error_category`, `std::error_code` та `std::error_condition`.

### 4.1. Специфікація класу std::error_category

```cpp
namespace std {
    class error_category {
    public:
        constexpr error_category() noexcept;
        virtual ~error_category() noexcept;

        error_category(const error_category&) = delete;
        error_category& operator=(const error_category&) = delete;

        // Назва категорії помилок
        virtual const char* name() const noexcept = 0;

        // Повертає текстовий опис коду помилки
        virtual string message(int ev) const = 0;

        // Зіставляє системний код із загальним кодом
        virtual error_condition default_error_condition(int ev) const noexcept;

        // Порівняння категорій
        bool operator==(const error_category& rhs) const noexcept;
        bool operator!=(const error_category& rhs) const noexcept;
    };

    // Глобальні функції-фабрики стандартних категорій
    const error_category& system_category() noexcept;
    const error_category& generic_category() noexcept;
    const error_category& iostream_category() noexcept;
    const error_category& future_category() noexcept;
}
```

### 4.2. Специфікація класу std::error_code

```cpp
namespace std {
    class error_code {
    public:
        error_code() noexcept;
        error_code(int val, const error_category& cat) noexcept;

        template<class ErrorCodeEnum>
        error_code(ErrorCodeEnum e) noexcept;

        void assign(int val, const error_category& cat) noexcept;
        void clear() noexcept;

        int value() const noexcept;
        const error_category& category() const noexcept;
        error_condition default_error_condition() const noexcept;
        string message() const;

        explicit operator bool() const noexcept;
    };
}
```

---

## 5. Винятки виділення пам'яті та низькорівневі збої (<new>, <typeinfo>)

Окремими заголовочними файлами визначаються спеціалізовані винятки, пов'язані з низькорівневим функціонуванням середовища виконання C++.

### 5.1. Винятки динамічної пам'яті (<new>)

- **`std::bad_alloc`**: Кидається оператором `operator new`, коли система не здатна виділити необхідний обсяг динамічної пам'яті в купі.
- **`std::bad_array_new_length` (C++11)**: Похідний від `std::bad_alloc`. Виникає при спробі виділення пам'яті під масив `new T[N]`, коли розмір `N` є від'ємним чи перевищує максимально допустимий ліміт реалізації.

```cpp
namespace std {
    class bad_alloc : public exception {
    public:
        bad_alloc() noexcept;
        bad_alloc(const bad_alloc&) noexcept;
        bad_alloc& operator=(const bad_alloc&) noexcept;
        virtual const char* what() const noexcept override;
    };

    class bad_array_new_length : public bad_alloc {
    public:
        bad_array_new_length() noexcept;
        virtual const char* what() const noexcept override;
    };
}
```

### 5.2. Винятки системи типів RTTI (<typeinfo>)

- **`std::bad_cast`**: Виникає при невдалій спробі приведення поліморфного типу через посилання `dynamic_cast<T&>(ref)`.
- **`std::bad_typeid`**: Виникає при спробі застосування оператора `typeid` до нульового вказівника на поліморфний тип (`typeid(*ptr)`, де `ptr == nullptr`).

---

## 6. Винятки безпечних контейнерних обгорток (C++11 / C++17)

З появою в стандартній бібліотеці Vocabulary Types у стандартах C++11 та C++17 було додано класи винятків для сигналізування про порушення контракту доступу до даних:

1. **`std::bad_optional_access` (<optional>, C++17)**: Кидається методом `std::optional::value()`, якщо екземпляр `std::optional` порожній.
2. **`std::bad_variant_access` (<variant>, C++17)**: Виникає при зверненні до значення `std::variant` через `std::get<T>(v)` або `std::visit`, якщо актуальний активний тип альтернативи не збігається з запитуваним `T`.
3. **`std::bad_any_cast` (<any>, C++17)**: Виникає при невдалій спробі витягнути вміст із `std::any` за допомогою `std::any_cast<T>(a)`.
4. **`std::bad_weak_ptr` (<memory>, C++11)**: Виникає при спробі сконструювати `std::shared_ptr` із простроченого екземпляра `std::weak_ptr` (`wp.expired() == true`).
5. **`std::bad_function_call` (<functional>, C++11)**: Кидається при спробі виклику порожнього об'єкта `std::function`, який не містить цільового функтора чи вказівника на функцію.

---

## 7. Механізми вкладених винятків та транспортування між потоками (<exception>)

Стандарт C++11 запровадив інтерфейси для керування винятками як розумними вказівниками та створення ланцюжків помилок.

### 7.1. Клас std::nested_exception та супутні функції

```cpp
namespace std {
    class nested_exception {
    public:
        nested_exception() noexcept;
        nested_exception(const nested_exception&) noexcept = default;
        nested_exception& operator=(const nested_exception&) noexcept = default;
        virtual ~nested_exception() = default;

        // Повертає збережений вкладений виняток
        exception_ptr nested_ptr() const noexcept;

        // Повторно кидає вкладений виняток
        [[noreturn]] void rethrow_nested() const;
    };

    // Створює вкладений виняток із поточного активного винятку
    template<class T>
    [[noreturn]] void throw_with_nested(T&& t);

    // Повторно кидає вкладений виняток, якщо об'єкт успадковує від std::nested_exception
    template<class E>
    void rethrow_if_nested(const E& e);
}
```

### 7.2. Робота з std::exception_ptr

Об'єкт `std::exception_ptr` являє собою тип збалансованого вказівника (схожого на `std::shared_ptr`), який здатний посилатися на довільний об'єкт винятку, збережений у системній EH-купі.

- `std::exception_ptr current_exception() noexcept`: Повертає `std::exception_ptr`, який посилається на поточний активний виняток у блоці `catch`, або порожній `exception_ptr`, якщо активних винятків немає.
- `[[noreturn]] void rethrow_exception(std::exception_ptr p)`: Повторно генерує виняток, на який вказує `p`.
- `template<class E> std::exception_ptr make_exception_ptr(E e) noexcept`: Створює `std::exception_ptr`, що містить копію об'єкта `e`, без фактичного виконання інструкції `throw`.

---

## 8. Зведена матриця стандартних класів винятків C++

Нижче наведено зведену таблицю всіх стандартних класів винятків, їхніх заголовочних файлів, вихідних предків та стандартних умов виникнення:

| Клас винятку | Заголовочний файл | Базовий клас | Спеціальні методи | Причина виникнення |
| :--- | :--- | :--- | :--- | :--- |
| `std::exception` | `<exception>` | — | `what()` | Базовий поліморфний корінь усіх винятків |
| `std::logic_error` | `<stdexcept>` | `std::exception` | `what()` | Базовий клас логічних помилок коду |
| `std::invalid_argument` | `<stdexcept>` | `std::logic_error` | `what()` | Некоректне значення переданого аргументу |
| `std::domain_error` | `<stdexcept>` | `std::logic_error` | `what()` | Порушення математичної області визначення |
| `std::length_error` | `<stdexcept>` | `std::logic_error` | `what()` | Спроба перевищити максимальний розмір `max_size()` |
| `std::out_of_range` | `<stdexcept>` | `std::logic_error` | `what()` | Вихід за межі допустимих індексів |
| `std::future_error` | `<future>` | `std::logic_error` | `code()` | Некоректний стан асинхронного `std::future` |
| `std::runtime_error` | `<stdexcept>` | `std::exception` | `what()` | Базовий клас помилок середовища виконання |
| `std::range_error` | `<stdexcept>` | `std::runtime_error` | `what()` | Помилка діапазону обчисленого результату |
| `std::overflow_error` | `<stdexcept>` | `std::runtime_error` | `what()` | Арифметика: переповнення верхньої межі |
| `std::underflow_error` | `<stdexcept>` | `std::runtime_error` | `what()` | Арифметика: втрата значущості під нижню межу |
| `std::system_error` | `<system_error>` | `std::runtime_error` | `code()` | Системні помилки ОС (`errno`, Win32 API) |
| `std::filesystem_error` | `<filesystem>` | `std::system_error` | `path1()`, `path2()` | Збої операцій із файловою системою |
| `std::format_error` | `<format>` | `std::runtime_error` | `what()` | Помилки синтаксису рядка `std::format` |
| `std::bad_alloc` | `<new>` | `std::exception` | `what()` | Збій виділення пам'яті в купі (`operator new`) |
| `std::bad_array_new_length`| `<new>` | `std::bad_alloc` | `what()` | Некоректний розмір масиву `new T[N]` |
| `std::bad_cast` | `<typeinfo>` | `std::exception` | `what()` | Невдале приведення `dynamic_cast<T&>` |
| `std::bad_typeid` | `<typeinfo>` | `std::exception` | `what()` | Виклик `typeid(*ptr)` над `nullptr` |
| `std::bad_optional_access` | `<optional>` | `std::exception` | `what()` | Спроба виклику `value()` над порожнім `optional` |
| `std::bad_variant_access` | `<variant>` | `std::exception` | `what()` | Запит неактивного типу з `std::variant` |
| `std::bad_any_cast` | `<any>` | `std::exception` | `what()` | Невдале приведення типів `std::any_cast` |
| `std::bad_weak_ptr` | `<memory>` | `std::exception` | `what()` | Конструювання `shared_ptr` із застарілого `weak_ptr` |
| `std::bad_function_call` | `<functional>` | `std::exception` | `what()` | Виклик порожнього об'єкта `std::function` |
