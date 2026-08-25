# Симуляція Форсингу на C++17

[Метод форсингу Коена](root:math-logic/cohen-forcing) є глибоко абстрактним логічним інструментом, але ми можемо створити програмну модель, яка симулює основні ідеї Коена: частково впорядковані умови, їх поєднання та створення генерного фільтра. Нижче наведено практичний скрипт на C++17, який реалізує спрощену симуляцію додавання нових "дійсних чисел" до базової моделі за допомогою 5-компонентної структури.

Ця структура складається з таких компонентів:
1. Базова модель (набір існуючих "чисел").
2. Умова форсингу (часткова інформація про нове число).
3. Відношення порядку між умовами.
4. Щільні множини (вимоги, які має задовольнити нове число).
5. Генерний фільтр, що формує фінальний результат.

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <optional>
#include <algorithm>

// 1. Умова форсингу: представляє часткову інформацію про нове дійсне число.
// Тут дійсне число моделюється як нескінченна послідовність бітів (0 або 1).
// Умова визначає значення лише скінченної кількості бітів за їхніми індексами.
struct ForcingCondition {
    std::map<int, int> bits;

    // 2. Відношення порядку: q <= p означає, що q містить більше інформації.
    bool is_extension_of(const ForcingCondition& p) const {
        for (const auto& [index, value] : p.bits) {
            auto it = bits.find(index);
            if (it == bits.end() || it->second != value) {
                return false; // q суперечить p або не містить інформації з p
            }
        }
        return true;
    }

    // Перевірка на сумісність двох умов
    bool is_compatible_with(const ForcingCondition& other) const {
        for (const auto& [index, value] : bits) {
            auto it = other.bits.find(index);
            if (it != other.bits.end() && it->second != value) {
                return false;
            }
        }
        return true;
    }
};

// 3. Щільна множина: функція, яка генерує умову, що задовольняє певну властивість.
// У реальному форсингу щільних множин нескінченно багато, ми моделюємо кілька базових.
using DenseSet = std::function<std::optional<ForcingCondition>(const ForcingCondition&)>;

// 4. Генерний фільтр: послідовно накопичує умови, перетинаючи щільні множини.
class GenericFilter {
private:
    ForcingCondition current_condition;

public:
    bool meet_dense_set(const DenseSet& D) {
        auto extension = D(current_condition);
        if (extension.has_value()) {
            current_condition = extension.value();
            return true;
        }
        return false;
    }

    void print_state() const {
        std::cout << "Поточний генерний фільтр фіксує біти: ";
        for (const auto& [idx, val] : current_condition.bits) {
            std::cout << "x[" << idx << "]=" << val << " ";
        }
        std::cout << "\n";
    }
};

// 5. Симулятор розширення: збирає все разом.
int main() {
    std::cout << "--- Симулятор Форсингу Коена ---\n";
    GenericFilter G;

    // Щільна множина 1: Нове число повинно мати визначений біт на позиції 0
    DenseSet d1 = [](const ForcingCondition& p) -> std::optional<ForcingCondition> {
        if (p.bits.count(0) > 0) return p;
        ForcingCondition ext = p;
        ext.bits[0] = 1; // Форсуємо 1
        return ext;
    };

    // Щільна множина 2: Нове число повинно відрізнятися від числа '0000...'
    // Тобто має бути хоча б одна одиниця на позиції > 0.
    DenseSet d2 = [](const ForcingCondition& p) -> std::optional<ForcingCondition> {
        for (const auto& [idx, val] : p.bits) {
            if (idx > 0 && val == 1) return p; // Вже задоволено
        }
        ForcingCondition ext = p;
        int next_idx = p.bits.empty() ? 1 : p.bits.rbegin()->first + 1;
        ext.bits[next_idx] = 1; 
        return ext;
    };

    std::cout << "Початковий стан (порожня умова):\n";
    G.print_state();

    std::cout << "\nПеретин із щільною множиною D1 (визначення нульового біта):\n";
    G.meet_dense_set(d1);
    G.print_state();

    std::cout << "\nПеретин із щільною множиною D2 (відмінність від нульової послідовності):\n";
    G.meet_dense_set(d2);
    G.print_state();

    std::cout << "\nУ розширеній моделі V[G] з'явилося нове 'дійсне число', "
              << "сформоване накопиченням умов з генерного фільтра.\n";

    return 0;
}
```

### Як це працює
Код ілюструє ядро логіки форсингу. `ForcingCondition` діє як наближення до нового об'єкта. Функція `is_extension_of` відображає концепцію посилення умов: чим більше бітів визначено, тим "меншою" (сильнішою) є умова в частковому порядку. 

Щільні множини `d1` та `d2` моделюють вимоги базового всесвіту. У реальному математичному доведенні всесвіт V містить нескінченно багато таких щільних множин. `GenericFilter` крок за кроком адаптує свою поточну умову, гарантуючи, що нове число успішно уникає збігів із уже існуючими об'єктами. Коли фільтр перетинає всі щільні множини базової моделі, він повністю визначає нове дійсне число (так зване "число Коена"), яке розширює всесвіт.

Симулятор показує, що додавання об'єктів — це не створення їх з повітря, а ретельне проходження крізь систему логічних обмежень.
