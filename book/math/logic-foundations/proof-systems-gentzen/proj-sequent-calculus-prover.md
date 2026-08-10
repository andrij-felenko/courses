# ⚙️ Доведення теорем численням секвенцій Генцена (Sequent Calculus Prover)

Автоматичне виведення в численні секвенцій Ґенцена (System LK/LJ) будує дерево виведення рекурсивним розщепленням секвенцій $\Gamma \vdash \Delta$ до аксіоматичних вершин.

## Постановка інженерної задачі та інтуїція рішення
Числення секвенцій маніпулює об'єктами, що називаються "секвенціями" у вигляді `Γ ⊢ Δ`, де `Γ` (антецеденти, припущення) і `Δ` (сукцеденти, висновки) — це множини формул. Секвенція вважається істинною, якщо кон'юнкція формул у `Γ` імплікує диз'юнкцію формул у `Δ`. Якщо секвенція містить одну й ту ж саму пропозиційну змінну з обох боків (наприклад, `A, B ⊢ A, C`), це тривіальна аксіома, яка вважається доведеною.

Завдання полягає у побудові "дерева доведення" від низу до верху (від цільової теореми до аксіом). Для кожного логічного оператора (AND, OR, NOT, IMPLIES) існують правила виведення, які розщеплюють або перетворюють формули зліва або справа від знаку "⊢". Оскільки в пропозиційній логіці ці правила є аналітичними (зменшують складність формул на кожному кроці), алгоритм гарантовано зупиниться і є повною процедурою розв'язання.

## Логічна архітектура та алгоритм дерева доведення
Ми реалізуємо пропозиційний секвенціальний прувер. Секвенція моделюється як пара векторів: `std::vector<Formula> left` та `std::vector<Formula> right`.
Алгоритм рекурсивно обробляє секвенцію:
1. **Перевірка аксіоми:** Якщо існує спільний літерал у `left` та `right`, гілка успішно доведена.
2. **Розгортання (Декомпозиція):** Ми ітеруємося по формулах у секвенції і шукаємо складні формули (AND, OR, NOT).
3. **Застосування правил Генцена:** 
   - `AND` ліворуч (`A ∧ B ⊢ Δ`): замінюємо на `A, B ⊢ Δ`.
   - `AND` праворуч (`Γ ⊢ A ∧ B, Δ`): гілкується на ДВІ підцілі: `Γ ⊢ A, Δ` та `Γ ⊢ B, Δ`. Обидві повинні бути доведені.
   - `OR` ліворуч (`A ∨ B ⊢ Δ`): гілкується на `A ⊢ Δ` та `B ⊢ Δ`.
   - `OR` праворуч (`Γ ⊢ A ∨ B, Δ`): замінюємо на `Γ ⊢ A, B, Δ`.
   - `NOT` ліворуч (`¬A ⊢ Δ`): переносимо A направо `⊢ A, Δ`.
   - `NOT` праворуч (`Γ ⊢ ¬A`): переносимо A наліво `A, Γ ⊢`.
4. Якщо не залишилося складних формул для розгортання і перетин множин порожній, секвенція недоказова (і, відповідно, теорема недійсна).

## Повний робочий код на C++

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <algorithm>

// Типи вузлів
enum class NodeType { VAR, AND, OR, NOT };

// Абстрактне синтаксичне дерево
struct Node {
    NodeType type;
    std::string name;
    std::shared_ptr<Node> left, right;

    Node(std::string n) : type(NodeType::VAR), name(std::move(n)) {}
    Node(NodeType t, std::shared_ptr<Node> l, std::shared_ptr<Node> r = nullptr)
        : type(t), left(std::move(l)), right(std::move(r)) {}
};

// Секвенція
struct Sequent {
    std::vector<std::shared_ptr<Node>> left;
    std::vector<std::shared_ptr<Node>> right;
};

// Допоміжна перевірка на аксіому (спільна змінна)
bool isAxiom(const Sequent& seq) {
    for (const auto& l : seq.left) {
        if (l->type == NodeType::VAR) {
            for (const auto& r : seq.right) {
                if (r->type == NodeType::VAR && l->name == r->name) {
                    return true;
                }
            }
        }
    }
    return false;
}

