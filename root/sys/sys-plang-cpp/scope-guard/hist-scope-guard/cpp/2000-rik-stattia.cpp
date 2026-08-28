// Концептуальний вигляд використання в бібліотеці Loki (2000–2001 рр.)
void process_transaction(Account& acc, double amount, Logger& log, Network& net) {
    acc.reserve(amount);
    ScopeGuard guard_acc = MakeObjGuard(acc, &Account::cancel_reservation, amount);

    log.record_intent(acc.id(), amount);
    ScopeGuard guard_log = MakeObjGuard(log, &Logger::cancel_intent, acc.id(), amount);

    net.notify_peer(acc.id(), amount);

    // Якщо дійшли сюди — все успішно, скасовуємо відкат:
    guard_log.dismiss();
    guard_acc.dismiss();
}
