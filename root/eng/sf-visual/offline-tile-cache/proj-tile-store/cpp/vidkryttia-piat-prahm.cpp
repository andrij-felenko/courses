static bool exec(sqlite3* db, const char* sql)
{
    char* err = nullptr;
    if (sqlite3_exec(db, sql, nullptr, nullptr, &err) == SQLITE_OK) return true;
    std::fprintf(stderr, "sqlite: %s [%s]\n", err ? err : "?", sql);
    sqlite3_free(err);
    return false;
}

static int64_t scalar(sqlite3* db, const char* sql)
{
    sqlite3_stmt* s = nullptr;
    if (sqlite3_prepare_v2(db, sql, -1, &s, nullptr) != SQLITE_OK) return -1;
    int64_t v = (sqlite3_step(s) == SQLITE_ROW) ? sqlite3_column_int64(s, 0) : -1;
    sqlite3_finalize(s);
    return v;
}

bool TileStore::open(const char* path, int page_size /* = 32768 */)
{
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_NOMUTEX;
    if (sqlite3_open_v2(path, &db_, flags, nullptr) != SQLITE_OK) return false;

    char buf[64];
    std::snprintf(buf, sizeof buf, "PRAGMA page_size=%d;", page_size);
    exec(db_, buf);                              // подіє лише на ЩЕ НЕ створеній базі
    exec(db_, "PRAGMA auto_vacuum=INCREMENTAL;");// теж лише до перших таблиць
    exec(db_, "PRAGMA journal_mode=WAL;");
    exec(db_, "PRAGMA synchronous=NORMAL;");
    exec(db_, "PRAGMA foreign_keys=ON;");        // поза транзакцією — інакше мовчазний no-op
    sqlite3_busy_timeout(db_, 5000);

    if (!exec(db_, SCHEMA_SQL)) return false;
    if (scalar(db_, "PRAGMA page_size;") != page_size)
        std::fprintf(stderr, "увага: база лишилася зі сторінкою %lld\n",
                     (long long)scalar(db_, "PRAGMA page_size;"));

    exec(db_, "UPDATE download_queue SET state=0 WHERE state=1;");  // після аварійного виходу
    return prepare_all();
}
