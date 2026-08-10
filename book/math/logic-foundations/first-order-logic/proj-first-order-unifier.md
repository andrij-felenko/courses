# ⚙️ Уніфікатор логіки першого порядку (First-Order Logic Unifier)

Уніфікація термів логіки першого порядку знаходить найбільш загальну підстановку (MGU) для зведення двох символьних виразів до ідентичного вигляду.

## Постановка інженерної задачі та інтуїція рішення
Уніфікація — це процес знаходження такої підстановки (substitution) змінних, яка робить два логічних терми синтаксично ідентичними. Наприклад, терми `f(X, a)` та `f(b, Y)` можна уніфікувати, замінивши `X` на `b` та `Y` на `a`. Це є фундаментальною операцією, оскільки вона дозволяє виводити нові факти з існуючих правил (наприклад, Modus Ponens із кванторами загальності).

Інженерний виклик полягає у правильній обробці вкладених термів (дерев) та уникненні нескінченних циклів. Ключовою проблемою є "occurs check" (перевірка входження): ми не можемо уніфікувати змінну `X` з термом, який містить саму цю змінну `X` (наприклад, `X` та `f(X)`), оскільки це призведе до рекурсивного розгортання нескінченного розміру. 

## Логічна архітектура та алгоритм Мартеллі-Монтанарі (в спрощенні)
Алгоритм приймає два терми (дерева) і намагається побудувати мапу підстановок `std::map<Variable, Term>`.
1. **Ідентичність:** Якщо обидва терми є однаковими змінними або однаковими константами, уніфікація успішна (підстановка не потрібна).
2. **Зв'язування змінної:** Якщо один терм — це змінна `V`, а інший — довільний терм `T`:
   - Спочатку перевіряємо, чи зустрічається `V` всередині `T` (Occurs Check). Якщо так — уніфікація неможлива.
   - Інакше додаємо підстановку `V -> T`.
3. **Функціональні символи (Предикати):** Якщо обидва терми є функціями `f(t1, ..., tn)` та `g(u1, ..., um)`:
   - Перевіряємо, чи збігаються їхні імена (`f == g`) та арність (кількість аргументів `n == m`). Якщо ні — провал.
   - Рекурсивно уніфікуємо відповідні аргументи `t_i` та `u_i`, оновлюючи глобальну мапу підстановок на кожному кроці та застосовуючи нові підстановки до залишкових термів.

## Повний робочий код на C++

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <algorithm>

// Типи термів
enum class TermType { VARIABLE, CONSTANT, FUNCTION };

// Вузол терму
struct Term {
    TermType type;
    std::string name;
    std::vector<std::shared_ptr<Term>> args;

    // Конструктор для змінних/констант
    Term(TermType t, std::string n) : type(t), name(std::move(n)) {}
    
    // Конструктор для функцій
    Term(std::string n, std::vector<std::shared_ptr<Term>> a) 
        : type(TermType::FUNCTION), name(std::move(n)), args(std::move(a)) {}
};

using Substitution = std::map<std::string, std::shared_ptr<Term>>;

// Перевірка входження (Occurs Check)
bool occursCheck(const std::string& varName, const std::shared_ptr<Term>& term) {
    if (term->type == TermType::VARIABLE) {
        return term->name == varName;
    }
    if (term->type == TermType::FUNCTION) {
        for (const auto& arg : term->args) {
            if (occursCheck(varName, arg)) return true;
        }
    }
    return false;
}

// Функція для застосування підстановок до терму (оновлення середовища)
std::shared_ptr<Term> applySubstitution(std::shared_ptr<Term> term, const Substitution& sub) {
    if (term->type == TermType::VARIABLE) {
        auto it = sub.find(term->name);
        if (it != sub.end()) {
            return applySubstitution(it->second, sub); // Рекурсивне розгортання
        }
        return term;
    }
    if (term->type == TermType::FUNCTION) {
        std::vector<std::shared_ptr<Term>> newArgs;
        for (const auto& arg : term->args) {
            newArgs.push_back(applySubstitution(arg, sub));
        }
        return std::make_shared<Term>(term->name, newArgs);
    }
    return term; // КОНСТАНТА
}

