// Шаблонний клас дискретного експоненційного БІХ-фільтра
template <typename T = float>
class ExponentialFilter {
public:
    explicit constexpr ExponentialFilter(float alpha = 0.08f) noexcept
        : alpha_((alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.08f),
          filteredVal_(0.0f),
          initialized_(false) {}

    // Оновлення стану фільтра новим сирим виміром АЦП
    T update(T rawVal) noexcept {
        const float val = static_cast<float>(rawVal);
        if (!initialized_) {
            filteredVal_ = val;
            initialized_ = true;
        } else {
            filteredVal_ += alpha_ * (val - filteredVal_);
        }
        return static_cast<T>(filteredVal_);
    }

    void reset(T initVal = 0) noexcept {
        filteredVal_ = static_cast<float>(initVal);
        initialized_ = (initVal != 0);
    }

    [[nodiscard]] T getValue() const noexcept {
        return static_cast<T>(filteredVal_);
    }

private:
    float alpha_;
    float filteredVal_;
    bool  initialized_;
};

// Приклад використання в класі контролера:
// ExponentialFilter<uint16_t> currentFilter_{0.08f};
// uint16_t current = currentFilter_.update(cfg_.hal.readCurrentMa ? cfg_.hal.readCurrentMa() : 0);
// if (current >= cfg_.stallCurrentMa) { ... }
