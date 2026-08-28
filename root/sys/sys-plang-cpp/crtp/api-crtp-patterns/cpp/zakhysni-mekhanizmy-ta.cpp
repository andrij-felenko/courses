#include <concepts>
#include <type_traits>

template <typename Derived>
class StaticInterface {
private:
    StaticInterface() = default;
    friend Derived;

public:
    void execute() noexcept(noexcept(std::declval<Derived&>().execute_impl())) {
        Derived& self = *static_cast<Derived*>(this);
        
        static_assert(requires(Derived d) { d.execute_impl(); },
            "Похідний клас зобов'язаний реалізувати void execute_impl()");
            
        self.execute_impl();
    }

    void execute() const noexcept(noexcept(std::declval<const Derived&>().execute_impl())) {
        const Derived& self = *static_cast<const Derived*>(this);
        
        static_assert(requires(const Derived d) { d.execute_impl(); },
            "Похідний клас зобов'язаний реалізувати void execute_impl() const");
            
        self.execute_impl();
    }
};
