#include <concepts>

template <typename T>
concept CanProcess = requires(T t) {
    { t.process_impl() } -> std::same_as<void>;
};

template <typename Derived>
class ValidatedCRTP {
public:
    void process() {
        static_assert(CanProcess<Derived>,
            "Похідний клас зобов'язаний надати метод 'void process_impl()'");
        static_cast<Derived*>(this)->process_impl();
    }
};
