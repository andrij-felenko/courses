void apply_transfer(Account& from, Account& to, double amount, AuditLog& log, Network& net) {
    from.balance -= amount;                  // крок 1: змінили стан у пам'яті
    to.balance += amount;

    auto* tx_buf = new TransactionRecord();  // крок 2: виділили пам'ять (може кинути std::bad_alloc)

    log.append(from.id(), to.id(), amount);  // крок 3: запис на диск (може кинути FileError)

    net.send_receipt(from.id(), amount);     // крок 4: мережа (може кинути SocketError)

    delete tx_buf;
}
