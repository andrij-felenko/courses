#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_set>
#include <map>

// 1. Абстрактне синтаксичне дерево (AST) для формул
enum class Op { VAR, AND, OR, IMPLIES, NOT };

struct Formula {
    Op op;
    std::string name; // Для атомарних змінних
    std::shared_ptr<Formula> left;
    std::shared_ptr<Formula> right;

    static std::shared_ptr<Formula> Var(const std::string& n) {
        return std::make_shared<Formula>(Formula{Op::VAR, n, nullptr, nullptr});
    }
    static std::shared_ptr<Formula> Or(auto l, auto r) {
        return std::make_shared<Formula>(Formula{Op::OR, "", l, r});
    }
    static std::shared_ptr<Formula> Not(auto f) {
        return std::make_shared<Formula>(Formula{Op::NOT, "", f, nullptr});
    }
};

// 2. Світ у моделі Кріпке
struct World {
    std::string id;
    std::unordered_set<std::string> truths;
    std::vector<World*> children; // Майбутні стани (w <= w')
};

// 3. Логіка обчислення (Evaluation)
bool evaluate(World* w, std::shared_ptr<Formula> f) {
    switch (f->op) {
        case Op::VAR:
            // Змінна істинна, якщо вона є у множині відомих фактів цього світу.
            return w->truths.count(f->name) > 0;
            
        case Op::OR:
            // Диз'юнкція обчислюється як класична логічна сума в поточному світі.
            return evaluate(w, f->left) || evaluate(w, f->right);
            
        case Op::NOT:
            // w ⊩ ¬A <=> для всіх w' (w <= w'), w' НЕ ⊩ A
            // Спочатку перевіряємо поточний світ
            if (evaluate(w, f->left)) return false;
            // Потім рекурсивно перевіряємо всі доступні майбутні світи
            for (World* child : w->children) {
                if (!evaluate(child, f)) return false;
            }
            return true;
            
        default:
            return false;
    }
}

// 4. Точка входу та перевірка закону виключеного третього
int main() {
    // Будуємо модель: Root -> (Left, Right)
    World root{"Root", {}};
    World left{"Left", {"p"}};
    World right{"Right", {"q"}};
    root.children = {&left, &right};

    // Перевіряємо закон виключеного третього: p ∨ ¬p
    auto p = Formula::Var("p");
    auto not_p = Formula::Not(p);
    auto lem = Formula::Or(p, not_p);

    std::cout << "У світі Root, (p ∨ ¬p) є: " 
              << (evaluate(&root, lem) ? "Істина" : "Хиба") << "\n";
              
    // Очікуваний результат: Хиба. 
    // root не має p. Але root не має ¬p, бо світ left містить p.
    return 0;
}
