/* uapi/linux/pacer.h — цей файл більше ніколи не можна змінювати,
   можна тільки дописувати в кінець структур і в кінець списку бітів */

#include <linux/types.h>

struct pacer_policy {
        __u32          size;         /*  0.. 3  довжина структури від відправника */
        __u32          __reserved0;  /*  4.. 7  мусить бути 0 */
        __aligned_u64  flags;        /*  8..15 */
        __aligned_u64  rate;         /* 16..23  операцій за секунду; 0 = без межі */
        __u32          burst;        /* 24..27  дозволений сплеск; 0 = без сплеску */
        __u32          __reserved1;  /* 28..31  мусить бути 0 */
        /* ─────────── PACER_POLICY_SIZE_VER0 == 32 ─────────── */
        __aligned_u64  deadline_ns;  /* 32..39  0 = без дедлайну */
        /* ─────────── PACER_POLICY_SIZE_VER1 == 40 ─────────── */
        __s32          cgroup_fd;    /* 40..43  чинне лише з PACER_CGROUP */
        __u32          __reserved2;  /* 44..47  мусить бути 0 */
        /* ─────────── PACER_POLICY_SIZE_VER2 == 48 ─────────── */
        __aligned_u64  attrs;        /* 48..55  (uintptr_t) на хвіст атрибутів */
        __u32          attrs_len;    /* 56..59  0 = хвоста немає */
        __u32          __reserved3;  /* 60..63  мусить бути 0 */
        /* ─────────── PACER_POLICY_SIZE_VER3 == 64 ─────────── */
};

#define PACER_POLICY_SIZE_VER0  32
#define PACER_POLICY_SIZE_VER1  40
#define PACER_POLICY_SIZE_VER2  48
#define PACER_POLICY_SIZE_VER3  64

#define PACER_STRICT  (1ULL << 0)   /* з версії 0 */
#define PACER_NOTIFY  (1ULL << 1)   /* з версії 1 */
#define PACER_CGROUP  (1ULL << 2)   /* з версії 2: поле cgroup_fd має сенс */

#define PACER_ARM   _IO('P', 1)     /* поставити політику */
#define PACER_INFO  _IO('P', 0)     /* спитати, що це ядро вміє */
