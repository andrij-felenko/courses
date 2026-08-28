#include <memory>

// Дерево — це або порожньо (nullptr), або спільний незмінний вузол
// під підрахунком посилань. `const` усередині shared_ptr робить вузол
// недоторканним: у поділений вузол не можна записати.
template <class K, class V>
struct Node {
    K key;
    V val;
    std::shared_ptr<const Node> left;
    std::shared_ptr<const Node> right;
};

template <class K, class V>
using Tree = std::shared_ptr<const Node<K, V>>;

template <class K, class V>
Tree<K, V> insert(const Tree<K, V>& node, K key, V val) {
    if (!node)                                             // дійшли до порожнього місця —
        return std::make_shared<const Node<K, V>>(         //   новий листок
            Node<K, V>{key, val, nullptr, nullptr});

    if (key < node->key)                                   // ліворуч: новий вузол,
        return std::make_shared<const Node<K, V>>(Node<K, V>{
            node->key, node->val,                          //   той самий ключ і значення,
            insert(node->left, key, val),                  //   НОВЕ ліве (рекурсія),
            node->right});                                 //   СПІЛЬНЕ праве: копія shared_ptr = +1 до лічильника

    if (key > node->key)                                   // праворуч: дзеркально
        return std::make_shared<const Node<K, V>>(Node<K, V>{
            node->key, node->val,
            node->left,                                    //   СПІЛЬНЕ ліве
            insert(node->right, key, val)});               //   НОВЕ праве

    return std::make_shared<const Node<K, V>>(Node<K, V>{  // ключ уже є — нове значення,
        key, val, node->left, node->right});               //   обидві дитини спільні (оновлення)
}
