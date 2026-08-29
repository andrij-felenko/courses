#include "programmer.hpp"

#include <array>
#include <cstdio>
#include <cstring>
#include <format>
#include <stdexcept>
#include <vector>

#include <fcntl.h>
#include <sys/wait.h>
#include <unistd.h>

#include "posix.hpp"

namespace {

constexpr auto kProgramTimeout = std::chrono::seconds{120};
constexpr auto kEraseTimeout = std::chrono::seconds{60};
constexpr auto kGrace = std::chrono::seconds{2};

// Дочекатися openocd, а якщо він завис на мертвому SWD — прибрати його.
// Повертає true лише за чистого нульового виходу.
bool waitOpenocd(pid_t pid, std::chrono::seconds timeout) noexcept
{
    auto deadline = std::chrono::steady_clock::now() + timeout;
    bool askedToStop = false;
    bool killed = false;

    for (;;) {
        int status = 0;
        const pid_t r = ::waitpid(pid, &status, WNOHANG);

        if (r == pid) {
            if (WIFEXITED(status)) {
                const int code = WEXITSTATUS(status);
                if (code == 0) {
                    return true;
                }
                std::fprintf(stderr, "openocd завершився з кодом %d\n", code);
                return false;
            }
            std::fprintf(stderr, "openocd убито сигналом %d\n",
                         WIFSIGNALED(status) ? WTERMSIG(status) : 0);
            return false;
        }
        if (r < 0) {
            if (errno == EINTR) {
                continue;
            }
            std::fprintf(stderr, "waitpid(openocd): %s\n", std::strerror(errno));
            return false;
        }

        if (std::chrono::steady_clock::now() >= deadline || gStopRequested) {
            if (!askedToStop) {
                // Найчастіша причина зависання — мертвий SWD: адаптер чекає на
                // відповідь ядра, якого вже немає. Спершу просимо по-доброму.
                std::fprintf(stderr, "openocd не вкладається в час — SIGTERM\n");
                ::kill(pid, SIGTERM);
                askedToStop = true;
                deadline = std::chrono::steady_clock::now() + kGrace;
            } else if (!killed) {
                ::kill(pid, SIGKILL);
                killed = true;
                deadline = std::chrono::steady_clock::now() + kGrace;
            }
            // Після SIGKILL лишається тільки прибрати зомбі — цикл це й робить.
        }
        ::usleep(50 * 1000);
    }
}

} // namespace

bool Programmer::tryOpenocd(std::span<const std::string> commands, std::chrono::seconds timeout)
{
    // Налагоджувачі стійки мають серійні номери DUT01…DUTnn; за тим самим номером
    // udev будує /dev/dut-slot-XX-swd, тож ми й openocd говоримо про один адаптер.
    const std::array<std::string, 7> head{
        "openocd",
        "-f", "interface/cmsis-dap.cfg",
        "-c", std::format("adapter serial DUT{:02d}", slotId_),
        "-f", "target/stm32f4x.cfg",
    };

    // Рядки мусять пережити exec, тому argv збираємо з посилань на них.
    std::vector<char*> argv;
    argv.reserve(head.size() + 2 * commands.size() + 1);
    for (const auto& arg : head) {
        argv.push_back(const_cast<char*>(arg.c_str()));
    }
    for (const auto& cmd : commands) {
        argv.push_back(const_cast<char*>("-c"));
        argv.push_back(const_cast<char*>(cmd.c_str()));
    }
    argv.push_back(nullptr);

    const pid_t pid = ::fork();
    if (pid < 0) {
        std::fprintf(stderr, "fork: %s\n", std::strerror(errno));
        return false;
    }

    if (pid == 0) {
        // Наш stdout — це живий потік консолі плати, який читає CI. Балаканину
        // openocd зводимо в stderr, щоб вона не змішалася з логом завантаження.
        if (::dup2(STDERR_FILENO, STDOUT_FILENO) < 0) {
            ::_exit(126);
        }
        const int devnull = ::open("/dev/null", O_RDONLY | O_CLOEXEC);
        if (devnull >= 0) {
            ::dup2(devnull, STDIN_FILENO);
            ::close(devnull);
        }
        ::execvp("openocd", argv.data());
        std::fprintf(stderr, "не запускається openocd: %s\n", std::strerror(errno));
        ::_exit(127);
    }

    return waitOpenocd(pid, timeout);
}

void Programmer::runOpenocd(std::span<const std::string> commands, std::chrono::seconds timeout)
{
    if (!tryOpenocd(commands, timeout)) {
        throw std::runtime_error{std::format("слот {:02d}: openocd не впорався", slotId_)};
    }
}

void Programmer::program(const std::filesystem::path& image)
{
    std::error_code ec;
    if (!std::filesystem::is_regular_file(image, ec)) {
        throw std::runtime_error{std::format("образ {} не читається", image.string())};
    }

    // Шлях загортаємо у фігурні дужки Tcl: інакше пробіл у назві розлетівся б
    // на два аргументи команди program.
    const std::array<std::string, 3> cmds{
        "init",
        "reset halt",
        std::format("program {{{}}} verify reset exit", image.string()),
    };
    runOpenocd(cmds, kProgramTimeout);
}

void Programmer::massErase()
{
    const std::array<std::string, 4> erase{"init", "reset halt", "stm32f4x mass_erase 0",
                                           "shutdown"};
    if (tryOpenocd(erase, kEraseTimeout)) {
        return;
    }

    // Стирання не пройшло — найімовірніше стоїть захист читання RDP Level 1:
    // у цьому стані flash недоступна взагалі. Зняття захисту саме по собі стирає
    // кристал повністю, тож другої спроби mass_erase уже не треба.
    std::fprintf(stderr, "слот %02d: mass_erase не пройшов, пробую зняти RDP\n", slotId_);
    const std::array<std::string, 3> unlock{"init", "stm32f4x unlock 0", "shutdown"};
    runOpenocd(unlock, kEraseTimeout);
}
