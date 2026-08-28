struct xa_switch_t {
    char name[32];          /* ім'я RM (наприклад, "PostgreSQL_XA", "Oracle_XA") */
    long flags;             /* прапорці можливостей (TMNOFLAGS, TMREGISTER тощо) */
    long version;           /* версія інтерфейсу (константа 0) */
    int (*xa_open_entry)(char *xa_info, int rmid, long flags);
    int (*xa_close_entry)(char *xa_info, int rmid, long flags);
    int (*xa_start_entry)(XID *xid, int rmid, long flags);
    int (*xa_end_entry)(XID *xid, int rmid, long flags);
    int (*xa_rollback_entry)(XID *xid, int rmid, long flags);
    int (*xa_prepare_entry)(XID *xid, int rmid, long flags);
    int (*xa_commit_entry)(XID *xid, int rmid, long flags);
    int (*xa_recover_entry)(XID *xids, long count, int rmid, long flags);
    int (*xa_forget_entry)(XID *xid, int rmid, long flags);
    int (*xa_complete_entry)(int *handle, int *retval, int rmid, long flags);
};
