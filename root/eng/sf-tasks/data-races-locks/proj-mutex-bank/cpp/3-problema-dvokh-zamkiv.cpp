// НЕБЕЗПЕЧНО: ПРИЗВОДИТЬ ДО ДЕДЛОКУ!
bool bad_transfer(SafeAccount& from, SafeAccount& to, int64_t amount) {
    std::unique_lock<std::mutex> lock_from(from.get_mutex());
    std::unique_lock<std::mutex> lock_to(to.get_mutex());

    if (from.raw_balance() >= amount) {
        from.raw_modify(-amount);
        to.raw_modify(amount);
        return true;
    }
    return false;
}
