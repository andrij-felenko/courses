// console.cpp — збирання рядка з потоку байтів і диспетчер команд.
#include "console.hpp"

#include <algorithm>
#include <ranges>

namespace fw {
namespace {

constexpr std::string_view kPrompt = "fw> ";
constexpr std::string_view kSpaces = " \t";

constexpr std::string_view trim_left(std::string_view text) noexcept
{
    const auto pos = text.find_first_not_of(kSpaces);
    return pos == std::string_view::npos ? std::string_view{} : text.substr(pos);
}

}  // namespace

void Console::prompt() const
{
    out_(kPrompt);
}

void Console::greet() const
{
    out_("\r\nСлужбова консоль прошивки. help — перелік команд.\r\n");
    prompt();
}

CommandResult Console::print_help() const
{
    out_("\r\nДоступні команди:\r\n");
    for (const Command& command : commands_) {
        out_("  ");
        out_(command.name);
        out_("\t— ");
        out_(command.help);
        out_("\r\n");
    }
    out_("  help\t— цей перелік\r\n");
    return {};
}

CommandResult Console::execute(std::string_view line) const
{
    line = trim_left(line);
    if (line.empty()) {
        return std::unexpected(ConsoleError::Empty);
    }

    const auto split = line.find_first_of(kSpaces);
    const std::string_view name = line.substr(0, split);
    const std::string_view args =
        split == std::string_view::npos ? std::string_view{}
                                        : trim_left(line.substr(split));

    if (name == "help") {
        return print_help();
    }

    const auto it = std::ranges::find(commands_, name, &Command::name);
    if (it == commands_.end()) {
        return std::unexpected(ConsoleError::UnknownCommand);
    }
    return it->run(args, out_);
}

void Console::feed(char byte)
{
    if (byte == '\r' || byte == '\n') {
        out_("\r\n");

        const CommandResult result =
            overflow_ ? CommandResult{std::unexpected(ConsoleError::LineTooLong)}
                      : execute(std::string_view(line_.data(), length_));

        if (!result && result.error() != ConsoleError::Empty) {
            out_("помилка: ");
            out_(describe(result.error()));
            out_("\r\n");
        }

        length_ = 0;
        overflow_ = false;
        prompt();
        return;
    }

    // Забій стирає символ і в буфері, і на екрані.
    if (byte == '\b' || byte == '\x7f') {
        if (length_ > 0 && !overflow_) {
            --length_;
            out_("\b \b");
        }
        return;
    }

    if (byte == '\x03') {           // Ctrl-C — кинути набране
        length_ = 0;
        overflow_ = false;
        out_("^C\r\n");
        prompt();
        return;
    }

    // Керівні байти в буфер не пускаємо: стрілки термінала приходять
    // escape-послідовностями й інакше пролізли б у назву команди.
    const auto raw = static_cast<unsigned char>(byte);
    if (raw < 0x20 || raw == 0x1b) {
        return;
    }

    if (length_ == line_.size()) {
        overflow_ = true;           // решту рядка дочитуємо й викидаємо цілком
        return;
    }

    line_[length_++] = byte;
    out_(std::string_view(&line_[length_ - 1], 1));
}

}  // namespace fw
