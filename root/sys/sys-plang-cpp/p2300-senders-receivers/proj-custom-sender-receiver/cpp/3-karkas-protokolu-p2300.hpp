namespace exec_model {

// Точки кастомізації каналів завершення
struct set_value_t {
    template <class Receiver, class... Args>
    void operator()(Receiver&& r, Args&&... args) const noexcept {
        std::forward<Receiver>(r).set_value(std::forward<Args>(args)...);
    }
};

struct set_error_t {
    template <class Receiver, class Error>
    void operator()(Receiver&& r, Error&& err) const noexcept {
        std::forward<Receiver>(r).set_error(std::forward<Error>(err));
    }
};

struct set_stopped_t {
    template <class Receiver>
    void operator()(Receiver&& r) const noexcept {
        std::forward<Receiver>(r).set_stopped();
    }
};

// Точки кастомізації життєвого циклу
struct connect_t {
    template <class Sender, class Receiver>
    auto operator()(Sender&& s, Receiver&& r) const {
        return std::forward<Sender>(s).connect(std::forward<Receiver>(r));
    }
};

struct start_t {
    template <class OpState>
    void operator()(OpState& op) const noexcept {
        op.start();
    }
};

inline constexpr set_value_t set_value{};
inline constexpr set_error_t set_error{};
inline constexpr set_stopped_t set_stopped{};
inline constexpr connect_t connect{};
inline constexpr start_t start{};

} // namespace exec_model
