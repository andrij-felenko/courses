void folio_add_new_anon_rmap(struct folio *, struct vm_area_struct *,
                             unsigned long address, rmap_t flags);
void folio_add_anon_rmap_ptes(struct folio *, struct page *, int nr_pages,
                              struct vm_area_struct *, unsigned long address,
                              rmap_t flags);
void folio_add_anon_rmap_pmd(struct folio *, struct page *,
                             struct vm_area_struct *, unsigned long address,
                             rmap_t flags);
void folio_add_file_rmap_ptes(struct folio *, struct page *, int nr_pages,
                              struct vm_area_struct *);
void folio_add_file_rmap_pmd(struct folio *, struct page *,
                             struct vm_area_struct *);
void folio_remove_rmap_ptes(struct folio *, struct page *, int nr_pages,
                            struct vm_area_struct *);
void folio_remove_rmap_pmd(struct folio *, struct page *,
                           struct vm_area_struct *);
void folio_move_anon_rmap(struct folio *, struct vm_area_struct *);

/* однослівні форми — макроси-обгортки з nr_pages = 1 */
#define folio_add_anon_rmap_pte(folio, page, vma, address, flags)  \
        folio_add_anon_rmap_ptes(folio, page, 1, vma, address, flags)
#define folio_add_file_rmap_pte(folio, page, vma)   folio_add_file_rmap_ptes(folio, page, 1, vma)
#define folio_remove_rmap_pte(folio, page, vma)     folio_remove_rmap_ptes(folio, page, 1, vma)
