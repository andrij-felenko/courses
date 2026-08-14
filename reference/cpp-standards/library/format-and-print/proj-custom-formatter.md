# ⚙️ Практика: власні форматирувальники та безалокаційний формат

Надання підтримки форматування власноруч створеним структурам даних у C++ — це не лише зручність виводу, а й ключовий компонент побудови високопродуктивних систем логування, мережевих протоколів, наукових обчислень та інструментів серіалізації. У цій практичній вставці ми побудуємо повноцінні форматирувальники для математичного класу `Matrix3x3` та структури запису логу `LogRecord`, а також розберемо детальні техніки безалокаційного форматування у стековий буфер за допомогою функцій `std::format_to` та `std::format_to_n`.

## Постановка задачі: швидке логування та обчислення без виділення пам'яті у купі

У системних сервісах обробки запитів (наприклад, торгових шлюзах HFT, мережевих проксі, графічних рушіях та вбудованій авіоніці) операція виділення пам'яті у купі під час форматування кожного рядка логу чи матриці створює неприпустимі затримки (latency spikes). Коли алокатор системної бібліотеки змушений шукати вільний блок у таблицях купи чи брати блокування багатопотокового середовища, затримка виконання може зростати з декількох наносекунд до мікросекунд.

Причина полягає у тому, що системний `malloc` або `operator new[]` виконує складний алгоритм пошуку відповідного блока пам'яті, бере загальносистемні спинові локи та може викликати перемикання контексту операційної системи. Крім того, створення об'єкта `std::string` на стеку з вказівником на купу призводить до погіршення локальності кешу процесора (L1/L2 cache misses) через розіменування вказівників.

Для вирішення цієї проблеми ми поставимо наступні інженерні завдання:
1. Реалізувати математичний клас `Matrix3x3` та реалізувати для нього спеціалізацію `std::formatter<Matrix3x3>` із підтримкою однорядкового та багаторядкового вирівняного виводу.
2. Створити структуру запису логу `LogRecord` із полями мітки часу, рівня логування, імені компонента та текстового повідомлення.
3. Реалізувати для `LogRecord` спеціалізацію шаблону `std::formatter<LogRecord>` із підтримкою трьох режимів виводу: розширеного тексту, короткого підсумку та форматного рядка JSON.
4. Написати безалокаційний клас логування `FastLogger`, який форматує запис безпосередньо у фіксований стековий буфер `std::array<char, N>` за допомогою `std::format_to_n`, повністю усуваючи системні виклики `malloc` та гарантуючи захист від переповнення буфера.

## Частина 1. Спеціалізація std::formatter для математичного класу Matrix3x3

Матриці три на три активно використовуються у тривимірній графіці, фізичних симуляціях та робототехніці. Ми хочемо підтримати два режими виводу для `Matrix3x3`:
- `{}` або `{:m}` — багаторядковий формат із фіксованою точністю та вирівнюванням по стовпчиках;
- `{:1l}` — однорядковий формат для компактного друку у логах вида `[[1, 0, 0], [0, 1, 0], [0, 0, 1]]`.

```cpp
#include <format>
#include <array>
#include <string_view>
#include <iostream>
#include <algorithm>
#include <chrono>

class Matrix3x3 {
public:
    std::array<double, 9> data{};

    constexpr Matrix3x3() noexcept : data{1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0} {}
    constexpr Matrix3x3(std::initializer_list<double> list) noexcept {
        std::copy(list.begin(), list.end(), data.begin());
    }

    constexpr double at(std::size_t r, std::size_t c) const noexcept {
        return data[r * 3 + c];
    }
};

template <>
struct std::formatter<Matrix3x3> {
    bool single_line = false;
    int precision = 2;

    // 1. Компіляційний розбір специфікаторів у constexpr контексті
    constexpr auto parse(std::format_parse_context& ctx) {
        auto it = ctx.begin();
        auto end = ctx.end();

        if (it != end && *it == '1') {
            single_line = true;
            ++it;
        }

        if (it != end && *it == '.') {
            ++it;
            if (it != end && *it >= '0' && *it <= '9') {
                precision = *it - '0';
                ++it;
            }
        }

        if (it != end && *it != '}') {
            throw std::format_error("Invalid format specifier for Matrix3x3");
        }
        return it;
    }

    // 2. Генерація заформатованого виводу у вихідний ітератор
    template <typename FormatContext>
    auto format(const Matrix3x3& m, FormatContext& ctx) const {
        if (single_line) {
            return std::format_to(ctx.out(), 
                "[[{:.{}f}, {:.{}f}, {:.{}f}], [{:.{}f}, {:.{}f}, {:.{}f}], [{:.{}f}, {:.{}f}, {:.{}f}]]",
                m.at(0,0), precision, m.at(0,1), precision, m.at(0,2), precision,
                m.at(1,0), precision, m.at(1,1), precision, m.at(1,2), precision,
                m.at(2,0), precision, m.at(2,1), precision, m.at(2,2), precision);
        }

        return std::format_to(ctx.out(),
            "| {:>{}.{}f} {:>{}.{}f} {:>{}.{}f} |\n"
            "| {:>{}.{}f} {:>{}.{}f} {:>{}.{}f} |\n"
            "| {:>{}.{}f} {:>{}.{}f} {:>{}.{}f} |",
            m.at(0,0), precision + 5, precision, m.at(0,1), precision + 5, precision, m.at(0,2), precision + 5, precision,
            m.at(1,0), precision + 5, precision, m.at(1,1), precision + 5, precision, m.at(1,2), precision + 5, precision,
            m.at(2,0), precision + 5, precision, m.at(2,1), precision + 5, precision, m.at(2,2), precision + 5, precision);
    }
};
```

