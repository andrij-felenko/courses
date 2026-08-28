#include <chrono>
#include <thread>
#include <functional>

/* Ідіоматична C++ реалізація з лямбда-предикатом та std::chrono */
template <typename Predicate>
bool waitUntil(Predicate&& predicate,
               std::chrono::milliseconds timeout,
               std::chrono::milliseconds pollInterval = std::chrono::milliseconds(10)) {
    const auto startTime = std::chrono::steady_clock::now();

    while (true) {
        if (predicate()) {
            return true; // Подія настала
        }

        const auto elapsed = std::chrono::steady_clock::now() - startTime;
        if (elapsed >= timeout) {
            return false; // Таймаут
        }

        std::this_thread::sleep_for(pollInterval);
    }
}
