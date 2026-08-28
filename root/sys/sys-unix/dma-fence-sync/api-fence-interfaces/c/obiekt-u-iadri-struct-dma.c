/* include/linux/dma-fence.h — під цим іменем з v4.10 (доти struct fence) */
struct dma_fence {
    spinlock_t                 *lock;   /* спільний із чергою, що сигналізує */
    const struct dma_fence_ops *ops;
    union {                             /* три стадії життя, ніколи разом    */
        struct list_head cb_list;       /* доки не спрацювала: спостерігачі  */
        ktime_t          timestamp;     /* після падіння: мить сигналу       */
        struct rcu_head  rcu;           /* після звільнення                  */
    };
    u64            context;   /* ідентифікатор апаратної черги */
    u64            seqno;     /* місце в цій черзі             */
    unsigned long  flags;
    struct kref    refcount;
    int            error;     /* 0 або від'ємний errno */
};
