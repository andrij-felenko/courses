// Адаптований приймач, що викликає користувацьку функцію func_
template <class DownstreamReceiver, class Func>
class then_receiver {
public:
    then_receiver(DownstreamReceiver rcvr, Func f)
        : downstream_(std::move(rcvr)), func_(std::move(f)) {}

    template <class... Args>
    void set_value(Args&&... args) noexcept {
        try {
            if constexpr (std::is_void_v<std::invoke_result_t<Func, Args...>>) {
                std::invoke(func_, std::forward<Args>(args)...);
                exec_model::set_value(std::move(downstream_));
            } else {
                auto res = std::invoke(func_, std::forward<Args>(args)...);
                exec_model::set_value(std::move(downstream_), std::move(res));
            }
        } catch (...) {
            // Перехоплюємо будь-які винятки користувача та автоматично направляємо у set_error
            exec_model::set_error(std::move(downstream_), std::current_exception());
        }
    }

    template <class Error>
    void set_error(Error&& err) noexcept {
        exec_model::set_error(std::move(downstream_), std::forward<Error>(err));
    }

    void set_stopped() noexcept {
        exec_model::set_stopped(std::move(downstream_));
    }

private:
    DownstreamReceiver downstream_;
    Func func_;
};

// Складений сендер для адаптера then
template <class PrevSender, class Func>
class then_sender {
public:
    then_sender(PrevSender prev, Func f)
        : prev_(std::move(prev)), func_(std::move(f)) {}

    template <class Receiver>
    auto connect(Receiver&& rcvr) && {
        using adapted_rcvr_t = then_receiver<std::decay_t<Receiver>, Func>;
        adapted_rcvr_t adapted(std::forward<Receiver>(rcvr), std::move(func_));
        return exec_model::connect(std::move(prev_), std::move(adapted));
    }

private:
    PrevSender prev_;
    Func func_;
};

// Перевантаження конвеєрного оператора |
template <class Sender, class Func>
auto operator|(Sender&& snd, Func&& f) {
    return then_sender<std::decay_t<Sender>, std::decay_t<Func>>(
        std::forward<Sender>(snd), std::forward<Func>(f));
}
