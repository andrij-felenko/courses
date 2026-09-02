// ttyxx — розбір, псування й відновлення стану термінала мовою C++:
//
//   ttyxx dump             розбір поточного termios у словах stty + діагноз
//   ttyxx abi              розкладка struct termios і ядрової struct termios2
//   ttyxx sane | cooked    застосувати профіль із перевіркою
//   ttyxx raw              сирий режим: коди клавіш, поки не натиснуто q
//   ttyxx reset            escape-скидання модальних регістрів емулятора
//   ttyxx baud <dev> [n]   швидкість лінії числом; із n — довільна через BOTHER
//   ttyxx pty <cmd> …      запуск команди під PTY у пакетному режимі
#include "abi.hpp"
#include "baud.hpp"
#include "flags.hpp"
#include "pty_session.hpp"
#include "terminal.hpp"

#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <format>
#include <print>
#include <span>
#include <string>
#include <string_view>
#include <system_error>

#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>

namespace {

void write_line(std::string_view text) noexcept
{
    // У сирому режимі OPOST вимкнено: сам \n лише опустить курсор,
    // не повернувши його до нульової колонки.
    (void)::write(STDOUT_FILENO, text.data(), text.size());
}

int cmd_dump()
{
    const auto t = tty::attributes(STDIN_FILENO);
    if (!t) {
        std::print(stderr, "tcgetattr: {}\n", t.error().message());
        return 1;
    }

    winsize ws{};
    if (::ioctl(STDIN_FILENO, TIOCGWINSZ, &ws) == 0)
        std::print("вікно: {} рядків, {} стовпчиків, {} x {} пікселів\n",
                   ws.ws_row, ws.ws_col, ws.ws_xpixel, ws.ws_ypixel);

    std::print("{}", tty::describe(*t));

    const std::string report = tty::diagnose(*t);
    std::print("\n{}", report.empty() ? "діагноз: типових поломок не видно\n" : report);
    return 0;
}

int cmd_profile(std::string_view name)
{
    const auto t = tty::attributes(STDIN_FILENO);
    if (!t) {
        std::print(stderr, "tcgetattr: {}\n", t.error().message());
        return 1;
    }

    const termios want = (name == "sane") ? tty::make_sane(*t) : tty::make_cooked(*t);
    // TCSADRAIN — як робить сама stty: спершу дати дописати те, що вже
    // в черзі виводу, і аж тоді міняти правила під ним.
    if (const auto ok = tty::apply_verified(STDIN_FILENO, TCSADRAIN, want); !ok) {
        std::print(stderr, "профіль {} застосовано не повністю: {}\n",
                   name, ok.error().message());
        return 1;
    }
    std::print("профіль {} застосовано\n", name);
    return 0;
}

int cmd_raw()
{
    try {
        // VMIN = 1, VTIME = 0 — квадрант чистого блокування: read() чекає
        // рівно на один байт і ніколи не повертає 0 через таймер.
        tty::RawMode raw{STDIN_FILENO, 1, 0};
        tty::SignalGuard guard{raw};

        write_line("сирий режим: показую коди клавіш; вихід — q\r\n");

        for (;;) {
            unsigned char c = 0;
            switch (tty::read_byte(STDIN_FILENO, c)) {
            case tty::ReadResult::Interrupted: {
                // read() перервано сигналом (типово SIGWINCH) — це не
                // помилка: обробляємо подію й повторюємо виклик.
                if (tty::SignalGuard::window_resized()) {
                    winsize ws{};
                    if (::ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0)
                        write_line(std::format("SIGWINCH: {} x {}\r\n",
                                               ws.ws_col, ws.ws_row));
                }
                continue;
            }
            case tty::ReadResult::Eof:
                return 0;
            case tty::ReadResult::Error:
                return 1;
            case tty::ReadResult::Byte:
                break;
            }

            if (c == 0x7F)
                write_line(std::format("0x{:02X}  ^?\r\n", c));
            else if (c < 0x20)
                write_line(std::format("0x{:02X}  ^{}\r\n", c,
                                       static_cast<char>(c + 64)));
            else
                write_line(std::format("0x{:02X}  '{}'\r\n", c,
                                       static_cast<char>(c)));
            if (c == 'q')
                return 0;
        }
    } catch (const std::system_error& e) {
        std::print(stderr, "сирий режим: {}\n", e.code().message());
        return 1;
    }
}

// Швидкість беремо з ПРИСТРОЮ, а не зі stdin: довільний бодрейт має сенс
// лише на справжньому UART — псевдотермінал проковтне будь-яке число
// мовчки, і перевірити нічого не вийде.
int cmd_baud(std::span<char* const> args)
{
    const char* dev = args[0];
    // O_NONBLOCK на відкритті: без CLOCAL ядро тримало б open() доти,
    // доки на лінії не з'явиться сигнал носія DCD.
    tty::Fd fd{::open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK)};
    if (!fd) {
        std::print(stderr, "{}: {}\n", dev,
                   std::error_code(errno, std::generic_category()).message());
        return 1;
    }

