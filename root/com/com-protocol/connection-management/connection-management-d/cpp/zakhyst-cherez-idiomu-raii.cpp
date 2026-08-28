// Надійний підхід у C++: обгортка RAII
int executeTransaction(ConnectionPool& pool) {
    // Деструктор об'єкта lease гарантовано поверне сокет у пул
    // при будь-якому шляху виходу з функції, включно з генерацією винятків
    auto lease = pool.acquire(std::chrono::seconds(5));
    if (!lease) {
        return -1;
    }

    if (processTransaction(lease->fd()) < 0) {
        lease->markBroken(); // Позначаємо сокет як пошкоджений для закриття
        return -1;
    }
    return 0;
}
