struct nvme_uring_cmd {
    __u8   opcode;       /* Опкод команди NVMe (наприклад, 0x02 = Read, 0x01 = Write) */
    __u8   flags;        /* Прапорці NVMe команди (NVME_CMD_SGL_METABUF тощо) */
    __u16  rsvd1;        /* Зарезервовано для вирівнювання */
    __u32  nsid;         /* Ідентифікатор простору імен (Namespace ID) */
    __u32  cdw2;         /* Command Dword 2 (опціональне розширення) */
    __u32  cdw3;         /* Command Dword 3 (опціональне розширення) */
    __u64  metadata;     /* Указник на буфер метаданих простору користувача */
    __u64  addr;         /* Указник на буфер даних простору користувача */
    __u32  metadata_len; /* Довжина метаданих у байтах */
    __u32  data_len;     /* Довжина буфера даних у байтах */
    __u32  cdw10;        /* Command Dword 10 (нижні 32 біти Starting LBA) */
    __u32  cdw11;        /* Command Dword 11 (верхні 32 біти Starting LBA) */
    __u32  cdw12;        /* Command Dword 12 (кількість блоків LBA мінус 1) */
    __u32  cdw13;        /* Command Dword 13 (прапорці DSM, частота доступу) */
    __u32  cdw14;        /* Command Dword 14 (специфічні апаратні параметри) */
    __u32  cdw15;        /* Command Dword 15 (параметри перевірки цілісності) */
    __u32  timeout_ms;   /* Таймаут виконання операції пристроєм у мілісекундах */
    __u32  rsvd2;        /* Зарезервовано */
};
