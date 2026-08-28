struct mmu_interval_notifier_ops {
        bool (*invalidate)(struct mmu_interval_notifier *interval_sub,
                           const struct mmu_notifier_range *range,
                           unsigned long cur_seq);
};

int  mmu_interval_notifier_insert(struct mmu_interval_notifier *interval_sub,
                                  struct mm_struct *mm, unsigned long start,
                                  unsigned long length,
                                  const struct mmu_interval_notifier_ops *ops);
int  mmu_interval_notifier_insert_locked(/* те саме */);
void mmu_interval_notifier_remove(struct mmu_interval_notifier *interval_sub);

unsigned long mmu_interval_read_begin(struct mmu_interval_notifier *interval_sub);
bool mmu_interval_read_retry(struct mmu_interval_notifier *interval_sub, unsigned long seq);
bool mmu_interval_check_retry(struct mmu_interval_notifier *interval_sub, unsigned long seq);
void mmu_interval_set_seq(struct mmu_interval_notifier *interval_sub, unsigned long cur_seq);