// Головна рекурсивна функція доведення
bool prove(Sequent seq) {
    // Якщо секвенція тривіально доказова
    if (isAxiom(seq)) return true;

    // Шукаємо складну формулу ЗЛІВА
    for (size_t i = 0; i < seq.left.size(); ++i) {
        auto node = seq.left[i];
        if (node->type == NodeType::VAR) continue;

        // Видаляємо складну формулу з секвенції для застосування правила
        auto newLeft = seq.left;
        newLeft.erase(newLeft.begin() + i);
        
        if (node->type == NodeType::AND) {
            // L-AND: A ∧ B ⊢ ... -> A, B ⊢ ...
            newLeft.push_back(node->left);
            newLeft.push_back(node->right);
            return prove({newLeft, seq.right});
        } 
        else if (node->type == NodeType::OR) {
            // L-OR: A ∨ B ⊢ ... -> A ⊢ ... ТА B ⊢ ... (розгалуження)
            auto leftBranchL = newLeft; leftBranchL.push_back(node->left);
            auto rightBranchL = newLeft; rightBranchL.push_back(node->right);
            return prove({leftBranchL, seq.right}) && prove({rightBranchL, seq.right});
        }
        else if (node->type == NodeType::NOT) {
            // L-NOT: ¬A ⊢ ... -> ⊢ A, ...
            auto newRight = seq.right;
            newRight.push_back(node->left);
            return prove({newLeft, newRight});
        }
    }

    // Шукаємо складну формулу СПРАВА
    for (size_t i = 0; i < seq.right.size(); ++i) {
        auto node = seq.right[i];
        if (node->type == NodeType::VAR) continue;

        auto newRight = seq.right;
        newRight.erase(newRight.begin() + i);

        if (node->type == NodeType::OR) {
            // R-OR: ... ⊢ A ∨ B -> ... ⊢ A, B
            newRight.push_back(node->left);
            newRight.push_back(node->right);
            return prove({seq.left, newRight});
        }
        else if (node->type == NodeType::AND) {
            // R-AND: ... ⊢ A ∧ B -> ... ⊢ A ТА ... ⊢ B (розгалуження)
            auto leftBranchR = newRight; leftBranchR.push_back(node->left);
            auto rightBranchR = newRight; rightBranchR.push_back(node->right);
            return prove({seq.left, leftBranchR}) && prove({seq.left, rightBranchR});
        }
        else if (node->type == NodeType::NOT) {
            // R-NOT: ... ⊢ ¬A -> A, ... ⊢ 
            auto newLeft = seq.left;
            newLeft.push_back(node->left);
            return prove({newLeft, newRight});
        }
    }

    // Немає складних формул і не аксіома -> не доказово
    return false;
}

int main() {
    // Тестуємо Закон виключеного третього: ⊢ A ∨ ¬A
    auto varA = std::make_shared<Node>("A");
    auto notA = std::make_shared<Node>(NodeType::NOT, varA);
    auto lawOfExcludedMiddle = std::make_shared<Node>(NodeType::OR, varA, notA);

    Sequent target;
    target.right.push_back(lawOfExcludedMiddle); // Мета праворуч

    if (prove(target)) {
        std::cout << "Theorem PROVEN!\n";
    } else {
        std::cout << "Theorem INVALID.\n";
    }

    return 0;
}
```

## Построчний аналіз, пам'ять та керування ресурсами
Рекурсивний алгоритм активно маніпулює списками формул на кожному кроці розгортання. Використання `std::shared_ptr<Node>` критично важливе для уникнення надмірного копіювання глибоких абстрактних синтаксичних дерев під час копіювання векторів `auto newLeft = seq.left;`. Ми копіюємо лише вектори вказівників (неглибоке копіювання масивів стану), що забезпечує швидке розгалуження (branching).

Обробка крайових випадків реалізована перевіркою `node->type == NodeType::VAR`. Змінні відіграють роль атомарних блоків (literals), які алгоритм ігнорує під час декомпозиції, поступово "очищуючи" секвенцію. Інваріант алгоритму полягає в тому, що на кожному рекурсивному виклику загальна кількість логічних конекторів у секвенції строго зменшується на 1, що математично гарантує відсутність нескінченних циклів.

## Вхідні та вихідні дані і оцінка складності (I/O)
Приклад виконання для `⊢ A ∨ ¬A` (Закон виключеного третього):
```text
Theorem PROVEN!
```
Розгортання:
1. `⊢ A ∨ ¬A` (R-OR)
2. `⊢ A, ¬A`  (R-NOT на ¬A)
3. `A ⊢ A`    (Аксіома! Збіг ліворуч і праворуч)

**Оцінка складності:**
- **Часова складність:** У найгіршому випадку, правила розгалуження (R-AND, L-OR) подвоюють кількість цілей для доведення. Це призводить до експоненційного часу O(2^M), де M — кількість логічних конекторів. Це очікувано, оскільки пропозиційне виведення є co-NP повним.
- **Просторова складність:** O(M) у стеку викликів завдяки структурному розподілу пам'яті (`shared_ptr`), що робить алгоритм досить безпечним до Stack Overflow для формул розумної довжини. Максимальна глибина дерева доведення дорівнює розміру вихідної формули.
