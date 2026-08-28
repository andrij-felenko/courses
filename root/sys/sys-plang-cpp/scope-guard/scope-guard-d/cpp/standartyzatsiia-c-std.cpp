#include <scope>
#include <fstream>
#include <iostream>

void process_transaction_modern(Database& db, const std::string& query) {
    db.execute("BEGIN TRANSACTION");

    // Відкат у разі винятку
    std::scope_fail rollback_guard = [&] noexcept {
        db.execute("ROLLBACK");
    };

    // Фіксація у разі успіху
    std::scope_success commit_guard = [&] noexcept {
        db.execute("COMMIT");
    };

    // Безумовне логування тривалості на виході
    const auto start_time = std::chrono::steady_clock::now();
    std::scope_exit log_guard = [&] noexcept {
        auto elapsed = std::chrono::steady_clock::now() - start_time;
        std::cout << "Query executed in " << elapsed.count() << " ms\n";
    };

    db.execute(query); // якщо виклик кине виняток — спрацює rollback_guard і log_guard
}
