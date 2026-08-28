// Контейнер правил є незмінним (immutable) об'єктом
std::atomic<std::shared_ptr<const FlagRuleset>> current_ruleset_;

// Читання на гарячому шляху (Lock-Free)
bool is_enabled(...) {
    auto rules = current_ruleset_.load(std::memory_order_relaxed);
    return rules->eval(...);
}

// Оновлення з фонового потоку
void update_ruleset(std::shared_ptr<const FlagRuleset> new_rules) {
    current_ruleset_.store(new_rules, std::memory_order_release);
}
