struct mmu_notifier_range {
        struct mm_struct        *mm;
        unsigned long            start;
        unsigned long            end;
        unsigned                 flags;
        enum mmu_notifier_event  event;
        void                    *owner;
};

#define MMU_NOTIFIER_RANGE_BLOCKABLE (1 << 0)

static inline bool mmu_notifier_range_blockable(const struct mmu_notifier_range *range)
{
        return (range->flags & MMU_NOTIFIER_RANGE_BLOCKABLE);
}
