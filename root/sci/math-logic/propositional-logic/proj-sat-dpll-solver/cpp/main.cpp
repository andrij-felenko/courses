#include <iostream>
#include <vector>
#include <algorithm>
#include <set>

// Представлення CNF формули
// Літерали: 1 для X1, -1 для NOT X1
using Clause = std::vector<int>;
using Formula = std::vector<Clause>;

// Функція для пошуку одиничного клозу
int findUnitClause(const Formula& formula) {
    for (const auto& clause : formula) {
        if (clause.size() == 1) {
            return clause[0];
        }
    }
    return 0; // 0 означає, що одиничних клозів не знайдено
}

// Функція для застосування поширення одиниць або спрощення після вибору
Formula simplify(Formula formula, int literal) {
    Formula newFormula;
    for (const auto& clause : formula) {
        // Якщо клоз містить літерал, він стає True, тому весь клоз видаляється (задоволений)
        if (std::find(clause.begin(), clause.end(), literal) != clause.end()) {
            continue;
        }
        
        // Якщо клоз містить протилежний літерал, цей літерал стає False і видаляється з клозу
        Clause newClause;
        for (int l : clause) {
            if (l != -literal) {
                newClause.push_back(l);
            }
        }
        newFormula.push_back(newClause);
    }
    return newFormula;
}

// Головна рекурсивна функція DPLL
bool dpll(Formula formula) {
    // 1. Базові випадки
    if (formula.empty()) return true; // Всі клози задоволені
    for (const auto& clause : formula) {
        if (clause.empty()) return false; // Конфлікт: знайдено порожній клоз
    }

    // 2. Unit Propagation (Поширення одиничних клозів)
    int unitLiteral = findUnitClause(formula);
    while (unitLiteral != 0) {
        formula = simplify(formula, unitLiteral);
        if (formula.empty()) return true;
        for (const auto& clause : formula) {
            if (clause.empty()) return false;
        }
        unitLiteral = findUnitClause(formula);
    }

    // 3. Branching (Вибір нерозподіленої змінної)
    // Обираємо перший літерал з першого клозу
    if (formula.empty()) return true; // Перевірка безпеки
    int splitLiteral = formula.front().front();

    // Спроба призначити змінній True
    if (dpll(simplify(formula, splitLiteral))) {
        return true;
    }

    // Backtrack: Спроба призначити змінній False
    return dpll(simplify(formula, -splitLiteral));
}

int main() {
    // Формула: (X1 OR NOT X2) AND (NOT X1 OR X2) AND (X1 OR X2) AND (NOT X1 OR NOT X2)
    // Це класичний приклад нездійсненної формули (XNOR AND XOR).
    Formula cnf = {
        {1, -2},
        {-1, 2},
        {1, 2},
        {-1, -2}
    };

    bool isSatisfiable = dpll(cnf);
    std::cout << "Formula is " << (isSatisfiable ? "SATISFIABLE" : "UNSATISFIABLE") << std::endl;
    
    return 0;
}
