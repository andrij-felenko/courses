// НЕБЕЗПЕЧНО: ПРИЗВОДИТЬ ДО ДЕДЛОКУ ПРИ ЗУСТРІЧНИХ ПЕРЕКАЗАХ!
bool bad_transfer(SafeAccount *from, SafeAccount *to, int64_t amount) {
    pthread_mutex_lock(&from->lock); // Захоплюємо перший рахунок
    pthread_mutex_lock(&to->lock);   // Захоплюємо другий рахунок

    bool success = false;
    if (from->balance >= amount) {
        from->balance -= amount;
        to->balance += amount;
        success = true;
    }

    pthread_mutex_unlock(&to->lock);
    pthread_mutex_unlock(&from->lock);
    return success;
}