    if (args.size() < 2) {
        const auto rate = tty::line_speed(fd.get());
        if (!rate) {
            std::print(stderr, "TCGETS2: {}\n", rate.error().message());
            return 1;
        }
        std::print("{}: {} бод\n", dev, *rate);
        return 0;
    }

    char* end = nullptr;
    const unsigned long want = std::strtoul(args[1], &end, 10);
    if (end == args[1] || *end != '\0' || want == 0) {
        std::print(stderr, "швидкість має бути додатним числом бод\n");
        return 2;
    }

    const auto got = tty::set_line_speed(fd.get(), want);
    if (!got) {
        std::print(stderr, "TCSETS2: {}\n", got.error().message());
        return 1;
    }
    std::print("{}: просили {} бод, ядро виставило {}\n", dev, want, *got);
    return 0;
}

int cmd_pty(std::span<char* const> argv)
{
    auto master = tty::PtyMaster::open();
    if (!master) {
        std::print(stderr, "openpt: {}\n", master.error().message());
        return 1;
    }
    if (const auto child = master->spawn(argv); !child) {
        std::print(stderr, "spawn: {}\n", child.error().message());
        return 1;
    }
    const auto rc = master->run();
    if (!rc) {
        std::print(stderr, "цикл ведучого: {}\n", rc.error().message());
        return 1;
    }
    return *rc;
}

void usage(const char* argv0)
{
    std::print(stderr,
               "вжиток: {} dump | abi | sane | cooked | raw | reset"
               " | baud <dev> [бод] | pty <cmd> …\n",
               argv0);
}

}  // namespace

int main(int argc, char* argv[])
{
    if (argc < 2) {
        usage(argv[0]);
        return 2;
    }

    const std::string_view cmd{argv[1]};
    const std::span<char* const> rest(argv + 2,
                                      static_cast<std::size_t>(argc - 2));

    if (cmd == "dump")
        return cmd_dump();
    if (cmd == "abi") {
        std::print("{}", tty::abi_report());
        return 0;
    }
    if (cmd == "sane" || cmd == "cooked")
        return cmd_profile(cmd);
    if (cmd == "raw")
        return cmd_raw();
    if (cmd == "reset") {
        tty::emulator_reset(STDOUT_FILENO);
        if (const auto t = tty::attributes(STDIN_FILENO); t)
            (void)tty::apply_verified(STDIN_FILENO, TCSANOW, tty::make_sane(*t));
        std::print("емулятор і termios скинуто\n");
        return 0;
    }
    if (cmd == "baud") {
        if (rest.empty()) {
            usage(argv[0]);
            return 2;
        }
        return cmd_baud(rest);
    }
    if (cmd == "pty") {
        if (rest.empty()) {
            usage(argv[0]);
            return 2;
        }
        return cmd_pty(rest);
    }

    usage(argv[0]);
    return 2;
}
