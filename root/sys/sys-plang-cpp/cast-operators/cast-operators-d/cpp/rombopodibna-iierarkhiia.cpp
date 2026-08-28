struct Node { virtual ~Node() = default; };
struct LeftBranch : virtual Node {};
struct RightBranch : virtual Node {};
struct DiamondNode : LeftBranch, RightBranch {};

void inspect_diamond(Node* node) {
    // ПОМИЛКА КОМПІЛЯЦІЇ: static_cast не може виконати downcast від віртуальної бази!
    // DiamondNode* d = static_cast<DiamondNode*>(node); // Error: cannot cast from virtual base

    // ЄДИНИЙ безпечний спосіб — dynamic_cast:
    DiamondNode* d = dynamic_cast<DiamondNode*>(node);
}
