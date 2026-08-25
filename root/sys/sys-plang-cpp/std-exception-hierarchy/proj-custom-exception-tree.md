# ⚙️ Проєктування доменної ієрархії винятків із підтримкою error_code та stacktrace

У промислових системних проєктах високого навантаження — таких як високочастотні торгові платформи, СУБД або мережеві розподілені сховища — прямого використання стандартних класів `std::runtime_error` або `std::logic_error` виявляється недостатньо. Стандартні винятки зберігають лише один рядок `what()`, що не дозволяє програмно розібрати причину збою, не містить інформації про вихідний файл та рядок коду (source location), не зберігає системний код помилки операційної системи та не фіксує стек викликів (stacktrace).

Для розв'язання цієї проблеми створюється власна доменна ієрархія винятків, успадкована від `std::runtime_error`, яка поєднує в собі чотири фундаментальні діагностичні механізми:

1. **Системний код помилки `std::error_code`**: дозволяє програмно перевіряти категорію та тип збою без розбору текстового рядка `what()`, що уможливлює створення автоматизованих стратегій повторного виклику (retry mechanisms) або перемикання на резервні вузли (failover).
2. **Контекст вихідного коду `std::source_location` (C++20)**: замінює застарілі препроцесорні макроси `__FILE__`, `__LINE__` та `__func__`. Завдяки стандартному аргументу за замовчуванням `std::source_location::current()` виняток фіксує ім'я файлу, назву функції та рядок у місці конструювання об'єкта без використання синтаксичних макросних обгорток.
3. **Знімок стеку викликів `std::stacktrace` (C++23)**: захоплює послідовність фреймів викликів функцій у момент створення винятку. Це дозволяє миттєво відтворити шлях виконання програми до точки збою в журналах спостережуваності (observability logs).
4. **Підтримку вкладених винятків (`std::nested_exception`)**: реалізує концепцію причинно-наслідкових ланцюжків помилок (Cause Chain), коли низькорівневий мережевий або файловий виняток обгортається у високорівневу доменну помилку бізнес-логіки зі збереженням початкового контексту.

---

## 1. Архітектура та компроміси виділення пам'яті

При проєктуванні доменних винятків ключовим архітектурним викликом є забезпечення безпеки виділення пам'яті під час генерації винятку. Якщо середовище виконання перебуває під загрозою вичерпання ресурсів, спроба форматування довгого рядка або захоплення стеку викликів може спровокувати виділення пам'яті у купі, яке завершиться викликом `std::bad_alloc`.

Для запобігання цьому використовується стратегія ледачого форматування (lazy formatting). Внутрішнє текстове поле `formatted_what_` залишається порожнім під час створення об'єкта винятку. Воно форматується та заповнюється лише при першому виклику віртуального методу `what()`. Якщо у процес форматування виникає виняток виділення пам'яті, внутрішній блок `try-catch` перехоплює його та безпечно повертає заздалегідь підготовлений статичний рядок із базового класу `std::runtime_error`.

Крім того, використання `std::source_location` не створює жодних додаткових виділень пам'яті в купі, оскільки вказівники на назви файлів та функцій посилаються на статичну пам'ять специфікації рядкових літералів у сегменті коду (`.rodata`).

### Захоплення фреймів стеку через std::stacktrace (C++23)

Захоплення стеку викликів через `std::stacktrace::current()` вимагає взаємодії з системними таблицями unwinding та символізатором (symbolizer). Створення об'єкта `std::stacktrace` виділяє пам'ять під масив вказівників на інструкції (IP registers). 

У проєктах з екстремальними вимогами до латентності створення знімка стеку може бути відкладено або зроблено опціональним через конфігураційний прапорець, щоб уникнути викликів `malloc` під час генерації винятку у гарячих циклах.

### Інтеграція системних кодів помилок через std::error_code

Об'єкт `std::error_code` являє собою пару з двох елементів: цілочисельного значення та вказівника на константний екземпляр `std::error_category`. Це дозволяє передавати системні помилки POSIX (`errno`), помилки мережевих бібліотек (Asio, WinSock) або доменні коди СУБД у формі компактного 16-байтного об'єкта, який не вимагає виділення пам'яті в купі та підтримує порівняння за нульовий час CPU.

---

## 2. Повна реалізація проєкту: Доменна ієрархія винятків мережевого сховища

Нижче наведено повну вихідну реалізацію базового доменного винятку `storage_exception` та його похідного класифікованого винятку `network_io_exception`.

