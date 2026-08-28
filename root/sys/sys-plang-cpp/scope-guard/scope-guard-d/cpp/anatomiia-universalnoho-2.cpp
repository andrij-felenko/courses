void apply_transfer_safe(Account& from, Account& to, double amount, AuditLog& log, Network& net) {
    from.balance -= amount;
    to.balance += amount;
    // Реєструємо відкат балансу поруч зі зміною:
    auto balance_guard = ScopeGuard([&] {
        from.balance += amount;
        to.balance += amount;
    });

    auto* tx_buf = new TransactionRecord();
    // Реєструємо видалення пам'яті:
    auto memory_guard = ScopeGuard([tx_buf] {
        delete tx_buf;
    });

    log.append(from.id(), to.id(), amount);
    auto log_guard = ScopeGuard([&] {
        log.rollback_last();
    });

    net.send_receipt(from.id(), amount);

    // УСІ кроки виконано успішно: скасовуємо відкати бізнес-стану
    log_guard.dismiss();
    balance_guard.dismiss();

    // memory_guard НЕ скасовуємо — tx_buf треба видалити наприкінці в будь-якому разі
}
