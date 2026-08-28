#include <iostream>
#include <memory>
#include <string>
#include <variant>
#include <string_view>

namespace peano {

struct Term;
using TermPtr = std::unique_ptr<Term>;

struct Zero {};
struct Var { std::string name; };
struct Succ { TermPtr child; };
struct Add { TermPtr left; TermPtr right; };
struct Mul { TermPtr left; TermPtr right; };

struct Term {
    std::variant<Zero, Var, Succ, Add, Mul> node;

    explicit Term(Zero z) : node(std::move(z)) {}
    explicit Term(Var v) : node(std::move(v)) {}
    explicit Term(Succ s) : node(std::move(s)) {}
    explicit Term(Add a) : node(std::move(a)) {}
    explicit Term(Mul m) : node(std::move(m)) {}
};

// Фабричні функції
inline TermPtr make_zero() {
    return std::make_unique<Term>(Zero{});
}

inline TermPtr make_var(std::string_view name) {
    return std::make_unique<Term>(Var{std::string(name)});
}

inline TermPtr make_succ(TermPtr child) {
    return std::make_unique<Term>(Succ{std::move(child)});
}

inline TermPtr make_add(TermPtr left, TermPtr right) {
    return std::make_unique<Term>(Add{std::move(left), std::move(right)});
}

inline TermPtr make_mul(TermPtr left, TermPtr right) {
    return std::make_unique<Term>(Mul{std::move(left), std::move(right)});
}

// Рекурсивне глибоке копіювання
inline TermPtr copy_term(const TermPtr& t) {
    if (!t) return nullptr;
    return std::visit([](const auto& arg) -> TermPtr {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, Zero>) return make_zero();
        else if constexpr (std::is_same_v<T, Var>) return make_var(arg.name);
        else if constexpr (std::is_same_v<T, Succ>) return make_succ(copy_term(arg.child));
        else if constexpr (std::is_same_v<T, Add>) return make_add(copy_term(arg.left), copy_term(arg.right));
        else if constexpr (std::is_same_v<T, Mul>) return make_mul(copy_term(arg.left), copy_term(arg.right));
    }, t->node);
}

// Друк терма
inline void print_term(const TermPtr& t) {
    if (!t) return;
    std::visit([](const auto& arg) {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, Zero>) {
            std::cout << "0";
        } else if constexpr (std::is_same_v<T, Var>) {
            std::cout << arg.name;
        } else if constexpr (std::is_same_v<T, Succ>) {
            std::cout << "S(";
            print_term(arg.child);
            std::cout << ")";
        } else if constexpr (std::is_same_v<T, Add>) {
            std::cout << "(";
            print_term(arg.left);
            std::cout << " + ";
            print_term(arg.right);
            std::cout << ")";
        } else if constexpr (std::is_same_v<T, Mul>) {
            std::cout << "(";
            print_term(arg.left);
            std::cout << " · ";
            print_term(arg.right);
            std::cout << ")";
        }
    }, t->node);
}

// Однокрокова редукція за аксіомами Пеано
inline TermPtr reduce_step(TermPtr t, bool& changed) {
    if (!t) return nullptr;

    if (auto* s = std::get_if<Succ>(&t->node)) {
        s->child = reduce_step(std::move(s->child), changed);
        return t;
    }

    if (auto* a = std::get_if<Add>(&t->node)) {
        a->left = reduce_step(std::move(a->left), changed);
        a->right = reduce_step(std::move(a->right), changed);

        if (std::holds_alternative<Zero>(a->right->node)) {
            changed = true;
            return std::move(a->left); // x + 0 -> x
        }

        if (auto* s = std::get_if<Succ>(&a->right->node)) {
            changed = true;
            TermPtr left = std::move(a->left);
            TermPtr y = std::move(s->child);
            return make_succ(make_add(std::move(left), std::move(y))); // x + S(y) -> S(x + y)
        }
    }

    if (auto* m = std::get_if<Mul>(&t->node)) {
        m->left = reduce_step(std::move(m->left), changed);
        m->right = reduce_step(std::move(m->right), changed);

        if (std::holds_alternative<Zero>(m->right->node)) {
            changed = true;
            return make_zero(); // x · 0 -> 0
        }

        if (auto* s = std::get_if<Succ>(&m->right->node)) {
            changed = true;
            TermPtr left = std::move(m->left);
            TermPtr y = std::move(s->child);
            TermPtr mul_xy = make_mul(copy_term(left), std::move(y));
            return make_add(std::move(mul_xy), std::move(left)); // x · S(y) -> (x · y) + x
        }
    }

    return t;
}

inline TermPtr normalize(TermPtr t) {
    bool changed = false;
    do {
        changed = false;
        t = reduce_step(std::move(t), changed);
    } while (changed);
    return t;
}

} // namespace peano

int main() {
    using namespace peano;

    std::cout << "=== Інтерпретатор термів арифметики Пеано (C++20 RAII) ===\n\n";

    // Побудова виразу: (x · S(0)) + (y + 0)
    auto expr = make_add(
        make_mul(make_var("x"), make_succ(make_zero())),
        make_add(make_var("y"), make_zero())
    );

    std::cout << "Початковий вираз: ";
    print_term(expr);
    std::cout << "\n";

    expr = normalize(std::move(expr));

    std::cout << "Після символьної редукції PA: ";
    print_term(expr);
    std::cout << "\n\n";

    return 0;
}