:::tabs
```cpp
#include <iostream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <source_location>
#include <stacktrace>
#include <exception>

// Базовий доменний виняток розподіленого сховища даних
class storage_exception : public std::runtime_error {
private:
    std::error_code code_;
    std::source_location location_;
    std::stacktrace trace_;
    mutable std::string formatted_what_;

public:
    // Конструктор із підтримкою error_code, source_location та stacktrace
    explicit storage_exception(
        std::error_code ec,
        const std::string& message,
        std::source_location loc = std::source_location::current(),
        std::stacktrace trace = std::stacktrace::current()
    ) : std::runtime_error(message),
        code_(ec),
        location_(loc),
        trace_(std::move(trace)) {}

    // Доступ до системного коду помилки
    [[nodiscard]] const std::error_code& code() const noexcept {
        return code_;
    }

    // Доступ до точки генерації у вихідному коді
    [[nodiscard]] const std::source_location& location() const noexcept {
        return location_;
    }

    // Доступ до знімку стеку викликів
    [[nodiscard]] const std::stacktrace& trace() const noexcept {
        return trace_;
    }

    // Перекритий поліморфний метод what() з ледачим форматуванням
    [[nodiscard]] const char* what() const noexcept override {
        if (formatted_what_.empty()) {
            try {
                formatted_what_ = std::string(std::runtime_error::what()) +
                    "\n  [Помилка]: " + code_.category().name() + ":" + std::to_string(code_.value()) +
                    " (" + code_.message() + ")" +
                    "\n  [Локація]: " + location_.file_name() + ":" +
                    std::to_string(location_.line()) + " in " + location_.function_name();
            } catch (...) {
                return std::runtime_error::what();
            }
        }
        return formatted_what_.c_str();
    }
};

// Спеціалізований виняток мережевого I/O
class network_io_exception : public storage_exception {
private:
    std::string remote_endpoint_;

public:
    network_io_exception(
        std::error_code ec,
        std::string endpoint,
        const std::string& msg,
        std::source_location loc = std::source_location::current()
    ) : storage_exception(ec, msg + " [Endpoint: " + endpoint + "]", loc),
        remote_endpoint_(std::move(endpoint)) {}

    [[nodiscard]] const std::string& endpoint() const noexcept {
        return remote_endpoint_;
    }
};

// Приклад використання та демонстрація вкладених винятків
void low_level_network_read(const std::string& host) {
    // Імітація системного збою ECONNRESET (Connection reset by peer)
    std::error_code ec(104, std::generic_category());
    throw network_io_exception(ec, host + ":8080", "Помилка читання із сокета");
}

void process_client_request(const std::string& host) {
    try {
        low_level_network_read(host);
    } catch (...) {
        // Загортаємо низькорівневу мережеву помилку у виняток бізнес-логіки
        std::throw_with_nested(
            storage_exception(
                std::make_error_code(std::errc::io_error),
                "Не вдалося виконати транзакцію клієнта"
            )
        );
    }
}

int main() {
    try {
        process_client_request("192.168.1.50");
    } catch (const storage_exception& e) {
        std::cout << "=== ПЕРЕХОПЛЕНО ДОМЕННИЙ ВИНЯТОК ===" << std::endl;
        std::cout << e.what() << std::endl;

        // Друк стеку викликів (якщо підтримується платформою)
        if (!e.trace().empty()) {
            std::cout << "\n=== СТЕК ВИКЛИКІВ (STACKTRACE) ===" << std::endl;
            std::cout << std::to_string(e.trace()) << std::endl;
        }

        // Перевірка на наявність вкладеного винятку
        try {
            std::rethrow_if_nested(e);
        } catch (const network_io_exception& nested) {
            std::cout << "\n=== ПРИЧИННИЙ ВКЛАДЕНИЙ ВИНЯТОК ===" << std::endl;
            std::cout << "Вузол: " << nested.endpoint() << std::endl;
            std::cout << "Код: " << nested.code().value() << std::endl;
        } catch (...) {
            std::cout << "\nПерехоплено невідомий вкладений виняток." << std::endl;
        }
    }
    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Ідіоматичний еквівалент обробки помилок у C через статус-структури
typedef struct {
    int code;
    const char* category;
    char message[256];
    char file[128];
    int line;
} c_error_context;

// Потік-локальний стек помилок (Thread-Local Error Context)
static __thread c_error_context g_last_error = {0};

void set_last_error(int code, const char* cat, const char* msg, const char* file, int line) {
    g_last_error.code = code;
    g_last_error.category = cat;
    g_last_error.line = line;
    snprintf(g_last_error.message, sizeof(g_last_error.message), "%s", msg);
    snprintf(g_last_error.file, sizeof(g_last_error.file), "%s", file);
}

const c_error_context* get_last_error(void) {
    return &g_last_error;
}

// Функція з C-моделлю повернення статусу
int low_level_network_read_c(const char* host) {
    if (strcmp(host, "invalid") == 0) {
        set_last_error(104, "POSIX", "Connection reset by peer", __FILE__, __LINE__);
        return -1; // Сигнал помилки
    }
    return 0; // Успіх
}

int main(void) {
    if (low_level_network_read_c("invalid") != 0) {
        const c_error_context* err = get_last_error();
        printf("=== C-STYLE ERROR CONTEXT ===\n");
        printf("Код: %s:%d\n", err->category, err->code);
        printf("Опис: %s\n", err->message);
        printf("Локація: %s:%d\n", err->file, err->line);
    }
    return 0;
}
```
:::

