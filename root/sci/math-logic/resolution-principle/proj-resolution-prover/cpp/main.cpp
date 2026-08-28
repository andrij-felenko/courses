#include <iostream>
#include <vector>
#include <set>
#include <algorithm>

// Літерали представлені цілими числами (додатні = X, від'ємні = ¬X)
// Клоз є впорядкованою множиною літерлів для швидкого порівняння та уникнення дублікатів (наприклад X v X -> X)
using Clause = std::set<int>;

// База знань
using ClauseSet = std::set<Clause>;

// Функція для виконання резолюції між двома клозами
// Повертає вектор можливих резольвент (їх може бути декілька, якщо є кілька комплементарних пар)
std::vector<Clause> resolve(const Clause& c1, const Clause& c2) {
    std::vector<Clause> resolvents;

    for (int l1 : c1) {
        // Шукаємо комплементарний літерал у c2
        if (c2.find(-l1) != c2.end()) {
            Clause res;
            // Копіюємо всі елементи з c1, окрім l1
            for (int x : c1) if (x != l1) res.insert(x);
            // Копіюємо всі елементи з c2, окрім -l1
            for (int x : c2) if (x != -l1) res.insert(x);
            
            resolvents.push_back(res);
        }
    }
    return resolvents;
}

// Головний цикл резолюційного прувера
bool resolutionProver(ClauseSet kb) {
    ClauseSet newClauses;

    while (true) {
        int pairsChecked = 0;
        newClauses.clear();

        // Ітеруємо по всіх парах клозів (O(N^2) на кожній ітерації)
        for (auto it1 = kb.begin(); it1 != kb.end(); ++it1) {
            auto it2 = it1; ++it2; // Починаємо з наступного, щоб не дублювати пари і не резольвувати з собою
            for (; it2 != kb.end(); ++it2) {
                std::vector<Clause> resolvents = resolve(*it1, *it2);
                
                for (const Clause& res : resolvents) {
                    // Якщо отримали порожній клоз - знайдено протиріччя
                    if (res.empty()) {
                        return true; 
                    }
                    newClauses.insert(res);
                }
                pairsChecked++;
            }
        }

        // Перевіряємо, чи отримали ми хоча б один НОВИЙ клоз
        bool hasNew = false;
        for (const Clause& c : newClauses) {
            if (kb.find(c) == kb.end()) {
                kb.insert(c);
                hasNew = true;
            }
        }

        // Якщо нових клозів немає (сатурація бази знань), протиріччя не знайдено
        if (!hasNew) {
            return false; 
        }
    }
}

int main() {
    // Задача: маємо правила (¬A ∨ B), (¬B ∨ C), і факт (A).
    // Хочемо довести теорему (C).
    // Доведення від супротивного: додаємо заперечення теореми, тобто (¬C), до бази.
    ClauseSet kb = {
        {-1, 2},  // ¬A ∨ B
        {-2, 3},  // ¬B ∨ C
        {1},      // A
        {-3}      // ¬C (Заперечення теореми)
    };

    if (resolutionProver(kb)) {
        std::cout << "Theorem PROVED by contradiction.\n";
    } else {
        std::cout << "Theorem CANNOT be proved.\n";
    }

    return 0;
}
