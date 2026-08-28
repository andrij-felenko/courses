#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <format>

struct FlatRecord {
    int id;
    int parent_id;
    std::string name;
};

class TreeNode {
public:
    int id;
    std::string name;
    int lft{0};
    int rgt{0};
    int depth{0};
    std::string path;
    TreeNode* parent{nullptr};
    std::vector<std::unique_ptr<TreeNode>> children;

    explicit TreeNode(int node_id, std::string_view node_name)
        : id(node_id), name(node_name) {}

    void add_child(std::unique_ptr<TreeNode> child) {
        child->parent = this;
        children.push_back(std::move(child));
    }

    void compute_metrics(int& counter, int current_depth, std::string_view parent_path) {
        lft = counter++;
        depth = current_depth;
        path = parent_path.empty() ? ("/" + std::to_string(id) + "/")
                                   : (std::string(parent_path) + std::to_string(id) + "/");

        for (const auto& child : children) {
            child->compute_metrics(counter, current_depth + 1, path);
        }

        rgt = counter++;
    }

    void print() const {
        std::string indent(depth * 2, ' ');
        std::cout << indent << "|- [" << id << "] " << name
                  << " (lft: " << lft << ", rgt: " << rgt
                  << ", depth: " << depth << ", path: " << path << ")\n";
        for (const auto& child : children) {
            child->print();
        }
    }
};

int main() {
    std::vector<FlatRecord> db_records = {
        {1, 0, "Каталог"},
        {2, 1, "Електроніка"},
        {3, 1, "Одяг"},
        {4, 2, "Телефони"},
        {5, 2, "Ноутбуки"},
        {6, 3, "Взуття"}
    };

    std::unordered_map<int, std::unique_ptr<TreeNode>> node_map;
    std::unordered_map<int, TreeNode*> raw_ptrs;

    // Фаза 1: Створення вузлів за допомогою std::make_unique
    for (const auto& rec : db_records) {
        auto node = std::make_unique<TreeNode>(rec.id, rec.name);
        raw_ptrs[rec.id] = node.get();
        node_map[rec.id] = std::move(node);
    }

    std::unique_ptr<TreeNode> root;

    // Фаза 2: Збирання ієрархії через переміщення володіння (std::move)
    for (const auto& rec : db_records) {
        if (rec.parent_id == 0) {
            root = std::move(node_map[rec.id]);
        } else {
            auto parent_it = raw_ptrs.find(rec.parent_id);
            auto child_it = node_map.find(rec.id);
            if (parent_it != raw_ptrs.end() && child_it != node_map.end()) {
                parent_it->second->add_child(std::move(child_it->second));
            }
        }
    }

    if (root) {
        int counter = 1;
        root->compute_metrics(counter, 0, "");
        std::cout << "Побудоване дерево в C++ (автоматичне керування пам'яттю):\n";
        root->print();
    }

    return 0;
}
