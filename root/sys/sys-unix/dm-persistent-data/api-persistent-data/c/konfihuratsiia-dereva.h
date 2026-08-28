struct dm_btree_value_type {
    void *context;
    size_t size;
    void (*inc)(void *context, const void *value);
    void (*dec)(void *context, const void *value);
    int (*equal)(void *context, const void *value1, const void *value2);
};

struct dm_btree_info {
    struct dm_transaction_manager *tm;
    unsigned levels;
    struct dm_btree_value_type value_type;
};
