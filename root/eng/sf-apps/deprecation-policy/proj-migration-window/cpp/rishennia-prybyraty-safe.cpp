// Рішення прибирати ухвалюють НЕ за датою, а за цим — за порожнім вікном.
class RemovalGate {
public:
    explicit RemovalGate(DeprecationMeter& m,
                         std::chrono::hours quiet_needed = std::chrono::hours(24 * 14))
        : meter_(m), quiet_needed_(quiet_needed) {}

    // Кличемо періодично (напр. раз на годину зі спостерігача).
    // Стежимо, чи лічильник ТРИМАЄ нуль достатньо довго.
    void poll() {
        auto now = std::chrono::steady_clock::now();
        if (meter_.hits() == 0) {
            if (!zero_since_) zero_since_ = now;            // нуль щойно почався
            // інакше — нуль триває, момент початку не чіпаємо
        } else {
            zero_since_.reset();                            // хтось прийшов — відлік скинуто
        }
        meter_.reset();                                     // нове вікно вимірювання
    }

    // Безпечно прибирати ⟺ нуль протримався не менше quiet_needed_.
    bool safe_to_remove() const {
        if (!zero_since_) return false;                     // зараз є користувачі
        return std::chrono::steady_clock::now() - *zero_since_ >= quiet_needed_;
    }

private:
    DeprecationMeter& meter_;
    std::chrono::hours quiet_needed_;
    std::optional<std::chrono::steady_clock::time_point> zero_since_;
};
