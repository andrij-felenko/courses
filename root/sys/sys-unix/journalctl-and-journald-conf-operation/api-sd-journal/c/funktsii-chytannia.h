/* Відкриття та закриття сесії журналу */
int sd_journal_open(sd_journal **ret, int flags);
void sd_journal_close(sd_journal *j);

/* Прапорці відкриття (flags): */
/* SD_JOURNAL_LOCAL_ONLY    - лише локальні логи поточного хоста */
/* SD_JOURNAL_RUNTIME_ONLY  - лише тимчасові логи з /run (tmpfs) */
/* SD_JOURNAL_SYSTEM        - лише системні логи (без логів користувачів) */
/* SD_JOURNAL_CURRENT_USER   - лише логи поточного користувача */

/* Додавання та скидання фільтрів (matches) */
int sd_journal_add_match(sd_journal *j, const void *data, size_t size);
int sd_journal_add_disjunction(sd_journal *j); // Логічне АБО (OR)
int sd_journal_add_conjunction(sd_journal *j); // Логічне І (AND)
void sd_journal_flush_matches(sd_journal *j);  // Очищення всіх фільтрів

/* Навігація покажчиком читання */
int sd_journal_next(sd_journal *j);
int sd_journal_previous(sd_journal *j);
int sd_journal_seek_head(sd_journal *j);
int sd_journal_seek_tail(sd_journal *j);
int sd_journal_seek_monotonic_usec(sd_journal *j, sd_id128_t boot_id, uint64_t usec);
int sd_journal_seek_realtime_usec(sd_journal *j, uint64_t usec);
int sd_journal_seek_cursor(sd_journal *j, const char *cursor);

/* Отримання даних та стан курсора */
int sd_journal_get_data(sd_journal *j, const char *field, const void **data, size_t *l);
int sd_journal_get_cursor(sd_journal *j, char **cursor);
int sd_journal_test_cursor(sd_journal *j, const char *cursor);

/* Асинхронне відстеження нових подій через epoll/poll */
int sd_journal_get_fd(sd_journal *j);
int sd_journal_get_events(sd_journal *j);
int sd_journal_get_timeout(sd_journal *j, uint64_t *timeout_usec);
int sd_journal_process(sd_journal *j);
int sd_journal_wait(sd_journal *j, uint64_t timeout_usec);
