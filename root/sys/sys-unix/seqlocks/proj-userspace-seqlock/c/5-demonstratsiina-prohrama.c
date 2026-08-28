/* Головний приклад використання на мові C */

typedef struct {
    double price;
    uint64_t volume;
    uint64_t timestamp;
} quote_data_t;

static seqlock_t g_seqlock;
static quote_data_t g_quote;

void *writer_thread(void *arg)
{
    (void)arg;
    for (uint64_t i = 1; i <= 100000; i++) {
        seqlock_write_begin(&g_seqlock);
        g_quote.price = 100.0 + (double)i;
        g_quote.volume = i * 10;
        g_quote.timestamp = i;
        seqlock_write_end(&g_seqlock);
    }
    return NULL;
}

void *reader_thread(void *arg)
{
    (void)arg;
    uint64_t successful_reads = 0;
    uint64_t retries = 0;

    for (int i = 0; i < 10000; i++) {
        quote_data_t local_copy;
        uint32_t seq;

        do {
            seq = seqlock_read_begin(&g_seqlock);
            local_copy = g_quote;
            if (seqlock_read_retry(&g_seqlock, seq)) {
                retries++;
                continue;
            }
            break;
        } while (1);

        /* Перевірка цілісності: volume має дорівнювати timestamp * 10 */
        if (local_copy.volume != local_copy.timestamp * 10) {
            printf("ПОМИЛКА: Розрив даних! price=%.2f vol=%lu ts=%lu\n",
                   local_copy.price, local_copy.volume, local_copy.timestamp);
        } else {
            successful_reads++;
        }
    }

    printf("Читач завершив: успішно=%lu, повторів=%lu\n",
           successful_reads, retries);
    return NULL;
}

int main(void)
{
    pthread_t w, r1, r2;

    seqlock_init(&g_seqlock);

    pthread_create(&w, NULL, writer_thread, NULL);
    pthread_create(&r1, NULL, reader_thread, NULL);
    pthread_create(&r2, NULL, reader_thread, NULL);

    pthread_join(w, NULL);
    pthread_join(r1, NULL);
    pthread_join(r2, NULL);

    seqlock_destroy(&g_seqlock);
    return 0;
}
