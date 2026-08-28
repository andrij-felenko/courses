struct ublksrv_ctrl_dev_info {
        __u16   nr_hw_queues;      /* ≤ UBLK_MAX_NR_QUEUES        */
        __u16   queue_depth;       /* ≤ UBLK_MAX_QUEUE_DEPTH = 4096 */
        __u16   state;             /* ← ядро: DEAD 0, LIVE 1, QUIESCED 2, FAIL_IO 3 */
        __u16   pad0;
        __u32   max_io_buf_bytes;  /* стеля одного запиту в байтах */
        __u32   dev_id;            /* ↔ на вході -1, на виході — виданий номер */
        __s32   ublksrv_pid;       /* ← ядро: pid демона з START_DEV */
        __u32   pad1;
        __u64   flags;             /* UBLK_F_*                     */
        __u64   ublksrv_flags;     /* ядро не читає: приватне поле сервера */
        __u32   owner_uid;         /* ← ядро, для UBLK_F_UNPRIVILEGED_DEV */
        __u32   owner_gid;
        __u64   reserved1, reserved2;
};
