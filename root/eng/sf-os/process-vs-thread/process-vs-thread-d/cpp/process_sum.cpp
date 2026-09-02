#include "process_sum.hpp"

#include "chunking.hpp"
#include "fd.hpp"

#include <cerrno>
#include <iostream>
#include <numeric>
#include <vector>

#include <sys/wait.h>
#include <unistd.h>

namespace {

struct Child {
    ::pid_t pid = -1;
    Fd result;                    // кінець каналу на читання
    std::size_t size = 0;
};

// Та сама глобальна змінна, що й у потоковому варіанті, але чіпають її діти.
// Батько своєї копії зміненою не побачить: сторінка роздвоїться при записі.
long long gVisits = 0;

[[noreturn]] void runChild(const Fd &writeEnd, std::span<const int> piece)
{
    // Масив дістався дитині копією-при-записі: ті самі адреси, ті самі
    // фізичні сторінки, поки ніхто не пише. Ми лише читаємо — тож 32 МіБ
    // насправді нікуди не копіюються.
    const long long part = std::accumulate(piece.begin(), piece.end(), 0LL);
    gVisits += 1;   // а ось цей запис у .bss сторінку таки роздвоює

    const std::error_code ec =
        writeExactly(writeEnd.get(), std::as_bytes(std::span<const long long, 1>(&part, 1)));

    // Після fork у програмі з потоками дозволені тільки async-signal-safe
    // виклики й _exit(): ані iostream, ані malloc, ані розкрутки стека з
    // деструкторами — м'ютекси чужих потоків лишилися захопленими навіки.
    ::_exit(ec ? 1 : 0);
}

} // namespace

std::expected<long long, std::error_code> sumWithProcesses(std::span<const int> data,
                                                           std::size_t workers)
{
    if (workers == 0)
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));

    const auto pieces = splitEvenly(data, workers);
    std::vector<Child> kids;
    kids.reserve(workers);
    gVisits = 0;

    std::error_code failure;

    for (std::size_t i = 0; i < workers; ++i) {
        auto channel = Pipe::create();
        if (!channel) {
            failure = channel.error();
            break;
        }

        const ::pid_t pid = ::fork();
        if (pid < 0) {
            failure = { errno, std::generic_category() };
            break;
        }
        if (pid == 0) {
            channel->readEnd.reset();   // дитині кінець на читання не потрібен
            runChild(channel->writeEnd, pieces[i]);
        }

        // Батько закриває кінець на запис одразу: поки він відкритий бодай в
        // одному процесі, read() не побачить EOF.
        channel->writeEnd.reset();
        kids.push_back(Child{ pid, std::move(channel->readEnd), pieces[i].size() });
    }

    long long total = 0;
    for (auto &kid : kids) {
        long long part = 0;
        const std::error_code ec =
            readExactly(kid.result.get(),
                        std::as_writable_bytes(std::span<long long, 1>(&part, 1)));
        if (ec) {
            if (!failure)
                failure = ec;
            continue;   // поховати дитину все одно доведеться нижче
        }
        total += part;
        std::cout << "  дитина PID=" << kid.pid << ": " << kid.size
                  << " елементів -> " << part << '\n';
    }

    // Дитину, якої не діждалися через waitpid(), ядро тримає зомбі.
    for (auto &kid : kids) {
        int status = 0;
        while (::waitpid(kid.pid, &status, 0) < 0) {
            if (errno != EINTR)
                break;
        }
        if (!(WIFEXITED(status) && WEXITSTATUS(status) == 0) && !failure)
            failure = std::make_error_code(std::errc::io_error);
    }

    std::cout << "  gVisits у батька = " << gVisits
              << ": записи дітей пішли в їхні власні копії сторінок\n";

    if (failure)
        return std::unexpected(failure);
    return total;
}
