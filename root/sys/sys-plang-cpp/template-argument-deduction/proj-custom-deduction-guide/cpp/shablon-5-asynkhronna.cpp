#include <iostream>
#include <functional>
#include <future>
#include <type_traits>
#include <tuple>

template<typename Callable, typename... Args>
class ThreadPoolTask {
public:
    using return_type = std::invoke_result_t<Callable, Args...>;

    explicit ThreadPoolTask(Callable fn, Args... args)
        : m_func(std::move(fn)), m_args(std::move(args)...) {}

    return_type execute() {
        return std::apply(m_func, m_args);
    }

private:
    Callable m_func;
    std::tuple<Args...> m_args;
};

// Керівне правило виведення для обгортки завдання
template<typename Callable, typename... Args>
ThreadPoolTask(Callable, Args...) 
    -> ThreadPoolTask<std::decay_t<Callable>, std::decay_t<Args>...>;
