union sctp_notification {
    struct {
        uint16_t sn_type;   /* Тип сповіщення (SCTP_ASSOC_CHANGE, SCTP_PEER_ADDR_CHANGE) */
        uint16_t sn_flags;
        uint32_t sn_length;
    } sn_header;
    struct sctp_assoc_change   sn_assoc_change;
    struct sctp_paddr_change   sn_paddr_change;
    struct sctp_send_failed    sn_send_failed;
    struct sctp_remote_error   sn_remote_error;
    struct sctp_shutdown_event sn_shutdown_event;
};
