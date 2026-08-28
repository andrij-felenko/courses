struct TileIn {                    // те, що щойно принесла мережа
    uint64_t             key;
    const unsigned char* body;     // nullptr → «такого тайла не існує»
    int                  len;
    std::string          etag;
};

struct Reset {                     // повертає підготовлений вираз у вихідний стан
    sqlite3_stmt* s;
    ~Reset() { sqlite3_reset(s); sqlite3_clear_bindings(s); }
};

int TileStore::put_batch(const std::vector<TileIn>& in, int64_t set_id, int64_t now)
{
    if (in.empty()) return 0;
    if (!exec(db_, "BEGIN IMMEDIATE")) return -1;   // одразу беремо право на запис

    int written = 0;
    for (const TileIn& t : in) {
        const bool missing = (t.body == nullptr);
        if (!missing && !looks_like_tile(t.body, t.len)) continue;   // не картинка — не пишемо

        Reset r{put_};
        sqlite3_bind_int64(put_, 1, (sqlite3_int64)t.key);
        sqlite3_bind_int  (put_, 2, missing ? 0 : t.len);
        sqlite3_bind_int64(put_, 3, now);
        sqlite3_bind_int64(put_, 4, now);
        if (t.etag.empty()) sqlite3_bind_null(put_, 5);
        else sqlite3_bind_text(put_, 5, t.etag.c_str(), -1, SQLITE_STATIC);
        if (missing) sqlite3_bind_null(put_, 6);
        else sqlite3_bind_blob(put_, 6, t.body, t.len, SQLITE_STATIC);

        if (sqlite3_step(put_) != SQLITE_DONE) { exec(db_, "ROLLBACK"); return -1; }
        ++written;

        if (set_id > 0) {                            // тайл дістає посилання від набору
            Reset rl{link_};
            sqlite3_bind_int64(link_, 1, set_id);
            sqlite3_bind_int64(link_, 2, (sqlite3_int64)t.key);
            sqlite3_step(link_);
        }
    }
    if (!exec(db_, "COMMIT")) { exec(db_, "ROLLBACK"); return -1; }
    return written;
}
