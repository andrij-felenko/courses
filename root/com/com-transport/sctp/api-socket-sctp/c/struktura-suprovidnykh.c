struct sctp_sndrcvinfo {
    uint16_t     sinfo_stream;     /* Номер потоку, з якого надійшло повідомлення */
    uint16_t     sinfo_ssn;        /* Номер послідовності всередині потоку (SSN) */
    uint16_t     sinfo_flags;      /* Прапорці чанка (SCTP_UNORDERED тощо) */
    uint32_t     sinfo_ppid;       /* Ідентифікатор прикладного протоколу (PPID) */
    uint32_t     sinfo_context;    /* Контекст відправника */
    uint32_t     sinfo_timetolive; /* Залишковий час життя */
    uint32_t     sinfo_tsn;        /* Глобальний порядковий номер передачі (TSN) */
    uint32_t     sinfo_cumtsn;     /* Поточний накопичувальний TSN підтвердження */
    sctp_assoc_t sinfo_assoc_id;   /* Числовий дескриптор асоціації */
};
