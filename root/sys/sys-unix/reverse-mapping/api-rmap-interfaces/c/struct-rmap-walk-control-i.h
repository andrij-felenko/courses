struct rmap_walk_control {
        void *arg;
        bool  try_lock;
        bool  contended;
        bool (*rmap_one)(struct folio *folio, struct vm_area_struct *vma,
                         unsigned long addr, void *arg);
        int  (*done)(struct folio *folio);
        struct anon_vma *(*anon_lock)(struct folio *folio,
                                      struct rmap_walk_control *rwc);
        bool (*invalid_vma)(struct vm_area_struct *vma, void *arg);
};

void rmap_walk(struct folio *folio, struct rmap_walk_control *rwc);
void rmap_walk_locked(struct folio *folio, struct rmap_walk_control *rwc);
