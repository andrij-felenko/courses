struct mmu_notifier_ops {
        void (*release)(struct mmu_notifier *subscription, struct mm_struct *mm);

        int  (*clear_flush_young)(struct mmu_notifier *subscription, struct mm_struct *mm,
                                  unsigned long start, unsigned long end);
        int  (*clear_young)(struct mmu_notifier *subscription, struct mm_struct *mm,
                            unsigned long start, unsigned long end);
        int  (*test_young)(struct mmu_notifier *subscription, struct mm_struct *mm,
                           unsigned long address);

        int  (*invalidate_range_start)(struct mmu_notifier *subscription,
                                       const struct mmu_notifier_range *range);
        void (*invalidate_range_end)(struct mmu_notifier *subscription,
                                     const struct mmu_notifier_range *range);

        void (*arch_invalidate_secondary_tlbs)(struct mmu_notifier *subscription,
                                               struct mm_struct *mm,
                                               unsigned long start, unsigned long end);

        struct mmu_notifier *(*alloc_notifier)(struct mm_struct *mm);
        void (*free_notifier)(struct mmu_notifier *subscription);
};