Зверніть увагу на використання `std::format_to` всередині методом `format()`. Ми делегуємо форматування окремих елементів типу `double` стандартному підсистемному форматирувальнику числа із плаваючою крапкою, який використовує швидкий безалокаційний алгоритм Dragonbox.

## Частина 2. Спеціалізація std::formatter для типу даних LogRecord

Тепер створимо перелічувальний тип `LogLevel` та структуру `LogRecord`. Зверніть увагу, що поля `component` та `message` використовують безволодісні погляди `std::string_view`, що уможливлює передачу строкових літералів без копіювання символів у купу:

```cpp
enum class LogLevel { Trace, Debug, Info, Warn, Error, Fatal };

struct LogRecord {
    std::chrono::system_clock::time_point timestamp;
    LogLevel level;
    std::string_view component;
    std::string_view message;
};

template <>
struct std::formatter<LogRecord> {
    enum class Mode { Full, Short, Json };
    Mode mode = Mode::Full;

    // 1. Компіляційний розбір специфікаторів у constexpr контексті
    constexpr auto parse(std::format_parse_context& ctx) {
        auto it = ctx.begin();
        auto end = ctx.end();

        if (it != end && *it != '}') {
            if (*it == 's') { mode = Mode::Short; ++it; }
            else if (*it == 'j') { mode = Mode::Json; ++it; }
            else if (*it == 'f') { mode = Mode::Full; ++it; }
            else { throw std::format_error("Unknown specifier for LogRecord"); }
        }

        if (it != end && *it != '}') {
            throw std::format_error("Invalid format specifier for LogRecord");
        }
        return it;
    }

    // Допоміжна функція перетворення рівня в рядок
    static constexpr std::string_view level_to_string(LogLevel lvl) noexcept {
        switch (lvl) {
            case LogLevel::Trace: return "TRACE";
            case LogLevel::Debug: return "DEBUG";
            case LogLevel::Info:  return "INFO";
            case LogLevel::Warn:  return "WARN";
            case LogLevel::Error: return "ERROR";
            case LogLevel::Fatal: return "FATAL";
        }
        return "UNKNOWN";
    }

    // 2. Генерація текстового виводу у вихідний ітератор
    template <typename FormatContext>
    auto format(const LogRecord& rec, FormatContext& ctx) const {
        std::string_view lvl_str = level_to_string(rec.level);

        if (mode == Mode::Short) {
            return std::format_to(ctx.out(), "{}: {}", lvl_str, rec.message);
        } 
        else if (mode == Mode::Json) {
            return std::format_to(ctx.out(), 
                "{{\"level\":\"{}\",\"comp\":\"{}\",\"msg\":\"{}\"}}", 
                lvl_str, rec.component, rec.message);
        }

        // За замовчуванням Full: дата-час + рівень + компонент + повідомлення
        return std::format_to(ctx.out(), 
            "[{:%Y-%m-%d %H:%M:%S}] [{}] [{}]: {}", 
            rec.timestamp, lvl_str, rec.component, rec.message);
    }
};
```

У режимі JSON зауважте екранування подвійних фігурних дужок `{{` та `}}`. У граматиці `std::format` подвійні фігурні дужки інтерпретуються як буквальні символи дужок `{` та `}`, а не як замінники аргументів.

## Частина 3. Безалокаційне логування через std::format_to_n

Функція `std::format_to_n` є ключовим інструментом побудови безалокаційних систем форматування у C++. Вона приймає вихідний вказівник або ітератор, максимальний обсяг запису `N`, рядок формату та довільні аргументи.

