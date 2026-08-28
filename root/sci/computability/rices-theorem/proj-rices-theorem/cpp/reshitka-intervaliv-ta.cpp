#include <iostream>
#include <string>
#include <algorithm>
#include <limits>
#include <optional>

struct Interval {
    int min_val{0};
    int max_val{0};
    bool is_bottom{false};

    static constexpr int Inf = std::numeric_limits<int>::max();
    static constexpr int NegInf = std::numeric_limits<int>::min();

    static constexpr Interval Bottom() noexcept {
        return Interval{0, 0, true};
    }

    static constexpr Interval Range(int low, int high) noexcept {
        if (low > high) return Bottom();
        return Interval{low, high, false};
    }

    [[nodiscard]] constexpr bool contains_zero() const noexcept {
        if (is_bottom) return false;
        return min_val <= 0 && max_val >= 0;
    }
};

// Операція Join (найменша верхня межа)
constexpr Interval operator|(const Interval& a, const Interval& b) noexcept {
    if (a.is_bottom) return b;
    if (b.is_bottom) return a;
    return Interval::Range(std::min(a.min_val, b.min_val), std::max(a.max_val, b.max_val));
}

// Операція перетину (Meet)
constexpr Interval operator&(const Interval& a, const Interval& b) noexcept {
    if (a.is_bottom || b.is_bottom) return Interval::Bottom();
    return Interval::Range(std::max(a.min_val, b.min_val), std::min(a.max_val, b.max_val));
}

// Оператор розширення (Widening)
constexpr Interval widen(const Interval& prev, const Interval& next) noexcept {
    if (prev.is_bottom) return next;
    if (next.is_bottom) return prev;
    const int new_min = (next.min_val < prev.min_val) ? Interval::NegInf : prev.min_val;
    const int new_max = (next.max_val > prev.max_val) ? Interval::Inf : prev.max_val;
    return Interval::Range(new_min, new_max);
}

// Оператор звуження (Narrowing)
constexpr Interval narrow(const Interval& prev, const Interval& next) noexcept {
    if (prev.is_bottom || next.is_bottom) return Interval::Bottom();
    const int new_min = (prev.min_val == Interval::NegInf) ? next.min_val : prev.min_val;
    const int new_max = (prev.max_val == Interval::Inf) ? next.max_val : prev.max_val;
    return Interval::Range(new_min, new_max);
}

// Абстрактне додавання інтервалів
constexpr Interval operator+(const Interval& a, const Interval& b) noexcept {
    if (a.is_bottom || b.is_bottom) return Interval::Bottom();
    const int low = (a.min_val == Interval::NegInf || b.min_val == Interval::NegInf) 
                    ? Interval::NegInf : a.min_val + b.min_val;
    const int high = (a.max_val == Interval::Inf || b.max_val == Interval::Inf) 
                     ? Interval::Inf : a.max_val + b.max_val;
    return Interval::Range(low, high);
}

void print_interval(std::string_view name, const Interval& iv) {
    if (iv.is_bottom) {
        std::cout << name << ": ⊥ (недосяжний)\n";
        return;
    }
    std::cout << name << ": [";
    if (iv.min_val == Interval::NegInf) std::cout << "-INF";
    else std::cout << iv.min_val;
    std::cout << ", ";
    if (iv.max_val == Interval::Inf) std::cout << "+INF";
    else std::cout << iv.max_val;
    std::cout << "]\n";
}

int main() {
    // Моделюємо аналіз циклу:
    // int x = 1;
    // while (x < 100) { x = x + 2; }
    // int res = 1000 / x;

    Interval x = Interval::Range(1, 1);
    std::cout << "Початковий інтервал:\n";
    print_interval("x_0", x);

    // Фаза 1: Розширення (Widening)
    constexpr Interval guard = Interval::Range(Interval::NegInf, 99);
    for (int iter = 1; iter <= 2; ++iter) {
        const Interval inside_loop = x & guard;
        const Interval step = Interval::Range(2, 2);
        const Interval x_next = inside_loop + step;
        const Interval x_widened = widen(x, x | x_next);
        std::cout << "Ітерація " << iter << " (з розширенням):\n";
        print_interval("x_loop", x_widened);
        x = x_widened;
    }

    // Фаза 2: Звуження (Narrowing) після виходу
    constexpr Interval exit_guard = Interval::Range(100, Interval::Inf);
    const Interval x_exit = x & exit_guard;
    std::cout << "Стан після виходу з циклу (зі звуженням):\n";
    print_interval("x_exit", x_exit);

    if (!x_exit.contains_zero()) {
        std::cout << "Висновок: вираз 1000 / x є ГАРАНТОВАНО БЕЗПЕЧНИМ (нуль поза інтервалом)\n";
    } else {
        std::cout << "Попередження: можливе ділення на нуль!\n";
    }

    return 0;
}
