int main() {
    // 1. Ініціалізація: клієнт має депозит $10.00 (10 000 000 мікродоларів)
    CreditQuotaManager quota(10'000'000);
    DoubleEntryLedger ledger;
    EventIngestEngine ingest;
    BatchEventBuffer buffer(100, std::chrono::milliseconds(50));

    std::string tenant = "tenant_alpha_42";

    // Тарифна сітка: перші 1000 токенів по $0.002, понад 1000 по $0.001
    std::vector<PricingTier> tiers = {
        {1000, 2000},                 // $0.002 за одиницю (2000 micros)
        {UINT64_MAX, 1000}            // $0.001 за одиницю (1000 micros)
    };

    // Крок А: Запит на виконання важкого запиту (Hold $5.00)
    auto hold = quota.acquire_hold(tenant, "hold_req_9981", 5'000'000);
    if (!hold) {
        std::cerr << "Помилка: Недостатньо коштів на балансі!" << std::endl;
        return 1;
    }
    std::cout << "Холд успішно встановлено на $5.00. Доступний залишок: $" 
              << (quota.get_available_balance() / 1'000'000.0) << std::endl;

    // Крок Б: Виконання роботи та буферизація події споживання
    UsageEvent event{
        "evt_1001",
        "hash_tenant_alpha_42_req_9981",
        tenant,
        "llm_tokens",
        1500,
        std::chrono::system_clock::now()
    };
    buffer.push(event);

    // Крок В: Скидання пакета та прийом у ядро
    auto batch = buffer.extract_batch();
    for (const auto& ev : batch) {
        auto status = ingest.ingest_event(ev);
        if (status != IngestResult::Accepted) {
            quota.release_hold(*hold);
            return 1;
        }
    }

    // Крок Г: Тарифікація ($2.50)
    CurrencyMicros final_cost = RatingEngine::calculate_graduated_cost(event.quantity, tiers);

    // Крок Ґ: Завершення холду ($2.50 списано, $2.50 повернено в доступні)
    quota.settle_hold(*hold, final_cost);

    // Крок Д: Фіксація в незмінному реєстрі
    ledger.record_usage_charge("tx_88112", tenant, final_cost, event.event_id);

    std::cout << "Операцію завершено." << std::endl;
    std::cout << "Фактична вартість: $" << (final_cost / 1'000'000.0) << std::endl;
    std::cout << "Фінальний доступний баланс: $" << (quota.get_available_balance() / 1'000'000.0) << std::endl;
    std::cout << "Баланс реєстру зобов'язань: $" 
              << (ledger.get_account_balance("liability:" + tenant) / 1'000'000.0) << std::endl;
    std::cout << "Аудит реєстру збігається: " << (ledger.verify_audit_invariant() ? "ТАК" : "НІ") << std::endl;

    return 0;
}
