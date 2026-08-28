// Старий шлях лічить власне використання — щоб знати, чи можна прибирати.
static std::atomic<uint64_t> legacy_hits{0};

void send_raw(const char* bytes, size_t len) {
    legacy_hits.fetch_add(1, std::memory_order_relaxed);   // хтось іще нами користується
    log_deprecated("send_raw", /* хто саме */ current_caller());
    /* … стара логіка досі працює … */
}

// Рішення прибирати ухвалюють НЕ за датою, а за цим числом:
bool safe_to_remove() {
    return legacy_hits.load() == 0;   // вікно спорожніло — тепер безпечно
}
