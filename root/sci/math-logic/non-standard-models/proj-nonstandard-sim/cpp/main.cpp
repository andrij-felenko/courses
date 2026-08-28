#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <memory>
#include <optional>
#include <span >
#include <format>
#include <functional>

namespace NonStandard {

constexpr size_t MAX_DEGREE = 4;

// Клас символьного нестандартного числа в кільці Z[H]
class NonStandardInt {
private:
    std::vector<int64_t> coeffs_;

public:
    explicit NonStandardInt(int64_t standard_val = 0) 
        : coeffs_(MAX_DEGREE, 0) {
        coeffs_[0] = standard_val;
    }

    static NonStandardInt make_inf(size_t degree, int64_t coeff = 1) {
        NonStandardInt result;
        if (degree < MAX_DEGREE) {
            result.coeffs_[degree] = coeff;
        }
        return result;
    }

    [[nodiscard]] bool is_standard() const noexcept {
        for (size_t i = 1; i < MAX_DEGREE; ++i) {
            if (coeffs_[i] != 0) return false;
        }
        return coeffs_[0] >= 0;
    }

    [[nodiscard]] std::span<const int64_t> coefficients() const noexcept {
        return coeffs_;
    }

    auto operator<=>(const NonStandardInt& other) const noexcept {
        for (int i = static_cast<int>(MAX_DEGREE) - 1; i >= 0; --i) {
            if (coeffs_[i] != other.coeffs_[i]) {
                return coeffs_[i] <=> other.coeffs_[i];
            }
        }
        return std::strong_ordering::equal;
    }

    bool operator==(const NonStandardInt& other) const noexcept {
        return (*this <=> other) == std::strong_ordering::equal;
    }

    NonStandardInt operator+(const NonStandardInt& other) const {
        NonStandardInt result;
        for (size_t i = 0; i < MAX_DEGREE; ++i) {
            result.coeffs_[i] = coeffs_[i] + other.coeffs_[i];
        }
        return result;
    }

    NonStandardInt operator*(const NonStandardInt& other) const {
        NonStandardInt result;
        for (size_t i = 0; i < MAX_DEGREE; ++i) {
            for (size_t j = 0; j < MAX_DEGREE - i; ++j) {
                result.coeffs_[i + j] += coeffs_[i] * other.coeffs_[j];
            }
        }
        return result;
    }

    [[nodiscard]] std::string to_string() const {
        std::string out;
        bool first = true;
        for (int i = static_cast<int>(MAX_DEGREE) - 1; i >= 0; --i) {
            if (coeffs_[i] != 0) {
                if (!first && coeffs_[i] > 0) out += " + ";
                if (coeffs_[i] < 0) out += " - ";
                
                int64_t abs_val = std::abs(coeffs_[i]);
                if (i == 0) {
                    out += std::to_string(abs_val);
                } else if (i == 1) {
                    out += (abs_val == 1) ? "H" : std::to_string(abs_val) + "·H";
                } else {
                    out += (abs_val == 1) ? "H^" + std::to_string(i) 
                                          : std::to_string(abs_val) + "·H^" + std::to_string(i);
                }
                first = false;
            }
        }
        return first ? "0" : out;
    }
};

// Клас аналізатора принципу Оверспілу (Переливу)
class OverspillEvaluator {
public:
    static bool evaluate(std::function<bool(int64_t)> pred, const NonStandardInt& limit) {
        for (int64_t i = 0; i < 100; ++i) {
            if (!pred(i)) return false;
        }
        return !limit.is_standard();
    }
};

// Симулятор Нестандартної Машини Тюринга
class NonStandardTuringMachine {
private:
    std::vector<uint8_t> tape_;
    size_t head_pos_;
    int state_;
    NonStandardInt steps_;
    bool halted_;

public:
    explicit NonStandardTuringMachine(size_t tape_size = 64)
        : tape_(tape_size, 0), head_pos_(tape_size / 2), state_(0), steps_(0), halted_(false) {}

    void step() {
        if (halted_) return;

        // Покроковий перехід стан-символ
        tape_[head_pos_] ^= 1;
        if (head_pos_ + 1 < tape_.size()) {
            head_pos_++;
        } else {
            halted_ = true;
        }

        steps_ = steps_ + NonStandardInt(1);
    }

    void execute_hyper_steps(const NonStandardInt& hyper_limit) {
        // Імітація обчислення в нестандартному часі H
        if (!hyper_limit.is_standard()) {
            steps_ = steps_ + hyper_limit;
        }
    }

    [[nodiscard]] std::string get_status() const {
        return std::string("Позиція: ") + std::to_string(head_pos_) + 
               ", Кроки: " + steps_.to_string() + 
               ", Зупинена: " + (halted_ ? "Так" : "Ні");
    }
};

} // namespace NonStandard

int main() {
    using namespace NonStandard;

    std::cout << "=== Об'єктний Симулятор Нестандартної Арифметики (C++20) ===\n\n";

    auto n5 = NonStandardInt(5);
    auto H = NonStandardInt::make_inf(1, 1);
    auto H2 = NonStandardInt::make_inf(2, 3);

    auto sum = H + n5;
    auto prod = sum * H;

    std::cout << "Стандартне число n5: " << n5.to_string() << "\n";
    std::cout << "Нестандартний елемент H: " << H.to_string() << "\n";
    std::cout << "Сума H + 5: " << sum.to_string() << "\n";
    std::cout << "Добуток (H + 5) · H: " << prod.to_string() << "\n\n";

    std::cout << "Порівняння (H < H + 5): " << std::boolalpha << (H < sum) << "\n";
    std::cout << "Перевірка стандартності (H + 5): " << sum.is_standard() << "\n\n";

    auto limit = NonStandardInt::make_inf(1, 500);
    bool overspill_valid = OverspillEvaluator::evaluate([](int64_t n) { return (n * n + 1) > 0; }, limit);
    std::cout << "Принцип Оверспілу для p(n) = n²+1 > 0: " << (overspill_valid ? "Пройшов" : "Помилка") << "\n\n";

    NonStandardTuringMachine tm(128);
    for (int i = 0; i < 5; ++i) tm.step();
    std::cout << "Стан TM після 5 стандартних кроків:\n" << tm.get_status() << "\n";

    tm.execute_hyper_steps(limit);
    std::cout << "Стан TM після виконання гіпер-кроку H:\n" << tm.get_status() << "\n";

    return 0;
}
