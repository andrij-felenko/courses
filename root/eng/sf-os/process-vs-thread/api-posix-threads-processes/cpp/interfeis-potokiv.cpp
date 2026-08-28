#include <thread>
#include <future>
#include <stop_token>
#include <concepts>

// Стандартний інтерфейс багатопотоковості C++20
namespace std {
    class thread;
    class jthread; // RAII-потік з автоматичним join та stop_token
    template<typename Function, typename... Args>
    [[nodiscard]] auto async(Function&& f, Args&&... args);
}
