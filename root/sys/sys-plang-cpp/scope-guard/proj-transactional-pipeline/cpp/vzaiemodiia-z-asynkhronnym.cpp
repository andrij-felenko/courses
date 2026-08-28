#include <coroutine>

// Приклад поведінки охоронця у сопрограмі
Task<void> async_transaction_step(Database& db) {
    db.acquire_lock();
    auto lock_guard = make_scope_guard([&db] noexcept {
        db.release_lock();
    });

    // Призупинення сопрограми: деструктор lock_guard НЕ викликається!
    co_await async_network_fetch();

    // Відновлення виконання: lock_guard залишається активним
    db.apply_changes();

    // Завершення сопрограми (co_return): lock_guard знищується тут
}
