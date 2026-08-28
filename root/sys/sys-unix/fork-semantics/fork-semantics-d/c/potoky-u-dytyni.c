static pthread_mutex_t log_lock = PTHREAD_MUTEX_INITIALIZER;

static void *writer(void *unused) {
    (void)unused;
    for (;;) {
        pthread_mutex_lock(&log_lock);
        write_line_to_journal();
        pthread_mutex_unlock(&log_lock);
    }
}

int main(void) {
    pthread_t t;
    pthread_create(&t, NULL, writer, NULL);

    pid_t pid = fork();
    if (pid == 0) {
        pthread_mutex_lock(&log_lock);   /* якщо writer тримав замок — не повернеться НІКОЛИ */
        write_line_to_journal();
        pthread_mutex_unlock(&log_lock);
        _exit(0);
    }
    wait(NULL);
}
