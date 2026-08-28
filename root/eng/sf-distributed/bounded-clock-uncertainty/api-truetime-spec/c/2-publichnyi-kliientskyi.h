/* Опитує підсистему часу та повертає поточний інтервал [earliest, latest] */
tt_interval_ns_t tt_now(void);

/* Перевіряє, чи момент часу target_time_ns гарантовано минув */
bool tt_after(int64_t target_time_ns);

/* Перевіряє, чи момент часу target_time_ns гарантовано знаходиться в майбутньому */
bool tt_before(int64_t target_time_ns);

/* Блокує потік виконання, доки не настане умова tt_after(commit_ts_ns) == true */
void tt_commit_wait(int64_t commit_ts_ns);

/* Отримує поточний діагностичний стан підсистеми */
int tt_get_diagnostics(tt_diagnostics_t *out_diag);
