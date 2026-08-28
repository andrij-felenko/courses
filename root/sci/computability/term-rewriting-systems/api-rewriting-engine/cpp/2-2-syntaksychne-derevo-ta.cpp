namespace trs {

struct Term;
using TermPtr = std::shared_ptr<const Term>;

struct Term {
    NodeKind kind;
    std::string name;             // Ім'я змінної або символу
    std::vector<TermPtr> args;    // Список підтермів-аргументів
    size_t hash_code;             // Кешований хеш виразу
    size_t size;                  // Кількість вузлів у дереві
    size_t depth;                 // Максимальна глибина дерева
};

// Правило переписування l -> r
struct RewriteRule {
    uint32_t id;                  // Унікальний числовий ідентифікатор правила
    TermPtr lhs;                  // Ліва частина (не може бути змінною: lhs->kind != Variable)
    TermPtr rhs;                  // Права частина (Var(rhs) subseteq Var(lhs))
    std::string label;            // Текстова мітка або коментар
};

// Критична пара, породжена накладанням правил
struct CriticalPair {
    TermPtr source;               // Базовий уніфікований вираз l1[l2]_p
    TermPtr left;                 // Лівий результат редукції (r1)
    TermPtr right;                // Правий результат редукції (l1[r2]_p)
    uint32_t rule1_id;            // Ідентифікатор першого правила
    uint32_t rule2_id;            // Ідентифікатор другого правила
};

// Підстановка (відображення змінних у терми)
using Substitution = std::unordered_map<std::string, TermPtr>;

} // namespace trs
