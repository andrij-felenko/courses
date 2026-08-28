struct dm_space_map {
    void (*destroy)(struct dm_space_map *sm);
    int (*extend)(struct dm_space_map *sm, dm_block_t extra_blocks);
    int (*get_nr_blocks)(struct dm_space_map *sm, dm_block_t *count);
    int (*get_nr_free)(struct dm_space_map *sm, dm_block_t *count);
    int (*get_count)(struct dm_space_map *sm, dm_block_t b, uint32_t *result);
    int (*set_count)(struct dm_space_map *sm, dm_block_t b, uint32_t count);
    int (*commit)(struct dm_space_map *sm);
    int (*inc_block)(struct dm_space_map *sm, dm_block_t b);
    int (*dec_block)(struct dm_space_map *sm, dm_block_t b);
    int (*new_block)(struct dm_space_map *sm, dm_block_t *b);
    int (*root_size)(struct dm_space_map *sm, size_t *result);
    int (*copy_root)(struct dm_space_map *sm, void *copy_to_here_le, size_t len);
};
