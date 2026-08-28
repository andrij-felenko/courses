#include <iostream>
#include <functional>
#include <type_traits>

template<typename Receiver, typename ReturnType, typename... Args>
class EventObserver {
public:
    using MethodPtr = ReturnType (Receiver::*)(Args...);

    EventObserver(MethodPtr method, Receiver* instance)
        : m_method(method), m_instance(instance) {}

    ReturnType trigger(Args... args) const {
        if (m_instance && m_method) {
            return (m_instance->*m_method)(std::forward<Args>(args)...);
        }
        if constexpr (!std::is_void_v<ReturnType>) {
            return ReturnType{};
        }
    }

private:
    MethodPtr m_method = nullptr;
    Receiver* m_instance = nullptr;
};

// -----------------------------------------------------------------------------
// Керівне правило виведення для покажчиків на методи
// -----------------------------------------------------------------------------

template<typename Receiver, typename ReturnType, typename... Args>
EventObserver(ReturnType (Receiver::*)(Args...), Receiver*)
    -> EventObserver<Receiver, ReturnType, Args...>;