На відміну від звичайного `std::format`, який виділяє пам'ять під новий `std::string`, `std::format_to_n` записує символи безпосередньо у наданий масив байтів. Функція повертає структуру `std::format_to_n_result`, що містить два поля:
- `out` — підсумковий ітератор, що вказує на позицію за останнім записаним символом;
- `size` — загальну кількість символів, які мав би залікувати `std::format` (навіть якщо вони не помістилися у фіксований ліміт `N`).

Це дозволяє легко виявити факт обрізання тексту: якщо `res.size > N`, це означає, що заформатований рядок перевищив розмір стекового буфера, але переповнення пам'яті не сталося.

```cpp
template <std::size_t BufferSize>
class FastLogger {
public:
    template <typename... Args>
    static void log(std::format_string<Args...> fmt, Args&&... args) {
        // Локальний стековий масив — 0 алокацій у купі!
        alignas(std::max_align_t) std::array<char, BufferSize> buf;

        try {
            // Форматуємо прямо у стековий буфер із суворим обмеженням BufferSize - 1
            auto res = std::format_to_n(buf.data(), buf.size() - 1, fmt, std::forward<Args>(args)...);

            // Обчислюємо кількість фактично записаних байтів
            std::size_t written = std::min(static_cast<std::size_t>(res.size), BufferSize - 1);
            buf[written] = '\0'; // Гарантуємо нульовий термінатор

            // Створюємо безволодісний погляд для прямоточного виводу
            std::string_view out_view(buf.data(), written);
            std::cout << out_view << "\n";

            if (res.size >= static_cast<std::ptrdiff_t>(BufferSize)) {
                // Текст було безпечно обрізано через брак місця у стеку
                std::cerr << "[WARNING]: Log record truncated! Required: " 
                          << res.size << " bytes, available buffer: " << BufferSize - 1 << "\n";
            }
        } catch (const std::format_error& e) {
            std::cerr << "[LOG ERROR]: Exception during formatting: " << e.what() << "\n";
        }
    }
};
```

Клас `FastLogger` використовує параметризацію шаблону розміром буфера `BufferSize`. У критичних вузлах обробки можна обирати малий розмір (наприклад, 128 байтів для стека), а для великих повідомлень створювати локальні буфери на 1024 байти. Оскільки `std::array<char, BufferSize>` живе безпосередньо у кадрі стека функції, виклик не потребує взаємодії з операційною системою чи алокатором.

Слід звернути увагу на специфікатор `alignas(std::max_align_t)`. Хоча форматирувальник записує символи побайтово, явне вирівнювання стекового масиву покращує ефективність SIMD-інструкцій (AVX2/AVX-512), якими компілятор векторально заповнює та копіює підсумковий буфер.

Блок `try-catch` гарантує, що якщо один із користувацьких форматирувачів кидає виняток `std::format_error` у runtime, додаток не впаде, а логер безпечно перехопить помилку й виведе повідомлення у `std::cerr`.

## Частина 4. Демонстраційний приклад та аналіз результатів

Продемонструємо роботу побудованого форматирувальника та логера у головній функції:

```cpp
int main() {
    // 1. Тестування форматування матриці
    Matrix3x3 mat{1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0};

    std::cout << "--- Друк Matrix3x3 ---\n";
    std::cout << "Багаторядковий:\n" << std::format("{:.2f}", mat) << "\n\n";
    std::cout << "Однорядковий: " << std::format("{:1.1f}", mat) << "\n\n";

    // 2. Тестування форматування логу
    LogRecord rec{
        .timestamp = std::chrono::system_clock::now(),
        .level = LogLevel::Info,
        .component = "HTTP/Server",
        .message = "GET /api/v1/status HTTP/1.1 200 OK"
    };

    std::cout << "--- Друк LogRecord ---\n";
    std::cout << std::format("Full: {}", rec) << "\n";
    std::cout << std::format("JSON: {:j}", rec) << "\n";
    std::cout << std::format("Short: {:s}", rec) << "\n\n";

    // 3. Високпродуктивне безалокаційне логування
    std::cout << "--- FastLogger ---\n";
    FastLogger<256>::log("Record: {:j}", rec);
    FastLogger<256>::log("Matrix state: {:1.2f}", mat);

    return 0;
}
```

## Анатомія продуктивності та безпеки

Використання обгортки `std::format_string<Args...>` у параметрі `fmt` функції `FastLogger::log` забезпечує компіляційну перевірку рядка формату під час збірки. Якщо розробник припуститься помилки й напише `FastLogger<256>::log("Value: {:d}", "string")`, компілятор негайно зупинить збірку з помилкою типу.

Завдяки поєднанню `std::format_to_n` та `std::array<char, N>` ми отримали повністю безалокаційний механізм логування, який гарантує відсутність накладних витрат на управління купою, а час виконання операції форматування лишається абсолютно детермінованим (O(N) за довжиною заформатованих символів).
