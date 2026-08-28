/* include/linux/rmap.h */
struct anon_vma {
        struct anon_vma        *root;             /* корінь дерева; у корені — сам на себе */
        struct rw_semaphore     rwsem;            /* справжній замок — тільки в корені */
        atomic_t                refcount;
        unsigned long           num_children;
        unsigned long           num_active_vmas;
        struct anon_vma        *parent;
        struct rb_root_cached   rb_root;          /* дерево інтервалів ребер */
};
