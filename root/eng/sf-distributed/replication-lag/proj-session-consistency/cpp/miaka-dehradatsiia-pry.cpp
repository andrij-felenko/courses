int main() {
    auto primary = std::make_shared<DatabasePrimary>("primary.db.internal:5432");
    auto rep1 = std::make_shared<DatabaseReplica>("replica-01", "rep1.db.internal:5432");
    auto rep2 = std::make_shared<DatabaseReplica>("replica-02", "rep2.db.internal:5432");

    SessionConsistentRouter router(primary, {rep1, rep2}, 50ms);

    ClientSession user_session{"user-uuid-42", 0};

    // 1. Користувач оновлює біографію
    std::cout << "\n--- Крок 1: Запис даних ---\n";
    router.handle_write(user_session, "UPDATE users SET bio = 'Senior Architect'");
    std::cout << "Токен клієнта після запису: min_lsn = " << user_session.min_lsn << "\n";

    // 2. Репліка 1 ще не отримала WAL (LSN = 1000)
    std::cout << "\n--- Крок 2: Читання до синхронізації ---\n";
    auto read_result = router.handle_read(user_session, "SELECT bio FROM users");
    if (read_result) {
        std::cout << *read_result << "\n";
    }

    // 3. Репліка 1 наздоганяє лідер
    std::cout << "\n--- Крок 3: Реплікація наздогнала лідер ---\n";
    rep1->update_applied_lsn(1001);
    auto fast_read = router.handle_read(user_session, "SELECT bio FROM users");
    if (fast_read) {
        std::cout << *fast_read << "\n";
    }

    return 0;
}
