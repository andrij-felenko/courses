int countNodesIter(const Component* root) {
    int total = 0;
    std::vector<const Component*> stack{ root };   // наш власний стек — у купі
    while (!stack.empty()) {
        const Component* node = stack.back();      // беремо вузол на обробку
        stack.pop_back();
        ++total;                                   // рахуємо його
        if (auto* folder = dynamic_cast<const Folder*>(node))
            for (const auto& child : folder->children)
                stack.push_back(child.get());      // дітей — назад у стек, на потім
    }
    return total;
}

// countNodesIter(tree.get())  →  10
