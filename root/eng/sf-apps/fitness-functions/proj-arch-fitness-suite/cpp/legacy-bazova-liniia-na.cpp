// current — нинішні порушення (напр. "legacy→report"); baseline — заморожені.
// Падаємо лише на НОВИХ; базу тіснимо до тих старих, що ще лишилися.
std::pair<bool, std::unordered_set<std::string>> gate(
        const std::unordered_set<std::string>& current,
        const std::unordered_set<std::string>& baseline) {
    std::unordered_set<std::string> fresh, kept;
    for (const auto& v : current) {
        if (baseline.count(v)) kept.insert(v);        // старі, що ще лишилися → нова база
        else                   fresh.insert(v);       // порушення, яких у базі не було
    }
    return { fresh.empty(), kept };
}
