/* Приклад логіки допуску на C */
bool should_admit_to_cache(CountingBloomFilter *filter, const char *url, size_t len) {
    if (cbf_contains(filter, url, len)) {
        /* Об'єкт запитується повторно -> допускаємо у постійний кеш */
        return true;
    }
    /* Перший запит -> реєструємо у фільтрі, але у кеш не записуємо */
    cbf_insert(filter, url, len);
    return false;
}
