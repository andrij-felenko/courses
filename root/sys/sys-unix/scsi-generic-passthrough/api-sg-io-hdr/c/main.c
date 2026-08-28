struct nvme_passthru_cmd {
    __u8  opcode;        __u8  flags;      __u16 rsvd1;
    __u32 nsid;
    __u32 cdw2;          __u32 cdw3;
    __u64 metadata;      __u64 addr;
    __u32 metadata_len;  __u32 data_len;
    __u32 cdw10, cdw11, cdw12, cdw13, cdw14, cdw15;
    __u32 timeout_ms;
    __u32 result;        /* [вих] слово завершення */
};
