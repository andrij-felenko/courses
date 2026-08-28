static const char* const EVICT_SQL =
    "DELETE FROM tiles WHERE key IN ("
    "  SELECT t.key FROM tiles t"
    "    LEFT JOIN set_tiles s ON s.key = t.key"
    "   WHERE s.key IS NULL"        // на тайл не посилається ЖОДЕН набір
    "   ORDER BY t.used ASC"        // найдавніше вживані першими
    "   LIMIT ?) "
    "RETURNING bytes";
// evict_ = prep(db_, EVICT_SQL) — так само один раз при відкритті

int64_t TileStore::evict(int64_t high, int64_t low)   // скажімо, 2 ГіБ і 1.7 ГіБ
{
    int64_t total = scalar(db_, "SELECT COALESCE(SUM(bytes),0) FROM tiles");
    if (total <= high) return 0;                      // нижче верхньої межі не рухаємось

    int64_t freed = 0;
    while (total - freed > low) {
        Reset r{evict_};
        sqlite3_bind_int(evict_, 1, 5000);
        int64_t round = 0, rows = 0;
        while (sqlite3_step(evict_) == SQLITE_ROW) {  // RETURNING віддає рядки видалених
            round += sqlite3_column_int64(evict_, 0);
            ++rows;
        }
        if (rows == 0) break;                         // вільного більше нема — усе закріплене
        freed += round;
    }
    exec(db_, "PRAGMA incremental_vacuum(2000)");     // віддати місце файловій системі
    return freed;
}
