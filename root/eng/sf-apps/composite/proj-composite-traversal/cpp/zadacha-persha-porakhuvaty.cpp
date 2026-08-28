int countNodes(const Component* node) {
    if (auto* folder = dynamic_cast<const Folder*>(node)) {   // «це тека?»
        int total = 1;                         // сама тека — один вузол
        for (const auto& child : folder->children)
            total += countNodes(child.get());  // плюс усе, що в кожній дитині
        return total;
    }
    return 1;                                  // листок — рівно один вузол
}

// countNodes(tree.get())  →  10
