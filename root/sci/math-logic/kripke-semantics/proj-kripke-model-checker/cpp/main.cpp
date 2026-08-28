#include <iostream>
#include <vector>
#include <string>
#include <set>
#include <map>
#include <queue>

// Тип для станів (ідентифікатори)
using State = int;
// Тип для атомарних висловлювань
using AtomicProposition = std::string;

class KripkeStructure {
private:
    std::set<State> S;                                     // Множина станів (S)
    std::set<State> S0;                                    // Початкові стани (S0)
    std::map<State, std::set<State>> R;                    // Відношення переходу (R)
    std::set<AtomicProposition> AP;                        // Атомарні висловлювання (AP)
    std::map<State, std::set<AtomicProposition>> L;        // Функція розмітки (L)

public:
    // Додавання стану
    void addState(State s, bool isInitial = false) {
        S.insert(s);
        if (isInitial) {
            S0.insert(s);
        }
    }

    // Додавання переходу (від s_from до s_to)
    void addTransition(State s_from, State s_to) {
        if (S.count(s_from) && S.count(s_to)) {
            R[s_from].insert(s_to);
        }
    }

    // Реєстрація атомарного висловлювання
    void addProposition(const AtomicProposition& ap) {
        AP.insert(ap);
    }

    // Розмітка стану висловлюванням
    void labelState(State s, const AtomicProposition& ap) {
        if (S.count(s) && AP.count(ap)) {
            L[s].insert(ap);
        }
    }

    // Перевірка, чи істинне висловлювання у стані (моделює відношення s ⊨ p)
    bool isTrueInState(State s, const AtomicProposition& p) const {
        if (L.count(s) == 0) return false;
        return L.at(s).count(p) > 0;
    }

    // Перевірка кон'юнкції (p AND q)
    bool checkAnd(State s, const AtomicProposition& p, const AtomicProposition& q) const {
        return isTrueInState(s, p) && isTrueInState(s, q);
    }

    // Перевірка глобальної досяжності: чи досяжний стан, де істинне p
    bool isReachableFromInitial(const AtomicProposition& p) const {
        std::set<State> visited;
        std::queue<State> q;

        // Починаємо пошук з усіх початкових станів
        for (State init_s : S0) {
            q.push(init_s);
            visited.insert(init_s);
        }

        while (!q.empty()) {
            State curr = q.front();
            q.pop();

            // Якщо знайшли стан, де виконується p - властивість істинна
            if (isTrueInState(curr, p)) {
                return true;
            }

            // Додаємо сусідів до черги для подальшого обходу
            if (R.count(curr)) {
                for (State next_s : R.at(curr)) {
                    if (visited.count(next_s) == 0) {
                        visited.insert(next_s);
                        q.push(next_s);
                    }
                }
            }
        }
        return false; // Такий стан недосяжний
    }
};

int main() {
    KripkeStructure model;

    // 1. Створюємо стани (S). Стан 1 є початковим (S0).
    model.addState(1, true);
    model.addState(2);
    model.addState(3);

    // 2. Визначаємо переходи (R)
    model.addTransition(1, 2);
    model.addTransition(2, 3);
    model.addTransition(3, 1); // Утворюємо цикл

    // 3. Визначаємо атомарні висловлювання (AP)
    model.addProposition("ready");
    model.addProposition("running");
    model.addProposition("finished");

    // 4. Розмітка станів (L)
    model.labelState(1, "ready");
    model.labelState(2, "running");
    model.labelState(3, "finished");

    // 5. Тестування системи
    std::cout << "State 1 is 'ready': " 
              << (model.isTrueInState(1, "ready") ? "true" : "false") << "\n";
              
    std::cout << "State 2 is 'ready' AND 'running': " 
              << (model.checkAnd(2, "ready", "running") ? "true" : "false") << "\n";

    std::cout << "Is 'finished' reachable from initial states? " 
              << (model.isReachableFromInitial("finished") ? "Yes" : "No") << "\n";

    return 0;
}
