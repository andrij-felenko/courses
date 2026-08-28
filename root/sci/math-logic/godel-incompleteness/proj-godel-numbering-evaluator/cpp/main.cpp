#include <iostream>
#include <vector>
#include <memory>
#include <optional>
#include <cmath>
#include <numeric>
#include <string_view>
#include <expected>

namespace godel {

// Перелічення токенів мови арифметики
enum class TokenType : uint32_t {
    Zero = 1,
    Succ = 2,
    Plus = 3,
    Mult = 4,
    Eq   = 5,
    Not  = 6,
    Impl = 7,
    Ex   = 8,
    Var  = 9,
    LPar = 10,
    RPar = 11
};

// Таблиця перших простих чисел для Ґеделевої нумерації
inline constexpr uint64_t PRIMES[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47};

// Швидке типубезпечне піднесення до степеня
constexpr uint64_t power(uint64_t base, uint64_t exp) noexcept {
    uint64_t res = 1;
    while (exp > 0) {
        if (exp & 1) res *= base;
        base *= base;
        exp >>= 1;
    }
    return res;
}

// Клас синтаксичного кодувальника Ґеделя
class GodelEncoder {
public:
    [[nodiscard]] static std::expected<uint64_t, std::string_view> encode(const std::vector<TokenType>& tokens) noexcept {
        if (tokens.size() > std::size(PRIMES)) {
            return std::unexpected("Довжина формули перевищує розмір таблиці простих чисел");
        }
        uint64_t godel_num = 1;
        for (size_t i = 0; i < tokens.size(); ++i) {
            godel_num *= power(PRIMES[i], static_cast<uint64_t>(tokens[i]));
        }
        return godel_num;
    }

    [[nodiscard]] static std::vector<uint32_t> decode(uint64_t godel_num) {
        std::vector<uint32_t> exponents;
        size_t idx = 0;
        uint64_t temp = godel_num;

        while (temp > 1 && idx < std::size(PRIMES)) {
            uint32_t exp = 0;
            while (temp % PRIMES[idx] == 0) {
                exp++;
                temp /= PRIMES[idx];
            }
            exponents.push_back(exp);
            idx++;
        }
        return exponents;
    }
};

// Клас представлення речення та перевірки правил виведення
class ProofVerifier {
public:
    struct Sentence {
        std::vector<TokenType> tokens;
        uint64_t godel_number{0};
    };

    // Перевірка виведення Modus Ponens: A, A -> B |= B
    [[nodiscard]] static bool verify_modus_ponens(const Sentence& a, 
                                                 const Sentence& a_impl_b, 
                                                 const Sentence& b) noexcept {
        if (a_impl_b.tokens.size() != a.tokens.size() + b.tokens.size() + 1) {
            return false;
        }

        // Перевіряємо префікс A
        for (size_t i = 0; i < a.tokens.size(); ++i) {
            if (a_impl_b.tokens[i] != a.tokens[i]) return false;
        }

        // Перевіряємо роздільник IMPL
        if (a_impl_b.tokens[a.tokens.size()] != TokenType::Impl) return false;

        // Перевіряємо суфікс B
        for (size_t j = 0; j < b.tokens.size(); ++j) {
            if (a_impl_b.tokens[a.tokens.size() + 1 + j] != b.tokens[j]) return false;
        }

        return true;
    }
};

} // namespace godel

int main() {
    std::cout << "--- Демонстрація кодування Ґеделя мовою C++23 ---\n";

    using godel::TokenType;
    const std::vector<TokenType> formula = {
        TokenType::Not, TokenType::LPar, TokenType::Var, TokenType::Eq, TokenType::Zero, TokenType::RPar
    };

    auto result = godel::GodelEncoder::encode(formula);
    if (result) {
        std::cout << "Успішно обчислено Ґеделів номер: " << *result << "\n";
        
        auto decoded = godel::GodelEncoder::decode(*result);
        std::cout << "Декодовані показники простих множників: ";
        for (auto val : decoded) {
            std::cout << val << " ";
        }
        std::cout << "\n";
    } else {
        std::cerr << "Помилка кодування: " << result.error() << "\n";
    }

    return 0;
}
