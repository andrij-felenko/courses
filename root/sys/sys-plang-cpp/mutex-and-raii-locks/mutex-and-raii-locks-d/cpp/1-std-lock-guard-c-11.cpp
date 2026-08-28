void safe_deposit(BankAccount& account, int amount) {
    // Конструктор lock_guard викликає account.mtx.lock()
    std::lock_guard<std::mutex> lock(account.mtx);

    if (amount <= 0) {
        throw std::invalid_argument("Сума повинна бути додатною");
    } // При викиді винятку деструктор lock викликає account.mtx.unlock()

    account.balance += amount;
} // При виході з функції деструктор lock автоматично викликає account.mtx.unlock()
