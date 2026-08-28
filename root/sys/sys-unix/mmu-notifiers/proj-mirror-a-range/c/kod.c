/* uapi: те саме визначення включає і модуль, і програма */
struct mirror_range {
        __u64 start;
        __u64 length;
};
#define MIRROR_IOC_ATTACH _IOW('M', 1, struct mirror_range)
#define MIRROR_IOC_FAULT  _IOW('M', 2, struct mirror_range)

#define MIRROR_MAX_PAGES 1024

struct mirror {
        struct mmu_interval_notifier notifier;  /* вузол в інтервальному дереві */
        struct mm_struct *mm;                   /* утримано mmgrab() */
        bool attached;

        struct mutex setup;   /* впорядковує ioctl між собою */
        struct mutex lock;    /* ЗАМОК ОНОВЛЕННЯ: збій ↔ скасування */

        unsigned long start;
        unsigned long npages;
        unsigned long *dev_pte;  /* «таблиця пристрою»: номери кадрів або 0 */
        unsigned long *pfns;     /* буфер відповіді hmm_range_fault */
};
