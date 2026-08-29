#include <optional>

#include "fault_status.hpp"
#include "provoke.hpp"
#include "reset_cause.hpp"
#include "trace.hpp"
#include "watchdog.hpp"

namespace {

void print_menu()
{
    trace::out.line("\r\nстенд аварій (натисни цифру):");
    for (const provoke::Case& item : provoke::catalogue()) {
        trace::out.line("  ", item.key, ' ', item.label);
    }
}

} // namespace

int main()
{
    // Порядок важливий. Спершу UART — інакше звіт нікуди друкувати. Далі
    // прапорці скидання, поки їх ніхто не стер. І лише потім усе решта.
    trace::out.init();

    const reset::Causes& causes = reset::capture();

    trace::out.line("\r\n=== старт прошивки ===");
    causes.print();

    if (causes.looks_like_crash()) {
        trace::out.line("попередній запуск завершився крахом");
    }

    fault::enable_all_handlers();

    watchdog::Independent dog;
    dog.start();

    print_menu();

    for (;;) {
        dog.kick();

        if (const std::optional<char> key = trace::out.read()) {
            if (!provoke::run(*key)) {
                print_menu(); // натиснуто щось стороннє — показуємо меню знову
            }
        }
    }
}
