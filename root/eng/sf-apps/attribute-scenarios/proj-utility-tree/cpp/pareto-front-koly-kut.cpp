// A домінує над B: A не гірший за обома осями й строго кращий хоч за однією.
// «Кращий» = більший: більша важливість І більша складність — «драйверніший».
bool dominates(const Scenario& a, const Scenario& b) {
    return a.importance >= b.importance && a.difficulty >= b.difficulty &&
           (a.importance > b.importance || a.difficulty > b.difficulty);
}

// Парето-фронт: сценарії, яких не домінує жоден інший.
std::vector<Scenario> paretoFront(const std::vector<Scenario>& items) {
    std::vector<Scenario> front;
    std::copy_if(items.begin(), items.end(), std::back_inserter(front),
                 [&](const Scenario& a) {
                     return std::none_of(items.begin(), items.end(),
                         [&](const Scenario& b) { return dominates(b, a); });
                 });
    return front;
}
