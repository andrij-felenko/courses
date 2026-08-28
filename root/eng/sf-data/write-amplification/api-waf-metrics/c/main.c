#include <stdio.h>
#include <stdlib.h>
#include <rocksdb/c.h>

void inspect_rocksdb_amplification_c(rocksdb_t* db) {
    char* stats = rocksdb_property_value(db, "rocksdb.stats");
    if (stats) {
        printf("=== RocksDB Stats (C API) ===\n%s\n", stats);
        free(stats);
    }
    
    char* user_bytes_str = rocksdb_property_value(db, "rocksdb.stats.bytes-written");
    char* compact_bytes_str = rocksdb_property_value(db, "rocksdb.compact-write-bytes");
    
    if (user_bytes_str && compact_bytes_str) {
        unsigned long long user_bytes = strtoull(user_bytes_str, NULL, 10);
        unsigned long long compact_bytes = strtoull(compact_bytes_str, NULL, 10);
        
        if (user_bytes > 0) {
            double waf = (double)(user_bytes + compact_bytes) / (double)user_bytes;
            printf("User Bytes: %llu, Compact Bytes: %llu, WAF: %.2f\n", 
                   user_bytes, compact_bytes, waf);
        }
    }
    
    if (user_bytes_str) free(user_bytes_str);
    if (compact_bytes_str) free(compact_bytes_str);
}
