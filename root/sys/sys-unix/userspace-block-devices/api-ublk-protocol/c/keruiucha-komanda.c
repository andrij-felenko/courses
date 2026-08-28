struct ublksrv_ctrl_cmd {
        __u32   dev_id;         /* номер пристрою; -1 в ADD_DEV — «вибери сам» */
        __u16   queue_id;       /* -1, якщо команда не про чергу */
        __u16   len;            /* довжина буфера за addr */
        __u64   addr;           /* буфер команди: IN або OUT */
        __u64   data[1];        /* вбудоване число: pid, номер черги */
        __u16   dev_path_len;   /* лише для UBLK_F_UNPRIVILEGED_DEV, із нульовим байтом */
        __u16   pad;
        __u32   reserved;
};
