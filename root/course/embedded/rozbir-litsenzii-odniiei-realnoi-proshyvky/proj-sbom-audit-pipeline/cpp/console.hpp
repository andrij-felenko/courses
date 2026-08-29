// console.hpp — службова консоль UART/USB CDC.
//
// Вивід приймаємо як WriterRef — невласницьке посилання на будь-що викличне
// (стенд підсуне лямбду з накопиченням у рядок, прошивка — обгортку HAL_UART).
// Ні std::function, ні віртуальних таблиць: купи на мікроконтролері немає.
#ifndef FW_CONSOLE_HPP
#define FW_CONSOLE_HPP

#include <array>
#include <concepts>
#include <cstddef>
#include <expected>
#include <memory>
#include <span>
#include <string_view>
#include <type_traits>

namespace fw {

// Спрощений std::function_ref (той з'явився аж у C++26).
class WriterRef {
public:
    template <typename Sink>
        requires std::invocable<Sink&, std::string_view>
              && (!std::same_as<std::remove_cvref_t<Sink>, WriterRef>)
    constexpr WriterRef(Sink& sink) noexcept
        : sink_(std::addressof(sink)),
          call_([](void* self, std::string_view text) {
              (*static_cast<Sink*>(self))(text);
          }) {}

    void operator()(std::string_view text) const { call_(sink_, text); }

private:
    void* sink_;
    void (*call_)(void*, std::string_view);
};

enum class ConsoleError {
    Empty,            // порожній рядок — не помилка, просто нічого робити
    UnknownCommand,
    BadArgument,
    LineTooLong,
};

constexpr std::string_view describe(ConsoleError error) noexcept
{
    switch (error) {
    case ConsoleError::Empty:          return "порожній рядок";
    case ConsoleError::UnknownCommand: return "невідома команда, спробуйте help";
    case ConsoleError::BadArgument:    return "хибний аргумент";
    case ConsoleError::LineTooLong:    return "рядок задовгий, його відкинуто";
    }
    return "невідома помилка";
}

using CommandResult = std::expected<void, ConsoleError>;

struct Command {
    std::string_view name;
    std::string_view help;
    CommandResult (*run)(std::string_view args, WriterRef out);
};

class Console {
public:
    static constexpr std::size_t kLineMax = 96;

    Console(WriterRef out, std::span<const Command> commands) noexcept
        : out_(out), commands_(commands) {}

    void greet() const;

    // Один байт із приймача. Викликати з задачі, не з переривання:
    // всередині є друк, а він блокує.
    void feed(char byte);

    // Розібрати й виконати готовий рядок.
    CommandResult execute(std::string_view line) const;

private:
    void prompt() const;
    CommandResult print_help() const;

    WriterRef out_;
    std::span<const Command> commands_;
    std::array<char, kLineMax> line_{};
    std::size_t length_{0};
    bool overflow_{false};
};

}  // namespace fw

#endif  // FW_CONSOLE_HPP
