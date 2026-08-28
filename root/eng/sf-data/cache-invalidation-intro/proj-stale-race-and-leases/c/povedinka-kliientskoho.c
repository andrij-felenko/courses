char* fetch_user_data(lease_cache_t *cache, const char *key) {
    char buffer[MAX_VAL_LEN];
    uint64_t token = 0;
    int retries = 5;

    while (retries-- > 0) {
        cache_status_t status = lease_cache_get(cache, key, buffer, &token);

        if (status == CACHE_HIT) {
            return strdup(buffer);
        }

        if (status == CACHE_MISS_LEASE_GRANTED) {
            char *db_val = "Alice";
            cache_status_t set_res = lease_cache_set(cache, key, db_val, token);
            if (set_res == SET_STALE_TOKEN_REJECTED) {
                fprintf(stderr, "Попередження: токен застарів, запис відхилено кешем.\n");
            }
            return strdup(db_val);
        }

        if (status == CACHE_MISS_LEASE_BUSY) {
            usleep(20000 + (rand() % 10000));
        }
    }

    return strdup("Alice");
}
