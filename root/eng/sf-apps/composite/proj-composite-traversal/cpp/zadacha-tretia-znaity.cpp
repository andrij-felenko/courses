const File* largestFile(const Component* node) {
    if (auto* file = dynamic_cast<const File*>(node))
        return file;                             // листок сам собі чемпіон

    auto* folder = static_cast<const Folder*>(node);   // не File → тека
    const File* best = nullptr;
    for (const auto& child : folder->children) {
        const File* candidate = largestFile(child.get());   // чемпіон піддерева-дитини
        if (candidate && (!best || candidate->bytes > best->bytes))
            best = candidate;
    }
    return best;                                 // порожня тека поверне nullptr
}

// auto* top = largestFile(tree.get());  →  modal.ts 1500
