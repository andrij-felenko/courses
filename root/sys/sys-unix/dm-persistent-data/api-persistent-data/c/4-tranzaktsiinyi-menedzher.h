int dm_tm_create_with_sm(struct dm_block_manager *bm,
                         dm_block_t sb_location,
                         struct dm_transaction_manager **tm,
                         struct dm_space_map **sm);

int dm_tm_open_with_sm(struct dm_block_manager *bm,
                       dm_block_t sb_location,
                       void *root_sm,
                       size_t root_sm_size,
                       struct dm_transaction_manager **tm,
                       struct dm_space_map **sm);

int dm_tm_shadow_block(struct dm_transaction_manager *tm,
                       dm_block_t orig,
                       struct dm_block_validator *v,
                       struct dm_block **result,
                       int *inc_children);

int dm_tm_new_block(struct dm_transaction_manager *tm,
                    struct dm_block_validator *v,
                    struct dm_block **result);

int dm_tm_commit(struct dm_transaction_manager *tm,
                 struct dm_block *root_block);
