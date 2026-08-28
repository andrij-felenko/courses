/* Простий вивід у стилі printf */
int sd_journal_print(int priority, const char *format, ...);
int sd_journal_printv(int priority, const char *format, va_list ap);

/* Структурований вивід ключ-значення */
int sd_journal_send(const char *format, ...);
int sd_journal_sendv(const struct iovec *iov, int n);

/* Запис із явним вказуванням location у коді */
int sd_journal_send_with_location(const char *file, const char *line, const char *func, const char *format, ...);
