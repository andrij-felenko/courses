#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Вузол AVL-дерева
typedef struct Node {
    int key;
    int height;
    struct Node *left;
    struct Node *right;
} Node;

// Допоміжні функції для роботи з висотою
static inline int get_height(const Node *node) {
    return node ? node->height : 0;
}

static inline int max(int a, int b) {
    return (a > b) ? a : b;
}

static inline void update_height(Node *node) {
    if (node) {
        node->height = 1 + max(get_height(node->left), get_height(node->right));
    }
}

// Фактор балансу: h(R) - h(L)
static inline int get_balance(const Node *node) {
    return node ? get_height(node->right) - get_height(node->left) : 0;
}

// Створення нового вузла
Node* create_node(int key) {
    Node *node = (Node*)malloc(sizeof(Node));
    if (!node) return NULL;
    node->key = key;
    node->height = 1;
    node->left = NULL;
    node->right = NULL;
    return node;
}

// Праве обертання навколо вузла y (LL-перекіс)
//       y                x
//      / \              / \
//     x   T3   ==>     T1  y
//    / \                  / \
//   T1  T2               T2  T3
Node* rotate_right(Node *y) {
    Node *x = y->left;
    Node *T2 = x->right;

    x->right = y;
    y->left = T2;

    update_height(y);
    update_height(x);

    return x; // Новий корінь піддерева
}

// Ліве обертання навколо вузла x (RR-перекіс)
//     x                  y
//    / \                / \
//   T1  y     ==>      x   T3
//      / \            / \
//     T2  T3         T1  T2
Node* rotate_left(Node *x) {
    Node *y = x->right;
    Node *T2 = y->left;

    y->left = x;
    x->right = T2;

    update_height(x);
    update_height(y);

    return y; // Новий корінь піддерева
}

// Відновлення балансу вузла
Node* rebalance(Node *node) {
    if (!node) return NULL;

    update_height(node);
    int balance = get_balance(node);

    // Лівий перекіс (BF <= -2)
    if (balance < -1) {
        // Якщо в лівого сина правий перекіс — виконуємо LR (попереднє ліве обертання сина)
        if (get_balance(node->left) > 0) {
            node->left = rotate_left(node->left);
        }
        return rotate_right(node);
    }

    // Правий перекіс (BF >= 2)
    if (balance > 1) {
        // Якщо в правого сина лівий перекіс — виконуємо RL (попереднє праве обертання сина)
        if (get_balance(node->right) < 0) {
            node->right = rotate_right(node->right);
        }
        return rotate_left(node);
    }

    return node; // Збалансовано
}

// Рекурсивна вставка ключа
Node* insert(Node *node, int key) {
    if (!node) return create_node(key);

    if (key < node->key) {
        node->left = insert(node->left, key);
    } else if (key > node->key) {
        node->right = insert(node->right, key);
    } else {
        return node; // Дублікати не додаються
    }

    return rebalance(node);
}

// Пошук мінімального вузла в піддереві
Node* min_value_node(Node *node) {
    Node *current = node;
    while (current && current->left != NULL) {
        current = current->left;
    }
    return current;
}

// Рекурсивне видалення ключа
Node* delete_node(Node *root, int key) {
    if (!root) return NULL;

    if (key < root->key) {
        root->left = delete_node(root->left, key);
    } else if (key > root->key) {
        root->right = delete_node(root->right, key);
    } else {
        // Вузол знайдено
        if (!root->left || !root->right) {
            Node *temp = root->left ? root->left : root->right;
            if (!temp) { // Немає дітей (листок)
                temp = root;
                root = NULL;
            } else { // Один син
                *root = *temp; // Копіюємо вміст
            }
            free(temp);
        } else {
            // Два сини: шукаємо найменший ключ у правому піддереві (наступник)
            Node *temp = min_value_node(root->right);
            root->key = temp->key;
            root->right = delete_node(root->right, temp->key);
        }
    }

    if (!root) return NULL;
    return rebalance(root);
}

// Пошук ключа
bool search(const Node *root, int key) {
    if (!root) return false;
    if (key == root->key) return true;
    if (key < root->key) return search(root->left, key);
    return search(root->right, key);
}

// Симетричний обхід (In-order traversal)
void print_in_order(const Node *root) {
    if (root) {
        print_in_order(root->left);
        printf("%d (h=%d, bf=%d) ", root->key, root->height, get_balance(root));
        print_in_order(root->right);
    }
}

// Звільнення пам'яті
void free_tree(Node *root) {
    if (root) {
        free_tree(root->left);
        free_tree(root->right);
        free(root);
    }
}

int main(void) {
    Node *root = NULL;

    int keys[] = {10, 20, 30, 40, 50, 25};
    size_t n = sizeof(keys) / sizeof(keys[0]);

    printf("Вставка елементів: ");
    for (size_t i = 0; i < n; ++i) {
        printf("%d ", keys[i]);
        root = insert(root, keys[i]);
    }
    printf("\nIn-order обхід після вставки:\n");
    print_in_order(root);
    printf("\n");

    printf("\nВидалення 30:\n");
    root = delete_node(root, 30);
    print_in_order(root);
    printf("\n");

    free_tree(root);
    return 0;
}
