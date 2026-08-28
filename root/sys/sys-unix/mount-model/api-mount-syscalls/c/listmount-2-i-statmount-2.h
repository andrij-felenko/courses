struct mnt_id_req {
    __u32 size;             /* sizeof(struct mnt_id_req) — так ядро знає версію */
    union {
        __u32 mnt_ns_fd;    /* дескриптор чужого простору імен монтувань */
        __u32 mnt_fd;       /* або дескриптор на саме монтування */
    };
    __u64 mnt_id;      /* чиїх дітей питаємо; LSMT_ROOT — корінь простору */
    __u64 param;       /* listmount: з якого ID продовжити; statmount: маска STATMOUNT_* */
    __u64 mnt_ns_id;   /* з 6.11: чужий простір імен за його ідентифікатором */
};

/* скільки монтувань покладено в mnt_ids; 0 — більше немає */
syscall(SYS_listmount, &req, mnt_ids, nr_mnt_ids, flags);
syscall(SYS_statmount, &req, smbuf, bufsize, flags);
