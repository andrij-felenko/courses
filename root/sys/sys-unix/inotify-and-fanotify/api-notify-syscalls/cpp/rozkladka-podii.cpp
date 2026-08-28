struct fanotify_event_info_header {
    std::uint8_t   info_type;   // FAN_EVENT_INFO_TYPE_*
    std::uint8_t   pad;
    std::uint16_t  len;         // довжина цього запису разом із заголовком
};

struct fanotify_event_info_fid {      // FID, DFID, DFID_NAME
    struct fanotify_event_info_header hdr;
    __kernel_fsid_t fsid;
    unsigned char handle[];           // struct file_handle, за ним — ім'я для DFID_NAME
};

struct fanotify_event_info_pidfd {    // PIDFD
    struct fanotify_event_info_header hdr;
    std::int32_t pidfd;
};

struct fanotify_event_info_error {    // ERROR
    struct fanotify_event_info_header hdr;
    std::int32_t error;
    std::uint32_t error_count;
};
