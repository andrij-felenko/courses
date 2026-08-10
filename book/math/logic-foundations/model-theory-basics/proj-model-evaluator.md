# Скрипт: Інтерпретатор моделей та валідатор формул (C++17)

Цей проєкт демонструє, як можна реалізувати базову структуру моделі `M = (D, I)` та перевірку задоволення формул `M ⊨ φ` мовою C++17. Наш скрипт працюватиме зі скінченною предметною областю та дозволятиме обчислювати істинність базових логічних виразів (кон'юнкцій, диз'юнкцій та кванторів) над цією областю.

У теорії моделей модель складається з універсуму (домену) `D` та інтерпретації `I`, яка зіставляє символам констант, функцій та предикатів реальні об'єкти, операції та відношення над `D`. У нашому коді ми визначимо домен як набір цілих чисел для простоти, а інтерпретації — як `std::map`.

## Архітектура інтерпретатора

Ми реалізуємо 5-компонентну структуру:
1. `Domain`: Множина елементів (цілі числа).
2. `Constants`: Відображення константних символів (рядків) на елементи домену.
3. `Predicates`: Відображення предикатних символів на функції, які приймають вектор аргументів і повертають `bool`.
4. `Functions`: Відображення функціональних символів на функції, що повертають елементи домену.
5. `Environment` (Оцінка змінних `v`): Зіставлення вільних змінних із поточними значеннями.

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <functional>
#include <memory>
#include <stdexcept>

// Тип елемента домену
using Element = int;

// 1. Інтерпретація моделі M = (D, I)
struct Model {
    std::set<Element> domain;
    std::map<std::string, Element> constants;
    std::map<std::string, std::function<bool(const std::vector<Element>&)>> predicates;
    std::map<std::string, std::function<Element(const std::vector<Element>&)>> functions;
};

// 2. Оцінка змінних v
using Environment = std::map<std::string, Element>;

// 3. Базовий клас для всіх термів
class Term {
public:
    virtual ~Term() = default;
    virtual Element evaluate(const Model& M, const Environment& env) const = 0;
};

class Variable : public Term {
    std::string name;
public:
    explicit Variable(std::string n) : name(std::move(n)) {}
    Element evaluate(const Model& M, const Environment& env) const override {
        return env.at(name);
    }
};

class Constant : public Term {
    std::string name;
public:
    explicit Constant(std::string n) : name(std::move(n)) {}
    Element evaluate(const Model& M, const Environment& env) const override {
        return M.constants.at(name);
    }
};

class FunctionCall : public Term {
    std::string name;
    std::vector<std::unique_ptr<Term>> args;
public:
    FunctionCall(std::string n, std::vector<std::unique_ptr<Term>> a) 
        : name(std::move(n)), args(std::move(a)) {}
    Element evaluate(const Model& M, const Environment& env) const override {
        std::vector<Element> evaluated_args;
        for (const auto& arg : args) {
            evaluated_args.push_back(arg->evaluate(M, env));
        }
        return M.functions.at(name)(evaluated_args);
    }
};

// 4. Базовий клас для логічних формул
class Formula {
public:
    virtual ~Formula() = default;
    virtual bool is_satisfied(const Model& M, const Environment& env) const = 0;
};

class PredicateCall : public Formula {
    std::string name;
    std::vector<std::unique_ptr<Term>> args;
public:
    PredicateCall(std::string n, std::vector<std::unique_ptr<Term>> a) 
        : name(std::move(n)), args(std::move(a)) {}
    bool is_satisfied(const Model& M, const Environment& env) const override {
        std::vector<Element> evaluated_args;
        for (const auto& arg : args) {
            evaluated_args.push_back(arg->evaluate(M, env));
        }
        return M.predicates.at(name)(evaluated_args);
    }
};

class ForAll : public Formula {
    std::string var;
    std::unique_ptr<Formula> body;
public:
    ForAll(std::string v, std::unique_ptr<Formula> b) : var(std::move(v)), body(std::move(b)) {}
    bool is_satisfied(const Model& M, const Environment& env) const override {
        for (Element d : M.domain) {
            Environment new_env = env;
            new_env[var] = d;
            if (!body->is_satisfied(M, new_env)) {
                return false;
            }
        }
        return true;
    }
};

class Exists : public Formula {
    std::string var;
    std::unique_ptr<Formula> body;
public:
    Exists(std::string v, std::unique_ptr<Formula> b) : var(std::move(v)), body(std::move(b)) {}
    bool is_satisfied(const Model& M, const Environment& env) const override {
        for (Element d : M.domain) {
            Environment new_env = env;
            new_env[var] = d;
            if (body->is_satisfied(M, new_env)) {
                return true;
            }
        }
        return false;
    }
};

int main() {
    // Побудова конкретної моделі (світ графів)
    Model M;
    M.domain = {1, 2, 3}; // Три вершини
    
    // Інтерпретація предикату "Edge" (Ребро)
    M.predicates["Edge"] = [](const std::vector<Element>& args) {
        if (args[0] == 1 && args[1] == 2) return true;
        if (args[0] == 2 && args[1] == 3) return true;
        return false;
    };

    Environment env;

    // Перевірка формули ∃y Edge(x, y) (З вершини x виходить хоча б одне ребро)
    auto inner_args = std::vector<std::unique_ptr<Term>>();
    inner_args.push_back(std::make_unique<Variable>("x"));
    inner_args.push_back(std::make_unique<Variable>("y"));
    auto edge_xy = std::make_unique<PredicateCall>("Edge", std::move(inner_args));
    
    auto exists_y = std::make_unique<Exists>("y", std::move(edge_xy));

    // Валідація: 
    env["x"] = 1;
    std::cout << "M |= Exists y Edge(1, y)? " 
              << (exists_y->is_satisfied(M, env) ? "True" : "False") << "\n";
              
    env["x"] = 3;
    std::cout << "M |= Exists y Edge(3, y)? " 
              << (exists_y->is_satisfied(M, env) ? "True" : "False") << "\n";

    return 0;
}
```

## Як це працює

Програма відображає концепцію `M ⊨ φ`. Клас `Model` виступає контейнером для універсуму `D` та інтерпретації `I`. `Environment` працює як оцінка вільних змінних `v`. 

Метод `is_satisfied` рекурсивно перевіряє виконання формул. Найцікавішим є підхід до кванторів: класи `ForAll` та `Exists` ітерують по всій множині `domain`, створюючи нове середовище з перепризначеною змінною, і рекурсивно викликають перевірку істинності внутрішньої формули. Це прямолінійна алгоритмічна реалізація семантики Тарського для скінченних моделей. Завдяки поліморфізму, цей підхід можна розширити для підтримки будь-яких логічних зв'язок `AND`, `OR` та `NOT`.
