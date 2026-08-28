struct msqid_ds {
    struct ipc_perm msg_perm;   /* власник і права */
    time_t          msg_stime;  /* час останнього msgsnd */
    time_t          msg_rtime;  /* час останнього msgrcv */
    time_t          msg_ctime;  /* створення або останньої зміни */
    unsigned long   msg_cbytes; /* байтів у черзі зараз */
    msgqnum_t       msg_qnum;   /* повідомлень у черзі зараз */
    msglen_t        msg_qbytes; /* стеля черги в байтах */
    pid_t           msg_lspid;  /* PID останнього msgsnd */
    pid_t           msg_lrpid;  /* PID останнього msgrcv */
};

struct ipc_perm {
    key_t          __key;  /* ключ, переданий у msgget */
    uid_t          uid;    /* власник (змінюваний) */
    gid_t          gid;    /* група власника (змінювана) */
    uid_t          cuid;   /* творець */
    gid_t          cgid;   /* група творця */
    unsigned short mode;   /* права (змінювані) */
    unsigned short __seq;  /* лічильник поколінь ідентифікатора */
};
