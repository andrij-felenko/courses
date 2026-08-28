// НЕБЕЗПЕЧНО В C:
bool process_transaction(Transaction *tx) {
    pthread_mutex_lock(&g_mutex);
    if (!validate_transaction(tx)) {
        return false; // КАТАСТРОФА: М'ютекс залишився заблокованим назавжди!
    }
    apply_transaction(tx);
    pthread_mutex_unlock(&g_mutex);
    return true;
}
