void process_transaction(Account& acc, double amount, Logger& log, Network& net) {
    acc.reserve(amount);
    try {
        log.record_intent(acc.id(), amount);
        try {
            net.notify_peer(acc.id(), amount);
        } catch (...) {
            log.cancel_intent(acc.id(), amount);
            throw;
        }
    } catch (...) {
        acc.cancel_reservation(amount);
        throw;
    }
}
