#include <variant>
#include <string>
#include <iostream>

// Патерн перевантаження для std::visit
template<class... Ts> struct overloaded : Ts... { using Ts::operator()...; };
template<class... Ts> overloaded(Ts...) -> overloaded<Ts...>;

using Command = std::variant<int, std::string, double>;

void process_command(const Command& cmd) {
    std::visit(overloaded {
        [](int val) { std::cout << "Команда скидання: " << val << "\n"; },
        [](const std::string& str) { std::cout << "Текстова команда: " << str << "\n"; },
        [](double timeout) { std::cout << "Таймаут: " << timeout << "с\n"; }
    }, cmd);
}
