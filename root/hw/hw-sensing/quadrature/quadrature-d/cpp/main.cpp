#include <cstdint>
#include <array>
#include <atomic>

/**
 * @brief Напрям здійсненого переміщення
 */
enum class QuadDirection : int8_t {
    None = 0,
    Cw   = 1,
    Ccw  = -1
};

/**
 * @brief Відмовостійкий клас квадратурного декодера C++20
 * @tparam PositionType Цілочисельний тип зберігання координати (за замовчуванням int64_t)
 */
template <typename PositionType = int64_t>
class QuadratureDecoder {
public:
    struct Snapshot {
        PositionType  position;
        uint32_t      error_count;
        QuadDirection last_direction;
    };

    /**
     * @brief Конструктор з початковими логічними рівнями на лініях
     */
    constexpr QuadratureDecoder(bool initial_raw_a = false, bool initial_raw_b = false) noexcept
        : position_(0),
          error_count_(0),
          stable_a_(initial_raw_a ? 1 : 0),
          stable_b_(initial_raw_b ? 1 : 0),
          history_a_(initial_raw_a ? 0xFF : 0x00),
          history_b_(initial_raw_b ? 0xFF : 0x00),
          prev_valid_state_((stable_a_ << 1) | stable_b_),
          last_direction_(QuadDirection::None) {}

    /**
     * @brief Обробка вибірки з входів (викликається з переривання або таймерного циклу)
     */
    QuadDirection process(bool raw_a, bool raw_b) noexcept {
        // 1. Цифрова фільтрація брязкоту (3-бітове ковзне вікно)
        history_a_ = static_cast<uint8_t>((history_a_ << 1) | (raw_a ? 1 : 0));
        history_b_ = static_cast<uint8_t>((history_b_ << 1) | (raw_b ? 1 : 0));

        if ((history_a_ & 0x07) == 0x07) {
            stable_a_ = 1;
        } else if ((history_a_ & 0x07) == 0x00) {
            stable_a_ = 0;
        }

        if ((history_b_ & 0x07) == 0x07) {
            stable_b_ = 1;
        } else if ((history_b_ & 0x07) == 0x00) {
            stable_b_ = 0;
        }

        // 2. Формування 2-бітного вектора поточного стану
        const uint8_t curr_state = static_cast<uint8_t>((stable_a_ << 1) | stable_b_);
        if (curr_state == prev_valid_state_) {
            last_direction_ = QuadDirection::None;
            return QuadDirection::None;
        }

        // 3. Табличне декодування FSM
        const uint8_t lut_index = static_cast<uint8_t>((prev_valid_state_ << 2) | curr_state);
        const int8_t step = FSM_LUT[lut_index];

        if (step == INVALID_TRANSITION) {
            ++error_count_;
            prev_valid_state_ = curr_state;
            last_direction_ = QuadDirection::None;
            return QuadDirection::None;
        }

        // 4. Оновлення позиції
        position_ += step;
        prev_valid_state_ = curr_state;
        last_direction_ = (step > 0) ? QuadDirection::Cw : QuadDirection::Ccw;

        return last_direction_;
    }

    [[nodiscard]] PositionType position() const noexcept {
        return position_;
    }

    [[nodiscard]] uint32_t errors() const noexcept {
        return error_count_;
    }

    [[nodiscard]] QuadDirection last_direction() const noexcept {
        return last_direction_;
    }

    [[nodiscard]] Snapshot snapshot() const noexcept {
        return { position_, error_count_, last_direction_ };
    }

    void reset(PositionType new_position = 0) noexcept {
        position_ = new_position;
    }

    void reset_errors() noexcept {
        error_count_ = 0;
    }

private:
    static constexpr int8_t INVALID_TRANSITION = 2;

    // Константна таблиця переходів у Flash/ROM
    static constexpr std::array<int8_t, 16> FSM_LUT = {
        0,   1,  -1,  INVALID_TRANSITION,
       -1,   0,  INVALID_TRANSITION,   1,
        1,  INVALID_TRANSITION,   0,  -1,
        INVALID_TRANSITION,  -1,   1,   0
    };

    PositionType  position_{0};
    uint32_t      error_count_{0};
    uint8_t       stable_a_{0};
    uint8_t       stable_b_{0};
    uint8_t       history_a_{0};
    uint8_t       history_b_{0};
    uint8_t       prev_valid_state_{0};
    QuadDirection last_direction_{QuadDirection::None};
};
