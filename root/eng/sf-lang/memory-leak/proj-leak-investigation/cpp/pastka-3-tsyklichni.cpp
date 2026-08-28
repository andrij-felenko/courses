#include <iostream>
#include <memory>

struct BadNode {
    int value;
    std::shared_ptr<BadNode> next;
    ~BadNode() { std::cout << "[BadNode] Знищено " << value << "\n"; }
};

struct GoodNode {
    int value;
    /* Слабке посилання std::weak_ptr не збільшує лічильник сильних власників */
    std::weak_ptr<GoodNode> next;
    ~GoodNode() { std::cout << "[GoodNode] Знищено " << value << "\n"; }
};

int main() {
    std::cout << "--- Циклічне посилання shared_ptr (витік) ---\n";
    {
        auto a = std::make_shared<BadNode>(BadNode{1, nullptr});
        auto b = std::make_shared<BadNode>(BadNode{2, nullptr});
        a->next = b;
        b->next = a; // Цикл! Лічильники обох = 2. При виході з блоку лічильники стануть 1.
    } // Деструктори НЕ викликаються!

    std::cout << "\n--- Розрив циклу через weak_ptr (успішне звільнення) ---\n";
    {
        auto a = std::make_shared<GoodNode>(GoodNode{1, {}});
        auto b = std::make_shared<GoodNode>(GoodNode{2, {}});
        a->next = b;
        b->next = a; // Слабке посилання!
    } // Обидва вузли успішно знищуються автоматично.
    return 0;
}
