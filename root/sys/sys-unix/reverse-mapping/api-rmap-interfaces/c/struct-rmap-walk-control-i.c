struct mapper_scan {
        unsigned int count;
};

static bool report_one(struct folio *folio, struct vm_area_struct *vma,
                       unsigned long addr, void *arg)
{
        struct mapper_scan *s = arg;

        s->count++;
        pr_info("rmap: mm=%p addr=%#lx %s\n",
                vma->vm_mm, addr, vma->vm_file ? "file" : "anon");
        return true;                     /* далі, до кінця дерева */
}

static void who_maps(struct folio *folio)
{
        struct mapper_scan scan = { .count = 0 };
        struct rmap_walk_control rwc = {
                .arg       = &scan,
                .rmap_one  = report_one,
                .anon_lock = folio_lock_anon_vma_read,
                .try_lock  = true,       /* під тиском краще відступити */
        };

        folio_lock(folio);               /* обов'язково для файлових і злитих */
        rmap_walk(folio, &rwc);
        folio_unlock(folio);

        if (rwc.contended)
                pr_info("rmap: lock contended, list incomplete\n");
        else
                pr_info("rmap: %u mappings total\n", scan.count);
}
