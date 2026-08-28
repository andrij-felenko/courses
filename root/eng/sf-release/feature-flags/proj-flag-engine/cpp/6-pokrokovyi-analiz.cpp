int main() {
    FlagEngine engine;

    // Створюємо початковий набір правил для фічі нового оформлення замовлення
    auto initial_rules = std::make_shared<RuleSet>();
    
    FlagDefinition checkout_flag;
    checkout_flag.key = "new-checkout-v2";
    checkout_flag.default_value = false;
    checkout_flag.rollout_percentage = 20; // 20% звичайних користувачів
    checkout_flag.whitelist_users = { "beta_tester_42", "qa_lead" };
    checkout_flag.rules.push_back({ "country", "UA", true }); // 100% для користувачів з UA

    initial_rules->flags["new-checkout-v2"] = checkout_flag;
    engine.update_rules(initial_rules);

    // Сценарій 1: Тестувальник із Whitelist (примусове ввімкнення незалежно від правил)
    EvaluationContext beta_user{ "beta_tester_42", {} };
    auto r1 = engine.evaluate("new-checkout-v2", beta_user);
    std::cout << "Beta user: " << r1.value << " (" << r1.reason << ")\n";
    // Очікуваний вивід: Beta user: 1 (OVERRIDE)

    // Сценарій 2: Користувач з України (спрацьовує правило таргетингу за атрибутом)
    EvaluationContext ua_user{ "user_999", { {"country", std::string("UA")} } };
    auto r2 = engine.evaluate("new-checkout-v2", ua_user);
    std::cout << "UA user: " << r2.value << " (" << r2.reason << ")\n";
    // Очікуваний вивід: UA user: 1 (RULE_MATCH)

    // Сценарій 3: Звичайний користувач з Польщі (розрахунок хеш-бакета для 20% розкатки)
    EvaluationContext pl_user{ "user_1001", { {"country", std::string("PL")} } };
    auto r3 = engine.evaluate("new-checkout-v2", pl_user);
    std::cout << "PL user (20% rollout): " << r3.value << " (" << r3.reason << ")\n";

    // Сценарій 4: Аварійне вимкнення (Kill Switch) під час збою нової платіжки
    auto emergency_rules = std::make_shared<RuleSet>();
    checkout_flag.rollout_percentage = 0;
    checkout_flag.rules.clear();
    checkout_flag.whitelist_users.clear();
    emergency_rules->flags["new-checkout-v2"] = checkout_flag;

    // Атомарна підміна: миттєве скидання на нуль для всіх потоків без перезавантаження
    engine.update_rules(emergency_rules);
    auto r4 = engine.evaluate("new-checkout-v2", ua_user);
    std::cout << "After emergency rollback: " << r4.value << " (" << r4.reason << ")\n";
    // Очікуваний вивід: After emergency rollback: 0 (DEFAULT)

    return 0;
}
