#include <iostream>
#include <string>
#include <memory>
#include <span>
#include <rocksdb/db.h>
#include <rocksdb/write_batch.h>

namespace kv_store {

class EmbeddedKeyValueStore {
public:
    explicit EmbeddedKeyValueStore(const std::string& db_path) {
        rocksdb::Options options;
        options.create_if_missing = true;
        options.IncreaseParallelism(4);
        options.OptimizeLevelStyleCompaction();

        rocksdb::DB* raw_db = nullptr;
        rocksdb::Status status = rocksdb::DB::Open(options, db_path, &raw_db);
        if (!status.ok()) {
            throw std::runtime_error("Не вдалося відкрити RocksDB: " + status.ToString());
        }
        db_.reset(raw_db);
    }

    void insert_batch(std::span<const std::pair<std::string, std::string>> records) {
        rocksdb::WriteBatch batch;
        for (const auto& [key, value] : records) {
            batch.Put(key, value);
        }

        rocksdb::WriteOptions write_opts;
        write_opts.sync = false;

        rocksdb::Status s = db_->Write(write_opts, &batch);
        if (!s.ok()) {
            throw std::runtime_error("Помилка запису пакета: " + s.ToString());
        }
    }

private:
    std::unique_ptr<rocksdb::DB> db_;
};

} // namespace kv_store
