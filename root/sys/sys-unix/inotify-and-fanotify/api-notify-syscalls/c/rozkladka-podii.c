struct fanotify_event_info_header {
    __u8   info_type;   /* FAN_EVENT_INFO_TYPE_* */
    __u8   pad;
    __u16  len;         /* довжина цього запису разом із заголовком */
};

struct fanotify_event_info_fid {      /* FID, DFID, DFID_NAME */
    struct fanotify_event_info_header hdr;
    __kernel_fsid_t fsid;
    unsigned char handle[];           /* struct file_handle, за ним — ім'я для DFID_NAME */
};

struct fanotify_event_info_pidfd {    /* PIDFD */
    struct fanotify_event_info_header hdr;
    __s32 pidfd;
};

struct fanotify_event_info_error {    /* ERROR */
    struct fanotify_event_info_header hdr;
    __s32 error;
    __u32 error_count;
};
