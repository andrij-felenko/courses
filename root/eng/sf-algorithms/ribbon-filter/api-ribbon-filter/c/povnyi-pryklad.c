#include "rocksdb/c.h"

rocksdb_options_t* setup_c_rocksdb_ribbon() {
    rocksdb_options_t *opt = rocksdb_options_create();
    rocksdb_options_set_create_if_missing(opt, 1);
    
    rocksdb_block_based_table_options_t *table_opt = rocksdb_block_based_options_create();
    rocksdb_filterpolicy_t *ribbon = rocksdb_filterpolicy_create_ribbon(10.0, 2);
    rocksdb_block_based_options_set_filter_policy(table_opt, ribbon);
    rocksdb_block_based_options_set_format_version(table_opt, 5);
    
    rocksdb_options_set_block_based_table_factory(opt, table_opt);
    return opt;
}
