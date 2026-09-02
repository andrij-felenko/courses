// node.hpp — комірка значення AWK у C++: той самий двоїстий стан, що й у
// c/internals/node_layout.h.
//
// Різниця не косметична. У C стан «числова форма актуальна» доводиться
// тримати окремим бітом NUMCUR поруч із полем numbr, і будь-яка мутація мусить
// не забути його зняти. Тут це один std::optional<double>: порожній optional
// і Є відсутністю кешу, забути нема чого. Прапорці ПОХОДЖЕННЯ лишаються —
// саме вони, а не вміст, вирішують, як порівнювати.
//
// Файл навмисно нічого не знає про <gawkapi.h>: модель перевіряється тестами
// без встановленого gawk-devel.
#pragma once

#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <optional>
#include <string>
#include <utility>

namespace awk::internals {

inline constexpr const char *kDefaultConvfmt = "%.6g";

// Походження значення. У gawk це біти в NODE.flags; сенс той самий.
enum class Origin {
    Uninitialized,  // змінної ще не торкалися: вона водночас 0 і ""
    Number,         // числовий літерал або результат арифметики
    String,         // рядковий літерал, конкатенація, substr, sprintf
    Input           // $0, $i, getline, ARGV — кандидат у strnum
};

// Синтаксис числа за POSIX: провідні й кінцеві пробіли дозволені, а от
// "100MB", "0x1F", "inf" і "nan" числовим РЯДКОМ не є. strtod() три останні
// з'їв би залюбки, тому літери відсікаємо до нього.
[[nodiscard]] inline bool looks_numeric(const std::string &text) noexcept
{
    for (const unsigned char c : text)
        if (std::isalpha(c) && c != 'e' && c != 'E')
            return false;

    const char *begin = text.c_str();
    while (std::isspace(static_cast<unsigned char>(*begin)))
        ++begin;
    if (*begin == '\0')
        return false;

    char *end = nullptr;
    std::strtod(begin, &end);
    if (end == begin)
        return false;
    while (std::isspace(static_cast<unsigned char>(*end)))
        ++end;
    return *end == '\0';        // хвіст з'їдено весь — це число
}

// Префіксна семантика перетворення: "100MB" -> 100, "error" -> 0.
[[nodiscard]] inline double parse_prefix(const std::string &text) noexcept
{
    std::size_t i = 0;
    while (i < text.size() && std::isspace(static_cast<unsigned char>(text[i])))
        ++i;

    const std::size_t start = i;
    if (i < text.size() && (text[i] == '+' || text[i] == '-'))
        ++i;

    // strtod() з C99 розпізнає "0x1F", "inf" і "nan". AWK без --posix цього
    // НЕ робить: там "0x1F" + 0 дорівнює нулю, а шістнадцяткове читає лише
    // strtonum(). Тому такі префікси відсікаємо самі.
    if (i >= text.size())
        return 0.0;
    if (!std::isdigit(static_cast<unsigned char>(text[i])) && text[i] != '.')
        return 0.0;
    if (text[i] == '0' && i + 1 < text.size() && (text[i + 1] == 'x' || text[i + 1] == 'X'))
        return 0.0;

    const char *from = text.c_str() + start;
    char *end = nullptr;
    const double value = std::strtod(from, &end);
    return end == from ? 0.0 : value;
}

// Число -> рядок за CONVFMT. Цілі значення POSIX вимагає друкувати як цілі
// незалежно від формату: інакше arr[1000000] став би ключем "1e+06".
[[nodiscard]] inline std::string format_number(double value, const char *convfmt)
{
    char buffer[64];            // довше за будь-яке представлення double
    int length;

    if (value == std::floor(value) && std::fabs(value) < 1e16)
        length = std::snprintf(buffer, sizeof buffer, "%.0f", value);
    else
        // Формат приходить із CONVFMT у РАНТАЙМІ — тому тут printf, а не
        // std::format: перевірити такий рядок на етапі компіляції нікому.
        length = std::snprintf(buffer, sizeof buffer, convfmt, value);

    if (length < 0)
        return {};
    if (static_cast<std::size_t>(length) >= sizeof buffer)
        length = static_cast<int>(sizeof buffer) - 1;
    return std::string(buffer, static_cast<std::size_t>(length));
}

class Node {
public:
    // Комірка за замовчуванням — неініціалізована змінна AWK: обидві форми
    // чинні одразу, тому обидва optional заповнені.
    Node() : origin_(Origin::Uninitialized), text_(std::string{}), number_(0.0) {}

