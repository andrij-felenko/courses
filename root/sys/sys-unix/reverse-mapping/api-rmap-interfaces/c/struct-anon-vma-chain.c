struct anon_vma_chain {
        struct vm_area_struct  *vma;
        struct anon_vma        *anon_vma;
        struct list_head        same_vma;         /* ланка в списку ділянки */
        struct rb_node          rb;               /* вузол у дереві об'єкта */
        unsigned long           rb_subtree_last;  /* доповнення дерева інтервалів */
#ifdef CONFIG_DEBUG_VM_RB
        unsigned long           cached_vma_start, cached_vma_last;
#endif
};
