#define MAX_CLOCK_SKEW_SEC 5

int is_timestamp_valid(uint64_t token_time, uint64_t now_time, uint64_t max_age) {
    if (token_time > now_time) {
        if ((token_time - now_time) > MAX_CLOCK_SKEW_SEC) {
            return 0; /* Надто далеко в майбутньому */
        }
        return 1; /* У межах допустимого дрейфу */
    }
    if ((now_time - token_time) > max_age) {
        return 0; /* Виклик протермінований */
    }
    return 1;
}
