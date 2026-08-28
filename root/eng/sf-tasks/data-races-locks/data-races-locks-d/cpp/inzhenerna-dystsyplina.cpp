// НАЇВНО І НЕБЕЗПЕЧНО В C++:
bool process_transaction(Transaction& tx) {
    g_mutex.lock();
    if (!validate_transaction(tx)) {
        return false; // КАТАСТРОФА: Замок не звільнено!
    }
    apply_transaction(tx);
    g_mutex.unlock();
    return true;
}
