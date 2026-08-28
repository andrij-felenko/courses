void TileStore::touch(uint64_t key) { pending_.push_back(key); }

void TileStore::flush_touches(int64_t now)      // раз на кілька секунд або при паузі
{
    if (pending_.empty() || !exec(db_, "BEGIN IMMEDIATE")) return;
    for (uint64_t k : pending_) {
        Reset r{touch_};
        sqlite3_bind_int64(touch_, 1, now);
        sqlite3_bind_int64(touch_, 2, (sqlite3_int64)k);
        sqlite3_step(touch_);
    }
    exec(db_, "COMMIT");
    pending_.clear();
}
