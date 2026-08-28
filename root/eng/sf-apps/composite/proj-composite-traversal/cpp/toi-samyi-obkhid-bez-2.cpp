#include <queue>

std::vector<std::string> collectByLevel(const Component* root) {
    std::vector<std::string> out;
    std::queue<const Component*> queue;            // черга замість стека — обхід ушир
    queue.push(root);
    while (!queue.empty()) {
        const Component* node = queue.front();     // беремо з ПОЧАТКУ (FIFO)
        queue.pop();
        out.push_back(node->name);
        if (auto* folder = dynamic_cast<const Folder*>(node))
            for (const auto& child : folder->children)
                queue.push(child.get());           // діти йдуть у хвіст
    }
    return out;   // [проєкт, src, docs, README.md, main.ts, util.ts, ui, ...]
}
