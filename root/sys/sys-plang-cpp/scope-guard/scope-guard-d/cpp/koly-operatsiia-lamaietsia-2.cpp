void apply_transfer_nested(Account& from, Account& to, double amount, AuditLog& log, Network& net) {
    from.balance -= amount;
    to.balance += amount;

    TransactionRecord* tx_buf = nullptr;
    try {
        tx_buf = new TransactionRecord();
        try {
            log.append(from.id(), to.id(), amount);
            try {
                net.send_receipt(from.id(), amount);
            } catch (...) {
                log.rollback_last();
                throw;
            }
        } catch (...) {
            delete tx_buf;
            throw;
        }
    } catch (...) {
        from.balance += amount; // відкат балансу
        to.balance -= amount;
        throw;
    }

    delete tx_buf;
}
