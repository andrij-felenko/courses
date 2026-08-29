// rack-slot — керування одним слотом тестової стійки з CI-джоби.
//
//   rack-slot 3 boot            холодний старт і очікування банера
//   rack-slot 3 flash fw.hex    прошити образ і дочекатися банера
//   rack-slot 3 unbrick         реанімація через фабричний ROM-завантажувач
//
// Коди виходу: 0 — гаразд, 1 — помилка, 2 — слот зайнятий, 3 — плата мовчить.
#include <charconv>
#include <cstdio>
#include <cstring>
#include <span>
#include <string_view>

#include <csignal>
#include <unistd.h>

#include "slot_session.hpp"

volatile std::sig_atomic_t gStopRequested = 0;

namespace {

using namespace std::chrono_literals;

constexpr auto kLockWait = 30s;
constexpr auto kBootTimeout = 5s;
constexpr std::string_view kBootBanner = "[BOOT]";

extern "C" void onSignal(int) noexcept
{
    gStopRequested = 1;
}

void installHandlers()
{
    struct sigaction sa {};
    sa.sa_handler = onSignal;
    ::sigemptyset(&sa.sa_mask);
    // Свідомо без SA_RESTART: select у циклі очікування має ВИЙТИ з EINTR,
    // інакше демон досидить до кінця таймауту, тримаючи слот за собою.
    ::sigaction(SIGINT, &sa, nullptr);
    ::sigaction(SIGTERM, &sa, nullptr);

    // CI закриває свій кінець пайпа, щойно джобу скасовано. Обірваний stdout
    // не має вбивати сесію: слот ще треба знеструмити й відпустити.
    ::signal(SIGPIPE, SIG_IGN);
}

void usage(const char* argv0)
{
    std::fprintf(stderr, "вжиток: %s <слот 1..99> boot | flash <образ> | unbrick\n", argv0);
}

int parseSlotId(std::string_view text)
{
    int value = 0;
    const auto* last = text.data() + text.size();
    const auto [ptr, ec] = std::from_chars(text.data(), last, value);
    if (ec != std::errc{} || ptr != last || value < 1 || value > 99) {
        throw std::runtime_error{"номер слота має бути числом 1..99"};
    }
    return value;
}

} // namespace

int main(int argc, char** argv)
{
    const std::span<char*> args{argv, static_cast<std::size_t>(argc)};
    if (args.size() < 3) {
        usage(args[0]);
        return 1;
    }

    installHandlers();

    try {
        const int slotId = parseSlotId(args[1]);
        const std::string_view command = args[2];

        auto session = SlotSession::acquire(slotId, kLockWait, STDOUT_FILENO);

        if (command == "boot") {
            session.boot(kBootBanner, kBootTimeout);
        } else if (command == "flash") {
            if (args.size() < 4) {
                usage(args[0]);
                return 1;
            }
            session.flash(args[3]);
            // openocd сам пустив плату командою reset — ловимо той самий банер.
            session.console().expect(kBootBanner, kBootTimeout);
        } else if (command == "unbrick") {
            session.unbrick();
            // Після стирання банера не буде — просто показуємо, що каже плата.
            session.console().drain(500ms);
        } else {
            usage(args[0]);
            return 1;
        }
        // Тут SlotSession знеструмлює слот і знімає flock — у будь-якому разі,
        // хоч поверненням, хоч виходом через виняток.
        return 0;
    } catch (const SlotBusy& e) {
        std::fprintf(stderr, "%s\n", e.what());
        return 2;
    } catch (const ConsoleTimeout& e) {
        std::fprintf(stderr, "%s\n", e.what());
        return 3;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "помилка: %s\n", e.what());
        return 1;
    }
}
