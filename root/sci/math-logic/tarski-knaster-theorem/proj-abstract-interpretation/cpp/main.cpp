#include <iostream>
#include <string>
#include <optional>
#include <algorithm>
#include <limits>

class Interval {
public:
    static constexpr long kInfPos = std::numeric_limits<long>::max() / 2;
    static constexpr long kInfNeg = std::numeric_limits<long>::min() / 2;

    constexpr Interval() : is_bottom_(true), min_(0), max_(0) {}
    constexpr Interval(long min, long max) 
        : is_bottom_(min > max), min_(min), max_(max) {}

    static constexpr Interval Bottom() noexcept { return Interval(); }
    static constexpr Interval Top() noexcept { return Interval(kInfNeg, kInfPos); }

    [[nodiscard]] constexpr bool IsBottom() const noexcept { return is_bottom_; }
    [[nodiscard]] constexpr long Min() const noexcept { return min_; }
    [[nodiscard]] constexpr long Max() const noexcept { return max_; }

    constexpr bool operator==(const Interval& other) const noexcept {
        if (is_bottom_ && other.is_bottom_) return true;
        if (is_bottom_ || other.is_bottom_) return false;
        return min_ == other.min_ && max_ == other.max_;
    }

    constexpr bool operator!=(const Interval& other) const noexcept {
        return !(*this == other);
    }

    // Операція часткового порядку (включення знань)
    [[nodiscard]] constexpr bool Leq(const Interval& other) const noexcept {
        if (is_bottom_) return true;
        if (other.is_bottom_) return false;
        return other.min_ <= min_ && max_ <= other.max_;
    }

    // Операція точної верхньої грані (Join, ⊔)
    [[nodiscard]] Interval Join(const Interval& other) const noexcept {
        if (is_bottom_) return other;
        if (other.is_bottom_) return *this;
        return Interval(std::min(min_, other.min_), std::max(max_, other.max_));
    }

    // Операція точної нижньої грані (Meet, ⊓)
    [[nodiscard]] Interval Meet(const Interval& other) const noexcept {
        if (is_bottom_ || other.is_bottom_) return Bottom();
        long new_min = std::max(min_, other.min_);
        long new_max = std::min(max_, other.max_);
        return (new_min <= new_max) ? Interval(new_min, new_max) : Bottom();
    }

    // Абстрактний трансформатор додавання константи
    [[nodiscard]] Interval AddConst(long val) const noexcept {
        if (is_bottom_) return Bottom();
        long new_min = (min_ <= kInfNeg) ? kInfNeg : min_ + val;
        long new_max = (max_ >= kInfPos) ? kInfPos : max_ + val;
        return Interval(new_min, new_max);
    }

    // Оператор розширення (Widening, ∇)
    [[nodiscard]] Interval Widen(const Interval& next) const noexcept {
        if (is_bottom_) return next;
        if (next.is_bottom_) return *this;
        long new_min = (next.min_ < min_) ? kInfNeg : min_;
        long new_max = (next.max_ > max_) ? kInfPos : max_;
        return Interval(new_min, new_max);
    }

    // Оператор звуження (Narrowing, Δ)
    [[nodiscard]] Interval Narrow(const Interval& next) const noexcept {
        if (is_bottom_ || next.is_bottom_) return Bottom();
        long new_min = (min_ <= kInfNeg) ? next.min_ : min_;
        long new_max = (max_ >= kInfPos) ? next.max_ : max_;
        return Interval(new_min, new_max);
    }

    [[nodiscard]] std::string ToString() const {
        if (is_bottom_) return "⊥ (недосяжний стан)";
        std::string res = "[";
        res += (min_ <= kInfNeg) ? "-∞" : std::to_string(min_);
        res += ", ";
        res += (max_ >= kInfPos) ? "+∞" : std::to_string(max_);
        res += "]";
        return res;
    }

private:
    bool is_bottom_;
    long min_;
    long max_;
};

int main() {
    const Interval init_state(0, 0);
    const Interval guard(Interval::kInfNeg, 99);
    Interval loop_head = Interval::Bottom();

    // Етап 1: Пошук нерухомої точки з розширенням (Widening)
    std::cout << "=== Етап 1: Ітерація розширення (Widening) ===\n";
    for (int iter = 1; iter <= 10; ++iter) {
        Interval in_loop = loop_head.Meet(guard);
        Interval step = in_loop.AddConst(1);
        Interval combined = init_state.Join(step);
        Interval next_head = loop_head.Widen(combined);

        std::cout << "Ітерація " << iter << ": loop_head = " 
                  << next_head.ToString() << '\n';

        if (loop_head == next_head) {
            std::cout << "Постфіксну точку стабілізовано на кроці " << iter << ".\n\n";
            break;
        }
        loop_head = next_head;
    }

    // Етап 2: Уточнення значень оператором звуження (Narrowing)
    std::cout << "=== Етап 2: Ітерація звуження (Narrowing) ===\n";
    for (int iter = 1; iter <= 5; ++iter) {
        Interval in_loop = loop_head.Meet(guard);
        Interval step = in_loop.AddConst(1);
        Interval combined = init_state.Join(step);
        Interval next_head = loop_head.Narrow(combined);

        std::cout << "Ітерація " << iter << ": loop_head = " 
                  << next_head.ToString() << '\n';

        if (loop_head == next_head) {
            std::cout << "Найменшу нерухому точку знайдено на кроці " << iter << ".\n\n";
            break;
        }
        loop_head = next_head;
    }

    // Фінальні інваріанти за теоремою Тарського — Кнастера
    Interval body_inv = loop_head.Meet(guard);
    Interval exit_guard(100, Interval::kInfPos);
    Interval exit_inv = loop_head.Meet(exit_guard);

    std::cout << "=== Результати аналізу програми ===\n";
    std::cout << "Інваріант на вході в цикл   : " << loop_head.ToString() << '\n';
    std::cout << "Інваріант у тілі циклу      : " << body_inv.ToString() << '\n';
    std::cout << "Інваріант на виході з циклу : " << exit_inv.ToString() << '\n';

    return 0;
}
