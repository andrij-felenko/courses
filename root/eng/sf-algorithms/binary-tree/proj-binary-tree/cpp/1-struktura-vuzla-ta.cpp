#include <iostream>
#include <memory>
#include <vector>
#include <queue>
#include <stack>
#include <algorithm>
#include <string>
#include <unordered_map>

// Вузол двійкового дерева мовою C++ з використанням розумних вказівників (RAII)
struct TreeNode {
    int data;
    std::unique_ptr<TreeNode> left;
    std::unique_ptr<TreeNode> right;

    explicit TreeNode(int val) 
        : data(val), left(nullptr), right(nullptr) {}

    // Фабричний метод для зручного створення вузлів
    static std::unique_ptr<TreeNode> make(int val) {
        return std::make_unique<TreeNode>(val);
    }
};

// В C++ пам'ять автоматично звільняється деструктором std::unique_ptr,
// додаткова функція destroy_tree не потрібна!
