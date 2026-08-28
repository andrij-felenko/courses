// Вихідний виклик через покажчик на функцію (C)
typedef struct Handler {
    uint64_t (*process)(const void* data);
} Handler;

uint64_t dispatch(Handler* h, const void* data) {
    // Непрямий перехід у статичній збірці:
    // return h->process(data);

    // Трансформація компілятора після PGO (Indirect Call Promotion):
    if (h->process == fast_process) {
        // Прямий виклик + повний інлайнінг тіла fast_process
        return fast_process(data);
    } else {
        // Резервний непрямий виклик для решти 0.6% випадків
        return h->process(data);
    }
}
