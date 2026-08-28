#define DM_IOCTL 0xfd
#define DM_DEV_CREATE   _IOWR(DM_IOCTL, DM_DEV_CREATE_CMD,   struct dm_ioctl)
#define DM_TABLE_LOAD   _IOWR(DM_IOCTL, DM_TABLE_LOAD_CMD,   struct dm_ioctl)
#define DM_DEV_SUSPEND  _IOWR(DM_IOCTL, DM_DEV_SUSPEND_CMD,  struct dm_ioctl)
#define DM_TABLE_STATUS _IOWR(DM_IOCTL, DM_TABLE_STATUS_CMD, struct dm_ioctl)
#define DM_TARGET_MSG   _IOWR(DM_IOCTL, DM_TARGET_MSG_CMD,   struct dm_ioctl)

struct dm_ioctl {
        __u32 version[3];      /* заповнює програма; ядро вписує свою й повертає */
        __u32 data_size;       /* увесь буфер разом із цією структурою */
        __u32 data_start;      /* де починається корисне навантаження */
        __u32 target_count;    /* скільки рядків таблиці далі */
        __s32 open_count;      /* ← ядро: скільки разів пристрій відкрито */
        __u32 flags;
        __u32 event_nr;        /* номер події або cookie для udev */
        __u32 padding;
        __u64 dev;             /* пара номерів, спакована в 64 біти */
        char  name[DM_NAME_LEN];   /* 128 */
        char  uuid[DM_UUID_LEN];   /* 129 */
        char  data[7];             /* вирівнювання; sizeof — 312 */
};
