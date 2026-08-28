#include <rocksdb/db.h>
#include <rocksdb/options.h>
#include <rocksdb/table.h>
#include <rocksdb/filter_policy.h>

rocksdb::Options setup_rocksdb_ribbon() {
    rocksdb::Options options;
    options.create_if_missing = true;

    rocksdb::BlockBasedTableOptions table_options;
    table_options.filter_policy.reset(
        rocksdb::NewRibbonFilterPolicy(10.0, /*bloom_before_level=*/2)
    );
    table_options.cache_index_and_filter_blocks = true;
    table_options.pin_l0_filter_and_index_blocks_in_cache = true;
    table_options.format_version = 5;

    options.table_factory.reset(
        rocksdb::NewBlockBasedTableFactory(table_options)
    );
    options.max_background_jobs = 8;
    return options;
}
