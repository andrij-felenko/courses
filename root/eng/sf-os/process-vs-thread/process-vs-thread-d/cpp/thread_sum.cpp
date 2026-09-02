#include "thread_sum.hpp"

#include "chunking.hpp"

#include <atomic>
#include <iostream>
#include <new>
#include <numeric>
#include <thread>
#include <vector>

#include <unistd.h>

namespace {

#ifdef __cpp_lib_hardware_interference_size
constexpr std::size_t kCacheLine = std::hardware_destructive_interference_size;
#else
constexpr std::size_t kCacheLine = 64;
#endif

// Часткова сума кожного потоку — у власній кеш-лінії. Без alignas сусідні
// long long лягли б в одну лінію, і ядра ганяли б її між собою протоколом
// когерентності: класичне псевдорозділення (false sharing).
struct alignas(kCacheLine) Partial {
    long long value = 0;
};

// Одна комірка на ВЕСЬ процес: у неї пишуть усі потоки, тому вона атомарна.
std::atomic<long long> gVisits{ 0 };

// А ця змінна — приватна копія на КОЖЕН потік (сегмент TLS).
// Ні атомарності, ні замка тут не треба: сусід її просто не бачить.
thread_local long long tlsProcessed = 0;

} // namespace

long long sumWithThreads(std::span<const int> data, std::size_t workers)
{
    const auto pieces = splitEvenly(data, workers);

    std::vector<Partial> partials(workers);
    std::vector<std::thread::id> ids(workers);
    gVisits.store(0, std::memory_order_relaxed);

    auto work = [&](std::size_t i) {
        ids[i] = std::this_thread::get_id();
        partials[i].value = std::accumulate(pieces[i].begin(), pieces[i].end(), 0LL);
        tlsProcessed += static_cast<long long>(pieces[i].size());
        gVisits.fetch_add(1, std::memory_order_relaxed);
    };

    {
        std::vector<std::jthread> pool;
        pool.reserve(workers - 1);
        for (std::size_t i = 1; i < workers; ++i)
            pool.emplace_back(work, i);

        // Частку 0 бере на себе головний потік, а не чекає склавши руки.
        work(0);

        // Деструктор jthread сам приєднує потік — це RAII замість
        // розсипаних по гілках pthread_join(). Якщо emplace_back кине
        // виняток, уже створені потоки все одно буде приєднано тут.
    }

    long long total = 0;
    std::cout << "  PID процесу: " << ::getpid()
              << " (однаковий для всіх потоків)\n";
    for (std::size_t i = 0; i < workers; ++i) {
        total += partials[i].value;
        std::cout << "  потік " << ids[i] << ": " << pieces[i].size()
                  << " елементів -> " << partials[i].value << '\n';
    }
    std::cout << "  спільна gVisits = " << gVisits.load()
              << " (усі потоки писали в ту саму комірку)\n"
              << "  tlsProcessed головного потоку = " << tlsProcessed
              << " з " << data.size() << " (у кожного потоку своя копія)\n";

    return total;
}
