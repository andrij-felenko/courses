struct address_space_operations {
    int  (*read_folio)(struct file *, struct folio *);
    void (*readahead)(struct readahead_control *);
    int  (*writepages)(struct address_space *, struct writeback_control *);
    bool (*dirty_folio)(struct address_space *, struct folio *);
    int  (*write_begin)(const struct kiocb *, struct address_space *,
                        loff_t pos, unsigned len, struct folio **, void **fsdata);
    int  (*write_end)(const struct kiocb *, struct address_space *,
                      loff_t pos, unsigned len, unsigned copied,
                      struct folio *, void *fsdata);
    sector_t (*bmap)(struct address_space *, sector_t);
    void (*invalidate_folio)(struct folio *, size_t start, size_t len);
    bool (*release_folio)(struct folio *, gfp_t);
    void (*free_folio)(struct folio *);
    ssize_t (*direct_IO)(struct kiocb *, struct iov_iter *);
    int  (*migrate_folio)(struct address_space *, struct folio *dst,
                          struct folio *src, enum migrate_mode);
    int  (*launder_folio)(struct folio *);
    bool (*is_partially_uptodate)(struct folio *, size_t from, size_t count);
    int  (*error_remove_folio)(struct address_space *, struct folio *);
};
