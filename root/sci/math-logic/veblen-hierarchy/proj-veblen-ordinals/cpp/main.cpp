#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <compare>
#include <utility>
#include <cassert>

namespace veblen {

enum class Kind {
    Zero,
    Finite,
    Add,
    Veblen
};

class Ordinal;
using OrdinalPtr = std::unique_ptr<Ordinal>;

class Ordinal {
public:
    Kind kind;
    unsigned long long value{0};
    OrdinalPtr left{nullptr};
    OrdinalPtr right{nullptr};

    Ordinal() : kind(Kind::Zero) {}
    explicit Ordinal(unsigned long long val) : kind(Kind::Finite), value(val) {
        if (val == 0) kind = Kind::Zero;
    }
    Ordinal(Kind k, OrdinalPtr l, OrdinalPtr r)
        : kind(k), left(std::move(l)), right(std::move(r)) {}

    [[nodiscard]] bool is_zero() const noexcept {
        return kind == Kind::Zero;
    }

    [[nodiscard]] bool is_principal() const noexcept {
        return kind == Kind::Veblen;
    }

    [[nodiscard]] OrdinalPtr clone() const {
        auto copy = std::make_unique<Ordinal>();
        copy->kind = this->kind;
        copy->value = this->value;
        if (this->left) copy->left = this->left->clone();
        if (this->right) copy->right = this->right->clone();
        return copy;
    }
};

/* Фабричні методи створення об'єктів */
inline OrdinalPtr make_zero() {
    return std::make_unique<Ordinal>();
}

inline OrdinalPtr make_finite(unsigned long long val) {
    if (val == 0) return make_zero();
    return std::make_unique<Ordinal>(val);
}

inline OrdinalPtr make_veblen(OrdinalPtr gamma, OrdinalPtr beta) {
    return std::make_unique<Ordinal>(Kind::Veblen, std::move(gamma), std::move(beta));
}

/* Тристороннє рекурсивне порівняння синтаксичних дерев ординалів */
std::strong_ordering compare(const Ordinal* a, const Ordinal* b) noexcept;

namespace detail {
    inline std::strong_ordering compare_veblen(const Ordinal* a, const Ordinal* b) noexcept {
        assert(a->kind == Kind::Veblen && b->kind == Kind::Veblen);

        auto g_cmp = compare(a->left.get(), b->left.get());
        if (g_cmp == std::strong_ordering::equal) {
            return compare(a->right.get(), b->right.get());
        } else if (g_cmp == std::strong_ordering::less) {
            /* a->gamma < b->gamma: A < B <=> beta_A < B */
            auto cmp_b = compare(a->right.get(), b);
            return (cmp_b == std::strong_ordering::less) 
                ? std::strong_ordering::less 
                : std::strong_ordering::greater;
        } else {
            /* a->gamma > b->gamma: A < B <=> A <= beta_B */
            auto cmp_a = compare(a, b->right.get());
            return (cmp_a == std::strong_ordering::less || cmp_a == std::strong_ordering::equal)
                ? std::strong_ordering::less 
                : std::strong_ordering::greater;
        }
    }
}

inline std::strong_ordering compare(const Ordinal* a, const Ordinal* b) noexcept {
    if (a == b) return std::strong_ordering::equal;
    bool a_zero = (!a || a->is_zero());
    bool b_zero = (!b || b->is_zero());

    if (a_zero && b_zero) return std::strong_ordering::equal;
    if (a_zero) return std::strong_ordering::less;
    if (b_zero) return std::strong_ordering::greater;

    if (a->kind == Kind::Finite && b->kind == Kind::Finite) {
        return a->value <=> b->value;
    }
    if (a->kind == Kind::Finite) return std::strong_ordering::less;
    if (b->kind == Kind::Finite) return std::strong_ordering::greater;

    if (a->kind == Kind::Veblen && b->kind == Kind::Veblen) {
        return detail::compare_veblen(a, b);
    }

    /* Розбір сум */
    const Ordinal* a_head = (a->kind == Kind::Add) ? a->left.get() : a;
    const Ordinal* b_head = (b->kind == Kind::Add) ? b->left.get() : b;

    auto head_cmp = compare(a_head, b_head);
    if (head_cmp != std::strong_ordering::equal) return head_cmp;

    const Ordinal* a_tail = (a->kind == Kind::Add) ? a->right.get() : nullptr;
    const Ordinal* b_tail = (b->kind == Kind::Add) ? b->right.get() : nullptr;

    return compare(a_tail, b_tail);
}

/* Операція додавання з поглинанням менших лівих операндів */
inline OrdinalPtr add(OrdinalPtr a, OrdinalPtr b) {
    if (!a || a->is_zero()) return b;
    if (!b || b->is_zero()) return a;

    if (a->kind == Kind::Finite && b->kind == Kind::Finite) {
        return make_finite(a->value + b->value);
    }

    const Ordinal* b_lead = (b->kind == Kind::Add) ? b->left.get() : b.get();

    /* 1 + omega = omega */
    if (a->kind == Kind::Finite && b_lead->kind == Kind::Veblen) {
        return b;
    }

    if (a->kind == Kind::Veblen) {
        if (compare(a.get(), b_lead) == std::strong_ordering::less) {
            return b;
        }
    } else if (a->kind == Kind::Add) {
        if (compare(a->left.get(), b_lead) == std::strong_ordering::less) {
            return b;
        }
        a->right = add(std::move(a->right), std::move(b));
        return a;
    }

    return std::make_unique<Ordinal>(Kind::Add, std::move(a), std::move(b));
}

/* Форматування у читабельний рядок */
inline std::string to_string(const Ordinal* n) {
    if (!n || n->is_zero()) return "0";
    if (n->kind == Kind::Finite) return std::to_string(n->value);

    if (n->kind == Kind::Veblen) {
        std::string g_str = to_string(n->left.get());
        std::string b_str = to_string(n->right.get());

        if (n->left->is_zero()) {
            if (n->right->is_zero()) return "1";
            if (n->right->kind == Kind::Finite && n->right->value == 1) return "w";
            return "w^(" + b_str + ")";
        }
        if (n->left->kind == Kind::Finite && n->left->value == 1) {
            return "eps(" + b_str + ")";
        }
        if (n->left->kind == Kind::Finite && n->left->value == 2) {
            return "zeta(" + b_str + ")";
        }
        return "phi(" + g_str + ", " + b_str + ")";
    }

    if (n->kind == Kind::Add) {
        return to_string(n->left.get()) + " + " + to_string(n->right.get());
    }
    return "?";
}

} // namespace veblen

