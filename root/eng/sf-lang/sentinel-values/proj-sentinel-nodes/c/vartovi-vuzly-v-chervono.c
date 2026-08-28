// Класична перевірка БЕЗ вартового: заплутана й повільна
typedef enum { RED, BLACK } Color;
typedef struct RBNode {
    int key;
    Color color;
    struct RBNode *left, *right, *parent;
} RBNode;

bool is_uncle_red_classic(RBNode* z) {
    if (z->parent != NULL && z->parent->parent != NULL) {
        RBNode* grandparent = z->parent->parent;
        if (grandparent->right != NULL && grandparent->right != z->parent) {
            return grandparent->right->color == RED;
        }
    }
    return false;
}