---

## 3. Детальний розбір механізмів обгортання у C та C++

Порівняльний аналіз представлених реалізацій C та C++ висвітлює принципову різницю у філософіях передачі контексту помилки між мовами.

### Модель C: Thread-Local контекст та статус-структури

У мові C винятки як мовна конструкція відсутні. Тому для створення насиченого контексту помилки (із кодом, категорією, текстом та точкою у коді `__FILE__`/`__LINE__`) застосовується потік-локальний стек помилок (Thread-Local Error Context), реалізований через специфікатор `__thread` (або `thread_local` у C11).

Головні властивості цієї моделі:
- **Передавання коду статусу**: Функції повертають цілочисельний індикатор (наприклад, `0` для успіху та `-1` для збою).
- **Збереження контексту**: Деталі помилки записуються у потік-локальну структуру `g_last_error`.
- **Нульовий оверхед при успіху**: Нормальний шлях виконання повертає простий інвертований нуль у регістрі `RAX` без будь-якого виділення пам'яті.
- **Ризик ігнорування**: Викликаюча сторона зобов'язана явно перевірити повернуте значення. Якщо розробник забуде додати `if (res != 0)`, помилка мовчки проігнорується.

### Модель C++: Поліморфні доменні винятки та вкладеність

У мові C++ виняток являє собою повноцінний об'єкт із віртуальною таблицею методів, який автоматично піднімається по стеку викликів до першого відповідного обробника `catch`.

Головні переваги поліморфної моделі C++:
- **Неможливість ігнорування**: Якщо блок `try-catch` відсутній, програма перериває виконання через `std::terminate()`, що запобігає роботі зі зіпсованими даними.
- **Збереження точного типу**: Завдяки поліморфізму блок `catch (const storage_exception& e)` здатен перехоплювати як `storage_exception`, так і `network_io_exception` без зрізання полів (slicing).
- **Ланцюжки причин (Cause Chains)**: Механізм `std::throw_with_nested` дозволяє зберігати первинну низькорівневу причину збою всередині об'єкта `std::nested_exception`, створюючи ієрархічний деревоподібний знімок проблеми.

---

## 4. Інженерний регламент створення доменних класів помилок

При практичному застосуванні створеної ієрархії слід дотримуватися п'яти ключових правил розробки:

1. **Запобігання витокам пам'яті у what()**: Поле `formatted_what_` завжди має бути помічене як `mutable`, щоб дозволити обчислення рядка всередині константного методу `what() const`. Захист через `try-catch` всередині `what()` гарантує відсутність подвійних винятків під час розгортання стеку.
2. **Семантика переміщення для складних полів**: Усі об'єкти, що передаються в конструктор (рядки `endpoint`, знімки `std::stacktrace`), мають передаватися через rvalue-посилання або за значенням з наступним `std::move` у списку ініціалізації.
3. **Суворе успадкування від std::runtime_error або std::logic_error**: Не успадковуйте класи безпосередньо від `std::exception`. У більшості реалізацій стандартних бібліотек (GCC libstdc++, LLVM libc++, MSVC STL) клас `std::exception` не містить внутрішніх полів для збереження текстових повідомлень, тому успадкування від нього змусить вас вручну реалізовувати буферизацію та копіювання вказівників `const char*`.
4. **Гарантія noexcept для всіх getter-методів**: Усі додаткові методи доступу (`code()`, `location()`, `trace()`) зобов'язані містити специфікатор `noexcept` та атрибут `[[nodiscard]]`, щоб унеможливити порожнє ігнорування результату перевірки.
5. **Тестування поведінки при вичерпанні пам'яті**: Регулярно перевіряйте роботу доменної ієрархії під навантажувальними тестами з обмеженим обсягом купи (heap limits), щоб переконатися, що генерація винятків не спричиняє вторинних викликів `std::bad_alloc`.
