#include "rocksdb/filter_policy.h"
#include <memory>

namespace ROCKSDB_NAMESPACE {

// Створення політики Ribbon Filter для RocksDB
std::shared_ptr<const FilterPolicy> NewRibbonFilterPolicy(
    double bloom_equivalent_bits_per_key,
    int bloom_before_level = 0);

} // namespace ROCKSDB_NAMESPACE
