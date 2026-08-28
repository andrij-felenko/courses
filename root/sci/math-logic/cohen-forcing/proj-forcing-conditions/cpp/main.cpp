#include <iostream>
#include <vector>
#include <map>
#include <optional>
#include <algorithm>
#include <functional>
#include <string>

// 1. Умова форсингу (часткова функція від індексу до біта).
// У пам'яті це std::map. Менша кількість записів означає "слабшу" умову.
// Більше записів = більше інформації (сильніша умова).
struct Condition {
    std::map<int, int> fixed_bits;

    // Уточнення: поточна умова <= other (поточна сильніша за other).
    // Поточна умова повинна містити ВСІ пари з other.
    bool extends(const Condition& other) const {
        for (const auto& [index, bit] : other.fixed_bits) {
            auto it = fixed_bits.find(index);
            if (it == fixed_bits.end() || it->second != bit) {
                return false;
            }
        }
        return true;
    }
    
    // Друк для відладки та візуалізації
    void print() const {
        std::cout << "{";
        for (const auto& [i, b] : fixed_bits) {
            std::cout << i << ":" << b << " ";
        }
        std::cout << "} ";
    }
};

// 2 & 3. Перевірка сумісності двох умов.
// Якщо вони фіксують різні значення для одного й того ж біта, вони несумісні (p ⊥ q).
// Якщо сумісні, повертає їхнє об'єднання — найслабшу умову, яка сильніша за обидві.
std::optional<Condition> get_compatible_extension(const Condition& p, const Condition& q) {
    Condition r = p;
    for (const auto& [index, bit] : q.fixed_bits) {
        auto it = r.fixed_bits.find(index);
        // Якщо індекс вже зафіксований і його значення відрізняється — конфлікт!
        if (it != r.fixed_bits.end() && it->second != bit) {
            return std::nullopt; // Несумісні
        }
        // Інакше додаємо нову інформацію до результату
        r.fixed_bits[index] = bit;
    }
    return r;
}

// 4. Щільна множина. 
// У реальному форсингу щільна множина нескінченна, тут моделюємо її як генератор.
// За визначенням, D є щільною, якщо для будь-якого p існує q в D, таке що q <= p.
struct DenseSet {
    std::string name;
    // Функція, що повертає розширення умови p, яке гарантовано належить цій щільній множині
    std::function<Condition(const Condition&)> get_extension_in_dense_set;
};

// 5. Алгоритм пошуку генерного фільтра.
// Фільтр має перетнутися з усіма заданими щільними множинами з D_list.
// Це прямий аналог побудови фільтра за лемою Ресівої-Сікорського для зліченного набору.
std::vector<Condition> build_generic_filter(
        const std::vector<DenseSet>& D_list, 
        Condition starting_condition = {}) 
{
    std::vector<Condition> filter;
    Condition current = starting_condition;
    filter.push_back(current);

    std::cout << "Starting filter generation...\n";

    // Ітеруємося по всіх вимогах (щільних множинах)
    for (const auto& D : D_list) {
        std::cout << "Meeting dense set: " << D.name << " -> ";
        
        // Знаходимо умову, яка сильніша за поточну і одночасно задовольняє D
        Condition next_cond = D.get_extension_in_dense_set(current);
        next_cond.print();
        std::cout << "\n";
        
        filter.push_back(next_cond);
        current = next_cond; // Наступний крок почнеться з цієї посиленої умови
    }

    return filter;
}

int main() {
    // Визначимо кілька щільних множин.
    // Наприклад: множина умов D_i = { p | p фіксує значення біта i }.
    // Очевидно, що ця множина є щільною: для будь-якої поточної умови, 
    // якщо біт 'i' ще не зафіксований, ми можемо розширити умову, додавши фіксацію цього біта.
    std::vector<DenseSet> dense_sets;
    for (int i = 0; i < 5; ++i) {
        dense_sets.push_back({
            "Bit " + std::to_string(i) + " is determined",
            [i](const Condition& p) -> Condition {
                Condition q = p;
                // Якщо біт ще не визначений, ми приймаємо рішення: фіксуємо його в 1
                // У справжньому форсингу це рішення залежить від конкретного генерного фільтра.
                if (q.fixed_bits.find(i) == q.fixed_bits.end()) {
                    q.fixed_bits[i] = 1; 
                }
                return q;
            }
        });
    }

    // Будуємо генерний фільтр починаючи з порожньої умови (ніякої інформації).
    Condition empty_condition;
    std::vector<Condition> G = build_generic_filter(dense_sets, empty_condition);

    std::cout << "\nFinal Filter (Union forms the new object): ";
    // Оскільки кожна наступна умова розширює попередню, остання умова у списку 
    // містить об'єднання всієї накопиченої інформації.
    G.back().print(); 
    std::cout << "\n";

    return 0;
}
