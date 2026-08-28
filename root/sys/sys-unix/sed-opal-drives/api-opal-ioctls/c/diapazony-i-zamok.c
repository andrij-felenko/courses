struct opal_user_lr_setup {
        __u64 range_start;
        __u64 range_length;
        __u32 RLE;                /* Read Lock Enabled  */
        __u32 WLE;                /* Write Lock Enabled */
        struct opal_session_info session;
};

struct opal_lock_unlock {
        struct opal_session_info session;
        __u32 l_state;            /* OPAL_RO = 1 | OPAL_RW = 2 | OPAL_LK = 4 */
        __u16 flags;              /* OPAL_SAVE_FOR_LOCK = 1 */
        __u8  __align[2];
};