    [[nodiscard]] static Node from_input(std::string text)
    {
        return Node(Origin::Input, std::move(text));
    }
    [[nodiscard]] static Node from_string(std::string text)
    {
        return Node(Origin::String, std::move(text));
    }
    [[nodiscard]] static Node from_number(double value)
    {
        Node node;
        node.origin_ = Origin::Number;
        node.text_.reset();          // рядкової форми ще немає
        node.number_ = value;
        return node;
    }

    [[nodiscard]] Origin origin() const noexcept { return origin_; }

    // Крок 2 і 3 з опису двоїстого стану: перше звертання платить за
    // strtod(), решта беруть готове. Метод не const саме тому, що кешує.
    [[nodiscard]] double as_number()
    {
        if (!number_)
            number_ = parse_prefix(*text_);
        return *number_;
    }

    [[nodiscard]] const std::string &as_string(const char *convfmt = kDefaultConvfmt)
    {
        if (!text_)
            text_ = format_number(*number_, convfmt);
        return *text_;
    }

    // Крок 4: рядкова мутація. Кеш числа й ознака «прийшло з вводу» гинуть —
    // після $1 = $1 "_x" поле більше не strnum і порівнюється як рядок.
    void assign_string(std::string text)
    {
        origin_ = Origin::String;
        text_ = std::move(text);
        number_.reset();
    }

    void assign_number(double value)
    {
        origin_ = Origin::Number;
        number_ = value;
        text_.reset();
    }

    // strnum: прийшло з вводу І синтаксично є числом.
    //
    // Тонкість, у якій ця модель свідомо розходиться з gawk: справжній gawk
    // вважає strnum-ом ще й порожнє (або з самих пробілів) поле зі значенням
    // 0, тому там $1 == 0 істинне для порожньої колонки. Тут порожнє поле
    // лишається рядком — і саме цю різницю фіксує тест.
    [[nodiscard]] bool is_strnum() const
    {
        return origin_ == Origin::Input && text_ && looks_numeric(*text_);
    }

    // Чи є в комірки чинна рядкова / числова форма — те, що в NODE.flags
    // позначалося б бітами STRCUR і NUMCUR.
    [[nodiscard]] bool has_string_form() const noexcept { return text_.has_value(); }
    [[nodiscard]] bool has_number_cache() const noexcept { return number_.has_value(); }

private:
    Node(Origin origin, std::string text)
        : origin_(origin), text_(std::move(text)), number_(std::nullopt) {}

    Origin origin_;
    std::optional<std::string> text_;    // STRCUR: рядкова форма актуальна
    std::optional<double> number_;       // NUMCUR: кеш перетворення
};

// std::partial_ordering підійшов би краще, але він із C++20, а модуль
// збирається під C++17 — розкладку структур розширення диктує gawk, і
// піднімати стандарт заради одного типу немає причин.
enum class Ordering { Less, Equal, Greater, Unordered };

// Матриця POSIX одним рядком: порівняння числове тоді й лише тоді, коли
// ЖОДЕН операнд не є справжнім рядком. Число проти рядка — рядкове.
[[nodiscard]] inline bool compares_numerically(const Node &a, const Node &b)
{
    const auto numeric_side = [](const Node &n) {
        return n.origin() == Origin::Number
            || n.origin() == Origin::Uninitialized
            || n.is_strnum();
    };
    return numeric_side(a) && numeric_side(b);
}

[[nodiscard]] inline Ordering compare(Node &a, Node &b,
                                      const char *convfmt = kDefaultConvfmt)
{
    if (compares_numerically(a, b)) {
        const double x = a.as_number();
        const double y = b.as_number();
        // NaN не менший, не більший і не рівний нічому — включно із собою.
        if (std::isnan(x) || std::isnan(y))
            return Ordering::Unordered;
        if (x < y) return Ordering::Less;
        if (x > y) return Ordering::Greater;
        return Ordering::Equal;
    }

    // Побайтове порівняння. Справжній awk у локалі з LC_COLLATE узяв би
    // strcoll(3), і тоді "a" < "B" стало б істинним — саме тому конвеєри
    // з sort(1) прийнято ганяти під LC_ALL=C.
    const int rc = a.as_string(convfmt).compare(b.as_string(convfmt));
    if (rc < 0) return Ordering::Less;
    if (rc > 0) return Ordering::Greater;
    return Ordering::Equal;
}

[[nodiscard]] inline bool equals(Node &a, Node &b, const char *convfmt = kDefaultConvfmt)
{
    return compare(a, b, convfmt) == Ordering::Equal;
}

[[nodiscard]] inline bool less_than(Node &a, Node &b, const char *convfmt = kDefaultConvfmt)
{
    return compare(a, b, convfmt) == Ordering::Less;
}

} // namespace awk::internals
