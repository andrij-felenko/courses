// Елегантна перевірка З ВАРТОВИМ T.nil у C++
enum class RBColor : uint8_t { Red, Black };

struct RBNode {
    int key{0};
    RBColor color{RBColor::Black};
    RBNode* left{nullptr};
    RBNode* right{nullptr};
    RBNode* parent{nullptr};
};

bool is_uncle_red_sentinel(const RBNode* z, const RBNode* nil) noexcept {
    // Вказівник grandparent->right ніколи не дорівнює nullptr:
    // якщо вузла немає, він вказує на nil, колір якого завжди Black!
    const RBNode* uncle = z->parent->parent->right;
    return uncle->color == RBColor::Red;
}
