// Концептуальна структура std::function у 64-бітних реалізаціях
template <typename R, typename... Args>
class function<R(Args...)> {
private:
    using invoker_t = R(*)(const void*, Args&&...);
    invoker_t invoker_{nullptr};

    // Об'єднання для SBO та алокації у купі
    union Storage {
        alignas(std::max_align_t) char sbo_buffer[24]; // 24 байти для SBO
        void* heap_ptr;                                // Вказівник на купу, якщо size > 24
    } storage_;
};
