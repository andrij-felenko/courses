// Приклад отримання статистики через RocksDB C++ API
#include <rocksdb/db.h>
#include <rocksdb/filter_policy.h>
#include <iostream>

void print_bloom_stats(rocksdb::DB* db) {
    std::string stats_str;
    if (db->GetProperty("rocksdb.sstables", &stats_str)) {
        std::cout << "RocksDB SSTable & Bloom Filter Stats:\n" << stats_str << '\n';
    }
}
