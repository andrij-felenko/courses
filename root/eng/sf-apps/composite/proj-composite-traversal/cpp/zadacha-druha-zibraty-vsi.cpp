// робоча рекурсія: акумулятор out передаємо посиланням і дописуємо в нього
void collectPaths(const Component* node, const std::string& prefix,
                  std::vector<std::string>& out) {
    std::string path = prefix.empty() ? node->name : prefix + "/" + node->name;
    if (auto* folder = dynamic_cast<const Folder*>(node)) {
        for (const auto& child : folder->children)
            collectPaths(child.get(), path, out);   // спускаємось, несучи шлях сюди
    } else {
        out.push_back(path);                         // листок — фіксуємо повний шлях
    }
}

// зручна обгортка: свіжий акумулятор на кожен виклик — тож пастки «спільного
// стандартного значення», як у Python, тут не виникає в принципі
std::vector<std::string> collectPaths(const Component* root) {
    std::vector<std::string> out;
    collectPaths(root, "", out);
    return out;
}