// Головна функція уніфікації
bool unify(std::shared_ptr<Term> t1, std::shared_ptr<Term> t2, Substitution& sub) {
    t1 = applySubstitution(t1, sub);
    t2 = applySubstitution(t2, sub);

    // Якщо терми ідентичні, нічого робити не треба
    if (t1->type == t2->type && t1->name == t2->name && t1->args.empty() && t2->args.empty()) {
        return true;
    }

    // Якщо t1 - змінна
    if (t1->type == TermType::VARIABLE) {
        if (occursCheck(t1->name, t2)) return false; // Occurs check
        sub[t1->name] = t2;
        return true;
    }

    // Якщо t2 - змінна
    if (t2->type == TermType::VARIABLE) {
        if (occursCheck(t2->name, t1)) return false;
        sub[t2->name] = t1;
        return true;
    }

    // Якщо обидва - функції
    if (t1->type == TermType::FUNCTION && t2->type == TermType::FUNCTION) {
        if (t1->name != t2->name || t1->args.size() != t2->args.size()) {
            return false;
        }
        for (size_t i = 0; i < t1->args.size(); ++i) {
            if (!unify(t1->args[i], t2->args[i], sub)) {
                return false;
            }
        }
        return true;
    }

    // Константа з іншою константою або функцією (вже відфільтровано ідентичність)
    return false;
}

// Допоміжна функція для виводу термів
void printTerm(const std::shared_ptr<Term>& term) {
    if (term->type == TermType::VARIABLE) std::cout << "?" << term->name;
    else if (term->type == TermType::CONSTANT) std::cout << term->name;
    else {
        std::cout << term->name << "(";
        for (size_t i = 0; i < term->args.size(); ++i) {
            printTerm(term->args[i]);
            if (i < term->args.size() - 1) std::cout << ", ";
        }
        std::cout << ")";
    }
}

int main() {
    // Уніфікація: f(X, b) та f(a, Y)
    auto varX = std::make_shared<Term>(TermType::VARIABLE, "X");
    auto constB = std::make_shared<Term>(TermType::CONSTANT, "b");
    auto t1 = std::make_shared<Term>("f", std::vector<std::shared_ptr<Term>>{varX, constB});

    auto constA = std::make_shared<Term>(TermType::CONSTANT, "a");
    auto varY = std::make_shared<Term>(TermType::VARIABLE, "Y");
    auto t2 = std::make_shared<Term>("f", std::vector<std::shared_ptr<Term>>{constA, varY});

    Substitution sub;
    if (unify(t1, t2, sub)) {
        std::cout << "Unification SUCCESS. Substitution:\n";
        for (const auto& [var, term] : sub) {
            std::cout << "?" << var << " -> ";
            printTerm(term);
            std::cout << "\n";
        }
    } else {
        std::cout << "Unification FAILED.\n";
    }

    return 0;
}
```

## Построчний аналіз, пам'ять та керування ресурсами
В коді ми використовуємо `std::shared_ptr<Term>`. Це виправдано, оскільки при побудові підстановок одне і те ж піддерево (наприклад, константа `a`) може багаторазово присвоюватись різним змінним у `Substitution`. Використання спільних вказівників дозволяє уникнути глибокого копіювання AST дерев, реалізуючи ефективне спільне використання пам'яті (structural sharing).

Функція `applySubstitution` має критично важливий інваріант: вона завжди перевіряє, чи була поточна змінна вже замінена на щось раніше. Якщо ми раніше визначили, що `X -> Y`, а потім `Y -> a`, виклик `applySubstitution(X)` транзитивно розгорне `X` до `a`. Це запобігає виникненню непослідовних станів уніфікації.

`occursCheck` виконує глибокий пошук по дереву `O(M)`. Якщо ми спробуємо уніфікувати `X` і `f(X)`, ця функція зловить цикл і поверне `false`, запобігаючи нескінченній рекурсії стеку викликів і можливого Stack Overflow.

## Вхідні та вихідні дані і оцінка складності (I/O)
Приклад виконання для `f(X, b)` та `f(a, Y)`:
```text
Unification SUCCESS. Substitution:
?X -> a
?Y -> b
```

**Оцінка складності:**
- **Часова складність:** Описаний алгоритм є наївним, і через `applySubstitution` та `occursCheck` у найгіршому випадку він може мати експоненційну або квадратичну часову складність O(N^2) від розміру термів. Сучасні алгоритми уніфікації (наприклад, алгоритм Мартеллі-Монтанарі з використанням Union-Find) можуть досягати майже лінійного часу O(N \alpha(N)).
- **Просторова складність:** O(V + D), де V — кількість змінних для мапи підстановок, а D — максимальна глибина дерева термів (для стеку рекурсії). Завдяки `shared_ptr` ми не роздуваємо пам'ять під час зв'язування.
