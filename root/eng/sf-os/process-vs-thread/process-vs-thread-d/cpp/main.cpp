#include "process_sum.hpp"
#include "thread_sum.hpp"

#include <chrono>
#include <cstddef>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <utility>
#include <vector>

namespace {

constexpr std::size_t kCount = 8 * 1024 * 1024;   // ≈ 32 МіБ int-ів
constexpr std::size_t kWorkers = 4;

// Міряє час виклику й повертає пару {результат, мілісекунди}.
template <class F>
auto timed(F &&fn)
{
    const auto start = std::chrono::steady_clock::now();
    auto value = fn();
    const std::chrono::duration<double, std::milli> elapsed =
        std::chrono::steady_clock::now() - start;
    return std::pair{ std::move(value), elapsed.count() };
}

} // namespace

int main()
{
    std::vector<int> data(kCount);
    for (std::size_t i = 0; i < data.size(); ++i)
        data[i] = static_cast<int>(i % 7) - 3;

    const long long reference = std::accumulate(data.begin(), data.end(), 0LL);
    std::cout << std::fixed << std::setprecision(2);

    std::cout << "--- ПОТОКИ: спільний адресний простір, обмін через покажчик ---\n";
    const auto [threadTotal, threadMs] =
        timed([&] { return sumWithThreads(data, kWorkers); });
    std::cout << "  сума = " << threadTotal << ", час = " << threadMs << " мс\n\n";

    std::cout << "--- ПРОЦЕСИ: копія-при-записі, обмін через канал ---\n";
    // Форкаємо, коли всі робочі потоки вже приєднані. fork() копіює ЛИШЕ
    // потік-викликач, тож м'ютекс, захоплений чужим потоком, застряг би в
    // дитині захопленим назавжди — і перший же malloc там став би дедлоком.
    const auto [processTotal, processMs] =
        timed([&] { return sumWithProcesses(data, kWorkers); });
    if (!processTotal) {
        std::cerr << "процеси: " << processTotal.error().message() << '\n';
        return EXIT_FAILURE;
    }
    std::cout << "  сума = " << *processTotal << ", час = " << processMs << " мс\n\n";

    std::cout << "контроль = " << reference << "; обидві відповіді збіглися: "
              << ((threadTotal == reference && *processTotal == reference) ? "так" : "НІ")
              << '\n';
    return 0;
}
