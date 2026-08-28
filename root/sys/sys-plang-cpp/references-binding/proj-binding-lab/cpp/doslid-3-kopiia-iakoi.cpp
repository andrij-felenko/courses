static void part_materialization() {
    head("3. Копія, якої немає в тексті");

    std::map<std::string, Loud> registry;
    registry.emplace("альфа", Loud("датчик-альфа"));
    registry.emplace("бета",  Loud("датчик-бета"));

    std::cout << "    цикл із власноруч виписаним типом елемента:\n";
    for (const std::pair<std::string, Loud>& kv : registry)
        std::cout << "        " << kv.first << " → #" << kv.second.id() << '\n';

    std::cout << "    цикл із const auto&:\n";
    for (const auto& kv : registry)
        std::cout << "        " << kv.first << " → #" << kv.second.id() << '\n';
}
