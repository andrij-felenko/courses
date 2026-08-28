// sgh_engine.hpp / sgh_engine.cpp — Обчислювач повільнозростаючої ієрархії на C++20
#include <iostream>
#include <memory>
#include <vector>
#include <cstdint>
#include <cmath>
#include <string>
#include <string_view>
#include <stdexcept>

namespace sgh {

class OrdinalNode {
public:
    virtual ~OrdinalNode() = default;
    [[nodiscard]] virtual uint64_t evaluate(uint64_t n) const = 0;
    [[nodiscard]] virtual std::string to_string() const = 0;
};

using OrdinalPtr = std::unique_ptr<OrdinalNode>;

class ConstantNode final : public OrdinalNode {
private:
    uint64_t value_;
public:
    explicit ConstantNode(uint64_t val) noexcept : value_(val) {}
    [[nodiscard]] uint64_t evaluate(uint64_t /*n*/) const noexcept override {
        return value_;
    }
    [[nodiscard]] std::string to_string() const override {
        return std::to_string(value_);
    }
};

class OmegaTermNode final : public OrdinalNode {
private:
    OrdinalPtr exponent_;
    uint64_t coefficient_;

    [[nodiscard]] static uint64_t int_pow(uint64_t base, uint64_t exp) {
        uint64_t res = 1;
        while (exp > 0) {
            if (exp & 1) res *= base;
            base *= base;
            exp >>= 1;
        }
        return res;
    }

public:
    OmegaTermNode(OrdinalPtr exp, uint64_t coeff)
        : exponent_(std::move(exp)), coefficient_(coeff) {
        if (!exponent_) {
            throw std::invalid_argument("Exponent node must not be null");
        }
    }

    [[nodiscard]] uint64_t evaluate(uint64_t n) const override {
        uint64_t exp_val = exponent_->evaluate(n);
        uint64_t base_pow = int_pow(n, exp_val);
        return base_pow * coefficient_;
    }

    [[nodiscard]] std::string to_string() const override {
        std::string s = "w^(" + exponent_->to_string() + ")";
        if (coefficient_ > 1) {
            s += " * " + std::to_string(coefficient_);
        }
        return s;
    }
};

class SumNode final : public OrdinalNode {
private:
    std::vector<OrdinalPtr> terms_;
public:
    SumNode() = default;

    void add_term(OrdinalPtr term) {
        if (term) {
            terms_.push_back(std::move(term));
        }
    }

    [[nodiscard]] uint64_t evaluate(uint64_t n) const override {
        uint64_t total = 0;
        for (const auto& term : terms_) {
            total += term->evaluate(n);
        }
        return total;
    }

    [[nodiscard]] std::string to_string() const override {
        if (terms_.empty()) return "0";
        std::string res;
        for (size_t i = 0; i < terms_.size(); ++i) {
            if (i > 0) res += " + ";
            res += terms_[i]->to_string();
        }
        return res;
    }
};

class CollapseNode final : public OrdinalNode {
private:
    OrdinalPtr inner_;
public:
    explicit CollapseNode(OrdinalPtr inner) : inner_(std::move(inner)) {
        if (!inner_) {
            throw std::invalid_argument("Collapsed inner node cannot be null");
        }
    }

    [[nodiscard]] uint64_t evaluate(uint64_t n) const override {
        uint64_t inner_val = inner_->evaluate(n);
        uint64_t res = 1;
        for (uint64_t i = 0; i < inner_val; ++i) {
            res *= n;
        }
        return res;
    }

    [[nodiscard]] std::string to_string() const override {
        return "psi(" + inner_->to_string() + ")";
    }
};

} // namespace sgh

int main() {
    using namespace sgh;

    auto sum = std::make_unique<SumNode>();
    sum->add_term(std::make_unique<OmegaTermNode>(std::make_unique<ConstantNode>(3), 2));
    sum->add_term(std::make_unique<OmegaTermNode>(std::make_unique<ConstantNode>(2), 5));
    sum->add_term(std::make_unique<ConstantNode>(7));

    constexpr uint64_t n = 3;
    const uint64_t res = sum->evaluate(n);

    std::cout << "Ordinal: " << sum->to_string() << "\n";
    std::cout << "G_alpha(" << n << ") = " << res << "\n";

    return 0;
}
