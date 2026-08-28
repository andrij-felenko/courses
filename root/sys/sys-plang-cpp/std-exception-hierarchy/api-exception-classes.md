# 📋 Інтерфейсна специфікація стандартних класів винятків C++

Стандартна бібліотека C++ надає розвинену та суворо впорядковану ієрархію зумовлених класів винятків. Вони розподілені за спеціалізованими заголовочними файлами: `<exception>`, `<stdexcept>`, `<system_error>`, `<new>`, `<typeinfo>`, `<optional>`, `<variant>`, `<any>`, `<future>`, `<format>`, `<filesystem>` та `<stacktrace>`.

Усі стандартні винятки успадковують від єдиного базового класу `std::exception`. Фундаментальний контракт передбачає надання віртуального методу `what()` для одержання текстового опису помилки та дотримання суворого специфікатора `noexcept` для всіх деструкторів і конструкторів копіювання, що унеможливлює виникнення повторних збоїв під час розгортання стеку.

---

## 1. Базовий клас std::exception (<exception>)

Клас `std::exception` виступає поліморфним корнем усієї ієрархії винятків стандартної бібліотеки C++. Він визначений у заголовочному файлі `<exception>`.

:::code api-exception-classes/cpp/1-bazovyi-klas-std.cpp

### Члени класу та вимоги контракту:
- `exception()`: Створює базовий об'єкт винятку. Гарантує `noexcept` — не здійснює виділень пам'яті в купі.
- `virtual ~exception() noexcept`: Віртуальний деструктор. Забезпечує коректне очищення ресурсів похідних об'єктів при поліморфному видаленні через вказівник на базовий тип `std::exception*`.
- `virtual const char* what() const noexcept`: Повертає нуль-термінований рядок символів (`const char*`), що описує причину помилки. Повернений вказівник залишається дійсним принаймні до знищення об'єкта винятку або до виклику операторів присвоєння.

---

## 2. Логічні винятки (<stdexcept>): std::logic_error та похідні

Класи цієї групи описують помилки в логіці програми. Вони виникають у ситуаціях, які теоретично могли бути виявлені й відвернені на етапі проєктування або статичного аналізу коду (порушення прекондицій, передача некоректних аргументів, некоректний стан об'єкта).

### 2.1. std::logic_error
Базовий клас для всіх логічних помилок. Зберігає текстовий буфер повідомлення, переданий під час конструювання.

:::code api-exception-classes/cpp/2-1-std-logic-error.hpp

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

:::code api-exception-classes/cpp/3-1-std-runtime-error.hpp

### 3.2. Похідні класи std::runtime_error

1. **`std::range_error`**: Виникає при внутрішньому обчисленні результату, який виходить за межі допустимого діапазону результатів (range error у математичних алгоритмах).
2. **`std::overflow_error`**: Сигналізує про математичне переповнення верхньої межі типу даних (arithmetic overflow).
3. **`std::underflow_error`**: Сигналізує про математичне втрачання значущості під нижню межу типів із плаваючою крапкою (arithmetic underflow).
4. **`std::system_error` (<system_error>, C++11)**: Інтегрує винятки C++ із числовими кодами системних помилок операційної системи (`errno` в POSIX або `GetLastError()` у Win32 API).

:::code api-exception-classes/cpp/3-2-pokhidni-klasy-std.hpp

5. **`std::filesystem_error` (<filesystem>, C++17)**: Похідний від `std::system_error`. Інформує про помилки файлової системи та надає шляхи до проблемних файлів.

:::code api-exception-classes/cpp/3-2-pokhidni-klasy-std-2.hpp

6. **`std::format_error` (<format>, C++20)**: Виникає при помилках форматування рядків через `std::format` або `std::print` (некоректний специфікатор формату).

---

## 4. Інтерфейси категорій системних помилок (<system_error>)

Для підтримки роботи `std::system_error` стандарт C++11 вводить допоміжні типи `std::error_category`, `std::error_code` та `std::error_condition`.

### 4.1. Специфікація класу std::error_category

:::code api-exception-classes/cpp/4-1-spetsyfikatsiia-klasu.cpp

### 4.2. Специфікація класу std::error_code

:::code api-exception-classes/cpp/4-2-spetsyfikatsiia-klasu.cpp

---

## 5. Винятки виділення пам'яті та низькорівневі збої (<new>, <typeinfo>)

Окремими заголовочними файлами визначаються спеціалізовані винятки, пов'язані з низькорівневим функціонуванням середовища виконання C++.

### 5.1. Винятки динамічної пам'яті (<new>)

- **`std::bad_alloc`**: Кидається оператором `operator new`, коли система не здатна виділити необхідний обсяг динамічної пам'яті в купі.
- **`std::bad_array_new_length` (C++11)**: Похідний від `std::bad_alloc`. Виникає при спробі виділення пам'яті під масив `new T[N]`, коли розмір `N` є від'ємним чи перевищує максимально допустимий ліміт реалізації.

:::code api-exception-classes/cpp/5-1-vyniatky-dynamichnoi.cpp

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

:::code api-exception-classes/cpp/7-1-klas-std-nested.hpp

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
