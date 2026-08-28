struct group_req {
    uint32_t                gr_interface;   /* індекс інтерфейсу */
    struct sockaddr_storage gr_group;       /* група: AF_INET або AF_INET6 */
};

struct group_source_req {
    uint32_t                gsr_interface;
    struct sockaddr_storage gsr_group;
    struct sockaddr_storage gsr_source;
};