int main() {
    using namespace veblen;
    std::cout << "=== Демонстрація синтаксичного рушія ординалів Веблена (C++20) ===\n";

    auto zero = make_zero();
    auto one = make_finite(1);
    auto w = make_veblen(make_zero(), make_finite(1));
    auto w2 = make_veblen(make_zero(), make_finite(2));
    auto eps0 = make_veblen(make_finite(1), make_zero());
    auto eps1 = make_veblen(make_finite(1), make_finite(1));
    auto zet0 = make_veblen(make_finite(2), make_zero());

    std::cout << "Ординал w: " << to_string(w.get()) << "\n";
    std::cout << "Ординал eps0: " << to_string(eps0.get()) << "\n";
    std::cout << "Ординал zeta0: " << to_string(zet0.get()) << "\n";

    assert(compare(zero.get(), one.get()) == std::strong_ordering::less);
    assert(compare(one.get(), w.get()) == std::strong_ordering::less);
    assert(compare(w.get(), w2.get()) == std::strong_ordering::less);
    assert(compare(w2.get(), eps0.get()) == std::strong_ordering::less);
    assert(compare(eps0.get(), eps1.get()) == std::strong_ordering::less);
    assert(compare(eps1.get(), zet0.get()) == std::strong_ordering::less);

    auto sum_1_w = add(make_finite(1), w->clone());
    std::cout << "1 + w = " << to_string(sum_1_w.get()) << "\n";
    assert(compare(sum_1_w.get(), w.get()) == std::strong_ordering::equal);

    auto sum_w_1 = add(w->clone(), make_finite(1));
    std::cout << "w + 1 = " << to_string(sum_w_1.get()) << "\n";
    assert(compare(sum_w_1.get(), w.get()) == std::strong_ordering::greater);

    std::cout << "Усі перевірки впорядкування C++20 пройдено успішно!\n";
    return 0;
}
