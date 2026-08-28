#include <iostream>
#include <string>
#include <memory>
#include <rocksdb/db.h>
#include <rocksdb/options.h>

void inspect_rocksdb_amplification(rocksdb::DB* db) {
    std::string stats_out;
    
    // Отримання текстового звіту про стан рівнів та Compaction WAF
    if (db->GetProperty("rocksdb.stats", &stats_out)) {
        std::cout << "=== RocksDB Compaction Stats ===" << std::endl;
        std::cout << stats_out << std::endl;
    }

    // Отримання точних числових показників через GetIntProperty
    uint64_t bytes_written_user = 0;
    uint64_t bytes_written_flush = 0;
    uint64_t bytes_written_compaction = 0;

    db->GetIntProperty("rocksdb.stats.bytes-written", &bytes_written_user);
    db->GetIntProperty("rocksdb.base-level-write-bytes", &bytes_written_flush);
    db->GetIntProperty("rocksdb.compact-write-bytes", &bytes_written_compaction);

    if (bytes_written_user > 0) {
        uint64_t total_db_writes = bytes_written_flush + bytes_written_compaction;
        double db_waf = static_cast<double>(total_db_writes) / static_cast<double>(bytes_written_user);

        std::cout << "Логічний запис користувача: " << bytes_written_user / (1024 * 1024) << " MB\n";
        std::cout << "Запис при Flush (MemTable): " << bytes_written_flush / (1024 * 1024) << " MB\n";
        std::cout << "Запис при Compaction:       " << bytes_written_compaction / (1024 * 1024) << " MB\n";
        std::cout << "Підсумковий Database WAF:   " << db_waf << std::endl;
    }
}
